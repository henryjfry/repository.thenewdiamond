# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from caches.base_cache import connect_database, make_database
from modules import kodi_utils, settings
from modules.import_export_utils import offer_save_export_directory, pick_export_folder
from modules.watched_status import get_database

BACKUP_FORMAT = 1
BACKUP_MASK = '.json'
PROGRESS_MIN_PERCENT = 1.0

_EXTERNAL_HISTORY_PROVIDERS = {1: 'Trakt', 2: 'Simkl', 3: 'MDBList'}


def _local_history_active():
	return settings.watched_indicators() == 0


def _external_history_provider_name():
	return _EXTERNAL_HISTORY_PROVIDERS.get(settings.watched_indicators())


def _history_not_included_message():
	provider = _external_history_provider_name()
	if not provider:
		return None
	return 'Watch history not included[CR](%s Indicators)' % provider


def _history_count_line(progress_count, watched_count):
	parts = []
	if progress_count:
		parts.append('%s in progress' % progress_count)
	if watched_count:
		parts.append('%s watched' % watched_count)
	return ', '.join(parts) if parts else '0 history'


def _has_history_counts(counts):
	return counts.get('progress', 0) or counts.get('watched', 0)


def _default_backup_dir():
	return settings.import_export_directory_setting()


def _pick_import_file(default_dir):
	path = kodi_utils.browse_file(BACKUP_MASK, default_dir, heading='Choose favorites & history backup', force_defaultt=True)
	if not path:
		return None
	tpath = kodi_utils.translate_path(path)
	if not os.path.isfile(tpath):
		return None
	if not tpath.lower().endswith('.json'):
		kodi_utils.ok_dialog(heading='Import favorites & history', text='Please choose a Red Light backup (.json).')
		return None
	return tpath


def export_data(params):
	payload, counts = _build_export_payload()
	if not payload:
		return kodi_utils.ok_dialog(heading='Export favorites & history', text='Nothing to export on this device.')
	folder = pick_export_folder(heading='Choose export folder')
	if not folder:
		return
	filename = 'redlight-backup-%s.json' % datetime.now().strftime('%Y%m%d-%H%M%S')
	path = os.path.join(folder, filename)
	preview = _export_preview_text(filename, counts)
	if not kodi_utils.confirm_dialog(heading='Export favorites & history', text=preview, ok_label='Export', cancel_label='Cancel', default_control=10, scroll=True):
		return
	try:
		kodi_utils.make_directory(folder)
		with open(path, 'w', encoding='utf-8') as handle:
			json.dump(payload, handle, indent=2, ensure_ascii=False)
	except Exception as e:
		return kodi_utils.ok_dialog(heading='Export failed', text=str(e))
	summary = _export_summary(counts, filename)
	kodi_utils.ok_dialog(heading='Export complete', text=summary, scroll=True)
	kodi_utils.notification(summary, 6500)
	offer_save_export_directory(folder)


def import_data(params):
	default_dir = _default_backup_dir()
	path = _pick_import_file(default_dir)
	if not path:
		return
	try:
		with open(path, 'r', encoding='utf-8') as handle:
			payload = json.load(handle)
	except Exception as e:
		return kodi_utils.ok_dialog(heading='Import failed', text='Could not read that file.[CR][CR]%s' % e)
	file_stats = _payload_stats(payload)
	if not file_stats['favorites'] and not _has_history_counts(file_stats):
		return kodi_utils.ok_dialog(heading='Import favorites & history', text='That file contains no favorites or watch history.')
	local_stats = _local_stats()
	empty_dest = not _local_has_data(local_stats)
	preview = _preview_text(path, file_stats, local_stats)
	if not kodi_utils.confirm_dialog(
		heading='Import favorites & history',
		text=preview,
		ok_label='Import' if empty_dest else 'Continue',
		cancel_label='Cancel',
		default_control=10,
		scroll=True,
	):
		return
	if empty_dest:
		mode = 'merge'
	else:
		mode_choices = [
			('Merge — add from backup; keep what is already here', 'merge'),
			('Replace — remove local data first, then import backup', 'replace'),
		]
		list_items = [{'line1': i[0]} for i in mode_choices]
		kwargs = {'items': json.dumps(list_items), 'heading': 'Import mode', 'narrow_window': 'true'}
		mode = kodi_utils.select_dialog([i[1] for i in mode_choices], **kwargs)
		if not mode:
			return
		rules = _import_rules_text(mode, file_stats)
		if not kodi_utils.confirm_dialog(heading='Import %s' % mode, text=rules, ok_label='Import', cancel_label='Cancel', default_control=10, scroll=True):
			return
		if mode == 'replace':
			if not kodi_utils.confirm_dialog(heading='Replace local data?', text=_replace_warning(local_stats), ok_label='Replace', cancel_label='Cancel', default_control=10):
				return
	try:
		make_database('favorites_db')
		make_database('watched_db')
		summary = _apply_import(payload, mode, file_stats)
	except Exception as e:
		return kodi_utils.ok_dialog(heading='Import failed', text=str(e))
	kodi_utils.ok_dialog(heading='Import complete', text=summary, scroll=True)
	kodi_utils.notification('Import complete', 6500)
	kodi_utils.kodi_refresh()


def _addon_version():
	try:
		return kodi_utils.addon_info('version') or ''
	except:
		return ''


def _build_export_payload():
	favorites = _export_favorites()
	progress = _export_progress()
	watched = _export_watched()
	counts = {'favorites': len(favorites), 'progress': len(progress), 'watched': len(watched)}
	if not counts['favorites'] and not _has_history_counts(counts):
		return None, counts
	payload = {
		'format': BACKUP_FORMAT,
		'addon_version': _addon_version(),
		'exported': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
	}
	if favorites:
		payload['favorites'] = favorites
	if progress:
		payload['progress'] = progress
	if watched:
		payload['watched'] = watched
	return payload, counts


def _export_favorites():
	dbcon = connect_database('favorites_db')
	try:
		rows = dbcon.execute('SELECT db_type, tmdb_id, title FROM favourites ORDER BY db_type, title').fetchall()
	except:
		rows = []
	return [{'db_type': str(i[0]), 'tmdb_id': str(i[1]), 'title': str(i[2])} for i in rows]


def _export_progress():
	if not _local_history_active():
		return []
	dbcon = get_database(0)
	try:
		rows = dbcon.execute(
			'SELECT db_type, media_id, season, episode, resume_point, curr_time, last_played, resume_id, title FROM progress'
		).fetchall()
	except:
		rows = []
	result = []
	for row in rows:
		if float(row[4] or 0) <= PROGRESS_MIN_PERCENT:
			continue
		result.append(_progress_row_to_dict(row))
	return result


def _export_watched():
	if not _local_history_active():
		return []
	dbcon = get_database(0)
	try:
		rows = dbcon.execute(
			'SELECT db_type, media_id, season, episode, last_played, title FROM watched ORDER BY db_type, title'
		).fetchall()
	except:
		rows = []
	return [_watched_row_to_dict(row) for row in rows]


def _progress_row_to_dict(row):
	return {
		'db_type': str(row[0]),
		'media_id': str(row[1]),
		'season': row[2],
		'episode': row[3],
		'resume_point': str(row[4]),
		'curr_time': str(row[5]),
		'last_played': str(row[6] or ''),
		'resume_id': int(row[7] or 0),
		'title': str(row[8] or ''),
	}


def _watched_row_to_dict(row):
	return {
		'db_type': str(row[0]),
		'media_id': str(row[1]),
		'season': row[2],
		'episode': row[3],
		'last_played': str(row[4] or ''),
		'title': str(row[5] or ''),
	}


def _payload_stats(payload):
	if not isinstance(payload, dict):
		return {'favorites': 0, 'progress': 0, 'watched': 0, 'fav_keys': set(), 'progress_keys': set(), 'watched_keys': set()}
	favorites = payload.get('favorites') if isinstance(payload.get('favorites'), list) else []
	progress = payload.get('progress') if isinstance(payload.get('progress'), list) else []
	watched = payload.get('watched') if isinstance(payload.get('watched'), list) else []
	return {
		'favorites': len(favorites),
		'progress': len(progress),
		'watched': len(watched),
		'fav_keys': {_favorite_key(i) for i in favorites if _favorite_key(i)},
		'progress_keys': {_history_item_key(i) for i in progress if _history_item_key(i)},
		'watched_keys': {_history_item_key(i) for i in watched if _history_item_key(i)},
	}


def _local_stats():
	favorites = _export_favorites()
	progress = _export_progress() if _local_history_active() else []
	watched = _export_watched() if _local_history_active() else []
	return {
		'favorites': len(favorites),
		'progress': len(progress),
		'watched': len(watched),
		'fav_keys': {_favorite_key(i) for i in favorites},
		'progress_keys': {_history_item_key(i) for i in progress},
		'watched_keys': {_history_item_key(i) for i in watched},
	}


def _favorite_key(item):
	try:
		return (str(item['db_type']), str(item['tmdb_id']))
	except:
		return None


def _history_item_key(item):
	try:
		return (str(item['db_type']), str(item['media_id']), int(item.get('season') or 0), int(item.get('episode') or 0))
	except:
		return None


def _local_has_data(local_stats):
	return local_stats['favorites'] or _has_history_counts(local_stats)


def _preview_text(path, file_stats, local_stats):
	name = os.path.basename(path)
	lines = [
		'[B]%s[/B]' % name,
		'Backup: %s favorite(s), %s' % (file_stats['favorites'], _history_count_line(file_stats['progress'], file_stats['watched'])),
		'This device: %s favorite(s), %s' % (local_stats['favorites'], _history_count_line(local_stats['progress'], local_stats['watched'])),
	]
	if _has_history_counts(file_stats) and not _local_history_active():
		lines.append('[COLOR yellow]Watch history in the backup will be skipped (%s Indicators).[/COLOR]' % _external_history_provider_name())
	return '[CR]'.join(lines)


def _replace_warning(local_stats):
	parts = []
	if local_stats['favorites']:
		parts.append('%s favorite(s)' % local_stats['favorites'])
	if _has_history_counts(local_stats):
		parts.append(_history_count_line(local_stats['progress'], local_stats['watched']))
	return 'This will remove %s on this device before importing.' % ' and '.join(parts)


def _export_preview_text(filename, counts):
	lines = [
		'[B]%s[/B]' % filename,
		'%s favorite(s), %s' % (counts['favorites'], _history_count_line(counts['progress'], counts['watched'])),
	]
	msg = _history_not_included_message()
	if msg:
		lines.append('[COLOR yellow]%s[/COLOR]' % msg.replace('[CR]', ' '))
	return '[CR]'.join(lines)


def _export_summary(counts, filename):
	parts = []
	if counts['favorites']:
		parts.append('%s favorite(s)' % counts['favorites'])
	if _has_history_counts(counts) and _local_history_active():
		parts.append(_history_count_line(counts['progress'], counts['watched']))
	if parts:
		return 'Exported %s to %s' % (' and '.join(parts), filename)
	return 'Exported to %s' % filename


def _import_rules_text(mode, file_stats):
	lines = []
	if file_stats['favorites']:
		if mode == 'merge':
			lines.append('Favorites: add from backup; keep existing entries.')
		else:
			lines.append('Favorites: replace everything on this device.')
	if _has_history_counts(file_stats) and _local_history_active():
		if mode == 'merge':
			if file_stats['progress']:
				lines.append('In progress: add from backup; keep the furthest position when both match.')
			if file_stats['watched']:
				lines.append('Watched: add from backup; keep the newer date when both match.')
		else:
			lines.append('Watch history: replace everything on this device.')
	elif _has_history_counts(file_stats):
		lines.append('Watch history: skipped (%s Indicators).' % _external_history_provider_name())
	return '[CR]'.join(lines) if lines else 'Nothing to import.'


def _apply_import(payload, mode, file_stats):
	summary_parts = []
	if file_stats['favorites']:
		summary_parts.append(_import_favorites(payload.get('favorites') or [], mode))
	if _local_history_active():
		if file_stats['progress']:
			summary_parts.append(_import_progress(payload.get('progress') or [], mode))
		if file_stats['watched']:
			summary_parts.append(_import_watched(payload.get('watched') or [], mode))
	elif _has_history_counts(file_stats):
		summary_parts.append('Watch history skipped (%s Indicators)' % _external_history_provider_name())
	return 'Import complete — %s' % '; '.join([i for i in summary_parts if i]) if summary_parts else 'Import complete'


def _import_favorites(items, mode):
	dbcon = connect_database('favorites_db')
	if mode == 'replace':
		dbcon.execute('DELETE FROM favourites')
	added, updated = 0, 0
	for item in items:
		key = _favorite_key(item)
		if not key:
			continue
		exists = dbcon.execute('SELECT 1 FROM favourites WHERE db_type=? AND tmdb_id=?', key).fetchone()
		dbcon.execute('INSERT OR REPLACE INTO favourites VALUES (?, ?, ?)', (key[0], key[1], str(item.get('title') or '')))
		if exists:
			updated += 1
		else:
			added += 1
	return 'favorites: %s added, %s updated' % (added, updated)


def _import_progress(items, mode):
	dbcon = get_database(0)
	local = {}
	try:
		for row in dbcon.execute('SELECT db_type, media_id, season, episode, resume_point, curr_time, last_played, resume_id, title FROM progress').fetchall():
			key = _history_item_key(_progress_row_to_dict(row))
			if key:
				local[key] = _progress_row_to_dict(row)
	except:
		pass
	if mode == 'replace':
		dbcon.execute('DELETE FROM progress')
		local = {}
	added, updated, kept = 0, 0, 0
	for item in items:
		key = _history_item_key(item)
		if not key:
			continue
		winner = _merge_progress_row(local.get(key), item) if mode == 'merge' and key in local else item
		if key in local and mode == 'merge':
			if winner is local.get(key):
				kept += 1
				continue
			updated += 1
		else:
			added += 1
		dbcon.execute(
			'INSERT OR REPLACE INTO progress VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
			(
				winner['db_type'], winner['media_id'], winner.get('season'), winner.get('episode'),
				str(winner.get('resume_point', '0')), str(winner.get('curr_time', '0')),
				str(winner.get('last_played') or ''), int(winner.get('resume_id') or 0), str(winner.get('title') or ''),
			)
		)
	return 'in progress: %s added, %s updated, %s unchanged' % (added, updated, kept)


def _import_watched(items, mode):
	dbcon = get_database(0)
	local = {}
	try:
		for row in dbcon.execute('SELECT db_type, media_id, season, episode, last_played, title FROM watched').fetchall():
			key = _history_item_key(_watched_row_to_dict(row))
			if key:
				local[key] = _watched_row_to_dict(row)
	except:
		pass
	if mode == 'replace':
		dbcon.execute('DELETE FROM watched')
		local = {}
	added, updated, kept = 0, 0, 0
	for item in items:
		key = _history_item_key(item)
		if not key:
			continue
		winner = _merge_watched_row(local.get(key), item) if mode == 'merge' and key in local else item
		if key in local and mode == 'merge':
			if winner is local.get(key):
				kept += 1
				continue
			updated += 1
		else:
			added += 1
		dbcon.execute(
			'INSERT OR REPLACE INTO watched VALUES (?, ?, ?, ?, ?, ?)',
			(
				winner['db_type'], winner['media_id'], winner.get('season'), winner.get('episode'),
				str(winner.get('last_played') or ''), str(winner.get('title') or ''),
			)
		)
	return 'watched: %s added, %s updated, %s unchanged' % (added, updated, kept)


def _merge_progress_row(local, incoming):
	if not local:
		return incoming
	local_time = float(local.get('curr_time') or 0)
	incoming_time = float(incoming.get('curr_time') or 0)
	if incoming_time > local_time:
		return incoming
	if local_time > incoming_time:
		return local
	local_pct = float(local.get('resume_point') or 0)
	incoming_pct = float(incoming.get('resume_point') or 0)
	if incoming_pct > local_pct:
		return incoming
	if local_pct > incoming_pct:
		return local
	if str(incoming.get('last_played') or '') > str(local.get('last_played') or ''):
		return incoming
	return local


def _merge_watched_row(local, incoming):
	if not local:
		return incoming
	if str(incoming.get('last_played') or '') > str(local.get('last_played') or ''):
		return incoming
	return local
