import xbmc, xbmcgui
from resources.lib import Utils
import gc
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
import json
from resources.lib.WindowManager import wm

from resources.lib.Utils import tools_log
from inspect import currentframe, getframeinfo
#tools_log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

try:
	from infotagger.listitem import ListItemInfoTag
except:
	pass

class VideoPlayer(xbmc.Player):

	def wait_for_video_end(self):
		while xbmc.Player().isPlaying()==1:
			xbmc.sleep(250)
			#while xbmc.getCondVisibility('Window.IsActive(10138)') or xbmcgui.Window(10000).getProperty('Next_EP.ResolvedUrl') == 'true' or xbmcgui.Window(10000).getProperty('Next_EP.ResolvedUrl_playlist') == 'true':
			#	xbmc.sleep(250)
		xbmc.sleep(250)
		#self.stopped = False

	def container_position(self, container=None, position=None):
		params = {'sender': addon_ID_short(),
						  'message': 'SetFocus',
						  'data': {'command': 'SetFocus',
									   'command_params': {'container': container, 'position': position}
									   },
						  }

		command = json.dumps({'jsonrpc': '2.0',
									  'method': 'JSONRPC.NotifyAll',
									  'params': params,
									  'id': 1,
									  })
		result = xbmc.executeJSONRPC(command)
		return result

	def get_next_ep_details(self, season, episode, tmdb):
		from resources.lib.TheMovieDB import extended_season_info
		from resources.lib.TheMovieDB import extended_episode_info
		from resources.lib.TheMovieDB import extended_tvshow_info
		from resources.lib.TheMovieDB import get_tvshow_ids
		import datetime, time
		info = extended_episode_info(tmdb,season, episode)

		xbmcgui.Window(10000).clearProperty('Next_EP.ResolvedUrl')
		
		response_extended_season_info = extended_season_info(tmdb,season)
		response_extended_tvshow_info = extended_tvshow_info(tmdb)
		#Utils.tools_log(response_extended_season_info)
		

		tvdb_id = Utils.fetch(get_tvshow_ids(tmdb), 'tvdb_id')
		tmdb_id = tmdb

		curr_ep_flag = False
		air_date_timestamp = 0
		meta_source = 'tmdb_seasons'
		for i in response_extended_season_info[1]['episodes']:
			i_air_date = str(i.get('release_date','1901-01-01'))
			try: i_air_date = datetime.datetime.strptime(i_air_date, "%Y-%m-%d")
			except TypeError: i_air_date = datetime.datetime(*(time.strptime(i_air_date, "%Y-%m-%d")[0:6]))
			i_air_date = i_air_date.timetuple()
			air_date_timestamp = time.mktime(i_air_date)
			if int(i['episode']) == int(episode) and int(i['season']) == int(season):
				curr_ep_flag = True
				curr_air_date_timestamp = air_date_timestamp

			if int(i['episode']) > int(episode) and int(i['season']) == int(season) and curr_ep_flag == True:
				curr_ep_flag = False
				next_ep_episode = i['episode']
				next_ep_season = i['season']
				break

		#tools.log('curr_air_date_timestamp',curr_air_date_timestamp,'air_date_timestamp',air_date_timestamp)
		if curr_ep_flag == True:
			next_ep_episode = 1
			next_ep_season = int(i['season']) + 1
			if next_ep_season > (response_extended_tvshow_info[0]['TotalSeasons']):
				print_log(str('ENDED')+'===>PHIL')
				return None

		else:
			if air_date_timestamp > ( time.time()+60*60*36): #air_date > tomorrow
				print_log(str('NET_EP_NOT_AIRED')+'===>PHIL')
				return None
			if air_date_timestamp == None or str(air_date_timestamp) == '' and curr_air_date_timestamp >= ( time.time()-(60*60*24*2.5)): #air_date > today- 2.5days
				print_log(str('NET_EP_NOT_AIRED')+'===>PHIL')
				return None

		next_ep_show = None
		for i in response_extended_season_info[1]['episodes']:
			if int(i['episode']) == int(next_ep_episode) and int(i['season']) == int(next_ep_season):
				next_ep_show = response_extended_tvshow_info[0]['TVShowTitle']
				next_ep_thumbnail = i['still']
				next_ep_title = i['title']
				next_ep_rating = i['Rating']
				next_ep_year = i['release_date'][:4]
				air_date = i.get('release_date','')
		
		if next_ep_show == None:
			response_extended_season_info = extended_season_info(tmdb,int(season)+1)
			for i in response_extended_season_info[1]['episodes']:
				if int(i['episode']) == int(next_ep_episode) and int(i['season']) == int(next_ep_season):
					next_ep_show = response_extended_tvshow_info[0]['TVShowTitle']
					next_ep_thumbnail = i['still']
					next_ep_title = i['title']
					next_ep_rating = i['Rating']
					next_ep_year = i['release_date'][:4]
					air_date = i.get('release_date','')
		next_ep_genre = response_extended_tvshow_info[0]['genre']
		strm_title = '%s - S%sE%s - %s' % (next_ep_show, str(next_ep_season).zfill(2),str(next_ep_episode).zfill(2), next_ep_title)
		
		strm_title = str(next_ep_show)+' - S'+str(next_ep_season)+'E'+str(next_ep_episode)+' - '+str(next_ep_title)
		next_ep_details = {}
		next_ep_details['next_ep_show'] = next_ep_show
		next_ep_details['next_ep_season'] = next_ep_season
		next_ep_details['next_ep_episode'] = next_ep_episode
		next_ep_details['next_ep_title'] = next_ep_title
		next_ep_details['next_ep_thumbnail'] = next_ep_thumbnail
		next_ep_details['next_ep_thumb2'] = next_ep_thumbnail
		next_ep_details['tmdb_id'] = tmdb_id
		next_ep_details['tvdb_id'] = tvdb_id
		next_ep_details['next_ep_genre'] = next_ep_genre
		next_ep_details['next_ep_year'] = next_ep_year
		next_ep_details['air_date'] = air_date
		next_ep_details['strm_title'] = strm_title
		next_ep_details['next_ep_rating'] = next_ep_rating
		Utils.tools_log(next_ep_details, 'next_ep_details')
		return next_ep_details

	def prepare_play_VOD_episode(self, tmdb = None, series_id=None, search_str = None, episode=None, season=None, window=False):
		from resources.lib.library import get_fanart_results_full
		from resources.lib.TheMovieDB import get_trakt_playback
		from resources.lib.TheMovieDB import extended_season_info
		from resources.lib.TheMovieDB import extended_episode_info
		from resources.lib.TheMovieDB import extended_tvshow_info
		from resources.lib.TheMovieDB import get_tvshow_ids
		from resources.lib.TheMovieDB import get_vod_alltv
		import xbmcplugin
		import time, sys
		xbmcgui.Window(10000).clearProperty('script.xtreme_vod.ResolvedUrl')
		Utils.show_busy()

		response_extended_season_info = extended_season_info(tmdb,season)
		response_extended_episode_info = extended_episode_info(tmdb,season, episode)
		response_extended_tvshow_info = extended_tvshow_info(tmdb)

		if series_id == None:
			search_str = get_vod_alltv()
			for i in search_str:
				if str(i['tmdb']) == str(tmdb):
					series_id = i['series_id']

		#Utils.tools_log(series_id)
		from resources.lib.TheMovieDB import get_vod_data
		movies = get_vod_data(action= 'get_series_info&series_id=%s' % (str(series_id)) ,cache_days=1)

		try:
			for i in movies['episodes'][str(season)]:
				if str(i['episode_num']) == str(episode):
					#Utils.tools_log(i)
					full_url = '%s%s/%s/%s/%s.%s' % (Utils.xtreme_codes_server_path,'series',Utils.xtreme_codes_username,Utils.xtreme_codes_password,str(i['id']),str(i['container_extension']))
					#Utils.tools_log(full_url)
		except:
			for i in movies['episodes']:
				for x in i:
					if str(x['episode_num']) == str(episode) and str(x['season']) == str(season):
						#Utils.tools_log(i)
						full_url = '%s%s/%s/%s/%s.%s' % (Utils.xtreme_codes_server_path,'series',Utils.xtreme_codes_username,Utils.xtreme_codes_password,str(x['id']),str(x['container_extension']))
						#Utils.tools_log(full_url)

		trakt_progress = get_trakt_playback('tv')
		runtime_seconds = response_extended_episode_info[1]['runtime'] * 60
		resume_progress_seconds = 0
		resumetime, resumeTimeInSeconds = 0, 0
		if trakt_progress:
			for i in trakt_progress:
				if str(i['show']['ids']['tmdb']) == str(tmdb):
					if str(i['episode']['season']) == str(season) and str(i['episode']['number']) == str(episode):
						resume_progress = i['progress']
						resume_progress_seconds = int(float(runtime_seconds) * float(resume_progress/100))
						break

		tvdb_id = Utils.fetch(get_tvshow_ids(tmdb), 'tvdb_id')
		imdb_id = Utils.fetch(get_tvshow_ids(tmdb), 'imdb_id')
		hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = get_fanart_results_full(tvdb_id, media_type='tv_tvdb',show_season=season )

		#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
		if seasonposter != '' and seasonposter != None:
			poster = seasonposter 
		elif tvposter != '' and tvposter != None:
			poster = tvposter
		else:
			poster = response_extended_season_info[0]['poster_original']
		fanart = showbackground
		if clearlogo == '' :
			clearlogo = hdtvlogo
		else:
			clearlogo = clearlogo
		landscape = showbackground
		if landscape == '' or  landscape == None:
			try: landscape = response_extended_season_info[0]['fanart_original']
			except: landscape = tvthumb
		banner = tvbanner
		thumb = response_extended_episode_info[0]['still']
		#duration = str(duration)
		#dbid = str(dbid)
		dbtype = 'episode'
		handle = -1
		infolabels = {'episode': None, 'sortepisode': None, 'season': None, 'sortseason': None, 'year': None, 'premiered': None, 'aired': None, 'imdbnumber': None, 'duration': None, 'dateadded': None, 'rating': None, 'votes': None, 'mediatype': None, 'title': None, 'originaltitle': None, 'sorttitle': None, 'plot': None, 'plotoutline': None, 'tvshowtitle': None, 'playcount': None, 'director': None, 'writer': None, 'mpaa': None, 'genre': None, 'studio': None}

		label = response_extended_episode_info[0]['title']
		xbmcplugin.setContent(handle, 'episodes')
		if xbmc.Player().isPlaying() == False:
			if (resumetime == None or resumetime == '' or resumetime == 0) and resume_progress_seconds > 0:
				resumetime = resume_progress_seconds
				resumeTimeInSeconds = resume_progress_seconds

		try:
			li = xbmcgui.ListItem(label, iconImage=thumb)
		except:
			li = xbmcgui.ListItem(label, thumb)

		li.setProperty('startoffset', str(resumeTimeInSeconds))

		li.setArt({ 'poster': poster, 'fanart': fanart, 'banner': banner, 'clearlogo': clearlogo, 'landscape': landscape, 'thumb': thumb})


		li.setProperty('IsPlayable', 'true')
		li.setProperty('IsFolder', 'false')
		li.setPath(full_url)

		li.setProperty('DBID', None)
		actors = []
		actor_name = []
		actor_role = []
		actor_thumbnail = []
		actor_order = []
		idx = 0
		info_tag_flag = False
		if response_extended_episode_info:
			for idx, i in enumerate(response_extended_episode_info[1]['actors']):
				actor = {'name': i['name'], 'role': i['character'],'thumbnail': i.get('thumb'), 'order': idx+1}
				actors.append(actor)
				actor_name.append(i['name'])
				actor_role.append(i['character'])
				actor_thumbnail.append(i.get('thumb'))
				actor_order.append(idx+1)
			start = idx+1
			for idx, i in enumerate(response_extended_episode_info[1]['guest_stars']):
				actor = {'name': i['name'], 'role': i['character'],'thumbnail': i.get('thumb'), 'order': start+idx+1}
				actors.append(actor)
				actor_name.append(i['name'])
				actor_role.append(i['character'])
				actor_thumbnail.append(i.get('thumb'))
				actor_order.append(idx+1)

			if len(actors) > 0:
				try:
					info_tag = ListItemInfoTag(li, 'video')
					info_tag_flag = True
					info_tag.set_cast(actors)
				except:
					li.setCast(actors)
				li.setProperty('Cast', str(actors))
				li.setProperty('CastAndRole', str(actors))

			director = []
			writer = []
			for i in response_extended_episode_info[1]['crew']:
				if 'Director' in str(i):
					director.append(i['name'])
				if 'Writer' in str(i):
					writer.append(i['name'])
		studio = []
		if response_extended_tvshow_info:
			for i in response_extended_tvshow_info[1]['studios']:
				studio.append(i['title'])

		if response_extended_season_info:
			infolabels['votes'] = int(response_extended_episode_info[0]['Votes'])
			infolabels['mpaa'] = response_extended_tvshow_info[0]['mpaa']
			infolabels['studio'] = studio
		if response_extended_episode_info:
			infolabels['director'] = director
			infolabels['writer'] = writer


		infolabels['episode'] = int(episode)
		infolabels['sortepisode'] = int(episode)
		infolabels['season'] = int(season)
		infolabels['sortseason'] = int(season)
		infolabels['year'] = str(response_extended_episode_info[0]['year'])
		infolabels['premiered'] = str(response_extended_episode_info[0]['release_date'])+'T00:00:00'
		infolabels['aired'] = str(response_extended_episode_info[0]['release_date'])+'T00:00:00'
		infolabels['imdbnumber'] = imdb_id
		try: infolabels['duration'] = int(response_extended_season_info[1]['runtime'])*60
		except: infolabels['duration'] = int(runtime_seconds)
		infolabels['dateadded'] = str(response_extended_episode_info[0]['release_date'])+'T00:00:00'
		infolabels['rating'] = float(response_extended_episode_info[0]['Rating'])
		infolabels['mediatype'] = 'episode'
		infolabels['title'] = label
		infolabels['originaltitle'] = label
		infolabels['sorttitle'] = label
		infolabels['plot'] = response_extended_episode_info[0]['Plot']
		infolabels['plotoutline'] = response_extended_episode_info[0]['Plot']
		infolabels['tvshowtitle'] = response_extended_episode_info[0]['TVShowTitle']
		infolabels['playcount'] = 0

		infolabels['genre'] = response_extended_tvshow_info[0]['genre']

		#infolabels['FileNameAndPath'] = full_url
		#infolabels['EpisodeName'] = episode_name

		li.setProperty('FileNameAndPath', str(full_url))
		li.setProperty('EpisodeName', str(label))

		infolabels['path'] = full_url

		try:
			if info_tag_flag == False:
				info_tag = ListItemInfoTag(li, 'video')
			info_tag.set_info(infolabels)
		except:
			li.setInfo(type='Video', infoLabels = infolabels)

		from get_meta import get_episode_meta
		meta = get_episode_meta(season=int(season), episode=int(episode),tmdb=tmdb, show_name=infolabels['tvshowtitle'], year=infolabels['year'] , interactive=False)

		import sub_lim, tools
		subs_out_ENG, subs_out_FORCED = sub_lim.get_subs_file(cache_directory=tools.ADDON_USERDATA_PATH, video_path = full_url, same_folder=False, meta_info=meta['episode_meta'])
		subs_list = [subs_out_ENG]
		if subs_out_FORCED:
			subs_list.append(subs_out_FORCED)

		#tools.log(subs_list)
		if len(subs_list) > 0:
			from subcleaner import clean_file
			from pathlib import Path
			for i in subs_list:
				sub = Path(i)
				clean_file.clean_file(sub)
			tools.sub_cleaner_log_clean()
			clean_file.files_handled = []

		if len(subs_list) > 0:
			li.setSubtitles(subs_list)

		xbmcplugin.setContent(handle, 'episodes')
		xbmcgui.Window(10000).setProperty('script.xtreme_vod_time', str(int(time.time())+30))
		xbmcgui.Window(10000).setProperty('script.xtreme_vod_player_time', str(int(time.time())+30))
		xbmcgui.Window(10000).setProperty('script.xtreme_vod_download_link', full_url)
		xbmcgui.Window(10000).setProperty('script.xtreme_vod.ResolvedUrl', 'true')

		tvdb_id = Utils.fetch(get_tvshow_ids(tmdb), 'tvdb_id')
		TMDbHelper_NEW_PlayerInfoString = {'tmdb_type': 'episode', 'tmdb_id': str(tmdb), 'imdb_id': str(infolabels['imdbnumber']), 'tvdb_id': str(tvdb_id), 'season': str(infolabels['season']), 'episode': str(infolabels['episode'])}
		xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))


		if 'test=True' in str(sys.argv):

			xbmc.executebuiltin('Dialog.Close(busydialog)')
			xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
			Utils.tools_log('EXIT')

			Utils.tools_log({ 'poster': poster, 'fanart': fanart, 'banner': banner, 'clearlogo': clearlogo, 'landscape': landscape, 'thumb': thumb})

			Utils.tools_log(str(infolabels)[:750].replace('\'','"'),'===>OPENINFO')

			return
		if xbmc.Player().isPlaying() == True:
			player_playing = True
		else:
			player_playing = False
		if xbmc.Player().isPlaying():
			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

			Utils.tools_log('['+str(label)+']'+'[E'+str(episode)+']'+'[S'+str(season)+']'+'['+str(infolabels['tvshowtitle'])+']'+'['+str(full_url)+']','_PRESCRAPE_ADDED===>OPENINFO')

			playlist.add(full_url, li)

			xbmcplugin.setResolvedUrl(handle, True, li)
			xbmcplugin.endOfDirectory(handle)
			return infolabels
		elif player_playing == True and xbmc.Player().isPlaying() == False:
			Utils.tools_log(str('Play_State_Changed_During_Execution_RETURN'),'===>OPENINFO')
			return infolabels
		else:
			xbmc.executebuiltin('Dialog.Close(busydialog)')
			xbmc.executebuiltin('Dialog.Close(busydialognocancel)')

			if window:
				wm.add_to_stack(window, 'curr_window')
				window.close()
			xbmc.executebuiltin('Dialog.Close(all,true)')
			#Utils.get_kodi_json(method='Player.Open', params='{"item": %s}' % item)
			xbmc.executebuiltin('Dialog.Close(okdialog)')
			#xbmc.executebuiltin('RunScript(%s,info=play_test_pop_stack)' % addon_ID())
			#xbmc.sleep(2000)
			xbmc.executebuiltin('Dialog.Close(okdialog)')

			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
			playlist.clear()


			playlist.add(full_url, li)

			xbmcplugin.addDirectoryItem(handle=handle, url=full_url , listitem=li, isFolder=False)
			xbmcplugin.setResolvedUrl(handle, True, li)
			xbmcplugin.endOfDirectory(handle)
			xbmc.Player().play(playlist)


		return

	def prepare_play_VOD_movie(self, tmdb = None, title = None, stream_id=None, search_str = None, window=False):
		from resources.lib.library import get_fanart_results_full
		from resources.lib.TheMovieDB import get_trakt_playback
		from resources.lib.TheMovieDB import extended_movie_info
		from resources.lib.TheMovieDB import single_movie_info
		from resources.lib.TheMovieDB import get_vod_allmovies
		from resources.lib.TheMovieDB import handle_tmdb_movies
		import xbmcplugin
		movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = get_fanart_results_full(tvdb_id=tmdb, media_type='movie')
		xbmcgui.Window(10000).clearProperty('script.xtreme_vod.ResolvedUrl')
		Utils.show_busy()
		#hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = get_fanart_results_full(tvdb_id, media_type='tv_tvdb',show_season=show_season )

		if tmdb == None or tmdb == '':
			tmdb = None

		if search_str:
			for i in search_str:
				if str(i['stream_id']) == str(stream_id):
					full_url = i['full_url']
		else:
			search_str = get_vod_allmovies()
			full_url_list = []
			full_url_titles = []
			response1 = single_movie_info(tmdb)
			responses = {'page': 1, 'results': [],'total_pages': 1, 'total_results': 0}
			results = []
			for idx,i in enumerate(search_str):
				response2 = response1
				
				if i['tmdb'] == tmdb:
					#Utils.tools_log(i['title'])
					response2['OriginalTitle'] = i['title']
					response2['original_title'] = i['title']
					response2['title'] = i['title']
					response2['Label'] = i['title']
					response2['full_url'] = i['full_url']
					response2['stream_id'] = i['stream_id']
					response2['path'] = i['full_url']
					results.append(idx)
					responses['results'].append(response2)
					response2 = None
			#for i in results:
			#	Utils.tools_log(i['OriginalTitle'])
			#selection = xbmcgui.Dialog().select('LINK', full_url_titles)
			#Utils.tools_log(responses['results'])
			listitems=handle_tmdb_movies(responses['results'])
			for idx, i in enumerate(results):
				Utils.tools_log(search_str[i]['title'])
				listitems[idx]['title'] = search_str[i]['title']
				listitems[idx]['Label'] = search_str[i]['title']
				listitems[idx]['OriginalTitle'] = search_str[i]['title']
				#Utils.tools_log(idx)
				#Utils.tools_log(listitems[idx])
			listitem, index = wm.open_selectdialog(listitems=listitems)
			
			if index > -1:
				full_url = search_str[results[index]]['full_url']
			else:
				return

		if tmdb:
			response_extended_movie_info = extended_movie_info(movie_id=tmdb)
			#Utils.tools_log(response_extended_movie_info)
			runtime_seconds = response_extended_movie_info[0]['duration'] * 60
			trakt_progress = get_trakt_playback('movie')
			resume_progress_seconds = 0
			if trakt_progress:
				for i in trakt_progress:
					if str(i['movie']['ids']['tmdb']) == str(tmdb):
						resume_progress = i['progress']
						resume_progress_seconds = int(float(runtime_seconds) * float(resume_progress/100))
						#Utils.tools_log(resume_progress_seconds)
						#Utils.tools_log(runtime_seconds)
						#Utils.tools_log(resume_progress)
						#Utils.tools_log('trakt_progress')
						break

		xbmcplugin.setContent(0, 'movies')

		if tmdb:
			if movieposter != '':
				poster = movieposter 
			else:
				poster = movie_poster

			if moviebackground != '':
				fanart = moviebackground
			else:
				fanart = movie_backdrop

			if hdmovielogo != '':
				clearlogo = hdmovielogo
			else:
				clearlogo = movielogo

			if moviebackground != '':
				landscape = moviebackground
			else:
				landscape = movie_backdrop

			banner = moviebanner

			thumb = moviethumb

			#duration = str(duration)
			#dbid = str(dbid)

		dbtype = 'movie'

		if tmdb:
			label = response_extended_movie_info[0]['title']
			try:
				li = xbmcgui.ListItem(label, iconImage=thumb)
			except:
				li = xbmcgui.ListItem(label, thumb)
			li.setProperty('fanart_image', fanart)
			li.setProperty('startoffset', str(resume_progress_seconds))
			#li.setProperty('DBID', dbid)
		else:
			li = xbmcgui.ListItem(title, '')

		"""
		try:
			json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "VideoLibrary.GetMovieDetails", "params": {"movieid": '+str(dbid)+', "properties": ["art"]}}')
			json_result = json.loads(json_result)
			li.setArt(json_result['result']['moviedetails']['art'])
		except:
			pass

		try:
			json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "VideoLibrary.GetMovieDetails", "params": {"movieid": '+str(dbid)+', "properties": ["title","genre","year","rating","director","trailer","tagline","plot","plotoutline","originaltitle","lastplayed","playcount","writer","studio","mpaa","cast","country","imdbnumber","runtime","set","showlink","streamdetails","top250","votes","fanart","thumbnail","file","sorttitle","resume","setid","dateadded","tag","userrating","ratings","premiered","uniqueid"]}}')
			json_result = json.loads(json_result)

			try:
				info_tag = ListItemInfoTag(li, 'video')
				info_tag.set_info(json_result['result']['moviedetails'])
			except:
				li.setInfo(type='Video', infoLabels=str(json_result['result']['moviedetails']))
		except:
			pass
		"""

		li.setProperty('IsPlayable', 'true')
		li.setProperty('IsFolder', 'false')

		li.setPath(full_url)

		infolabels = {'year': None, 'premiered': None, 'aired': None, 'mpaa': None, 'genre': None, 'imdbnumber': None, 'duration': None, 'dateadded': None, 'rating': None, 'votes': None, 'tagline': None, 'mediatype': None, 'title': None, 'originaltitle': None, 'sorttitle': None, 'plot': None, 'plotoutline': None, 'studio': None, 'country': None, 'director': None, 'writer': None, 'status': None, 'trailer': None}

		if tmdb:
			#Utils.tools_log( response_extended_movie_info[0])
			li.setProperty('MovieTitle', response_extended_movie_info[0]['title'])
			li.setProperty('Duration', str(response_extended_movie_info[0]['duration']))
			actors = []
			actor_name = []
			actor_role = []
			actor_thumbnail = []
			actor_order = []
			for idx, i in enumerate(response_extended_movie_info[1]['actors']):
				actor = {'name': i['name'], 'role': i['character'],'thumbnail': i.get('thumb'), 'order': idx+1}
				actors.append(actor)
				actor_name.append(i['name'])
				actor_role.append(i['character'])
				actor_thumbnail.append(i.get('thumb'))
				actor_order.append(idx+1)

			if len(actors) > 0:

				try:
					info_tag = ListItemInfoTag(li, 'video')
					info_tag.set_cast(actors)
				except:
					li.setCast(actors)
				li.setProperty('Cast', str(actors))
				li.setProperty('CastAndRole', str(actors))

			director = []
			writer = []
			for i in response_extended_movie_info[1]['crew']:
				if 'Director' == str(i['job']):
					director.append(i['name'])
				if 'Writer' == str(i['job']):
					writer.append(i['name'])
			studio = []
			for i in response_extended_movie_info[1]['studios']:
				studio.append(i['title'])

			infolabels['year'] = str(response_extended_movie_info[0]['year'])
			infolabels['premiered'] = str(response_extended_movie_info[0]['Premiered'])+'T00:00:00'
			infolabels['aired'] = str(response_extended_movie_info[0]['Premiered'])+'T00:00:00'
			infolabels['imdbnumber'] = response_extended_movie_info[0]['imdb_id']
			try: infolabels['duration'] = int(response_extended_movie_info[0]['duration'])
			except: infolabels['duration'] = int(response_extended_movie_info[0]['duration'])
			infolabels['dateadded'] = str(response_extended_movie_info[0]['Premiered'])+'T00:00:00'+'T00:00:00'
			infolabels['rating'] = float(response_extended_movie_info[0]['Rating'])
			infolabels['votes'] = int(response_extended_movie_info[0]['Votes'])
			infolabels['tagline'] = response_extended_movie_info[0]['Tagline']
			infolabels['mediatype'] = 'movie'
			infolabels['title'] = response_extended_movie_info[0]['title']
			infolabels['originaltitle'] = response_extended_movie_info[0]['title']
			infolabels['sorttitle'] = response_extended_movie_info[0]['title']
			infolabels['plot'] = response_extended_movie_info[0]['Plot']
			infolabels['plotoutline'] = response_extended_movie_info[0]['Plot']
			infolabels['playcount'] = 0
			infolabels['director'] = director
			infolabels['writer'] = writer
			infolabels['status'] = response_extended_movie_info[0]['Status']
			infolabels['mpaa'] = response_extended_movie_info[0]['mpaa']
			infolabels['genre'] = response_extended_movie_info[0]['genre']
			infolabels['studio'] = studio
			infolabels['country'] = response_extended_movie_info[0]['Country']

		li.setProperty('FileNameAndPath', str(full_url))
		infolabels['path'] = full_url

		TMDbHelper_NEW_PlayerInfoString = {'tmdb_type': 'movie', 'tmdb_id': str(tmdb), 'imdb_id': str(infolabels['imdbnumber']), 'year': str(infolabels['year'])}
		xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))

		try:
			info_tag = ListItemInfoTag(li, 'video')
			info_tag.set_info(infolabels)
		except:
			li.setInfo(type='Video', infoLabels = infolabels)

		if tmdb:
			li.setArt({ 'poster': poster, 'fanart': fanart, 'banner': banner, 'clearlogo': clearlogo, 'landscape': landscape, 'thumb': thumb})

		from get_meta import get_movie_meta
		meta = get_movie_meta(tmdb=tmdb, movie_name=infolabels['title'], year=infolabels['year'] , imdb=infolabels['imdbnumber'], interactive=False)

		import sub_lim, tools
		subs_out_ENG, subs_out_FORCED = sub_lim.get_subs_file(cache_directory=tools.ADDON_USERDATA_PATH, video_path = full_url, same_folder=False, meta_info=meta)
		subs_list = [subs_out_ENG]
		if subs_out_FORCED:
			subs_list.append(subs_out_FORCED)

		#tools.log(subs_list)
		if len(subs_list) > 0:
			from subcleaner import clean_file
			from pathlib import Path
			for i in subs_list:
				sub = Path(i)
				clean_file.clean_file(sub)
			tools.sub_cleaner_log_clean()
			clean_file.files_handled = []

		if len(subs_list) > 0:
			li.setSubtitles(subs_list)
		import time
		xbmc.executebuiltin('Dialog.Close(okdialog)')
		xbmcgui.Window(10000).setProperty('script.xtreme_vod_time', str(int(time.time())+120))
		#if dbid != 0 and 1==2:
		#	item = '{"%s": %s}' % (type, dbid)
		#else:
		#	item = '{"file": "%s"}' % url
		item = '{"file": "%s"}' % full_url
		if Utils.window_stack_enable == 'false':
			#super(VideoPlayer, self).play(item=url, listitem=listitem, windowed=False, startpos=-1)

			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
			playlist.clear()
			xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
			playlist.add(full_url, li)
			xbmcplugin.setResolvedUrl(0, True, li)
			xbmcplugin.endOfDirectory(0)
			xbmc.Player().play(playlist)
			
			if window:
				window.close()
			gc.collect()
			#xbmc.executebuiltin('RunPlugin(%s)' % url)
			del window
			#xbmc.executebuiltin('Dialog.Close(all,true)')
			#try: self.close()
			#except: pass
			return
		xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'False')
		xbmcgui.Window(10000).setProperty('script.xtreme_vod_started', 'True')
		xbmcgui.Window(10000).clearProperty('xtreme_vod_window_number')
		if window:
			wm.add_to_stack(window, 'curr_window')
			window.close()
		xbmc.executebuiltin('Dialog.Close(all,true)')
		#Utils.get_kodi_json(method='Player.Open', params='{"item": %s}' % item)
		xbmc.executebuiltin('Dialog.Close(okdialog)')
		#xbmc.executebuiltin('RunScript(%s,info=play_test_pop_stack)' % addon_ID())
		#xbmc.sleep(2000)
		xbmc.executebuiltin('Dialog.Close(okdialog)')
		
		playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		playlist.clear()
		xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
		playlist.add(full_url, li)
		xbmcplugin.setResolvedUrl(0, True, li)
		xbmcplugin.endOfDirectory(0)
		xbmc.Player().play(playlist)

		
		#xbmc.executebuiltin('RunPlugin(%s)' % url)
		#xbmc.log(str('play_from_button')+'_________________________play_from_button===>OPENINFO', level=xbmc.LOGINFO)
		tools_log(str(str('play_from_button')+'_________________________play_from_button'))
		tools_log(str(str(item)+'_________________________play_from_button'))
		return


	def play(self, url, listitem, window=False):
		import time
		xbmc.executebuiltin('Dialog.Close(okdialog)')
		xbmcgui.Window(10000).setProperty('script.xtreme_vod_time', str(int(time.time())+120))
		container = xbmc.getInfoLabel('System.CurrentControlId')
		position = int(xbmc.getInfoLabel('Container('+str(container)+').CurrentItem'))-1
		#window.close()
		#super(VideoPlayer, self).play(item=url, listitem=listitem, windowed=False, startpos=-1)
		xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'False')
		xbmcgui.Window(10000).setProperty('script.xtreme_vod_started', 'True')
		xbmcgui.Window(10000).clearProperty('xtreme_vod_window_number')
		wm.add_to_stack(window, 'curr_window')
		window.close()
		xbmc.executebuiltin('Dialog.Close(all,true)')
		##Utils.get_kodi_json(method='Player.Open', params='{"item": %s}' % item)
		#xbmc.executebuiltin('RunPlugin(%s)' % url)
		xbmcgui.Window(10000).clearProperty('reopen_window_var')
		xbmc.executebuiltin('Dialog.Close(okdialog)')
		xbmc.executebuiltin('RunScript(%s,info=play_test_pop_stack)' % addon_ID())
		super(VideoPlayer, self).play(item=url, listitem=listitem, windowed=False, startpos=-1)
		#xbmc.log(str('play')+'_________________________play===>OPENINFO', level=xbmc.LOGINFO)
		tools_log(str(str('play')+'_________________________play'))
		return

		for i in range(600):
			if xbmc.getCondVisibility('VideoPlayer.IsFullscreen'):
				if window and window.window_type == 'dialog':
					wm.add_to_stack(window, 'curr_window')
					#window.close()
					if Utils.window_stack_enable == 'true':
						window = None
						del window
					self.wait_for_video_end()
					if Utils.window_stack_enable == 'false':
						self.container_position(container=container,position=position)
						window.doModal()
						window = None
						del window
						return
					self.container_position(container=container,position=position)
					tools_log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
					return wm.pop_stack()
			xbmc.sleep(50)

	def play_from_button(self, url=None, listitem=None, window=False, type='', dbid=0):
		#from resources.lib.WindowManager import wm
		import time
		xbmc.executebuiltin('Dialog.Close(okdialog)')
		xbmcgui.Window(10000).setProperty('script.xtreme_vod_time', str(int(time.time())+120))
		if dbid != 0 and 1==2:
			item = '{"%s": %s}' % (type, dbid)
		else:
			item = '{"file": "%s"}' % url
		if Utils.window_stack_enable == 'false':
			super(VideoPlayer, self).play(item=url, listitem=listitem, windowed=False, startpos=-1)
			if window:
				window.close()
			gc.collect()
			#xbmc.executebuiltin('RunPlugin(%s)' % url)
			del window
			#xbmc.executebuiltin('Dialog.Close(all,true)')
			#try: self.close()
			#except: pass
			return
		xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'False')
		xbmcgui.Window(10000).setProperty('script.xtreme_vod_started', 'True')
		xbmcgui.Window(10000).clearProperty('xtreme_vod_window_number')
		if window:
			wm.add_to_stack(window, 'curr_window')
			window.close()
		xbmc.executebuiltin('Dialog.Close(all,true)')
		#Utils.get_kodi_json(method='Player.Open', params='{"item": %s}' % item)
		xbmc.executebuiltin('Dialog.Close(okdialog)')
		xbmc.executebuiltin('RunScript(%s,info=play_test_pop_stack)' % addon_ID())
		xbmc.sleep(2000)
		xbmc.executebuiltin('Dialog.Close(okdialog)')
		xbmc.executebuiltin('RunPlugin(%s)' % url)
		#xbmc.log(str('play_from_button')+'_________________________play_from_button===>OPENINFO', level=xbmc.LOGINFO)
		tools_log(str(str('play_from_button')+'_________________________play_from_button'))
		tools_log(str(str(item)+'_________________________play_from_button'))
		return

		for i in range(800):
			#xbmc.log(str('self.wait_for_video_end()')+str(i)+'before===>OPENINFO', level=xbmc.LOGINFO)
			#if xbmc.getCondVisibility('VideoPlayer.IsFullscreen'):
			if xbmc.Player().isPlaying()==1:
				if window and window.window_type == 'dialog':
					wm.add_to_stack(window, 'curr_window')
					window = None
					del window
					if xbmcgui.Window(10000).getProperty('bluray') == 'true':
						xbmc.sleep(500)
					#xbmc.log(str('wait_for_video_end')+'append_window_stack_table===>OPENINFO', level=xbmc.LOGINFO)
					self.wait_for_video_end()
					#xbmc.log(str('wait_for_video_end')+'append_window_stack_table===>OPENINFO', level=xbmc.LOGINFO)
					tools_log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
					return wm.pop_stack()
			if xbmcgui.Window(10000).getProperty('bluray') == 'true':
				xbmc.sleep(350)
				i = i - 20
			xbmc.sleep(150)

	def playtube(self, youtube_id=False, listitem=None, window=False):
		xbmc.executebuiltin('Dialog.Close(okdialog)')
		xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'False')
		url = 'plugin://plugin.video.youtube/play/?video_id=%s' % str(youtube_id)
		self.play(url=url, listitem=listitem, window=window)

PLAYER = VideoPlayer()