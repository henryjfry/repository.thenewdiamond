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

from inspect import currentframe, getframeinfo
#Utils.tools_log( (str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))) )

def start_info_actions(infos, params):
	addonID = addon_ID()
	addonID_short = addon_ID_short()

	wm.custom_filter = params.get('meta_filter')
	Utils.tools_log(Utils.db_con)
	if wm.custom_filter:
		wm.custom_filter = eval(unquote(wm.custom_filter))

	keep_stack = params.get('keep_stack',False)

	if 'imdbid' in params and 'imdb_id' not in params:
		params['imdb_id'] = params['imdbid']
	for info in infos:
		Utils.show_busy()
		data = [], ''

		if info == 'trakt_refresh':
			from resources.lib.trakt_api import refresh_token
			refresh_token()
			Utils.hide_busy()
			return

		if info == 'login_trakt':
			from resources.lib.trakt_api import login_trakt
			login_trakt()
			Utils.hide_busy()
			return


		if info == 'trakt_cleanup':
			Utils.tools_log('trakt_watched_tv_movies_cleanup')
			from resources.lib.library import trakt_watched_tv_movies_cleanup
			trakt_watched_tv_movies_cleanup()

		if info == 'rss_test':
			from a4kscrapers_wrapper import get_meta
			get_meta.get_rss_cache()

		if info == 'imdb_trailers_best' or info == 'imdb_trailers_choice':
			import imdb_trailers
			imdb_id = params.get('imdb_id')
			if info == 'imdb_trailers_best':
				select = False
			else:
				try: select = params.get('select')
				except: select = False
				if str(select).lower() == 'true' or select == True:
					select = True
				else:
					select = False
			try: season = int(params.get('season'))
			except: season = None
			imdb_trailers.play_imdb_trailer(imdb_id=imdb_id, select=select, season=season)

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

		if info == 'setup_magneto_scrapers':
			from a4kscrapers_wrapper import getSources
			getSources.setup_magneto_scrapers()

		if info == 'setup_coco_scrapers':
			from a4kscrapers_wrapper import getSources
			getSources.setup_coco_scrapers()

		if info == 'a4kProviders':
			from a4kscrapers_wrapper import getSources
			getSources.setup_providers('https://bit.ly/a4kScrapers')
			Utils.hide_busy()

		if info == 'a4kProviders_manage':
			from a4kscrapers_wrapper import getSources
			getSources.enable_disable_providers_kodi()
			Utils.hide_busy()

		if info == 'get_imdb_language':
			from resources.lib import TheMovieDB
			languages = TheMovieDB.get_imdb_language('tt8421350')
			Utils.tools_log(languages)

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
			wm.window_stack_empty()
			return wm.open_video_list(search_str=search_str, mode='filter')



		elif info == 'reopen_window':
			reopen_window()

		elif info == 'youtube':
			search_str = params.get('search_str')
			wm.window_stack_empty()
			return wm.open_youtube_list(search_str=search_str)

		elif info == 'tastedive_search':
			search_str = params.get('search_str')
			media_type = str(params['media_type'])
			limit = params.get('limit', 10)
			from resources.lib import TheMovieDB
			response = TheMovieDB.get_tastedive_data_scrape(query=search_str, year='', limit=50, media_type=media_type)
			wm.window_stack_empty()
			return wm.open_video_list(mode='tastedive&' + str(media_type), listitems=[], search_str=response, filter_label='TasteDive Similar ('+str(search_str)+'):')

		elif info == 'tastedive_movies':
			from resources.lib import TheMovieDB
			response = TheMovieDB.get_trakt(trakt_type='movie',info='trakt_watched',limit=30)
			response3 = []
			for i in response:
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

		elif info == 'play_test_pop_stack':
			import json
			tmdbhelper_flag = False
			reopen_play_fail = xbmcaddon.Addon(addon_ID()).getSetting('reopen_play_fail')
			xbmcgui.Window(10000).setProperty('diamond_info_started', 'True')
			xbmc.sleep(3000)
			if reopen_play_fail == 'false':
				return
			Utils.tools_log('start...','play_test_pop_stack')
			home_count = 0
			for i in range(1, int((145 * 1000)/1000)):
				window_id = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
				window_id = json.loads(window_id)
				xbmc.sleep(1000)
				window_id2 = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
				window_id2 = json.loads(window_id2)
				if (window_id['result']['currentwindow']['label'].lower() in ['home','notification'] or window_id['result']['currentwindow']['id'] in [10000,10107]) and window_id2 == window_id:
					home_count = home_count + 1
					if home_count > 10:
						Utils.tools_log('\n\n\n\nwm.pop_stack()......','1play_test_pop_stack')
						Utils.tools_log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
						
						return wm.pop_stack()
				if (window_id['result']['currentwindow']['label'].lower() in ['busydialognocancel'] or window_id['result']['currentwindow']['id'] in [10160]) and window_id2 == window_id:
					error_flag = get_log_error_flag(mode='Exception')
					if error_flag:
						xbmc.executebuiltin('Dialog.Close(all,true)')
						Utils.tools_log('\n\n\n\nwm.pop_stack()......','2play_test_pop_stack')
						Utils.tools_log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
						return wm.pop_stack()
				if xbmc.Player().isPlaying() or xbmc.getCondVisibility('Window.IsActive(12005)'):
					Utils.tools_log('\n\n\n\nPlayback_Success.......','play_test_pop_stack')
					return

				if tmdbhelper_flag == True and window_id != window_id2:
					xbmc.sleep(500)
					error_flag = get_log_error_flag(mode='tmdb_helper')
					if error_flag:
						Utils.tools_log('\n\n\n\ntmdb_helper_error_flag.......SLEEP......','play_test_pop_stack')
						xbmc.sleep(7500)

				if window_id['result']['currentwindow']['label'] == 'Select dialog' or window_id['result']['currentwindow']['id'] == 12000:
					if tmdbhelper_flag == False:
						Utils.hide_busy()
					tmdbhelper_flag = True
				elif tmdbhelper_flag and ( xbmc.Player().isPlaying() or ( window_id['result']['currentwindow']['label'].lower() == 'fullscreenvideo' or window_id['result']['currentwindow']['id'] == 12005 and window_id2 == window_id and i > 4 ) ):
					Utils.tools_log('\n\n\n\nPlayback_Success.......','play_test_pop_stack')
					return
				elif tmdbhelper_flag and (window_id['result']['currentwindow']['label'].lower() in ['home','notification'] or window_id['result']['currentwindow']['id'] in [10000,10107]) and window_id2 == window_id and i > 4:
					if xbmc.Player().isPlaying():
						Utils.tools_log('\n\n\n\nPlayback_Success.......','play_test_pop_stack')
						return
					else:
						error_flag = get_log_error_flag(mode='seren')
						if error_flag == False:
							Utils.tools_log('\n\n\n\nwm.pop_stack()......','3play_test_pop_stack')
							Utils.tools_log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
							return wm.pop_stack()
						elif error_flag == True:
							Utils.tools_log('\n\n\n\nseren_error_flag.......SLEEP......','play_test_pop_stack')
							xbmc.sleep(2500)
			Utils.tools_log('return......','play_test_pop_stack')
			return


		elif info == 'test_route':
			#from resources.lib.con_man_fix import list_and_select_wifi
			#list_and_select_wifi()
			from resources.lib import library
			library.trakt_watched_movies()
			return


		elif info == 'setup_trakt_watched':
			Utils.show_busy()
			from resources.lib import library
			library.trakt_watched_tv_shows_full()
			Utils.tools_log('trakt_watched_tv_shows_full')
			library.trakt_watched_movies_full()
			Utils.tools_log('trakt_watched_movies_full')
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
				Utils.tools_log({'rd_player_path_in': rd_player_path_in, 'rd_player_path_out': rd_player_path_out})
			if xbmcvfs.exists(rd_player_path_out) and RD_player == 'true':
				shutil.copyfile(rd_player_path_in, rd_player_path_out)
				Utils.tools_log({'rd_player_path_in': rd_player_path_in, 'rd_player_path_out': rd_player_path_out})
			if not xbmcvfs.exists(rd_player_path_out2) and RD_player == 'true':
				shutil.copyfile(rd_player_path_in2, rd_player_path_out2)
				Utils.tools_log({'rd_player_path_in': rd_player_path_in2, 'rd_player_path_out': rd_player_path_out2})
			if xbmcvfs.exists(rd_player_path_out2) and RD_player == 'true':
				shutil.copyfile(rd_player_path_in2, rd_player_path_out2)
				Utils.tools_log({'rd_player_path_in': rd_player_path_in2, 'rd_player_path_out': rd_player_path_out2})
			if not xbmcvfs.exists(rd_player_path_out3) and RD_player == 'true':
				shutil.copyfile(rd_player_path_in3, rd_player_path_out3)
				Utils.tools_log({'rd_player_path_in3': rd_player_path_in3, 'rd_player_path_out3': rd_player_path_out3})
			if xbmcvfs.exists(rd_player_path_out3) and RD_player == 'true':
				shutil.copyfile(rd_player_path_in3, rd_player_path_out3)
				Utils.tools_log({'rd_player_path_in3': rd_player_path_in3, 'rd_player_path_out3': rd_player_path_out3})

			if not xbmcvfs.exists(rd_bluray_player_path_out) and RD_bluray_player == 'true':
				shutil.copyfile(rd_bluray_player_path_in, rd_bluray_player_path_out)
				Utils.tools_log({'rd_bluray_player_path_in': rd_bluray_player_path_in, 'rd_bluray_player_path_out': rd_bluray_player_path_out})
			if xbmcvfs.exists(rd_bluray_player_path_out) and RD_bluray_player == 'true':
				shutil.copyfile(rd_bluray_player_path_in, rd_bluray_player_path_out)
				Utils.tools_log({'rd_bluray_player_path_in': rd_bluray_player_path_in, 'rd_bluray_player_path_out': rd_bluray_player_path_out})
			if not xbmcvfs.exists(rd_bluray_player2_path_out) and RD_bluray_player2 == 'true':
				shutil.copyfile(rd_bluray_player2_path_in, rd_bluray_player2_path_out)
				Utils.tools_log({'rd_bluray_player2_path_in': rd_bluray_player2_path_in, 'rd_bluray_player2_path_out': rd_bluray_player2_path_out})
			if xbmcvfs.exists(rd_bluray_player2_path_out) and RD_bluray_player2 == 'true':
				shutil.copyfile(rd_bluray_player2_path_in, rd_bluray_player2_path_out)
				Utils.tools_log({'rd_bluray_player2_path_in': rd_bluray_player2_path_in, 'rd_bluray_player2_path_out': rd_bluray_player2_path_out})
			Utils.hide_busy()

		elif info == 'open_settings':
			xbmc.executebuiltin('Addon.OpenSettings(%s)' % addon_ID())
			Utils.hide_busy()

		elif info == 'open_settings_magneto_scrapers':
			xbmc.executebuiltin('Addon.OpenSettings(script.module.magneto)')
			Utils.hide_busy()

		elif info == 'open_settings_coco_scrapers':
			xbmc.executebuiltin('Addon.OpenSettings(script.module.cocoscrapers)')
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
				Utils.tools_log({'fen_player_1_in': fen_player_1_out, 'fen_player_1_out': fen_player_1_out})
			if not xbmcvfs.exists(fen_player_2_out):
				shutil.copyfile(fen_player_2_in, fen_player_2_out)
				Utils.tools_log({'fen_player_2_in': fen_player_2_out, 'fen_player_2_out': fen_player_2_out})

			Utils.hide_busy()

		elif info == 'install_latest_fen_light':
			Utils.show_busy()

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
			Utils.tools_log(json.dumps(payload))
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

				from resources.lib.TheMovieDB import get_imdb_list_ids
				from resources.lib.TheMovieDB import get_imdb_watchlist_items
				movies = get_imdb_list_ids(list_str,limit=limit)
				if list_script == 'False':
					return get_imdb_watchlist_items(movies=movies,limit=limit)
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


		#elif info == 'string':
		#	resolve_url(params.get('handle'))
		#	xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
		#	dialog = xbmcgui.Dialog()
		#	if params.get('type', '') == 'movie':
		#		moviesearch = dialog.input('MovieSearch')
		#		xbmc.executebuiltin('Skin.SetString(MovieSearch,%s)' % moviesearch)
		#		xbmc.executebuiltin('Container.Refresh')
		#	elif params.get('type', '') == 'tv':
		#		showsearch = dialog.input('ShowSearch')
		#		xbmc.executebuiltin('Skin.SetString(ShowSearch,%s)' % showsearch)
		#		xbmc.executebuiltin('Container.Refresh')
		#	elif params.get('type', '') == 'youtube':
		#		youtubesearch = dialog.input('YoutubeSearch')
		#		xbmc.executebuiltin('Skin.SetString(YoutubeSearch,%s)' % youtubesearch)
		#		xbmc.executebuiltin('Container.Refresh')
		#	xbmcgui.Window(10000).clearProperty('infodialogs.active')

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
					Utils.tools_log(e)
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
			Utils.tools_log(msg)

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
			Utils.tools_log('run_downloader___','run_downloader')
			return getSources.run_downloader(magnet_list, download_path)
			
		elif info == 'stop_downloader':
			Utils.hide_busy()
			stop_downloader = xbmcaddon.Addon(addon_ID()).getSetting('magnet_list').replace('magnet_list.txt','stop_downloader')
			open(stop_downloader, 'w')
			Utils.tools_log('stop_downloader__','stop_downloader')
	
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
				else:
					log_message = str(str('%s | %s | %s' % (new_line['download_type'].upper(), unquote(new_line['file_name']), unquote(new_line['release_title']))))+str(idx+1)+'_KEEP_DOWNLOAD'
					Utils.tools_log(log_message)
					file1 = open(magnet_list, "a") 
					file1.write(str(line))
					file1.write("\n")
					file1.close()
					idx = idx + 1
			Utils.hide_busy()


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
				Utils.tools_log('setup_favourites')
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
				Utils.tools_log('patch_seren_a4k')
				file1 = open(file_path, 'w')
				file1.writelines(new_file)
				file1.close()
			Utils.hide_busy()

		elif info == 'patch_tmdb_helper':
			Utils.show_busy()
			patch_tmdbh()
			Utils.hide_busy()

def do_patch(patch_file_path, patch_lines, log_addon_name, start_line, end_line):
	file_path = patch_file_path
	Utils.tools_log(file_path,log_addon_name)
	file1 = open(file_path, 'r')
	lines = file1.readlines()
	new_file = ''
	update_flag = False
	line_update = patch_lines
	keep_update = False
	end_line_match = False
	for idx, line in enumerate(lines):
		if '## PATCH' in str(line):
			update_flag = False
			log_message = 'ALREADY_PATCHED_%s_' % (log_addon_name)
			Utils.tools_log(log_message)
			break

		if start_line in str(line):
			new_file = new_file + line_update
			update_flag = True
			keep_update = True
		elif update_flag == True and keep_update == True:
			if end_line in str(line):
				keep_update = False
				end_line_match = True
		elif keep_update == False:
			new_file = new_file + line
	file1.close()
	if update_flag and end_line_match == True:
		file1 = open(file_path, 'w')
		file1.writelines(new_file)
		file1.close()
		log_message = '%s_PATCH_%s' % (file_path,log_addon_name)
		Utils.tools_log(log_message)
	elif update_flag and end_line_match == False:
		log_message = 'NO_PATCH_%s_PATCH_%s__%s' % (file_path,log_addon_name,'END_LINE_NOT_FOUND')


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

	xbmc.sleep(250)  # found originally that it wasn't written yet
	with open(logfn, 'r') as f:
		f.seek(0, 2)           # seek @ EOF
		fsize = f.tell()        # Get Size
		f.seek(max(fsize - 9024, 0), 0)  # Set pos @ last n chars
		lines = f.readlines()       # Read to end
	lines = lines[-15:]    # Get last 10 lines

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
	Utils.tools_log('STARTING===>auto_clean_cache_seren_downloader')
	path = xbmcvfs.translatePath('special://profile/addon_data/'+str('plugin.video.seren_downloader')+'/')
	if days==None:
		days = -30
	else:
		days = int(days)*-1

	today = datetime.datetime.today()#gets current time
	if not xbmcvfs.exists(path):
		return
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
						Utils.tools_log(str(target)+'===>DELETE')
						os.remove(target)

def auto_clean_cache(days=None):
	Utils.tools_log('STARTING===>auto_clean_cache')
	try:
		Utils.db_delete_expired(connection=Utils.db_con)
	except:
		xbmc.sleep(2*1000)
		try:
			Utils.tools_log('EXCEPTION__1_auto_clean_cache')
			Utils.db_delete_expired(connection=Utils.db_con)
		except:
			Utils.tools_log('EXCEPTION__2_auto_clean_cache')
			pass
	Utils.tools_log('FINISH===>auto_clean_cache')
	#Utils.db_con.close()
	#auto_clean_cache_seren_downloader(days=30)

def auto_library():
	Utils.hide_busy()
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
		Utils.tools_log('refresh_recently_added')
		refresh_recently_added()
		Utils.tools_log('trakt_calendar_list')
		if not xbmc.Player().isPlaying():
			xbmcgui.Dialog().notification(heading='Startup Tasks', message='trakt_calendar_list', icon=icon_path(),time=1000,sound=False)
		trakt_calendar_list()
	if not xbmc.Player().isPlaying() and (library_tv_sync or library_movies_sync):
		xbmcgui.Dialog().notification(heading='Startup Tasks', message='Startup Complete!', icon=icon_path(), time=1000,sound=False)

	if library_movies_sync:
		Utils.tools_log('UpdateLibrary_MOVIES')
		xbmc.executebuiltin('UpdateLibrary(video, {})'.format(basedir_movies_path()))
	if library_tv_sync:
		Utils.tools_log('UpdateLibrary_TV')
		xbmc.executebuiltin('UpdateLibrary(video, {})'.format(basedir_tv_path()))
	return
	rss_1_enabled = xbmcaddon.Addon(addon_ID()).getSetting('rss.1')
	rss_2_enabled = xbmcaddon.Addon(addon_ID()).getSetting('rss.2')
	rss_3_enabled = xbmcaddon.Addon(addon_ID()).getSetting('rss.3')
	rss_4_enabled = xbmcaddon.Addon(addon_ID()).getSetting('rss.4')
	if rss_1_enabled == 'true' or rss_2_enabled == 'true' or rss_3_enabled == 'true'  or rss_4_enabled == 'true':

		from a4kscrapers_wrapper import get_meta
		Utils.tools_log('get_meta.get_rss_cache()')
		get_meta.get_rss_cache()


def context_info():
	import json
	base = 'RunScript('+str(addon_ID())+',info='

	json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Title", "Player.Filename","Player.Filenameandpath", "VideoPlayer.MovieTitle", "VideoPlayer.TVShowTitle", "VideoPlayer.DBID", "VideoPlayer.DBTYPE", "VideoPlayer.Duration", "VideoPlayer.Season", "VideoPlayer.Episode", "VideoPlayer.DBID", "VideoPlayer.Year", "VideoPlayer.Rating", "VideoPlayer.mpaa", "VideoPlayer.Studio", "VideoPlayer.VideoAspect", "VideoPlayer.Plot", "VideoPlayer.RatingAndVotes", "VideoPlayer.Genre", "VideoPlayer.LastPlayed", "VideoPlayer.IMDBNumber", "ListItem.DBID", "Container.FolderPath", "Container.FolderName", "Container.PluginName", "ListItem.TVShowTitle", "ListItem.FileNameAndPath"]}, "id":1}')
	json_object  = json.loads(json_result)

	dbid = json_object['result']['VideoPlayer.DBID']
	type = json_object['result']['VideoPlayer.DBTYPE']
	episode = json_object['result']['VideoPlayer.Episode']
	Season = json_object['result']['VideoPlayer.Season']
	remote_id = None
	IMDBNumber = json_object['result']['VideoPlayer.IMDBNumber']

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
	Utils.tools_log(params)
	if infos:
		start_info_actions(infos, params)


def context_info2():
	import json
	base = 'RunScript('+str(addon_ID())+',info='

	json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["ListItem.Title", "ListItem.Label",  "ListItem.MovieTitle",    "ListItem.DBTYPE",  "ListItem.Season", "ListItem.Episode", "ListItem.Year",  "ListItem.IMDBNumber", "ListItem.DBID",   "ListItem.TVShowTitle", "ListItem.FileNameAndPath", "ListItem.UniqueID(tmdb)", "ListItem.UniqueID(imdb)", "Container.ListItem.UniqueID(imdb)"]}, "id":1}')
	json_object  = json.loads(json_result)

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

	IMDBNumber = json_object['result']['ListItem.IMDBNumber']
	if (IMDBNumber == '' or IMDBNumber == None):
		IMDBNumber = imdb

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

	elif type == 'tvshow':
		infos.append('extendedtvinfo')
		params['dbid'] = dbid
		params['id'] = remote_id
		params['imdb_id'] = IMDBNumber
		params['name'] = TVShowTitle

	elif type == 'season':
		infos.append('seasoninfo')
		params['dbid'] = dbid
		params['id'] = remote_id
		params['tvshow'] = TVShowTitle
		params['season'] = Season

	elif type == 'episode':
		infos.append('extendedepisodeinfo')
		params['dbid'] = dbid
		params['id'] = remote_id
		params['tvshow'] = TVShowTitle
		params['season'] = Season
		params['episode'] = episode

	elif type in ['actor', 'director']:
		infos.append('extendedactorinfo')
		params['name'] = Label
	Utils.tools_log(params,'context_info2')
	if infos:
		start_info_actions(infos, params)


def patch_tmdbh():
	from pathlib import Path
	touch_file = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib') , 'PATCH')
	if os.path.exists(touch_file):
		Utils.tools_log('TMDBH_already_patched')
		return 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','player') , 'players.py')
	if not os.path.exists(file_path):
		file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'lib','player') , 'players.py')
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
	first_line = '            for idx, i in enumerate(players_list): '
	last_line = 'return Dialog().select(header, players, useDetails=detailed)'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','player') , 'select.py')
	line_update = '''    def select_player(players_list, header=None, detailed=True, index=False, players=None):
        """ Select from a list of players """
        if 'episode' in str(players[0]['mode']):
            db_type = 'episode'
        else:
            db_type = 'movie'
        for idx, i in enumerate(players): ## PATCH
            if 'auto_cloud' in str(i['name']).lower() and db_type != 'movie': ## PATCH
                auto_var = idx ## PATCH
                break ## PATCH
            if 'Auto_Torr_Scrape' in str(i['name']) and db_type == 'movie': ## PATCH
                auto_var = idx ## PATCH
                break ## PATCH
        x = Dialog().select(header or get_localized(32042), [i.listitem for i in players_list],useDetails=detailed, autoclose=30000, preselect=auto_var)
        return x if index or x == -1 else players_list[x].posx

    def get_player(self, x):
        player = self.players_list[x]
        player['idx'] = x
        return player

    def select(self, header=None, detailed=True):
        """ Select a player from the list """
        x = self.select_player(self.players_generated_list, header=header, detailed=detailed, players=self.players)
        return {} if x == -1 else self.get_player(x)
'''
	first_line = '    def select_player(players_list, header=None, detailed=True, index=False):'
	last_line = '        return {} if x == -1 else self.get_player(x)'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','script','method') , 'maintenance.py')
	line_update = '''    def vacuum(self, force=False):  ##PATCH
        import time
        if not force and self.is_next_vacuum == False:
            return
        if time.time() < self.next_vacuum:
            return
        self.set_next_vacuum()
        from tmdbhelper.lib.addon.logger import TimerFunc
        from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        with TimerFunc('Vacuuming databases:', inline=True):
            ItemDetailsDatabase().execute_sql("VACUUM")
            FindQueriesDatabase().execute_sql("VACUUM")

    def delete_legacy_folders(self, force=False): ##PATCH
'''
	first_line = '    def vacuum(self, force=False):'
	last_line = '    def delete_legacy_folders(self, force=False):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','api','trakt') , 'authenticator.py')
	line_update = '''    def poller(self): ## PATCH
        import xbmc
        while True:
            xbmc.log(str(self.user_code)+'===>PHIL', level=xbmc.LOGINFO)
            if self.xbmc_monitor.abortRequested(): ## PATCH
'''
	first_line = '    def poller(self):'
	last_line = '            if self.xbmc_monitor.abortRequested():'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	Path(touch_file).touch()
	return

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','script','method') , 'trakt.py')
	line_update = '''def authenticate_trakt(**kwargs): ## PATCH
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    TraktAPI(force=True)
    invalidate_trakt_sync('all', notification=False)

def authorize_trakt(**kwargs):
    import xbmc
    from tmdbhelper.lib.addon.logger import kodi_log
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from tmdbhelper.lib.api.trakt.token import TraktStoredAccessToken
    trakt_api = TraktAPI(force=False)
    TraktStoredAccessToken(trakt_api).winprop_traktusertoken = ''
    refresh_token = TraktStoredAccessToken(trakt_api).refresh_token
    response = trakt_api.set_authorisation_token(refresh_token)
    if response != {}:
        xbmc.log(str('Trakt authenticated successfully!')+'===>PHIL', level=xbmc.LOGINFO)
    from tmdbhelper.lib.files.futils import json_dumps as data_dumps
    trakt_api.user_token.value = data_dumps(response)
    from tmdbhelper.lib.api.api_keys.tokenhandler import TokenHandler
    USER_TOKEN = TokenHandler('trakt_token', store_as='setting')
    TraktStoredAccessToken(trakt_api).winprop_traktusertoken = USER_TOKEN.value
    TraktStoredAccessToken(trakt_api).confirm_authorization()
    return

def revoke_trakt(**kwargs): ## PATCH
'''
	first_line = 'def authenticate_trakt(**kwargs):'
	last_line = 'def revoke_trakt(**kwargs):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','script') , 'router.py')
	line_update = '''        'authenticate_trakt': ## PATCH
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'authenticate_trakt')(**kwargs),
        'authorize_trakt':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'authorize_trakt')(**kwargs),
        'revoke_trakt': ## PATCH
'''
	first_line = "        'authenticate_trakt':"
	last_line = "        'revoke_trakt':" 
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','monitor') , 'player.py')
	line_update = '''    def onAVStarted(self):  ## PATCH
        import xbmc
        xbmc.sleep(5*1000)
        try: self.get_playingitem()
        except: return

    def onPlayBackStarted(self):
        import xbmc
        xbmc.sleep(5*1000)
        try: self.get_playingitem()
        except: return

    def onAVChange(self):
        import xbmc
        xbmc.sleep(5*1000)
        try: self.get_playingitem()
        except: return

    def onPlayBackEnded(self):  ## PATCH
'''
	first_line = '    def onAVStarted(self):'
	last_line = '    def onPlayBackEnded(self):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 


	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','api', 'trakt') , 'api.py')
	line_update = '''    def access_token(self):   ## PATCH
        #if not self.authenticator.access_token:
        #    return
        #if not self.authenticator.trakt_stored_access_token.has_valid_token:
        #    self.refresh_authenticator()
        #return self.authenticator.access_token
        if not self.authenticator.trakt_stored_access_token.has_valid_token:
            self.refresh_authenticator()
        from tmdbhelper.lib.api.api_keys.tokenhandler import TokenHandler
        from tmdbhelper.lib.files.futils import json_loads as data_loads
        USER_TOKEN = TokenHandler('trakt_token', store_as='setting')
        try: access_token = data_loads(USER_TOKEN.value)['access_token']
        except: return None
        if access_token != self.authenticator.access_token:
            #self.authenticator.access_token = access_token
            from tmdbhelper.lib.api.trakt.token import TraktStoredAccessToken
            TraktStoredAccessToken(self).on_success()
            self.refresh_authenticator()
        return access_token

    @cached_property
    def authenticator(self):  ## PATCH
'''
	first_line = '    def access_token(self):'
	last_line = '    def authenticator(self):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','api', 'trakt') , 'token.py')
	line_update = '''    def update_stored_authorization(self):  ## PATCH
        test_user_token = self.winprop_traktusertoken
        self.trakt_api.user_token.value = self.winprop_traktusertoken = data_dumps(self.stored_authorization)
        if test_user_token != self.trakt_api.user_token.value and len(test_user_token) > 4:
            self.trakt_api.user_token.value = data_dumps(test_user_token)
            self.stored_authorization = data_dumps(test_user_token)
            self.winprop_traktusertoken = data_dumps(test_user_token)

    @property
    def winprop_traktusertoken(self):  ## PATCH
'''
	first_line = '    def update_stored_authorization(self):'
	last_line = '    def winprop_traktusertoken(self):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	Path(touch_file).touch()
	return

def estuary_fix():
	#osmc_home = '/usr/share/kodi/addons/skin.estuary/xml/Home.xml'
	import os
	osmc_home = xbmcvfs.translatePath('special://skin/xml/Home.xml')
	estuary_home_fix2 = xbmcvfs.translatePath(Utils.ADDON_PATH + '/estuary_home_fix2.py')
	command = "sudo python %s '%s'" % (estuary_home_fix2, osmc_home)
	Utils.tools_log(command)
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
