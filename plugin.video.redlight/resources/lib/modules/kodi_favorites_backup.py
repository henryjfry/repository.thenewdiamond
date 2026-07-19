# -*- coding: utf-8 -*-
import json
import os
import shutil
from datetime import datetime
from xml.etree import ElementTree as ET
from modules import kodi_utils, settings
from modules.import_export_utils import offer_save_export_directory, pick_export_folder
_KODI_FAVORITES_FILENAMES = ('Favourites.xml', 'favourites.xml')

BACKUP_MASK = '.xml'


def _kodi_favorites_path():
	profile = kodi_utils.translate_path('special://profile/')
	for name in _KODI_FAVORITES_FILENAMES:
		path = os.path.join(profile, name)
		if os.path.isfile(path):
			return path
	return os.path.join(profile, 'Favourites.xml')


def _pick_import_file():
	path = kodi_utils.browse_file(BACKUP_MASK, settings.import_export_directory_setting(), heading='Choose Kodi favorites backup', force_defaultt=True)
	if not path:
		return None
	tpath = kodi_utils.translate_path(path)
	if not os.path.isfile(tpath):
		return None
	if not tpath.lower().endswith('.xml'):
		kodi_utils.ok_dialog(heading='Import Kodi favorites', text='Please choose a Kodi favorites backup (.xml).')
		return None
	return tpath


def _parse_favorites_file(path):
	try:
		tree = ET.parse(path)
	except Exception as e:
		raise ValueError('Invalid XML (%s)' % e)
	root = tree.getroot()
	if root.tag.lower() != 'favourites':
		raise ValueError('This file is not a Kodi favorites backup (expected a favourites root element).')
	items = []
	for node in root.findall('favourite'):
		action = (node.text or '').strip()
		if not action:
			continue
		items.append({
			'name': node.get('name') or '',
			'thumb': node.get('thumb') or '',
			'action': action,
		})
	return items


def _write_favorites_file(path, items):
	root = ET.Element('favourites')
	for item in items:
		node = ET.SubElement(root, 'favourite')
		if item.get('name'):
			node.set('name', item['name'])
		if item.get('thumb'):
			node.set('thumb', item['thumb'])
		node.text = item.get('action') or ''
	tree = ET.ElementTree(root)
	kodi_utils.make_directory(os.path.dirname(path))
	with open(path, 'wb') as handle:
		tree.write(handle, encoding='utf-8', xml_declaration=True)


def _compat_note():
	return '[COLOR yellow]Kodi favorites usually only work with the add-on that created them.[/COLOR]'


def export_favorites(params):
	src = _kodi_favorites_path()
	if not os.path.isfile(src):
		return kodi_utils.ok_dialog(heading='Export Kodi favorites', text='No Kodi favorites file found on this profile.')
	try:
		items = _parse_favorites_file(src)
	except Exception as e:
		return kodi_utils.ok_dialog(heading='Export failed', text='Could not read Kodi favorites.[CR][CR]%s' % e)
	if not items:
		return kodi_utils.ok_dialog(heading='Export Kodi favorites', text='Your Kodi favorites file is empty.')
	folder = pick_export_folder(heading='Choose export folder')
	if not folder:
		return
	filename = 'kodi-favorites-%s.xml' % datetime.now().strftime('%Y%m%d-%H%M%S')
	dest = os.path.join(folder, filename)
	count = len(items)
	preview_lines = [
		'[B]%s[/B]' % filename,
		'%s Kodi favorite(s).' % count,
		'',
		_compat_note(),
	]
	if not kodi_utils.confirm_dialog(heading='Export Kodi favorites', text='[CR]'.join(preview_lines), ok_label='Export', cancel_label='Cancel', default_control=10, scroll=True):
		return
	try:
		kodi_utils.make_directory(folder)
		shutil.copy2(src, dest)
	except Exception as e:
		return kodi_utils.ok_dialog(heading='Export failed', text=str(e))
	summary = 'Exported %s Kodi favorite(s) to %s' % (count, filename)
	kodi_utils.ok_dialog(heading='Export complete', text=summary, scroll=True)
	kodi_utils.notification(summary, 6500)
	offer_save_export_directory(folder)


def import_favorites(params):
	path = _pick_import_file()
	if not path:
		return
	try:
		import_items = _parse_favorites_file(path)
	except Exception as e:
		return kodi_utils.ok_dialog(heading='Import failed', text='Could not read that file.[CR][CR]%s' % e)
	if not import_items:
		return kodi_utils.ok_dialog(heading='Import Kodi favorites', text='That file contains no Kodi favorites.')
	dest = _kodi_favorites_path()
	local_items = []
	if os.path.isfile(dest):
		try:
			local_items = _parse_favorites_file(dest)
		except:
			local_items = []
	file_count = len(import_items)
	local_count = len(local_items)
	empty_dest = local_count == 0
	preview_lines = [
		'[B]%s[/B]' % os.path.basename(path),
		'Backup: %s favorite(s).' % file_count,
		'This device: %s favorite(s).' % local_count,
		'',
		_compat_note(),
	]
	if not kodi_utils.confirm_dialog(
		heading='Import Kodi favorites',
		text='[CR]'.join(preview_lines),
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
			('Replace — remove local Kodi favorites first, then import backup', 'replace'),
		]
		list_items = [{'line1': i[0]} for i in mode_choices]
		kwargs = {'items': json.dumps(list_items), 'heading': 'Import mode', 'narrow_window': 'true'}
		mode = kodi_utils.select_dialog([i[1] for i in mode_choices], **kwargs)
		if not mode:
			return
		rules = _import_rules_text(mode)
		if not kodi_utils.confirm_dialog(heading='Import %s' % mode, text=rules, ok_label='Import', cancel_label='Cancel', default_control=10, scroll=True):
			return
		if mode == 'replace':
			if not kodi_utils.confirm_dialog(heading='Replace local data?', text=_replace_warning(local_count), ok_label='Replace', cancel_label='Cancel', default_control=10):
				return
	try:
		if mode == 'merge':
			merged = _merge_favorites(local_items, import_items)
			_write_favorites_file(dest, merged)
			added = len(merged) - len(local_items)
			summary = 'Import complete — %s favorite(s) now (%s added)' % (len(merged), max(added, 0))
		else:
			if os.path.isfile(dest):
				backup = dest + '.redlight.bak'
				shutil.copy2(dest, backup)
			shutil.copy2(path, dest)
			summary = 'Import complete — %s favorite(s) imported (replace)' % file_count
	except Exception as e:
		return kodi_utils.ok_dialog(heading='Import failed', text=str(e))
	kodi_utils.ok_dialog(
		heading='Import complete',
		text='%s[CR][CR][COLOR yellow]Restart Kodi if the Favorites menu does not update.[/COLOR]' % summary,
		scroll=True,
	)
	kodi_utils.notification('Import complete', 6500)


def _import_rules_text(mode):
	if mode == 'merge':
		return 'Kodi favorites: add from backup; keep existing entries.'
	return 'Kodi favorites: replace everything on this device.[CR]A copy of your current Kodi favorites is saved before importing.'


def _replace_warning(local_count):
	return (
		'This will replace %s favorite(s) on this device with the backup.[CR]'
		'Your current Kodi favorites are copied to Favourites.xml.redlight.bak first.'
	) % local_count


def _merge_favorites(local_items, import_items):
	seen = set(i['action'] for i in local_items)
	merged = list(local_items)
	for item in import_items:
		if item['action'] in seen:
			continue
		merged.append(item)
		seen.add(item['action'])
	return merged
