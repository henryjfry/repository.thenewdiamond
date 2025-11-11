import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import os
import shutil

import datetime
from datetime import date, datetime, timedelta
import time
from pathlib import Path

from inspect import currentframe, getframeinfo
#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>VOD_INFO', level=xbmc.LOGINFO)

def addon_ID():
	addonID = xbmcaddon.Addon().getAddonInfo('id')
	return addonID

def addon_ID_short():
	addonID = xbmcaddon.Addon().getAddonInfo('id')
	addonID_short = addonID.replace('script.','')
	return addonID_short

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
	tmdb_traktapi_path1 = Path(main_file_path().replace(addon_ID(),'plugin.video.themoviedb.helper') + 'resources/lib/traktapi.py')
	tmdb_traktapi_path2 = Path(main_file_path().replace(addon_ID(),'plugin.video.themoviedb.helper') + 'resources/lib/trakt/api.py')
	tmdb_traktapi_path3 = Path(main_file_path().replace(addon_ID(),'plugin.video.themoviedb.helper') + 'resources/lib/api/trakt/api.py')
	tmdb_traktapi_path4 = Path(main_file_path().replace(addon_ID(),'plugin.video.themoviedb.helper') + 'resources/tmdbhelper/lib/api/api_keys/trakt.py')
	if xbmcvfs.exists(str(tmdb_traktapi_path1)):
		return tmdb_traktapi_path1
	elif xbmcvfs.exists(str(tmdb_traktapi_path2)):
		return tmdb_traktapi_path2
	elif xbmcvfs.exists(str(tmdb_traktapi_path3)):
		return tmdb_traktapi_path3
	elif xbmcvfs.exists(str(tmdb_traktapi_path4)):
		return tmdb_traktapi_path4


def get_file(url=None,file_path=None):
	import requests
	try:
		r = requests.get(url)
		with open(file_path, 'wb') as outfile:
			outfile.write(r.content)
	except:
		pass

def db_path():
	import glob
	db_name = 'MyVideos*.db'
	path_db = 'special://profile/Database/%s' % db_name
	try: filelist = sorted(glob.glob(xbmcvfs.translatePath(path_db)))
	except AttributeError: sorted(glob(xbmcvfs.translatePath(path_db)))
	if filelist:
		return filelist[-1]

def db_connection():
	import sqlite3
	con = sqlite3.connect(db_path())
	return con

def icon_path():
	icon_path = Path(main_file_path() + 'icon2.png')
	return str(icon_path)

def tmdb_api_key():
	#return xbmcaddon.Addon('plugin.video.seren').getSetting('tmdb.apikey')#
	tmdb_API_key = xbmcaddon.Addon(addon_ID()).getSetting('tmdb_api')
	if len(tmdb_API_key) != 32:
		tmdb_API_key = 'edde6b5e41246ab79a2697cd125e1781'
	return tmdb_API_key

def fanart_api_key():
	fanart_api_key = xbmcaddon.Addon(addon_ID()).getSetting('fanart_api')
	if str(fanart_api_key) == '':
		fanart_api_key = xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('fanarttv_clientkey')
	if len(fanart_api_key) != 32:
		fanart_api_key = '184e1a2b1fe3b94935365411f919f638'
	return fanart_api_key

def show_settings_menu():
	if xbmcaddon.Addon(addon_ID()).getSetting('settings_user_config') == 'Settings Selection Menu':
		return True
	if xbmcaddon.Addon(addon_ID()).getSetting('settings_user_config') == 'TMDBHelper Context Menu':
		return False


def get_art_fanart_movie(tmdb_id, fanart_api, show_file_path, art_path,tmdb_api):
	from resources.lib.TheMovieDB import get_fanart_data
	from resources.lib.TheMovieDB import get_tmdb_data
	show_file_path = str(show_file_path)

	try: 
		response = get_fanart_data(tmdb_id=tmdb_id,media_type='movie')
	except: 
		response = ''
		

	d1 = {}
	for i in response:
	#	print(i)
		for j in response[i]:
			try: 
				lang = j['lang']
				if j['lang'] == 'en' or (i == 'movielogo' and j['lang'] == ''):
					if i == 'movielogo':
						d1['movielogo'] = j['url']
						break
				if j['lang'] == 'en' or (i == 'hdmovielogo' and j['lang'] == ''):
					if i == 'hdmovielogo':
						d1['hdmovielogo'] = j['url']
						break
				if i == 'movieposter':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['movieposter'] = k['url']
							break
				if i == 'hdmovieclearart':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['hdmovieclearart'] = k['url']
							break
				if i == 'movieart':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['movieart'] = k['url']
							break
				if i == 'moviedisc':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['moviedisc'] = k['url']
							break
				if i == 'moviebanner':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['moviebanner'] = k['url']
							break
				if i == 'moviethumb':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['moviethumb'] = k['url']
							break
				if i == 'moviebackground':
					for k in response[i]:
						if k['lang'] == 'en' or k['lang'] == '':
							d1['moviebackground'] = k['url']
							break
			except:
				pass
	#TMDB_ID - poster, fanart, season posters
	#tvposter, showbackground, seasonposters
	if not d1.__contains__('moviebackground') or not d1.__contains__('movieposter'):
		url = 'movie/'+str(tmdb_id) + '?'
		response = get_tmdb_data(url=url)

		if not d1.__contains__('moviebackground'):
			try: 
				#d1['moviebackground'] = str('https://image.tmdb.org/t/p/original') + response.json()['backdrop_path']
				d1['moviebackground'] = str('https://image.tmdb.org/t/p/w500') + response.json()['backdrop_path']
			except:
				pass

		if not d1.__contains__('movieposter'):
			try:
				#d1['movieposter'] = str('https://image.tmdb.org/t/p/original') + response.json()['poster_path']
				d1['movieposter'] = str('https://image.tmdb.org/t/p/w500') + response.json()['poster_path']
			except:
				pass

	if d1.__contains__('moviebanner'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/banner.jpg')):
			get_file(d1['moviebanner'].replace(' ', '%20'), Path(show_file_path + '/banner.jpg'))

	if d1.__contains__('hdmovielogo'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/clearlogo.png')):
			get_file(d1['hdmovielogo'].replace(' ', '%20'), Path(show_file_path + '/clearlogo.png'))
	elif d1.__contains__('movielogo'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/clearlogo.png')):
			get_file(d1['movielogo'].replace(' ', '%20'), Path(show_file_path + '/clearlogo.png'))

	if d1.__contains__('moviethumb'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/landscape.jpg')):
			get_file(d1['moviethumb'].replace(' ', '%20'), Path(show_file_path + '/landscape.jpg'))
	elif d1.__contains__('moviebackground'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/landscape.jpg')):
			get_file(d1['moviebackground'].replace(' ', '%20'), Path(show_file_path + '/landscape.jpg'))

	if d1.__contains__('moviebackground'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/fanart.jpg')):
			get_file(d1['moviebackground'].replace(' ', '%20'), Path(show_file_path + '/fanart.jpg'))
	elif d1.__contains__('moviethumb'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/fanart.jpg')):
			get_file(d1['moviethumb'].replace(' ', '%20'), Path(show_file_path + '/fanart.jpg'))

	if d1.__contains__('movieposter'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/poster.jpg')):
			get_file(d1['movieposter'].replace(' ', '%20'), Path(show_file_path + '/poster.jpg'))

def get_art_fanart_tv(tvdb_id, fanart_api, show_file_path, art_path,tmdb_id,tmdb_api):
	from resources.lib.TheMovieDB import get_fanart_data
	from resources.lib.TheMovieDB import get_tmdb_data
	d1 = {}
	show_file_path = str(show_file_path)
	try: 
		response = get_fanart_data(tmdb_id=tvdb_id,media_type='tv_tvdb')
	except: 
		response = ''

	d1 = {}
	for i in response:
		for j in response[i]:
			try: 
				lang = j['lang']
				if j['lang'] in ('en','00','')  or (i == 'showbackground' and j['lang'] == ''):
					if i == 'hdclearart' and i not in d1:
						d1['hdclearart'] = j['url']
						break
					if i == 'seasonposter' and 'seasonposters' not in d1:
						d1['seasonposters'] = {}
						for k in response[i]:
							if k['season'] != 'all':
								if k['lang'] in ('en','00','') and not d1['seasonposters'].__contains__(int(k['season'])):
									d1['seasonposters'][int(k['season'])] = k['url']
						break
					if i == 'seasonthumb' and i not in d1:
						d1['seasonthumb'] = {}
						for k in response[i]:
							if k['season'] != 'all':
								if k['lang'] in ('en','00','') and not d1['seasonthumb'].__contains__(int(k['season'])):
									d1['seasonthumb'][int(k['season'])] = k['url']
						break
					if i == 'seasonbanner' and i not in d1:
						d1['seasonbanner'] = {}
						for k in response[i]:
							if k['season'] != 'all':
								if k['lang'] in ('en','00','') and not d1['seasonbanner'].__contains__(int(k['season'])):
									d1['seasonbanner'][int(k['season'])] = k['url']
						break
					if i == 'tvthumb' and i not in d1:
						d1['tvthumb'] = j['url']
						break
					if i == 'tvbanner' and i not in d1:
						d1['tvbanner'] = j['url']
						break
					if i == 'showbackground' and i not in d1:
						d1['showbackground'] = j['url']
						break
					if i == 'clearlogo' and i not in d1:
						d1['clearlogo'] = j['url']
						break
					if i == 'characterart' and i not in d1:
						d1['characterart'] = j['url']
						break
					if i == 'tvposter' and i not in d1:
						d1['tvposter'] = j['url']
						break
					if i == 'clearart' and i not in d1:
						d1['clearart'] = j['url']
						break
					if i == 'hdtvlogo' and i not in d1:
						d1['hdtvlogo'] = j['url']
						break
			except:
				pass
				

	#TVDB_ID - poster, banner, fanart
	#tvposter, tvbanner, showbackground
	if not d1.__contains__('showbackground') or not d1.__contains__('tvposter') or not d1.__contains__('tvbanner'):
		try:
			response = requests.get('https://api.thetvdb.com/series/'+str(tvdb_id))

			if not d1.__contains__('showbackground'):
				try: 
					d1['showbackground'] = str('https://artworks.thetvdb.com/banners/') + response.json()['data']['fanart']
				except:
					pass

			if not d1.__contains__('tvposter'):
				try:
					d1['tvposter'] = str('https://artworks.thetvdb.com/banners/') + response.json()['data']['poster']
				except:
					pass
				
			if not d1.__contains__('tvbanner'):
				try:
					d1['tvbanner'] = str('https://artworks.thetvdb.com/banners/') + response.json()['data']['banner']
				except:
					pass
		except:
			pass

	#TMDB_ID - poster, fanart, season posters
	#tvposter, showbackground, seasonposters
	if not d1.__contains__('showbackground') or not d1.__contains__('tvposter') or not d1.__contains__('seasonposters'):
		url = 'tv/'+str(tmdb_id) + '?'
		response = get_tmdb_data(url=url)

		if not d1.__contains__('showbackground'):
			try: 
				d1['showbackground'] = str('https://image.tmdb.org/t/p/w500') + response.json()['backdrop_path']
				#d1['showbackground'] = str('https://image.tmdb.org/t/p/original') + response.json()['backdrop_path']
			except:
				pass

		if not d1.__contains__('tvposter'):
			try:
				d1['tvposter'] = str('https://image.tmdb.org/t/p/w500') + response.json()['poster_path']
				#d1['tvposter'] = str('https://image.tmdb.org/t/p/original') + response.json()['poster_path']
			except:
				pass
			
		if not d1.__contains__('seasonposters'):
			d1['seasonposters'] = {}
			try:
				for k in response.json()['seasons']:
					try:
						d1['seasonposters'][int(k['season_number'])] = str('https://image.tmdb.org/t/p/w500') + k['poster_path']
						#d1['seasonposters'][int(k['season_number'])] = str('https://image.tmdb.org/t/p/original') + k['poster_path']
					except:
						pass
			except:
				pass

	if d1.__contains__('tvbanner'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/banner.jpg')):
			get_file(d1['tvbanner'].replace(' ', '%20'), Path(show_file_path + '/banner.jpg'))

	if d1.__contains__('hdtvlogo'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/clearlogo.png')):
			get_file(d1['hdtvlogo'].replace(' ', '%20'), Path(show_file_path + '/clearlogo.png'))
	elif d1.__contains__('clearlogo'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/clearlogo.png')):
			get_file(d1['clearlogo'].replace(' ', '%20'), Path(show_file_path + '/clearlogo.png'))

	if d1.__contains__('tvthumb'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/landscape.jpg')):
			get_file(d1['tvthumb'].replace(' ', '%20'), Path(show_file_path + '/landscape.jpg'))
	elif d1.__contains__('showbackground'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/landscape.jpg')):
			get_file(d1['showbackground'].replace(' ', '%20'), Path(show_file_path + '/landscape.jpg'))

	if d1.__contains__('showbackground'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/fanart.jpg')):
			get_file(d1['showbackground'].replace(' ', '%20'), Path(show_file_path + '/fanart.jpg'))
	elif d1.__contains__('tvthumb'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/fanart.jpg')):
			get_file(d1['tvthumb'].replace(' ', '%20'), Path(show_file_path + '/fanart.jpg'))


	if d1.__contains__('tvposter'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/poster.jpg')):
			get_file(d1['tvposter'].replace(' ', '%20'), Path(show_file_path + '/poster.jpg'))

	if d1.__contains__('seasonbanner'):
		for i in d1['seasonbanner']:
			if i != 0:
				if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/season' + format(i, '02d') + '-banner.jpg')):
					get_file(d1['seasonbanner'][i].replace(' ', '%20'), Path(show_file_path + '/season' + format(i, '02d') + '-banner.jpg'))

	if d1.__contains__('seasonthumb'):
		for i in d1['seasonthumb']:
			if i != 0:
				if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/season' + format(i, '02d') + '-landscape.jpg')):
					get_file(d1['seasonthumb'][i].replace(' ', '%20'), Path(show_file_path + '/season' + format(i, '02d') + '-landscape.jpg'))

	if d1.__contains__('seasonposters'):
		for i in d1['seasonposters']:
			if i != 0:
				if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/season' + format(i, '02d') + '-poster.jpg')):
					get_file(d1['seasonposters'][i].replace(' ', '%20'), Path(show_file_path + '/season' + format(i, '02d') + '-poster.jpg'))
	return


def get_fanart_results(tvdb_id, media_type=None, show_season = None):
	from resources.lib.TheMovieDB import get_fanart_data
	from resources.lib.Utils import tools_log
	hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = '', '', '', '', '', '', '', '', '', '', '', '';
	tv_dict = {'hdclearart': None,'seasonposter': None,'seasonthumb': None,'seasonbanner': None,'tvthumb': None,'tvbanner': None,'showbackground': None,'clearlogo': None,'characterart': None,'tvposter': None,'clearart': None,'hdtvlogo': None}

	if 'tv_tvdb' == media_type:
		try: 
			response = get_fanart_data(tmdb_id=tvdb_id,media_type='tv_tvdb')
		except: 
			response = get_fanart_data(tmdb_id=tvdb_id,media_type='tv_tvdb')
	else:
		response = get_fanart_data(tmdb_id=tvdb_id,media_type='movie')
		
	#tools_log(tvdb_id)
	#tools_log(response)
	if 'tv_tvdb' == media_type:
		for i in response:
			if i == 'name' or i == 'thetvdb_id' or '_count' in str(i):
				continue
			for j in response[i]:
				try:
					#tools.log(j)
					if j['lang'] == 'en' or (i in ['showbackground','tvposter','tvthumb'] and j['lang'] == ''):
						if i in ('seasonposter', 'seasonthumb', 'seasonbanner'):
							for k in response[i]:
								if int(k['season']) == int(show_season) and k['lang'] == 'en':
									tv_dict[i] = k['url']
									break
					if i in ('hdclearart', 'tvthumb', 'tvbanner', 'showbackground', 'clearlogo', 'characterart', 'tvposter', 'clearart', 'hdtvlogo'):
						if i == 'clearlogo' or i == 'hdtvlogo':
							tv_dict['clearlogo'] = j['url']
							tv_dict['hdtvlogo'] = j['url']
							break
						else:
							tv_dict[i] = j['url']
							break
				except:
					continue
		#return hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo

		for i in tv_dict:
			if tv_dict[i] == None and i in ('seasonposter', 'seasonthumb', 'seasonbanner'):
				for k in response.get(i,[]):
					if str(k['season']) == 'all':
						tv_dict[i] = k['url']
						break
					if int(k['season']) == int(show_season):
						tv_dict[i] = k['url']
						break
		#tools.log(tv_dict)
		return tv_dict['hdclearart'], tv_dict['seasonposter'], tv_dict['seasonthumb'], tv_dict['seasonbanner'], tv_dict['tvthumb'], tv_dict['tvbanner'], tv_dict['showbackground'], tv_dict['clearlogo'], tv_dict['characterart'], tv_dict['tvposter'], tv_dict['clearart'], tv_dict['hdtvlogo']
	else:
		movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = '', '', '', '', '', '', '', '', ''
		movie_dict = {'movielogo': None,'hdmovielogo': None,'movieposter': None,'hdmovieclearart': None,'movieart': None,'moviedisc': None,'moviebanner': None,'moviethumb': None,'moviebackground': None}
		for i in response:
			#print_log(i)
			if '_count' in str(i):
				continue
			for j in response[i]:
				try:
					lang = j['lang']
					if j['lang'] == 'en' or (i in ['movielogo','hdmovielogo','moviebackground','moviethumb','movieposter'] and j['lang'] == ''): 
						if i in ('movielogo', 'hdmovielogo'):
							movie_dict[i] = j['url']
							break
						if i in ('movieposter','hdmovieclearart','movieart','moviedisc','moviebanner','moviethumb','moviebackground'):
							for k in response[i]:
								if k['lang'] == 'en' or (i in ['movielogo','hdmovielogo','moviebackground','moviethumb','movieposter'] and j['lang'] == ''): 
									movie_dict[i] = k['url']
									break
				except:
					pass

		#return movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground
		#tools.log(movie_dict)
		return movie_dict['movielogo'], movie_dict['hdmovielogo'], movie_dict['movieposter'], movie_dict['hdmovieclearart'], movie_dict['movieart'], movie_dict['moviedisc'], movie_dict['moviebanner'], movie_dict['moviethumb'], movie_dict['moviebackground']

def get_fanart_results_full(tvdb_id, media_type=None, show_season = None):
	#from a4kscrapers_wrapper import get_meta
	#get_fanart_results(tvdb_id, media_type=None, show_season = None)

	if 'tv_tvdb' == media_type:
		hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = '', '', '', '', '', '', '', '', '', '', '', '';
		hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = get_fanart_results(tvdb_id, media_type='tv_tvdb', show_season = show_season)
		return hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo
	else:
		movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = '', '', '', '', '', '', '', '', ''
		movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = get_fanart_results(tvdb_id, media_type='movie', show_season = None)
		return movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground




def trakt_next_episode_normal(tmdb_id_num=None):
	#import requests
	#import json

	tmdb_id=tmdb_id_num
	#headers = trak_auth()

	try:
		#response = requests.get('https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show', headers=headers).json()
		response = get_trakt_data(url='https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show', cache_days=0.5)
	except:
		xbmc.executebuiltin('Dialog.Close(busydialog)')

	id = response[0]['show']['ids']['trakt']
	title = response[0]['show']['title']

	response1 = ''
	i = 0
	while response1 == '' and i < 11:
		try:
			#response1 = requests.get('https://api.trakt.tv/shows/'+str(id)+'/progress/watched',headers=headers).json()
			response1 = get_trakt_data(url='https://api.trakt.tv/shows/'+str(id)+'/progress/watched', cache_days=0.00001)
		except:
			i = i + 1

	try:
		season = response1['next_episode']['season']
		episode = response1['next_episode']['number']
	except:
		season = '1'
		episode = '1'

	response2 = ''
	i = 0
	while response2 == '' and i < 22:
		try:
			#response2 = requests.get('https://api.trakt.tv/shows/'+str(id)+'/seasons/'+str(season)+'/episodes/'+str(episode)+'?extended=full', headers=headers).json()
			response2 = get_trakt_data(url='https://api.trakt.tv/shows/'+str(id)+'/seasons/'+str(season)+'/episodes/'+str(episode)+'?extended=full', cache_days=0.00001)
		except:
			i = i + 1

	first_aired = response2['first_aired']
	try:
			first_aired2 = datetime.strptime(first_aired, '%Y-%m-%dT%H:%M:%S.%fZ')
	except TypeError:
			first_aired2 = datetime(*(time.strptime(first_aired, '%Y-%m-%dT%H:%M:%S.%fZ')[0:6]))

	now = datetime.now()

	if first_aired2 < now:
		#url = 'RunPlugin(plugin://plugin.video.themoviedb.helper?info=play&amp;query='+str(title)+'&amp;type=episode&amp;season='+str(season)+'&amp;episode='+str(episode)+')'
		#url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id='+ str(tmdb_id) + '&amp;season='+str(season)+'&amp;episode='+str(episode)
		xbmc.executebuiltin('Dialog.Close(busydialog)')
		
		return tmdb_id, season, episode
	else:
		xbmcgui.Dialog().notification(heading='Trakt Next Episode Normal', message='Next Episode Not aired yet', icon=icon_path(),time=1000,sound=False)

def trakt_next_episode_rewatch(tmdb_id_num=None):
	#import requests
	#import json

	tmdb_id=tmdb_id_num
	#headers = trak_auth()

	#response = requests.get('https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show', headers=headers).json()
	response = get_trakt_data(url='https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show', cache_days=0.5)
	id = response[0]['show']['ids']['trakt']
	title = response[0]['show']['title']

	response1 = ''
	i = 0
	while response1 == '' and i < 11:
		try:
			#response1 = requests.get('https://api.trakt.tv/shows/'+str(id)+'/progress/watched',headers=headers).json()
			response1 = get_trakt_data('https://api.trakt.tv/shows/'+str(id)+'/progress/watched', cache_days=0.00001)
		except:
			i = i + 1

	last_watched_at = ''
	next_season_to_watch  = ''
	next_ep_to_watch = ''
	try:
		for i in response1['seasons']:
			for j in i['episodes']:
				if last_watched_at == '':
					last_watched_at = j['last_watched_at']
				if j['last_watched_at'] != None:
					if last_watched_at != '' and last_watched_at <= j['last_watched_at']:
						last_watched_at  = j['last_watched_at']
						next_season_to_watch = i['number']
						next_ep_to_watch = j['number']
	except:
		last_watched_at = ''
		next_season_to_watch  = ''
		next_ep_to_watch = ''
		import sqlite3
		#import ast
		addon = xbmcaddon.Addon()
		addon_path = addon.getAddonInfo('path')
		addonID = addon.getAddonInfo('id')
		addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
		con = sqlite3.connect(str(Path(addonUserDataFolder + '/trakt_tv_watched.db')))
		cur = con.cursor()
		sql_query = "select * from trakt where trakt  like '%" + str(title) + "%'"
		sql_result = cur.execute(sql_query).fetchall()
		#try: response1 = ast.literal_eval(sql_result[0][1].replace('\'\'','"'))
		#except: response1= None
		try: response1 = eval(sql_result[0][1].replace("'overview': ''",'\'overview\': "').replace("'', 'first_aired':",'", \'first_aired\':').replace("'title': ''",'\'title\': "').replace("'', 'year':",'", \'year\':'))
		except: response1 = None
		try:
			for i in response1['seasons']:
				for j in i['episodes']:
					if last_watched_at == '':
						last_watched_at = j['last_watched_at']
					if last_watched_at != '' and last_watched_at <= j['last_watched_at']:
						last_watched_at  = j['last_watched_at']
						next_season_to_watch = i['number']
						next_ep_to_watch = j['number']
		except:
			xbmc.executebuiltin('Dialog.Close(busydialog)')
			xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
			xbmcgui.Dialog().notification(heading='Trakt Next Episode Rewatch', message='Not REWATCHING!', icon=icon_path(),time=1000,sound=False)
			return

	next_flag = 'false'
	for i in response1['seasons']:
		for j in i['episodes']:
			if next_flag == 'true':
				last_watched_at  = j['last_watched_at']
				next_season_to_watch = i['number']
				next_ep_to_watch = j['number']
				next_flag = 'false'
				break
			try:
				if int(i['number']) == int(next_season_to_watch) and int(j['number']) == int(next_ep_to_watch):
					next_flag = 'true'
			except:
				xbmc.executebuiltin('Dialog.Close(busydialog)')
				xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
				xbmcgui.Dialog().notification(heading='Trakt Next Episode Rewatch', message='Not REWATCHING!', icon=icon_path(),time=1000,sound=False)
				return

	try:	
		season = int(next_season_to_watch)
		episode = int(next_ep_to_watch)
	except:
		season = '1'
		episode = '1'

	response2 = ''
	i = 0
	while response2 == '' and i < 22:
		try:
			#response2 = requests.get('https://api.trakt.tv/shows/'+str(id)+'/seasons/'+str(season)+'/episodes/'+str(episode)+'?extended=full', headers=headers).json()
			response2 = get_trakt_data('https://api.trakt.tv/shows/'+str(id)+'/seasons/'+str(season)+'/episodes/'+str(episode)+'?extended=full', cache_days=0.00001)
		except:
			i = i + 1

	first_aired = response2['first_aired']
	#first_aired2 = datetime.datetime.strptime(first_aired, '%Y-%m-%dT%H:%M:%S.%fZ')
	import time
	try:
		first_aired2 = datetime.strptime(first_aired, '%Y-%m-%dT%H:%M:%S.%fZ')
	except TypeError:
		first_aired2 = datetime(*(time.strptime(first_aired, '%Y-%m-%dT%H:%M:%S.%fZ')[0:6]))

	now = datetime.now()

	if first_aired2 < now:
		#url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id='+ str(tmdb_id) + '&amp;season='+str(season)+'&amp;episode='+str(episode)
		xbmc.executebuiltin('Dialog.Close(busydialog)')
		return tmdb_id, season, episode
	else:
		xbmcgui.Dialog().notification(heading='Trakt Next Episode Rewatch', message='Next Episode Not aired yet', icon=icon_path(),time=1000,sound=False)

def get_trakt_data(url='', cache_days=14, folder='Trakt'):
	from resources.lib.Utils import get_JSON_response
	headers = trak_auth()
	return get_JSON_response(url, cache_days, folder,headers=headers)

def trakt_refresh_all():
	try:
		trakt_watched_movies(cache_days=0.00001)
		trakt_watched_movies_full()
		trakt_watched_tv_shows_full()
		trakt_watched_tv_shows(cache_days=0.00001)
		#trakt_popular_shows(cache_days=0.00001)
		#trakt_popular_movies(cache_days=0.00001)
		#trakt_trending_shows(cache_days=0.00001)
		#trakt_trending_movies(cache_days=0.00001)
		#trakt_collection_shows(cache_days=0.00001)
		#trakt_collection_movies(cache_days=0.00001)
	except TypeError: 
		pass

def trakt_watched_movies(cache_days=None):
	#import requests
	#import json
	#headers = trak_auth()
	url = 'https://api.trakt.tv/sync/watched/movies'
	#response = requests.get(url, headers=headers).json()
	if cache_days:
		response = get_trakt_data(url, cache_days)
		#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>VOD_INFO', level=xbmc.LOGINFO)
	else:
		response = get_trakt_data(url, 1)
	reverse_order = True
	response = sorted(response, key=lambda k: k['last_updated_at'], reverse=reverse_order)
	return response
  
def trakt_watched_movies_full():
	#import requests
	#import json
	from pathlib import Path
	headers = trak_auth()
	addon = xbmcaddon.Addon()
	addon_path = addon.getAddonInfo('path')
	addonID = addon.getAddonInfo('id')
	addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
	url = 'https://api.trakt.tv/sync/watched/movies'
	trakt_watched_stats = xbmcaddon.Addon(addon_ID()).getSetting('trakt_watched_stats')
	if trakt_watched_stats == 'true':
		#response = requests.get(url, headers=headers).json()
		response = get_trakt_data(url=url, cache_days=0.000001)
	else:
		trakt_data = None
		return None
	import os
	if os.path.exists(Path(addonUserDataFolder + '/trakt_movies_watched.db')):
		try: os.remove(Path(addonUserDataFolder + '/trakt_movies_watched.db'))
		except PermissionError: return

	import sqlite3
	con = sqlite3.connect(str(Path(addonUserDataFolder + '/trakt_movies_watched.db')))
	cur = con.cursor()

	sql_result = cur.execute("""
	CREATE TABLE trakt (
		tmdb_id INTEGER PRIMARY KEY,
		trakt VARCHAR NOT NULL
	);
	""").fetchall()
	con.commit()

	for i in response:
		sql_result = """
		INSERT INTO trakt (tmdb_id,trakt)
		VALUES( %s,%s);
		""" % (i['movie']['ids']['tmdb'],'"'+str(i).replace('"','\'\'')+'"')
		sql_result = cur.execute(sql_result).fetchall()
		con.commit()
	cur.close()
	con.close()

def trakt_watched_tv_shows_full():
	import requests
	import json
	from pathlib import Path
	headers = trak_auth()
	addon = xbmcaddon.Addon()
	addon_path = addon.getAddonInfo('path')
	addonID = addon.getAddonInfo('id')
	addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
	url = 'https://api.trakt.tv/sync/watched/shows?extended=full'
	trakt_watched_stats = xbmcaddon.Addon(addon_ID()).getSetting('trakt_watched_stats')
	if trakt_watched_stats == 'true':
		#response = requests.get(url, headers=headers).json()
		response = get_trakt_data(url=url, cache_days=0.000001)
	else:
		trakt_data = None
		return
	import os
	if os.path.exists(Path(addonUserDataFolder + '/trakt_tv_watched.db')):
		try: os.remove(Path(addonUserDataFolder + '/trakt_tv_watched.db'))
		except PermissionError: return

	import sqlite3
	con = sqlite3.connect(str(Path(addonUserDataFolder + '/trakt_tv_watched.db')))
	cur = con.cursor()

	sql_result = cur.execute("""
	CREATE TABLE trakt (
		tmdb_id INTEGER PRIMARY KEY,
		trakt VARCHAR NOT NULL
	);
	""").fetchall()
	con.commit()

	for i in response:
		sql_result = """
		INSERT INTO trakt (tmdb_id,trakt)
		VALUES( %s,%s);
		""" % (i['show']['ids']['tmdb'],'"'+str(i).replace('"','\'\'')+'"')
		sql_result = cur.execute(sql_result).fetchall()
		con.commit()
	cur.close()
	con.close()


def trakt_watched_tv_shows_progress(cache_days=None):
	#import requests
	#import json
	#headers = trak_auth()
	url = 'https://api.trakt.tv/sync/watched/shows?extended=full'
	#response = requests.get(url, headers=headers).json()
	response = get_trakt_data(url, 0.125)

	response2 = []
	for i in response:
		x = 0
		aired_episodes = i['show']['aired_episodes']
		tmdb_id = i['show']['ids']['tmdb']
		show_title = i['show']['title']
		for j in i['seasons']:
			for k in j['episodes']:
				if int(k['plays']) >= 1:
					x = x + 1
		played_episodes = x
		if aired_episodes > played_episodes:
			response2.append(i)
			print(show_title, tmdb_id, aired_episodes, played_episodes)

	#reverse_order = True
	#response = sorted(response2, key=lambda k: k['updated_at'], reverse=reverse_order)
	return response2

def trakt_calendar_eps(cache_days=None):
	from resources.lib.TheMovieDB import extended_episode_info
	#url = 'https://api.trakt.tv/sync/playback/type?start_at=2023-09-26T00%3A00%3A00.000Z&end_at=2023-07-01T23%3A59%3A59.000Z'
	past_date = datetime.now() - timedelta(days=12)
	tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
	today = (datetime.now()).strftime('%Y-%m-%d')
	url = 'https://api.trakt.tv/calendars/my/shows/%s/14' % str(past_date.strftime('%Y-%m-%d'))
	response = get_trakt_data(url=url, cache_days=0.0001, folder='Trakt')
	listitems1 = []
	for i in reversed(response):
		ep = extended_episode_info(i['show']['ids']['tmdb'], i['episode']['season'], i['episode']['number'])
		if ep[0]['release_date'] == tomorrow:
			ep[0]['title'] = ep[0]['title'] + '**'
		if ep[0]['release_date'] == today:
			ep[0]['title'] = ep[0]['title'] + '*'
		episode_title = str('%s - S%sE%s - %s' % (i['show']['title'], str(ep[0]['season']).zfill(2), str(ep[0]['episode']).zfill(2), ep[0]['title']))
		ep[0]['tmdb_id'] = ep[1]['tvshow_id']
		ep[0]['Plot'] = episode_title + ' \n ' + ep[0]['Plot']
		ep[0]['Description'] = episode_title + ' \n ' + ep[0]['Description'] 
		listitems1.append(ep[0])
	return listitems1

def trakt_eps_movies_in_progress(cache_days=None):
	from resources.lib.TheMovieDB import get_trakt_playback
	from resources.lib.TheMovieDB import extended_episode_info
	from resources.lib.TheMovieDB import extended_movie_info
	response = get_trakt_playback('tv')
	listitems1 = []
	if response:
		for i in response:
			ep = extended_episode_info(i['show']['ids']['tmdb'], i['episode']['season'], i['episode']['number'])
			ep[0]['tmdb_id'] = ep[1]['tvshow_id']
			ep[0]['PercentPlayed'] = int(i['progress'])
			listitems1.append(ep[0])
	response = None
	response = get_trakt_playback('movie')
	if response:
		for i in response:
			mov = extended_movie_info(i['movie']['ids']['tmdb'])
			mov[0]['PercentPlayed'] = int(i['progress'])
			listitems1.append(mov[0])
	return listitems1

def trakt_watched_tv_shows(cache_days=None):
	url = 'https://api.trakt.tv/sync/watched/shows?extended=noseasons'
	response = get_trakt_data(url, 0)
	reverse_order = True
	response = sorted(response, key=lambda k: k['last_updated_at'], reverse=reverse_order)
	return response


def trakt_trending_movies(cache_days=None):
	url = 'https://api.trakt.tv/movies/trending?limit=600'
	if cache_days:
		response = get_trakt_data(url, cache_days)
	else:
		response = get_trakt_data(url, 1)
	return response

def trakt_trending_shows(cache_days=None):
	url = 'https://api.trakt.tv/shows/trending?limit=600'
	if cache_days:
		response = get_trakt_data(url, cache_days)
	else:
		response = get_trakt_data(url, 1)
	return response

def trakt_popular_movies(cache_days=None):
	url = 'https://api.trakt.tv/movies/popular?limit=600'
	if cache_days:
		response = get_trakt_data(url, cache_days)
	else:
		response = get_trakt_data(url, 1)
	return response

def trakt_popular_shows(cache_days=None):
	url = 'https://api.trakt.tv/shows/popular?limit=600'
	if cache_days:
		response = get_trakt_data(url, cache_days)
	else:
		response = get_trakt_data(url, 1)

	return response


def trakt_watched_tv_shows_progress(cache_days=None):
	url = 'https://api.trakt.tv/sync/watched/shows?extended=full'
	response = get_trakt_data(url, 0.125)

	response2 = []
	for i in response:
		x = 0
		aired_episodes = i['show']['aired_episodes']
		tmdb_id = i['show']['ids']['tmdb']
		show_title = i['show']['title']
		for j in i['seasons']:
			for k in j['episodes']:
				if int(k['plays']) >= 1:
					x = x + 1
		played_episodes = x
		if aired_episodes > played_episodes:
			response2.append(i)
			print(show_title, tmdb_id, aired_episodes, played_episodes)

	#reverse_order = True
	#response = sorted(response2, key=lambda k: k['updated_at'], reverse=reverse_order)
	return response2



def trak_auth():
	from resources.lib.trakt_api import get_trakt_auth
	from resources.lib import Utils
	#Utils.tools_log('get_trakt_auth')
	headers = get_trakt_auth()
	#Utils.tools_log(headers)
	return headers

def trak_auth_old():
	import time
	trakt_token = None
	try: trakt_token = xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('trakt_token')
	except: trakt_token = None
	vod_trakt_notice = xbmcgui.Window(10000).getProperty('vod_trakt_notice')
	if vod_trakt_notice == '':
		vod_trakt_notice = None
	if not trakt_token and vod_trakt_notice:
		return
	if not trakt_token:
		xbmcgui.Dialog().notification(heading='Trakt NOT AUTHENTICATED', message='Please go to the settings and authenticate TMDB Helper Trakt', icon=str(Path(icon_path())),time=1000,sound=False)
		xbmcgui.Window(10000).setProperty('vod_trakt_notice', str(int(time.time())))
		return None

	#import xml.etree.ElementTree as ET
	#import json

	file_path = main_file_path()
	tmdb_settings = tmdb_settings_path()
	tmdb_traktapi = tmdb_traktapi_path()

	import html
	trakt_token = xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('trakt_token')
	trakt_token = eval(html.unescape(trakt_token))
	del html

	#tree = ET.parse(tmdb_settings)
	#root = tree.getroot()

	#for child in root:
	#	if (child.attrib)['id'] == 'trakt_token':
	#		token = json.loads(child.text)
	token = trakt_token

	inFile = open(tmdb_traktapi)
	client_id = ''
	client_secret = ''
	for line in inFile:
		
		if ('self.client_id = ' in line or 'CLIENT_ID = ' in line) and client_id == '':
			client_id = line.split("'")[1]
		if ('self.client_secret = ' in line or 'CLIENT_SECRET = ' in line) and client_secret == '':
			client_secret = line.split("'")[1]

	inFile.close()

	headers = {'trakt-api-version': '2', 'trakt-api-key': client_id, 'Content-Type': 'application/json'}
	headers['Authorization'] = 'Bearer {0}'.format(token.get('access_token'))
	return headers

