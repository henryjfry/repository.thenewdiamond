import os, shutil
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
from resources.lib import Utils
from resources.lib.WindowManager import wm
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib.library import icon_path
from resources.autocomplete import AutoCompletion
from resources.autocomplete import AutoCompletion_plugin
from urllib.parse import quote, urlencode, quote_plus, unquote, unquote_plus
import time

from a4kscrapers_wrapper.tools import log
from inspect import currentframe, getframeinfo
#log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

def start_info_actions(infos, params):
	addonID = addon_ID()
	addonID_short = addon_ID_short()

	wm.custom_filter = params.get('meta_filter')
	log(Utils.db_con)
	if wm.custom_filter:
		wm.custom_filter = eval(unquote(wm.custom_filter))

	keep_stack = params.get('keep_stack',False)

	if 'imdbid' in params and 'imdb_id' not in params:
		params['imdb_id'] = params['imdbid']
	for info in infos:
		Utils.show_busy()
		data = [], ''

		if info == 'rss_test':
			from a4kscrapers_wrapper import get_meta
			get_meta.get_rss_cache()

		if info == 'con_man_fix':
			from resources.lib.con_man_fix import list_and_select_wifi
			Utils.hide_busy()
			list_and_select_wifi()
			Utils.hide_busy()
			return

		if info == 'delete_db_expired':
			Utils.db_delete_expired(Utils.db_con)

		if info == 'clear_db':
			table_name = params.get('table_name', False)
			Utils.clear_db(Utils.db_con,table_name)

		if info == 'getplayingfile':
			xbmc.log(str(xbmc.Player().getPlayingFile())+'===>OPENINFO', level=xbmc.LOGINFO)

		if info == 'authRealDebrid':
			from a4kscrapers_wrapper import real_debrid
			rd_api = real_debrid.RealDebrid()
			rd_api.auth_kodi()
			Utils.hide_busy()

		if info == 'context_info':
			if xbmc.Player().isPlaying():
				context_info()
			else:
				context_info2()

		if info == 'a4kProviders':
			from a4kscrapers_wrapper import getSources
			getSources.setup_providers('https://bit.ly/a4kScrapers')
			#try: getSources.setup_providers('https://bit.ly/a4kScrapers')
			#except Exception: 
			#	if 'shutil.Error:' in str(Exception):
			#		tools.log('Error', 'Already Exists',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			Utils.hide_busy()

		if info == 'a4kProviders_manage':
			from a4kscrapers_wrapper import getSources
			getSources.enable_disable_providers_kodi()
			Utils.hide_busy()

		if info == 'url_encode_test':
			meta_filters = "{'filters' : {'sort': 'desc', 'sort_string': 'revenue', 'with_genres': ['action','comedy'], 'without_genres': ['horror','reality','documentary'], 'with_original_language': 'en', 'vote_count.gte': '10', 'vote_count.lte': '10 000 000', 'lower_year': '1990', 'upper_year': '1999' } }"
			meta_filters = "{'filters' : {'sort': 'desc', 'sort_string': 'popularity', 'without_genres': ['horror','reality','documentary'], 'genre_mode': 'OR', 'with_original_language': 'en' } }"
			meta_filters = "{'filters' : {'sort': 'desc', 'sort_string': 'popularity', 'with_genres': ['Science Fiction'], 'genre_mode': 'OR', 'with_original_language': 'en' } }"
			meta_filters = "{'filters' : {'sort': 'desc', 'sort_string': 'popularity', 'with_genres': ['Sci-Fi'], 'genre_mode': 'OR', 'with_original_language': 'en' } }"
			meta_filters = quote(meta_filters)
			xbmc.log(str(meta_filters)+'===>META_FILTERS', level=xbmc.LOGINFO)

		if info == 'get_trakt_playback':
			from resources.lib import TheMovieDB
			trakt_type = params.get('trakt_type')
			TheMovieDB.get_trakt_playback(trakt_type)
			return

		if info == 'display_dialog':
			next_ep_url = params.get('next_ep_url')
			title = unquote_plus(params.get('title'))
			thumb = params.get('thumb')
			rating = params.get('rating')
			show = params.get('show')
			season = params.get('season')
			episode = params.get('episode')
			year = params.get('year')
			from resources.player import PlayerDialogs
			PlayerDialogs().display_dialog(str(next_ep_url), str(title), str(thumb), str(rating), str(show), str(season), str(episode), str(year))

		if info == 'libraryallmovies':
			from resources.lib import local_db
			try:
				script = str(params['script'])
			except:
				script = 'True'
			if script == 'False':
				return local_db.get_db_movies('"sort": {"order": "descending", "method": "dateadded", "limit": %s}' % params.get("limit", "0"))
			wm.window_stack_empty()
			return wm.open_video_list(media_type='movie', mode='list_items', filter_label='My TV Shows (Movies)' ,search_str=local_db.get_db_tvshows('"sort": {"order": "descending", "method": "dateadded", "limit": %s}' % params.get("limit", "0")), listitems=[])

		elif info == 'libraryalltvshows':
			from resources.lib import local_db
			try:
				script = str(params['script'])
			except:
				script = 'True'
			if script == 'False':
				return local_db.get_db_tvshows('"sort": {"order": "descending", "method": "dateadded", "limit": %s}' % params.get("limit", "0"))
			wm.window_stack_empty()
			return wm.open_video_list(media_type='tv', mode='list_items', filter_label='My TV Shows (Library)' ,search_str=local_db.get_db_tvshows('"sort": {"order": "descending", "method": "dateadded", "limit": %s}' % params.get("limit", "0")), listitems=[])

		elif info == 'popularmovies':
			from resources.lib import TheMovieDB
			tmdb_var = 'popular'
			filter_label = 'Popular Movies'
			media_type = 'movie'
			try:
				script = str(params['script'])
			except:
				script = 'True'
			if script == 'False':
				return TheMovieDB.get_tmdb_movies(tmdb_var)
			wm.window_stack_empty()
			return wm.open_video_list(media_type=media_type, mode='list_items', filter_label=filter_label, search_str=TheMovieDB.get_tmdb_movies(tmdb_var), listitems=[])

		elif info == 'topratedmovies':
			from resources.lib import TheMovieDB
			tmdb_var = 'top_rated'
			filter_label = 'Top Rated Movies'
			media_type = 'movie'
			try:
				script = str(params['script'])
			except:
				Utils.hide_busy()
				script = 'False'
			if script == 'False':
				return TheMovieDB.get_tmdb_movies(tmdb_var)
			wm.window_stack_empty()
			return wm.open_video_list(media_type=media_type, mode='list_items', filter_label=filter_label, search_str=TheMovieDB.get_tmdb_movies(tmdb_var), listitems=[])

		elif info == 'incinemamovies':
			from resources.lib import TheMovieDB
			tmdb_var = 'now_playing'
			filter_label = 'In Theaters Movies'
			media_type = 'movie'
			try:
				script = str(params['script'])
			except:
				script = 'True'
			if script == 'False':
				return TheMovieDB.get_tmdb_movies(tmdb_var)
			wm.window_stack_empty()
			return wm.open_video_list(media_type=media_type, mode='list_items', filter_label=filter_label, search_str=TheMovieDB.get_tmdb_movies(tmdb_var), listitems=[])

		elif info == 'upcomingmovies':
			from resources.lib import TheMovieDB
			tmdb_var = 'upcoming'
			filter_label = 'Upcoming Movies'
			media_type = 'movie'
			try:
				script = str(params['script'])
			except:
				script = 'True'
			if script == 'False':
				return TheMovieDB.get_tmdb_movies(tmdb_var)
			wm.window_stack_empty()
			return wm.open_video_list(media_type=media_type, mode='list_items', filter_label=filter_label, search_str=TheMovieDB.get_tmdb_movies(tmdb_var), listitems=[])

		elif info == 'populartvshows':
			from resources.lib import TheMovieDB
			tmdb_var = 'popular'
			filter_label = 'Popular TV Shows'
			media_type = 'tv'
			try:
				script = str(params['script'])
			except:
				script = 'True'
			if script == 'False':
				return TheMovieDB.get_tmdb_shows(tmdb_var)
			wm.window_stack_empty()
			return wm.open_video_list(media_type=media_type, mode='list_items', filter_label=filter_label, search_str=TheMovieDB.get_tmdb_shows(tmdb_var), listitems=[])


		elif info == 'topratedtvshows':
			from resources.lib import TheMovieDB
			tmdb_var = 'top_rated'
			filter_label = 'Top Rated TV Shows'
			media_type = 'tv'
			try:
				script = str(params['script'])
			except:
				Utils.hide_busy()
				script = 'False'
			if script == 'False':
				return TheMovieDB.get_tmdb_shows(tmdb_var)
			wm.window_stack_empty()
			return wm.open_video_list(media_type=media_type, mode='list_items', filter_label=filter_label, search_str=TheMovieDB.get_tmdb_shows(tmdb_var), listitems=[])

		elif info == 'onairtvshows':
			from resources.lib import TheMovieDB
			tmdb_var = 'on_the_air'
			filter_label = 'Currently Airing TV Shows'
			media_type = 'tv'
			try:
				script = str(params['script'])
			except:
				script = 'True'
			if script == 'False':
				return TheMovieDB.get_tmdb_shows(tmdb_var)
			wm.window_stack_empty()
			return wm.open_video_list(media_type=media_type, mode='list_items', filter_label=filter_label, search_str=TheMovieDB.get_tmdb_shows(tmdb_var), listitems=[])

		elif info == 'airingtodaytvshows':
			from resources.lib import TheMovieDB
			tmdb_var = 'airing_today'
			filter_label = 'Airing Today TV Shows'
			media_type = 'tv'
			try:
				script = str(params['script'])
			except:
				script = 'True'
			if script == 'False':
				return TheMovieDB.get_tmdb_shows(tmdb_var)
			wm.window_stack_empty()
			return wm.open_video_list(media_type=media_type, mode='list_items', filter_label=filter_label, search_str=TheMovieDB.get_tmdb_shows(tmdb_var), listitems=[])

		elif info == 'allmovies':
			wm.window_stack_empty()
			wm.open_video_list(media_type='movie',mode='filter')

		elif info == 'alltvshows':
			wm.window_stack_empty()
			wm.open_video_list(media_type='tv',mode='filter')

		elif info == 'search_menu':
			search_str = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
			wm.window_stack_empty()
			return wm.open_video_list(search_str=search_str, mode='search')


		elif info == 'ep_movie_progress':
			search_str = 'Trakt Episodes/Movies in progress'
			#type = 'movie'
			wm.window_stack_empty()
			return wm.open_video_list(search_str=search_str, mode='filter')



		elif info == 'reopen_window':
			reopen_window()

		elif info == 'service2':
			import service2

		elif info == 'youtube':
			search_str = params.get('search_str')
			wm.window_stack_empty()
			return wm.open_youtube_list(search_str=search_str)

		elif info == 'tastedive_search':
			search_str = params.get('search_str')
			media_type = str(params['media_type'])
			limit = params.get('limit', 10)
			from resources.lib import TheMovieDB
			#response = TheMovieDB.get_tastedive_data(query=search_str, limit=limit, media_type=media_type)
			response = TheMovieDB.get_tastedive_data_scrape(query=search_str, year='', limit=50, media_type=media_type)
			wm.window_stack_empty()
			return wm.open_video_list(mode='tastedive&' + str(media_type), listitems=[], search_str=response, filter_label='TasteDive Similar ('+str(search_str)+'):')

		elif info == 'tastedive_movies':
			from resources.lib import TheMovieDB
			response = TheMovieDB.get_trakt(trakt_type='movie',info='trakt_watched',limit=30)
			response3 = []
			for i in response:
				#response2 = TheMovieDB.get_tastedive_data(query=i['title'], limit=30, media_type='movie')
				response2 = TheMovieDB.get_tastedive_data_scrape(query=i['title'], year=i['year'], limit=50, media_type='movie',item_id=i['id'])

				original_title = i['original_title']
				original_title2 = ''
				try:
					for ix in i['alternative_titles']['titles']:
						if ix['type'] == 'original title' and ix['iso_3166_1'] in {'US','UK'}:
							original_title2 = ix['title']
					if original_title2 != original_title and original_title2 != '':
						original_title = original_title2
				except:
					pass

				for x in response2:
					if x not in response3:
						response3.append(x)
			wm.window_stack_empty()
			return wm.open_video_list(mode='tastedive&' + str('movie'), listitems=[], search_str=response3, filter_label='TasteDive Based on Recently Watched Movies:')

		elif info == 'tastedive_tv':
			from resources.lib import TheMovieDB
			response = TheMovieDB.get_trakt(trakt_type='tv',info='trakt_watched',limit=30)
			response3 = []
			for i in response:
				#response2 = TheMovieDB.get_tastedive_data(query=i['title'], limit=30, media_type='tv')
				response2 = TheMovieDB.get_tastedive_data_scrape(query=i['title'], year=i['year'], limit=50, media_type='tv',item_id=i['id'])
				for x in response2:
					if x not in response3:
						response3.append(x)
			wm.window_stack_empty()
			return wm.open_video_list(mode='tastedive&' + str('tv'), listitems=[], search_str=response3, filter_label='TasteDive Based on Recently Watched TV:')

		elif info == 'autocomplete' or info == 'selectautocomplete':
			items = AutoCompletion_plugin.start_info_actions(infos, params)
			return items

		elif info == 'eject_load_dvd':
			try:
				import platform
				if platform.system() == "Linux":
					platform_var = 'Linux'

			except:
				platform_var = None
				pass
			if platform_var == None:
				json_result_test = xbmc.executeJSONRPC('{"jsonrpc": "2.0","method": "System.EjectOpticalDrive","params": {},"id": "1"}')
			else:
				os.system('sudo mount -a')
				#os.system('sudo umount /dev/sr0')
				#os.system('sudo eject /dev/sr0')
				os.system('sudo eject -T /dev/sr0')
			indexes2 = xbmcgui.Dialog().yesno('Drive Tray', 'Insert Drive Tray', 'No', 'Yes') 
			if indexes2 == True:
				if platform_var == None:
					json_result_test = xbmc.executeJSONRPC('{"jsonrpc": "2.0","method": "System.EjectOpticalDrive","params": {},"id": "1"}')
				else:
					os.system('sudo eject -T /dev/sr0')
					os.system('sudo mount -a')
			Utils.hide_busy()
			return

		elif info == 'play_test_call_pop_stack':
			log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			return wm.pop_stack()

		elif info == 'play_test_pop_stack_new':
			reopen_play_fail = xbmcaddon.Addon(addon_ID()).getSetting('reopen_play_fail')
			xbmcgui.Window(10000).setProperty('diamond_info_started', 'True')
			if reopen_play_fail == 'false':
				return
			xbmc.log(str('start...')+'play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
			time_start = time.time()
			time_end = time_start + 145
			tmdb_plugin_flag = False
			tmdb_helper_finished = 0
			plugin_finished = 0
			plugin_name = 'not.a.plugin'
			reset_flag = False
			pop_flag = False
			old_line = ''
			line = ''
			while time.time() < time_end:

				if line == '':
					line = follow2()
					full_line = line
				else:
					old_line = full_line
					line = follow2()
					full_line = line
					line = line.replace(old_line,'')


				if tmdb_helper_finished != 0 and time.time() > tmdb_helper_finished +1.5 and plugin_name == 'not.a.plugin':
					xbmc.log('NO_ITEM'+'__play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
					reset_flag = True
					pop_flag = True

				if 'VideoPlayerVideo::OpenStream' in str(line) or 'diamond_info_started===>diamond_info_started' in str(line) or 'Creating InputStream' in str(line) or 'onPlayBackStarted===>___OPEN_INFO' in str(line):
					xbmc.log('PLAYBACK_STARTED'+'__play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
					reset_flag = True
					pop_flag = False
				if plugin_finished != 0 and time.time() > plugin_finished +1.5:
					xbmc.log('NO_ITEM'+'__play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
					pop_flag = True
					reset_flag = True
				if 'The following content is not available on this app' in str(line) or '.YouTubeException:' in str(line):
					xbmc.log('Youtube_playback_failed'+'__play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
					reset_flag = True
					pop_flag = True
				if 'Playlist Player: skipping unplayable item:' in str(line):
					xbmc.log('Video_playback_failed'+'__play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
					pop_flag = True
					reset_flag = True

				if old_line == line and reset_flag == False:
					xbmc.sleep(50)
					continue
				xbmc.sleep(50)

				if tmdb_helper_finished == 0 and 'TMDbHelper - Done!' in str(line):
					pop_flag = False
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
					xbmc.log('tmdb_helper_started'+'__play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
				if 'lib.player - playing path with PlayMedia' in str(line):
					tmdb_plugin_flag = True
				elif tmdb_plugin_flag == True:
					plugin_name = line.split('plugin://')[1].split('/')[0]
					xbmc.log(plugin_name+'__play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
					tmdb_plugin_flag = False
					tmdb_helper_finished = 0
				if tmdb_helper_finished == 0 and 'DestroyWindow' in str(line):
					xbmc.log('tmdb_helper_finished'+'__play_test_pop_stack1===>OPENINFO', level=xbmc.LOGINFO)
					tmdb_helper_finished = time.time()
				if tmdb_helper_finished != 0 and plugin_finished == 0 and 'DestroyWindow' in str(line):
					xbmc.log(str('%s_finished' % plugin_name)+'__play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
					plugin_finished = time.time()
					plugin_name = 'not.a.plugin'
					tmdb_helper_finished = 0
				if tmdb_helper_finished == 0 and 'script successfully run' in str(line) and 'plugin.video.themoviedb.helper' in str(line):
					xbmc.log('tmdb_helper_finished'+'__play_test_pop_stack1===>OPENINFO', level=xbmc.LOGINFO)
					tmdb_helper_finished = time.time()
				if ('script aborted' in str(line) or 'script successfully run' in str(line)) and plugin_name in str(line) and not 'plugin.video.themoviedb.helper/plugin.py): script successfully run' in str(line):
					xbmc.log(str('%s_finished' % plugin_name)+'__play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
					plugin_finished = time.time()
					plugin_name = 'not.a.plugin'
					tmdb_helper_finished = 0
				if 'Playlist Player: skipping unplayable item:' in str(line):
					xbmc.log('Video_playback_failed'+'__play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
					pop_flag = True
					reset_flag = True
				if reset_flag == True:
					tmdb_plugin_flag = False
					tmdb_helper_finished = 0
					plugin_finished = 0
					plugin_name = 'not.a.plugin'
					if pop_flag == True:
						#xbmc.log('pop_the_stack!!!_return'+'__play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
						log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
						return wm.pop_stack()
						pop_flag = False
					reset_flag = False
					pop_flag = False
					xbmc.log('return'+'__play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
					return


		elif info == 'play_test_pop_stack':
			import json
			tmdbhelper_flag = False
			reopen_play_fail = xbmcaddon.Addon(addon_ID()).getSetting('reopen_play_fail')
			xbmcgui.Window(10000).setProperty('diamond_info_started', 'True')
			xbmc.sleep(3000)
			if reopen_play_fail == 'false':
				return
			xbmc.log(str('start...')+'play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
			home_count = 0
			for i in range(1, int((145 * 1000)/1000)):
				window_id = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
				window_id = json.loads(window_id)
				xbmc.sleep(1000)
				window_id2 = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
				window_id2 = json.loads(window_id2)
				#xbmc.log(str(window_id)+str(i)+'===>OPENINFO', level=xbmc.LOGINFO)
				if (window_id['result']['currentwindow']['label'].lower() in ['home','notification'] or window_id['result']['currentwindow']['id'] in [10000,10107]) and window_id2 == window_id:
					home_count = home_count + 1
					if home_count > 10:
						xbmc.log(str('\n\n\n\nwm.pop_stack()......')+'1play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
						log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
						#xbmc.executebuiltin('RunPlugin(plugin://%s/?info=play_test_call_pop_stack)' % addon_ID())
						return wm.pop_stack()
				if (window_id['result']['currentwindow']['label'].lower() in ['busydialognocancel'] or window_id['result']['currentwindow']['id'] in [10160]) and window_id2 == window_id:
					error_flag = get_log_error_flag(mode='Exception')
					if error_flag:
						xbmc.executebuiltin('Dialog.Close(all,true)')
						xbmc.log(str('\n\n\n\nm.pop_stack()......')+'2play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
						#xbmc.executebuiltin('RunPlugin(plugin://%s/?info=play_test_call_pop_stack)' % addon_ID())
						log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
						return wm.pop_stack()
				if xbmc.Player().isPlaying() or xbmc.getCondVisibility('Window.IsActive(12005)'):
					xbmc.log(str('\n\n\n\nPlayback_Success.......')+'play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
					return

				if tmdbhelper_flag == True and window_id != window_id2:
					xbmc.sleep(500)
					error_flag = get_log_error_flag(mode='tmdb_helper')
					if error_flag:
						xbmc.log(str('\n\n\n\ntmdb_helper_error_flag.......SLEEP......')+'play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
						xbmc.sleep(7500)

				if window_id['result']['currentwindow']['label'] == 'Select dialog' or window_id['result']['currentwindow']['id'] == 12000:
					if tmdbhelper_flag == False:
						Utils.hide_busy()
					tmdbhelper_flag = True
				elif tmdbhelper_flag and ( xbmc.Player().isPlaying() or ( window_id['result']['currentwindow']['label'].lower() == 'fullscreenvideo' or window_id['result']['currentwindow']['id'] == 12005 and window_id2 == window_id and i > 4 ) ):
					xbmc.log(str('\n\n\n\nPlayback_Success.......')+'play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
					return
				elif tmdbhelper_flag and (window_id['result']['currentwindow']['label'].lower() in ['home','notification'] or window_id['result']['currentwindow']['id'] in [10000,10107]) and window_id2 == window_id and i > 4:
					#xbmc.log(str(window_id)+str(i)+'===>OPENINFO', level=xbmc.LOGINFO)
					if xbmc.Player().isPlaying():
						xbmc.log(str('Playback_Success')+'play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
						return
					else:
						error_flag = get_log_error_flag(mode='seren')
						if error_flag == False:
							xbmc.log(str('\n\n\n\nwm.pop_stack()......')+'3play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
							log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
							#xbmc.executebuiltin('RunPlugin(plugin://%s/?info=play_test_call_pop_stack)' % addon_ID())
							return wm.pop_stack()
						elif error_flag == True:
							xbmc.log(str('\n\n\n\nseren_error_flag.......SLEEP......')+'play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
							xbmc.sleep(2500)
			xbmc.log(str('return......')+'play_test_pop_stack===>OPENINFO', level=xbmc.LOGINFO)
			return


		elif info == 'test_route':
			from resources.lib.con_man_fix import list_and_select_wifi
			list_and_select_wifi()
			Utils.hide_busy()
			return
			#from resources.lib.library import trakt_collection_movies
			#movies = trakt_collection_movies()
			#for i in movies:
			#	xbmc.log(str(i)+'===>OPEN_INFO', level=xbmc.LOGINFO)
			#xbmc.log(str(movies)+'===>OPEN_INFO', level=xbmc.LOGINFO)
			from resources.lib.library import trakt_uncollected_watched_movies
			#from resources.lib.library import trakt_unwatched_collection_movies
			movies = trakt_uncollected_watched_movies()
			xbmc.log(str(movies)+'===>OPEN_INFO', level=xbmc.LOGINFO)
			Utils.hide_busy()
			return
			#from resources.lib.TheMovieDB import get_trakt_userlists
			#from resources.lib.library import trak_auth
			#trakt_data = get_trakt_userlists()
			#import json
			#import requests
			#headers = trak_auth()
			##xbmc.log(str(trakt_data)+'===>OPEN_INFO', level=xbmc.LOGINFO)

			#for i in trakt_data['trakt_list']:
			#	list_slug = i['list_slug']
			#	user_id = i['user_id']
			#	if 'watchlist' in str(i):
			#		continue
			#	url = 'https://api.trakt.tv/users/%s/lists/%s/items' % (user_id,list_slug)
			#	response2 = requests.get(url, headers=headers)
			#	if not 'Response [200]' in str(response2):
			#		xbmc.log(str(url)+'===>OPEN_INFO', level=xbmc.LOGINFO)
			#		xbmc.log(str(response2)+'===>OPEN_INFO', level=xbmc.LOGINFO)
			#		xbmc.log(str(i)+'===>OPEN_INFO', level=xbmc.LOGINFO)
			#		url = 'https://api.trakt.tv/users/%s/lists/%s' % (user_id,list_slug)
			#		response2 = requests.get(url, headers=headers)
			#		xbmc.log(str(response2)+'===>OPEN_INFO', level=xbmc.LOGINFO)
			#		url = 'https://api.trakt.tv/users/%s/lists/%s/like' % (user_id,list_slug)
			#		response2 = requests.delete(url, headers=headers)
			#		xbmc.log(str(response2)+'===>OPEN_INFO', level=xbmc.LOGINFO)
			#		url = 'https://api.trakt.tv/lists/%s/like' % (list_slug)
			#		response2 = requests.delete(url, headers=headers)
			#		xbmc.log(str(response2)+'===>OPEN_INFO', level=xbmc.LOGINFO)
			#Utils.hide_busy()
			#return

			xbmc.log(str('test_route')+'===>OPEN_INFO', level=xbmc.LOGINFO)
			Utils.hide_busy()
			from resources.lib.library import trakt_uncollected_watched_movies
			search_str = trakt_uncollected_watched_movies()
			#xbmc.log(str(search_str)+'===>OPEN_INFO', level=xbmc.LOGINFO)
			output = []
			for i in search_str:
				try: output.append(str(i['movie']['title'])+'__'+str(i['movie']['year']))
				except: pass
			for i in sorted(output):
				xbmc.log(str(i)+'===>OPEN_INFO', level=xbmc.LOGINFO)

		elif info == 'setup_trakt_watched':
			Utils.show_busy()
			from resources.lib import library
			library.trakt_watched_tv_shows_full()
			xbmc.log(str('trakt_watched_tv_shows_full')+'===>OPEN_INFO', level=xbmc.LOGINFO)
			library.trakt_watched_movies_full()
			xbmc.log(str('trakt_watched_movies_full')+'===>OPEN_INFO', level=xbmc.LOGINFO)
			Utils.hide_busy()

		elif info == 'setup_players':
			Utils.show_busy()
			from pathlib import Path
			RD_player = xbmcaddon.Addon(addon_ID()).getSetting('RD_player')
			RD_bluray_player = xbmcaddon.Addon(addon_ID()).getSetting('RD_bluray_player')
			RD_bluray_player2 = xbmcaddon.Addon(addon_ID()).getSetting('RD_bluray_player2')
			from resources.lib.library import tmdb_settings_path
			player_path = str(Path(str(tmdb_settings_path()).replace('settings.xml','players')))
			from resources.lib.library import main_file_path
			rd_player_path_in = xbmcvfs.translatePath(main_file_path() + 'direct.diamond_player.json')
			rd_player_path_in2 = xbmcvfs.translatePath(main_file_path() + 'direct.diamond_player_torr_scrape.json')
			rd_player_path_in3 = xbmcvfs.translatePath(main_file_path() + 'direct.diamond_player_torr_scrape_dialog.json')
			rd_bluray_player_path_in = xbmcvfs.translatePath(main_file_path() + 'direct.diamond_player_bluray.json')
			rd_bluray_player2_path_in = xbmcvfs.translatePath(main_file_path() + 'direct.diamond_player_bluray2.json')
			
			rd_player_path_out = xbmcvfs.translatePath(player_path + '/direct.diamond_player.json')
			rd_player_path_out2 = xbmcvfs.translatePath(player_path + '/direct.diamond_player_torr_scrape.json')
			rd_player_path_out3 = xbmcvfs.translatePath(player_path + '/direct.diamond_player_torr_scrape_dialog.json')
			rd_bluray_player_path_out = xbmcvfs.translatePath(player_path + '/direct.diamond_player_bluray.json')
			rd_bluray_player2_path_out = xbmcvfs.translatePath(player_path + '/direct.diamond_player_bluray2.json')
			import shutil
			if not xbmcvfs.exists(rd_player_path_out) and RD_player == 'true':
				shutil.copyfile(rd_player_path_in, rd_player_path_out)
				xbmc.log(str({'rd_player_path_in': rd_player_path_in, 'rd_player_path_out': rd_player_path_out})+'===>OPENINFO', level=xbmc.LOGINFO)
			if xbmcvfs.exists(rd_player_path_out) and RD_player == 'true':
				shutil.copyfile(rd_player_path_in, rd_player_path_out)
				xbmc.log(str({'rd_player_path_in': rd_player_path_in, 'rd_player_path_out': rd_player_path_out})+'===>OPENINFO', level=xbmc.LOGINFO)
			if not xbmcvfs.exists(rd_player_path_out2) and RD_player == 'true':
				shutil.copyfile(rd_player_path_in2, rd_player_path_out2)
				xbmc.log(str({'rd_player_path_in': rd_player_path_in2, 'rd_player_path_out': rd_player_path_out2})+'===>OPENINFO', level=xbmc.LOGINFO)
			if xbmcvfs.exists(rd_player_path_out2) and RD_player == 'true':
				shutil.copyfile(rd_player_path_in2, rd_player_path_out2)
				xbmc.log(str({'rd_player_path_in': rd_player_path_in2, 'rd_player_path_out': rd_player_path_out2})+'===>OPENINFO', level=xbmc.LOGINFO)
			if not xbmcvfs.exists(rd_player_path_out3) and RD_player == 'true':
				shutil.copyfile(rd_player_path_in3, rd_player_path_out3)
				xbmc.log(str({'rd_player_path_in3': rd_player_path_in3, 'rd_player_path_out3': rd_player_path_out3})+'===>OPENINFO', level=xbmc.LOGINFO)
			if xbmcvfs.exists(rd_player_path_out3) and RD_player == 'true':
				shutil.copyfile(rd_player_path_in3, rd_player_path_out3)
				xbmc.log(str({'rd_player_path_in3': rd_player_path_in3, 'rd_player_path_out3': rd_player_path_out3})+'===>OPENINFO', level=xbmc.LOGINFO)

			if not xbmcvfs.exists(rd_bluray_player_path_out) and RD_bluray_player == 'true':
				shutil.copyfile(rd_bluray_player_path_in, rd_bluray_player_path_out)
				xbmc.log(str({'rd_bluray_player_path_in': rd_bluray_player_path_in, 'rd_bluray_player_path_out': rd_bluray_player_path_out})+'===>OPENINFO', level=xbmc.LOGINFO)
			if xbmcvfs.exists(rd_bluray_player_path_out) and RD_bluray_player == 'true':
				shutil.copyfile(rd_bluray_player_path_in, rd_bluray_player_path_out)
				xbmc.log(str({'rd_bluray_player_path_in': rd_bluray_player_path_in, 'rd_bluray_player_path_out': rd_bluray_player_path_out})+'===>OPENINFO', level=xbmc.LOGINFO)
			if not xbmcvfs.exists(rd_bluray_player2_path_out) and RD_bluray_player2 == 'true':
				shutil.copyfile(rd_bluray_player2_path_in, rd_bluray_player2_path_out)
				xbmc.log(str({'rd_bluray_player2_path_in': rd_bluray_player2_path_in, 'rd_bluray_player2_path_out': rd_bluray_player2_path_out})+'player_path===>OPENINFO', level=xbmc.LOGINFO)
			if xbmcvfs.exists(rd_bluray_player2_path_out) and RD_bluray_player2 == 'true':
				shutil.copyfile(rd_bluray_player2_path_in, rd_bluray_player2_path_out)
				xbmc.log(str({'rd_bluray_player2_path_in': rd_bluray_player2_path_in, 'rd_bluray_player2_path_out': rd_bluray_player2_path_out})+'player_path===>OPENINFO', level=xbmc.LOGINFO)
			Utils.hide_busy()

		elif info == 'open_settings':
			xbmc.executebuiltin('Addon.OpenSettings(%s)' % addon_ID())
			Utils.hide_busy()

		elif info == 'setup_fen_light_players':
			Utils.show_busy()
			from pathlib import Path

			from resources.lib.library import tmdb_settings_path
			player_path = str(Path(str(tmdb_settings_path()).replace('settings.xml','players')))
			from resources.lib.library import main_file_path
		
			fen_player_1_in = os.path.join(main_file_path(), 'resources','skins','direct.fenlight.json')
			fen_player_2_in = os.path.join(main_file_path(), 'resources','skins','direct.fenlight.select.json')
			fen_player_1_out = os.path.join(player_path, 'direct.fenlight.json')
			fen_player_2_out = os.path.join(player_path, 'direct.fenlight.select.json')

			import shutil
			if not xbmcvfs.exists(fen_player_1_out):
				shutil.copyfile(fen_player_1_in, fen_player_1_out)
				xbmc.log(str({'fen_player_1_in': fen_player_1_out, 'fen_player_1_out': fen_player_1_out})+'===>OPENINFO', level=xbmc.LOGINFO)
			if not xbmcvfs.exists(fen_player_2_out):
				shutil.copyfile(fen_player_2_in, fen_player_2_out)
				xbmc.log(str({'fen_player_2_in': fen_player_2_out, 'fen_player_2_out': fen_player_2_out})+'===>OPENINFO', level=xbmc.LOGINFO)

			Utils.hide_busy()

		elif info == 'install_latest_fen_light':
			Utils.show_busy()
			#import os
			import requests
			import json

			GITHUB_URL = 'https://github.com/Tikipeter/repository.tikipeter.test/raw/main/zips/plugin.video.fenlight/'

			result = requests.get(GITHUB_URL).json()
			for i in result['payload']['tree']['items']:
				path = i['path']

			latest_zip = 'https://github.com/Tikipeter/repository.tikipeter.test/raw/main/zips/plugin.video.fenlight/' + path.split('/')[-1]

			payload = {
					"jsonrpc": "2.0",
					"method": "Addons.InstallAddon",
					"params": {"addonid": "plugin.video.fenlight", "url": latest_zip},
					"id": 1
			}
			xbmc.log(str(json.dumps(payload))+'===>OPENINFO', level=xbmc.LOGINFO)
			response = xbmc.executeJSONRPC(json.dumps(payload))
			Utils.hide_busy()


		elif info == 'setup_sources':
			from resources.lib.library import basedir_tv_path
			from resources.lib.library import basedir_movies_path
			from resources.lib.library import library_source_exists_tv
			from resources.lib.library import setup_library_tv
			from resources.lib.library import library_source_exists_movies
			from resources.lib.library import setup_library_movies
			from resources.lib.library import icon_path
			library_tv_sync = str(xbmcaddon.Addon(addon_ID()).getSetting('library_tv_sync'))
			library_movies_sync = str(xbmcaddon.Addon(addon_ID()).getSetting('library_movies_sync'))
			library_folder = str(basedir_tv_path())
			if not xbmcvfs.exists(library_folder):
				xbmcvfs.mkdir(library_folder)
			library_folder = str(basedir_movies_path())
			if not xbmcvfs.exists(library_folder):
				xbmcvfs.mkdir(library_folder)
			if not library_source_exists_tv():
				response = setup_library_tv()
			if not library_source_exists_movies():
				response = setup_library_movies()
			xbmcgui.Dialog().notification(heading='Setup Sources', message='Sources Setup, Please Reboot to finish setup.', icon=icon_path(),time=2000,sound=False)
			Utils.hide_busy()

		elif info == 'setup_xml_filenames':
			from resources.lib.library import setup_xml_filenames
			setup_xml_filenames()
			xbmcgui.Dialog().notification(heading='Setup XML Names', message='XML files renamed to match = '+ addon_ID(), icon=icon_path(),time=2000,sound=False)
			return

		elif info == 'auto_library':
			auto_library()

		elif info == 'trakt_watched' or info == 'trakt_coll' or info == 'trakt_list' or info == 'trakt_trend' or info == 'trakt_popular' or info == 'trakt_progress' or info == 'trakt_unwatched':
			#kodi-send --action='RunPlugin(plugin://'+str(addon_ID())+'/?info=trakt_watched&trakt_type=movie&script=True)'
			#kodi-send --action='RunPlugin(plugin://'+str(addon_ID())+'/?info=trakt_watched&trakt_type=tv&script=True)'
			#kodi-send --action='RunPlugin(plugin://'+str(addon_ID())+'/?info=trakt_coll&trakt_type=movie&script=True)'
			#kodi-send --action='RunPlugin(plugin://'+str(addon_ID())+'/?info=trakt_coll&trakt_type=tv&script=True)'
			trakt_type = str(params['trakt_type'])
			limit = params.get('limit', 0)
			Utils.show_busy()
			try: trakt_token = xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('trakt_token')
			except: trakt_token = None
			if not trakt_token:
				Utils.hide_busy()
				return
			try:
				trakt_script = str(params['script'])
			except:
				trakt_script = 'True'
			if trakt_script == 'False' and (info == 'trakt_watched' or info == 'trakt_coll' or info == 'trakt_trend' or info == 'trakt_popular'  or info == 'trakt_progress' or info == 'trakt_unwatched'):
				from resources.lib import TheMovieDB
				return TheMovieDB.get_trakt(trakt_type=trakt_type,info=info,limit=limit)
			else:
				if info == 'trakt_watched' and trakt_type == 'movie':
					from resources.lib.library import trakt_watched_movies
					movies = trakt_watched_movies()
					trakt_label = 'Trakt Watched Movies'
				elif info == 'trakt_watched' and trakt_type == 'tv':
					from resources.lib.library import trakt_watched_tv_shows
					movies = trakt_watched_tv_shows()
					trakt_label = 'Trakt Watched Shows'

				elif info == 'trakt_unwatched' and trakt_type == 'tv':
					from resources.lib.library import trakt_unwatched_tv_shows
					movies = trakt_unwatched_tv_shows()
					trakt_label = 'Trakt Unwatched Shows'

				elif info == 'trakt_coll' and trakt_type == 'movie':
					from resources.lib.library import trakt_collection_movies
					movies = trakt_collection_movies()
					trakt_label = 'Trakt Collection Movies'
				elif info == 'trakt_coll' and trakt_type == 'tv':
					from resources.lib.library import trakt_collection_shows
					movies = trakt_collection_shows()
					trakt_label = 'Trakt Collection Shows'

				elif info == 'trakt_trend' and trakt_type == 'tv':
					from resources.lib.library import trakt_trending_shows
					movies = trakt_trending_shows()
					trakt_label = 'Trakt Trending Shows'
				elif info == 'trakt_trend' and trakt_type == 'movie':
					from resources.lib.library import trakt_trending_movies
					movies = trakt_trending_movies()
					trakt_label = 'Trakt Trending Movies'

				elif info == 'trakt_popular' and trakt_type == 'tv':
					from resources.lib.library import trakt_popular_shows
					movies = trakt_popular_shows()
					trakt_label = 'Trakt Trending Shows'
				elif info == 'trakt_popular' and trakt_type == 'movie':
					from resources.lib.library import trakt_popular_movies
					movies = trakt_popular_movies()
					trakt_label = 'Trakt Trending Movies'

				elif info == 'trakt_popular' and trakt_type == 'tv':
					from resources.lib.library import trakt_watched_tv_shows_progress
					movies = trakt_watched_tv_shows_progress()
					trakt_label = 'Trakt Shows Progress'
				elif info == 'trakt_list':
					from resources.lib.library import trakt_lists
					from resources.lib.TheMovieDB import get_trakt_lists
					trakt_type = str(params['trakt_type'])
					trakt_label = str(params['trakt_list_name'])
					trakt_user_id = str(params['user_id'])
					takt_list_slug = str(params['list_slug'])
					trakt_sort_by = str(params['trakt_sort_by'])
					trakt_sort_order = str(params['trakt_sort_order'])
					if trakt_script == 'False':
						return get_trakt_lists(list_name=trakt_label,user_id=trakt_user_id,list_slug=takt_list_slug,sort_by=trakt_sort_by,sort_order=trakt_sort_order,limit=limit)
					movies = trakt_lists(list_name=trakt_label,user_id=trakt_user_id,list_slug=takt_list_slug,sort_by=trakt_sort_by,sort_order=trakt_sort_order,limit=limit)
				if keep_stack == None or keep_stack == False:
					wm.window_stack_empty()
				return wm.open_video_list(mode='trakt', listitems=[], search_str=movies, media_type=trakt_type, filter_label=trakt_label)

		elif info == 'imdb_list':
			limit = params.get('limit', 0)
			list_name = str(params['list_name'])
			try:
				list_script = str(params['script'])
			except:
				list_script = 'True'
			list_str = str(params['list'])
			Utils.show_busy()
			if 'ls' in str(list_str):
				#from resources.lib.TheMovieDB import get_imdb_list
				from resources.lib.TheMovieDB import get_imdb_list_ids
				from resources.lib.TheMovieDB import get_imdb_watchlist_items
				movies = get_imdb_list_ids(list_str,limit=limit)
				if list_script == 'False':
					return get_imdb_watchlist_items(movies=movies,limit=limit)
				#from imdb import IMDb, IMDbError
				#ia = IMDb()
				#movies = ia.get_movie_list(list_str)
				wm.window_stack_empty()
				wm.open_video_list(mode='imdb2', listitems=[], search_str=movies, filter_label=list_name)
			elif 'ur' in str(list_str):
				from resources.lib.TheMovieDB import get_imdb_watchlist_ids
				movies = get_imdb_watchlist_ids(list_str,limit=limit)
				if list_script == 'False':
					from resources.lib.TheMovieDB import get_imdb_watchlist_items
					return get_imdb_watchlist_items(movies=movies,limit=limit)
				wm.window_stack_empty()
				wm.open_video_list(mode='imdb2', listitems=[], search_str=movies, filter_label=list_name)
			return

		elif info == 'search_string':
			search_str = params['str']
			wm.window_stack_empty()
			return wm.open_video_list(search_str=search_str, mode='search')

		elif info == 'search_person':
			from resources.lib.TheMovieDB import get_person_info
			from resources.lib.TheMovieDB import get_person
			search_str = params['person']
			if params.get('person'):
				person = get_person_info(person_label=params['person'])
				if person and person.get('id'):
					movies = get_person(person['id'])
					newlist = sorted(movies, key=lambda k: k['Popularity'], reverse=True)
					movies = {}
					movies['cast_crew'] = []
					movies['person'] = params['person']
					for i in newlist:
						try:
							if str("'id': " + str(i['id'])) not in str(movies['cast_crew']) and i['poster'] != None:
								if str("'id': '" + str(i['id']) + "'") not in str(movies['cast_crew']):
									movies['cast_crew'].append(i)
						except KeyError:
							pass
					newlist = None
					wm.window_stack_empty()
					return wm.open_video_list(mode='person', search_str=movies, listitems=movies['cast_crew'])

		elif info == 'studio':
			from resources.lib import TheMovieDB
			if 'id' in params and params['id']:
				wm.window_stack_empty()
				return wm.open_video_list(media_type='tv', mode='filter', listitems=TheMovieDB.get_company_data(params['id']))
			elif 'studio' in params and params['studio']:
				company_data = TheMovieDB.search_company(params['studio'])
				if company_data:
					return TheMovieDB.get_company_data(company_data[0]['id'])

		elif info == 'set':
			from resources.lib import TheMovieDB
			from resources.lib import local_db
			if params.get('dbid') and 'show' not in str(params.get('type', '')):
				name = local_db.get_set_name_from_db(params['dbid'])
				if name:
					params['setid'] = TheMovieDB.get_set_id(name)
			if params.get('setid'):
				set_data, _ = TheMovieDB.get_set_movies(params['setid'])
				return set_data

		elif info == 'keywords':
			from resources.lib import TheMovieDB
			movie_id = params.get('id', False)
			if not movie_id:
				movie_id = TheMovieDB.get_movie_tmdb_id(imdb_id=params.get('imdb_id'), dbid=params.get('dbid'))
			if movie_id:
				return TheMovieDB.get_keywords(movie_id)

		elif info == 'directormovies':
			from resources.lib import TheMovieDB
			if params.get('director'):
				director_info = TheMovieDB.get_person_info(person_label=params['director'])
				if director_info and director_info.get('id'):
					movies = TheMovieDB.get_person_movies(director_info['id'])
					for item in movies:
						del item['credit_id']
					return Utils.merge_dict_lists(movies, key='department')

		elif info == 'writermovies':
			from resources.lib import TheMovieDB
			if params.get('writer') and not params['writer'].split(' / ')[0] == params.get('director', '').split(' / ')[0]:
				writer_info = TheMovieDB.get_person_info(person_label=params['writer'])
				if writer_info and writer_info.get('id'):
					movies = TheMovieDB.get_person_movies(writer_info['id'])
					for item in movies:
						del item['credit_id']                    
					return Utils.merge_dict_lists(movies, key='department')

		elif info == 'afteradd':
			return Utils.after_add(params.get('type'))

		elif info == 'moviedbbrowser':
			if xbmcgui.Window(10000).getProperty('infodialogs.active'):
				return None
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			search_str = params.get('id', '')
			if not search_str and params.get('search'):
				result = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
				if result and result > -1:
					search_str = result
				else:
					xbmcgui.Window(10000).clearProperty('infodialogs.active')
					return None
			xbmcgui.Window(10000).clearProperty('infodialogs.active')
			wm.window_stack_empty()
			return wm.open_video_list(search_str=search_str, mode='search')

		elif info == 'playmovie':
			resolve_url(params.get('handle'))
			Utils.get_kodi_json(method='Player.Open', params='{"item": {"movieid": %s}, "options": {"resume": true}}' % params.get('dbid'))

		elif info == 'playepisode':
			resolve_url(params.get('handle'))
			Utils.get_kodi_json(method='Player.Open', params='{"item": {"episodeid": %s}, "options": {"resume": true}}' % params.get('dbid'))

		elif info == 'playmusicvideo':
			resolve_url(params.get('handle'))
			Utils.get_kodi_json(method='Player.Open', params='{"item": {"musicvideoid": %s}}' % params.get('dbid'))

		elif info == 'playalbum':
			resolve_url(params.get('handle'))
			Utils.get_kodi_json(method='Player.Open', params='{"item": {"albumid": %s}}' % params.get('dbid'))

		elif info == 'playsong':
			resolve_url(params.get('handle'))
			Utils.get_kodi_json(method='Player.Open', params='{"item": {"songid": %s}}' % params.get('dbid'))

		elif info == 'diamondinfodialog' or info == 'extendedinfodialog' or info == str(addon_ID_short()) + 'dialog':
			resolve_url(params.get('handle'))
			if xbmc.getCondVisibility('System.HasActiveModalDialog | System.HasModalDialog'):
				container_id = ''
			else:
				container_id = xbmc.getInfoLabel('Container(%s).ListItem.label' % xbmc.getInfoLabel('System.CurrentControlID'))
			dbid = xbmc.getInfoLabel('%sListItem.DBID' % container_id)
			if not dbid:
				dbid = xbmc.getInfoLabel('%sListItem.Property(dbid)' % container_id)
			db_type = xbmc.getInfoLabel('%sListItem.DBType' % container_id)
			if db_type == 'movie':
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info='+str(addon_ID_short())+',dbid=%s,id=%s,imdb_id=%s,name=%s)' % (dbid, xbmc.getInfoLabel('ListItem.Property(id)'), xbmc.getInfoLabel('ListItem.IMDBNumber'), xbmc.getInfoLabel('ListItem.Title')))
			elif db_type == 'tvshow':
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=extendedtvinfo,dbid=%s,id=%s,tvdb_id=%s,name=%s)' % (dbid, xbmc.getInfoLabel('ListItem.Property(id)'), xbmc.getInfoLabel('ListItem.Property(tvdb_id)'), xbmc.getInfoLabel('ListItem.Title')))
			elif db_type == 'season':
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=seasoninfo,tvshow=%s,season=%s)' % (xbmc.getInfoLabel('ListItem.TVShowTitle'), xbmc.getInfoLabel('ListItem.Season')))
			elif db_type == 'episode':
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=extendedepisodeinfo,tvshow=%s,season=%s,episode=%s)' % (xbmc.getInfoLabel('ListItem.TVShowTitle'), xbmc.getInfoLabel('ListItem.Season'), xbmc.getInfoLabel('ListItem.Episode')))
			elif db_type in ['actor', 'director']:
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=extendedactorinfo,name=%s)' % xbmc.getInfoLabel('ListItem.Label'))
			else:
				Utils.notify('Error', 'Could not find valid content type')

		elif info == 'diamondinfo' or info == 'extendedinfo' or info == str(addon_ID_short()):
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			if not params.get('id'):
				from resources.lib.TheMovieDB import get_movie_info
				#response = get_tmdb_data('search/%s?query=%s&language=en-US&include_adult=%s&' % ('movie', params.get('name'), xbmcaddon.Addon().getSetting('include_adults')), 30)
				#params['id'] = response['results'][0]['id']
				if not params.get('id') and not params.get('dbid') and (not params.get('imdb_id') or not 'tt' in str(params.get('imdb_id'))):
					movie = get_movie_info(movie_label=params.get('name'), year=params.get('year'))
					if movie and movie.get('id'):
						params['id'] = movie.get('id')
					elif not movie:
						xbmcgui.Window(10000).clearProperty('infodialogs.active')
						Utils.hide_busy()
						return
			wm.window_stack_empty()
			wm.open_movie_info(movie_id=params.get('id'), dbid=params.get('dbid'), imdb_id=params.get('imdb_id'), name=params.get('name'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'extendedactorinfo':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			wm.window_stack_empty()
			wm.open_actor_info(actor_id=params.get('id'), name=params.get('name'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'extendedtvinfo':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			if not params.get('id'):
				from resources.lib.TheMovieDB import get_tvshow_info
				#response = get_tmdb_data('search/%s?query=%s&language=en-US&include_adult=%s&' % ('tv', params.get('name'), xbmcaddon.Addon().getSetting('include_adults')), 30)
				#params['id'] = response['results'][0]['id']
				if not params.get('id') and not params.get('dbid') and not params.get('tvdb_id') and (not params.get('imdb_id') or not 'tt' in str(params.get('imdb_id'))):
					tvshow = get_tvshow_info(tvshow_label=params.get('name'), year=params.get('year'))
					if tvshow and tvshow.get('id'):
						params['id'] = tvshow.get('id')
					elif not tvshow:
						xbmcgui.Window(10000).clearProperty('infodialogs.active')
						Utils.hide_busy()
						return
			wm.window_stack_empty()
			wm.open_tvshow_info(tmdb_id=params.get('id'), tvdb_id=params.get('tvdb_id'), dbid=params.get('dbid'), imdb_id=params.get('imdb_id'), name=params.get('name'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'seasoninfo':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			wm.window_stack_empty()
			wm.open_season_info(tvshow=params.get('tvshow'), tvshow_id=params.get('tvshow_id'), dbid=params.get('dbid'), season=params.get('season'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'extendedepisodeinfo':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			wm.window_stack_empty()
			wm.open_episode_info(tvshow=params.get('tvshow'), tvshow_id=params.get('tvshow_id'), tvdb_id=params.get('tvdb_id'), dbid=params.get('dbid'), season=params.get('season'), episode=params.get('episode'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'albuminfo':
			resolve_url(params.get('handle'))
			if params.get('id', ''):
				album_details = get_album_details(params.get('id', ''))
				Utils.pass_dict_to_skin(album_details, params.get('prefix', ''))

		elif info == 'artistdetails':
			resolve_url(params.get('handle'))
			artist_details = get_artist_details(params['artistname'])
			Utils.pass_dict_to_skin(artist_details, params.get('prefix', ''))

		elif info == 'setfocus':
			resolve_url(params.get('handle'))
			xbmc.executebuiltin('SetFocus(22222)')

		elif info == 'slideshow':
			resolve_url(params.get('handle'))
			window_id = xbmcgui.getCurrentwindow_id()
			window = xbmcgui.Window(window_id)
			itemlist = window.getFocus()
			num_items = itemlist.getSelectedPosition()
			for i in range(0, num_items):
				Utils.notify(item.getProperty('Image'))

		elif info == 'action':
			resolve_url(params.get('handle'))
			for builtin in params.get('id', '').split('$$'):
				xbmc.executebuiltin(builtin)

		elif info == 'youtubevideo':
			from resources.lib.VideoPlayer import PLAYER
			resolve_url(params.get('handle'))
			xbmc.executebuiltin('Dialog.Close(all,true)')
			PLAYER.playtube(params.get('id', ''))

		elif info == 'playtrailer':
			from resources.lib import TheMovieDB
			from resources.lib import local_db
			resolve_url(params.get('handle'))
			if params.get('id'):
				movie_id = params['id']
			elif int(params.get('dbid', -1)) > 0:
				movie_id = local_db.get_imdb_id_from_db(media_type='movie', dbid=params['dbid'])
			elif params.get('imdb_id'):
				movie_id = TheMovieDB.get_movie_tmdb_id(params['imdb_id'])
			else:
				movie_id = ''
			if movie_id:
				TheMovieDB.play_movie_trailer_fullscreen(movie_id)

		elif info == 'playtvtrailer' or info == 'tvtrailer':
			from resources.lib import local_db
			from resources.lib import TheMovieDB
			resolve_url(params.get('handle'))
			if params.get('id'):
				tvshow_id = params['id']
			elif int(params.get('dbid', -1)) > 0:
				tvshow_id = local_db.get_imdb_id_from_db(media_type='show', dbid=params['dbid'])
			elif params.get('tvdb_id'):
				tvshow_id = TheMovieDB.get_show_tmdb_id(params['tvdb_id'])
			else:
				tvshow_id = ''
			if tvshow_id:

				TheMovieDB.play_tv_trailer_fullscreen(tvshow_id)

		elif info == 'prescrape_seren':
			from diamond_rd_player import prescrape_seren
			tmdb = params.get('tmdb_id')
			show_season = params.get('show_season')
			show_episode = params.get('show_episode')
			deete = prescrape_seren(tmdb=tmdb, season=show_season, episode=show_episode)

		elif info == 'a4kwrapper_player':
		#kodi-send --action="RunScript(script.extendedinfo,info=diamond_rd_player,type=tv,show_title=Star Trek: Enterprise,show_season=4,show_episode=20,tmdb=314)"
		#kodi-send --action="RunScript(script.extendedinfo,info=diamond_rd_player,type=movie,movie_year=,movie_title=Elf,tmdb=)"
			if params.get('type') == 'tv':
				from a4kwrapper_player import next_ep_play
				show_title = params.get('show_title')
				show_season = params.get('show_season')
				show_episode = params.get('show_episode')
				tmdb = params.get('tmdb')
				next_ep_play(show_title, show_season, show_episode, tmdb)
			elif params.get('type') == 'movie':
				from a4kwrapper_player import next_ep_play_movie
				movie_year = params.get('movie_year')
				movie_title = params.get('movie_title')
				tmdb = params.get('tmdb')
				next_ep_play_movie(movie_year, movie_title, tmdb)

		elif info == 'diamond_rd_player':
		#kodi-send --action="RunScript(script.extendedinfo,info=diamond_rd_player,type=tv,show_title=Star Trek: Enterprise,show_season=4,show_episode=20,tmdb=314)"
		#kodi-send --action="RunScript(script.extendedinfo,info=diamond_rd_player,type=movie,movie_year=,movie_title=Elf,tmdb=)"
			if params.get('type') == 'tv':
				from diamond_rd_player import next_ep_play
				show_title = params.get('show_title')
				show_season = params.get('show_season')
				show_episode = params.get('show_episode')
				tmdb = params.get('tmdb')
				next_ep_play(show_title, show_season, show_episode, tmdb)
			elif params.get('type') == 'movie':
				from diamond_rd_player import next_ep_play_movie
				movie_year = params.get('movie_year')
				movie_title = params.get('movie_title')
				tmdb = params.get('tmdb')
				next_ep_play_movie(movie_year, movie_title, tmdb)

		elif info == 'diamond_bluray_player':
				from diamond_bluray_player import next_ep_play_movie
				movie_year = params.get('movie_year')
				movie_title = params.get('movie_title')
				tmdb = params.get('tmdb')
				menu = params.get('menu')
				if menu == 'True':
					menu = True
				next_ep_play_movie(movie_year, movie_title, tmdb, menu)


		elif info == 'string':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			dialog = xbmcgui.Dialog()
			if params.get('type', '') == 'movie':
				moviesearch = dialog.input('MovieSearch')
				xbmc.executebuiltin('Skin.SetString(MovieSearch,%s)' % moviesearch)
				xbmc.executebuiltin('Container.Refresh')
			elif params.get('type', '') == 'tv':
				showsearch = dialog.input('ShowSearch')
				xbmc.executebuiltin('Skin.SetString(ShowSearch,%s)' % showsearch)
				xbmc.executebuiltin('Container.Refresh')
			elif params.get('type', '') == 'youtube':
				youtubesearch = dialog.input('YoutubeSearch')
				xbmc.executebuiltin('Skin.SetString(YoutubeSearch,%s)' % youtubesearch)
				xbmc.executebuiltin('Container.Refresh')
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'deletecache':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')
			xbmcgui.Window(10000).clearProperty(str(addon_ID_short())+'_running')
			for rel_path in os.listdir(Utils.ADDON_DATA_PATH):
				path = os.path.join(Utils.ADDON_DATA_PATH, rel_path)
				try:
					if os.path.isdir(path):
						shutil.rmtree(path)
				except Exception as e:
					Utils.log(e)
			Utils.notify('Cache deleted')

		elif info == 'auto_clean_cache':
			#info=auto_clean_cache&days=10
			days = params.get('days')
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')
			xbmcgui.Window(10000).clearProperty(str(addon_ID_short())+'_running')
			auto_clean_cache(days=days)
			Utils.notify('Cache deleted')

		elif info == 'setDownloadLocation':
			Utils.show_busy()
			new_location = xbmcgui.Dialog().browse(0, "Select Download Location", "video", defaultt=Utils.ADDON_DATA_PATH)
			xbmcaddon.Addon(addon_ID()).setSetting('DOWNLOAD_FOLDER', new_location)
			xbmcaddon.Addon(addon_ID()).setSetting('download_path', new_location)
			try: 
				xbmcaddon.Addon('plugin.video.seren_downloader').setSetting('DOWNLOAD_FOLDER',new_location)
				xbmcaddon.Addon('plugin.video.seren_downloader').setSetting('download_path',new_location)
			except:
				pass
			Utils.hide_busy()

		elif info == 'setmagnet_list':
			Utils.show_busy()
			new_location = xbmcgui.Dialog().browse(0, "Select Magnet Path Location", "video", defaultt=Utils.ADDON_DATA_PATH)
			new_location = os.path.join(new_location, 'magnet_list.txt')
			xbmcaddon.Addon(addon_ID()).setSetting('magnet_list', new_location)
			try: xbmcaddon.Addon('plugin.video.seren_downloader').setSetting('magnet_list',new_location)
			except: pass
			Utils.hide_busy()
			

		elif info == 'downloader_progress':
			Utils.hide_busy()
			curr_percent = xbmcgui.Window(10000).getProperty('curr_percent')
			percent_done = xbmcgui.Window(10000).getProperty('percent_done')
			seconds_remaining = xbmcgui.Window(10000).getProperty('seconds_remaining')
			minutes_remaining = xbmcgui.Window(10000).getProperty('minutes_remaining')
			hours_remaining = xbmcgui.Window(10000).getProperty('hours_remaining')
			num_lines_remaining = xbmcgui.Window(10000).getProperty('num_lines_remaining')
			msg = 'File_num_lines_remaining = %s || percent_done = %s || hours_remaining = %s ' % (str(num_lines_remaining),str(percent_done),str(hours_remaining))
			xbmcgui.Dialog().notification(heading='downloader_progress', message=msg, icon=xbmcaddon.Addon().getAddonInfo('icon'), time=5000, sound=True)
			xbmc.log(str(msg), level=xbmc.LOGINFO)

		elif info == 'run_downloader':
			Utils.hide_busy()
			try:
				import getSources
			except:
				from a4kscrapers_wrapper import getSources
			stop_downloader = xbmcaddon.Addon(addon_ID()).getSetting('magnet_list').replace('magnet_list.txt','stop_downloader')
			if os.path.exists(stop_downloader):
				os.remove(stop_downloader)

			magnet_list = xbmcaddon.Addon(addon_ID()).getSetting('magnet_list')
			download_path = xbmcaddon.Addon(addon_ID()).getSetting('download_path')
			xbmc.log(str('run_downloader___')+'run_downloader===>OPENINFO', level=xbmc.LOGINFO)
			return getSources.run_downloader(magnet_list, download_path)
			
		elif info == 'stop_downloader':
			Utils.hide_busy()
			#filename = "stop_downloader"
			stop_downloader = xbmcaddon.Addon(addon_ID()).getSetting('magnet_list').replace('magnet_list.txt','stop_downloader')
			open(stop_downloader, 'w')
			xbmc.log(str('stop_downloader__')+'stop_downloader===>OPENINFO', level=xbmc.LOGINFO)
			
	
		elif info == 'manage_download_list':
			magnet_list = xbmcaddon.Addon(addon_ID()).getSetting('magnet_list')
			from a4kscrapers_wrapper.tools import read_all_text
			lines = read_all_text(magnet_list).split('\n')
			curr_percent = xbmcgui.Window(10000).getProperty('curr_percent')
			percent_done = xbmcgui.Window(10000).getProperty('percent_done')
			seconds_remaining = xbmcgui.Window(10000).getProperty('seconds_remaining')
			minutes_remaining = xbmcgui.Window(10000).getProperty('minutes_remaining')
			hours_remaining = xbmcgui.Window(10000).getProperty('hours_remaining')
			num_lines_remaining = xbmcgui.Window(10000).getProperty('num_lines_remaining')
			msg = 'File_num_lines_remaining = %s || percent_done = %s || hours_remaining = %s ' % (str(num_lines_remaining),str(percent_done),str(hours_remaining))
			xbmcgui.Dialog().notification(heading='downloader_progress', message=msg, icon=xbmcaddon.Addon().getAddonInfo('icon'), time=5000, sound=True)
			labels = []
			for line in lines:
				try: new_line = eval(line)
				except: continue
				labels.append(str('%s | %s | %s' % (new_line['download_type'].upper(), unquote(new_line['file_name']), unquote(new_line['release_title']))))
			indexes = []
			indexes = xbmcgui.Dialog().multiselect(heading='Select Lines to Delete',options=labels)
			#xbmc.log(str(indexes)+'indexes===>OPENINFO', level=xbmc.LOGINFO)
			if indexes == None:
				Utils.hide_busy()
				return
			if len(indexes) == 0:
				Utils.hide_busy()
				return
			file1 = open(magnet_list, "w")
			file1.write("\n")
			file1.close()
			idx = 0
			for line in lines:
				try: 
					new_line = eval(line)
				except: 
					continue
				if idx in indexes:
					idx = idx + 1
					continue
					#xbmc.log(str(line)+'indexes===>OPENINFO', level=xbmc.LOGINFO)
				else:
					xbmc.log(str(str('%s | %s | %s' % (new_line['download_type'].upper(), unquote(new_line['file_name']), unquote(new_line['release_title']))))+str(idx+1)+'_KEEP_DOWNLOAD===>OPENINFO', level=xbmc.LOGINFO)
					file1 = open(magnet_list, "a") 
					file1.write(str(line))
					file1.write("\n")
					file1.close()
					idx = idx + 1
			Utils.hide_busy()

		elif info == 'fix_video':
			import json
			json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0","id": "1","method": "Player.GetProperties","params": {"playerid": 1,"properties": ["currentaudiostream", "currentsubtitle", "currentvideostream"]}}')
			curr_sub_audio_json  = json.loads(json_result)
			xbmc.log(str(curr_sub_audio_json)+'fix_video===>OPENINFO', level=xbmc.LOGINFO)
			aspect_43 = 4/3
			aspect_169 = 16/9
			height = curr_sub_audio_json['result']['currentvideostream']['height']
			width = curr_sub_audio_json['result']['currentvideostream']['width']
			xbmc.log(str(aspect_43)+'fix_video===>OPENINFO', level=xbmc.LOGINFO)
			xbmc.log(str(aspect_169)+'fix_video===>OPENINFO', level=xbmc.LOGINFO)
			xbmc.log(str(height)+'fix_video===>OPENINFO', level=xbmc.LOGINFO)
			xbmc.log(str(width)+'fix_video===>OPENINFO', level=xbmc.LOGINFO)
			xbmc.log(str(width/height)+'fix_video===>OPENINFO', level=xbmc.LOGINFO)
			test_43 = abs(aspect_43-(width/height))
			test_169 = abs(aspect_169-(width/height))
			#xbmc.log(str(test_43)+"__"+str(test_169)+'fix_video===>OPENINFO', level=xbmc.LOGINFO)
			if min(test_43,test_169) == test_43:
				if width/height > aspect_43:
					pixel_ratio = aspect_43/(width/height)
				else:
					pixel_ratio =  (width/height)/aspect_43
			else:
				if width/height > aspect_169:
					pixel_ratio = aspect_169/(width/height)
				else:
					pixel_ratio =  (width/height)/aspect_169
			pixel_ratio = round(pixel_ratio,2)
			xbmc.log(str(pixel_ratio)+'fix_video===>OPENINFO', level=xbmc.LOGINFO)
			json_result = xbmc.executeJSONRPC('{"id":1,"jsonrpc":"2.0","method":"Player.SetViewMode","params":{"viewmode": {"pixelratio": %s}}}' % str(pixel_ratio))
			curr_sub_audio_json  = json.loads(json_result)
			xbmc.log(str(curr_sub_audio_json)+'fix_video===>OPENINFO', level=xbmc.LOGINFO)

		elif info == 'estuary_fix':
			estuary_fix()
			Utils.hide_busy()

		elif info == 'setup_favourites':
			file_path = xbmcvfs.translatePath('special://userdata/favourites.xml')
			fav1_list = []
			fav1_list.append('    <favourite name="Trakt Watched TV" thumb="special://home/addons/script.extendedinfo/resources/skins/Default/media/tmdb/thumb.png">RunScript('+str(addonID)+',info=trakt_watched,trakt_type=tv)</favourite>')
			fav1_list.append('    <favourite name="Trakt Watched Movies" thumb="special://home/addons/script.extendedinfo/resources/skins/Default/media/tmdb/thumb.png">RunScript('+str(addonID)+',info=trakt_watched,trakt_type=movie)</favourite>')
			fav1_list.append('    <favourite name="Reopen Last" thumb="special://home/addons/script.extendedinfo/resources/skins/Default/media/tmdb/thumb.png">RunScript('+str(addonID)+',info=reopen_window)</favourite>')
			fav1_list.append('    <favourite name="Youtube Trailers" thumb="special://home/addons/script.extendedinfo/resources/skins/Default/media/common/youtube.png">RunScript('+str(addonID)+',info=youtube,search_str=trailers)</favourite>')
			fav1_list.append('    <favourite name="Eps_Movies Watching" thumb="special://home/addons/script.extendedinfo/resources/skins/Default/media/tmdb/thumb.png">RunScript('+str(addonID)+',info=ep_movie_progress)</favourite>')
			fav1_list.append('    <favourite name="Settings" thumb="special://home/addons/script.extendedinfo/resources/skins/Default/media/icons/tool2.png">RunScript('+str(addonID)+',info=open_settings)</favourite>')
			fav1_list.append('    <favourite name="manage_download_list" thumb="special://home/addons/script.extendedinfo/resources/skins/Default/media/icons/database.png">RunScript('+str(addonID)+',info=manage_download_list)</favourite>')
			fav1_list.append('    <favourite name="run_downloader" thumb="special://home/addons/script.extendedinfo/resources/skins/Default/media/netflix/play.png">RunScript('+str(addonID)+',info=run_downloader)</favourite>')
			fav1_list.append('    <favourite name="stop_downloader" thumb="special://home/addons/script.extendedinfo/resources/skins/Default/media/netflix/stop.png">RunScript('+str(addonID)+',info=stop_downloader)</favourite>')
			file1 = open(file_path, 'r')
			lines = file1.readlines()
			new_file = ''
			update_list = []
			for j in fav1_list:
				curr_test = j.split('RunScript(')[1].split(')</favourite>')[0]
				if curr_test in str(lines):
					continue
				else:
					update_list.append(j)
			for idx, line in enumerate(lines):
				if line == '</favourites>\n' or idx == len(lines) - 1:
					for j in update_list:
						new_file = new_file + j + '\n'
					new_file = new_file + line
				else:
					new_file = new_file + line
			file1.close()
			if len(update_list) > 0:
				xbmc.log(str('setup_favourites')+'_patch_seren_a4k===>OPENINFO', level=xbmc.LOGINFO)
				file1 = open(file_path, 'w')
				file1.writelines(new_file)
				file1.close()
			Utils.hide_busy()

		elif info == 'patch_core':
			from a4kscrapers_wrapper import getSources
			getSources.patch_ak4_core_find_url()

		elif info == 'patch_urllib3':
			Utils.show_busy()
			Utils.patch_urllib()
			Utils.hide_busy()

		elif info == 'patch_seren_a4k':
			Utils.show_busy()
			patch_line_147 = '            response = None'
			patch_update_147 = """            response = response_err ## PATCH
"""

			patch_line_150 = '                response = request(None)'
			patch_update_150 = """                try: response = request(None) ## PATCH
                except requests.exceptions.ConnectionError: return response ## PATCH
"""

			patch_line_154 = '                response_err = response'
			patch_update_154 = """                if response: ## PATCH
                    response_err = response ## PATCH
                    self._verify_response(response) ## PATCH
                else: ## PATCH
                    self._verify_response(response_err) ## PATCH
"""

			if params.get('downloader','') == 'true':
				#kodi-send --action="RunScript(script.extendedinfo,info=patch_seren_a4k,downloader=true)"
				file_path = os.path.join(os.path.join(Utils.ADDON_DATA_PATH.replace(addonID,'plugin.video.seren_downloader'), 'providerModules', 'a4kScrapers') , 'request.py')
			else:
				#kodi-send --action="RunScript(script.extendedinfo,info=patch_seren_a4k)"
				file_path = os.path.join(os.path.join(Utils.ADDON_DATA_PATH.replace(addonID,'plugin.video.seren'), 'providerModules', 'a4kScrapers') , 'request.py')
			file1 = open(file_path, 'r')
			lines = file1.readlines()
			new_file = ''
			update_flag = False
			for idx, line in enumerate(lines):
				if update_flag == 154:
					update_flag = True
					continue
				if '## PATCH' in str(line):
					update_flag = False
					break
				if idx == 147-1 and line == patch_line_147 or patch_line_147 in str(line):
					new_file = new_file + patch_update_147
					update_flag = True
				elif idx == 150-1 and line == patch_line_150 or patch_line_150 in str(line):
					new_file = new_file + patch_update_150
					update_flag = True
				elif idx == 154-1 and line == patch_line_154 or patch_line_154 in str(line):
					new_file = new_file + patch_update_154
					update_flag = 154
				else:
					new_file = new_file + line
			file1.close()
			if update_flag:
				xbmc.log(str('patch_seren_a4k')+'_patch_seren_a4k===>OPENINFO', level=xbmc.LOGINFO)
				file1 = open(file_path, 'w')
				file1.writelines(new_file)
				file1.close()
			Utils.hide_busy()

		elif info == 'patch_fen_light':
			Utils.show_busy()
			file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.fenlight'), 'resources','lib','modules') , 'sources.py')
			from distutils.dir_util import copy_tree
			skin_source = os.path.join(Utils.ADDON_PATH, 'resources' , 'skins', 'skin.estuary_fen_light')
			skin_dest = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.fenlight'), 'resources', 'skins'), 'Custom','skin.estuary')

			fenlight_path = os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.fenlight'))
			if os.path.exists(fenlight_path):
				if not os.path.exists(skin_dest):
					copy_tree(skin_source, skin_dest)
					xbmc.log(str(skin_dest)+'_FENLIGHT_SKIN===>OPENINFO', level=xbmc.LOGINFO)
			
			fen_path = os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.fen'))
			skin_source = os.path.join(Utils.ADDON_PATH, 'resources' , 'skins', 'skin.estuary_fen')
			skin_dest = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.fen'), 'resources', 'skins'), 'Custom','skin.estuary')
			if os.path.exists(fen_path):
				if not os.path.exists(skin_dest):
					copy_tree(skin_source, skin_dest)
					xbmc.log(str(skin_dest)+'_FEN_SKIN===>OPENINFO', level=xbmc.LOGINFO)

			xbmc.log(str(file_path)+'===>OPENINFO', level=xbmc.LOGINFO)
			Utils.hide_busy()
			return

			file1 = open(file_path, 'r')
			lines = file1.readlines()
			new_file = ''
			update_flag = False
			line_update = '''		params_get = self.params.get ## PATCH
		params['number'] = fenlight_number() ## PATCH
'''
			for idx, line in enumerate(lines):
				if '## PATCH' in str(line):
					update_flag = False
					xbmc.log('ALREADY_PATCHED_FEN_===>OPENINFO', level=xbmc.LOGINFO)
					break
				try: test_var = lines[idx+1]
				except: test_var = ''
				if 'params_get = self.params.get' in str(line) and 'TMDbHelper cannot be used with Fen Light' in str(test_var):
					new_file = new_file + line_update
					update_flag = True
				else:
					new_file = new_file + line
			file1.close()
			if update_flag:
				file1 = open(file_path, 'w')
				file1.writelines(new_file)
				file1.close()
				xbmc.log(str(file_path)+'_PATCH_FEN===>OPENINFO', level=xbmc.LOGINFO)
			Utils.hide_busy()

		elif info == 'patch_tmdb_helper':
			Utils.show_busy()
			
			file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','player') , 'players.py')
			if not os.path.exists(file_path):
				file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'lib','player') , 'players.py')

			themoviedb_helper_path = os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'))
			xbmc.log(str(file_path)+'===>OPENINFO', level=xbmc.LOGINFO)

			file1 = open(file_path, 'r')
			lines = file1.readlines()
			new_file = ''
			update_flag = False
			line_update = '''            for idx, i in enumerate(players_list): ## PATCH
                if 'auto_cloud' in str(i).lower() and self.tmdb_type != 'movie': ## PATCH
                    auto_var = idx ## PATCH
                    break ## PATCH
                if 'Auto_Torr_Scrape' in str(i) and self.tmdb_type == 'movie': ## PATCH
                    auto_var = idx ## PATCH
                    break ## PATCH
            #return Dialog().select(header, players, useDetails=detailed) ## PATCH
            #return Dialog().select(header, players, autoclose=30000, preselect=auto_var, useDetails=detailed) ## PATCH
            return Dialog().select(header, players, autoclose=30000, preselect=auto_var, useDetails=detailed) ## PATCH
'''
			for idx, line in enumerate(lines):
				if '## PATCH' in str(line):
					update_flag = False
					xbmc.log('ALREADY_PATCHED_TMDB_HELPER_===>OPENINFO', level=xbmc.LOGINFO)
					break
				#try: test_var = lines[idx+1]
				#except: test_var = ''
				if 'return Dialog().select(header, players, useDetails=detailed)' in str(line):# and 'TMDbHelper cannot be used with Fen Light' in str(test_var):
					new_file = new_file + line_update
					update_flag = True
				else:
					new_file = new_file + line
			file1.close()
			if update_flag:
				file1 = open(file_path, 'w')
				file1.writelines(new_file)
				file1.close()
				xbmc.log(str(file_path)+'_PATCH_TMDB_HELPER===>OPENINFO', level=xbmc.LOGINFO)
			Utils.hide_busy()


def follow(thefile):
	while True:
		line = thefile.readline()
		if not line or not line.endswith('\n'):
			time.sleep(0.1)
			continue
		yield line

def follow2():
	logfn = xbmcvfs.translatePath(r'special://logpath\kodi.log')
	with open(logfn, 'r') as f:
		f.seek(0, 2)           # seek @ EOF
		fsize = f.tell()        # Get Size
		f.seek(max(fsize - 9024, 0), 0)  # Set pos @ last n chars
		lines = f.readlines()       # Read to end
	line = lines[-6:]
	return str(line)

def get_log_error_flag(mode=None):
	"""
	Retrieves dimensions and framerate information from XBMC.log
	Will likely fail if XBMC in debug mode - could be remedied by increasing the number of lines read
	Props: http://stackoverflow.com/questions/260273/most-efficient-way-to-search-the-last-x-lines-of-a-file-in-python
	@return: dict() object with the following keys:
								'pwidth' (int)
								'pheight' (int)
								'par' (float)
								'dwidth' (int)
								'dheight' (int)
								'dar' (float)
								'fps' (float)
	@rtype: dict()
	"""
	logfn = xbmcvfs.translatePath(r'special://logpath\kodi.log')
	#logfn = '/home/osmc/.kodi/temp/kodi.log'
	xbmc.sleep(250)  # found originally that it wasn't written yet
	with open(logfn, 'r') as f:
		f.seek(0, 2)           # seek @ EOF
		fsize = f.tell()        # Get Size
		f.seek(max(fsize - 9024, 0), 0)  # Set pos @ last n chars
		lines = f.readlines()       # Read to end
	lines = lines[-15:]    # Get last 10 lines
	#xbmc.log(str(lines)+'===>OPENINFO', level=xbmc.LOGINFO)
	ret = None
	error_flag = False
	if mode == 'Exception':
		if 'The following content is not available on this app' in str(lines):
			error_flag = True
			return error_flag
	if mode == 'tmdb_helper':
		if 'lib.player - playing' in str(lines) and 'plugin://' in str(lines) and 'plugin.video.themoviedb.helper/plugin.py): script successfully run' in str(lines):
			error_flag = True
			return error_flag
		if 'TORRENTS_FOUND' in str(lines) and '===>A4K_Wrapper' in str(lines):
			error_flag = True
			return error_flag
	if mode == 'seren':
		if 'script successfully run' in str(lines) and '.seren_downloader' in str(lines):
			return error_flag
		if 'Exited Keep Alive' in str(lines) and 'SEREN' in str(lines):
			error_flag = True
			return error_flag
	return error_flag

def resolve_url(handle):
	import xbmcplugin
	if handle:
		xbmcplugin.setResolvedUrl(handle=int(handle), succeeded=False, listitem=xbmcgui.ListItem())

def reopen_window():
	while xbmc.Player().isPlaying():
		xbmc.sleep(500)
	wm.window_stack_empty()
	return wm.open_video_list(search_str='', mode='reopen_window')

def auto_clean_cache_seren_downloader(days=None):
	import os 
	import datetime
	import glob
	xbmc.log('STARTING===>auto_clean_cache_seren_downloader', level=xbmc.LOGINFO)
	path = xbmcvfs.translatePath('special://profile/addon_data/'+str('plugin.video.seren_downloader')+'/')
	if days==None:
		days = -30
	else:
		days = int(days)*-1

	today = datetime.datetime.today()#gets current time
	if not xbmcvfs.exists(path):
		return
		#xbmcvfs.mkdir(path)
	os.chdir(path) #changing path to current path(same as cd command)

	directories_list = ['TheMovieDB', 'TVMaze']
	#we are taking current folder, directory and files 
	#separetly using os.walk function
	for root,directories,files in os.walk(path,topdown=False): 
		for name in files:
			#this is the last modified time
			t = os.stat(os.path.join(root, name))[8] 
			filetime = datetime.datetime.fromtimestamp(t) - today
			#checking if file is more than 7 days old 
			#or not if yes then remove them
			if filetime.days <= days: # and 'Taste' not in str(root):
				#print(os.path.join(root, name), filetime.days)
				for i in directories_list:
					target = str(os.path.join(root, name))
					if str(i) in target:
						xbmc.log(str(target)+'===>DELETE', level=xbmc.LOGINFO)
						os.remove(target)

def auto_clean_cache(days=None):
	#import os 
	#import datetime
	#import glob
	xbmc.log('STARTING===>auto_clean_cache', level=xbmc.LOGINFO)
	#path = Utils.ADDON_DATA_PATH + '/'
	#if days==None:
	#	days = -30
	#else:
	#	days = int(days)*-1

	#today = datetime.datetime.today()#gets current time
	#if not xbmcvfs.exists(path):
	#	xbmcvfs.mkdir(path)
	#os.chdir(path) #changing path to current path(same as cd command)

	#directories_list = ['Trakt', 'TheMovieDB', 'show_filters', 'TVMaze', 'IMDB', 'FanartTV', 'TasteDive', 'YouTube', 'images', 'rss']
	##we are taking current folder, directory and files 
	##separetly using os.walk function
	#for root,directories,files in os.walk(path,topdown=False): 
	#	for name in files:
	#		#this is the last modified time
	#		t = os.stat(os.path.join(root, name))[8] 
	#		filetime = datetime.datetime.fromtimestamp(t) - today
	#		#checking if file is more than 7 days old 
	#		#or not if yes then remove them
	#		if filetime.days <= days: # and 'Taste' not in str(root):
	#			#print(os.path.join(root, name), filetime.days)
	#			for i in directories_list:
	#				target = str(os.path.join(root, name))
	#				if str(i) in target:
	#					xbmc.log(str(target)+'===>DELETE', level=xbmc.LOGINFO)
	#					os.remove(target)
	Utils.db_delete_expired(connection=Utils.db_con)
	#Utils.db_con.close()
	auto_clean_cache_seren_downloader(days=30)

def auto_library():
	Utils.hide_busy()
	#xbmc.log(str('auto_library')+'===>OPEN_INFO', level=xbmc.LOGINFO)
	#return
	from resources.lib.library import library_auto_tv
	from resources.lib.library import library_auto_movie
	from resources.lib.library import trakt_calendar_list
	from resources.lib.library import refresh_recently_added
	from resources.lib.library import basedir_tv_path
	from resources.lib.library import basedir_movies_path
	Utils.hide_busy()
	library_tv_sync = str(xbmcaddon.Addon(addon_ID()).getSetting('library_tv_sync'))
	if library_tv_sync == 'true':
		library_tv_sync = True
	if library_tv_sync == 'false':
		library_tv_sync = False
	library_movies_sync = str(xbmcaddon.Addon(addon_ID()).getSetting('library_movies_sync'))
	if library_movies_sync == 'true':
		library_movies_sync = True
	if library_movies_sync == 'false':
		library_movies_sync = False

	if not xbmc.Player().isPlaying() and (library_tv_sync or library_movies_sync):
		xbmcgui.Dialog().notification(heading='Startup Tasks', message='TRAKT_SYNC', icon=icon_path(),time=1000,sound=False)
	if library_movies_sync:
		library_auto_movie()
	if library_tv_sync:
		library_auto_tv()
		xbmc.log(str('refresh_recently_added')+'===>OPEN_INFO', level=xbmc.LOGFATAL)
		refresh_recently_added()
		xbmc.log(str('trakt_calendar_list')+'===>OPEN_INFO', level=xbmc.LOGFATAL)
		if not xbmc.Player().isPlaying():
			xbmcgui.Dialog().notification(heading='Startup Tasks', message='trakt_calendar_list', icon=icon_path(),time=1000,sound=False)
		trakt_calendar_list()
	if not xbmc.Player().isPlaying() and (library_tv_sync or library_movies_sync):
		xbmcgui.Dialog().notification(heading='Startup Tasks', message='Startup Complete!', icon=icon_path(), time=1000,sound=False)
	#xbmc.log(str('UPDATE_WIDGETS')+'===>OPEN_INFO', level=xbmc.LOGFATAL)
	#if not xbmc.Player().isPlaying():
	#	xbmc.executebuiltin('UpdateLibrary(video,widget_refresh,true)')
	if library_movies_sync:
		xbmc.log(str('UpdateLibrary_MOVIES')+'===>OPEN_INFO', level=xbmc.LOGFATAL)
		xbmc.executebuiltin('UpdateLibrary(video, {})'.format(basedir_movies_path()))
	if library_tv_sync:
		xbmc.log(str('UpdateLibrary_TV')+'===>OPEN_INFO', level=xbmc.LOGFATAL)
		xbmc.executebuiltin('UpdateLibrary(video, {})'.format(basedir_tv_path()))
	return
	rss_1_enabled = xbmcaddon.Addon(addon_ID()).getSetting('rss.1')
	rss_2_enabled = xbmcaddon.Addon(addon_ID()).getSetting('rss.2')
	rss_3_enabled = xbmcaddon.Addon(addon_ID()).getSetting('rss.3')
	rss_4_enabled = xbmcaddon.Addon(addon_ID()).getSetting('rss.4')
	if rss_1_enabled == 'true' or rss_2_enabled == 'true' or rss_3_enabled == 'true'  or rss_4_enabled == 'true':
	#if library_tv_sync or library_movies_sync:
		from a4kscrapers_wrapper import get_meta
		log(str('get_meta.get_rss_cache()'))
		get_meta.get_rss_cache()
		#import time
		#time_since_up = time.monotonic()
		#realizer_test = xbmc.getCondVisibility('System.HasAddon(plugin.video.realizer)')
		#if not xbmc.Player().isPlaying() and realizer_test:
		#	try:
		#		if time_since_up > 600:
		#			#print('NOW')
		#			hours_since_up = int((time_since_up)/60/60)
		#			xbmc.log(str(hours_since_up)+str('=multiple of 8 hours=')+ str(hours_since_up % 8 == 0)+'=hours_since_up===>OPEN_INFO', level=xbmc.LOGINFO)
		#			if hours_since_up >=1:
		#				xbmc.executebuiltin('RunPlugin(plugin://plugin.video.realizer/?action=rss_update)')
		#	except:
		#		if time_since_up > 600:
		#			#print('NOW')
		#			hours_since_up = int((time_since_up)/60/60)
		#			xbmc.log(str(hours_since_up)+str('=multiple of 8 hours=')+ str(hours_since_up % 8 == 0)+'=hours_since_up===>OPEN_INFO', level=xbmc.LOGINFO)
		#			if hours_since_up >=1:
		#				xbmc.executebuiltin('RunPlugin(plugin://plugin.video.realizer/?action=rss_update)')
		#xbmc.executebuiltin('RunPlugin(plugin://plugin.video.realizer/?action=rss_update)')
		

def context_info():
	import json
	base = 'RunScript('+str(addon_ID())+',info='
	#info = sys.listitem.getVideoInfoTag()

	json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Title", "Player.Filename","Player.Filenameandpath", "VideoPlayer.MovieTitle", "VideoPlayer.TVShowTitle", "VideoPlayer.DBID", "VideoPlayer.DBTYPE", "VideoPlayer.Duration", "VideoPlayer.Season", "VideoPlayer.Episode", "VideoPlayer.DBID", "VideoPlayer.Year", "VideoPlayer.Rating", "VideoPlayer.mpaa", "VideoPlayer.Studio", "VideoPlayer.VideoAspect", "VideoPlayer.Plot", "VideoPlayer.RatingAndVotes", "VideoPlayer.Genre", "VideoPlayer.LastPlayed", "VideoPlayer.IMDBNumber", "ListItem.DBID", "Container.FolderPath", "Container.FolderName", "Container.PluginName", "ListItem.TVShowTitle", "ListItem.FileNameAndPath"]}, "id":1}')
	json_object  = json.loads(json_result)

	dbid = json_object['result']['VideoPlayer.DBID']
	type = json_object['result']['VideoPlayer.DBTYPE']
	episode = json_object['result']['VideoPlayer.Episode']
	Season = json_object['result']['VideoPlayer.Season']
	remote_id = None
	IMDBNumber = json_object['result']['VideoPlayer.IMDBNumber']
	#xbmc.log(str(IMDBNumber)+'===>META_FILTERS', level=xbmc.LOGINFO)
	
	if not type in ['movie','tvshow','season','episode','actor','director']:
		if episode == '' or episode == None:
			type = 'movie'
			title = json_object['result']['VideoPlayer.MovieTitle']
		else:
			type = 'episode'
			title = json_object['result']['VideoPlayer.TVShowTitle']

	params = {}
	infos = []
	if type   == 'movie':
		base = 'RunScript('+str(addon_ID())+',info='+str(addon_ID_short())
		url = '%s,dbid=%s,id=%s,imdb_id=%s,name=%s)' % (base, dbid, remote_id, IMDBNumber, title)
		infos.append(str(addon_ID_short()))
		params['dbid'] = dbid
		params['id'] = remote_id
		params['imdb_id'] = IMDBNumber
		params['name'] = title
	elif type == 'episode':
		infos.append('extendedepisodeinfo')
		params['dbid'] = dbid
		params['id'] = remote_id
		params['tvshow'] = title
		params['season'] = Season
		params['episode'] = episode
	xbmc.log(str(params)+'===>context_info', level=xbmc.LOGINFO)
	if infos:
		start_info_actions(infos, params)


def context_info2():
	import json
	base = 'RunScript('+str(addon_ID())+',info='
	#info = sys.listitem.getVideoInfoTag()

	json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["ListItem.Title", "ListItem.Label",  "ListItem.MovieTitle",    "ListItem.DBTYPE",  "ListItem.Season", "ListItem.Episode", "ListItem.Year",  "ListItem.IMDBNumber", "ListItem.DBID",   "ListItem.TVShowTitle", "ListItem.FileNameAndPath", "ListItem.UniqueID(tmdb)", "ListItem.UniqueID(imdb)", "Container.ListItem.UniqueID(imdb)"]}, "id":1}')
	json_object  = json.loads(json_result)
	#xbmc.log(str(json_object)+'===>PHIL', level=xbmc.LOGINFO)
	dbid = json_object['result']['ListItem.DBID']
	type = json_object['result']['ListItem.DBTYPE']
	episode = json_object['result']['ListItem.Episode']
	Season = json_object['result']['ListItem.Season']
	TVShowTitle = json_object['result']['ListItem.TVShowTitle']
	MovieTitle = json_object['result']['ListItem.MovieTitle']
	Title = json_object['result']['ListItem.Title']
	Label = json_object['result']['ListItem.Label']
	remote_id = json_object['result']['ListItem.UniqueID(tmdb)']
	imdb = json_object['result']['ListItem.UniqueID(imdb)']

	#json_object['result']['ListItemTMDBNumber'] = property_value

	IMDBNumber = json_object['result']['ListItem.IMDBNumber']
	if (IMDBNumber == '' or IMDBNumber == None):
		IMDBNumber = imdb
	#xbmc.log(str(json_object)+'===>PHIL2', level=xbmc.LOGINFO)

	if not type in ['movie','tvshow','season','episode','actor','director']:
		if (episode == '' or episode == None) and (TVShowTitle == '' or TVShowTitle == None):
			type = 'movie'
		else:
			type = 'tvshow'

	params = {}
	infos = []
	if (TVShowTitle == '' or TVShowTitle == None):
		TVShowTitle = Title
	if type   == 'movie':
		base = 'RunScript('+str(addon_ID())+',info='+str(addon_ID_short())
		if (MovieTitle == '' or MovieTitle == None):
			MovieTitle = Title
		url = '%s,dbid=%s,id=%s,imdb_id=%s,name=%s)' % (base, dbid, remote_id, IMDBNumber, MovieTitle)
		infos.append(str(addon_ID_short()))
		params['dbid'] = dbid
		params['id'] = remote_id
		params['imdb_id'] = IMDBNumber
		params['name'] = MovieTitle
		#xbmc.executebuiltin(url)
	elif type == 'tvshow':
		infos.append('extendedtvinfo')
		params['dbid'] = dbid
		params['id'] = remote_id
		params['imdb_id'] = IMDBNumber
		params['name'] = TVShowTitle
		#xbmc.executebuiltin('%sextendedtvinfo,dbid=%s,id=%s,name=%s)' % (base, dbid, remote_id, info.getTVShowTitle()))
	elif type == 'season':
		infos.append('seasoninfo')
		params['dbid'] = dbid
		params['id'] = remote_id
		params['tvshow'] = TVShowTitle
		params['season'] = Season
		#xbmc.executebuiltin('%sseasoninfo,dbid=%s,id=%s,tvshow=%s,season=%s)' % (base, dbid, remote_id, info.getTVShowTitle(), info.getSeason()))
	elif type == 'episode':
		infos.append('extendedepisodeinfo')
		params['dbid'] = dbid
		params['id'] = remote_id
		params['tvshow'] = TVShowTitle
		params['season'] = Season
		params['episode'] = episode
		#xbmc.executebuiltin('%sextendedepisodeinfo,dbid=%s,id=%s,tvshow=%s,season=%s,episode=%s)' % (base, dbid, remote_id, info.getTVShowTitle(), info.getSeason(), info.getEpisode()))
	elif type in ['actor', 'director']:
		infos.append('extendedactorinfo')
		params['name'] = Label
		#xbmc.executebuiltin('%sextendedactorinfo,name=%s)' % (base, sys.listitem.getLabel()))
	xbmc.log(str(params)+'===>context_info2', level=xbmc.LOGINFO)
	if infos:
		start_info_actions(infos, params)

def estuary_fix():
	#osmc_home = '/usr/share/kodi/addons/skin.estuary/xml/Home.xml'
	import os
	osmc_home = xbmcvfs.translatePath('special://skin/xml/Home.xml')
	estuary_home_fix2 = xbmcvfs.translatePath(Utils.ADDON_PATH + '/estuary_home_fix2.py')
	command = "sudo python %s '%s'" % (estuary_home_fix2, osmc_home)
	xbmc.log(str(command)+'===>OPEN_INFO', level=xbmc.LOGINFO)
	os.system(command)
	return

	home_xml = osmc_home 
	file1 = open(home_xml, 'r')
	Lines = file1.readlines()
	out_xml = ''
	item_flag = False
	new_item = '''

							<item>
								<label>$LOCALIZE[10134]</label>
								<onclick>ActivateWindow(favourites)</onclick>
								<property name="menu_id">$NUMBER[14000]</property>
								<thumb>icons/sidemenu/favourites.png</thumb>
								<property name="id">favorites</property>
								<visible>!Skin.HasSetting(HomeMenuNoFavButton)</visible>
							</item>

	'''
	item_count = 0
	change_flag = False
	for line in Lines:
		if item_flag == False and not '<item>' in line:
			out_xml = out_xml + line 
		if '<item>' in line:
			item_flag = True
			string = line
			item_count = item_count + 1
			continue
		if item_flag == True:
			string  = string + line
		if '</item>' in line:
			item_flag = False
			curr_item = string.split('<property name="id">')[1].split('</property>')[0]
			print(item_count, curr_item )
			if curr_item == 'movies' and item_count == 1:
				string = new_item + string 
				change_flag = True
			if curr_item == 'favorites' and item_count == 1:
				change_flag = False
			if curr_item == 'favorites' and item_count > 2:
				continue
				change_flag = True
			out_xml = out_xml + string

	if change_flag == True:
		file1 = open(home_xml, 'w')
		file1.writelines(out_xml)
		file1.close()
		print(out_xml)


	#osmc_home = '/usr/share/kodi/addons/skin.estuary/xml/VideoOSD.xml'
	#osmc_home = '/usr/share/kodi/addons/skin.estuary/xml/Home.xml'
	osmc_home = xbmcvfs.translatePath('special://skin/xml/VideoOSD.xml')

	home_xml = osmc_home 
	file1 = open(home_xml, 'r')
	Lines = file1.readlines()
	out_xml = ''
	item_flag = False
	old_item = '''<defaultcontrol always="true">602</defaultcontrol>'''
	new_item = '''
		<defaultcontrol always="true">70048</defaultcontrol>
	'''

	item_count = 0
	change_flag = False
	for line in Lines:
		if item_flag == False and old_item in str(line):
			out_xml = out_xml + new_item 
			item_flag = True
			change_flag = True
		else:
			out_xml = out_xml + line


	if change_flag == True:
		file1 = open(home_xml, 'w')
		file1.writelines(out_xml)
		file1.close()
		print(out_xml)
		
	line_593_594 = """				<onup>noop</onup>
				<ondown>105</ondown>"""
	line_593 = """<onup>noop</onup>"""
	line_594 = """<ondown>105</ondown>"""
	line_3 = """<defaultcontrol always="true">300</defaultcontrol>"""

	line_593_594_new = """				<onup>300</onup>
				<ondown>300</ondown>"""
	line_3_new = """	<defaultcontrol always="true">105</defaultcontrol>"""

	osmc_home = xbmcvfs.translatePath('special://skin/xml/DialogKeyboard.xml')
	home_xml = osmc_home 
	file1 = open(home_xml, 'r')
	Lines = file1.readlines()
	out_xml = ''
	item_flag = False
	item_count = 0
	change_flag = False
	for line in Lines:
		if line_3 in str(line):
			out_xml = out_xml + line_3_new 
			item_flag = True
			change_flag = True
		if line_593 in str(line):
			out_xml = out_xml + line_593_594_new 
			item_flag = True
			change_flag = True
		if line_594 in str(line):
			continue
		else:
			out_xml = out_xml + line


	if change_flag == True:
		file1 = open(home_xml, 'w')
		file1.writelines(out_xml)
		file1.close()
		print(out_xml)