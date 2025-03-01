#!/usr/bin/python3
import time
import sys
import urllib
import urllib.parse
import requests
import json
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, json

from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib.library import trak_auth
from resources.lib.TheMovieDB import get_tvshow_ids
from resources.lib.TheMovieDB import extended_episode_info
from resources.lib.TheMovieDB import get_trakt_playback

from resources.lib.library import db_connection

from resources.lib.Utils import get_JSON_response

from a4kscrapers_wrapper import get_meta

from resources.lib.TheMovieDB import get_tmdb_data

from resources.lib.library import get_processor_info

tmdb_api = xbmcaddon.Addon(addon_ID()).getSetting('tmdb_api')
fanart_api = xbmcaddon.Addon(addon_ID()).getSetting('fanart_api')

if len(fanart_api) != 32:
	fanart_api = '184e1a2b1fe3b94935365411f919f638'
if len(tmdb_api) != 32:
	tmdb_api = 'edde6b5e41246ab79a2697cd125e1781'

try:
	from infotagger.listitem import ListItemInfoTag
except:
	pass

from os.path import expanduser
home = expanduser("~")


#try: 
#	url = 'https://cable.ayra.ch/makemkv/api.php?json'
#	headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
#	response= requests.get(url.strip(), headers=headers, timeout=10).json()
#
#	f = open(home + '/.MakeMKV/settings.conf', 'r') 
#	f_content = f.read()
#	f.close()
#	re_sub = str('app_Key = "%s"' % (response['key']))
#	f_content = re.sub(r'app_Key = "{1}.*"{1}', re_sub,f_content)
#	f = open(home + '/.MakeMKV/settings.conf', 'w') 
#	f.write(f_content)
#	f.close()
#except:
#	pass

try: os.system('sudo mount -a')
except : pass

import os.path
import subprocess
from inspect import currentframe, getframeinfo
script_path = os.path.dirname(os.path.abspath(getframeinfo(currentframe()).filename))
#print(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))

import xbmcvfs

def tmdb_api():
	tmdb_api = xbmcaddon.Addon(addon_ID()).getSetting('tmdb_api')
	if len(tmdb_api) != 32:
		tmdb_api = 'edde6b5e41246ab79a2697cd125e1781'
	return tmdb_api

def fanart_api():
	fanart_api = xbmcaddon.Addon(addon_ID()).getSetting('fanart_api')
	if len(fanart_api) != 32:
		fanart_api = '184e1a2b1fe3b94935365411f919f638'
	return fanart_api

def print_log(log_item1, log_item2=None):
	xbmc.log(str(log_item1)+str(log_item2)+'===>OPENINFO', level=xbmc.LOGFATAL)

def main_file_path():
	return xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('path'))

def tmdb_settings_path():
	addon = xbmcaddon.Addon()
	addon_path = addon.getAddonInfo('path')
	addonID = addon.getAddonInfo('id')
	addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
	tmdb_settings_path = addonUserDataFolder.replace(addonID,'plugin.video.themoviedb.helper') + '/settings.xml'
	tmdb_settings_path = Path(tmdb_settings_path)
	return tmdb_settings_path

def tmdb_traktapi_path():
	tmdb_traktapi_path = Path(main_file_path().replace(addon_ID(),'plugin.video.themoviedb.helper') + 'resources/lib/traktapi.py')
	return tmdb_traktapi_path

def tmdb_traktapi_new_path():
	tmdb_traktapi_new_path = Path(main_file_path().replace(addon_ID(),'plugin.video.themoviedb.helper') + 'resources/lib/trakt/api.py')
	return tmdb_traktapi_new_path

def tmdb_traktapi_new_path2():
	tmdb_traktapi_new_path = Path(main_file_path().replace(addon_ID(),'plugin.video.themoviedb.helper') + 'resources/lib/api/trakt/api.py')
	return tmdb_traktapi_new_path

def clear_next_ep_props():
	xbmcgui.Window(10000).clearProperty('Next_EP.ResolvedUrl')
	xbmcgui.Window(10000).clearProperty('Next_EP.ResolvedUrl_playlist')
	xbmcgui.Window(10000).clearProperty('Next_EP.Url')
	xbmcgui.Window(10000).clearProperty('Next_EP.poster')
	xbmcgui.Window(10000).clearProperty('Next_EP.fanart')
	xbmcgui.Window(10000).clearProperty('Next_EP.clearlogo')
	xbmcgui.Window(10000).clearProperty('Next_EP.landscape')
	xbmcgui.Window(10000).clearProperty('Next_EP.banner')
	xbmcgui.Window(10000).clearProperty('Next_EP.thumb')
	xbmcgui.Window(10000).clearProperty('Next_EP.duration')
	xbmcgui.Window(10000).clearProperty('Next_EP.dbid')
	xbmcgui.Window(10000).clearProperty('Next_EP.dbtype')
	xbmcgui.Window(10000).clearProperty('Next_EP.genre')
	xbmcgui.Window(10000).clearProperty('Next_EP.imdb')
	xbmcgui.Window(10000).clearProperty('Next_EP.icon')
	xbmcgui.Window(10000).clearProperty('Next_EP.label')
	xbmcgui.Window(10000).clearProperty('Next_EP.label2')
	xbmcgui.Window(10000).clearProperty('Next_EP.originaltitle')
	xbmcgui.Window(10000).clearProperty('Next_EP.plot')
	xbmcgui.Window(10000).clearProperty('Next_EP.plotoutline')
	xbmcgui.Window(10000).clearProperty('Next_EP.premiered')
	xbmcgui.Window(10000).clearProperty('Next_EP.rating')
	xbmcgui.Window(10000).clearProperty('Next_EP.movie_title')
	xbmcgui.Window(10000).clearProperty('Next_EP.title')
	xbmcgui.Window(10000).clearProperty('Next_EP.year')
	xbmcgui.Window(10000).clearProperty('Next_EP.resumetime')
	xbmcgui.Window(10000).clearProperty('diamond_player_time')

def dvd_eject():
	"""
	import ctypes
	ctypes.windll.WINMM.mciSendStringW(u"set cdaudio door open", None, 0, None)

	import os
	#import xbmc,xbmcgui

	#json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"Application.GetProperties","params":{"properties": ["volume", "muted"]}}')

	#xbmc.executebuiltin('ActivateWindow(fullscreenvideo)')

	#xbmc.log(str(json_result)+str(xbmcgui.getCurrentWindowId())+'YLIST', level=xbmc.LOGNOTICE)

	kodi_command = 'kodi-send --action=\"Stop\"'
	os.system(kodi_command)
	try: os.system("sudo eject cdrom")
	except: pass
	try: os.system('sudo umount /dev/sr0')
	except : pass
	#kodi_command = 'kodi-send --action=\"ActivateWindow(Favourites)\"'
	#os.system(kodi_command)
	"""
	import xbmc
	json_result_test = xbmc.executeJSONRPC('{"jsonrpc": "2.0","method": "System.EjectOpticalDrive","params": {},"id": "1"}')

def bluray_menu(menu=None):
	import xbmc, json
	"""
	kodi_params = ('{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"disc.playback"}, "id": 1}')
	kodi_response = xbmc.executeJSONRPC(kodi_params)
	json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
	json_object  = json.loads(json_data)
	print(json_object['result'])
	if json_object['result']['value'] == 2:
		disc_value = 0
		disc_message = 'Toggle=show simplified menu '
	if json_object['result']['value'] == 0:
		disc_value = 2
		disc_message = 'Toggle=play main movie '
	"""
	if menu == True:
		#'show simplified menu '
		disc_value = 0
	else:
		#'play main movie '
		disc_value = 2

	kodi_params = ('{"jsonrpc":"2.0","method":"Settings.SetSettingValue","params":{"setting":"disc.playback","value":%s}, "id": 1}' % (disc_value))
	kodi_response = xbmc.executeJSONRPC(kodi_params)
	#json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
	json_object  = json.loads(kodi_response)
	#print_log(json_object['result'])

	#kodi_params = ('{"jsonrpc":"2.0","method":"GUI.ShowNotification","params":{"title":"disc.playback","message":"%s"}, "id": 1}' % (disc_message))
	#kodi_response = xbmc.executeJSONRPC(kodi_params)
	#json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
	#json_object  = json.loads(json_data)
	#print(json_object['result'])


def get_fanart_results(tvdb_id, media_type=None, show_season = None):
	#from a4kscrapers_wrapper import get_meta
	#get_fanart_results(tvdb_id, media_type=None, show_season = None)

	if 'tv_tvdb' == media_type:
		hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = '', '', '', '', '', '', '', '', '', '', '', '';
		hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = get_meta.get_fanart_results(tvdb_id, media_type='tv_tvdb', show_season = show_season)
		return hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo
	else:
		movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = '', '', '', '', '', '', '', '', ''
		movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = get_meta.get_fanart_results(tvdb_id, media_type='movie', show_season = None)
		return movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground


def next_ep_play_movie(movie_year, movie_title, tmdb, menu):
	import sys
	if sys.version_info[0] >= 3:
		unicode = str
		basestring = str
	from resources.lib.TheMovieDB import get_tmdb_data
	from resources.lib.TheMovieDB import single_movie_info
	from resources.lib.TheMovieDB import extended_movie_info
	from resources.lib.TheMovieDB import get_movie_info
	bluray_menu(menu=menu)

	xbmcgui.Window(10000).setProperty('bluray', 'true')

	tmdbhelper_tvshow_poster = xbmcgui.Window(10000).getProperty('tmdbhelper_tvshow.poster')
	xbmc_plugin = 'True'

	li = None
	clear_next_ep_props()
	xbmc_plugin = 'True'
	#print_log(str(getframeinfo(currentframe()).filename)+' show=\''+str(movie_title)+'\' year='+str(movie_year))
	kodi_send_command = 'kodi-send --action="RunScript(%s,info=diamond_bluray_player,type=movie,movie_year=%s,movie_title=%s,tmdb=%s,menu=False)"' % (addon_ID(), movie_year, movie_title, tmdb)
	print_log(kodi_send_command,'kodi_send_command')

	import re
	regex = re.compile('[^a-zA-Z]')

	movie_title_clean = regex.sub(' ', movie_title).replace('  ',' ').lower()

	#xbmc.log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)+'===>OPENINFO', level=xbmc.LOGFATAL)
	response = get_movie_info(movie_label=movie_title, year=movie_year, use_dialog=False)

	try: 
		i = response['results'][0]
	except: 
		response2 = response
		response = {}
		response['results'] = []
		response['results'].append(response2)
	#print_log(str(response)+'===>OPENINFO')

	if tmdb:
		response2 = single_movie_info(movie_id=tmdb)
		response['results'] = []
		response['results'].append(response2)

	#print_log(str(response)+'===>OPENINFO')
	for i in response['results']:
		if str(movie_year) in str(i['release_date']):
			tmdb_id = i['id']
			try: movie_poster = 'https://image.tmdb.org/t/p/original/' + i['poster_path']
			except: movie_poster = ''
			try: 
				try:
					movie_title = i['title']
				except:
					movie_title = str(u''.join(i['title']).encode('utf-8').strip())
			except: pass
			try: 
				try:
					movie_plot = i['overview']
				except:
					movie_plot = str(u''.join(i['overview']).encode('utf-8').strip())
			except: movie_plot = ''
			try: movie_release_date = str(u''.join(i['release_date']).encode('utf-8').strip())
			except: movie_release_date = ''
			try: movie_popularity = str(u''.join(i['popularity']).encode('utf-8').strip())
			except: movie_popularity = ''
			try: 
				try:
					movie_original_title = i['original_title']
				except:
					movie_original_title = str(u''.join(i['original_title']).encode('utf-8').strip())
			except: movie_original_title = ''
			try: movie_backdrop = 'https://image.tmdb.org/t/p/original/'+i['backdrop_path']
			except: movie_backdrop = ''
			try: movie_vote_count = str(u''.join(i['vote_count']).encode('utf-8').strip())
			except: movie_vote_count = ''
			try: movie_vote_average = i['vote_average']
			except: movie_vote_average = ''
			try: movie_original_language = str(i['original_language'])
			except: movie_original_language = ''
			try: 
				movie_genre = i['genre_ids']
				genres = get_tmdb_data('genre/movie/list?language=%s&' % xbmcaddon.Addon().getSetting('LanguageID'), 30)
				xy = 0
				for x in movie_genre:
					for y in genres['genres']:
						if x == y['id']:
							movie_genre[xy] = y['name']
					xy = xy + 1
			except: 
				movie_genre = ''
			break

	session_str = ''
	response = get_tmdb_data('movie/%s?append_to_response=external_ids,runtime,alternative_titles&language=%s&%s' % (tmdb_id, xbmcaddon.Addon().getSetting('LanguageID'), session_str), 14)
	imdb_id = response['external_ids']['imdb_id']
	#print_log(response)
	runtime = response['runtime']
	runtime_seconds = response['runtime']* 60

	response = single_movie_info(movie_id=tmdb_id)
	#print_log(response)
	alternate_titles = []
	y = 0
	for i in response['alternative_titles']['titles']:
		try:
			alternate_titles.append(['title'])
		except:
			alternate_titles.append(str(u''.join(['title']).encode('utf-8').strip()))
		y = y + 1

	trakt_progress = get_trakt_playback('movie')
	resume_progress_seconds = 0
	if trakt_progress:
		for i in trakt_progress:
			if str(i['movie']['ids']['tmdb']) == str(tmdb):
				resume_progress = i['progress']
				resume_progress_seconds = int(float(runtime_seconds) * float(resume_progress/100))
				break

#	if xbmc_plugin == 'True':
#		xbmc.executebuiltin('ActivateWindow(busydialognocancel)')

	print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = get_fanart_results(tvdb_id=tmdb, media_type='movie')

	dvd_flag = 'False'
	BDMV = ''
	bluray_dvd_path = xbmcaddon.Addon(addon_ID()).getSetting('bluray_dvd_path')
	for root, subdirs, files in os.walk(bluray_dvd_path):
		for d in subdirs:
			if d == "BDMV":
				dvd_flag = 'False'
				BDMV = os.path.join(root, d + '/index.bdmv')
				xbmc.Player().stop()
				xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
			if d == "VIDEO_TS":
				dvd_flag = 'True'
				BDMV = os.path.join(root, d + '/VIDEO_TS.IFO')
				xbmc.Player().stop()
				xbmc.executebuiltin('ActivateWindow(busydialognocancel)')


	con = db_connection()
	cur = con.cursor()

	sql_test = "SELECT * from files,movie where movie.idfile = files.idfile and movie.c00 = '"+str(movie_title).replace('\'','\'\'')+"' order by dateadded asc"
	sql_result1 = cur.execute(sql_test).fetchall()

	try: dbid = sql_result1[0][0]
	except: dbid = 0

	sql_result = cur.execute("SELECT resumeTimeInSeconds,C11 from movie_view where idmovie = " + str(dbid)).fetchall()
	try: resumeTimeInSeconds = sql_result[0][0]
	except: resumeTimeInSeconds = ''
	try: duration = sql_result[0][1]
	except: duration = ''
	if duration == '' or duration == None:
		duration = ''
	if resumeTimeInSeconds == None:
		resumeTimeInSeconds = 0
	#try:
	#	file_name = BDMV.split('/')[-1]
	#	delete_result = cur.execute("DELETE FROM files WHERE strFilename = '"+str(file_name)+"' ;")
	#	con.commit()
	#	#delete_result = cur.execute("DELETE FROM files WHERE strFilename = '"+str('index.bdmv')+"' ;")
	#	#con.commit()
	#except:
	#	pass
	try:
		file_name = BDMV.split('/')[-1]
		sql_result = cur.execute("SELECT idfile,strFilename  from files where strFilename = '"+str(file_name)+"' ;").fetchall()
		for i in sql_result:
			id_file = i[0]
			delete_result = cur.execute("DELETE FROM stacktimes WHERE idFile  = '"+str(id_file)+"' ;")
			#delete_result = cur.execute("DELETE FROM movie WHERE idFile  = '"+str(id_file)+"' ;")
			delete_result = cur.execute("DELETE FROM settings WHERE idFile  = '"+str(id_file)+"' ;")
			#delete_result = cur.execute("DELETE FROM episode WHERE idFile  = '"+str(id_file)+"' ;")
			delete_result = cur.execute("DELETE FROM bookmark WHERE idFile  = '"+str(id_file)+"' ;")
			delete_result = cur.execute("DELETE FROM streamdetails WHERE idFile  = '"+str(id_file)+"' ;")
			#delete_result = cur.execute("DELETE FROM musicvideo WHERE idFile  = '"+str(id_file)+"' ;")
			delete_result = cur.execute("DELETE FROM files WHERE idFile  = '"+str(id_file)+"' ;")
		con.commit()
	except:
		pass
	cur.close()


	cur.close()
	con.close()

	try: movie_release_date = str(movie_release_date).replace('b\'','').replace('\'','')
	except: pass

	if xbmc_plugin == 'True':
		if movieposter != '':
			poster = movieposter 
		else:
			poster = movie_poster
		xbmcgui.Window(10000).setProperty('Next_EP.poster', poster)
		if moviebackground != '':
			fanart = moviebackground
		else:
			fanart = movie_backdrop
		xbmcgui.Window(10000).setProperty('Next_EP.fanart', fanart)
		if hdmovielogo != '':
			clearlogo = hdmovielogo
		else:
			clearlogo = movielogo
		xbmcgui.Window(10000).setProperty('Next_EP.clearlogo', clearlogo)
		if moviebackground != '':
			landscape = moviebackground
		else:
			landscape = movie_backdrop
		xbmcgui.Window(10000).setProperty('Next_EP.landscape', landscape)
		banner = moviebanner
		xbmcgui.Window(10000).setProperty('Next_EP.banner', banner)
		thumb = moviethumb
		xbmcgui.Window(10000).setProperty('Next_EP.thumb', thumb)
		#director = xbmc.getInfoLabel('listitem.Director')
		#cast = xbmc.getInfoLabel('listitem.Cast')
		#cast_role = xbmc.getInfoLabel('listitem.CastAndRole')
		duration = str(duration)
		xbmcgui.Window(10000).setProperty('Next_EP.duration', duration)
		dbid = str(dbid)
		xbmcgui.Window(10000).setProperty('Next_EP.dbid', dbid)
		dbtype = 'movie'
		xbmcgui.Window(10000).setProperty('Next_EP.dbtype', dbtype)


		try:
			if (movie_genre[-1] == '\'' and movie_genre[:2] == 'b\'') or (movie_genre[-1] == '"' and movie_genre[:2] == 'b"'):
				movie_genre = movie_genre[:-1]
				movie_genre = movie_genre[2:]
		except:
			pass
		if (movie_title[-1] == '\'' and movie_title[:2] == 'b\'') or (movie_title[-1] == '"' and movie_title[:2] == 'b"'):
			movie_title = movie_title[:-1]
			movie_title = movie_title[2:]
		if (movie_original_title[-1] == '\'' and movie_original_title[:2] == 'b\'') or (movie_original_title[-1] == '"' and movie_original_title[:2] == 'b"'):
			movie_original_title = movie_original_title[:-1]
			movie_original_title = movie_original_title[2:]
		if (movie_plot[-1] == '\'' and movie_plot[:2] == 'b\'') or (movie_plot[-1] == '"' and movie_plot[:2] == 'b"'):
			movie_plot = movie_plot[:-1]
			movie_plot = movie_plot[2:]

		movie_title = movie_original_title
		genre = movie_genre
		xbmcgui.Window(10000).setProperty('Next_EP.genre', str(genre))
		imdb = imdb_id 
		xbmcgui.Window(10000).setProperty('Next_EP.imdb', imdb)
		icon = moviethumb
		xbmcgui.Window(10000).setProperty('Next_EP.icon', icon)
		label = movie_title
		xbmcgui.Window(10000).setProperty('Next_EP.label', label)
		label2 = movie_title
		xbmcgui.Window(10000).setProperty('Next_EP.label2', label2)
		#MPAA = xbmc.getInfoLabel('listitem.MPAA')
		originaltitle = movie_original_title
		xbmcgui.Window(10000).setProperty('Next_EP.originaltitle', originaltitle)
		plot = movie_plot
		xbmcgui.Window(10000).setProperty('Next_EP.plot', plot)
		plotoutline = movie_plot
		xbmcgui.Window(10000).setProperty('Next_EP.plotoutline', plotoutline)
		premiered = movie_release_date
		xbmcgui.Window(10000).setProperty('Next_EP.premiered', premiered)
		rating = movie_vote_average
		xbmcgui.Window(10000).setProperty('Next_EP.rating', str(rating))
		movie_title = movie_title
		xbmcgui.Window(10000).setProperty('Next_EP.movie_title', movie_title)
		#rating_votes = xbmc.getInfoLabel('listitem.RatingAndVotes')
		#set = xbmc.getInfoLabel('listitem.Set')
		#setid = xbmc.getInfoLabel('listitem.SetID')
		#studio = xbmc.getInfoLabel('listitem.Studio')
		#tagline = xbmc.getInfoLabel('listitem.Tagline')
		title = movie_title.replace('b\'','').replace('  ','')
		xbmcgui.Window(10000).setProperty('Next_EP.title', title)
		#votes = xbmc.getInfoLabel('listitem.Votes')
		#writer = xbmc.getInfoLabel('listitem.Writer')
		year = movie_release_date[0:4]
		xbmcgui.Window(10000).setProperty('Next_EP.year', year)
		#percent_played = xbmc.getInfoLabel('ListItem.PercentPlayed')
		resumetime = resumeTimeInSeconds
		xbmcgui.Window(10000).setProperty('Next_EP.resumetime', str(resumetime))

		xbmcplugin.setContent(-1, 'movies')

		if (resumetime == None or resumetime == '' or resumetime == 0) and resume_progress_seconds > 0:
			resumetime = resume_progress_seconds
			resumeTimeInSeconds = resume_progress_seconds
			xbmcgui.Window(10000).setProperty('Next_EP.resumetime', str(resumetime))

		try:
			li = xbmcgui.ListItem(label, iconImage=thumb)
		except:
			li = xbmcgui.ListItem(label, thumb)
		li.setProperty('fanart_image', fanart)
		li.setProperty('startoffset', str(resumeTimeInSeconds))
		li.setProperty('DBID', dbid)
		li.setProperty('MovieTitle', movie_title)
		li.setProperty('title', movie_original_title)
		#li.setProperty('Cast', cast)
		#li.setProperty('CastAndRole', cast_role)
		li.setProperty('Duration', duration)
		li.setArt({ 'poster': poster, 'fanart': fanart, 'banner': banner, 'clearlogo': clearlogo, 'landscape': landscape, 'thumb': thumb})
		
		try:
			json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "VideoLibrary.GetMovieDetails", "params": {"movieid": '+str(dbid)+', "properties": ["art"]}}')
			json_result = json.loads(json_result)
			#xbmc.log(str(json_result['result']['episodedetails']['art'])+'===>OPENINFO', level=xbmc.LOGFATAL)
			li.setArt(json_result['result']['moviedetails']['art'])
		except:
			pass

		try:
			json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "VideoLibrary.GetMovieDetails", "params": {"movieid": '+str(dbid)+', "properties": ["title","genre","year","rating","director","trailer","tagline","plot","plotoutline","originaltitle","lastplayed","playcount","writer","studio","mpaa","cast","country","imdbnumber","runtime","set","showlink","streamdetails","top250","votes","fanart","thumbnail","file","sorttitle","resume","setid","dateadded","tag","userrating","ratings","premiered","uniqueid"]}}')
			json_result = json.loads(json_result)
			#xbmc.log(str(json_result['result']['episodedetails']['art'])+'===>OPENINFO', level=xbmc.LOGFATAL)
			#li.setInfo(type='Video', infoLabels=str(json_result['result']['moviedetails']))
			try:
				info_tag = ListItemInfoTag(li, 'video')
				info_tag.set_info(json_result['result']['moviedetails'])
			except:
				li.setInfo(type='Video', infoLabels=str(json_result['result']['moviedetails']))
		except:
			pass

		li.setProperty('IsPlayable', 'true')
		li.setProperty('IsFolder', 'false')

		#print('kodi-send --action=\"PlayMedia(\"' + BDMV + "\")\"")
		#if BDMV <> '':
		#	kodi_command = 'kodi-send --action=\"PlayMedia(\"' + BDMV + "\")\""
		#	os.system(kodi_command)
		#else:
		#	os.system('kodi-send --action=PlayDVD')
		li.setPath(BDMV)
		print_log(str(BDMV),'BDMV_path')

		"""
		li.setInfo('video', {'title': title, 'MovieTitle': movie_title, 'genre': genre, 'plotoutline': plotoutline, 'plot': plot, 'path': BDMV,'premiered': premiered, 'dbid': dbid, 'mediatype': dbtype, 'duration': duration, 'IMDBNumber': imdb, 'Rating': rating, 'Year': year})
		"""
		infolabels = {'year': None, 'premiered': None, 'aired': None, 'mpaa': None, 'genre': None, 'imdbnumber': None, 'duration': None, 'dateadded': None, 'rating': None, 'votes': None, 'tagline': None, 'mediatype': None, 'title': None, 'originaltitle': None, 'sorttitle': None, 'plot': None, 'plotoutline': None, 'studio': None, 'country': None, 'director': None, 'writer': None, 'status': None, 'trailer': None}

		response_extended_movie_info = extended_movie_info(movie_id=tmdb_id)
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
		#print_log(str(list(zip(actor_name,actor_role,actor_thumbnail,actor_order))),'zip_list')
		if len(actors) > 0:
			#li.setCast(actors)
			try:
				info_tag = ListItemInfoTag(li, 'video')
				info_tag.set_cast(actors)
			except:
				li.setCast(actors)
			li.setProperty('Cast', str(actors))
			li.setProperty('CastAndRole', str(actors))
			infolabels['Cast'] = list(zip(actor_name,actor_role,actor_thumbnail,actor_order))
			infolabels['CastAndRole'] = list(zip(actor_name,actor_role,actor_thumbnail,actor_order))
			#li.setInfo('video', {'Cast': list(zip(actor_name,actor_role,actor_thumbnail,actor_order)), 'CastAndRole': list(zip(actor_name,actor_role,actor_thumbnail,actor_order)) })
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

		infolabels['year'] = str(year)
		infolabels['premiered'] = str(premiered)+'T00:00:00'
		infolabels['aired'] = str(premiered)+'T00:00:00'
		infolabels['imdbnumber'] = imdb
		try: infolabels['duration'] = int(duration)
		except: infolabels['duration'] = int(runtime_seconds)
		infolabels['dateadded'] = str(premiered)+'T00:00:00'
		infolabels['rating'] = float(rating)
		infolabels['votes'] = int(response_extended_movie_info[0]['Votes'])
		infolabels['tagline'] = response_extended_movie_info[0]['Tagline']
		infolabels['mediatype'] = 'movie'
		infolabels['title'] = movie_title
		infolabels['originaltitle'] = movie_title
		infolabels['sorttitle'] = movie_title
		infolabels['plot'] = plot
		infolabels['plotoutline'] = plot
		infolabels['playcount'] = 0
		infolabels['director'] = director
		infolabels['writer'] = writer
		infolabels['status'] = response_extended_movie_info[0]['Status']
		infolabels['mpaa'] = response_extended_movie_info[0]['mpaa']
		infolabels['genre'] = genre
		infolabels['studio'] = studio
		infolabels['country'] = None
		infolabels['FileNameAndPath'] = BDMV
		infolabels['path'] = BDMV

		#print_log(infolabels)
		#li.setInfo(type='Video', infoLabels = infolabels)
		try:
			info_tag = ListItemInfoTag(li, 'video')
			info_tag.set_info(infolabels)
		except:
			li.setInfo(type='Video', infoLabels = infolabels)
		#info_tag.set_cast(infolabels['Cast'])
		#info_tag.set_cast(infolabels['CastAndRole'])

		playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		current_action = xbmcgui.Window(10000).getProperty('Next_EP.TMDB_action')
		playlist.clear()
		xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
		#playlist.add(BDMV, li)
		##xbmcplugin.addDirectoryItem(handle=-1, url=PTN_download , listitem=li, isFolder=False)
		#xbmcplugin.setResolvedUrl(-1, False, li)

		#xbmcplugin.addDirectoryItem(handle=-1, url=BDMV, listitem=li, isFolder=True)
		playlist.add(BDMV, li)
		xbmcplugin.setResolvedUrl(-1, True, li)
		xbmcplugin.endOfDirectory(-1)

		xbmcgui.Window(10000).clearProperty('Next_EP.TMDB_action')
		xbmcgui.Window(10000).setProperty('tmdbhelper_tvshow.poster', str(tmdbhelper_tvshow_poster))
		xbmcgui.Window(10000).setProperty('diamond_player_time', str(int(time.time())+120))
		if dvd_flag == 'False':
			xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
			#xbmc.Player().play(item=BDMV, listitem=li)
			xbmc.Player().play(playlist)
		if dvd_flag == 'True':
			xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
			#xbmc.Player().play(item=BDMV, listitem=li)
			xbmc.Player().play(playlist)
			xbmc.Player().setSubtitleStream(0)
		
		##xbmc.Player().play(item=PTN_download, listitem=li)
		#xbmc.Player().play(playlist)
		#exit()
		#return
