# -*- coding: utf-8 -*-
import json
import time
import requests
from operator import itemgetter
from caches import mdblist_cache
from caches.settings_cache import get_setting, set_setting
from modules import kodi_utils, settings
from modules.utils import sort_for_article, paginate_list, get_datetime, TaskPool, make_thread_list, copy2clip, make_qrcode, make_tinyurl

BASE_URL = 'https://api.mdblist.com/%s'
_OAUTH_DEVICE_URL = 'https://api.mdblist.com/oauth/device-authorization/'
_OAUTH_TOKEN_URL = 'https://api.mdblist.com/oauth/token/'
MAX_LIST_ITEMS = 250_000
session = requests.Session()
session.mount('https://api.mdblist.com', requests.adapters.HTTPAdapter(pool_maxsize=100, max_retries=requests.adapters.Retry(total=4, status_forcelist=(429, 500, 502, 503, 504))))

def _mdblist_token():
	from caches.settings_cache import settings_cache
	token = settings_cache.read_db_value('mdblist.token')
	if token in (None, '0', '', 'empty_setting'):
		token = get_setting('redlight.mdblist.token', '0')
	return token

def _mdblist_oauth_active():
	refresh = get_setting('redlight.mdblist.refresh', '0')
	return refresh not in (None, '0', '', 'empty_setting')

def call_mdblist(path, params=None, json_data=None, method=None):
	params = params or {}
	token = _mdblist_token()
	if not token or token in ('0', 'empty_setting'): return None
	headers = {'Authorization': 'Bearer %s' % token} if _mdblist_oauth_active() else {}
	if not headers: params['apikey'] = token
	try:
		response = session.request(method or 'get', BASE_URL % path.lstrip('/'), params=params, json=json_data, headers=headers, timeout=20)
		if 'json' in response.headers.get('Content-Type', ''):
			result = response.json()
		else:
			result = response.text
		if not response.ok:
			kodi_utils.logger('MDBList', 'HTTP %s %s' % (response.status_code, path))
			return None
		if isinstance(result, list):
			result = {'items': result, 'pagination': {'has_more': response.headers.get('X-Has-More') == 'true'}}
			if next_cursor := response.headers.get('X-Next-Cursor'):
				result['pagination']['next_cursor'] = next_cursor
		return result
	except Exception as e:
		kodi_utils.logger('MDBList Error', str(e))
		return None

def _get_mdbl_paginated_list(url):
	params = {'limit': 1000}
	items = {'movies': [], 'shows': [], 'episodes': [], 'items': []}
	try:
		for _ in range(MAX_LIST_ITEMS // params['limit']):
			result = call_mdblist(url, params=params)
			if not isinstance(result, dict): break
			for key in items:
				if key in result and isinstance(result[key], list):
					items[key].extend(result[key])
			pagination = result.get('pagination') or {}
			if not pagination.get('has_more'): break
			next_cursor = pagination.get('next_cursor')
			if not next_cursor: break
			params['cursor'] = next_cursor
	except: pass
	return items

def _get_mdbl_playback_items():
	return _get_mdbl_paginated_list('sync/playback').get('items', [])

def _tmdb_id_from_ids(ids):
	for key in ('tmdb', 'tmdbid'):
		try:
			if ids.get(key): return str(int(ids[key]))
		except: pass
	return None

def _imdb_from_ids(ids, block=None):
	for source in (ids, block or {}):
		for key in ('imdb', 'imdb_id', 'imdbid'):
			if value := source.get(key):
				return value
	return ''

def _tvdb_from_ids(ids, block=None):
	for source in (ids, block or {}):
		for key in ('tvdb', 'tvdb_id', 'tvdbid'):
			if value := source.get(key):
				return value
	return ''

def _resolve_movie_id(ids):
	if tmdb_id := _tmdb_id_from_ids(ids): return tmdb_id
	from modules import metadata
	for key, id_type in (('imdb', 'imdb_id'), ('imdbid', 'imdb_id')):
		try:
			value = ids.get(key)
			if value: return str(metadata.movie_meta(id_type, value, settings.tmdb_api_key(), settings.mpaa_region(), get_datetime())['tmdb_id'])
		except: pass
	return None

def _resolve_tvshow_id(ids):
	if tmdb_id := _tmdb_id_from_ids(ids): return tmdb_id
	from modules import metadata
	for key, id_type in (('imdb', 'imdb_id'), ('imdbid', 'imdb_id'), ('tvdb', 'tvdb_id'), ('tvdbid', 'tvdb_id')):
		try:
			value = ids.get(key)
			if value: return str(metadata.tvshow_meta(id_type, value, settings.tmdb_api_key(), settings.mpaa_region(), get_datetime())['tmdb_id'])
		except: pass
	return None

def _normalize_mdbl_personal_item(item, media_kind):
	is_movie = media_kind in ('movie', 'movies')
	nested_key = 'movie' if is_movie else 'show'
	block = item.get(nested_key)
	if isinstance(block, dict):
		ids = block.get('ids') or {}
		tmdb_id = _resolve_movie_id(ids) if is_movie else _resolve_tvshow_id(ids)
		title = block.get('title', '')
		year = block.get('year') or block.get('release_year', '')
		imdb_id = ids.get('imdb', '')
		tvdb_id = ids.get('tvdb', '')
	else:
		block = item if isinstance(item, dict) else {}
		ids = block.get('ids') or {}
		tmdb_id = None
		if block.get('tmdb') is not None:
			try: tmdb_id = str(int(block['tmdb']))
			except: pass
		if not tmdb_id:
			merged_ids = dict(ids)
			if block.get('imdb_id'): merged_ids['imdb'] = block['imdb_id']
			if block.get('tvdb_id'): merged_ids['tvdb'] = block['tvdb_id']
			tmdb_id = _resolve_movie_id(merged_ids) if is_movie else _resolve_tvshow_id(merged_ids)
		title = block.get('title', '')
		year = block.get('year') or block.get('release_year', '')
		imdb_id = block.get('imdb_id') or ids.get('imdb', '')
		tvdb_id = block.get('tvdb_id') or ids.get('tvdb', '')
	if not tmdb_id: return None
	return {'id': tmdb_id, 'title': title, 'year': year, 'imdb_id': imdb_id or '', 'tvdb_id': tvdb_id or '',
		'watchlist_at': item.get('watchlist_at', ''), 'collected_at': item.get('collected_at', ''), 'release_date': item.get('release_date', '')}

def _mdbl_item_media_kind(item):
	mediatype = (item.get('mediatype') or item.get('type') or item.get('media_type') or '').lower()
	if mediatype in ('movie', 'movies'): return 'movie'
	if mediatype in ('show', 'shows', 'tvshow', 'tv', 'series'): return 'show'
	if item.get('tvdb_id'): return 'show'
	return 'movie'

def _mdbl_item_to_list_entry(item, media_kind):
	if not isinstance(item, dict): return None
	ids = item.get('ids') or {}
	tmdb_id = _tmdb_id_from_ids(ids)
	if not tmdb_id and item.get('tmdb') is not None:
		try: tmdb_id = str(int(item['tmdb']))
		except: pass
	if not tmdb_id and item.get('mediatype') and item.get('id') is not None:
		try: tmdb_id = str(int(item['id']))
		except: pass
	if tmdb_id:
		return {'id': tmdb_id, 'title': item.get('title', ''), 'year': item.get('year') or item.get('release_year', ''),
			'imdb_id': _imdb_from_ids(ids, item), 'tvdb_id': _tvdb_from_ids(ids, item),
			'watchlist_at': item.get('watchlist_at', ''), 'collected_at': item.get('collected_at', ''), 'release_date': item.get('release_date', '')}
	entry = _normalize_mdbl_personal_item(item, media_kind)
	if entry: return entry
	if item.get('id') is not None:
		try:
			tmdb_id = str(int(item['id']))
			return {'id': tmdb_id, 'title': item.get('title', ''), 'year': item.get('year') or item.get('release_year', ''),
				'imdb_id': _imdb_from_ids(ids, item), 'tvdb_id': _tvdb_from_ids(ids, item),
				'watchlist_at': item.get('watchlist_at', ''), 'collected_at': item.get('collected_at', ''), 'release_date': item.get('release_date', '')}
		except: pass
	return None

def mdbl_list_media_type(list_item, fallback='movie'):
	"""Route param for build_mdbl_list: movie | tvshow from MDBList list metadata."""
	if not isinstance(list_item, dict):
		return 'tvshow' if fallback in ('tv', 'tvshow', 'show', 'shows', 'series') else 'movie'
	mediatype = (list_item.get('mediatype') or list_item.get('media_type') or '').lower()
	if mediatype in ('show', 'shows', 'tvshow', 'tv', 'series'):
		return 'tvshow'
	if mediatype in ('movie', 'movies'):
		return 'movie'
	if fallback in ('tv', 'tvshow', 'show', 'shows', 'series'):
		return 'tvshow'
	return 'movie'

def mdbl_unified_item_tmdb_id(item):
	"""Resolve TMDb id from unified list item payloads (nested show/movie blocks)."""
	entry = _mdbl_item_to_list_entry(item, _mdbl_item_media_kind(item))
	if not entry or not entry.get('id'):
		return None
	try:
		return int(entry['id'])
	except:
		return None

def _mdbl_personal_list(original_list, media_kind):
	is_movie = media_kind in ('movie', 'movies')
	key = 'movies' if is_movie else 'shows'
	raw_items = list(original_list.get(key, []) or [])
	for item in original_list.get('items', []) or []:
		kind = _mdbl_item_media_kind(item)
		if is_movie and kind == 'movie': raw_items.append(item)
		elif not is_movie and kind == 'show': raw_items.append(item)
	normalized = []
	for item in raw_items:
		entry = _mdbl_item_to_list_entry(item, media_kind)
		if entry: normalized.append(entry)
	return normalized

def _mdblist_device_auth_url(device_data):
	verification_url = (device_data.get('verification_uri') or device_data.get('verification_url') or 'https://mdblist.com/oauth/device/').rstrip('/')
	user_code = device_data.get('user_code', '')
	if user_code: return '%s?code=%s' % (verification_url, user_code)
	return verification_url

def mdblist_get_device_code():
	client_id = settings.mdblist_client()
	if not client_id or client_id in ('empty_setting', ''): return None
	try:
		response = session.post(_OAUTH_DEVICE_URL, data={'client_id': client_id, 'scope': 'write'}, timeout=20)
		if not response.ok: return None
		return response.json()
	except: return None

def mdblist_poll_device(device_data):
	device_code, user_code = device_data.get('device_code'), device_data.get('user_code')
	if not device_code or not user_code: return None
	expires_in = int(device_data.get('expires_in') or 300)
	interval = max(int(device_data.get('interval') or 5), 1)
	auth_url = _mdblist_device_auth_url(device_data)
	qr_code = make_qrcode(auth_url) or ''
	copy2clip(auth_url)
	short_url = make_tinyurl(auth_url)
	p_dialog_insert = '[CR]OR visit [B]%s[/B]' % short_url if short_url else ''
	verify_display = (device_data.get('verification_uri') or device_data.get('verification_url') or 'mdblist.com/oauth/device').replace('https://', '')
	content = ('Enter [B]%s[/B] at [B]%s[/B][CR]OR scan the [B]QR Code[/B][CR]Link copied to clipboard%s[CR][CR]'
		'Waiting for authorisation...' % (user_code, verify_display, p_dialog_insert))
	progress = kodi_utils.progress_dialog('MDBList Authorise', qr_code)
	progress.update(content, 0)
	start = time.time()
	while time.time() - start < expires_in:
		if progress.iscanceled():
			progress.close()
			return None
		kodi_utils.sleep(interval * 1000)
		try:
			client_id = settings.mdblist_client()
			response = session.post(_OAUTH_TOKEN_URL, data={
				'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
				'device_code': device_code,
				'client_id': client_id}, timeout=20)
			if response.status_code == 200:
				result = response.json()
				progress.close()
				return result
		except: pass
		progress.update(content, int(100 * (time.time() - start) / float(expires_in)))
	progress.close()
	return None

def mdblist_authenticate(dummy=''):
	device_data = mdblist_get_device_code()
	if not device_data or not device_data.get('user_code'): return kodi_utils.notification('MDBList Authorisation Failed', 3000)
	token_result = mdblist_poll_device(device_data)
	if not token_result: return kodi_utils.notification('MDBList Authorisation Canceled', 3000)
	access_token = token_result.get('access_token')
	if not access_token: return kodi_utils.notification('MDBList Authorisation Failed', 3000)
	set_setting('mdblist.token', access_token)
	set_setting('mdblist.refresh', token_result.get('refresh_token') or '0')
	from caches.settings_cache import settings_cache
	settings_cache.clear_db_cache()
	user_info = call_mdblist('user') or {}
	set_setting('mdblist.user', str(user_info.get('username') or user_info.get('user_id') or 'MDBList User'))
	settings_cache.clear_db_cache()
	mdblist_cache.clear_mdblist_collection_watchlist_data('watchlist')
	try: _mdbl_watchlist_raw()
	except: pass
	switched = settings.offer_watched_provider(3, 'MDBList')
	kodi_utils.notification('MDBList Account Authorised', 3000)
	if switched:
		try: mdblist_sync_activities(force_update=True)
		except Exception as e: kodi_utils.logger('MDBList', 'Post-auth sync failed: %s' % e)
	try: kodi_utils.container_refresh()
	except: pass
	return True

def mdblist_revoke_authentication(dummy=''):
	set_setting('mdblist.user', 'empty_setting')
	set_setting('mdblist.token', '0')
	set_setting('mdblist.refresh', '0')
	settings.fallback_watched_provider_on_revoke(3)
	mdblist_cache.clear_all_mdblist_cache_data(silent=True, refresh=False)
	kodi_utils.notification('MDBList Authorisation Reset', 3000)

def mdblist_force_sync(params=None):
	if not settings.mdblist_user_active(): return kodi_utils.notification('MDBList account not authorised', 3000)
	progress = kodi_utils.progress_dialog('MDBList Sync')
	progress.update('Syncing with MDBList...', 0)
	status = 'failed'
	try:
		status = mdblist_sync_activities(force_update=True, progress=progress)
	except Exception as e:
		kodi_utils.logger('MDBList', 'Force sync failed: %s' % e)
		status = 'failed'
	finally:
		kodi_utils.close_progress_dialog(progress)
	if status == 'canceled': return status
	if status == 'failed': kodi_utils.notification('MDBList Sync Failed', 3000)
	elif status != 'no account':
		kodi_utils.notification('MDBList Sync Complete', 3000)
		kodi_utils.kodi_refresh()
	return status

def _mdbl_watched_unwatched(action, media, media_id, tvdb_id=0, season=None, episode=None, key='tmdb'):
	if action == 'mark_as_watched': url, result_key = 'sync/watched', 'updated'
	else: url, result_key = 'sync/watched/remove', 'removed'
	try: media_id = int(media_id)
	except: pass
	if media == 'movies':
		success_key, data = 'movies', {'movies': [{'ids': {key: media_id}}]}
	elif media == 'episode':
		success_key = 'episodes'
		data = {'shows': [{'ids': {key: media_id}, 'seasons': [{'number': int(season), 'episodes': [{'number': int(episode)}]}]}]}
	elif media == 'shows':
		success_key, data = 'episodes', {'shows': [{'ids': {key: media_id}}]}
	else:
		success_key = 'episodes'
		data = {'shows': [{'ids': {key: media_id}, 'seasons': [{'number': int(season)}]}]}
	result = call_mdblist(url, json_data=data, method='post')
	if not isinstance(result, dict): return False
	success = result.get(result_key, {}).get(success_key, 0) > 0
	if not success and media != 'movies' and tvdb_id:
		return _mdbl_watched_unwatched(action, media, tvdb_id, 0, season, episode, 'tvdb')
	return success

def mdblist_watched_status_mark(action, media_type, tmdb_id, tvdb_id=0, season=None, episode=None):
	if media_type == 'movie': media = 'movies'
	elif media_type == 'episode': media = 'episode'
	elif media_type == 'season': media = 'season'
	else: media = 'shows'
	success = _mdbl_watched_unwatched(action, media, tmdb_id, tvdb_id, season, episode)
	if success and action == 'mark_as_unwatched': mdblist_sync_activities()
	return success

def mdblist_official_status(media_type):
	if kodi_utils.service_scrobbler_defer('service.mdblist-scrobbler',
		auth_keys=('api_key', 'apikey', 'token', 'mdblist_api_key', 'mdblist.token', 'refresh_token'),
		scrobble_enable_keys=('scrobble', 'scrobble_enabled', 'enable_scrobble', 'scrobble_movies', 'scrobble_episodes')): return False
	return True

def mdblist_progress(action, media_type, tmdb_id, percent, season=None, episode=None, resume_id=None, refresh_mdblist=False):
	if action == 'clear_progress':
		call_mdblist('scrobble/clear', json_data={'id': resume_id}, method='post')
	else:
		try: tmdb_id = int(tmdb_id)
		except: pass
		if media_type == 'movie':
			payload = {'movie': {'ids': {'tmdb': tmdb_id}}, 'progress': float(percent)}
		else:
			payload = {'show': {'ids': {'tmdb': tmdb_id}, 'season': {'number': int(season), 'episode': {'number': int(episode)}}}, 'progress': float(percent)}
		call_mdblist('scrobble/pause', json_data=payload, method='post')
	if refresh_mdblist: mdblist_sync_activities(force_update=True)

def mdblist_reset_scrobble(params):
	if not settings.mdblist_user_active(): return
	tmdb_id = params.get('tmdb_id')
	tvdb_id = params.get('tvdb_id', 'None')
	season, episode = params.get('season'), params.get('episode')
	media_type = params.get('media_type') or params.get('content') or 'movie'
	from modules.watched_status import get_database, get_bookmarks_movie, get_bookmarks_episode
	watched_db = get_database(3)
	try:
		if media_type == 'movie':
			resume_id = get_bookmarks_movie(watched_db).get(str(tmdb_id), {}).get('resume_id')
			if resume_id: mdblist_progress('clear_progress', 'movie', tmdb_id, 0, resume_id=resume_id)
		else:
			bookmarks = get_bookmarks_episode(str(tmdb_id), season, watched_db)
			if episode and bookmarks:
				resume_id = bookmarks.get(int(episode), {}).get('resume_id')
				if resume_id: mdblist_progress('clear_progress', 'episode', tmdb_id, 0, season, episode, resume_id)
	except: pass
	mdblist_sync_activities(force_update=True)
	kodi_utils.notification('MDBList Scrobble Reset', 3000)
	kodi_utils.kodi_refresh()

_MDBL_DROPPED_CACHE_KEY = 'mdblist_hidden_items_dropped'

def mdblist_get_dropped_items():
	cached = mdblist_cache.mdblist_cache.get(_MDBL_DROPPED_CACHE_KEY)
	if cached is not None: return cached
	items = []
	result = call_mdblist('sync/dropped')
	if isinstance(result, dict):
		for item in result.get('shows', []):
			try:
				show = item.get('show', item)
				tmdb_id = _resolve_tvshow_id(show.get('ids', {}))
				if tmdb_id: items.append(int(tmdb_id))
			except: pass
	mdblist_cache.mdblist_cache.set(_MDBL_DROPPED_CACHE_KEY, items)
	return items

def _mdblist_dropped_payload(tmdb_id, imdb_id=None):
	payload = {'shows': [{'ids': {'tmdb': int(tmdb_id)}}]}
	if imdb_id and imdb_id not in ('None', '', '0'): payload['shows'][0]['ids']['imdb'] = imdb_id
	return payload

def _mdblist_resolve_show_imdb(tmdb_id, imdb_id=None):
	if imdb_id and imdb_id not in ('None', '', '0'): return imdb_id
	try:
		from modules.metadata import tvshow_meta
		from modules.settings import tmdb_api_key, mpaa_region
		from modules.utils import get_datetime
		meta = tvshow_meta('tmdb_id', tmdb_id, tmdb_api_key(), mpaa_region(), get_datetime())
		imdb_id = meta.get('imdb_id')
		if imdb_id and imdb_id not in ('None', '', '0'): return imdb_id
	except: pass
	return None

def mdblist_hide_unhide_progress_items(params):
	action, media_id = params['action'], params.get('media_id')
	imdb_id = params.get('imdb_id')
	mediatype = 'movies' if params.get('media_type') in ('movie', 'movies') else 'shows'
	if action in ('drop', 'hide'): action = 'hide'
	elif action in ('undrop', 'unhide'): action = 'unhide'
	elif action not in ('hide', 'unhide'):
		hidden = mdblist_get_dropped_items()
		action = 'unhide' if int(media_id) in hidden else 'hide'
	url = 'sync/dropped' if action == 'hide' else 'sync/dropped/remove'
	if mediatype == 'movies':
		json_data = {'movies': [{'ids': {'tmdb': int(media_id)}}]}
	else:
		json_data = _mdblist_dropped_payload(media_id, _mdblist_resolve_show_imdb(media_id, imdb_id))
	call_mdblist(url, json_data=json_data, method='post')
	mdblist_cache.mdblist_cache.delete(_MDBL_DROPPED_CACHE_KEY)
	mdblist_sync_activities()
	kodi_utils.kodi_refresh()
	if action == 'hide': kodi_utils.notification('Dropped from MDBList Progress', 3000)
	else: kodi_utils.notification('Removed from MDBList Dropped', 3000)

def mdblist_indicators_movies(watched_info):
	insert_list = []
	def _process(item):
		tmdb_id = _resolve_movie_id(item.get('movie', {}).get('ids', {}))
		if tmdb_id: insert_list.append(('movie', tmdb_id, '', '', item.get('last_watched_at', ''), item.get('movie', {}).get('title', '')))
	movies = watched_info.get('movies', [])
	for i in TaskPool().tasks(_process, movies, min(len(movies), settings.max_threads())): i.join()
	mdblist_cache.mdblist_watched_cache.set_bulk_movie_watched(insert_list)

def mdblist_indicators_tv(watched_info):
	insert_list = []
	def _process(item):
		show_ids = item.get('episode', {}).get('show', {}).get('ids', {})
		tmdb_id = _resolve_tvshow_id(show_ids)
		if not tmdb_id: return
		ep = item.get('episode', {})
		insert_list.append(('episode', tmdb_id, ep.get('season'), ep.get('number'), item.get('last_watched_at', ''), ep.get('show', {}).get('title', '')))
	episodes = watched_info.get('episodes', [])
	for i in TaskPool().tasks(_process, episodes, min(len(episodes), settings.max_threads())): i.join()
	mdblist_cache.mdblist_watched_cache.set_bulk_tvshow_watched(insert_list)

def mdblist_progress_movies(progress_info):
	insert_list = []
	def _process(item):
		tmdb_id = _resolve_movie_id(item.get('movie', {}).get('ids', {}))
		if tmdb_id:
			insert_list.append(('movie', tmdb_id, '', '', str(round(float(item['progress']), 1)), 0, item.get('paused_at', ''), item['id'], item.get('movie', {}).get('title', '')))
	threads = list(make_thread_list(_process, [i for i in progress_info if i.get('type') == 'movie' and float(i.get('progress', 0)) > 1]))
	[i.join() for i in threads]
	mdblist_cache.mdblist_watched_cache.set_bulk_movie_progress(insert_list)

def mdblist_progress_tv(progress_info):
	insert_list = []
	def _process(item):
		tmdb_id = _resolve_tvshow_id(item.get('show', {}).get('ids', {}))
		if not tmdb_id: return
		season, episode = item.get('episode', {}).get('season'), item.get('episode', {}).get('number')
		if season and int(season) > 0:
			insert_list.append(('episode', tmdb_id, season, episode, str(round(float(item['progress']), 1)), 0, item.get('paused_at', ''), item['id'], item.get('show', {}).get('title', '')))
	threads = list(make_thread_list(_process, [i for i in progress_info if i.get('type') == 'episode' and float(i.get('progress', 0)) > 1]))
	[i.join() for i in threads]
	mdblist_cache.mdblist_watched_cache.set_bulk_tvshow_progress(insert_list)

def mdblist_sync_activities(params=None, force_update=False, progress=None):
	if isinstance(params, dict): force_update = params.get('force_update', 'false') in ('true', 'True', True) or force_update
	if not settings.mdblist_user_active(): return 'no account'
	def _sync_canceled():
		return progress and progress.iscanceled()
	if force_update:
		mdblist_cache.clear_all_mdblist_cache_data(silent=True, refresh=False)
	if _sync_canceled(): return 'canceled'
	latest = call_mdblist('sync/last_activities')
	if not latest: return 'failed'
	if _sync_canceled(): return 'canceled'
	cached = mdblist_cache.reset_activity(latest)
	def _changed(key):
		try: return (latest.get(key) or '') > (cached.get(key) or '')
		except: return True
	success = 'not needed'
	if force_update or _changed('collected_at'):
		success = 'success'
		mdblist_cache.clear_mdblist_collection_watchlist_data('collection')
	if _sync_canceled(): return 'canceled'
	if force_update or _changed('watchlisted_at'):
		success = 'success'
		mdblist_cache.clear_mdblist_collection_watchlist_data('watchlist')
	if _sync_canceled(): return 'canceled'
	if force_update or _changed('dropped_at'):
		success = 'success'
		mdblist_cache.mdblist_cache.delete(_MDBL_DROPPED_CACHE_KEY)
	if _sync_canceled(): return 'canceled'
	if force_update or _changed('list_updated_at'):
		success = 'success'
		for list_type in ('external', 'my_lists'):
			mdblist_cache.clear_mdblist_list_data(list_type)
			mdblist_cache.clear_mdblist_list_contents_data(list_type)
		mdblist_cache.mdblist_cache.delete('mdblist_liked_lists')
	refresh_movies = force_update or _changed('watched_at')
	refresh_episodes = force_update or _changed('episode_watched_at')
	refresh_movie_pause = force_update or _changed('paused_at')
	refresh_episode_pause = force_update or _changed('episode_paused_at')
	if refresh_movies or refresh_episodes:
		if _sync_canceled(): return 'canceled'
		success = 'success'
		watched_info = _get_mdbl_paginated_list('sync/watched')
		if _sync_canceled(): return 'canceled'
		if refresh_movies: mdblist_indicators_movies(watched_info)
		if _sync_canceled(): return 'canceled'
		if refresh_episodes: mdblist_indicators_tv(watched_info)
	if refresh_movie_pause or refresh_episode_pause:
		if _sync_canceled(): return 'canceled'
		success = 'success'
		items = _get_mdbl_playback_items()
		if _sync_canceled(): return 'canceled'
		if refresh_movie_pause: mdblist_progress_movies(items)
		if _sync_canceled(): return 'canceled'
		if refresh_episode_pause: mdblist_progress_tv(items)
	return success

def _mdbl_collection_watchlist_items(string, url):
	return mdblist_cache.cache_mdblist_object(_get_mdbl_paginated_list, string, url) or {'movies': [], 'shows': []}

def _mdbl_watchlist_raw():
	string, url = 'mdblist_watchlist_live', 'watchlist/items'
	return mdblist_cache.cache_mdblist_object(_get_mdbl_paginated_list, string, url) or {'movies': [], 'shows': [], 'items': []}

def mdblist_watchlist(media_kind, page_no):
	# Umbrella/POV: plain GET watchlist/items → flat movies[]/shows[] (id = TMDb, imdb_id on item).
	raw = _mdbl_watchlist_raw()
	key = 'movies' if media_kind in ('movie', 'movies') else 'shows'
	original_list = list(raw.get(key) or [])
	if not original_list:
		for item in raw.get('items') or []:
			kind = _mdbl_item_media_kind(item)
			if key == 'movies' and kind == 'movie': original_list.append(item)
			elif key == 'shows' and kind == 'show': original_list.append(item)
	if not original_list:
		kodi_utils.logger('MDBList Watchlist', 'No %s items (movies=%s shows=%s)' % (
			media_kind, len(raw.get('movies') or []), len(raw.get('shows') or [])))
	else:
		kodi_utils.logger('MDBList Watchlist', '%s: %s items' % (media_kind, len(original_list)))
	normalized = []
	for item in original_list:
		entry = _mdbl_item_to_list_entry(item, media_kind)
		if entry: normalized.append(entry)
	if original_list and not normalized:
		kodi_utils.logger('MDBList Watchlist', 'Could not resolve TMDb ids from %s raw items' % len(original_list))
	original_list = normalized
	sort_key = settings.lists_sort_order('watchlist')
	if sort_key == 2: original_list.sort(key=itemgetter('release_date'), reverse=True)
	elif sort_key == 1: original_list.sort(key=itemgetter('watchlist_at'), reverse=True)
	else: original_list = sort_for_article(original_list, 'title', settings.ignore_articles())
	is_home = kodi_utils.external()
	if settings.paginate(is_home): return paginate_list(original_list, page_no, settings.page_limit(is_home))
	return original_list, 1

def mdblist_collection(media_kind, page_no):
	string, url = 'mdblist_collection', 'sync/collection'
	original_list = _mdbl_personal_list(_mdbl_collection_watchlist_items(string, url), media_kind)
	sort_key = settings.lists_sort_order('collection')
	if sort_key == 2: original_list.sort(key=itemgetter('year'), reverse=True)
	elif sort_key == 1: original_list.sort(key=itemgetter('collected_at'), reverse=True)
	else: original_list = sort_for_article(original_list, 'title', settings.ignore_articles())
	is_home = kodi_utils.external()
	if settings.paginate(is_home): return paginate_list(original_list, page_no, settings.page_limit(is_home))
	return original_list, 1

def mdblist_droplist(media_kind, page_no):
	return [{'id': i, 'imdb_id': ''} for i in mdblist_get_dropped_items()], 1

def mdbl_get_lists(list_type):
	if list_type == 'external': string, url = 'mdblist_external', 'external/lists/user'
	else: string, url = 'mdblist_my_lists', 'lists/user'
	result = mdblist_cache.cache_mdblist_object(call_mdblist, string, url)
	if isinstance(result, dict): return result.get('items', [])
	return result or []

def _mdbl_normalize_list_response(result):
	if isinstance(result, list): return result
	if isinstance(result, dict):
		for key in ('items', 'lists', 'liked', 'data', 'results'):
			if isinstance(result.get(key), list): return result[key]
	return []

def _mdbl_list_matches_media_type(item, media_type):
	if not media_type: return True
	mediatype = (item.get('mediatype') or item.get('media_type') or '').lower()
	if not mediatype: return True
	if media_type in ('movie', 'movies'): return mediatype in ('movie', 'movies')
	return mediatype in ('show', 'shows', 'tvshow', 'tv', 'series')

def mdbl_get_liked_lists(media_type=None):
	result = mdblist_cache.cache_mdblist_object(call_mdblist, 'mdblist_liked_lists', 'lists/liked')
	lists = _mdbl_normalize_list_response(result)
	if not media_type: return lists
	return [i for i in lists if _mdbl_list_matches_media_type(i, media_type)]

def mdbl_top_lists():
	result = mdblist_cache.cache_mdblist_object(call_mdblist, 'mdblist_top_lists', 'lists/top')
	if isinstance(result, dict): return result.get('items', [])
	return result or []

def get_mdbl_list_contents(list_type, list_id):
	string = 'mdblist_list_contents_%s_%s' % (list_type, list_id)
	if list_type == 'external': url = 'external/lists/%s/items?unified=true' % list_id
	else: url = 'lists/%s/items?unified=true' % list_id
	result = mdblist_cache.cache_mdblist_object(_get_mdbl_paginated_list, string, url)
	return result.get('items', []) if isinstance(result, dict) else []

def _mdblist_list_payload(media_type, tmdb_id, imdb_id=None):
	if media_type == 'movie':
		payload = {'movies': [{'ids': {'tmdb': int(tmdb_id)}}]}
	else:
		payload = {'shows': [{'ids': {'tmdb': int(tmdb_id)}}]}
		if imdb_id and imdb_id not in ('None', '', '0'): payload['shows'][0]['ids']['imdb'] = imdb_id
	return payload

def mdblist_add_to_watchlist(tmdb_id, media_type, imdb_id=None):
	result = call_mdblist('watchlist/items/add', json_data=_mdblist_list_payload(media_type, tmdb_id, imdb_id), method='post')
	if isinstance(result, dict) and result.get('added', {}).get('movies', 0) + result.get('added', {}).get('shows', 0) > 0:
		mdblist_sync_activities()
		return kodi_utils.notification('Added to MDBList Watchlist', 3000)
	return kodi_utils.notification(kodi_utils.LIST_ITEM_NOT_IN_LIST, 3000)

def mdblist_remove_from_watchlist(tmdb_id, media_type, imdb_id=None):
	result = call_mdblist('watchlist/items/remove', json_data=_mdblist_list_payload(media_type, tmdb_id, imdb_id), method='post')
	if isinstance(result, dict) and result.get('removed', {}).get('movies', 0) + result.get('removed', {}).get('shows', 0) > 0:
		mdblist_sync_activities()
		kodi_utils.kodi_refresh()
		return kodi_utils.notification('Removed from MDBList Watchlist', 3000)
	return kodi_utils.notification(kodi_utils.LIST_ITEM_NOT_IN_LIST, 3000)

def mdblist_add_to_library(tmdb_id, media_type, imdb_id=None):
	result = call_mdblist('sync/collection', json_data=_mdblist_list_payload(media_type, tmdb_id, imdb_id), method='post')
	if isinstance(result, dict) and result.get('updated', {}).get('movies', 0) + result.get('updated', {}).get('shows', 0) > 0:
		mdblist_sync_activities()
		return kodi_utils.notification('Added to MDBList Library', 3000)
	return kodi_utils.notification(kodi_utils.LIST_ITEM_NOT_IN_LIST, 3000)

def mdblist_remove_from_library(tmdb_id, media_type, imdb_id=None):
	result = call_mdblist('sync/collection/remove', json_data=_mdblist_list_payload(media_type, tmdb_id, imdb_id), method='post')
	if isinstance(result, dict) and result.get('removed', {}).get('movies', 0) + result.get('removed', {}).get('shows', 0) > 0:
		mdblist_sync_activities()
		kodi_utils.kodi_refresh()
		return kodi_utils.notification('Removed from MDBList Library', 3000)
	return kodi_utils.notification(kodi_utils.LIST_ITEM_NOT_IN_LIST, 3000)

def _mdbl_personal_tmdb_ids(media_kind, fetch_func):
	try:
		data, _ = fetch_func(media_kind, 1)
	except: return set()
	ids = set()
	for item in data or []:
		if not isinstance(item, dict): continue
		tmdb_id = item.get('id') or item.get('tmdb') or (item.get('ids') or {}).get('tmdb')
		if tmdb_id:
			try: ids.add(int(tmdb_id))
			except: pass
	return ids

def _mdbl_item_in_watchlist(list_media, tmdb_id):
	try: tmdb_id = int(tmdb_id)
	except: return False
	media_kind = 'movies' if list_media == 'movie' else 'shows'
	return tmdb_id in _mdbl_personal_tmdb_ids(media_kind, mdblist_watchlist)

def _mdbl_item_in_library(list_media, tmdb_id):
	try: tmdb_id = int(tmdb_id)
	except: return False
	media_kind = 'movies' if list_media == 'movie' else 'shows'
	return tmdb_id in _mdbl_personal_tmdb_ids(media_kind, mdblist_collection)

def _mdbl_item_in_dropped(tmdb_id):
	try: tmdb_id = int(tmdb_id)
	except: return False
	return tmdb_id in mdblist_get_dropped_items()

def mdblist_manager_choice(params):
	if not settings.mdblist_user_active(): return kodi_utils.notification('No Active MDBList Account', 3500)
	media_type = params.get('media_type') or params.get('content') or 'movie'
	list_media = 'movie' if media_type == 'movie' else 'tvshow'
	icon = params.get('icon') or kodi_utils.get_icon('mdblist')
	tmdb_id, imdb_id, tvdb_id = params.get('tmdb_id'), params.get('imdb_id'), params.get('tvdb_id')
	choices = []
	if _mdbl_item_in_watchlist(list_media, tmdb_id):
		choices.append(('Remove from [B]MDBList Watchlist[/B]', 'remove_watchlist'))
	else:
		choices.append(('Add to [B]MDBList Watchlist[/B]', 'add_watchlist'))
	if _mdbl_item_in_library(list_media, tmdb_id):
		choices.append(('Remove from [B]MDBList Library[/B]', 'remove_library'))
	else:
		choices.append(('Add to [B]MDBList Library[/B]', 'add_library'))
	if list_media != 'movie':
		if _mdbl_item_in_dropped(tmdb_id):
			choices.append(('Undrop [B]TV Show[/B]', 'undrop'))
		else:
			choices.append(('Drop [B]TV Show[/B]', 'drop'))
	choices.extend([
		('Mark as [B]Watched[/B]', 'mark_watched'),
		('Mark as [B]Unwatched[/B]', 'mark_unwatched'),
		('Reset [B]Scrobble[/B]', 'reset_scrobble'),
		('Open [B]MDBList Watchlist[/B]', 'open_watchlist'),
		('Open [B]MDBList Library[/B]', 'open_library'),
	])
	if list_media != 'movie':
		choices.append(('Open [B]Dropped TV Shows[/B]', 'open_dropped'))
	choices.extend([
		('Open [B]Liked Lists[/B]', 'open_liked_lists'),
		('Open [B]My MDBLists[/B]', 'open_my_lists'),
		('Refresh Widgets', 'refresh'),
	])
	list_items = [{'line1': item[0], 'icon': icon} for item in choices]
	choice = kodi_utils.select_dialog([i[1] for i in choices], **{'items': json.dumps(list_items), 'heading': 'MDBList Manager'})
	if choice is None: return
	if choice == 'refresh':
		kodi_utils.kodi_refresh()
		return kodi_utils.notification('Widgets Refreshed', 2500)
	watchlist_label = 'Movies Watchlist' if list_media == 'movie' else 'TV Shows Watchlist'
	library_label = 'Movies Library' if list_media == 'movie' else 'TV Shows Library'
	watchlist_mode = 'build_movie_list' if list_media == 'movie' else 'build_tvshow_list'
	library_mode = 'build_movie_list' if list_media == 'movie' else 'build_tvshow_list'
	open_modes = {
		'open_watchlist': {'mode': watchlist_mode, 'action': 'mdblist_watchlist', 'category_name': watchlist_label},
		'open_library': {'mode': library_mode, 'action': 'mdblist_collection', 'category_name': library_label},
		'open_dropped': {'mode': 'build_tvshow_list', 'action': 'mdblist_droplist', 'category_name': 'Dropped TV Shows'},
		'open_liked_lists': {'mode': 'mdblist.get_mdbl_liked_lists', 'name': 'Liked Lists', 'media_type': media_type},
		'open_my_lists': {'mode': 'mdblist.get_mdbl_lists', 'name': 'My Lists', 'media_type': media_type},
	}
	if choice in open_modes:
		return kodi_utils.container_update(open_modes[choice])
	if choice == 'mark_watched':
		from indexers.dialogs import _trakt_manager_mark
		return _trakt_manager_mark(params, 'mark_as_watched')
	if choice == 'mark_unwatched':
		from indexers.dialogs import _trakt_manager_mark
		return _trakt_manager_mark(params, 'mark_as_unwatched')
	if choice == 'reset_scrobble':
		return mdblist_reset_scrobble(params)
	if choice == 'add_watchlist':
		return mdblist_add_to_watchlist(tmdb_id, list_media, imdb_id)
	if choice == 'remove_watchlist':
		return mdblist_remove_from_watchlist(tmdb_id, list_media, imdb_id)
	if choice == 'add_library':
		return mdblist_add_to_library(tmdb_id, list_media, imdb_id)
	if choice == 'remove_library':
		return mdblist_remove_from_library(tmdb_id, list_media, imdb_id)
	if choice == 'drop':
		return mdblist_hide_unhide_progress_items({'action': 'drop', 'media_type': 'shows', 'media_id': tmdb_id, 'imdb_id': imdb_id})
	if choice == 'undrop':
		return mdblist_hide_unhide_progress_items({'action': 'undrop', 'media_type': 'shows', 'media_id': tmdb_id, 'imdb_id': imdb_id})

def get_mdbl_lists(params):
	from indexers import mdblist_lists
	return mdblist_lists.get_mdbl_lists(params)

def get_mdbl_liked_lists(params):
	from indexers import mdblist_lists
	return mdblist_lists.get_mdbl_liked_lists(params)

def get_mdbl_top_lists(params):
	from indexers import mdblist_lists
	return mdblist_lists.get_mdbl_top_lists(params)

def build_mdbl_list(params):
	from indexers import mdblist_lists
	return mdblist_lists.build_mdbl_list(params)

def build_mdbl_watchlist(params):
	from indexers import mdblist_lists
	return mdblist_lists.build_mdbl_watchlist(params)

def build_mdbl_library(params):
	from indexers import mdblist_lists
	return mdblist_lists.build_mdbl_library(params)
