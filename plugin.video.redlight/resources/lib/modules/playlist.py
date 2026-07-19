import xbmc, xbmcgui, xbmcvfs
#import os, urllib.parse, requests
from modules.player import RedLightPlayer
import uuid
import base64
import json
from modules import source_utils, kodi_utils

from modules.kodi_utils import addon_fanart
from windows.base_window import BaseDialog
import threading
from threading import Thread
from windows.base_window import open_window
from modules import debrid, settings, metadata, watched_status
from modules.episode_tools import EpisodeTools
from modules.sources import Sources
from modules import metadata
from modules.metadata import episodes_meta, all_episodes_meta
from modules.utils import normalize
from caches.settings_cache import get_setting
import time

pause_time_before_end, hold_pause_time = 10, 900
episode_flag_base = 'fenlight_flags/episodes/%s.png'
button_actions = {10: 'close', 11: 'play', 12: 'cancel', 13: 'stop'}
set_resume, set_watched = 5, 90

from inspect import currentframe, getframeinfo
#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)

PROP_SOURCES_BUSY = 'redlight.sources_busy'
PROP_SOURCES_OWNER = 'redlight.sources_busy_owner'
PROP_RESOLVE_BUSY = 'redlight.resolve_busy'
PROP_RESOLVE_OWNER = 'redlight.resolve_busy_owner'
PROP_RESOLVE_CANCEL = 'redlight.resolve_cancelled'
PROP_PLAY_OPENING = 'redlight.play_opening'
PROP_BROWSE_RETURN_SOURCES = 'redlight.browse_return_sources'
PROP_NEXTEP_SCRAPE_READY = 'redlight.nextep_scrape_ready'
PROP_NEXTEP_SCRAPE_KEY = 'redlight.nextep_scrape_key'

episode_status_dict = {
'season_premiere': 'b30385b5',
'mid_season_premiere': 'b385b503',
'series_premiere': 'b30385b5',
'series_finale': 'b38503b5',
'season_finale': 'b3b50385',
'mid_season_finale': 'b3b58503',
'':  ''}
 



##SOURCES__def_playback_prep
#-:		#if self._playback_already_active() and not self.background:
#-:		#	return
#-:		#if not self.prescrape and not self._playback_skips_prescrape_override() and settings.prescrape_enabled(self.media_type, self.active_internal_scrapers):
#-:		#	self.prescrape = True


#+:		self.make_search_info()
#+:		import modules.playlist as playlist_module
#+:		return playlist_module.sources_def_playback_prep_return(self, self.params)


def sources_def_playback_prep_return(sources_object, params):
	##self.make_search_info()

	xbmcgui.Window(10000).clearProperty(PROP_SOURCES_BUSY)
	xbmcgui.Window(10000).clearProperty(PROP_SOURCES_OWNER)
	xbmcgui.Window(10000).clearProperty(PROP_RESOLVE_BUSY)
	xbmcgui.Window(10000).clearProperty(PROP_RESOLVE_OWNER)
	xbmcgui.Window(10000).clearProperty(PROP_RESOLVE_CANCEL)
	xbmcgui.Window(10000).clearProperty(PROP_PLAY_OPENING)
	xbmcgui.Window(10000).clearProperty(PROP_BROWSE_RETURN_SOURCES)
	xbmcgui.Window(10000).clearProperty(PROP_NEXTEP_SCRAPE_READY)
	xbmcgui.Window(10000).clearProperty(PROP_NEXTEP_SCRAPE_KEY)

	#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
	#xbmc.log(str(sources_object.__dict__), level=xbmc.LOGINFO)
	#xbmc.log(str(params), level=xbmc.LOGINFO)

	if sources_object.params.get('autoplay', '') == 'false':
		from caches import base_cache
		cache_list = ('rd_cloud','internal_scrapers','external_scrapers','pm_cloud','rd_cloud','ad_cloud','oc_cloud','tb_cloud','pm_cloud', 'rd_cloud', 'ad_cloud', 'oc_cloud', 'tb_cloud', 'folders')
		results2 = []
		for cache_type in cache_list:
			success = base_cache.clear_cache(cache_type, silent=True)
			results2.append(success)

	if sources_object.autoscrape: 
		#sources_object.autoscrape_nextep_handler()
		return sources_object.get_sources()
	else: 
		return sources_object.get_sources()



#	def resolve_internal(self, scrape_provider, item_id, url_dl, direct_debrid_link=False, cloud_media_type=None):
###
#-:				elif any(i in scrape_provider for i in ('rd_', 'ad_', 'tb_')):
#-:					url = debrid_function().unrestrict_link(item_id)
#+:				elif any(i in scrape_provider for i in ('rd_', 'ad_', 'tb_')):
#+:					import modules.playlist as playlist_module
#+:					url = playlist_module.sources_def_resolve_internal_fix_debrid(debrid_function, scrape_provider, direct_debrid_link, url_dl, item_id)


def sources_def_resolve_internal_fix_debrid(debrid_function, scrape_provider, direct_debrid_link, url_dl, item_id):
	if scrape_provider == 'rd_cloud':
		# ✅ Direct RD links should NEVER be re-resolved
		if direct_debrid_link and url_dl:
			url = url_dl
		elif item_id and item_id.startswith('http'):
			url = item_id
		else:
			url = debrid_function().unrestrict_link(item_id)
	elif any(i in scrape_provider for i in ('ad_', 'tb_')):
		url = debrid_function().unrestrict_link(item_id)
	return url



#	def resolve_sources(self, item, meta=None):
###
#		import modules.playlist as playlist_module
#		url = playlist_module.sources_def_resolve_sources_fix_debrid(self,url, item)
#		return url

def sources_def_resolve_sources_fix_debrid(sources_object, url, item):
	# ✅ FIX: handle RD /d/ links
	if item.get('direct_debrid_link') and item.get('url_dl'):
		url = item['url_dl']
	elif item.get('url_dl'):
		url = item['url_dl']

	if url and 'real-debrid.com/d/' in url:
		xbmc.sleep(3000)
		debrid_function = sources_object.debrid_importer('Real-Debrid')
		try:
			# attempt to resolve again
			url2 = debrid_function().unrestrict_link(url)
			if url2 and 'real-debrid.com/d/' not in url2:
				url = url2
			else:
				# fallback: try legacy unrestricted endpoint
				xbmc.sleep(3000)
				url2 = debrid_function().unrestrict_link(url)
				return url2
		except:
			pass
	return url


#	def _make_resume_dialog(self, percent):
#		import modules.playlist as playlist_module
#		return playlist_module.make_resume_choice()

def make_resume_choice():

	#playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	#pl_size = playlist.size()
	#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
	#xbmc.log(str(playlist.size())+'===>pl_size', level=xbmc.LOGINFO)
	#if xbmc.Player().isPlayingVideo() == True:
	#	xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)

	try:
		if xbmc.Player().isPlayingVideo():
			return 'start_over'
		return 'resume'
	except:
		return 'resume'

#	def _make_nextep_dialog(self, default_action='cancel'):
#		import modules.playlist as playlist_module
#		return playlist_module.NEW_nextep_dialog(self, default_action)


def NEW_nextep_dialog(sources_object, default_action):
	try:
		sources_object._kill_progress_dialog()
		kodi_utils.close_all_dialog()
		def _run():
			try:
				open_window(('modules.playlist', 'NextEpisode'), 'next_episode.xml', meta=sources_object.meta, default_action=default_action)
			except:
				pass
		Thread(target=_run, daemon=True).start()
	except:
		pass
	return None

#	def results(self, info):
#			import modules.playlist as playlist_module
#			self.folder_queries = playlist_module.rd_cloud_def_results_alias_fix(title, aliases)

def rd_cloud_def_results_alias_fix(title, aliases):
	##self.folder_queries = rd_cloud_def_results_alias_fix(title, aliases)
	##def _scrape_cloud(self):
	#OLD:elif not self.folder_query in folder_name: continue
	#NEW:elif not any(q in folder_name for q in self.folder_queries): continue
	##def _scrape_downloads(self):
	#OLD:if not self.folder_query in folder_name: continue
	#NEW:if not any(q in folder_name for q in self.folder_queries): continue

	folder_queries = []
	try:
		alias_list = aliases or []
		all_titles = [title] + alias_list
		folder_queries  = [source_utils.clean_title(normalize(t)) for t in all_titles if t ]
	except:
		pass
	return folder_queries



def run_source_select_flow(sources_object, results):
	while True:

		window_format, window_number = settings.results_format()

		window_result = open_window(
			('windows.sources', 'SourcesResults'),
			'sources_results.xml',
			window_format=window_format,
			window_id=window_number,
			results=results,
			meta=sources_object.meta,
			sources_ref=sources_object,
			episode_group_label=sources_object.episode_group_label,
			scraper_settings=sources_object.scraper_settings,
			prescrape=sources_object.prescrape,
			filters_ignored=sources_object.filters_ignored,
			uncached_results=sources_object.uncached_results,
			cache_check_override=sources_object.cache_check_override
		)

		if not window_result:
			sources_object._kill_progress_dialog()
			return None, None

		action, chosen_item = window_result

		# ------------------------------
		# NO ACTION / BACK
		# ------------------------------
		if not action:

			if kodi_utils.get_property(PROP_BROWSE_RETURN_SOURCES) == 'true':
				kodi_utils.clear_property(PROP_BROWSE_RETURN_SOURCES)
				sources_object._wait_active_playback_end()
				continue

			if sources_object._playback_already_active():
				sources_object._kill_progress_dialog(join_timeout=1.0)
				sources_object.resolve_dialog_made = False
				return None, None

			sources_object._kill_progress_dialog(join_timeout=3.0)
			sources_object.resolve_dialog_made = False
			return None, None

		# ------------------------------
		# PLAY (RETURN TO PLAYLIST FLOW)
		# ------------------------------
		elif action == 'play':

			kodi_utils.clear_property(PROP_RESOLVE_CANCEL)

			try:
				sources_object._close_sources_results_window()
			except:
				pass

			return chosen_item, results

		# ------------------------------
		# FULL SEARCH
		# ------------------------------
		elif sources_object.prescrape and action == 'perform_full_search':

			sources_object._kill_progress_dialog(join_timeout=1.0)

			if not sources_object.progress_dialog and not sources_object.background:
				sources_object._make_progress_dialog()

			sources_object.prescrape = False
			sources_object.autoscrape = True
			sources_object.clear_properties = True
			sources_object.filters_ignored = sources_object.ignore_scrape_filters

			sources_object.prescrape_sources = []
			sources_object.prescrape_ran_scrapers = set()

			sources_object.orig_results = []
			sources_object.threads, sources_object.providers = [], []
			sources_object.prescrape_scrapers, sources_object.prescrape_threads = [], []
			sources_object.uncached_results, sources_object.cloud_scraper_names = [], []
			sources_object.active_folders, sources_object.folder_info = False, []
			sources_object.internal_scraper_names, sources_object.resolve_dialog_made = [], False

			sources_object.remove_scrapers = ['external']
			sources_object.cloud_prescrape_autoplay = False

			if not sources_object.ignore_scrape_filters:
				kodi_utils.clear_property('fs_filterless_search')
			sources_object.orig_results = results[:]
			sources_object._prepare_external_only_followup()

			new_results = sources_object.get_sources()

			if not new_results or not isinstance(new_results, list):
				#return None, None
				continue

			existing_ids = set(i.get('id') for i in results)
			merged = results[:]

			for item in new_results:
				item_id = item.get('id')
				if not item_id or item_id not in existing_ids:
					merged.append(item)

			results = merged
			continue

		# ------------------------------
		# CACHE RESCRAPE
		# ------------------------------
		elif action == 'cache_change_rescrape':

			sources_object.cache_check_override = chosen_item == 'true'
			sources_object._reset_scrape_state(keep_disabled_ext_ignored=True)

			new_results = sources_object.get_sources()

			if not new_results or not isinstance(new_results, list):
				return None, None

			results = new_results
			continue

def safe_resolve(sources_obj, item, timeout=15):
	result = {"url": None}

	def worker():
		try:
			result["url"] = sources_obj._resolve_sources_wait(item)
		except:
			result["url"] = None

	t = Thread(target=worker)
	t.start()
	t.join(timeout)

	if t.is_alive():
		xbmc.log("RESOLVE TIMEOUT - skipping source", xbmc.LOGERROR)
		return None

	return result["url"]


def is_valid_playable_url(url, item=None):
	if not url or not isinstance(url, str):
		return None

	u = url.lower()

	# --- must be http(s) ---
	if not (u.startswith('http://') or u.startswith('https://')):
		return None

	# --- obvious bad resolver output ---
	bad_tokens = (
		'error',
		'invalid',
		'unsupported',
		'not available','infringing_file','{files} is missing','too_many_requests','unknown_resource',
		'videostream'
	)
	if any(token in u for token in bad_tokens):
		return None

	"""
	# --- determine path (strip headers, query) ---
	name = ''
	try:
		if item:
			name = item.get('name', '') or item.get('display_name', '')
	except:
		pass

	path = (url or '').split('|')[0].split('?')[0]
	path_lower = (name or path).lower()
	path_lower2 = (path).lower()
	path_lower3 = str(url.split('.')[-1]).lower()
	"""
	# --- valid video extensions (proxy for MIME correctness) ---
	valid_exts = (
		'.m2ts',
		'.mts',
		'.ts',
		'.mkv',
		'.mp4',
		'.avi',
		'.mov',
		'.webm',
	)

	if "." + url.split(".")[-1] not in valid_exts:
		return None
	return url
 


def decode_sorttitle(player_obj, st):
	"""
	Safely decodes base64 sorttitle. Supports BOTH legacy underscore format 
	(tmdb_id_season_episode) and new full parameter JSON dictionary format.
	"""
	if not st:
		return None, None
	try:
		# Fix base64 padding issues if strings get stripped by database
		padded_st = st + '=' * (-len(st) % 4)
		decoded = base64.b64decode(padded_st).decode('utf-8', errors='ignore')

		# ✅ Path A: Check if it's the new JSON format
		if decoded.startswith('{') and decoded.endswith('}'):
			data = json.loads(decoded)
			
			# Automatically assign these back to player_obj so your player has the attributes!
			#player_obj.params = data
			player_obj.params = data.get('params', data)
			
			# Return the integers expected by get_current_episode_from_player()
			season = int(data.get('season')) if data.get('season') else None
			episode = int(data.get('episode')) if data.get('episode') else None
			return season, episode

		# ✅ Path B: Legacy fallback to prevent breaking your old code
		parts = decoded.split('_')
		if len(parts) == 3:
			_, season, episode = parts
			return int(season), int(episode)
			
		# Legacy movie fallback case
		elif len(parts) == 2 and parts[1] == 'movie':
			return None, None
		
	except Exception as e:
		xbmc.log(f"[decode_sorttitle] Failed parsing structure: {e}", xbmc.LOGDEBUG)
	
	return None, None

def get_current_sorttitle(player_obj, playerid=1):
	"""
	Retrieves the current item's sorttitle using a dynamic, retry-backed lookup
	to eliminate timing race conditions when new files initialize.
	"""
	def rpc(method, params=None):
		payload = {"jsonrpc": "2.0", "method": method, "params": params or {}, "id": 1}
		response = xbmc.executeJSONRPC(json.dumps(payload))
		return json.loads(response)

	# Try up to 10 times (1 second total) for Kodi's internal state machine to sync
	for _ in range(10):
		try:
			# ✅ Step 1: Resolve dynamic Player ID if hardcoded value is stale/unmapped
			active_players = rpc("Player.GetActivePlayers").get("result", [])
			if active_players:
				playerid = next((p["playerid"] for p in active_players if p["type"] == "video"), playerid)

			# ✅ Step 2: Extract current active file info directly (Most reliable target)
			item = rpc("Player.GetItem", {"playerid": playerid, "properties": ["sorttitle"]})
			sorttitle = item.get("result", {}).get("item", {}).get("sorttitle")
			if sorttitle:
				return sorttitle

			# ✅ Step 3: Playlist position lookup fallback if direct item lookup is slow
			res = rpc("Player.GetProperties", {"playerid": playerid, "properties": ["position", "playlistid"]})
			result = res.get("result", {})
			position = result.get("position", -1)
			playlistid = result.get("playlistid", 1)  # Default video playlist is 1

			if position >= 0:
				pl = rpc("Playlist.GetItems", {"playlistid": playlistid, "properties": ["sorttitle"]})
				items = pl.get("result", {}).get("items", [])
				if 0 <= position < len(items):
					sorttitle = items[position].get("sorttitle")
					if sorttitle:
						return sorttitle
						
		except Exception as e:
			xbmc.log(f"[get_current_sorttitle] Internal iteration exception: {e}", xbmc.LOGDEBUG)

		xbmc.sleep(100)  # Pause briefly between attempts to let Kodi populate data structures

	xbmc.log("[get_current_sorttitle] Warning: Exited retry engine without capturing metadata", xbmc.LOGWARN)
	return None


def get_current_episode_from_player(player_obj):
	try:
		st = get_current_sorttitle(player_obj)
		if not st:
			return None

		season, episode = decode_sorttitle(player_obj, st)
		if season is None or episode is None:
			return None

		return season, episode

	except Exception as e:
		xbmc.log(f"get_current_episode_from_player error: {str(e)}", xbmc.LOGDEBUG)
		return None


def get_playlist_sorttitles(player_obj):
	"""
	Gathers all available sorttitle tags from the active video queue safely.
	Uses an explicit property fallback if the video tag container lags.
	"""
	sorttitles = []
	try:
		playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		for i in range(playlist.size()):
			try:
				item = playlist[i]
				# Primary: Fetch native tag metadata structure
				st = item.getVideoInfoTag().getSortTitle()
				
				# Secondary Fallback: Fetch direct layout list property
				if not st:
					st = item.getProperty("sorttitle")
					
				if st:
					sorttitles.append(st)
			except:
				continue
	except Exception as e:
		xbmc.log(f"[get_playlist_sorttitles] Critical failure: {e}", xbmc.LOGDEBUG)

	return sorttitles


def make_sorttitle(meta, params=None):
	"""
	Encodes metadata context combined with custom execution parameters 
	straight into a serialized base64 sorttitle string profile.
	"""
	try:
		# 💡 Step 1: Initialize the core metadata layout dictionary
		payload = {'tmdb_id': str(meta.get('tmdb_id', '')),'media_type': str(meta.get('mediatype', 'episode')),'season': str(meta.get('season', '')),'episode': str(meta.get('episode', ''))}
		
		# 💡 Step 2: If a custom params dictionary was provided, merge it directly into the payload
		if isinstance(params, dict):
			#payload.update(params)
			payload['params'] = params
			payload['params']['REDLIGHT'] = 'REDLIGHT'
			
		# 💡 Step 3: Serialize to a uniform JSON string configuration payload and cast to base64
		serialized_json = json.dumps(payload)
		return base64.b64encode(serialized_json.encode('utf-8')).decode('utf-8')
		
	except Exception as e:
		# Safe fallback trace container boundary
		import xbmc
		xbmc.log(f"[make_sorttitle] Encoding execution failed: {e}", xbmc.LOGDEBUG)
		return ''



def get_params_from_sorttitle(player_obj):
	st = get_current_sorttitle(player_obj)
	if not st:
		xbmc.log("[get_params_from_sorttitle] Error: Sorttitle is empty or missing.", xbmc.LOGWARN)
		return {}

	# Step 2: Fix any potential base64 padding issues automatically
	padded_st = st + '=' * (-len(st) % 4)
	
	# Step 3: Decode from base64 string back into raw utf-8 string
	decoded_string = base64.b64decode(padded_st).decode('utf-8', errors='ignore')
	
	# Step 4: Verify it is a valid JSON payload string and load it back to a dictionary
	if decoded_string.startswith('{') and decoded_string.endswith('}'):
		params_dict = json.loads(decoded_string)
		return params_dict




#	def play_file(self, results, source={}):
#		import modules.playlist as playlist_module
#		return playlist_module.playlist_play_file(self, results, source)

def playlist_play_file(sources_obj, results, source=None):

	playable_results = [i for i in results if 'Uncached' not in i.get('cache_provider', '')]

	if not playable_results and not source:
		return sources_obj._no_results()

	sources_obj._playback_failed_notified = False
	kodi_utils.clear_property(PROP_RESOLVE_CANCEL)
	sources_obj._claim_resolve_busy()

	url = None
	monitor = None

	if 1 == 1:

		sources_obj.playback_successful, sources_obj.cancel_all_playback = None, False
		sources_obj._resolve_user_cancelled = False

		sources_obj._prepare_resolve_ui()

		defer_stop_for_nextep = sources_obj.background and (
			sources_obj.autoplay_nextep
			or sources_obj.autoscrape_nextep
			or sources_obj.play_type == 'random_continual'
			or sources_obj.random_continual
		)

		# Removed intentionally
		# if not defer_stop_for_nextep:
		#     sources_obj._stop_active_playback()

		retry_easynews = settings.easynews_playback_method('retry')
		retry_easynews_limit = settings.easynews_playback_method_retries()

		kodi_utils.hide_busy_dialog()

		# ---------------------------------------------------------
		# SOURCE SELECT CONTROL (CORRECT)
		# ---------------------------------------------------------

		if not source:

			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

			if sources_obj.params.get('autoplay', '') == 'false':
				sources_obj.autoplay = False

			should_show_select = (
				not sources_obj.autoplay and
				not sources_obj.background and
				playlist.size() == 0
			)

			if should_show_select:
				source, results = run_source_select_flow(sources_obj, results)

				if not source:
					xbmc.log("PLAY_FILE: user cancelled selection", xbmc.LOGINFO)
					return

		playable_results = results

		# ---------------------------------------------------------
		# BUILD ORDER
		# ---------------------------------------------------------

		if not source:
			source = results[0]

		items = [source]

		if not sources_obj.limit_resolve:
			source_index = results.index(source)
			results.remove(source)

			items_prev = results[:source_index]
			items_prev.reverse()

			items_next = results[source_index:]

			items = items + items_next + items_prev
		else:
			results.remove(source)

		processed_items = []
		processed_items_append = processed_items.append

		for count, item in enumerate(items, 1):

			resolve_item = dict(item)

			provider = item['scrape_provider']
			if provider == 'external':
				provider = item['debrid'].replace('.me', '')
			elif provider == 'folders':
				provider = item['source']

			provider_text = provider.upper()

			extra_info = '[B]%s[/B] | [B]%s[/B] | %s' % (
				item['quality'],
				item['size_label'],
				item['extraInfo']
			)

			display_name = item['display_name'].upper()

			resolve_item['resolve_display'] = '%02d. [B]%s[/B][CR]%s[CR]%s' % (
				count, provider_text, extra_info, display_name
			)

			processed_items_append(resolve_item)

			if provider == 'easynews' and retry_easynews:
				for retry in range(1, retry_easynews_limit):
					retry_item = dict(item)
					retry_item['resolve_display'] = '%02d. [B]%s (RETRYx%s)[/B][CR]%s[CR]%s' % (
						count, provider_text, retry, extra_info, display_name
					)
					processed_items_append(retry_item)

		items = list(processed_items)

		if not sources_obj.continue_resolve_check():
			sources_obj._kill_progress_dialog()
			return

		if defer_stop_for_nextep:
			sources_obj._stop_active_playback()

		kodi_utils.hide_busy_dialog()

		if not sources_obj.progress_dialog and not sources_obj.background:
			sources_obj._make_progress_dialog()

		#sources_obj.cloud_prescrape_autoplay = False
		sources_obj.playback_percent = sources_obj.get_playback_percent()

		if sources_obj.playback_percent is None:
			sources_obj._finish_resolve_cancel()
			return

		if not sources_obj.resolve_dialog_made:
			sources_obj._make_resolve_dialog()

		if sources_obj.background:
			kodi_utils.sleep(1000)

		monitor = kodi_utils.kodi_monitor()
		player = RedLightPlayer()

		# ---------------------------------------------------------
		# RESOLVE LOOP
		# ---------------------------------------------------------

		for count, item in enumerate(items, 1):

			kodi_utils.hide_busy_dialog()

			if not sources_obj.progress_dialog:
				break

			sources_obj.progress_dialog.reset_is_cancelled()
			sources_obj.progress_dialog.update_resolver(text=item['resolve_display'])
			sources_obj.progress_dialog.busy_spinner()

			url, sources_obj.playback_successful, sources_obj.cancel_all_playback = None, None, False

			sources_obj.playing_filename = item['name']
			sources_obj.playing_item = item

			url = sources_obj._resolve_sources_wait(item)
			#url = safe_resolve(sources_obj, item)
			#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
			#xbmc.log(str(item), level=xbmc.LOGINFO)

			if url:
				#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
				#xbmc.log(str(url), level=xbmc.LOGINFO)
				url = sources_obj._ensure_play_headers(url, item)
				#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
				#xbmc.log(str(url), level=xbmc.LOGINFO)
			else:
				xbmc.log(str('SLEEP'), level=xbmc.LOGINFO)
				xbmc.sleep(3000)

			url = is_valid_playable_url(url, item)
			if not url:
				xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
				xbmc.log(f"INVALID URL - skipping: {str(url)}", xbmc.LOGINFO)
				continue

			player.set_constants(url, sources_obj)
			listitem = player.make_listing()

			listitem.setProperty('IsPlayable', 'true')
			listitem.setPath(url)

			sorttitle_b64 = make_sorttitle(sources_obj.meta, sources_obj.params)
			

			info_tag = listitem.getVideoInfoTag()
			info_tag.setSortTitle(sorttitle_b64)
			listitem.getVideoInfoTag().setSortTitle(sorttitle_b64)

			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

			for i in range(playlist.size()):
				try:
					existing = playlist[i].getVideoInfoTag().getSortTitle()
					if existing == sorttitle_b64:
						return
				except:
					continue

			xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
			xbmc.log(str(url), xbmc.LOGINFO)
			if xbmc.Player().isPlaying() == False and playlist.size() >= 1:
					playlist.clear()
			playlist.add(url, listitem)

			if xbmc.Player().isPlaying() == False:

				sources_obj.progress_dialog.busy_spinner('false')
				kodi_utils.sleep(200)

				#player.play(playlist, listitem)
				sources_obj._kill_progress_dialog()
				sources_obj.playback_successful = True
				return player.play(playlist)

			sources_obj._kill_progress_dialog()
			sources_obj.playback_successful = True
			return
	# ---------------------------------------------------------
	# NO VALID STREAM FOUND → CLEAN EXIT
	# ---------------------------------------------------------
	sources_obj._kill_progress_dialog()
	xbmc.log("RESOLVE: No valid URLs found - exiting cleanly", xbmc.LOGERROR)
	# ✅ important: notify failure properly
	sources_obj._finish_resolve_cancel()
	return



def autoscrape_nextep_helper(sources_obj, results):
	from modules.player import RedLightPlayer
	player = RedLightPlayer()

	next_url = None
	for item in results:
		#next_url = sources_obj._resolve_sources_wait(item)
		next_url = safe_resolve(sources_obj, item)

		if next_url:
			next_url = sources_obj._ensure_play_headers(next_url, item)
		next_url = is_valid_playable_url(next_url, item)
		if not next_url:
			xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
			xbmc.log(f"INVALID URL - skipping: {str(next_url)}", xbmc.LOGINFO)
			continue
		else:
			break

	if not next_url:
		return

	listitem = player.make_listing()

	try:
		sorttitle_b64 = make_sorttitle(sources_obj.meta, sources_obj.params)
		listitem.getVideoInfoTag().setSortTitle(sorttitle_b64)
	except:
		pass

	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

	# prevent duplicates
	for i in range(playlist.size()):
		try:
			try:
				existing = playlist[i].getVideoInfoTag().getSortTitle()
			except:
				existing = None

			if existing == sorttitle_b64:
				return
		except:
			continue

	xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
	xbmc.log(str(next_url), xbmc.LOGINFO)
	return playlist.add(next_url, listitem)



def is_next_in_playlist(player_obj):
	"""
	Checks if the next physical item in the playlist matches our expected up-next tag.
	"""
	try:
		playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		current_pos = playlist.getposition()

		if current_pos < playlist.size() - 1:
			next_item = playlist[current_pos + 1]
			# Check native tag first
			st = next_item.getVideoInfoTag().getSortTitle()
			# Fallback to general listing item properties
			if not st:
				st = next_item.getProperty("sorttitle")

			if st:
				ns, ne = decode_sorttitle(player_obj, st)
				expected = player_obj.get_expected_next_episode()
				if expected == (ns, ne):
					return True
	except Exception as e:
		xbmc.log(f"is_next_in_playlist error: {str(e)}", xbmc.LOGDEBUG)

	return False

def get_expected_next_episode(player_obj):
	"""
	Resolves season and episode markers for the upcoming chronological episode.
	"""
	try:
		base_meta = dict(player_obj.meta)
		current_ep = get_current_episode_from_player(player_obj)
		if not current_ep:
			xbmc.log("NEXT_EP: Unable to resolve current episode from player", xbmc.LOGINFO)
			xbmcgui.Window(10000).clearProperty('fenlight.monitor_id')
			return
		cur_season, cur_episode = current_ep
		# ✅ Inject correct episode into meta
		base_meta.update({
			'season': cur_season,
			'episode': cur_episode
		})
		ep_tools = EpisodeTools(base_meta, player_obj.nextep_settings)

		all_eps = all_episodes_meta(player_obj.meta)
		# build correct structure
		season_map = {}
		for ep in all_eps:
			s = ep['season']
			season_map.setdefault(s, 0)
			season_map[s] = max(season_map[s], ep['episode'])
		season_data = [{'season_number': s, 'episode_count': count} for s, count in season_map.items()]
		player_obj.meta['season_data'] = season_data
		info = ep_tools.next_episode_info()

		#ep_tools = EpisodeTools(player_obj.meta, player_obj.nextep_settings)
		#info = ep_tools.next_episode_info()

		if not info:
			return None

		return int(info.get('season')), int(info.get('episode'))
	except:
		return None

def _reset_state(player_obj):
	"""
	Wipes local state logic parameters cleanly during track transition boundaries.
	"""
	player_obj._next_added = False
	#player_obj._nextep_dialog_shown = False
	player_obj.nextep_info_gathered = False
	player_obj.media_marked = False
	player_obj.start_prep = None
	player_obj.maybe_refresh_nextep = False
	try:
		player_obj.info_next_ep()
	except:
		pass

#	def set_playback_properties(self):
###
#		import modules.playlist as playlist_module
#		return playlist_module.set_playback_properties_additional(self, trakt_ids)

def set_playback_properties_additional(player_obj, trakt_ids):
	if xbmc.Player().isPlaying() == False:
		xbmcgui.Window(10000).clearProperty('fenlight.monitor_id')
	if player_obj.media_type == 'episode': 
		TMDbHelper_NEW_PlayerInfoString = {'tmdb_type': player_obj.media_type, 'tmdb_id': str(player_obj.tmdb_id), 'imdb_id': str(player_obj.imdb_id), 'tvdb_id': str(trakt_ids['tvdb']), 'season': player_obj.meta['season'], 'episode': player_obj.meta['episode']}
		xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))
	elif player_obj.media_type == 'movie':
		TMDbHelper_NEW_PlayerInfoString = {'tmdb_type': player_obj.media_type, 'tmdb_id': str(player_obj.tmdb_id), 'imdb_id': str(player_obj.imdb_id), 'year': str(player_obj.year)}
		xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))


def check_playlist(b64_encode_dict, playlistid=1):
	def _json_rpc(method, params=None):
		if params is None:
			params = {}
		payload = {"jsonrpc": "2.0","method": method,"params": params,"id": 1}
		response = xbmc.executeJSONRPC(json.dumps(payload))
		return json.loads(response)

	try:
		# Get playlist items with sorttitle
		res = _json_rpc("Playlist.GetItems", {"playlistid": playlistid,"properties": ["sorttitle"]})
		items = res.get("result", {}).get("items", [])
		for item in items:
			existing = item.get("sorttitle")
			if not existing:
				continue
			# Fast path: direct string compare
			if existing == b64_encode_dict:
				return True
			# Optional fallback: decoded compare (future-proof)
			try:
				decoded_existing = json.loads(base64.b64decode(existing).decode('utf-8'))
				decoded_target = json.loads(base64.b64decode(b64_encode_dict).decode('utf-8'))
				if decoded_existing == decoded_target:
					return True
			except Exception:
				continue
		return False
	except Exception as e:
		xbmc.log(f" playlist_contains_b64 error: {e}", xbmc.LOGERROR)
		return False

def run_next_ep_playlist(player_obj):
	#try:
	orig_player_obj = player_obj
	if 1==1:

		#nextep_settings = getattr(player_obj, "nextep_settings", None) or getattr(player_obj.sources_object, "nextep_settings", None)
		# ✅ HARD GUARANTEE nextep_settings is valid
		if not getattr(player_obj, "nextep_settings", None):
			try:
				# rebuild using same logic as info_next_ep
				play_type = 'autoplay_nextep' if getattr(player_obj, "autoplay_nextep", False) else 'autoscrape_nextep'
				nextep_settings = st.auto_nextep_settings(play_type)

				player_obj.nextep_settings = {
					'use_window': nextep_settings.get('alert_method', 0) == 0,
					'window_time': int((nextep_settings.get('window_percentage', 20) / 100) * (player_obj.getTotalTime() or 1800)),
					'default_action': nextep_settings.get('default_action', 'play'),
					'play_type': play_type
				}
			except:
				player_obj.nextep_settings = {
					'use_window': False,
					'window_time': 300,
					'default_action': 'play',
					'play_type': 'autoscrape_nextep'
				}


		nextep_settings = player_obj.nextep_settings
		# ✅ Get next episode
		#ep_tools = EpisodeTools(player_obj.meta, nextep_settings)

		# ✅ rebuild full meta (CRITICAL FIX)
		try:
			if player_obj.meta.get('media_type') == 'episode':
				base_meta = metadata.tvshow_meta(
					'tmdb_id',
					player_obj.meta.get('tmdb_id'),
					st.tmdb_api_key(),
					st.mpaa_region(),
					ku.get_datetime()
				)

				# ✅ merge current episode context back in
				base_meta.update({
					'season': player_obj.meta.get('season'),
					'episode': player_obj.meta.get('episode')
				})
			else:
				base_meta = player_obj.meta
		except:
			base_meta = player_obj.meta

		current_ep = get_current_episode_from_player(player_obj)
		if not current_ep:
			xbmc.log("NEXT_EP: Unable to resolve current episode from player", xbmc.LOGINFO)
			return orig_player_obj
		cur_season, cur_episode = current_ep
		# ✅ Inject correct episode into meta
		base_meta.update({
			'season': cur_season,
			'episode': cur_episode
		})
		ep_tools = EpisodeTools(base_meta, nextep_settings)
		url_params = ep_tools.next_episode_info()


		if not url_params or url_params in ('error', 'no_next_episode'):
			player_obj._next_added = False
			orig_player_obj._next_added = False
			xbmc.log('NEXT_EP: No valid next episode info', xbmc.LOGINFO)
			return orig_player_obj
		next_season = int(url_params.get('season', 0))
		next_episode_num = int(url_params.get('episode', 0))
		if not next_season or not next_episode_num:
			xbmc.log('NEXT_EP: Invalid episode numbers', xbmc.LOGINFO)
			return orig_player_obj

		params = url_params
		params.pop('nextep_settings', None)
		params.pop('play_type', None)

		params.update({
			'background': 'true',   # ✅ run in background
			'autoplay': 'false',    # ✅ DO NOT trigger play_file
		})
		sources = Sources()

		# ✅ Inject missing playback context (CRITICAL)
		if not hasattr(sources, 'playback_percent'):
			sources.playback_percent = 0.0

		if not hasattr(sources, 'playing_filename'):
			sources.playing_filename = ''

		if not hasattr(sources, 'playing_item'):
			sources.playing_item = {}

		# ✅ retry scrape (good)
		results = None
		params['prescrape'] = 'true'
		params['play_type'] = 'autoscrape_nextep'
		params['background'] = 'true'
		sources.autoscrape = True
		results = sources.playback_prep(params)
		#for _ in range(2):
		#	results = sources.playback_prep(params)
		#	
		#	if results:
		#		break

		if not results:
			xbmc.log('NEXT_EP: No results after retry', xbmc.LOGINFO)
			return orig_player_obj

		if isinstance(results, str):
			url = results

		elif isinstance(results, list):
			url = None
			for item in results:
				#url = sources._resolve_sources_wait(item)
				url = safe_resolve(sources, item)
				if url:
					url = sources._ensure_play_headers(url, item)
				url = is_valid_playable_url(url, item)
				if not url:
					xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
					xbmc.log(f"INVALID URL - skipping: {str(url)}", xbmc.LOGINFO)
					continue
				else:
					break

			
		elif isinstance(results, dict):
			url = None
			for item in results:
				#url = sources._resolve_sources_wait(item)
				url = safe_resolve(sources, item)
				if url:
					url = sources._ensure_play_headers(url, item)
				url = is_valid_playable_url(url, item)
				if not url:
					xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
					xbmc.log(f"INVALID URL - skipping: {str(url)}", xbmc.LOGINFO)
					continue
				else:
					break
		else:
			xbmc.log('NEXT_EP: unexpected result type', xbmc.LOGINFO)
			return orig_player_obj


		if not url:
			xbmc.log('NEXT_EP: resolve_url failed', xbmc.LOGINFO)
			return orig_player_obj

		# ✅ preserve current playback state
		saved_meta = player_obj.meta
		saved_sources = player_obj.sources_object

		# ✅ reuse CURRENT player instance (CRITICAL FIX)
		player_obj.set_constants(url, sources)
		listitem = player_obj.make_listing()

		# ✅ restore playback state
		player_obj.meta = saved_meta
		player_obj.sources_object = saved_sources

		try:
			sources.params = player_obj.params
			sources.params['episode'], sources.params['season'] = sources.meta['episode'], sources.meta['season']
			sorttitle_b64 = make_sorttitle(sources.meta, sources.params)
			listitem.getVideoInfoTag().setSortTitle(sorttitle_b64)
		except:
			sorttitle_b64 = None

		playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

		check_playlist_flag = check_playlist(b64_encode_dict=sorttitle_b64, playlistid=1)

		if check_playlist_flag == False:
			xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
			xbmc.log(str(url), xbmc.LOGINFO)
			playlist.add(url, listitem)
			xbmc.log('NEXT_EP: added to playlist', xbmc.LOGINFO)
		else:
			xbmc.log('NEXT_EP: ALREADY_IN_PLAYLIST', xbmc.LOGINFO)
		return orig_player_obj

	#except Exception as e:
	#	xbmc.log(f'NEXT_EP ERROR: {str(e)}', xbmc.LOGINFO)


def player_state_io(player_obj, data=None, mode='store'):
	"""
	mode='store'   → returns dict snapshot
	mode='restore' → restores values from dict back to player_obj
	"""

	# ✅ STORE
	if mode == 'store':
		out = {}
		for k, v in player_obj.__dict__.items():
			try:
				# only keep simple values
				if isinstance(v, (str, int, float, bool, type(None), dict, list)):
					out[k] = v
			except:
				continue
		return out

	# ✅ RESTORE
	elif mode == 'restore' and isinstance(data, dict):
		for k, v in data.items():
			try:
				setattr(player_obj, k, v)
			except:
				continue


def monitor_playlist(player_obj, monitor_id=None):
	"""
	ROBUST PLAYLIST MONITOR (PRODUCTION READY)
	"""
	from modules import kodi_utils as ku, settings as st, watched_status as ws
	xbmc.log("PLAYLIST MONITOR STARTED " + str(monitor_id), xbmc.LOGINFO)
	check_ep_flag = False
	try:
		# Short baseline buffer for incoming playback allocations
		xbmc.sleep(1000)
		if player_obj.isPlaying():
			player_obj.stop_file = False

		not_playing_since = None
		was_playing = False
		seconds_stopped = 0.0
		last_loop_time = time.time() 

		player_obj._simkl_scrobble_start()
		if st.auto_enable_subs() and not st.submaker_enabled(): player_obj.showSubtitles(False)
		player_obj.showSubtitles(False)

		player_obj._max_progress = 0.0
		player_obj.maybe_refresh_nextep = False
		player_obj._intro_skip_fetch_started = False
		player_obj.subs_searched = False
		while not player_obj.stop_file:
			xbmc.sleep(100)

			current_id = xbmcgui.Window(10000).getProperty('fenlight.monitor_id')
			if current_id == None or current_id == '':
				current_id = str(0)
			if monitor_id != None:
				if monitor_id != current_id:
					xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
					xbmc.log("PLAYLIST MONITOR ENDED " + str(monitor_id), xbmc.LOGINFO)
					#xbmcgui.Window(10000).clearProperty('fenlight.monitor_id')
					#player_obj.stop_file = True
					player_obj.stop_file = True
			if player_obj.stop_file:
				xbmc.log(f"PLAYLIST: Final progress = {player_obj._max_progress:.2f}", xbmc.LOGINFO)

				if player_obj._max_progress >= 97 and player_obj.media_marked != True:
					if player_obj._max_progress > 100:
						player_obj._max_progress = 99
						player_obj.current_point = player_obj._max_progress
					player_obj.media_watched_marker()
					player_obj.media_marked = True
					player_obj._simkl_scrobble_stop(100)
					xbmc.log(f"NEXTEP: media_watched_marker", xbmc.LOGERROR)

				elif player_obj._max_progress >= 5:
					player_obj.current_point = player_obj._max_progress
					player_obj.media_watched_marker()
					player_obj.media_marked = False
				xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
				xbmc.log("PLAYLIST MONITOR ENDED " + str(monitor_id), xbmc.LOGINFO)
				return

			current_loop_time = time.time()
			loop_duration = current_loop_time - last_loop_time
			last_loop_time = current_loop_time
			# ✅ PLAYBACK STATE ACCUMULATION WATCHDOG
			#if not player_obj.isPlayingVideo():
			#	seconds_stopped += loop_duration
			#	if seconds_stopped >= 10.0:
			#		xbmc.log(f"PLAYLIST MONITOR: Continuous stoppage reached {seconds_stopped:.2f}s. Terminating.", xbmc.LOGINFO)
			#		player_obj.stop_file = True
			#		break
			#	xbmc.sleep(250)
			#	# Removed 'continue' so the loop progresses normally and hits the main throttle below
			#else:
			#	seconds_stopped = 0.0
			#	progress_params_flag = 0
			#if not player_obj.isPlayingVideo():
			#	if progress_params_flag < progress:
			#		progress_params_flag = progress
			#		if progress >= 5:
			#			progress_params = {'media_type': player_obj.media_type, 'tmdb_id': player_obj.tmdb_id, 'curr_time': player_obj.curr_time, 'total_time': player_obj.total_time,
			#							'title': player_obj.title, 'season': player_obj.season, 'episode': player_obj.episode, 'from_playback': 'true'}
			#			Thread(target=player_obj.run_media_progress, args=(ws.set_bookmark, progress_params)).start()


			if not player_obj.isPlayingVideo():
				seconds_stopped += loop_duration

				if seconds_stopped >= 5.0:   # shorter, responsive
					xbmc.log(f"PLAYLIST: Final progress = {player_obj._max_progress:.2f}", xbmc.LOGINFO)

					if player_obj._max_progress >= 90 and player_obj.media_marked != True:
						player_obj.media_watched_marker()
						player_obj.media_marked = True
						player_obj._simkl_scrobble_stop(100)
						xbmc.log(f"NEXTEP: media_watched_marker", xbmc.LOGERROR)

					elif player_obj._max_progress >= 5:
						player_obj.current_point = player_obj._max_progress
						player_obj.media_watched_marker()
						player_obj.media_marked = False

					player_obj.stop_file = True
					break
			elif player_obj.isPlayingVideo() and seconds_stopped >=1:
				seconds_stopped = 0


			if player_obj.isPlaying() and check_ep_flag == False:
				if player_obj.media_type == 'movie':
					check_ep_flag = True
					player_obj._dialog_locked = True
					player_obj._next_added = True
				else:
					current_ep = get_current_episode_from_player(player_obj)
					if not current_ep:
						#xbmcgui.Window(10000).clearProperty('fenlight.monitor_id')
						xbmc.log("NEXT_EP: Unable to resolve current episode from player", xbmc.LOGINFO)
						player_obj.stop_file = True
						xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
						xbmc.log("PLAYLIST MONITOR ENDED " + str(monitor_id), xbmc.LOGINFO)
						#xbmcgui.Window(10000).clearProperty('fenlight.monitor_id')
						return
					check_ep_flag = True

				player_obj._simkl_scrobble_start()#
				player_obj._maybe_start_subtitle_alert_fetch()#
				player_obj._maybe_start_introdb_alert_fetch()#
				if st.auto_enable_subs() and st.subtitles_source() == '0':#
					try:#
						from indexers.subtitles import enable_local_subtitles#
						poster = player_obj.meta.get('poster') if getattr(player_obj, 'meta', None) else None#
						enable_local_subtitles(player_obj, poster=poster or ku.get_icon('box_office'), notify=False)#
					except:#
						player_obj.showSubtitles(False)#
				player_obj.showSubtitles(False)#


			# ✅ 2. PLAYBACK TIMING ENGINE
			try:
				total = player_obj.getTotalTime()
				current = player_obj.getTime()
				if not total or total <= 0:
					xbmc.sleep(200)
					continue
				
				progress = (current / total) * 100

				# ✅ sync legacy fields
				player_obj.curr_time = current
				player_obj.total_time = total
				player_obj.current_point = progress

				# ✅ track max progress seen
				if progress > player_obj._max_progress:
					player_obj._max_progress = progress

				remaining = total - current
			except Exception as e:
				xbmc.log(f"PLAYLIST TIME ACCUMULATION ERROR: {str(e)}", xbmc.LOGDEBUG)
				xbmc.sleep(500)
				continue

			if not getattr(player_obj, '_intro_skip_fetch_started', False):#
				player_obj._intro_skip_fetch_started = True#
				player_obj._start_intro_skip_fetch()#
			player_obj._maybe_apply_intro_skip()

			if player_obj.subs_searched == False: 
				player_obj.subs_searched = True
				player_obj.run_subtitles()
				xbmc.sleep(2000)
				player_obj.showSubtitles(False)
				player_obj.showSubtitles(False)

			# ✅ 3. DETECT TRACK CHANGE VIA PLAYLIST INDICES (FAST & NON-BLOCKING)
			try:
				playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
				pos = playlist.getposition()
			except:
				pos = -1

			if pos != getattr(player_obj, "_last_pos", None) and pos >= 0:
				xbmc.log(f"PLAYLIST: Track index changed → {pos}", xbmc.LOGINFO)
				xbmc.sleep(2500)
				player_obj._last_pos = pos
				player_obj._current_sort = None  # Force sorttitle recalculation flag
				player_obj._nextep_dialog_shown = False
				player_obj._dialog_locked = False
				check_ep_flag = False
				#_reset_state(player_obj)
				if not player_obj.media_type == 'movie':
					current_ep = get_current_episode_from_player(player_obj)
					cur_season, cur_episode = current_ep
					TMDbHelper_NEW_PlayerInfoString = {'tmdb_type': player_obj.media_type, 'tmdb_id': str(player_obj.tmdb_id), 'imdb_id': str(player_obj.imdb_id), 'tvdb_id': str(player_obj.tvdb_id), 'season': cur_season, 'episode': cur_episode}
					xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))
					PlayerInfoString = xbmcgui.Window(10000).getProperty('TMDbHelper.PlayerInfoString')

			# ✅ 4. VALIDATE META DATA SIGNATURES (NON-BLOCKING LOOKUP WITH TIMEOUT OMITTED IN LOOP)
			# Passing a custom dynamic flag or setting playerid parameters prevents loop stalls
			if not player_obj._dialog_locked:
				current_sort = get_current_sorttitle(player_obj)
				if current_sort and current_sort != getattr(player_obj, "_current_sort", None):
					prev_sort = getattr(player_obj, "_current_sort", None)
					player_obj._current_sort = current_sort
					#xbmc.log(f"PLAYLIST: Item changed metadata signature {prev_sort} → {current_sort}", xbmc.LOGINFO)
					xbmc.log(f"PLAYLIST: Item changed metadata signature", xbmc.LOGINFO)
					_reset_state(player_obj)
					if not player_obj.media_type == 'movie':
						current_ep = get_current_episode_from_player(player_obj)
						cur_season, cur_episode = current_ep
						TMDbHelper_NEW_PlayerInfoString = {'tmdb_type': player_obj.media_type, 'tmdb_id': str(player_obj.tmdb_id), 'imdb_id': str(player_obj.imdb_id), 'tvdb_id': str(player_obj.tvdb_id), 'season': cur_season, 'episode': cur_episode}
						xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))
						PlayerInfoString = xbmcgui.Window(10000).getProperty('TMDbHelper.PlayerInfoString')


			# ✅ 5. INITIALISE METADATA ENGINE ONCE PER EPISODE
			if not player_obj.nextep_info_gathered and not player_obj.media_type == 'movie':
				if not hasattr(player_obj, "autoplay_nextep"):
					player_obj.autoplay_nextep = False
				if not hasattr(player_obj, "autoscrape_nextep"):
					player_obj.autoscrape_nextep = True
				if not hasattr(player_obj, "nextep_settings") and player_obj.sources_object:
					player_obj.nextep_settings = getattr(player_obj.sources_object, "nextep_settings", None)
				
				try:
					player_obj.info_next_ep()
					player_obj.nextep_info_gathered = True
					xbmc.log("PLAYLIST: Successfully loaded upcoming item meta payload.", xbmc.LOGINFO)
				except Exception as e:
					xbmc.log(f"NEXTEP INFO ENGINE RECOVERY FAILURE: {str(e)}", xbmc.LOGERROR)

			# ✅ 6. WATCHED STATUS SYNC
			#if progress >= set_watched and not player_obj.media_marked:
			#	xbmc.log(f"NEXTEP: media_watched_marker", xbmc.LOGERROR)
			#	player_obj.media_watched_marker()
			#	player_obj.media_marked = True

			# ✅ 7. 35% SCRAPE COMPLETION TRIGGER
			if progress >= 35 and not player_obj._next_added:
				if player_obj.media_type == 'movie':
					player_obj._next_added = True
					continue
				# ✅ CRITICAL GUARD
				if is_next_in_playlist(player_obj):
					xbmc.log("PLAYLIST: Next already queued → skipping scrape trigger", xbmc.LOGINFO)
					player_obj._next_added = True
					continue
				player_obj._next_added = True
				xbmc.log(f"PLAYLIST: Processing scrape targets. Keys: {list(player_obj.meta.keys())}", xbmc.LOGINFO)
				try:
					if is_next_in_playlist(player_obj):
						xbmc.log("PLAYLIST: Expected target exists down-queue → skipping background engine scrape", xbmc.LOGINFO)
					else:
						xbmc.log("PLAYLIST: Querying engines for subsequent stream links...", xbmc.LOGINFO)
						current_ep = get_current_episode_from_player(player_obj)
						cur_season, cur_episode = current_ep

						new_player_obj_dict = player_state_io(player_obj, mode = 'store')
						player_obj = run_next_ep_playlist(player_obj)

						player_state_io(player_obj, data=new_player_obj_dict, mode = 'restore')

						TMDbHelper_NEW_PlayerInfoString = {'tmdb_type': player_obj.media_type, 'tmdb_id': str(player_obj.tmdb_id), 'imdb_id': str(player_obj.imdb_id), 'tvdb_id': str(player_obj.tvdb_id), 'season': cur_season, 'episode': cur_episode}
						xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))
						PlayerInfoString = xbmcgui.Window(10000).getProperty('TMDbHelper.PlayerInfoString')

						
				except Exception as e:
					xbmc.log(f"NEXT SCRAPE OPERATION EXCEPTION: {str(e)}", xbmc.LOGERROR)

			# ✅ 8. 97% NEXT EPISODE DIALOG TRIGGER
			#if (progress >= 97 or remaining <= 30) and not player_obj._nextep_dialog_shown:
			#	if player_obj.sources_object:
			#		player_obj._nextep_dialog_shown = True
			#		xbmc.log("PLAYLIST: Rendering playback transition interface overlay", xbmc.LOGINFO)
			#		player_obj.sources_object._make_nextep_dialog(default_action='play')

			"""
			self._simkl_scrobble_start()#
			self._maybe_start_subtitle_alert_fetch()#
			self._maybe_start_introdb_alert_fetch()#
			self._intro_skip_fetch_started = False#
			if st.auto_enable_subs() and st.subtitles_source() == '0':#
				try:#
					from indexers.subtitles import enable_local_subtitles#
					poster = self.meta.get('poster') if getattr(self, 'meta', None) else None#
					enable_local_subtitles(self, poster=poster or ku.get_icon('box_office'))#
				except:#
					self.showSubtitles(True)#
			while self.isPlayingVideo():

					if not getattr(self, '_intro_skip_fetch_started', False):#
						self._intro_skip_fetch_started = True#
						self._start_intro_skip_fetch()#
					self._maybe_apply_intro_skip()#
					self.current_point = round(float(self.curr_time/self.total_time * 100), 1)

					elif self.current_point >= 90:#
						if not self.media_marked: self.media_watched_marker()#
					if self.media_type == 'episode':

								self._maybe_refresh_nextep_subtitle_timing()#
								self._maybe_refresh_nextep_chapter_timing()#
								self._maybe_refresh_nextep_introdb_timing()#

					elif show_stinger and not self.movie_stingers_run: #
						final_chapter = self._stinger_trigger_point(stinger_alert_timing, stingers_percentage_fallback)#
						if self.current_point >= final_chapter: self.run_movie_stingers()#
				except: pass
				if not self.subs_searched: self.run_subtitles()#

				ku.clear_property(PROP_NEXTEP_PREP_SCHEDULED)#
			if not self.media_marked: self.media_watched_marker()#
			self.clear_playback_properties(clear_navigation=False)#
		except:#
			ku.hide_busy_dialog()#
			self.sources_object.playback_successful = False#
			self.sources_object.cancel_all_playback = True#
			return self.kill_dialog()#
			"""

			if player_obj.media_type == 'episode' and progress > 90 and player_obj._next_added == True and player_obj.maybe_refresh_nextep == False:
				player_obj._maybe_refresh_nextep_subtitle_timing()
				player_obj._maybe_refresh_nextep_chapter_timing()
				player_obj._maybe_refresh_nextep_introdb_timing()
				player_obj.maybe_refresh_nextep = True
			if ((progress >= 97 and remaining <= 60) or remaining <= 30):
				if player_obj.media_marked != True:
					player_obj._max_progress = progress
					player_obj.current_point = player_obj._max_progress
					player_obj.media_watched_marker()
					player_obj.media_marked = True
					player_obj._simkl_scrobble_stop(100)
					xbmc.log(f"NEXTEP: media_watched_marker", xbmc.LOGERROR)

				if player_obj.sources_object and not player_obj._dialog_locked:
					player_obj._dialog_locked = True      # ✅ HARD LOCK
					player_obj._nextep_dialog_shown = True

					xbmc.log("PLAYLIST: Rendering playback transition interface overlay", xbmc.LOGINFO)
					if player_obj._next_added == True:
						player_obj.sources_object._make_nextep_dialog(default_action='play')

			# ✅ 9. SYSTEM BALANCE THROTTLE
			xbmc.sleep(500) # Balanced to 500ms to balance accuracy with low CPU usage
	except Exception as e:
		xbmc.log(f"MONITOR CRASH: {str(e)}", xbmc.LOGERROR)
		#xbmcgui.Window(10000).clearProperty('fenlight.monitor_id')

	finally:
		RedLightPlayer._monitor_running = False
		xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
		xbmc.log("PLAYLIST MONITOR STOPPED " + str(monitor_id), xbmc.LOGINFO)
		try:
			xbmc.sleep(3000)
			if xbmc.Player().isPlaying() == False:
				xbmc.log("PLAYLIST MONITOR clearProperty " + str(monitor_id), xbmc.LOGINFO)
				xbmcgui.Window(10000).clearProperty('fenlight.monitor_id')
		except:
			pass
		#xbmcgui.Window(10000).clearProperty('fenlight.monitor_id')
		#playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		#current_pos = playlist.getposition()
		#if current_pos < playlist.size() - 1 and player_obj._next_added == True:
		#	xbmcgui.Window(10000).setProperty('fenlight.onPlayBackStarted', 'onPlayBackStarted')


class PlayerMonitor(xbmc.Player):
	def __init__(self):
		xbmc.Player.__init__(self)
		self.player = xbmc.Player()


	def self_prep(self, player_obj, params):
		"""
		Replicates playback_prep() logic WITHOUT triggering playback or scraping
		"""
		if not params:
			params = {}

		kodi_utils.hide_busy_dialog()
		
		# Create Sources object
		from modules.sources import Sources
		sources = Sources()
		player_obj.sources_object = sources
		player_obj._monitor_running = False

		# === Replicate playback_prep logic manually ===
		if params:
			sources.params = params
		params_get = sources.params.get

		sources.background = params_get('background', 'false') == 'true'
		sources.play_type = params_get('play_type', '')
		sources.prescrape = params_get('prescrape', getattr(sources, 'prescrape', True)) == 'true'
		sources.random = params_get('random', 'false') == 'true'
		sources.random_continual = params_get('random_continual', 'false') == 'true'

		if 'external_cache_check' in sources.params:
			sources.cache_check_override = params_get('external_cache_check') == 'true'
		else:
			sources.cache_check_override = None

		# Autoplay / Nextep logic
		if sources.play_type:
			if sources.play_type == 'autoplay_nextep':
				sources.autoplay_nextep, sources.autoscrape_nextep = True, False
			elif sources.play_type == 'random_continual':
				sources.autoplay_nextep, sources.autoscrape_nextep = False, False
			else:
				sources.autoplay_nextep, sources.autoscrape_nextep = False, True
		else:
			sources.autoplay_nextep = settings.autoplay_next_episode()
			sources.autoscrape_nextep = settings.autoscrape_next_episode()

		sources.autoscrape = sources.autoscrape_nextep and sources.background
		sources.ignore_scrape_filters = params_get('ignore_scrape_filters', 'false') == 'true'
		sources.nextep_settings = params_get('nextep_settings', {})
		sources.disable_autoplay_next_episode = params_get('disable_autoplay_next_episode', 'false') == 'true'
		sources.disabled_ext_ignored = params_get('disabled_ext_ignored', getattr(sources, 'disabled_ext_ignored', False)) == 'true'

		sources.folders_ignore_filters = get_setting('redlight.results.folders_ignore_filters', 'false') == 'true'
		sources.filter_size_method = int(get_setting('redlight.results.filter_size_method', '0'))

		# Media identifiers
		sources.media_type = params_get('media_type') or params_get('tmdb_type', 'episode')
		sources.tmdb_id = params_get('tmdb_id')
		sources.custom_title = params_get('custom_title')
		sources.custom_year = params_get('custom_year')
		sources.episode_group_label = params_get('episode_group_label', '')
		sources.episode_id = params_get('episode_id')
		sources.playcount = params_get('playcount')
		sources.watch_count = params_get('watch_count', 1)

		if sources.media_type == 'episode':
			sources.season = int(params_get('season') or 1)
			sources.episode = int(params_get('episode') or 1)
			sources.custom_season = params_get('custom_season')
			sources.custom_episode = params_get('custom_episode')
			try:
				sources.check_episode_group()
			except:
				pass
		else:
			sources.season = sources.episode = sources.custom_season = sources.custom_episode = ''

		if 'autoplay' in sources.params:
			sources.autoplay = params_get('autoplay', 'false') == 'true'
		else:
			sources.autoplay = settings.auto_play(sources.media_type)

		if hasattr(sources, '_random_playback') and sources._random_playback():
			sources.autoplay = True

		sources.cloud_prescrape_autoplay = False
		sources._playback_failed_notified = False

		# Critical meta calls
		try:
			sources.get_meta()
		except Exception as e:
			xbmc.log(f"[redlight] sources.get_meta failed: {e}", xbmc.LOGDEBUG)

		try:
			sources.determine_scrapers_status()
		except:
			pass

		# Remaining settings
		sources.sleep_time = 100
		sources.provider_sort_ranks = settings.provider_sort_ranks()
		sources.scraper_settings = settings.scraping_settings()
		sources.include_prerelease_results = settings.include_prerelease_results()
		sources.limit_resolve = settings.limit_resolve()
		sources.weight_size = settings.size_sort_weighted()
		sources.sort_function = settings.results_sort_order()
		try:
			sources.quality_filter = sources._quality_filter()
		except:
			pass
		sources.include_unknown_size = get_setting('redlight.results.size_unknown', 'false') == 'true'

		try:
			sources.make_search_info()
		except:
			pass

		# === Now transfer to RedLightPlayer ===
		player_obj.is_generic = False
		player_obj._killed = False
		player_obj.stop_file = False
		player_obj._max_progress = 0.0
		player_obj.media_marked = False
		player_obj.nextep_info_gathered = False
		player_obj._next_added = False
		player_obj._dialog_locked = False
		player_obj._nextep_dialog_shown = False

		# Transfer key attributes
		for attr in ['params', 'media_type', 'tmdb_id', 'season', 'episode', 'imdb_id', 
					 'tvdb_id', 'title', 'year', 'meta', 'meta_get', 'nextep_settings',
					 'autoplay_nextep', 'autoscrape_nextep', 'autoplay', 'autoscrape',
					 'background', 'play_type']:
			if hasattr(sources, attr):
				setattr(player_obj, attr, getattr(sources, attr))

		if hasattr(player_obj, 'meta') and player_obj.meta:
			player_obj.meta_get = player_obj.meta.get
		else:
			player_obj.meta = {}
			player_obj.meta_get = {}.get

		player_obj.tmdb_id, player_obj.imdb_id, player_obj.tvdb_id = player_obj.meta_get('tmdb_id', ''), player_obj.meta_get('imdb_id', ''), player_obj.meta_get('tvdb_id', '')
		player_obj.media_type, player_obj.title, player_obj.year = player_obj.meta_get('media_type'), player_obj.meta_get('title'), player_obj.meta_get('year')
		player_obj.season, player_obj.episode = player_obj.meta_get('season', ''), player_obj.meta_get('episode', '')

		return player_obj

	def onPlayBackStarted(self):
		xbmc.sleep(3000)
		player  = RedLightPlayer()

		self.params = get_params_from_sorttitle(player)
		#season, episode = decode_sorttitle(player, get_current_sorttitle(player))
		#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
		#xbmc.log(str(self.params), level=xbmc.LOGINFO)
		#xbmc.log(str(player.params), level=xbmc.LOGINFO)
		if self.params.get('params',{}).get('REDLIGHT','') == 'REDLIGHT' or self.params.get('REDLIGHT','') == 'REDLIGHT':# or player.params.get('params',{}).get('REDLIGHT','') == 'REDLIGHT' or player.params.get('REDLIGHT','') == 'REDLIGHT':
			player = self.self_prep(player, self.params['params'])
			player.params = self.params['params']

		try:
			current_ep = get_current_episode_from_player(player)
			TMDbHelper_PlayerInfoString = xbmcgui.Window(10000).getProperty('TMDbHelper.PlayerInfoString')
			if current_ep:
				data = json.loads(TMDbHelper_PlayerInfoString)
				cur_season, cur_episode = current_ep
				self.params['season'] = str(cur_season)
				self.params['episode'] = str(cur_episode)
				if 'tmdb_type' in self.params and 'media_type' not in self.params:
					self.params['media_type'] = self.params['tmdb_type']
				TMDbHelper_NEW_PlayerInfoString = {'tmdb_type': data['tmdb_type'], 'tmdb_id': str(data['tmdb_id']), 'imdb_id': str(data['imdb_id']), 'tvdb_id': str(data['tvdb_id']), 'season': cur_season, 'episode': cur_episode}
				xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))
		except Exception as e:
			xbmc.log(f"[redlight] Decode failed: {e}", xbmc.LOGERROR)

		if self.params.get('params',{}).get('REDLIGHT','') == 'REDLIGHT' or self.params.get('REDLIGHT','') == 'REDLIGHT':# or player.params.get('params',{}).get('REDLIGHT','') == 'REDLIGHT' or player.params.get('REDLIGHT','') == 'REDLIGHT':
			monitor_id = str(uuid.uuid4())
			xbmcgui.Window(10000).setProperty('fenlight.monitor_id', monitor_id)
			RedLightPlayer._monitor_running = True
			Thread(target=monitor_playlist,args=(player,monitor_id,), daemon=True).start()


	def onPlayBackStopped(self):
		xbmcgui.Window(10000).clearProperty('script.trakt.ids')
		xbmcgui.Window(10000).clearProperty('TMDbHelper.PlayerInfoString')
		xbmcgui.Window(10000).clearProperty('subs.player_filename')

		monitor_id = str(uuid.uuid4())
		xbmcgui.Window(10000).setProperty('fenlight.monitor_id', monitor_id)
		RedLightPlayer._monitor_running = False
		#xbmcgui.Window(10000).clearProperty('fenlight.onPlayBackStarted')

	def onPlayBackEnded(self):
		xbmcgui.Window(10000).clearProperty('script.trakt.ids')
		xbmcgui.Window(10000).clearProperty('TMDbHelper.PlayerInfoString')
		xbmcgui.Window(10000).clearProperty('subs.player_filename')
		monitor_id = str(uuid.uuid4())
		xbmcgui.Window(10000).setProperty('fenlight.monitor_id', monitor_id)
		RedLightPlayer._monitor_running = False
		#xbmcgui.Window(10000).clearProperty('fenlight.onPlayBackStarted')


class NextEpisode(BaseDialog):

	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, *args)
		self.closed = False
		self.meta = kwargs.get('meta')
		self.selected = kwargs.get('default_action', 'cancel')
		#self.selected = 'play'
		#self._initial_file = self.player.getPlayingFile()
		self.set_properties()


	def onInit(self):
		self._initial_file = self.player.getPlayingFile()
		self.sleep(250)  # ✅ let Kodi render firs
		self.setFocusId(11)
		from threading import Thread
		Thread(target=self.monitor, daemon=True).start()
		self.sleep(250)  # ✅ let Kodi render firs
		self.setFocusId(11)

	def run(self):
		self.doModal()
		self.clearProperties()
		self.clear_modals()
		return self.selected

	def onAction(self, action):
		if action in self.closing_actions:
			self.selected = 'close'
			self.closed = True
			self.close()

	def onClick(self, controlID):
		self.selected = button_actions[controlID]
		self.closed = True
		if self.selected == 'play':
			xbmc.executebuiltin('PlayerControl(BigSkipForward)')
		elif self.selected == 'stop':
			xbmc.executebuiltin('PlayerControl(Stop)')
		elif self.selected in ('cancel', 'close'):
			pass  # do nothing
		self.close()


	def set_properties(self):
		episode_type = self.meta.get('episode_type', '')
		self.setProperty('thumb', self.meta.get('ep_thumb', None) or self.meta.get('fanart', ''))
		self.setProperty('clearlogo', self.meta.get('clearlogo', ''))
		try: self.setProperty('episode_label', '%s[B] | [/B]%02dx%02d[B] | [/B]%s' % (self.meta['title'], self.meta['season'], self.meta['episode'], self.meta['ep_name']))
		except: self.setProperty('episode_label', '%s[B] | [/B]%02dx%02d[B] | [/B]%s' % (str(self.meta['title']), str(self.meta['season']), str(self.meta['episode']), str(self.meta['ep_name'])))
		self.setProperty('episode_status.highlight', episode_status_dict[episode_type])
		self.setProperty('episode_status.flag', episode_flag_base % episode_type)

	def is_paused(self):
		try:
			import xbmc, json
			result = xbmc.executeJSONRPC(
				'{"jsonrpc":"2.0","method":"Player.GetProperties","params":{"playerid":1,"properties":["speed"]},"id":1}'
			)
			speed = json.loads(result)['result']['speed']
			return int(speed) == 0
		except:
			return False

	def monitor(self):
		start_time = time.time()

		while True:
			try:
				if self.closed:
					break

				if not self.player.isPlayingVideo():
					break

				if self.player.getPlayingFile() != self._initial_file:
					break

				# ✅ pause-safe timeout
				if not self.is_paused():
					try: remaining_time = int(self.player.getTotalTime()) - int(self.player.getTime())
					except: remaining_time = 99
					if remaining_time < 2:
						break
				else:
					start_time = time.time()

				self.sleep(500)

			except:
				break

		self.closed = True
		self.sleep(200)

		try:
			self.close()
		except:
			pass
		return xbmc.executebuiltin('Dialog.Close(next_episode.xml,true)')