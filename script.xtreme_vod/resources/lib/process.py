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

		if info == 'select_pvr_client':
			client = select_pvr_client()
			if client:
				xbmc.executebuiltin('Dialog.Close(all,true)')
				xbmcaddon.Addon(addon_ID()).setSetting('pvr_client', client)
				Utils.tools_log(client)
			xbmcgui.Dialog().notification("pvr_client_UPDATED",client)
			Utils.hide_busy()
			return

		if info == 'reset_stuff':
			reset_stuff()
			Utils.hide_busy()
			return

		if info == 'm3u_ts_m3u8':
			from xtream2m3u_run import m3u_ts_m3u8
			m3u_ts_m3u8()
			Utils.hide_busy()
			return

		if info == 'generate_m3u_xml':
			from xtream2m3u_run import generate_m3u
			from xtream2m3u_run import generate_xmltv
			Utils.show_busy()
			generate_m3u()
			generate_xmltv()
			Utils.hide_busy()
			return

		if info == 'get_all_vod':
			from resources.lib.TheMovieDB import get_vod_data
			movies = get_vod_data(action= 'get_vod_streams' ,cache_days=1) 
			vod_movies = []
			for i in movies:
				vod_movies.append(i['name'])
			movies = get_vod_data(action= 'get_series' ,cache_days=1) 
			vod_tv = []
			for i in movies:
				vod_tv.append(i['name'])
			Utils.tools_log(vod_movies)
			Utils.tools_log(vod_tv)
			Utils.hide_busy()
			return

		if info == 'test':
			Utils.tools_log('ResetEPG')
			Utils.ResetEPG()
			Utils.hide_busy()
			return

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

		if info == 'setup_iptv_simple_settings':
			from xtream2m3u_run import setup_iptv_simple_settings
			Utils.show_busy()
			setup_iptv_simple_settings()
			Utils.hide_busy()
			return

		if info == 'output_curr_channels_pastebin':
			from xtream2m3u_run import output_curr_channels_pastebin
			url = output_curr_channels_pastebin()
			dialog = xbmcgui.Dialog()
			dialog.ok('PasteBin Channel List + EPG Group List', url)
			Utils.tools_log(url)
			Utils.hide_busy()
			return

		if info == 'output_lists_pastebin':
			from xtream2m3u_run import output_lists_pastebin
			url = output_lists_pastebin()
			dialog = xbmcgui.Dialog()
			dialog.ok('PasteBin Channel List + EPG Group List', url)
			Utils.tools_log(url)
			Utils.hide_busy()
			return

		if info == 'save_channel_order':
			from xtream2m3u_run import save_channel_order
			dialog = xbmcgui.Dialog()
			url = dialog.input('Enter Channel Order list Pastebin URL', 'https://pastebin.com/',  type=xbmcgui.INPUT_ALPHANUM)
			Utils.show_busy()
			if url != '' and len(url ) > len('https://pastebin.com/'):
				save_channel_order(url)
			Utils.hide_busy()
			return

		if info == 'save_allowed_groups':
			from xtream2m3u_run import save_allowed_groups
			dialog = xbmcgui.Dialog()
			url = dialog.input('Enter Allowed Groups list Pastebin URL', 'https://pastebin.com/',  type=xbmcgui.INPUT_ALPHANUM)
			Utils.show_busy()
			if url != '' and len(url ) > len('https://pastebin.com/'):
				save_allowed_groups(url)
			Utils.hide_busy()
			return

		if info == 'save_exclude_channels':
			from xtream2m3u_run import save_exclude_channels
			dialog = xbmcgui.Dialog()
			url = dialog.input('Enter Exclude Channels list Pastebin URL', 'https://pastebin.com/',  type=xbmcgui.INPUT_ALPHANUM)
			Utils.show_busy()
			if url != '' and len(url ) > len('https://pastebin.com/'):
				save_exclude_channels(url)
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
			media_type = 'movie'
			if info == 'allmovies2':
				from resources.lib.TheMovieDB import get_vod_allmovies
				search_str = get_vod_allmovies()
				filter_label = 'VOD Movies'

				if keep_stack == None or keep_stack == False:
					wm.window_stack_empty()
				return wm.open_video_list(mode='allmovies2', listitems=[], search_str=search_str, media_type=media_type, filter_label=filter_label)

		elif info == 'alltvshows2' or info == 'alltv2':
			Utils.show_busy()
			#log(addon_ID())
			media_type = 'tv'
			if info == 'alltvshows2' or info == 'alltv2':
				from resources.lib.TheMovieDB import get_vod_alltv
				search_str = get_vod_alltv()
				filter_label = 'VOD TV'
				if keep_stack == None or keep_stack == False:
					wm.window_stack_empty()
				return wm.open_video_list(mode='alltvshows2', listitems=[], search_str=search_str, media_type=media_type, filter_label=filter_label)


		elif info == 'calendar_eps':
			search_str = 'Trakt Episodes/Movies in progress'
			from resources.lib.library import trakt_calendar_eps
			#type = 'movie'
			movies = trakt_calendar_eps()
			wm.window_stack_empty()
			trakt_label = 'Trakt Calendar Episodes'
			return wm.open_video_list(mode='trakt', listitems=[], search_str=movies, media_type='tv', filter_label=trakt_label)

		elif info == 'ep_movie_progress':
			search_str = 'Trakt Episodes/Movies in progress'
			from resources.lib.library import trakt_eps_movies_in_progress
			#type = 'movie'
			movies = trakt_eps_movies_in_progress()
			wm.window_stack_empty()
			trakt_label = 'Trakt Episodes/Movies in progress'
			return wm.open_video_list(mode='trakt', listitems=[], search_str=movies, media_type='movie', filter_label=trakt_label)

		elif info == 'trakt_watched':
			#kodi-send --action='RunPlugin(plugin://script.extendedinfo/?info=trakt_watched&trakt_type=movie&script=True)'
			#kodi-send --action='RunPlugin(plugin://script.extendedinfo/?info=trakt_watched&trakt_type=tv&script=True)'
			trakt_type = str(params['trakt_type'])
			Utils.show_busy()
			try: trakt_token = xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('trakt_token')
			except: trakt_token = None
			if not trakt_token:
				Utils.hide_busy()
				return
			trakt_script = 'True'
			if info == 'trakt_watched' and trakt_type == 'movie':
				from resources.lib.library import trakt_watched_movies
				movies = trakt_watched_movies()
				trakt_label = 'Trakt Watched Movies'
			elif info == 'trakt_watched' and trakt_type == 'tv':
				from resources.lib.library import trakt_watched_tv_shows
				movies = trakt_watched_tv_shows()
				trakt_label = 'Trakt Watched Shows'

			if keep_stack == None or keep_stack == False:
				wm.window_stack_empty()
			return wm.open_video_list(mode='trakt', listitems=[], search_str=movies, media_type=trakt_type, filter_label=trakt_label)

		elif info == 'search_title':
			search_str = params.get('search_text')
			wm.window_stack_empty()
			Utils.tools_log(search_str)
			return wm.open_video_list(search_str=search_str, mode='search')

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
			return reopen_window()

		elif info == 'play_test_call_pop_stack':
			log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			return wm.pop_stack()


		elif info == 'play_test_pop_stack':
			play_test_pop_stack()
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

		elif info == 'search_string':
			search_str = params['str']
			wm.window_stack_empty()
			return wm.open_video_list(search_str=search_str, mode='search')



		elif info == 'VOD_infodialog' or info == str(addon_ID_short()) + 'dialog':
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

		elif info == 'VOD_info' or info == str(addon_ID_short()):
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


		elif info == 'slideshow':
			resolve_url(params.get('handle'))
			window_id = xbmcgui.getCurrentwindow_id()
			window = xbmcgui.Window(window_id)
			itemlist = window.getFocus()
			num_items = itemlist.getSelectedPosition()
			for i in range(0, num_items):
				Utils.notify(item.getProperty('Image'))

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



		elif info == 'deletecache':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')
			xbmcgui.Window(10000).clearProperty('xtreme_vod_running')
			for rel_path in os.listdir(Utils.ADDON_DATA_PATH):
				path = os.path.join(Utils.ADDON_DATA_PATH, rel_path)
				try:
					if os.path.isdir(path):
						shutil.rmtree(path)
				except Exception as e:
					Utils.log(e)
			Utils.notify('Cache deleted')
			Utils.hide_busy()

		elif info == 'auto_clean_cache':
			#info=auto_clean_cache&days=10
			days = params.get('days')
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')
			xbmcgui.Window(10000).clearProperty('xtreme_vod_running')
			auto_clean_cache(days=days)
			Utils.notify('Cache deleted')
			Utils.hide_busy()

		elif info == 'setDownloadLocation':
			Utils.show_busy()
			new_location = xbmcgui.Dialog().browse(0, "Select Download Location", "video", defaultt=Utils.ADDON_DATA_PATH)
			xbmcaddon.Addon(addon_ID()).setSetting('DOWNLOAD_FOLDER', new_location)
			xbmcaddon.Addon(addon_ID()).setSetting('download_path', new_location)
			Utils.hide_busy()

		elif info == 'custom_favourites':
			Utils.show_busy()
			custom_favourites()
			Utils.hide_busy()

		elif info == 'setup_favourites':
			Utils.show_busy()
			setup_favourites()
			Utils.hide_busy()

		elif info == 'patch_tmdb_helper':
			Utils.show_busy()
			patch_tmdbh()
			Utils.hide_busy()


		elif info == 'setup_players':
			import os
			Utils.show_busy()
			tmdb_players_path = os.path.join(Utils.ADDON_DATA_PATH.replace('script.xtreme_vod','plugin.video.themoviedb.helper'),'players')
			player_path_in = xbmcvfs.translatePath(os.path.join(Utils.ADDON_PATH,'direct.xtreme_vod_player.json'))
			player_path_out = xbmcvfs.translatePath(os.path.join(tmdb_players_path,'direct.xtreme_vod_player.json'))
			
			import shutil
			if not xbmcvfs.exists(player_path_out):
				shutil.copyfile(player_path_in, player_path_out)
				Utils.tools_log({'player_path_in': player_path_in, 'player_path_out': player_path_out})

			Utils.hide_busy()

		elif info == 'xml_startup_process':
			from xtream2m3u_run import xml_startup_process
			xml_startup_process()


		elif info == 'iptv_simple_enable':
			Utils.addon_disable_reable(addonid = 'pvr.iptvsimple' , enabled=True)

	return 



def do_patch(patch_file_path, patch_lines, log_addon_name, start_line, end_line):
	file_path = patch_file_path
	if not xbmcvfs.exists(file_path):
		Utils.tools_log('NO_FILE!!!',file_path)
		return 
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
		#Utils.notify('Success', log_message)
	elif update_flag and end_line_match == False:
		log_message = 'NO_PATCH_%s_PATCH_%s__%s' % (file_path,log_addon_name,'END_LINE_NOT_FOUND')
		Utils.tools_log(log_message)
		#Utils.notify('Error', log_message)
	return 

def custom_favourites():
	dialog = xbmcgui.Dialog()
	url = dialog.input('Custom Favourite eg imdb_list,list=ls594490332,list_name=tv_movies', 'RunScript(script.xtreme_vod,info=',  type=xbmcgui.INPUT_ALPHANUM)
	if url == '' or url == '-1':
		return
	if not 'RunScript(script.xtreme_vod,info=' in str(url):
		file_path = 'RunScript(script.xtreme_vod,info=%s)' % (str(url))
	else:
		file_path = url + ')'
	
	if file_path[-2:] == '))':
		file_path = file_path[:-2] + ')'
	fave_name = dialog.input('FAVOURITE NAME', '',  type=xbmcgui.INPUT_ALPHANUM)
	if url == '' or url == '-1':
		fave_name = 'Custom Favourite'
	fav1_list = []
	fav1_list.append('	<favourite name="%s" thumb="special://home/addons/script.xtreme_vod/icon.png">%s</favourite>' % (str(fave_name),str(file_path)))

	file_path = xbmcvfs.translatePath('special://userdata/favourites.xml')
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
		Utils.tools_log('custom_favourites')
		file1 = open(file_path, 'w')
		file1.writelines(new_file)
		file1.close()
	Utils.notify('DONE', 'Restart Kodi to take effect')
	return

def setup_favourites():
	file_path = xbmcvfs.translatePath('special://userdata/favourites.xml')
	fav1_list = []
	fav1_list.append('	<favourite name="VOD Movies" thumb="special://home/addons/script.xtreme_vod/icon.png">RunScript(script.xtreme_vod,info=allmovies2)</favourite>')
	fav1_list.append('	<favourite name="VOD TV" thumb="special://home/addons/script.xtreme_vod/icon.png">RunScript(script.xtreme_vod,info=alltv2)</favourite>')
	fav1_list.append('	<favourite name="Trakt Watched TV" thumb="special://home/addons/script.xtreme_vod/icon.png">RunScript(script.xtreme_vod,info=trakt_watched,trakt_type=tv)</favourite>')
	fav1_list.append('	<favourite name="Trakt Watched Movies" thumb="special://home/addons/script.xtreme_vod/icon.png">RunScript(script.xtreme_vod,info=trakt_watched,trakt_type=movie)</favourite>')
	fav1_list.append('	<favourite name="Eps_Movies Watching" thumb="special://home/addons/script.xtreme_vod/icon.png">RunScript(script.xtreme_vod,info=ep_movie_progress)</favourite>')
	fav1_list.append('	<favourite name="Reopen Last" thumb="special://home/addons/script.xtreme_vod/icon.png">RunScript(script.xtreme_vod,info=reopen_window)</favourite>')

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
	return


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


	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','player','dialog') , 'standard.py')
	line_update = '''    def select_player(players_list, header=None, detailed=True, index=False, players=None):
        """ Select from a list of players """
        import xbmc
        #xbmc.log(str([i.listitem for i in players_list])+' ===select_player', level=xbmc.LOGINFO)
        players = [i.__dict__ for i in players]
        if 'episode' in str(players[0]['mode']):
            db_type = 'episode'
        else:
            db_type = 'movie'
        for idx, i in enumerate(players): ## PATCH
            if 'auto_cloud' in str(i['meta']['name']).lower() and db_type != 'movie': ## PATCH
                auto_var = idx ## PATCH
                header = str(i['item']['name']) + ' - ' + str(i['item']['title']) + ' - ' + str(i['item']['firstaired'])
                break ## PATCH
            if 'Auto_Torr_Scrape' in str(i['meta']['name']) and db_type == 'movie': ## PATCH
                auto_var = idx ## PATCH
                header = str(i['item']['name']) + ' - ' + str(i['item']['year'])
                break ## PATCH
        x = Dialog().select(header or get_localized(32042), [i.listitem for i in players_list],useDetails=detailed, autoclose=30000, preselect=auto_var)
        return x if index or x == -1 else players_list[x].posx

    def get_player(self, x):
        return self.players_list[x]

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


def play_test_pop_stack():
	import json
	tmdbhelper_flag = False
	reopen_play_fail = xbmcaddon.Addon(addon_ID()).getSetting('reopen_play_fail')
	xbmcgui.Window(10000).setProperty('script.xtreme_vod_started', 'True')
	xbmc.sleep(3000)
	if reopen_play_fail == 'false':
		return
	Utils.tools_log(str('start...')+'play_test_pop_stack')
	home_count = 0
	for i in range(1, int((145 * 1000)/1000)):
		window_id = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
		window_id = json.loads(window_id)
		xbmc.sleep(1000)
		window_id2 = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
		window_id2 = json.loads(window_id2)
		#Utils.tools_log(str(window_id)+str(i)+'')
		if (window_id['result']['currentwindow']['label'].lower() in ['home','notification'] or window_id['result']['currentwindow']['id'] in [10000,10107]) and window_id2 == window_id:
			home_count = home_count + 1
			if home_count > 10:
				Utils.tools_log(str('\n\n\n\nwm.pop_stack()......')+'1play_test_pop_stack')
				log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				#xbmc.executebuiltin('RunPlugin(plugin://%s/?info=play_test_call_pop_stack)' % addon_ID())
				return wm.pop_stack()
		if (window_id['result']['currentwindow']['label'].lower() in ['busydialognocancel'] or window_id['result']['currentwindow']['id'] in [10160]) and window_id2 == window_id:
			error_flag = get_log_error_flag(mode='Exception')
			if error_flag:
				xbmc.executebuiltin('Dialog.Close(all,true)')
				Utils.tools_log(str('\n\n\n\nm.pop_stack()......')+'2play_test_pop_stack')
				#xbmc.executebuiltin('RunPlugin(plugin://%s/?info=play_test_call_pop_stack)' % addon_ID())
				log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				return wm.pop_stack()
		if xbmc.Player().isPlaying() or xbmc.getCondVisibility('Window.IsActive(12005)'):
			Utils.tools_log(str('\n\n\n\nPlayback_Success.......')+'play_test_pop_stack')
			return

		if tmdbhelper_flag == True and window_id != window_id2:
			xbmc.sleep(500)
			error_flag = get_log_error_flag(mode='tmdb_helper')
			if error_flag:
				Utils.tools_log(str('\n\n\n\ntmdb_helper_error_flag.......SLEEP......')+'play_test_pop_stack')
				xbmc.sleep(7500)

		if window_id['result']['currentwindow']['label'] == 'Select dialog' or window_id['result']['currentwindow']['id'] == 12000:
			if tmdbhelper_flag == False:
				Utils.hide_busy()
			tmdbhelper_flag = True
		elif tmdbhelper_flag and ( xbmc.Player().isPlaying() or ( window_id['result']['currentwindow']['label'].lower() == 'fullscreenvideo' or window_id['result']['currentwindow']['id'] == 12005 and window_id2 == window_id and i > 4 ) ):
			Utils.tools_log(str('\n\n\n\nPlayback_Success.......')+'play_test_pop_stack')
			return
		elif tmdbhelper_flag and (window_id['result']['currentwindow']['label'].lower() in ['home','notification'] or window_id['result']['currentwindow']['id'] in [10000,10107]) and window_id2 == window_id and i > 4:
			#Utils.tools_log(str(window_id)+str(i)+'')
			if xbmc.Player().isPlaying():
				Utils.tools_log(str('Playback_Success')+'play_test_pop_stack')
				return
			else:
				error_flag = get_log_error_flag(mode='seren')
				if error_flag == False:
					Utils.tools_log(str('\n\n\n\nwm.pop_stack()......')+'3play_test_pop_stack')
					log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
					#xbmc.executebuiltin('RunPlugin(plugin://%s/?info=play_test_call_pop_stack)' % addon_ID())
					return wm.pop_stack()
				elif error_flag == True:
					Utils.tools_log(str('\n\n\n\nseren_error_flag.......SLEEP......')+'play_test_pop_stack')
					xbmc.sleep(2500)
	Utils.tools_log(str('return......')+'play_test_pop_stack')
	return 

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
		f.seek(0, 2)		   # seek @ EOF
		fsize = f.tell()		# Get Size
		f.seek(max(fsize - 9024, 0), 0)  # Set pos @ last n chars
		lines = f.readlines()	   # Read to end
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
		f.seek(0, 2)		   # seek @ EOF
		fsize = f.tell()		# Get Size
		f.seek(max(fsize - 9024, 0), 0)  # Set pos @ last n chars
		lines = f.readlines()	   # Read to end
	lines = lines[-15:]	# Get last 10 lines
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



def select_pvr_client():
	import xbmc
	import xbmcgui
	import json
	"""
	Presents a selection dialog of installed PVR clients.
	Returns the selected addon ID, or None if cancelled.
	"""
	# JSON-RPC request to get all PVR client addons
	request = {
		"jsonrpc": "2.0",
		"method": "Addons.GetAddons",
		"params": {"enabled": True },
		"id": 1
	}
	
	response_json = xbmc.executeJSONRPC(json.dumps(request))
	response = json.loads(response_json)
	# Extract the list of PVR addons
	#Utils.tools_log(response)
	pvr_addons = response.get("result", {}).get("addons", [])
	
	if not pvr_addons:
		xbmcgui.Dialog().notification("PVR Clients", "No PVR clients installed", xbmcgui.NOTIFICATION_ERROR)
		return None
	
	# Prepare the list of names and IDs for the dialog
	#names = [addon["name"] for addon in pvr_addons]
	addon_ids = [addon["addonid"] for addon in pvr_addons if "pvr." in addon["addonid"]]
	
	if len(addon_ids) == 1:
		return addon_ids[0]

	# Show selection dialog
	dialog = xbmcgui.Dialog()
	selected_index = dialog.select("Select PVR Client", addon_ids)
	
	if selected_index == -1:
		# User cancelled
		return None
	
	# Return the addon ID corresponding to the selected name
	return addon_ids[selected_index]


def reset_stuff():
	import xbmc
	import xbmcgui
	xbmcgui.Dialog().notification("Starting","Starting")
	xbmc.executebuiltin('Dialog.Close(all,true)')
	xbmc.sleep(500)
	xbmc.executebuiltin('ActivateWindow(Home)')
	xbmc.sleep(500)
	xbmc.executebuiltin('ActivateWindow(pvrsettings)')
	xbmc.sleep(500)
	xbmc.executebuiltin('Action(right)')
	window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
	control = window.getControl(window.getFocusId())
	label = control.getLabel()
	x = 0
	while label != 'Clear data' and x < 25:
		xbmc.executebuiltin('Action(down)')
		xbmc.sleep(500)
		control = window.getControl(window.getFocusId())
		label = control.getLabel()
		if label == 'Clear data' or x >= 25:
			break
		x = x +1
	xbmc.executebuiltin('Action(select)')
	unique_labels = []
	curr_label = xbmc.getInfoLabel("ListItem.Label")
	x = 0
	while not curr_label in unique_labels:
		xbmc.sleep(500)
		curr_label = xbmc.getInfoLabel("ListItem.Label")
		if not curr_label == 'Channels, Groups, Guide, Providers':
			xbmc.executebuiltin('Action(select)')
			unique_labels.append(curr_label)
		if curr_label == 'Channels, Groups, Guide, Providers':
			unique_labels.append(curr_label)
		xbmc.sleep(500)
		xbmc.executebuiltin('Action(down)')
		xbmc.sleep(500)
		curr_label = xbmc.getInfoLabel("ListItem.Label")
	xbmc.sleep(500)
	xbmc.executebuiltin('SetFocus(5)')
	xbmc.sleep(500)
	#xbmc.executebuiltin('SetFocus(7)')#CANCEL
	xbmc.executebuiltin('Action(select)')
	xbmc.sleep(500)
	xbmc.executebuiltin('SetFocus(11)')
	xbmc.sleep(500)
	#xbmc.executebuiltin('SetFocus(10)')#NO
	xbmc.executebuiltin('Action(select)')
	xbmc.executebuiltin('Dialog.Close(all,true)')
	Utils.show_busy()
	xbmc.executebuiltin("ActivateWindow(Home)")
	Utils.addon_disable_reable(addonid = Utils.pvr_client , enabled=False)
	
	guide_out = os.path.join(Utils.ADDON_DATA_PATH, 'guide.xml')
	m3u_out = os.path.join(Utils.ADDON_DATA_PATH, 'LiveStream.m3u')
	if os.path.exists(m3u_out):
		os.remove(m3u_out)
	if os.path.exists(guide_out):
		os.remove(guide_out)
	from xtream2m3u_run import generate_m3u
	from xtream2m3u_run import generate_xmltv
	generate_m3u()
	generate_xmltv()
	Utils.addon_disable_reable(addonid = Utils.pvr_client , enabled=True)
	xbmcgui.Dialog().notification("FIN","FIN")