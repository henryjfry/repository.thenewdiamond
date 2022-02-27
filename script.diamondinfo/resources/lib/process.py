import os, shutil
import xbmc, xbmcgui, xbmcaddon
from resources.lib import Utils
from resources.lib.WindowManager import wm
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib.library import icon_path
from resources.autocomplete import AutoCompletion
from resources.autocomplete import AutoCompletion_plugin

def start_info_actions(infos, params):
	addonID = addon_ID()
	addonID_short = addon_ID_short()
	
	if 'imdbid' in params and 'imdb_id' not in params:
		params['imdb_id'] = params['imdbid']
	for info in infos:
		Utils.show_busy()
		data = [], ''
		if info == 'libraryallmovies':
			from resources.lib import local_db
			try:
				script = str(params['script'])
			except:
				script = 'True'
			if script == 'False':
				return local_db.get_db_movies('"sort": {"order": "descending", "method": "dateadded", "limit": %s}' % params.get("limit", "0"))
			return wm.open_video_list(media_type='movie', mode='list_items', filter_label='My TV Shows (Movies)' ,search_str=local_db.get_db_tvshows('"sort": {"order": "descending", "method": "dateadded", "limit": %s}' % params.get("limit", "0")), listitems=[])

		elif info == 'libraryalltvshows':
			from resources.lib import local_db
			try:
				script = str(params['script'])
			except:
				script = 'True'
			if script == 'False':
				return local_db.get_db_tvshows('"sort": {"order": "descending", "method": "dateadded", "limit": %s}' % params.get("limit", "0"))
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
			return wm.open_video_list(media_type=media_type, mode='list_items', filter_label=filter_label, search_str=TheMovieDB.get_tmdb_shows(tmdb_var), listitems=[])


		elif info == 'allmovies':
			wm.open_video_list(media_type='movie',mode='filter')

		elif info == 'alltvshows':
			wm.open_video_list(media_type='tv',mode='filter')

		elif info == 'search_menu':
			search_str = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
			return wm.open_video_list(search_str=search_str, mode='search')

		elif info == 'reopen_window':
			reopen_window()

		elif info == 'service2':
			import service2

		elif info == 'youtube':
			search_str = params.get('search_str')
			return wm.open_youtube_list(search_str=search_str)

		elif info == 'tastedive_search':
			search_str = params.get('search_str')
			media_type = str(params['media_type'])
			limit = params.get('limit', 10)
			from resources.lib import TheMovieDB
			response = TheMovieDB.get_tastedive_data(query=search_str, limit=limit, media_type=media_type)
			return wm.open_video_list(mode='tastedive&' + str(media_type), listitems=[], search_str=response, filter_label='TasteDive Similar ('+str(search_str)+'):')

		elif info == 'tastedive_movies':
			from resources.lib import TheMovieDB
			response = TheMovieDB.get_trakt(trakt_type='movie',info='trakt_watched',limit=30)
			response3 = []
			for i in response:
				response2 = TheMovieDB.get_tastedive_data(query=i['title'], limit=30, media_type='movie')

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
			return wm.open_video_list(mode='tastedive&' + str('movie'), listitems=[], search_str=response3, filter_label='TasteDive Based on Recently Watched Movies:')

		elif info == 'tastedive_tv':
			from resources.lib import TheMovieDB
			response = TheMovieDB.get_trakt(trakt_type='tv',info='trakt_watched',limit=30)
			response3 = []
			for i in response:
				response2 = TheMovieDB.get_tastedive_data(query=i['title'], limit=30, media_type='tv')
				for x in response2:
					if x not in response3:
						response3.append(x)
			return wm.open_video_list(mode='tastedive&' + str('tv'), listitems=[], search_str=response3, filter_label='TasteDive Based on Recently Watched TV:')

		elif info == 'autocomplete' or info == 'selectautocomplete':
			items = AutoCompletion_plugin.start_info_actions(infos, params)
			return items

		elif info == 'test_route':
			from resources.lib import library
			#import mediainfo
			#from resources.lib import TheMovieDB
			#import xbmcvfs, xbmcaddon
			#title = 'Game of Thrones'
			#response = TheMovieDB.get_tmdb_data('search/tv?query=%s&language=en-US&include_adult=%s&' % (title, xbmcaddon.Addon().getSetting('include_adults')), 30)
			#xbmc.log(str(response['results'][0]['id'])+'===>OPEN_INFO', level=xbmc.LOGINFO)
			#return
			#library.auto_setup_xml_filenames()
			#library.trakt_add_movie(tmdb_id_num=604563,mode='Add')
			#return
			
			#from pathlib import Path
			#tvdb_id = 295685
			#tmdb_id = 63174
			#tmdb_api = library.tmdb_api_key()
			#fanart_api = library.fanart_api_key()
			#file_path = library.main_file_path()
			#show_file_path = str(Path(str(library.basedir_tv_path()) + '/' + str(tvdb_id) + '/'))
			#art_path = str(Path(str(file_path) + '/' + str(tvdb_id) + '/' + 'tvshow.fanart'))
			#library.get_art_fanart_tv(tvdb_id, fanart_api, show_file_path, art_path, tmdb_id,tmdb_api)
			#return
			#
			#tmdb_id = 9999
			#show_file_path = library.basedir_movies_path() + '\\' + str(tmdb_id) + '\\'
			#art_path = library.basedir_movies_path() + '\\' + str(tmdb_id) + '\\' + 'movie.fanart'
			#library.get_art_fanart_movie(tmdb_id, fanart_api, show_file_path, art_path,tmdb_api)
		
			import xbmcvfs, xbmcaddon
			from resources.lib.library import icon_path
			xbmc.log(str(library.basedir_movies_path())+'===>OPEN_INFO', level=xbmc.LOGINFO)
			xbmc.log(str(addon_ID())+'===>OPEN_INFO', level=xbmc.LOGINFO)
			xbmc.log(str(addon_ID_short())+'===>OPEN_INFO', level=xbmc.LOGINFO)
			xbmc.log(str(library.main_file_path())+'===>OPEN_INFO', level=xbmc.LOGINFO)
			xbmc.log(str(library.tmdb_settings_path())+'===>OPEN_INFO', level=xbmc.LOGINFO)
			xbmc.log(str(library.tmdb_traktapi_path())+'===>OPEN_INFO', level=xbmc.LOGINFO)
			xbmc.log(str(library.tmdb_traktapi_new_path())+'===>OPEN_INFO', level=xbmc.LOGINFO)
			xbmc.log(str(library.basedir_tv_path())+'===>OPEN_INFO', level=xbmc.LOGINFO)
			xbmc.log(str(library.basedir_movies_path())+'===>OPEN_INFO', level=xbmc.LOGINFO)
			xbmc.log(str(icon_path())+'===>OPEN_INFO', level=xbmc.LOGINFO)
			realizer_test = xbmc.getCondVisibility('System.HasAddon(plugin.video.realizer)')
			xbmc.log(str(realizer_test)+'===>OPEN_INFO', level=xbmc.LOGINFO)

		elif info == 'setup_trakt_watched':
			Utils.show_busy()
			from resources.lib import library
			library.trakt_watched_tv_shows_full()
			xbmc.log(str('trakt_watched_tv_shows_full')+'===>OPEN_INFO', level=xbmc.LOGINFO)
			library.trakt_watched_movies_full()
			xbmc.log(str('trakt_watched_movies_full')+'===>OPEN_INFO', level=xbmc.LOGINFO)
			Utils.hide_busy()

		elif info == 'setup_sources':
			import xbmcvfs, xbmcaddon
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

		elif info == 'trakt_watched' or info == 'trakt_coll' or info == 'trakt_list' or info == 'trakt_trend' or info == 'trakt_popular' or info == 'trakt_progress':
			import xbmcaddon
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
			if trakt_script == 'False' and (info == 'trakt_watched' or info == 'trakt_coll' or info == 'trakt_trend' or info == 'trakt_popular'  or info == 'trakt_progress'):
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
				wm.open_video_list(mode='imdb2', listitems=[], search_str=movies, filter_label=list_name)
			elif 'ur' in str(list_str):
				from resources.lib.TheMovieDB import get_imdb_watchlist_ids
				movies = get_imdb_watchlist_ids(list_str,limit=limit)
				if list_script == 'False':
					from resources.lib.TheMovieDB import get_imdb_watchlist_items
					return get_imdb_watchlist_items(movies=movies,limit=limit)
				wm.open_video_list(mode='imdb2', listitems=[], search_str=movies, filter_label=list_name)
			return

		elif info == 'search_string':
			search_str = params['str']
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
					return wm.open_video_list(mode='person', search_str=movies, listitems=movies['cast_crew'])

		elif info == 'studio':
			from resources.lib import TheMovieDB
			if 'id' in params and params['id']:
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
				#import xbmcaddon
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
			wm.open_movie_info(movie_id=params.get('id'), dbid=params.get('dbid'), imdb_id=params.get('imdb_id'), name=params.get('name'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'extendedactorinfo':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			wm.open_actor_info(actor_id=params.get('id'), name=params.get('name'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'extendedtvinfo':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			if not params.get('id'):
				from resources.lib.TheMovieDB import get_tvshow_info
				import xbmcaddon
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
			wm.open_tvshow_info(tmdb_id=params.get('id'), tvdb_id=params.get('tvdb_id'), dbid=params.get('dbid'), imdb_id=params.get('imdb_id'), name=params.get('name'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'seasoninfo':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			wm.open_season_info(tvshow=params.get('tvshow'), tvshow_id=params.get('tvshow_id'), dbid=params.get('dbid'), season=params.get('season'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'extendedepisodeinfo':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
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
			days = params['days']
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')
			xbmcgui.Window(10000).clearProperty(str(addon_ID_short())+'_running')
			auto_clean_cache(days=days)
			Utils.notify('Cache deleted')

def resolve_url(handle):
	import xbmcplugin
	if handle:
		xbmcplugin.setResolvedUrl(handle=int(handle), succeeded=False, listitem=xbmcgui.ListItem())

def reopen_window():
	while xbmc.Player().isPlaying():
		xbmc.sleep(500)
	return wm.open_video_list(search_str='', mode='reopen_window')

def auto_clean_cache(days=None):
	import os 
	import datetime
	import glob
	path = Utils.ADDON_DATA_PATH
	if days==None:
		days = -14
	else:
		days = int(date)*-1

	today = datetime.datetime.today()#gets current time
	os.chdir(path) #changing path to current path(same as cd command)

	#we are taking current folder, directory and files 
	#separetly using os.walk function
	for root,directories,files in os.walk(path,topdown=False): 
		for name in files:
			#this is the last modified time
			t = os.stat(os.path.join(root, name))[8] 
			filetime = datetime.datetime.fromtimestamp(t) - today
			#checking if file is more than 7 days old 
			#or not if yes then remove them
			if filetime.days <= days:
				#print(os.path.join(root, name), filetime.days)
				xbmc.log(str(os.path.join(root, name))+'===>DELETE', level=xbmc.LOGINFO)
				os.remove(os.path.join(root, name))

def auto_library():
	Utils.hide_busy()
	#xbmc.log(str('auto_library')+'===>OPEN_INFO', level=xbmc.LOGINFO)
	#return

	import xbmcaddon
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
	if library_tv_sync or library_movies_sync:
		import time
		time_since_up = time.monotonic()
		realizer_test = xbmc.getCondVisibility('System.HasAddon(plugin.video.realizer)')
		if not xbmc.Player().isPlaying() and realizer_test:
			try:
				if time_since_up > 600:
					#print('NOW')
					hours_since_up = int((time_since_up)/60/60)
					xbmc.log(str(hours_since_up)+str('=multiple of 8 hours=')+ str(hours_since_up % 8 == 0)+'=hours_since_up===>OPEN_INFO', level=xbmc.LOGINFO)
					if hours_since_up >=1:
						xbmc.executebuiltin('RunPlugin(plugin://plugin.video.realizer/?action=rss_update)')
			except:
				if time_since_up > 600:
					#print('NOW')
					hours_since_up = int((time_since_up)/60/60)
					xbmc.log(str(hours_since_up)+str('=multiple of 8 hours=')+ str(hours_since_up % 8 == 0)+'=hours_since_up===>OPEN_INFO', level=xbmc.LOGINFO)
					if hours_since_up >=1:
						xbmc.executebuiltin('RunPlugin(plugin://plugin.video.realizer/?action=rss_update)')
		#xbmc.executebuiltin('RunPlugin(plugin://plugin.video.realizer/?action=rss_update)')