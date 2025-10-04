import re, urllib.request, urllib.parse, urllib.error
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
from resources.lib import Utils
import sys
import gc
import importlib
import json
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short

import time
import sqlite3

import os
from urllib.parse import urlencode, quote_plus, unquote, unquote_plus

global dialog
dialog = None

class WindowManager(object):
	if not 'auto_library' in str(sys.argv) and not xbmc.Player().isPlaying():
		Utils.show_busy()
	window_stack = []


	def __init__(self):
		global dialog
		self.reopen_window = False
		self.last_control = None
		self.active_dialog = None
		self.curr_window = None
		self.prev_window = None
		self.pop_video_list = False
		self.page = None
		self.total_items = None
		self.total_pages = None
		self.filter_url = None
		self.order = None
		self.sort = None
		self.sort_label = None
		self.type = None
		self.filter = None
		self.prev_page_flag = False
		self.prev_page_num = 0
		self.page_position = None
		self.position = None
		self.focus_id = None
		self.custom_filter = None

		try: self.window_stack_len = self.window_stack_len
		except: self.window_stack_len = 0

		self.focus_id = None
		self.position = None
		osAndroid = xbmc.getCondVisibility('system.platform.android')
		if osAndroid:
			self.osAndroid_path = '-android'
		else:
			self.osAndroid_path = ''
	if 'estuary' in str(Utils.SKIN_DIR):
			 Utils.SKIN_DIR = 'skin.estuary'



	def window_stack_connection(self):
		window_stack = str(xbmcvfs.translatePath("special://profile/addon_data/"+addon_ID()+ '/window_stack.db'))
		if not os.path.exists(window_stack):
			create_window_stack = True
		else:
			create_window_stack = False

		con = sqlite3.connect(window_stack)
		cur = con.cursor()

		if create_window_stack:
			sql_result = cur.execute("""
			CREATE TABLE window_stack (
				inc_id INTEGER PRIMARY KEY AUTOINCREMENT,
				window VARCHAR NOT NULL
			);
			""").fetchall()
			con.commit()

		return con

	def window_stack_empty(self):
		self.window_stack_length()

		con = self.window_stack_connection()
		cur = con.cursor()
		sql_result = """
		DELETE FROM window_stack;
		"""
		sql_result = cur.execute(sql_result).fetchall()
		con.commit()
		self.window_stack_len = 0
		cur.close()
		con.close()
		xbmcgui.Window(10000).clearProperty('focus_id')
		xbmcgui.Window(10000).clearProperty('position')
		xbmcgui.Window(10000).clearProperty('pop_stack_focus_id')
		xbmcgui.Window(10000).clearProperty('pop_stack_position')
		return

	def window_stack_length(self):
		con = self.window_stack_connection()
		cur = con.cursor()
		sql_result = """
		select * from window_stack 
		"""
		sql_result = cur.execute(sql_result).fetchall()
		self.window_stack_len = len(sql_result)
		#Utils.tools_log(self.window_stack_len,self.window_stack_len)
		diamond_info_started = xbmcgui.Window(10000).getProperty('diamond_info_started')
		if diamond_info_started != 'True':
			self.window_stack_len = 0
		cur.close()
		con.close()
		return len(sql_result)

	def update_windows(self, curr_window, prev_window):
		self.curr_window = curr_window
		self.prev_window = prev_window
		self.page = curr_window['params']['page']
		self.total_pages = curr_window['params']['total_pages']
		self.total_items = curr_window['params']['total_items']
		self.type = wm.curr_window['params']['type']
		self.order = wm.curr_window['params']['order']

		self.sort_label = wm.curr_window['params']['sort_label']
		self.sort = wm.curr_window['params']['sort']

		self.filter_url = wm.curr_window['params']['filter_url']
		self.filter = wm.curr_window['params']['filter']
		self.mode = wm.curr_window['params']['mode']
		self.filter_label =wm.curr_window['params']['filter_label']
		self.list_id = wm.curr_window['params']['list_id']
		self.media_type = wm.curr_window['params']['media_type']
		self.filters = wm.curr_window['params']['filters']
		self.position = xbmcgui.Window(10000).getProperty('position')
		self.focus_id = xbmcgui.Window(10000).getProperty('focus_id')
		return

	def append_window_stack_table(self, mode=None):
		Utils.tools_log('WM_append_window_stack_table')

		con = self.window_stack_connection()
		cur = con.cursor()
		if mode == 'curr_window':
			self.prev_window = self.curr_window

		self.focus_id = xbmcgui.Window(10000).getProperty('focus_id')
		self.position = xbmcgui.Window(10000).getProperty('position')
		self.focus_id = wm.focus_id
		self.position = wm.position
		self.prev_window['params']['focus_id'] = self.focus_id
		self.prev_window['params']['position'] = self.position
		self.focus_id = None
		self.position = None
		wm.focus_id = None
		wm.position = None
		xbmcgui.Window(10000).setProperty('focus_id', str(self.focus_id))
		xbmcgui.Window(10000).setProperty('position', str(self.position))
		xbmcgui.Window(10000).setProperty('pop_stack_focus_id', str(self.focus_id))
		xbmcgui.Window(10000).setProperty('pop_stack_position', str(self.position))

		try:
			if 'youtubevideo' in str(self.prev_window['params']['listitems']):
				self.prev_window['function'] = 'open_youtube_list'
		except:
			pass

		self.page_position = None

		window = urlencode(self.prev_window)
		sql_result = """
		INSERT INTO window_stack (window)
		VALUES( '%s');
		""" % (window)
		sql_result = cur.execute(sql_result).fetchall()

		con.commit()
		cur.close()
		con.close()
		self.window_stack_length()
		try:
			self.last_control = xbmc.getInfoLabel('System.CurrentControlId').decode('utf-8')
		except:
			self.last_control = xbmc.getInfoLabel('System.CurrentControlId')
		if mode == 'curr_window':
			xbmc.executebuiltin('Dialog.Close(all,true)')
		return con

	def pop_window_stack_table(self):
		Utils.tools_log('WM_pop_window_stack_table')
		con = self.window_stack_connection()
		cur = con.cursor()

		sql_result = """
		select * from window_stack 
		order by inc_id desc limit 1
		"""
		sql_result = cur.execute(sql_result).fetchall()
		try: curr_window_number = int(xbmcgui.Window(10000).getProperty('diamond_window_number'))
		except: curr_window_number = None

		if len(sql_result) == 0:
			return
		window = sql_result[0][1]
		window_number = int(sql_result[0][0])
		if curr_window_number:
			if int(window_number) < int(curr_window_number):
				Utils.tools_log('window_number < curr_window_number','WM_pop_window_stack_table')
				return
		window = '{' + unquote_plus(window).replace('function=',"'function': '").replace('&params=',"', 'params': ") + '}'
		window = eval(window)
		self.curr_window = window
		xbmcgui.Window(10000).setProperty('diamond_window_number', str(window_number))

		sql_result = """
		DELETE FROM window_stack
		WHERE inc_id = '%s';
		""" % int(window_number)
		sql_result = cur.execute(sql_result).fetchall()
		con.commit()

		sql_result = """
		delete from sqlite_sequence where name='window_stack';
		"""
		sql_result = cur.execute(sql_result).fetchall()
		con.commit()

		cur.close()
		con.close()
		self.window_stack_length()
		self.focus_id = self.curr_window['params']['focus_id']
		self.position = self.curr_window['params']['position']
		xbmcgui.Window(10000).setProperty('focus_id', str(self.focus_id))
		xbmcgui.Window(10000).setProperty('position', str(self.position))
		xbmcgui.Window(10000).setProperty('pop_stack_focus_id', str(self.focus_id))
		xbmcgui.Window(10000).setProperty('pop_stack_position', str(self.position))

		if window['function'] == 'open_movie_info':
			return self.open_movie_info(movie_id=window['params']['movie_id'],dbid=window['params']['dbid'],name=window['params']['name'],imdb_id=window['params']['imdb_id'])
		elif window['function'] == 'open_tvshow_info':
			return self.open_tvshow_info(tmdb_id=window['params']['tmdb_id'],dbid=window['params']['dbid'],tvdb_id=window['params']['tvdb_id'],imdb_id=window['params']['imdb_id'],name=window['params']['name'])
		elif window['function'] == 'open_season_info':
			return self.open_season_info(tvshow_id=window['params']['tvshow_id'],season=window['params']['season'],tvshow=window['params']['tvshow'],dbid=window['params']['dbid'])
		elif window['function'] == 'open_episode_info':
			return self.open_episode_info(tvshow_id=window['params']['tvshow_id'], tvdb_id=window['params']['tvdb_id'],season=window['params']['season'],episode=window['params']['episode'],tvshow=window['params']['tvshow'],dbid=window['params']['dbid'])
		elif window['function'] == 'open_actor_info':
			return self.open_actor_info(actor_id=window['params']['actor_id'],name=window['params']['name'])
		elif window['function'] == 'open_video_list':
			self.pop_video_list = True
			return self.open_video_list(listitems=window['params']['listitems'],filters=window['params']['filters'],mode=window['params']['mode'],list_id=window['params']['list_id'],filter_label=window['params']['filter_label'],media_type=window['params']['media_type'],search_str=window['params']['search_str'])
		elif window['function'] == 'open_youtube_list':
			self.pop_video_list = True
			return self.open_youtube_list(search_str=window['params']['search_str'],filters=window['params']['filters'],filter_label=window['params']['filter_label'],media_type=window['params']['media_type'])

	def add_to_stack(self, window, mode=None):
		import xbmc
		if Utils.window_stack_enable == 'true':
			xbmc.executebuiltin('Dialog.Close(all,true)')
			self.append_window_stack_table(mode)
			self.window_stack_length()
		if Utils.window_stack_enable == 'false':
			try: window_stack = []
			except: pass
			try: self.window_stack = window_stack
			except: pass
			try: self.reopen_window = False
			except: pass
			try: self.last_control = None
			except: pass
			try: self.active_dialog = None
			except: pass
			try: window = None
			except: pass
			try: del window
			except: pass
			gc.collect()
			try:
				for k,v in sys.modules.items():
					if k.startswith('xbmc'):
						importlib.reload(v)
				import xbmc, xbmcgui, xbmcaddon
			except:
				pass
			return

	def pop_stack(self):
		window_id = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
		window_id = json.loads(window_id)

		try: currentwindow_id = int(window_id['result']['currentwindow']['id'])
		except: currentwindow_id = 0
		#Utils.tools_log(currentwindow_id,'currentwindow_id',window_id,'window_id','WM_pop_stack')
		#Utils.tools_log(xbmcgui.Window(10000).getProperty(str(addon_ID_short())+'_running') == 'True',xbmcgui.Window(10000).getProperty(str(addon_ID_short())+'_running'),str(addon_ID_short())+'_running')
		#Utils.tools_log(self.window_stack,'self.window_stack', Utils.window_stack_enable,'Utils.window_stack_enable',self.last_control,'self.last_control',self.focus_id,'self.focus_id',self.position,'self.position',self.reopen_window,'self.reopen_window')
		
		xbmc.executebuiltin('Dialog.Close(okdialog)')
		if xbmc.Player().isPlaying() or xbmc.getCondVisibility('Window.IsActive(12005)') or currentwindow_id >= 13001:
			if currentwindow_id >= 13001:
				xbmcgui.Window(10000).setProperty('diamond_info_time', str(int(time.time())+15))
			return
		xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'True')
		self.window_stack_len = self.window_stack_length()
		if (self.window_stack or self.window_stack_len > 0) and Utils.window_stack_enable == 'true':
			self.pop_window_stack_table()
			if self.last_control:
				xbmc.sleep(100)
				xbmc.executebuiltin('SetFocus(%s)' % self.last_control)
			if self.focus_id and self.position:
				xbmc.sleep(100)
				xbmc.executebuiltin('Control.SetFocus(%s,%s)' % (self.focus_id, self.position))

			try: window_stack = []
			except: pass
			try: self.window_stack = window_stack
			except: pass
			xbmc.sleep(250)
		elif self.reopen_window:
			xbmc.sleep(500)
			xbmc.executebuiltin('Action(Info)')
			if self.last_control:
				xbmc.sleep(100)
				xbmc.executebuiltin('SetFocus(%s)' % self.last_control)

	def open_movie_info(self, prev_window=None, movie_id=None, dbid=None, name=None, imdb_id=None):
		xbmc.executebuiltin('Dialog.Close(all,true)')
		Utils.show_busy()
		xbmcgui.Window(10000).setProperty('diamond_info_started', 'True')
		self.prev_window = self.curr_window 
		self.curr_window = {'function': 'open_movie_info', 'params': {'movie_id': movie_id, 'dbid': dbid, 'name': name, 'imdb_id': imdb_id}}

		from resources.lib.library import addon_ID
		from resources.lib.TheMovieDB import get_movie_tmdb_id, play_movie_trailer
		from resources.lib.DialogVideoInfo import get_movie_window
		if not 'tt' in str(imdb_id):
			imdb_id=None
		if not movie_id:
			movie_id = get_movie_tmdb_id(imdb_id=imdb_id, dbid=dbid, name=name)
		movieclass = get_movie_window(DialogXML)
		if Utils.NETFLIX_VIEW == 'true' or Utils.NETFLIX_VIEW2 == 'true':
			dialog = movieclass(str(addon_ID())+'-DialogVideoInfo-Netflix.xml', Utils.ADDON_PATH, id=movie_id, dbid=dbid)
			if Utils.AUTOPLAY_TRAILER == 'true' and not xbmc.getCondVisibility('VideoPlayer.IsFullscreen') and not xbmc.Player().isPlayingAudio():
				play_movie_trailer(movie_id)
		else:
			if Utils.SKIN_DIR == 'skin.estuary':
				dialog = movieclass(str(addon_ID())+self.osAndroid_path+'-DialogVideoInfo-Estuary.xml', Utils.ADDON_PATH, id=movie_id, dbid=dbid)
			elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
				dialog = movieclass(str(addon_ID())+'-DialogVideoInfo-Aura.xml', Utils.ADDON_PATH, id=movie_id, dbid=dbid)
			else:
				dialog = movieclass(str(addon_ID())+'-DialogVideoInfo.xml', Utils.ADDON_PATH, id=movie_id, dbid=dbid)
		self.open_dialog(dialog, prev_window)

		gc.collect()

	def open_tvshow_info(self, prev_window=None, tmdb_id=None, dbid=None, tvdb_id=None, imdb_id=None, name=None):
		xbmc.executebuiltin('Dialog.Close(all,true)')
		Utils.show_busy()
		xbmcgui.Window(10000).setProperty('diamond_info_started', 'True')
		self.prev_window = self.curr_window 
		self.curr_window = {'function': 'open_tvshow_info', 'params': {'tmdb_id': tmdb_id, 'dbid': dbid, 'tvdb_id': tvdb_id, 'imdb_id': imdb_id, 'name': name}}

		from resources.lib.library import addon_ID
		dbid = int(dbid) if dbid and int(dbid) > 0 else None
		from resources.lib.TheMovieDB import get_show_tmdb_id, search_media, play_tv_trailer, get_tvshow_info
		from resources.lib.DialogTVShowInfo import get_tvshow_window
		from resources.lib.local_db import get_imdb_id_from_db
		from resources.lib.local_db import get_info_from_db
		if tmdb_id:
			pass
		elif tvdb_id:
			tmdb_id = get_show_tmdb_id(tvdb_id)
		elif imdb_id and 'tt' in str(imdb_id):
			tmdb_id = get_show_tmdb_id(imdb_id=imdb_id, source='imdb_id')
		elif dbid:
			tvdb_id = get_imdb_id_from_db(media_type='tvshow', dbid=dbid)
			tv_info = get_info_from_db(media_type='tvshow', dbid=dbid)
			try: year = str(tv_info['year'])
			except: year = ''
			if tvdb_id:
				try:
					tmdb_id = get_show_tmdb_id(tvdb_id)
				except IndexError:
					if name:
						if year != '':
							tvshow = get_tvshow_info(tvshow_label=name, year=year)
							if tvshow and tvshow.get('id'):
								tmdb_id = tvshow.get('id')
							else:
								tmdb_id = search_media(media_name=name, year='', media_type='tv')
					else:
						name = xbmc.getInfoLabel('listitem.TvShowTitle')
						if str(name) != '':
							name = xbmc.getInfoLabel('listitem.Label')
						tvshow = get_tvshow_info(tvshow_label=name, year=year)
						if tvshow and tvshow.get('id'):
							tmdb_id = tvshow.get('id')
						else:
							tmdb_id = search_media(media_name=name, year='', media_type='tv')
		elif name:
			tvshow = get_tvshow_info(tvshow_label=name, year=year)
			if tvshow and tvshow.get('id'):
				tmdb_id = tvshow.get('id')
			else:
				tmdb_id = search_media(media_name=name, year='', media_type='tv')
		tvshow_class = get_tvshow_window(DialogXML)
		if Utils.NETFLIX_VIEW == 'true' or Utils.NETFLIX_VIEW2 == 'true':
			dialog = tvshow_class(str(addon_ID())+'-DialogVideoInfo-Netflix.xml', Utils.ADDON_PATH, tmdb_id=tmdb_id, dbid=dbid)
			if Utils.AUTOPLAY_TRAILER == 'true' and not xbmc.getCondVisibility('VideoPlayer.IsFullscreen') and not xbmc.Player().isPlayingAudio():
				play_tv_trailer(tmdb_id)
		else:
			if Utils.SKIN_DIR == 'skin.estuary':
				dialog = tvshow_class(str(addon_ID())+self.osAndroid_path+'-DialogVideoInfo-Estuary.xml', Utils.ADDON_PATH, tmdb_id=tmdb_id, dbid=dbid)
			elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
				dialog = tvshow_class(str(addon_ID())+'-DialogVideoInfo-Aura.xml', Utils.ADDON_PATH, tmdb_id=tmdb_id, dbid=dbid)
			else:
				dialog = tvshow_class(str(addon_ID())+'-DialogVideoInfo.xml', Utils.ADDON_PATH, tmdb_id=tmdb_id, dbid=dbid)
		self.open_dialog(dialog, prev_window)
		gc.collect()

	def open_season_info(self, prev_window=None, tvshow_id=None, season=None, tvshow=None, dbid=None):
		xbmc.executebuiltin('Dialog.Close(all,true)')
		Utils.show_busy()
		xbmcgui.Window(10000).setProperty('diamond_info_started', 'True')
		self.prev_window = self.curr_window 
		self.curr_window = {'function': 'open_season_info', 'params': {'tvshow_id': tvshow_id, 'season': season, 'tvshow': tvshow, 'dbid': dbid}}

		from resources.lib.library import addon_ID
		from resources.lib.TheMovieDB import get_tmdb_data
		from resources.lib.DialogSeasonInfo import get_season_window
		if not tvshow_id:
			response = get_tmdb_data('search/tv?query=%s&language=%s&' % (Utils.url_quote(tvshow), xbmcaddon.Addon().getSetting('LanguageID')), 30)
			if response['results']:
				tvshow_id = str(response['results'][0]['id'])
			else:
				tvshow = re.sub('\(.*?\)', '', tvshow)
				response = get_tmdb_data('search/tv?query=%s&language=%s&' % (Utils.url_quote(tvshow), xbmcaddon.Addon().getSetting('LanguageID')), 30)
				if response['results']:
					tvshow_id = str(response['results'][0]['id'])
		season_class = get_season_window(DialogXML)
		if Utils.NETFLIX_VIEW == 'true' or Utils.NETFLIX_VIEW2 == 'true':
			dialog = season_class(str(addon_ID())+'-DialogVideoInfo-Netflix.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, dbid=dbid)
		else:
			if Utils.SKIN_DIR == 'skin.estuary':
				dialog = season_class(str(addon_ID())+self.osAndroid_path+'-DialogVideoInfo-Estuary.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, dbid=dbid)
			elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
				dialog = season_class(str(addon_ID())+'-DialogVideoInfo-Aura.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, dbid=dbid)
			else:
				dialog = season_class(str(addon_ID())+'-DialogVideoInfo.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, dbid=dbid)
		self.open_dialog(dialog, prev_window)
		gc.collect()

	def open_episode_info(self, prev_window=None, tvshow_id=None, tvdb_id=None, season=None, episode=None, tvshow=None, dbid=None):
		xbmc.executebuiltin('Dialog.Close(all,true)')
		Utils.show_busy()
		xbmcgui.Window(10000).setProperty('diamond_info_started', 'True')
		self.prev_window = self.curr_window 
		self.curr_window = {'function': 'open_episode_info', 'params': {'tvshow_id': tvshow_id, 'tvdb_id': tvdb_id, 'season': season, 'episode': episode, 'tvshow': tvshow, 'dbid': dbid}}

		from resources.lib.library import addon_ID
		from resources.lib.TheMovieDB import get_tmdb_data, get_show_tmdb_id
		from resources.lib.DialogEpisodeInfo import get_episode_window
		if not tvshow_id:
			if tvdb_id:
				tvshow_id = get_show_tmdb_id(tvdb_id)
			else:
				response = get_tmdb_data('search/tv?query=%s&language=%s&' % (Utils.url_quote(tvshow), xbmcaddon.Addon().getSetting('LanguageID')), 30)
				if response['results']:
					tvshow_id = str(response['results'][0]['id'])
				else:
					tvshow = re.sub('\(.*?\)', '', tvshow)
					response = get_tmdb_data('search/tv?query=%s&language=%s&' % (Utils.url_quote(tvshow), xbmcaddon.Addon().getSetting('LanguageID')), 30)
					if response['results']:
						tvshow_id = str(response['results'][0]['id'])
		ep_class = get_episode_window(DialogXML)
		if Utils.NETFLIX_VIEW == 'true' or Utils.NETFLIX_VIEW2 == 'true':
			dialog = ep_class(str(addon_ID())+'-DialogVideoInfo-Netflix.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, episode=episode, dbid=dbid)
		else:
			if Utils.SKIN_DIR == 'skin.estuary':
				dialog = ep_class(str(addon_ID())+self.osAndroid_path+'-DialogVideoInfo-Estuary.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, episode=episode, dbid=dbid)
			elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
				dialog = ep_class(str(addon_ID())+'-DialogVideoInfo-Aura.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, episode=episode, dbid=dbid)
			else:
				dialog = ep_class(str(addon_ID())+'-DialogVideoInfo.xml', Utils.ADDON_PATH, tvshow_id=tvshow_id, season=season, episode=episode, dbid=dbid)
		self.open_dialog(dialog, prev_window)
		gc.collect()

	def open_actor_info(self, prev_window=None, actor_id=None, name=None):
		xbmc.executebuiltin('Dialog.Close(all,true)')
		Utils.show_busy()
		xbmcgui.Window(10000).setProperty('diamond_info_started', 'True')
		self.prev_window = self.curr_window 
		self.curr_window = {'function': 'open_actor_info', 'params': {'actor_id': actor_id, 'name': name}}

		from resources.lib.DialogActorInfo import get_actor_window
		from resources.lib.TheMovieDB import get_person_info
		from resources.lib.library import addon_ID
		if not actor_id:
			try:
				name = name.decode('utf-8').split(' ' + 'as' + ' ')
			except:
				name = str(name).split(' ' + 'as' + ' ')
			names = name[0].strip().split(' / ')
			if len(names) > 1:
				ret = xbmcgui.Dialog().select(heading='Select person', list=names)
				if ret == -1:
					return None
				name = names[ret]
			else:
				name = names[0]
			Utils.show_busy()
			actor_info = get_person_info(name)
			if actor_info:
				actor_id = actor_info['id']
			else:
				return None
		else:
			Utils.show_busy()
		actor_class = get_actor_window(DialogXML)
		if Utils.SKIN_DIR == 'skin.estuary':
			dialog = actor_class(str(addon_ID())+'-DialogInfo-Estuary.xml', Utils.ADDON_PATH, id=actor_id)
		elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
			dialog = actor_class(str(addon_ID())+'-DialogInfo-Aura.xml', Utils.ADDON_PATH, id=actor_id)
		else:
			dialog = actor_class(str(addon_ID())+'-DialogInfo.xml', Utils.ADDON_PATH, id=actor_id)
		self.open_dialog(dialog, prev_window)
		gc.collect()

	def open_video_list(self, prev_window=None, listitems=None, filters=[], mode='filter', list_id=False, filter_label='', media_type='movie', search_str=''):
		xbmc.executebuiltin('Dialog.Close(all,true)')
		Utils.show_busy()
		xbmcgui.Window(10000).setProperty('diamond_info_started', 'True')
		self.prev_window = self.curr_window 
		self.curr_window = {'function': 'open_video_list', 'params': {'listitems': listitems, 'filters': filters, 'mode': mode, 'list_id': list_id, 'filter_label': filter_label, 'media_type': media_type, 'search_str': search_str, 'page': self.page, 'total_pages': self.total_pages, 'total_items': self.total_items,'type': self.type, 'filter_url': self.filter_url, 'order': self.order, 'filter': filter, 'sort': self.sort, 'sort_label': self.sort_label}}
		if mode == 'reopen_window':
			self.window_stack_empty()
			prev_window = None
		from resources.lib.library import addon_ID
		from resources.lib.DialogVideoList import get_tmdb_window
		browser_class = get_tmdb_window(DialogXML)
		try: prev_window.close()
		except: pass
		if prev_window:
			self.add_to_stack(prev_window, 'prev_window')
			prev_window = None
			try: del prev_window
			except: pass
		if Utils.NETFLIX_VIEW == 'true':
			dialog = browser_class(str(addon_ID())+'-VideoList-Netflix.xml', Utils.ADDON_PATH, listitems=listitems, filters=filters, mode=mode, list_id=list_id, filter_label=filter_label, type=media_type, search_str=search_str)
		else:
			if Utils.SKIN_DIR == 'skin.estuary':
				dialog = browser_class(str(addon_ID())+self.osAndroid_path+'-VideoList-Estuary.xml', Utils.ADDON_PATH, listitems=listitems, filters=filters, mode=mode, list_id=list_id, filter_label=filter_label, type=media_type, search_str=search_str)
			elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
				dialog = browser_class(str(addon_ID())+'-VideoList-Aura.xml', Utils.ADDON_PATH, listitems=listitems, filters=filters, mode=mode, list_id=list_id, filter_label=filter_label, type=media_type, search_str=search_str)
			else:
				dialog = browser_class(str(addon_ID())+'-VideoList.xml', Utils.ADDON_PATH, listitems=listitems, filters=filters, mode=mode, list_id=list_id, filter_label=filter_label, type=media_type, search_str=search_str)
		Utils.hide_busy()
		gc.collect()
		dialog.doModal()
		if xbmcgui.Window(10000).getProperty(str(addon_ID_short())+'_running') == 'True':
			self.focus_id = xbmcgui.Window(10000).getProperty('focus_id')
			self.position = xbmcgui.Window(10000).getProperty('position')
			xbmcgui.Window(10000).clearProperty('focus_id')
			xbmcgui.Window(10000).clearProperty('position')
			xbmcgui.Window(10000).clearProperty('pop_stack_focus_id')
			xbmcgui.Window(10000).clearProperty('pop_stack_position')
			xbmc.executebuiltin('Dialog.Close(all,true)')
			xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'False')
			try: dialog.close()
			except: pass
			try: del dialog
			except: pass
		else:
			xbmc.executebuiltin('Dialog.Close(all,true)')

	def open_youtube_list(self, prev_window=None, search_str="", filters=None, filter_label="", media_type="video", curr_window=None):
		"""
		open video list, deal with window stack
		"""
		Utils.show_busy()
		xbmcgui.Window(10000).setProperty('diamond_info_started', 'True')
		if curr_window:
			self.prev_window = curr_window
		else:
			self.prev_window = self.curr_window 
		self.curr_window = {'function': 'open_youtube_list', 'params': {'search_str': search_str, 'filters': filters, 'filter_label': filter_label, 'media_type': media_type}}

		from resources.lib.library import addon_ID
		from resources.lib.DialogYoutubeList import get_youtube_window
		if prev_window:
			prev_window.close()
			self.add_to_stack(prev_window, 'prev_window')
			prev_window = None
			try: del prev_window
			except: pass
		browser_class = get_youtube_window(DialogXML)
		dialog = browser_class(str(addon_ID())+'-YoutubeList.xml', Utils.ADDON_PATH, search_str=search_str, filters=[] if not filters else filters, type='video')

		Utils.hide_busy()
		gc.collect()
		dialog.doModal()
		if xbmcgui.Window(10000).getProperty(str(addon_ID_short())+'_running') == 'True':

			self.focus_id = xbmcgui.Window(10000).getProperty('focus_id')
			self.position = xbmcgui.Window(10000).getProperty('position')
			xbmcgui.Window(10000).clearProperty('focus_id')
			xbmcgui.Window(10000).clearProperty('position')
			xbmcgui.Window(10000).clearProperty('pop_stack_focus_id')
			xbmcgui.Window(10000).clearProperty('pop_stack_position')
			xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'False')

			gc.collect()
			return
		else:
			xbmc.executebuiltin('Dialog.Close(all,true)')

	def open_slideshow(self, listitems, index):
		from resources.lib.library import addon_ID
		if Utils.SKIN_DIR == 'skin.estuary':
			slideshow = SlideShow(str(addon_ID())+'-SlideShow-Estuary.xml', Utils.ADDON_PATH, listitems=listitems, index=index)
		elif Utils.SKIN_DIR == 'skin.aura' or Utils.SKIN_DIR == 'skin.auramod' or Utils.SKIN_DIR == 'skin.xonfluence' or Utils.SKIN_DIR == 'skin.xenon18':
			slideshow = SlideShow(str(addon_ID())+'-SlideShow-Aura.xml', Utils.ADDON_PATH, listitems=listitems, index=index)
		else:
			slideshow = SlideShow(str(addon_ID())+'-SlideShow.xml', Utils.ADDON_PATH, listitems=listitems, index=index)
		Utils.hide_busy()
		slideshow.doModal()
		return slideshow.position

	def open_textviewer(self, header='', text='', color='FFFFFFFF'):
		dialog = TextViewerDialog('DialogTextViewer.xml', Utils.ADDON_PATH, header=header, text=text, color=color)
		Utils.hide_busy()
		dialog.doModal()
		try: del dialog
		except: pass
		gc.collect()

	def open_selectdialog_autoclose(self, listitems, autoclose=0, autoselect=0):
		dialog = SelectDialog('DialogSelect.xml', Utils.ADDON_PATH, listing=listitems, autoclose=autoclose, autoselect=autoselect)
		Utils.hide_busy()
		dialog.doModal()
		return dialog.listitem, dialog.index

	def open_selectdialog(self, listitems):
		dialog = SelectDialog('DialogSelect.xml', Utils.ADDON_PATH, listing=listitems)
		Utils.hide_busy()
		dialog.doModal()
		return dialog.listitem, dialog.index

	def open_dialog(self, dialog, prev_window):

		xbmcgui.Window(10000).setProperty('diamond_info_started', 'True')
		if dialog.data:
			if Utils.window_stack_enable == 'true':
				self.active_dialog = dialog
			if xbmc.getCondVisibility('Window.IsVisible(movieinformation)'):
				self.reopen_window = True
				try:
					self.last_control = xbmc.getInfoLabel('System.CurrentControlId').decode('utf-8')
				except:
					self.last_control = xbmc.getInfoLabel('System.CurrentControlId')
				xbmc.executebuiltin('Dialog.Close(movieinformation)')
			xbmc.executebuiltin('Dialog.Close(all,true)')
			if prev_window:
				prev_window.close()
				if xbmc.Player().isPlayingVideo() and not xbmc.getCondVisibility('VideoPlayer.IsFullscreen'):
					xbmc.Player().stop()
				xbmc.executebuiltin('Dialog.Close(all,true)')
				self.add_to_stack(prev_window, 'prev_window')
				prev_window = None
				del prev_window
			Utils.hide_busy()
			gc.collect()
			dialog.doModal()
			if xbmcgui.Window(10000).getProperty(str(addon_ID_short())+'_running') == 'True':
				self.focus_id = xbmcgui.Window(10000).getProperty('focus_id')
				self.position = xbmcgui.Window(10000).getProperty('position')
				xbmcgui.Window(10000).clearProperty('focus_id')
				xbmcgui.Window(10000).clearProperty('position')
				xbmcgui.Window(10000).clearProperty('pop_stack_focus_id')
				xbmcgui.Window(10000).clearProperty('pop_stack_position')
				xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'False')
				gc.collect()
				return
			else:
				xbmc.executebuiltin('Dialog.Close(all,true)')
		else:
			Utils.hide_busy()
			self.active_dialog = None
			try: dialog.close()
			except: pass
			try: del dialog
			except: pass
			try: del prev_window
			except: pass
			gc.collect()
			Utils.notify('Could not find item at MovieDB')

wm = WindowManager()

class DialogXML(xbmcgui.WindowXMLDialog):

	def __init__(self, *args, **kwargs):
		xbmcgui.WindowXMLDialog.__init__(self)
		self.window_type = 'dialog'

	def onInit(self):
		self.window_id = xbmcgui.getCurrentWindowDialogId()
		self.window = xbmcgui.Window(self.window_id)


class TextViewerDialog(xbmcgui.WindowXMLDialog):

	ACTION_PREVIOUS_MENU = [9, 92, 10]

	def __init__(self, *args, **kwargs):
		xbmcgui.WindowXMLDialog.__init__(self)
		self.text = kwargs.get('text')
		self.header = kwargs.get('header')
		self.color = kwargs.get('color')

	def onInit(self):
		window_id = xbmcgui.getCurrentWindowDialogId()
		xbmcgui.Window(window_id).setProperty('WindowColor', self.color)
		self.getControl(1).setLabel(self.header)
		self.getControl(5).setText(self.text)

	def onAction(self, action):
		if action in self.ACTION_PREVIOUS_MENU:
			self.close()

	def onClick(self, control_id):
		pass

	def onFocus(self, control_id):
		pass

class SlideShow(DialogXML):

	ACTION_PREVIOUS_MENU = [9, 92, 10]

	def __init__(self, *args, **kwargs):
		self.images = kwargs.get('listitems')
		self.index = kwargs.get('index')
		self.image = kwargs.get('image')
		self.action = None

	def onInit(self):
		super(SlideShow, self).onInit()
		if not self.images:
			return None
		self.getControl(10001).addItems(Utils.create_listitems(self.images))
		self.getControl(10001).selectItem(self.index)
		self.setFocusId(10001)

	def onAction(self, action):
		if action in self.ACTION_PREVIOUS_MENU:
			self.position = self.getControl(10001).getSelectedPosition()
			self.close()

class SelectDialog(xbmcgui.WindowXMLDialog):

	ACTION_PREVIOUS_MENU = [9, 92, 10]

	def __init__(self, *args, **kwargs):
		xbmcgui.WindowXMLDialog.__init__(self)
		self.items = kwargs.get('listing')
		self.listitems = Utils.create_listitems(self.items)
		self.listitem = None
		self.index = -1
		self.closed = None
		self.autoselect = kwargs.get('autoselect')
		self.autoclose = kwargs.get('autoclose')
		self.autoclose_time = None
		if self.autoclose > 0:
			self.autoclose_time = time.time() + self.autoclose

	def onInit(self):
		self.list = self.getControl(6)
		self.getControl(3).setVisible(False)
		self.getControl(5).setVisible(False)
		self.getControl(1).setLabel('Choose option')
		self.getControl(8).setVisible(False)
		self.list.addItems(self.listitems)
		self.setFocus(self.list)
		self.background_tasks()

	def background_tasks(self):
		while not self.closed:
			curr_time = time.time()
			try: self.getControl(1).setLabel(self.list.getSelectedItem().getProperty('label2'))
			except AttributeError: 
				self.closed = True
				return
			if self.autoclose != 0 and self.autoclose_time <= curr_time:
				self.index = self.list.getSelectedPosition()
				self.closed = True
				self.close()
			xbmc.sleep(500)

	def onAction(self, action):
		if action in self.ACTION_PREVIOUS_MENU:
			self.closed = True
			self.close()

	def onClick(self, control_id):
		Utils.tools_log(control_id)
		if control_id == 6 or control_id == 3:
			self.index = int(self.list.getSelectedItem().getProperty('index'))
			self.listitem = self.items[self.index]
			self.closed = True
			self.close()
		if control_id == 7:
			self.index = -1
			self.listitem = []
			self.closed = True
			self.close()

	def onFocus(self, control_id):
		self.getControl(1).setLabel(self.list.getSelectedItem().getProperty('label2'))
		pass
