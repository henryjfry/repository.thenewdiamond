import os, shutil
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
from resources.lib import Utils
from resources.lib.WindowManager import wm
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib.library import icon_path

from urllib.parse import quote, urlencode, quote_plus, unquote, unquote_plus
import time

from resources.lib.Utils import tools_log as log
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


		if info == 'generate_m3u_xml':
			from xtream2m3u_run import generate_m3u
			from xtream2m3u_run import generate_xmltv
			generate_m3u()
			generate_xmltv()
			Utils.hide_busy()
			return

		if info == 'setup_iptv_simple_settings':
			from xtream2m3u_run import setup_iptv_simple_settings
			setup_iptv_simple_settings()
			Utils.hide_busy()
			return

		if info == 'output_lists_pastebin':
			from xtream2m3u_run import output_lists_pastebin
			url = output_lists_pastebin()
			dialog = xbmcgui.Dialog()
			dialog.ok('PasteBin Channel List + EPG Group List', url)
			Utils.hide_busy()
			return

		if info == 'save_channel_order':
			from xtream2m3u_run import save_channel_order
			dialog = xbmcgui.Dialog()
			url = dialog.input('Enter Channel Order list Pastebin URL', default='https://pastebin.com/',  type=xbmcgui.INPUT_ALPHANUM)
			save_channel_order(url)
			Utils.hide_busy()
			return

		if info == 'save_allowed_groups':
			from xtream2m3u_run import save_allowed_groups
			dialog = xbmcgui.Dialog()
			url = dialog.input('Enter Allowed Groups list Pastebin URL', default='https://pastebin.com/',  type=xbmcgui.INPUT_ALPHANUM)
			save_allowed_groups(url)
			Utils.hide_busy()
			return

		if info == 'delete_db_expired':
			Utils.db_delete_expired(Utils.db_con)
			Utils.hide_busy()
			return

		if info == 'clear_db':
			table_name = params.get('table_name', False)
			Utils.clear_db(Utils.db_con,table_name)
			Utils.hide_busy()
			return

		if info == 'getplayingfile':
			xbmc.log(str(xbmc.Player().getPlayingFile())+'===>OPENINFO', level=xbmc.LOGINFO)
			Utils.hide_busy()
			return

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

		elif info == 'test_movies2':
			Utils.show_busy()
			from resources.lib.TheMovieDB import get_vod_alltv
			search_str = get_vod_alltv()
			Utils.tools_log(search_str[-1])
			Utils.hide_busy()

		elif info == 'service2':
			Utils.show_busy()
			import service2
			Utils.hide_busy()

		elif info == 'xtream2m3u_run':
			Utils.show_busy()
			Utils.hide_busy()
			#from traceback import format_exc
			#from resources.lib.xtream2m3u_run import app as flask_app
			from xtream2m3u_run import start
			#Utils.tools_log('STARTING__SERVER')
			#flask_app.run(debug=False, host='0.0.0.0')
			start()
			Utils.hide_busy()
			return
			#import os
			#Utils.tools_log(os.getcwd())
			#from resources.lib.xtream2m3u_run import generate_m3u
			#generate_m3u()
			#exit()
			#from resources.lib.xtream2m3u_run import app as flask_app
			#from multiprocessing import Process
			#import socket
			#socket.setdefaulttimeout(120) # seconds
			#server = Process(target=flask_app.run(debug=False, host='0.0.0.0'))
			#server.start()
			##flask_app.run(debug=False, host='0.0.0.0')


		elif info == 'allmovies2':
			#kodi-send --action='RunPlugin(plugin://'+str(addon_ID())+'/?info=trakt_watched&trakt_type=movie&script=True)'
			#kodi-send --action='RunPlugin(plugin://'+str(addon_ID())+'/?info=trakt_watched&trakt_type=tv&script=True)'
			#kodi-send --action='RunPlugin(plugin://'+str(addon_ID())+'/?info=trakt_coll&trakt_type=movie&script=True)'
			#kodi-send --action='RunPlugin(plugin://'+str(addon_ID())+'/?info=trakt_coll&trakt_type=tv&script=True)'
			Utils.show_busy()
			#log(addon_ID())
			trakt_type = 'movie'
			if info == 'allmovies2':
				#from resources.lib.TheMovieDB import get_vod_data
				#movies = get_vod_data(action= 'get_vod_streams' ,cache_days=1) 
				from resources.lib.TheMovieDB import get_vod_allmovies
				search_str = get_vod_allmovies()
				#search_str = []
				trakt_label = 'VOD Movies'
				#for i in movies:
				#	#if len(i.get('tmdb','0')) == 0:
				#	#	log(i)
				#	full_url = '%s%s/%s/%s/%s.%s' % (Utils.xtreme_codes_server_path,i['stream_type'],Utils.xtreme_codes_username,Utils.xtreme_codes_password,str(i['stream_id']),str(i['container_extension']))
				#	search_str.append({'type': 'movie','title':i['name'],'tmdb':i['tmdb'], 'full_url': full_url, 'stream_type': i['stream_type'],'stream_icon': i['stream_icon'], 'rating': i['rating'],'category_ids': i['category_ids']})

				#Utils.tools_log(search_str)
				if keep_stack == None or keep_stack == False:
					wm.window_stack_empty()
				return wm.open_video_list(mode='allmovies2', listitems=[], search_str=search_str, media_type=trakt_type, filter_label=trakt_label)

		elif info == 'allmovies':
			wm.window_stack_empty()
			wm.open_video_list(media_type='movie',mode='filter')

		elif info == 'alltvshows2':
			Utils.show_busy()
			#log(addon_ID())
			trakt_type = 'tv'
			if info == 'alltvshows2':
				from resources.lib.TheMovieDB import get_vod_alltv
				search_str = get_vod_alltv()
				#search_str = []
				trakt_label = 'VOD TV'
				#Utils.tools_log(search_str)
				if keep_stack == None or keep_stack == False:
					wm.window_stack_empty()
				return wm.open_video_list(mode='alltvshows2', listitems=[], search_str=search_str, media_type=trakt_type, filter_label=trakt_label)

		elif info == 'alltvshows':
			wm.window_stack_empty()
			wm.open_video_list(media_type='tv',mode='filter')

		elif info == 'search_menu':
			search_str = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
			wm.window_stack_empty()
			return wm.open_video_list(search_str=search_str, mode='search')


		elif info == 'setmagnet_list':
			Utils.show_busy()
			new_location = xbmcgui.Dialog().browse(0, "Select Magnet Path Location", "video", defaultt=Utils.ADDON_DATA_PATH)
			new_location = os.path.join(new_location, 'magnet_list.txt')
			xbmcaddon.Addon(addon_ID()).setSetting('magnet_list', new_location)
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
			import vod_main
			stop_downloader = xbmcaddon.Addon(addon_ID()).getSetting('magnet_list').replace('magnet_list.txt','stop_downloader')
			if os.path.exists(stop_downloader):
				os.remove(stop_downloader)

			magnet_list = xbmcaddon.Addon(addon_ID()).getSetting('magnet_list')
			download_path = xbmcaddon.Addon(addon_ID()).getSetting('download_path')
			xbmc.log(str('run_downloader___')+'run_downloader===>OPENINFO', level=xbmc.LOGINFO)
			return vod_main.run_downloader(magnet_list, download_path)
			
		elif info == 'stop_downloader':
			Utils.hide_busy()
			#filename = "stop_downloader"
			stop_downloader = xbmcaddon.Addon(addon_ID()).getSetting('magnet_list').replace('magnet_list.txt','stop_downloader')
			open(stop_downloader, 'w')
			xbmc.log(str('stop_downloader__')+'stop_downloader===>OPENINFO', level=xbmc.LOGINFO)
			
	
		elif info == 'manage_download_list':
			magnet_list = xbmcaddon.Addon(addon_ID()).getSetting('magnet_list')
			from tools import read_all_text
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


		elif info == 'reopen_window':
			reopen_window()

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


		elif info == 'setup_trakt_watched':
			Utils.show_busy()
			from resources.lib import library
			library.trakt_watched_tv_shows_full()
			xbmc.log(str('trakt_watched_tv_shows_full')+'===>OPEN_INFO', level=xbmc.LOGINFO)
			library.trakt_watched_movies_full()
			xbmc.log(str('trakt_watched_movies_full')+'===>OPEN_INFO', level=xbmc.LOGINFO)
			Utils.hide_busy()

		elif info == 'open_settings':
			xbmc.executebuiltin('Addon.OpenSettings(%s)' % addon_ID())
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

		elif info == 'search_string':
			search_str = params['str']
			wm.window_stack_empty()
			return wm.open_video_list(search_str=search_str, mode='search')


		elif info == 'afteradd':
			return Utils.after_add(params.get('type'))


		elif info == 'playmovie':
			resolve_url(params.get('handle'))
			Utils.get_kodi_json(method='Player.Open', params='{"item": {"movieid": %s}, "options": {"resume": true}}' % params.get('dbid'))

		elif info == 'playepisode':
			resolve_url(params.get('handle'))
			Utils.get_kodi_json(method='Player.Open', params='{"item": {"episodeid": %s}, "options": {"resume": true}}' % params.get('dbid'))

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

		elif info == 'play_vod_player':
			from resources.lib.VideoPlayer import PLAYER
			#kodi-send --action="RunScript(script.xtreme_vod,info=prepare_play_VOD_movie,type=tv,show_title=Star Trek: Enterprise,show_season=4,show_episode=20,tmdb=314)"
			#kodi-send --action="RunScript(script.extendedinfo,info=prepare_play_VOD_movie,type=movie,movie_year=,movie_title=Elf,tmdb=)"
			xbmcgui.Window(10000).setProperty('script.xtreme_vod.ResolvedUrl', 'suppress_reopen_window')
			if params.get('type') == 'tv':
				PLAYER.prepare_play_VOD_episode(tmdb = params.get('tmdb'), series_id=None, search_str = None,episode=params.get('show_episode'), season=params.get('show_season'), window=False)
			elif params.get('type') == 'movie':
				PLAYER.prepare_play_VOD_movie(tmdb = params.get('tmdb'), title = params.get('movie_title'), stream_id=None, search_str = None, window=False)
				#movie_year = params.get('movie_year')



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

def auto_clean_cache(days=None):
	xbmc.log('STARTING===>auto_clean_cache', level=xbmc.LOGINFO)
	Utils.db_delete_expired(connection=Utils.db_con)
	#Utils.db_con.close()
	#auto_clean_cache_seren_downloader(days=30)

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

	if library_movies_sync:
		xbmc.log(str('UpdateLibrary_MOVIES')+'===>OPEN_INFO', level=xbmc.LOGFATAL)
		xbmc.executebuiltin('UpdateLibrary(video, {})'.format(basedir_movies_path()))
	if library_tv_sync:
		xbmc.log(str('UpdateLibrary_TV')+'===>OPEN_INFO', level=xbmc.LOGFATAL)
		xbmc.executebuiltin('UpdateLibrary(video, {})'.format(basedir_tv_path()))
	return

