# -*- coding: utf-8 -*-
import json
from threading import Thread
from apis.trakt_api import make_trakt_slug
from caches.settings_cache import get_setting
from modules import kodi_utils as ku, settings as st, watched_status as ws
# logger = ku.logger

import base64
from inspect import currentframe, getframeinfo
import xbmc,xbmcgui
import time
#xbmc.log(  str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))  , level=xbmc.LOGINFO)

set_property, clear_property, get_visibility, hide_busy_dialog, xbmc_actor = ku.set_property, ku.clear_property, ku.get_visibility, ku.hide_busy_dialog, ku.xbmc_actor
xbmc_player, execute_builtin, sleep = ku.xbmc_player, ku.execute_builtin, ku.sleep
make_listitem, volume_checker, get_infolabel, xbmc_monitor = ku.make_listitem, ku.volume_checker, ku.get_infolabel, ku.xbmc_monitor
close_all_dialog, notification, poster_empty, fanart_empty = ku.close_all_dialog, ku.notification, ku.empty_poster, ku.get_addon_fanart()
auto_resume, auto_nextep_settings, store_resolved_to_cloud = st.auto_resume, st.auto_nextep_settings, st.store_resolved_to_cloud
set_bookmark, mark_movie, mark_episode = ws.set_bookmark, ws.mark_movie, ws.mark_episode
total_time_errors = ('0.0', '', 0.0, None)
set_resume, set_watched = 5, 90
video_fullscreen_check = 'Window.IsActive(fullscreenvideo)'


class FenLightPlayer(xbmc_player):
	_monitor_running = False
	def __init__ (self):
		xbmc_player.__init__(self)
		self.player = xbmc_player()
		self.currently_popping = False
		self.sources_object = None
		self.nextep_info_gathered = False
		self.media_marked = False
		self.playback_successful = None
		self.cancel_all_playback = False
		self.stop_file = False
		self._next_added = False
		self._nextep_dialog_shown = False
		self._dialog_locked = False
		#FenLightPlayer._monitor_running = False

	def onPlayBackStarted(self):
		xbmc.log("onPlayBackStarted_FENLIGHT", xbmc.LOGINFO)
		self.currently_popping = False
		xbmc.log("FenLightPlayer___Playlist started", xbmc.LOGINFO)
		try:
			# ✅ reset state
			self._next_added = False
			self._nextep_dialog_shown = False
			# ✅ ensure monitor always running (CRITICAL FIX)
			#from threading import Thread
			#Thread(target=self.monitor_playlist, daemon=True).start()
		except Exception as e:
			xbmc.log(f"PLAYBACK START ERROR: {str(e)}", xbmc.LOGINFO)

	def onPlayBackEnded( self ):
		xbmc.log("onPlayBackEnded_FENLIGHT", xbmc.LOGINFO)
		if self.nextep_info_gathered: 
			try: self.clear_playback_properties()
			except: pass
			try: self.clear_playing_item()
			except: pass
			self.currently_popping = False
		else:
			self.currently_popping = True
		self.stop_file = True
		xbmc.log(  str("FenLightPlayer___End of Playlist" )  , level=xbmc.LOGINFO)

	def onPlayBackStopped( self ):
		hide_busy_dialog()
		try: self.clear_playback_properties()
		except: pass
		try: self.clear_playing_item()
		except: pass
		self.playback_successful = False
		self.cancel_all_playback = True
		self.currently_popping = True
		xbmc.log(  str("FenLightPlayer___playlist Stopped")  , level=xbmc.LOGINFO)
		self.stop_file = True
		return self.kill_dialog()

	def decode_sorttitle(self, st):
		"""
		Safely decodes base64 sorttitle and extracts season/episode integers.
		Handles potentially stripped base64 padding automatically.
		"""
		if not st:
			return None, None
		try:
			# Fix base64 padding issues if strings get stripped by database
			padded_st = st + '=' * (-len(st) % 4)
			decoded = base64.b64decode(padded_st).decode('utf-8', errors='ignore')
			
			# Extract structural elements from: tmdb_id_season_episode
			parts = decoded.split('_')
			if len(parts) == 3:
				_, season, episode = parts
				return int(season), int(episode)
			
		except Exception as e:
			xbmc.log(f"[decode_sorttitle] Failed parsing structure: {e}", xbmc.LOGDEBUG)
		
		return None, None

	def get_current_sorttitle(self, playerid=1):
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


	def get_current_episode_from_player(self):
		try:
			st = self.get_current_sorttitle()
			if not st:
				return None

			season, episode = self.decode_sorttitle(st)
			if season is None or episode is None:
				return None

			return season, episode

		except Exception as e:
			xbmc.log(f"get_current_episode_from_player error: {str(e)}", xbmc.LOGDEBUG)
			return None


	def get_playlist_sorttitles(self):
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

	def run(self, url=None, obj=None):
		hide_busy_dialog()
		self.clear_playback_properties()
		if not url: return self.run_error()
		try: return self.play_video(url, obj)
		except: return self.run_error()

	def play_video(self, url, obj):
		self.set_constants(url, obj)
		volume_checker()
		self.play(self.url, self.make_listing())
		if not self.is_generic:
			self.check_playback_start()
			if self.playback_successful: return self.monitor_playlist() #self.monitor()
			else:
				self.sources_object.playback_successful = self.playback_successful
				self.sources_object.cancel_all_playback = self.cancel_all_playback
				if self.cancel_all_playback: self.kill_dialog()
				self.stop()
			try: del self.kodi_monitor
			except: pass

	def check_playback_start(self):
		resolve_percent = 0
		while self.playback_successful is None:
			hide_busy_dialog()
			if not self.sources_object.progress_dialog: self.playback_successful = True
			elif self.sources_object.progress_dialog.skip_resolved(): self.playback_successful = False
			elif self.sources_object.progress_dialog.iscanceled() or self.kodi_monitor.abortRequested(): self.cancel_all_playback, self.playback_successful = True, False
			elif resolve_percent >= 100: self.playback_successful = False
			elif get_visibility('Window.IsTopMost(okdialog)'):
				execute_builtin('SendClick(okdialog, 11)')
				self.playback_successful = False
			elif self.isPlayingVideo():
				try:
					if self.getTotalTime() not in total_time_errors and get_visibility(video_fullscreen_check): self.playback_successful = True
				except: pass
			resolve_percent = round(resolve_percent + 26.0/100, 1)
			self.sources_object.progress_dialog.update_resolver(percent=resolve_percent)
			sleep(50)

	def playback_close_dialogs(self):
		self.sources_object.playback_successful = True
		self.kill_dialog()
		sleep(200)
		close_all_dialog()


	def run_playlist(self, url=None, obj=None):
		"""
		PLAYLIST MODE ENTRYPOINT (FIXED)
		"""
		hide_busy_dialog()
		self.clear_playback_properties()

		if not url:
			return self.run_error()

		self.set_constants(url, obj)

		playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

		# ✅ ONLY clear if nothing is playing
		if not self.isPlaying():
			playlist.clear()

		self._next_added = False
		self._nextep_dialog_shown = False

		# ✅ ONLY add first item if empty
		if playlist.size() == 0:
			listitem = self.make_listing()
			try:
				from modules.sources import make_sorttitle
				sorttitle_b64 = make_sorttitle(self.meta)
				listitem.getVideoInfoTag().setSortTitle(sorttitle_b64)
			except:
				pass

			playlist.add(url, listitem)
			self.play(playlist)

		# ✅ DO NOT depend on old resolve success logic
		# check_playback_start is unreliable for playlist model
		# self.check_playback_start()

		# ✅ start monitor ALWAYS (NEW)
		#Thread(target=self.monitor_playlist, daemon=True).start()

	def is_next_in_playlist(self):
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
					ns, ne = self.decode_sorttitle(st)
					expected = self.get_expected_next_episode()
					if expected == (ns, ne):
						return True
		except Exception as e:
			xbmc.log(f"is_next_in_playlist error: {str(e)}", xbmc.LOGDEBUG)

		return False

	def get_expected_next_episode(self):
		"""
		Resolves season and episode markers for the upcoming chronological episode.
		"""
		try:
			from modules.episode_tools import EpisodeTools

			base_meta = dict(self.meta)
			current_ep = self.get_current_episode_from_player()
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
			ep_tools = EpisodeTools(base_meta, self.nextep_settings)
			info = ep_tools.next_episode_info()

			#ep_tools = EpisodeTools(self.meta, self.nextep_settings)
			#info = ep_tools.next_episode_info()

			if not info:
				return None

			return int(info.get('season')), int(info.get('episode'))
		except:
			return None

	def _reset_state(self):
		"""
		Wipes local state logic parameters cleanly during track transition boundaries.
		"""
		self._next_added = False
		#self._nextep_dialog_shown = False
		self.nextep_info_gathered = False
		self.media_marked = False
		self.start_prep = None

		try:
			self.info_next_ep()
		except:
			pass

	def monitor_playlist(self, monitor_id=None):
		"""
		ROBUST PLAYLIST MONITOR (PRODUCTION READY)
		"""
		xbmc.log("PLAYLIST MONITOR STARTED", xbmc.LOGINFO)
		
		try:
			# Short baseline buffer for incoming playback allocations
			xbmc.sleep(1000)
			if self.isPlaying():
				self.stop_file = False

			not_playing_since = None
			was_playing = False
			seconds_stopped = 0.0
			last_loop_time = time.time() 
			while not self.stop_file:
				xbmc.sleep(100)
				current_id = xbmcgui.Window(10000).getProperty('fenlight.monitor_id')
				if current_id == None or current_id == '':
					current_id = str(0)
				if monitor_id != None:
					if monitor_id != current_id:
						xbmc.log("PLAYLIST MONITOR ENDED", xbmc.LOGINFO)
						self.stop_file = True
				if self.stop_file:
					break

				current_loop_time = time.time()
				loop_duration = current_loop_time - last_loop_time
				last_loop_time = current_loop_time
				# ✅ PLAYBACK STATE ACCUMULATION WATCHDOG
				if not self.isPlayingVideo():
					seconds_stopped += loop_duration
					if seconds_stopped >= 10.0:
						xbmc.log(f"PLAYLIST MONITOR: Continuous stoppage reached {seconds_stopped:.2f}s. Terminating.", xbmc.LOGINFO)
						self.stop_file = True
						break
					xbmc.sleep(250)
					# Removed 'continue' so the loop progresses normally and hits the main throttle below
				else:
					seconds_stopped = 0.0

				check_ep_flag = False
				if self.isPlaying() and check_ep_flag == False:
					current_ep = self.get_current_episode_from_player()
					if not current_ep:
						xbmcgui.Window(10000).clearProperty('fenlight.monitor_id')
						xbmc.log("NEXT_EP: Unable to resolve current episode from player", xbmc.LOGINFO)
						self.stop_file = True
						xbmc.log("PLAYLIST MONITOR ENDED", xbmc.LOGINFO)
						break
					check_ep_flag = True


				# ✅ 2. PLAYBACK TIMING ENGINE
				try:
					total = self.getTotalTime()
					current = self.getTime()
					if not total or total <= 0:
						xbmc.sleep(200)
						continue
					
					progress = (current / total) * 100
					remaining = total - current
				except Exception as e:
					xbmc.log(f"PLAYLIST TIME ACCUMULATION ERROR: {str(e)}", xbmc.LOGDEBUG)
					xbmc.sleep(500)
					continue

				# ✅ 3. DETECT TRACK CHANGE VIA PLAYLIST INDICES (FAST & NON-BLOCKING)
				try:
					playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
					pos = playlist.getposition()
				except:
					pos = -1

				if pos != getattr(self, "_last_pos", None) and pos >= 0:
					xbmc.log(f"PLAYLIST: Track index changed → {pos}", xbmc.LOGINFO)
					self._last_pos = pos
					self._current_sort = None  # Force sorttitle recalculation flag
					self._nextep_dialog_shown = False
					self._dialog_locked = False
					self._reset_state()
					current_ep = self.get_current_episode_from_player()
					cur_season, cur_episode = current_ep
					TMDbHelper_NEW_PlayerInfoString = {'tmdb_type': self.media_type, 'tmdb_id': str(self.tmdb_id), 'imdb_id': str(self.imdb_id), 'tvdb_id': str(self.tvdb_id), 'season': cur_season, 'episode': cur_episode}
					xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))
					PlayerInfoString = xbmcgui.Window(10000).getProperty('TMDbHelper.PlayerInfoString')

				# ✅ 4. VALIDATE META DATA SIGNATURES (NON-BLOCKING LOOKUP WITH TIMEOUT OMITTED IN LOOP)
				# Passing a custom dynamic flag or setting playerid parameters prevents loop stalls
				if not self._dialog_locked:
					current_sort = self.get_current_sorttitle()
					if current_sort and current_sort != getattr(self, "_current_sort", None):
						prev_sort = getattr(self, "_current_sort", None)
						self._current_sort = current_sort
						xbmc.log(f"PLAYLIST: Item changed metadata signature {prev_sort} → {current_sort}", xbmc.LOGINFO)
						self._reset_state()
						current_ep = self.get_current_episode_from_player()
						cur_season, cur_episode = current_ep
						TMDbHelper_NEW_PlayerInfoString = {'tmdb_type': self.media_type, 'tmdb_id': str(self.tmdb_id), 'imdb_id': str(self.imdb_id), 'tvdb_id': str(self.tvdb_id), 'season': cur_season, 'episode': cur_episode}
						xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))
						PlayerInfoString = xbmcgui.Window(10000).getProperty('TMDbHelper.PlayerInfoString')


				# ✅ 5. INITIALISE METADATA ENGINE ONCE PER EPISODE
				if not self.nextep_info_gathered:
					if not hasattr(self, "autoplay_nextep"):
						self.autoplay_nextep = False
					if not hasattr(self, "autoscrape_nextep"):
						self.autoscrape_nextep = True
					if not hasattr(self, "nextep_settings") and self.sources_object:
						self.nextep_settings = getattr(self.sources_object, "nextep_settings", None)
					
					try:
						self.info_next_ep()
						self.nextep_info_gathered = True
						xbmc.log("PLAYLIST: Successfully loaded upcoming item meta payload.", xbmc.LOGINFO)
					except Exception as e:
						xbmc.log(f"NEXTEP INFO ENGINE RECOVERY FAILURE: {str(e)}", xbmc.LOGERROR)

				# ✅ 6. WATCHED STATUS SYNC
				if progress >= set_watched and not self.media_marked:
					xbmc.log(f"NEXTEP: media_watched_marker", xbmc.LOGERROR)
					self.media_watched_marker()
					self.media_marked = True

				# ✅ 7. 35% SCRAPE COMPLETION TRIGGER
				if progress >= 35 and not self._next_added:
					# ✅ CRITICAL GUARD
					if self.is_next_in_playlist():
						xbmc.log("PLAYLIST: Next already queued → skipping scrape trigger", xbmc.LOGINFO)
						self._next_added = True
						continue
					self._next_added = True
					xbmc.log(f"PLAYLIST: Processing scrape targets. Keys: {list(self.meta.keys())}", xbmc.LOGINFO)
					try:
						if self.is_next_in_playlist():
							xbmc.log("PLAYLIST: Expected target exists down-queue → skipping background engine scrape", xbmc.LOGINFO)
						else:
							xbmc.log("PLAYLIST: Querying engines for subsequent stream links...", xbmc.LOGINFO)
							current_ep = self.get_current_episode_from_player()
							cur_season, cur_episode = current_ep
							self.run_next_ep_playlist()
							TMDbHelper_NEW_PlayerInfoString = {'tmdb_type': self.media_type, 'tmdb_id': str(self.tmdb_id), 'imdb_id': str(self.imdb_id), 'tvdb_id': str(self.tvdb_id), 'season': cur_season, 'episode': cur_episode}
							xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))
							PlayerInfoString = xbmcgui.Window(10000).getProperty('TMDbHelper.PlayerInfoString')

							
					except Exception as e:
						xbmc.log(f"NEXT SCRAPE OPERATION EXCEPTION: {str(e)}", xbmc.LOGERROR)

				# ✅ 8. 97% NEXT EPISODE DIALOG TRIGGER
				#if (progress >= 97 or remaining <= 30) and not self._nextep_dialog_shown:
				#	if self.sources_object:
				#		self._nextep_dialog_shown = True
				#		xbmc.log("PLAYLIST: Rendering playback transition interface overlay", xbmc.LOGINFO)
				#		self.sources_object._make_nextep_dialog(default_action='play')

				if (progress >= 97 or remaining <= 30):
					if self.sources_object and not self._dialog_locked:
						self._dialog_locked = True      # ✅ HARD LOCK
						self._nextep_dialog_shown = True

						xbmc.log("PLAYLIST: Rendering playback transition interface overlay", xbmc.LOGINFO)
						self.sources_object._make_nextep_dialog(default_action='play')

				# ✅ 9. SYSTEM BALANCE THROTTLE
				xbmc.sleep(500) # Balanced to 500ms to balance accuracy with low CPU usage
		except Exception as e:
			xbmc.log(f"MONITOR CRASH: {str(e)}", xbmc.LOGERROR)

		finally:
			FenLightPlayer._monitor_running = False
			xbmc.log("PLAYLIST MONITOR STOPPED", xbmc.LOGINFO)

	def check_playlist(self, b64_encode_dict, playlistid=1):
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

	def run_next_ep_playlist(self):
		#try:
		if 1==1:
			from modules.episode_tools import EpisodeTools
			from modules.sources import Sources, make_sorttitle

			#nextep_settings = getattr(self, "nextep_settings", None) or getattr(self.sources_object, "nextep_settings", None)

			# ✅ HARD GUARANTEE nextep_settings is valid
			if not getattr(self, "nextep_settings", None):
				try:
					# rebuild using same logic as info_next_ep
					play_type = 'autoplay_nextep' if getattr(self, "autoplay_nextep", False) else 'autoscrape_nextep'
					nextep_settings = st.auto_nextep_settings(play_type)

					self.nextep_settings = {
						'use_window': nextep_settings.get('alert_method', 0) == 0,
						'window_time': int((nextep_settings.get('window_percentage', 20) / 100) * (self.getTotalTime() or 1800)),
						'default_action': nextep_settings.get('default_action', 'play'),
						'play_type': play_type
					}
				except:
					self.nextep_settings = {
						'use_window': False,
						'window_time': 300,
						'default_action': 'play',
						'play_type': 'autoscrape_nextep'
					}

			nextep_settings = self.nextep_settings

			# ✅ Get next episode
			#ep_tools = EpisodeTools(self.meta, nextep_settings)

			from modules import metadata

			# ✅ rebuild full meta (CRITICAL FIX)
			try:
				if self.meta.get('media_type') == 'episode':
					base_meta = metadata.tvshow_meta(
						'tmdb_id',
						self.meta.get('tmdb_id'),
						st.tmdb_api_key(),
						st.mpaa_region(),
						ku.get_datetime()
					)

					# ✅ merge current episode context back in
					base_meta.update({
						'season': self.meta.get('season'),
						'episode': self.meta.get('episode')
					})
				else:
					base_meta = self.meta
			except:
				base_meta = self.meta

			#ep_tools = EpisodeTools(base_meta, nextep_settings)
			#url_params = ep_tools.next_episode_info()

			current_ep = self.get_current_episode_from_player()
			if not current_ep:
				xbmc.log("NEXT_EP: Unable to resolve current episode from player", xbmc.LOGINFO)
				return
			cur_season, cur_episode = current_ep
			# ✅ Inject correct episode into meta
			base_meta.update({
				'season': cur_season,
				'episode': cur_episode
			})
			ep_tools = EpisodeTools(base_meta, nextep_settings)
			url_params = ep_tools.next_episode_info()


			if not url_params or url_params in ('error', 'no_next_episode'):
				xbmc.log('NEXT_EP: No valid next episode info', xbmc.LOGINFO)
				return
			next_season = int(url_params.get('season', 0))
			next_episode_num = int(url_params.get('episode', 0))
			if not next_season or not next_episode_num:
				xbmc.log('NEXT_EP: Invalid episode numbers', xbmc.LOGINFO)
				return

			#if url_params == 'no_next_episode':
			#	xbmc.log("NEXT_EP: Series finished", xbmc.LOGINFO)
			#	return

			#params = {
			#	'media_type': 'episode',
			#	'tmdb_id': self.meta.get('tmdb_id'),
			#	'season': next_ep.get('season'),
			#	'episode': next_ep.get('episode'),
			#	'autoplay': 'true',
			#	'background': 'true'
			#}
			params = url_params
			
			# 🚨 HARD FIXES — THESE ARE THE WHOLE PROBLEM
			params.pop('nextep_settings', None)
			params.pop('play_type', None)

			params.update({
				'background': 'true',   # ✅ run in background
				'autoplay': 'false',    # ✅ DO NOT trigger play_file
			})


			#current_st = self.get_current_sorttitle()
			#cur_season, cur_episode = self.decode_sorttitle(current_st)
			## ✅ safety: only scrape NEXT episode
			#if cur_episode and cur_episode != self.meta.get('episode'):
			#	return


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
			for _ in range(2):
				results = sources.playback_prep(params)
				if results:
					break

			if not results:
				xbmc.log('NEXT_EP: No results after retry', xbmc.LOGINFO)
				return

			# ✅ ✅ CRITICAL FIX — use FULL autoplay resolve logic
			if isinstance(results, str):
				# ✅ Already resolved URL
				url = results

			elif isinstance(results, list):
				# ✅ Got source list (fallback case)
				url = sources.resolve_url(results)
			elif isinstance(results, dict):
				# ✅ Got source dict (fallback case)
				url = sources.resolve_url(results)
			else:
				xbmc.log('NEXT_EP: unexpected result type', xbmc.LOGINFO)
				return


			if not url:
				xbmc.log('NEXT_EP: resolve_url failed', xbmc.LOGINFO)
				return

			## ✅ Build listitem
			#player = FenLightPlayer()
			#player.set_constants(url, sources)
			#listitem = player.make_listing()


			# ✅ preserve current playback state
			saved_meta = self.meta
			saved_sources = self.sources_object

			# ✅ reuse CURRENT player instance (CRITICAL FIX)
			self.set_constants(url, sources)
			listitem = self.make_listing()

			# ✅ restore playback state
			self.meta = saved_meta
			self.sources_object = saved_sources

			try:
				sorttitle_b64 = make_sorttitle(sources.meta)
				listitem.getVideoInfoTag().setSortTitle(sorttitle_b64)
			except:
				sorttitle_b64 = None

			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

			# ✅ duplicate protection (correct)
			#existing_sorttitles = self.get_playlist_sorttitles()
			#if sorttitle_b64 in existing_sorttitles:
			#	xbmc.log('NEXT_EP: already exists in playlist, skipping scrape', xbmc.LOGINFO)
			#	return
			#if self.playlist_contains(sorttitle_b64):
			#	xbmc.log('NEXT_EP: already exists (logical match), skipping scrape', xbmc.LOGINFO)
			#	return

			check_playlist_flag = self.check_playlist(b64_encode_dict=sorttitle_b64, playlistid=1)

			if check_playlist_flag == False:
				playlist.add(url, listitem)
				xbmc.log('NEXT_EP: added to playlist', xbmc.LOGINFO)
			else:
				xbmc.log('NEXT_EP: ALREADY_IN_PLAYLIST', xbmc.LOGINFO)

		#except Exception as e:
		#	xbmc.log(f'NEXT_EP ERROR: {str(e)}', xbmc.LOGINFO)


	def monitor(self):
		# DISABLED - using playlist monitor
		return

		self.player_monitor = FenLightPlayer()
		try:
			ensure_dialog_dead, total_check_time = False, 0
			if self.media_type == 'episode':
				play_random_continual = self.sources_object.random_continual
				play_random = self.sources_object.random
				disable_autoplay_next_episode = self.sources_object.disable_autoplay_next_episode
				if disable_autoplay_next_episode: notification('Scrape with Custom Values - Autoplay Next Episode Cancelled', 4500)
				if any((play_random_continual, play_random, disable_autoplay_next_episode)): self.autoplay_nextep, self.autoscrape_nextep = False, False
				else: self.autoplay_nextep, self.autoscrape_nextep = self.sources_object.autoplay_nextep, self.sources_object.autoscrape_nextep
			else: play_random_continual, self.autoplay_nextep, self.autoscrape_nextep = False, False, False
			while total_check_time <= 30 and not get_visibility(video_fullscreen_check):
				sleep(100)
				total_check_time += 0.10
			hide_busy_dialog()
			sleep(1000)
			while self.isPlayingVideo():
				try:
					try: self.total_time, self.curr_time = self.getTotalTime(), self.getTime()
					except: sleep(250); continue
					if not ensure_dialog_dead:
						ensure_dialog_dead = True
						self.playback_close_dialogs()
					sleep(1000)
					self.current_point = round(float(self.curr_time/self.total_time * 100), 1)
					if self.current_point >= set_watched:
						if play_random_continual: self.run_random_continual(); break
						if not self.media_marked: self.media_watched_marker()
					if self.autoplay_nextep or self.autoscrape_nextep:
						if not self.nextep_info_gathered: self.info_next_ep()
						#xbmc.log(  str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))  , level=xbmc.LOGINFO)
						if round(self.total_time - self.curr_time) <= self.start_prep: 
							
							# DISABLED - playlist handles playback progression
							# return self.run_next_ep()
							# NEW
							return 
							
							#; break
				except: pass
			#xbmc.log(  str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))  , level=xbmc.LOGINFO)
			hide_busy_dialog()
			if not self.media_marked: self.media_watched_marker()
			sleep(500)
			#currently_popping = xbmcgui.Window(10000).getProperty('currently_popping')

			#window_id = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
			#window_id = json.loads(window_id)

			#xbmc.log(  str(self.currently_popping)  , level=xbmc.LOGINFO)
			#xbmc.log(  str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))  , level=xbmc.LOGINFO)
			#hide_busy_dialog()
			#if not self.media_marked: self.media_watched_marker()
			#if self.stop_file == True:
			#	xbmc.log(  str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))  , level=xbmc.LOGINFO)
			self.clear_playback_properties()
			self.clear_playing_item()
			if self.currently_popping == False:
				if self.autoplay_nextep or self.autoscrape_nextep:
					if not self.nextep_info_gathered: 
						self.info_next_ep()
					self.playback_successful, self.cancel_all_playback = None, False
					self.sources_object.playback_successful, self.sources_object.cancel_all_playback = None, False
					return  self.run_next_ep()
				#self.clear_playing_item()
			else:
				hide_busy_dialog()
				self.sources_object.playback_successful = False
				self.sources_object.cancel_all_playback = True
				return self.kill_dialog()
		except:
			hide_busy_dialog()
			self.sources_object.playback_successful = False
			self.sources_object.cancel_all_playback = True
			return self.kill_dialog()

	def make_listing(self):
		listitem = make_listitem()
		listitem.setPath(self.url)
		listitem.setContentLookup(False)
		if self.is_generic:
			info_tag = listitem.getVideoInfoTag()
			info_tag.setMediaType('video')
			info_tag.setFilenameAndPath(self.url)
		else:
			self.tmdb_id, self.imdb_id, self.tvdb_id = self.meta_get('tmdb_id', ''), self.meta_get('imdb_id', ''), self.meta_get('tvdb_id', '')
			self.media_type, self.title, self.year = self.meta_get('media_type'), self.meta_get('title'), self.meta_get('year')
			self.season, self.episode = self.meta_get('season', ''), self.meta_get('episode', '')
			self.auto_resume = auto_resume(self.media_type)
			poster = self.meta_get('poster') or poster_empty
			fanart = self.meta_get('fanart') or fanart_empty
			clearlogo = self.meta_get('clearlogo') or ''
			duration, plot, genre, trailer, mpaa = self.meta_get('duration'), self.meta_get('plot'), self.meta_get('genre', ''), self.meta_get('trailer'), self.meta_get('mpaa')
			rating, votes = self.meta_get('rating'), self.meta_get('votes')
			premiered, studio, tagline = self.meta_get('premiered'), self.meta_get('studio', ''), self.meta_get('tagline')
			director, writer, cast, country = self.meta_get('director', ''), self.meta_get('writer', ''), self.meta_get('cast', []), self.meta_get('country', '')
			listitem.setLabel(self.title)
			if self.media_type == 'movie':
				listitem.setArt({'poster': poster, 'fanart': fanart, 'icon': poster, 'clearlogo': clearlogo})
				info_tag = listitem.getVideoInfoTag()
				info_tag.setMediaType('movie'), info_tag.setTitle(self.title), info_tag.setOriginalTitle(self.meta_get('original_title')), info_tag.setPlot(plot)
				info_tag.setYear(int(self.year)), info_tag.setRating(rating), info_tag.setVotes(votes), info_tag.setMpaa(mpaa)
				info_tag.setDuration(duration), info_tag.setCountries(country), info_tag.setTrailer(trailer), info_tag.setPremiered(premiered)
				info_tag.setTagLine(tagline), info_tag.setStudios(studio), info_tag.setIMDBNumber(self.imdb_id), info_tag.setGenres(genre)
				info_tag.setWriters(writer), info_tag.setDirectors(director), info_tag.setUniqueIDs({'imdb': self.imdb_id, 'tmdb': str(self.tmdb_id)})
				info_tag.setCast([xbmc_actor(name=item['name'], role=item['role'], thumbnail=item['thumbnail']) for item in cast])
			else:
				listitem.setArt({'poster': poster, 'fanart': fanart, 'icon': poster, 'clearlogo': clearlogo, 'tvshow.poster': poster, 'tvshow.clearlogo': clearlogo})
				info_tag = listitem.getVideoInfoTag()
				info_tag.setMediaType('episode'), info_tag.setTitle(self.meta_get('ep_name')), info_tag.setOriginalTitle(self.meta_get('original_title'))
				info_tag.setTvShowTitle(self.title), info_tag.setTvShowStatus(self.meta_get('status')), info_tag.setSeason(self.season), info_tag.setEpisode(self.episode)
				info_tag.setPlot(plot), info_tag.setYear(int(self.year)), info_tag.setRating(rating), info_tag.setVotes(votes)
				info_tag.setMpaa(mpaa), info_tag.setDuration(duration), info_tag.setTrailer(trailer), info_tag.setFirstAired(premiered)
				info_tag.setStudios(studio), info_tag.setIMDBNumber(self.imdb_id), info_tag.setGenres(genre), info_tag.setWriters(writer)
				info_tag.setDirectors(director), info_tag.setUniqueIDs({'imdb': self.imdb_id, 'tmdb': str(self.tmdb_id), 'tvdb': str(self.tvdb_id)})
				info_tag.setCast([xbmc_actor(name=item['name'], role=item['role'], thumbnail=item['thumbnail']) for item in cast])
				info_tag.setFilenameAndPath(self.url)
			self.set_resume_point(listitem)
			self.set_playback_properties()
		return listitem

	def media_watched_marker(self, force_watched=False):
		self.media_marked = True
		try:
			if self.current_point >= set_watched or force_watched:
				if self.media_type == 'movie': watched_function = mark_movie
				else: watched_function = mark_episode
				watched_params = {'action': 'mark_as_watched', 'tmdb_id': self.tmdb_id, 'title': self.title, 'year': self.year, 'season': self.season, 'episode': self.episode,
									'tvdb_id': self.tvdb_id, 'from_playback': 'true'}
				Thread(target=self.run_media_progress, args=(watched_function, watched_params)).start()
			else:
				clear_property('fenlight.random_episode_history')
				if self.current_point >= set_resume:
					progress_params = {'media_type': self.media_type, 'tmdb_id': self.tmdb_id, 'curr_time': self.curr_time, 'total_time': self.total_time,
									'title': self.title, 'season': self.season, 'episode': self.episode, 'from_playback': 'true'}
					Thread(target=self.run_media_progress, args=(set_bookmark, progress_params)).start()
		except: pass

	def run_media_progress(self, function, params):
		try: function(params)
		except: pass

	def run_next_ep(self):
		from modules.episode_tools import EpisodeTools
		if not self.media_marked: self.media_watched_marker(force_watched=True)
		EpisodeTools(self.meta, self.nextep_settings).auto_nextep()

	def run_random_continual(self):
		from modules.episode_tools import EpisodeTools
		if not self.media_marked: self.media_watched_marker(force_watched=True)
		EpisodeTools(self.meta).play_random_continual(False)

	def set_resume_point(self, listitem):
		if self.playback_percent > 0.0: listitem.setProperty('StartPercent', str(self.playback_percent))

	def info_next_ep(self):
		self.nextep_info_gathered = True
		try:
			play_type = 'autoplay_nextep' if self.autoplay_nextep else 'autoscrape_nextep'
			nextep_settings = auto_nextep_settings(play_type)
			final_chapter = self.final_chapter() if nextep_settings['use_chapters'] else None
			percentage = 100 - final_chapter if final_chapter else nextep_settings['window_percentage']
			window_time = round((percentage/100) * self.total_time)
			use_window = nextep_settings['alert_method'] == 0
			default_action = nextep_settings['default_action']
			self.start_prep = nextep_settings['scraper_time'] + window_time
			self.nextep_settings = {'use_window': use_window, 'window_time': window_time, 'default_action': default_action, 'play_type': play_type}
		except: pass

	def final_chapter(self):
		try:
			final_chapter = float(get_infolabel('Player.Chapters').split(',')[-1])
			if final_chapter >= 90: return final_chapter
		except: pass
		return None

	def kill_dialog(self):
		try: self.sources_object._kill_progress_dialog()
		except: close_all_dialog()

	def set_constants(self, url, obj):
		self.url = url
		self.sources_object = obj
		self.is_generic = self.sources_object == 'video'
		if not self.is_generic:
			self.meta = self.sources_object.meta
			self.meta_get, self.kodi_monitor, self.playback_percent = self.meta.get, xbmc_monitor(), self.sources_object.playback_percent or 0.0
			#self.playing_filename = self.sources_object.playing_filename
			self.media_marked, self.nextep_info_gathered = False, False
			self.playback_successful, self.cancel_all_playback = None, False
			#self.playing_item = self.sources_object.playing_item
			self.playing_filename = getattr(self.sources_object, 'playing_filename', '')
			self.playing_item = getattr(self.sources_object, 'playing_item', {})


	def set_playback_properties(self):
		try:
			trakt_ids = {'tmdb': self.tmdb_id, 'imdb': self.imdb_id, 'slug': make_trakt_slug(self.title)}
			if self.media_type == 'episode': trakt_ids['tvdb'] = self.tvdb_id
			set_property('script.trakt.ids', json.dumps(trakt_ids))
			if self.playing_filename: set_property('subs.player_filename', self.playing_filename)
		except: pass
		if self.media_type == 'episode': 
			TMDbHelper_NEW_PlayerInfoString = {'tmdb_type': self.media_type, 'tmdb_id': str(self.tmdb_id), 'imdb_id': str(self.imdb_id), 'tvdb_id': str(trakt_ids['tvdb']), 'season': self.meta['season'], 'episode': self.meta['episode']}
			xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))
		#elif self.media_type == 'movie':
		#	data = {'tmdb_type': 'movie', 'tmdb_id': str(self.tmdb_id), 'imdb_id': str(self.imdb_id)}
		#	xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString',json.dumps(data))


	def clear_playback_properties(self):
		clear_property('fenlight.window_stack')
		clear_property('script.trakt.ids')
		clear_property('TMDbHelper.PlayerInfoString')
		clear_property('subs.player_filename')

	def clear_playing_item(self):
		if self.playing_item['cache_provider'] == 'Offcloud':
			if self.playing_item.get('direct_debrid_link', False): return
			if store_resolved_to_cloud('Offcloud', 'package' in self.playing_item): return
			from apis.offcloud_api import OffcloudAPI
			OffcloudAPI().clear_played_torrent(self.playing_item)

	def run_error(self):
		try: self.sources_object.playback_successful = False
		except: pass
		self.clear_playback_properties()
		notification('Playback Failed', 3500)
		return False
