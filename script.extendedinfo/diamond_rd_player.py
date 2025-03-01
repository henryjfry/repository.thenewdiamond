#!/usr/bin/python3
import requests
import time
import urllib
import urllib.parse
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, json
import sqlite3
import re
import sys

from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib.library import trak_auth
from resources.lib.TheMovieDB import get_tvshow_ids
from resources.lib.TheMovieDB import extended_episode_info
from resources.lib.TheMovieDB import extended_tvshow_info
from resources.lib.TheMovieDB import get_trakt_playback

from resources.lib.library import db_connection

from resources.lib.Utils import get_JSON_response
from resources.lib.TheMovieDB import get_fanart_data
from resources.lib.TheMovieDB import get_tmdb_data

from resources.lib.library import get_processor_info

try:
	from infotagger.listitem import ListItemInfoTag
except:
	pass

import sys
if sys.version_info[0] >= 3:
	unicode = str
	basestring = str

from resources import PTN
import re
regex = re.compile('[^a-zA-Z0-9]')

from os.path import expanduser
home = expanduser("~")

from pathlib import Path
import os.path
import subprocess
from inspect import currentframe, getframeinfo
script_path = os.path.dirname(os.path.abspath(getframeinfo(currentframe()).filename))
#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))

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
	#print_log(sys.argv)

def RD_api():
	RD_api = xbmcaddon.Addon(addon_ID()).getSetting('RD_api')
	return RD_api

def RD_header():
	header = {'Authorization': 'Bearer ' + RD_api()}
	return header
	
	
def RD_get_page(page,rd_type=None):
	params = {'page': page+1}
	response = requests.get('https://api.real-debrid.com/rest/1.0/' + rd_type, headers=RD_header(), params=params).json()
	return response

def RD_instantAvailability(torr_hash):
	torr_response = requests.get('https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/' + torr_hash, headers=RD_header()).json()
	return torr_response

def RD_torrents_info(id):
	torr_response3 = requests.get('https://api.real-debrid.com/rest/1.0/torrents/info/' + str(id), headers=RD_header()).json()
	return torr_response3

def RD_unrestrict_link(file_link):
	params = {'link': file_link}
	torr_unrestricted = requests.post('https://api.real-debrid.com/rest/1.0/unrestrict/link', headers=RD_header(), data=params).json()
	return torr_unrestricted

def RD_downloads_delete(RD_link):
	torr_link = requests.delete('https://api.real-debrid.com/rest/1.0/downloads/delete/' + RD_link, headers=RD_header())
	return torr_link

def tmdb_api():
	tmdb_api = xbmcaddon.Addon(addon_ID()).getSetting('tmdb_api')
	return tmdb_api

def fanart_api():
	fanart_api = xbmcaddon.Addon(addon_ID()).getSetting('fanart_api')
	return fanart_api

def print_log(log_item1, log_item2=None):
	xbmc.log(str(log_item1)+str(log_item2)+'===>OPENINFO', level=xbmc.LOGFATAL)

def get_fanart_results(tvdb_id, media_type=None):
	hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = '', '', '', '', '', '', '', '', '', '', '', '';

	if 'tv_tvdb' == media_type:
		try: 
			#response = requests.get('http://webservice.fanart.tv/v3/tv/'+str(tvdb_id)+'?api_key='+str(fanart_api)).json()
			response = get_fanart_data(tmdb_id=tvdb_id,media_type='tv_tvdb')
			#print_log(str(response)+'===>OPENINFO')
		except: 
			response = None
	else:
		#response = requests.get('http://webservice.fanart.tv/v3/movies/'+str(tmdb_id)+'?api_key='+str(fanart_api)).json()
		response = get_fanart_data(tmdb_id=tvdb_id,media_type='movie')
	
	if 'tv_tvdb' == media_type:
		for i in response:
			#print_log(i)
			for j in response[i]:
				try: 
					lang = j['lang']
					if j['lang'] == 'en' or (i == 'showbackground' and j['lang'] == ''):
						if i == 'hdclearart':
							hdclearart = j['url']
							break
						if i == 'seasonposter':
							for k in response[i]:
								if int(k['season']) == show_season and k['lang'] == 'en':
									#print_log(k['season'])
									seasonposter = k['url']
							break
						if i == 'seasonthumb':
							for k in response[i]:
								if int(k['season']) == show_season and k['lang'] == 'en':
									#print_log(k['season'])
									seasonthumb = k['url']
							break
						if i == 'seasonbanner':
							for k in response[i]:
								if int(k['season']) == show_season and k['lang'] == 'en':
									#print_log(k['season'])
									seasonbanner = k['url']
							break
						if i == 'tvthumb':
							tvthumb = j['url']
							break
						if i == 'tvbanner':
							tvbanner = j['url']
							break
						if i == 'showbackground':
							showbackground = j['url']
							break
						if i == 'clearlogo':
							clearlogo = j['url']
							break
						if i == 'characterart':
							characterart = j['url']
							break
						if i == 'tvposter':
							tvposter = j['url']
							break
						if i == 'clearart':
							clearart = j['url']
							break
						if i == 'hdtvlogo':
							hdtvlogo = j['url']
							break
				except:
					pass
		return hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo
	else:
		movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = '', '', '', '', '', '', '', '', ''
		for i in response:
			#print_log(i)
			for j in response[i]:
				try: 
					lang = j['lang']
					if j['lang'] == 'en' or (i == 'movielogo' and j['lang'] == ''):
						if i == 'movielogo':
							movielogo = j['url']
							break
					if j['lang'] == 'en' or (i == 'hdmovielogo' and j['lang'] == ''):
						if i == 'hdmovielogo':
							hdmovielogo = j['url']
							break
					if i == 'movieposter':
						for k in response[i]:
							if k['lang'] == 'en':
								movieposter = k['url']
								break
					if i == 'hdmovieclearart':
						for k in response[i]:
							if k['lang'] == 'en':
								hdmovieclearart = k['url']
								break
					if i == 'movieart':
						for k in response[i]:
							if k['lang'] == 'en':
								movieart = k['url']
								break
					if i == 'moviedisc':
						for k in response[i]:
							if k['lang'] == 'en':
								moviedisc = k['url']
								break
					if i == 'moviebanner':
						for k in response[i]:
							if k['lang'] == 'en':
								moviebanner = k['url']
								break
					if i == 'moviethumb':
						for k in response[i]:
							if k['lang'] == 'en':
								moviethumb = k['url']
								break
					if i == 'moviebackground':
						for k in response[i]:
							if k['lang'] == 'en' or k['lang'] == '':
								moviebackground = k['url']
								break
				except:
					pass
		return movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground



def prescrape_seren(tmdb=None, season=None, episode=None):
	from resources.lib.library import get_trakt_data
	headers = trak_auth()
	tmdb_id = tmdb
	url = 'https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show'
	#response = requests.get(url, headers=headers)
	#response = response.json()
	response = get_trakt_data(url=url, cache_days=14, folder='Trakt')
	#print_log(response)
	trakt_show_id = response[0]['show']['ids']['trakt']
	url = 'https://api.trakt.tv/shows/'+str(trakt_show_id)+'/seasons'
	#response = requests.get(url, headers=headers).json()
	response = get_trakt_data(url=url, cache_days=14, folder='Trakt')
	#print_log(response)
	for i in response:
		if str(i['number']) == str(season):
			trakt_season_id = i['ids']['trakt']
	url = 'https://api.trakt.tv/shows/'+str(trakt_show_id)+'/seasons/'+str(season)+'/episodes/' + str(episode)
	#response = requests.get(url, headers=headers).json()
	response = get_trakt_data(url=url, cache_days=14, folder='Trakt')
	trakt_episode_id = response['ids']['trakt']
	action_args={'mediatype': 'episode', 'trakt_id': trakt_episode_id, 'trakt_season_id': trakt_season_id, 'trakt_show_id': trakt_show_id}

	#plugin://plugin.video.seren/?action=preScrape_diamond&action_args={"mediatype": "episode", "trakt_id": 40983, "trakt_season_id": 2207, "trakt_show_id": 653}&from_widget=true
	#xbmcgui.Window(10000).clearProperty('seren_stream_link')
	#xbmcgui.Window(10000).clearProperty('seren_prescrape')
	#xbmcgui.Window(10000).setProperty('seren_prescrape', 'True')
	#print_log(str(action_args)+'===>OPENINFO')
	#query = str('RunPlugin(%splugin://plugin.video.seren/?action=preScrape_diamond&action_args=%s&from_widget=true%s)' % ('"',urllib.parse.quote(str(action_args)),'"'))
	
	xbmcgui.Window(10000).setProperty('plugin.video.seren.runtime.tempSilent', 'True')
	try: seren_version = xbmcaddon.Addon('plugin.video.seren').getAddonInfo("version")
	except: seren_version = ''
	xbmcgui.Window(10000).setProperty('plugin.video.seren.%s.runtime.tempSilent' % (str(seren_version)), 'True')
	url = 'plugin://plugin.video.seren/?action=preScrape&action_args=%257B%2522mediatype%2522%253A%2520%2522episode%2522%252C%2520%2522trakt_id%2522%253A%2520'+str(trakt_episode_id)+'%252C%2520%2522trakt_season_id%2522%253A%2520'+str(trakt_season_id)+'%252C%2520%2522trakt_show_id%2522%253A%2520'+str(trakt_show_id)+'%257D&from_widget=true'
	query = str("RunPlugin(%s)" % (url))
	kodi_send_command = 'kodi-send --action="RunPlugin(%s)"' % (url)
	print_log(str(kodi_send_command)+'_SEREN_URL===>OPENINFO')
	#urllib.parse.quote(query)
	#print_log(str(query)+'===>OPENINFO')
	xbmc.executebuiltin(query)
	return
	#seren_stream_link = xbmcgui.Window(10000).getProperty('seren_stream_link')
	#seren_prescrape = xbmcgui.Window(10000).getProperty('seren_prescrape')
	#count = 0
	#while seren_prescrape == 'True' and count < 90 * 1000:
	#	xbmc.sleep(500)
	#	seren_stream_link = xbmcgui.Window(10000).getProperty('seren_stream_link')
	#	seren_prescrape = xbmcgui.Window(10000).getProperty('seren_prescrape')
	#	print_log(str(seren_stream_link)+'seren_stream_link===>OPENINFO')
	#	#print_log(str(seren_prescrape)+'seren_stream_link===>OPENINFO')
	#	count = count + 500
	#	if seren_stream_link != '':
	#		xbmcgui.Window(10000).clearProperty('seren_stream_link')
	#		xbmcgui.Window(10000).clearProperty('seren_prescrape')
	#		break
	#return seren_stream_link

def download_movie_test(meta_info, filename):
	x265_enabled = meta_info['x265_enabled']
	meta_info_flags = {}
	filename = str(u''.join(filename).encode('utf-8').decode('utf-8').strip()).lower() 
	ptn_data = PTN.parse(filename.replace('_','.').replace('-',' ').replace('.',' '))
	movie_title_clean = meta_info['movie_title_clean']
	#print_log(movie_title_clean)
	try:
		PTN_excess = str(ptn_data['excess']).replace('u\'',' ').replace('\'','').replace(',','').replace(']','').replace('[','').replace('  ',' ')
	except:
		PTN_excess = ''
	if '265' in filename or 'hevc' in filename or 'hdr' in filename or 'hi10' in filename:
		x265_flag = 'True'
	else:
		x265_flag = 'False'
	if x265_enabled == 'True' or x265_enabled == 'true' or x265_enabled == True:
		x265_flag = 'False'
	try: PTN_title = regex.sub(' ', ptn_data['title']).replace('  ',' ').lower()
	except: PTN_title = ''
	meta_info_flags['x265_flag'] = x265_flag
	meta_info_flags['PTN_title'] = PTN_title
	
	try: PTN_res = ptn_data['resolution']
	except: PTN_res = ''
	meta_info_flags['PTN_res'] = PTN_res
	try: PTN_season = ptn_data['season']
	except: PTN_season = ''
	try: PTN_episode = ptn_data['episode']
	except: PTN_episode = ''
	if PTN_season != '' and PTN_episode == '':
		PTN_season = ''
	elif PTN_season == '' and PTN_episode != '':
		PTN_episode == ''
	meta_info_flags['PTN_season'] = PTN_season
	meta_info_flags['PTN_episode'] = PTN_episode
	meta_info_flags['PTN_excess'] = PTN_excess

	if str(movie_title_clean) in str(ptn_data).lower() or str(movie_title_clean) in str(PTN_excess).lower():
		PTN_title = movie_title_clean
		meta_info_flags['PTN_title'] = PTN_title
	for xi in meta_info['alternate_titles']:
		try: 
			test_title = xi.replace('-','').replace(':','').replace('։','').replace('  ',' ').strip()
			if str(test_title).lower() in str(ptn_data).lower():
				PTN_title = movie_title_clean
				meta_info_flags['PTN_title'] = PTN_title
				break
			if (str(u''.join(test_title).encode('utf-8').strip()).lower() in str(ptn_data).lower() or str(u''.join(test_title).encode('utf-8').strip()).lower() in str(PTN_excess).lower()) and str(u''.join(test_title).encode('utf-8').strip()).replace(' ','') != '':
				PTN_title = movie_title_clean
				meta_info_flags['PTN_title'] = PTN_title
				break
			if (str(u''.join(test_title).encode('utf-8').strip()).lower() in str(ptn_data).lower() or str(u''.join(test_title).encode('utf-8').strip()).lower() in str(PTN_excess).lower()) and str(u''.join(test_title).encode('utf-8').strip()).replace(' ','') != '':
				PTN_title = movie_title_clean
				meta_info_flags['PTN_title'] = PTN_title
				break
		except:
			pass
	#print_log(filename, meta_info)
	#print_log(filename, meta_info_flags)
	return meta_info_flags



def download_tv_test(meta_info, filename):
	meta_info['x265_enabled'] = xbmcaddon.Addon(addon_ID()).getSetting('x265_setting')
	#if x265_setting == 'true':
	#	x265_setting = True
	#else:
	#	x265_setting = False
	alternate_titles_flag = False
	meta_info['episode_list2'] = []
	if meta_info['part1_part2_flag'] == 2:
		show_season = int(meta_info['show_season'])
		show_episode = int(meta_info['show_episode'])
		if show_episode > 1:
			show_episode = show_episode -1
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+'E'+str(show_episode).zfill(1))
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+'E'+str(show_episode).zfill(2))
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+'E'+str(show_episode).zfill(3))
			meta_info['episode_list2'].append('S'+str(show_season).zfill(2)+'E'+str(show_episode).zfill(2))
			meta_info['episode_list2'].append('S'+str(show_season).zfill(2)+'E'+str(show_episode).zfill(3))
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+'EP'+str(show_episode).zfill(1))
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+'EP'+str(show_episode).zfill(2))
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+'EP'+str(show_episode).zfill(3))
			meta_info['episode_list2'].append('S'+str(show_season).zfill(2)+'EP'+str(show_episode).zfill(2))
			meta_info['episode_list2'].append('S'+str(show_season).zfill(2)+'EP'+str(show_episode).zfill(3))
			meta_info['episode_list2'].append(str(show_season).zfill(1)+'x'+str(show_episode).zfill(1))
			meta_info['episode_list2'].append(str(show_season).zfill(1)+'x'+str(show_episode).zfill(2))
			meta_info['episode_list2'].append(str(show_season).zfill(1)+'x'+str(show_episode).zfill(3))
			meta_info['episode_list2'].append(str(show_season).zfill(2)+'x'+str(show_episode).zfill(2))
			meta_info['episode_list2'].append(str(show_season).zfill(2)+'x'+str(show_episode).zfill(3))

			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+' - '+str(show_episode).zfill(1) + '\'')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+' - '+str(show_episode).zfill(2) + '\'')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+' - '+str(show_episode).zfill(3) + '\'')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(2)+' - '+str(show_episode).zfill(2) + '\'')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(2)+' - '+str(show_episode).zfill(3) + '\'')

			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+' - E'+str(show_episode).zfill(1) + '\'')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+' - E'+str(show_episode).zfill(2) + '\'')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+' - E'+str(show_episode).zfill(3) + '\'')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(2)+' - E'+str(show_episode).zfill(2) + '\'')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(2)+' - E'+str(show_episode).zfill(3) + '\'')

			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+' - '+str(show_episode).zfill(1) + '.')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+' - '+str(show_episode).zfill(2) + '.')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+' - '+str(show_episode).zfill(3) + '.')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(2)+' - '+str(show_episode).zfill(2) + '.')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(2)+' - '+str(show_episode).zfill(3) + '.')

			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+' - E'+str(show_episode).zfill(1) + '.')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+' - E'+str(show_episode).zfill(2) + '.')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(1)+' - E'+str(show_episode).zfill(3) + '.')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(2)+' - E'+str(show_episode).zfill(2) + '.')
			meta_info['episode_list2'].append('S'+str(show_season).zfill(2)+' - E'+str(show_episode).zfill(3) + '.')

	for xi in meta_info['alternate_titles']:
		alternate_title = regex.sub(' ', xi.replace('\'s','s').replace('&','and')).replace('  ',' ').lower()
		if alternate_title.replace(' ','') == '':
			continue
		if alternate_title in filename:
			alternate_titles_flag = True
		elif str(xi).lower() in filename:
			alternate_titles_flag = True
		if alternate_titles_flag == True:
			break
	episode_list_flag = False
	for xi in meta_info['episode_list']:
		if str(xi).lower() in filename:
			episode_list_flag = True
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
			break
	episode_list_flag2 = False
	for xi in meta_info['episode_list2']:
		if str(xi).lower() in filename:
			episode_list_flag2 = True
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
			break
	season_list_flag = False
	for xi in meta_info['season_list']:
		if str(xi).lower() in filename:
			season_list_flag = True
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
			break
	episode_name_flag = False
	if str(meta_info['episode_name']).lower() in filename or str(meta_info['clean_episode_name']).lower() in filename:
		if meta_info['episode_name'] in meta_info['alternate_titles']:
			episode_name_flag = False
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
		else:
			episode_name_flag = True
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))

	if episode_name_flag == False:
		name_word_list = meta_info['clean_episode_name'].split(' ')
		show_title_split = str(meta_info['show_title']).lower().split(' ')
		word_count = 0
		total_word_count = 0
		three_word_count = 0
		three_total_word_count = 0
		for i in name_word_list:
			if str(i) in filename and len(i) > 3 and not str(i) in show_title_split:
				word_count = word_count + 1
			if len(i) > 3:
				total_word_count = total_word_count + 1
			if str(i) in filename and len(i) >= 3 and not str(i) in show_title_split:
				three_word_count = three_word_count + 1
			if len(i) >= 3:
				three_total_word_count = three_total_word_count + 1

		#if len(name_word_list) <= 3 and len(name_word_list) > 1:
		#	if word_count >= len(name_word_list) - 1:
		#		episode_name_flag = True
		if len(name_word_list) > 3:
			if word_count >= len(name_word_list) -2:
				episode_name_flag = True
			if three_word_count >= len(name_word_list) -1:
				episode_name_flag = True
		if total_word_count >= 1 and word_count == total_word_count and len(name_word_list) -2 <= total_word_count:
			episode_name_flag = True

	if episode_list_flag == True and episode_name_flag == False:
		for xi in meta_info['season_ep_titles']:
			if str(xi).lower() in str(meta_info['alternate_titles']).lower() or str(xi).lower() in str(meta_info['show_title']).lower() or str(xi).lower() in str(meta_info['show_title_clean']).lower():
				continue
			clean_episode_name = regex.sub(' ', xi.replace('\'s','s').replace('&','and')).replace('  ',' ').lower()
			clean_episode_name = str(clean_episode_name).lower().replace('part ii','').replace('part 1','').replace('part 2','').replace('part i','').strip()
			if len(xi) > 1 and not xi in meta_info['alternate_titles'] and (str(xi).lower() in filename or str(clean_episode_name).lower() in filename):
				episode_list_flag = False
				#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
				break

	if episode_list_flag == False and episode_name_flag == True:
		if season_list_flag == False:
			episode_name_flag = False
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))

	show_title_flag = False
	if str(meta_info['show_title']).lower() in filename or str(meta_info['show_title_clean']).lower() in filename:
		show_title_flag = True
		#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	if show_title_flag == False:
		show_title_match = 0
		show_title_split = str(meta_info['show_title_clean']).lower().split(' ')
		for i in show_title_split:
			if i in filename:
				show_title_match = show_title_match + 1
		if show_title_match >= len(show_title_split)-1 and len(show_title_split)>2:
			show_title_flag = True
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))

	#if alternate_titles_flag ==True and show_title_flag == False:
	#	show_title_flag = True
	#	alternate_titles_flag = False

	part1_part2_match_flag = False
	if meta_info['part1_part2_flag'] > 0:
		regex_parts = re.compile('(part[^a-zA-Z]).*'+str(meta_info['part1_part2_flag']))
		regex_parts_match = regex_parts.search(filename)
		meta_info['regex_parts_match'] = regex_parts_match
		if regex_parts_match:
			part1_part2_match_flag = True
		elif meta_info['part1_part2_flag'] == 1 and not 'part' in filename:
			if episode_list_flag == True and episode_name_flag == True:
				part1_part2_match_flag = True
		elif meta_info['part1_part2_flag'] == 2 and (not 'part' in filename or meta_info['last_episode_flag'] == True):
			if episode_list_flag == True and episode_name_flag == True:
				part1_part2_match_flag = True
	elif meta_info['part1_part2_flag'] == 0:
		part1_part2_match_flag = True
	x265_match_pass = False
	if meta_info['x265_enabled'] == 'True' or meta_info['x265_enabled'] == 'true' or meta_info['x265_enabled'] == True:
		x265_match_pass = True
	elif meta_info['x265_enabled'] == 'False' or meta_info['x265_enabled'] == 'false' or meta_info['x265_enabled'] == False:
		if '265' in filename or 'hevc' in filename or 'hdr' in filename or 'hi10' in filename:
			x265_match_pass = False
		else:
			x265_match_pass = True

	#if x265_setting:
	#	if x265_match_pass ==  False:
	#		x265_match_pass = True

	if meta_info['part1_part2_flag'] == 2 and part1_part2_match_flag == False and episode_list_flag ==  True:
		regex_part_1 = re.compile('(part[^a-zA-Z]).*'+str(1))
		regex_part_1_match = regex_part_1.search(filename)
		meta_info['regex_part_1_match'] = regex_part_1_match
		regex_part_i = re.compile('(part[^a-zA-Z]).*'+str('i'))
		regex_part_i_match = regex_part_i.search(filename)
		meta_info['regex_part_i_match'] = regex_part_i_match
		regex_part_2 = re.compile('(part[^a-zA-Z]).*'+str(2))
		regex_part_2_match = regex_part_2.search(filename)
		meta_info['regex_part_2_match'] = regex_part_2_match
		regex_part_ii = re.compile('(part[^a-zA-Z]).*'+str('ii'))
		regex_part_ii_match = regex_part_ii.search(filename)
		meta_info['regex_part_ii_match'] = regex_part_ii_match
		if regex_part_1_match or regex_part_i_match:
			if not regex_part_2_match and not regex_part_ii_match:
				episode_list_flag = False
				#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	if part1_part2_match_flag == False:
		regex_part_check = re.compile('([^a-zA-Z]part[^a-zA-Z]).*')
		regex_part_check_match = regex_part_check.search(filename)
		meta_info['regex_part_check_match'] = regex_part_check_match
		if regex_part_check_match == None or episode_name_flag == True:
			if episode_list_flag == True and season_list_flag == True and (show_title_flag == True or alternate_titles_flag == True):
				part1_part2_match_flag = True
	
	if episode_name_flag == True and part1_part2_match_flag == True and (show_title_flag == False and alternate_titles_flag == False):
		episode_name_flag = False
		#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
		if episode_list_flag == True:
			episode_list_flag = False
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
		if season_list_flag == True:
			season_list_flag = False

	if episode_list_flag2 == True and episode_list_flag == False:
		if part1_part2_match_flag == True and episode_name_flag == True:
			episode_list_flag == True
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))

	if show_title_flag == True or alternate_titles_flag == True:
		if alternate_titles_flag == False:
			alternate_titles_flag = True
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
		if show_title_flag == False:
			show_title_flag = True
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
		if episode_list_flag == False and season_list_flag == True and episode_name_flag == False and part1_part2_match_flag == True:
			season_list_flag = False
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	if part1_part2_match_flag == False and episode_list_flag == False:
		if episode_name_flag == True and (alternate_titles_flag == True or show_title_flag == True):
			episode_name_flag = False
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
			if alternate_titles_flag == True:
				alternate_titles_flag = False
				#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
			if show_title_flag == True:
				show_title_flag = False
				#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))

	meta_info_flags = {'x265_match_pass': x265_match_pass,'alternate_titles_flag': alternate_titles_flag,'episode_list_flag': episode_list_flag,'season_list_flag': season_list_flag,'episode_name_flag': episode_name_flag,'show_title_flag': show_title_flag,'part1_part2_match_flag': part1_part2_match_flag}
	#if (show_title_flag == True or alternate_titles_flag == True):# and season_list_flag == True:
	#	print_log(filename, meta_info)
	#	print_log(filename, meta_info_flags)
	return meta_info_flags

def get_next_ep_details(show_title, show_curr_season, show_curr_episode, tmdb):
	xbmcgui.Window(10000).clearProperty('Next_EP.ResolvedUrl')
	season_num = show_curr_season
	ep_num = show_curr_episode
	external_ids = get_tvshow_ids(tvshow_id=tmdb, cache_time=14)
	tvdb_id = external_ids['tvdb_id']
	tmdb_id = tmdb
	url = 'http://api.tvmaze.com/lookup/shows?thetvdb='+str(tvdb_id)
	response = get_JSON_response(url=url, cache_days=7.0, folder='TVMaze')

	show_id = response['id']
	url = 'http://api.tvmaze.com/shows/'+str(show_id)+'/episodes'
	response = get_JSON_response(url=url, cache_days=7.0, folder='TVMaze')
	for i in response:
		if i['season'] == int(season_num) and i['number'] == int(ep_num):
			curr_episode_id =  i['id']
		if i['season'] == int(season_num) and i['number'] == int(ep_num)+1:
			next_episode_id =  i['id']
			break
		if i['season'] == int(season_num)+1 and i['number'] == 1:
			next_episode_id =  i['id']
			break

	try: episode_id = next_episode_id 
	except: return None

	url = 'http://api.tvmaze.com/episodes/'+str(episode_id)+'?embed=show'
	response = get_JSON_response(url=url, cache_days=7.0, folder='TVMaze')
	try:
		next_ep_show = response['_embedded']['show']['name']
	except:
		next_ep_show = str(u''.join(response['_embedded']['show']['name']).encode('utf-8').strip())
	if (next_ep_show[-1] == '\'' and next_ep_show[:2] == 'b\'') or (next_ep_show[-1] == '"' and next_ep_show[:2] == 'b"'):
		next_ep_show = next_ep_show[:-1]
		next_ep_show = next_ep_show[2:]
	next_ep_season = response['season']
	next_ep_episode = response['number']
	try: next_ep_thumbnail = response['image']['medium']
	except: next_ep_thumbnail = None
	try:
		next_ep_title  = response['name']
	except:
		next_ep_title  = str(u''.join(response['name']).encode('utf-8').strip())
	if next_ep_title[-1] == '\'' and next_ep_title[:2] == 'b\'':
		next_ep_title = next_ep_title[:-1]
		next_ep_title = next_ep_title[2:]
	next_ep_rating = response['rating']['average']
	try: 
		response2 = extended_episode_info(tvshow_id=tmdb_id, season=next_ep_season, episode=next_ep_episode, cache_time=7)
		next_ep_rating2 = str(response2[0]['Rating'])
		next_ep_thumb2 = str(response2[0]['still_original'])
	except:
		next_ep_rating2 = ''
		next_ep_thumb2 = ''

	next_ep_year = response['airdate'][0:4]
	next_ep_genre = response['_embedded']['show']['genres']
	#air_date = response['airstamp'].split('T')[0]
	air_date = response['airdate']
	#plot = response['summary'].replace('<p>','').replace('</p>','')
	#runtime = response['runtime']
	#tvmaze_thumb_large = response['image']['medium'].replace('medium','large')
	#tvmaze_thumb_original = response['image']['original'].replace('medium','large')
	strm_title = str(next_ep_show)+' - S'+str(next_ep_season)+'E'+str(next_ep_episode)+' - '+str(next_ep_title)
	xbmc.log(str(next_ep_show)+' - S'+str(next_ep_season)+'E'+str(next_ep_episode)+' - '+str(next_ep_title)+'===diamond_rd_player.py', level=xbmc.LOGFATAL)
	next_ep_details = {}
	next_ep_details['next_ep_show'] = next_ep_show
	next_ep_details['next_ep_season'] = next_ep_season
	next_ep_details['next_ep_episode'] = next_ep_episode
	next_ep_details['next_ep_title'] = next_ep_title
	if next_ep_thumbnail:
		next_ep_details['next_ep_thumbnail'] = next_ep_thumbnail
	else:
		next_ep_details['next_ep_thumbnail'] = next_ep_thumb2
	next_ep_details['tmdb_id'] = tmdb_id
	next_ep_details['tvdb_id'] = tvdb_id
	next_ep_details['next_ep_genre'] = next_ep_genre
	next_ep_details['next_ep_year'] = next_ep_year
	next_ep_details['air_date'] = air_date
	next_ep_details['strm_title'] = strm_title
	next_ep_details['next_ep_thumb2'] = next_ep_thumb2
	next_ep_details['next_ep_rating'] = next_ep_rating
	next_ep_details['next_ep_rating2'] = next_ep_rating2
	print_log(next_ep_details)
	return next_ep_details

def season_list_episode_list_1(show_season=None, show_episode=None):
	#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	season_list = []
	#season_list.append(str(show_season).zfill(1))
	#season_list.append(str(show_season).zfill(2))
	season_list.append('S'+str(show_season).zfill(1))
	season_list.append('S'+str(show_season).zfill(2))
	season_list.append('Season '+str(show_season).zfill(1))
	season_list.append('Season '+str(show_season).zfill(2))
	season_list.append('Season.'+str(show_season).zfill(1))
	season_list.append('Season.'+str(show_season).zfill(2))

	episode_list = []
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(show_episode).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(show_episode).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(show_episode).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(show_episode).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(show_episode).zfill(3))
	episode_list.append('S'+str(show_season).zfill(1)+'EP'+str(show_episode).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'EP'+str(show_episode).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'EP'+str(show_episode).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'EP'+str(show_episode).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'EP'+str(show_episode).zfill(3))
	episode_list.append(str(show_season).zfill(1)+'x'+str(show_episode).zfill(1))
	episode_list.append(str(show_season).zfill(1)+'x'+str(show_episode).zfill(2))
	episode_list.append(str(show_season).zfill(1)+'x'+str(show_episode).zfill(3))
	episode_list.append(str(show_season).zfill(2)+'x'+str(show_episode).zfill(2))
	episode_list.append(str(show_season).zfill(2)+'x'+str(show_episode).zfill(3))

	episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode).zfill(1) + '\'')
	episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode).zfill(2) + '\'')
	episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode).zfill(3) + '\'')
	episode_list.append('S'+str(show_season).zfill(2)+' - '+str(show_episode).zfill(2) + '\'')
	episode_list.append('S'+str(show_season).zfill(2)+' - '+str(show_episode).zfill(3) + '\'')

	episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode).zfill(1) + '\'')
	episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode).zfill(2) + '\'')
	episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode).zfill(3) + '\'')
	episode_list.append('S'+str(show_season).zfill(2)+' - E'+str(show_episode).zfill(2) + '\'')
	episode_list.append('S'+str(show_season).zfill(2)+' - E'+str(show_episode).zfill(3) + '\'')

	episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode).zfill(1) + '.')
	episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode).zfill(2) + '.')
	episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode).zfill(3) + '.')
	episode_list.append('S'+str(show_season).zfill(2)+' - '+str(show_episode).zfill(2) + '.')
	episode_list.append('S'+str(show_season).zfill(2)+' - '+str(show_episode).zfill(3) + '.')

	episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode).zfill(1) + '.')
	episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode).zfill(2) + '.')
	episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode).zfill(3) + '.')
	episode_list.append('S'+str(show_season).zfill(2)+' - E'+str(show_episode).zfill(2) + '.')
	episode_list.append('S'+str(show_season).zfill(2)+' - E'+str(show_episode).zfill(3) + '.')

	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)-1).zfill(1)+'-E'+str(show_episode).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)).zfill(1)+'-E'+str(int(show_episode)+1).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)-1).zfill(2)+'-E'+str(show_episode).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)-1).zfill(3)+'-E'+str(show_episode).zfill(3))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)).zfill(2)+'-E'+str(int(show_episode)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)).zfill(3)+'-E'+str(int(show_episode)+1).zfill(3))

	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)-1).zfill(1)+'E'+str(show_episode).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)).zfill(1)+'E'+str(int(show_episode)+1).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)-1).zfill(2)+'E'+str(show_episode).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)-1).zfill(3)+'E'+str(show_episode).zfill(3))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)).zfill(2)+'E'+str(int(show_episode)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)).zfill(3)+'E'+str(int(show_episode)+1).zfill(3))

	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)-1).zfill(2)+'-E'+str(show_episode).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)-1).zfill(3)+'-E'+str(show_episode).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)).zfill(2)+'-E'+str(int(show_episode)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)).zfill(3)+'-E'+str(int(show_episode)+1).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)-1).zfill(1)+'-E'+str(show_episode).zfill(1))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)).zfill(1)+'-E'+str(int(show_episode)+1).zfill(1))

	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)-1).zfill(2)+'E'+str(show_episode).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)-1).zfill(3)+'E'+str(show_episode).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)).zfill(2)+'E'+str(int(show_episode)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)).zfill(3)+'E'+str(int(show_episode)+1).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)-1).zfill(1)+'E'+str(show_episode).zfill(1))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)).zfill(1)+'E'+str(int(show_episode)+1).zfill(1))
	
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)-1).zfill(1)+'&'+str(show_episode).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)).zfill(1)+'&'+str(int(show_episode)+1).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)-1).zfill(2)+'&'+str(show_episode).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)-1).zfill(3)+'&'+str(show_episode).zfill(3))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)).zfill(2)+'&'+str(int(show_episode)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)).zfill(3)+'&'+str(int(show_episode)+1).zfill(3))

	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)-1).zfill(1)+'&E'+str(show_episode).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)).zfill(1)+'&E'+str(int(show_episode)+1).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)-1).zfill(2)+'&E'+str(show_episode).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)-1).zfill(3)+'&E'+str(show_episode).zfill(3))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)).zfill(2)+'&E'+str(int(show_episode)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode)).zfill(3)+'&E'+str(int(show_episode)+1).zfill(3))

	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)-1).zfill(2)+'&'+str(show_episode).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)-1).zfill(3)+'&'+str(show_episode).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)).zfill(2)+'&'+str(int(show_episode)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)).zfill(3)+'&'+str(int(show_episode)+1).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)-1).zfill(1)+'&'+str(show_episode).zfill(1))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)).zfill(1)+'&'+str(int(show_episode)+1).zfill(1))

	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)-1).zfill(2)+'&E'+str(show_episode).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)-1).zfill(3)+'&E'+str(show_episode).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)).zfill(2)+'&E'+str(int(show_episode)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)).zfill(3)+'&E'+str(int(show_episode)+1).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)-1).zfill(1)+'&E'+str(show_episode).zfill(1))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode)).zfill(1)+'&E'+str(int(show_episode)+1).zfill(1))
	return season_list, episode_list

def season_list_episode_list_2(episode_list=None,show_season=None, show_episode=None, show_episode_absolute=None):
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(show_episode_absolute).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(show_episode_absolute).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(show_episode_absolute).zfill(3))
	episode_list.append(str(show_season).zfill(1)+'x'+str(show_episode_absolute).zfill(1))
	episode_list.append(str(show_season).zfill(1)+'x'+str(show_episode_absolute).zfill(2))
	episode_list.append(str(show_season).zfill(1)+'x'+str(show_episode_absolute).zfill(3))
	episode_list.append(str(show_season).zfill(2)+'x'+str(show_episode_absolute).zfill(2))
	episode_list.append(str(show_season).zfill(2)+'x'+str(show_episode_absolute).zfill(3))

	episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode_absolute).zfill(1) + '\'')
	episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode_absolute).zfill(2) + '\'')
	episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode_absolute).zfill(3) + '\'')
	episode_list.append('S'+str(show_season).zfill(2)+' - '+str(show_episode_absolute).zfill(2) + '\'')
	episode_list.append('S'+str(show_season).zfill(2)+' - '+str(show_episode_absolute).zfill(3) + '\'')

	episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode_absolute).zfill(1) + '\'')
	episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode_absolute).zfill(2) + '\'')
	episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode_absolute).zfill(3) + '\'')
	episode_list.append('S'+str(show_season).zfill(2)+' - E'+str(show_episode_absolute).zfill(2) + '\'')
	episode_list.append('S'+str(show_season).zfill(2)+' - E'+str(show_episode_absolute).zfill(3) + '\'')

	episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode_absolute).zfill(1) + '.')
	episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode_absolute).zfill(2) + '.')
	episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode_absolute).zfill(3) + '.')
	episode_list.append('S'+str(show_season).zfill(2)+' - '+str(show_episode_absolute).zfill(2) + '.')
	episode_list.append('S'+str(show_season).zfill(2)+' - '+str(show_episode_absolute).zfill(3) + '.')

	episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode_absolute).zfill(1) + '.')
	episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode_absolute).zfill(2) + '.')
	episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode_absolute).zfill(3) + '.')
	episode_list.append('S'+str(show_season).zfill(2)+' - E'+str(show_episode_absolute).zfill(2) + '.')
	episode_list.append('S'+str(show_season).zfill(2)+' - E'+str(show_episode_absolute).zfill(3) + '.')

	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(1)+'-E'+str(show_episode_absolute).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(1)+'-E'+str(int(show_episode_absolute)+1).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(2)+'-E'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(3)+'-E'+str(show_episode_absolute).zfill(3))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(2)+'-E'+str(int(show_episode_absolute)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(3)+'-E'+str(int(show_episode_absolute)+1).zfill(3))

	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(2)+'-E'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(3)+'-E'+str(show_episode_absolute).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(2)+'-E'+str(int(show_episode_absolute)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(3)+'-E'+str(int(show_episode_absolute)+1).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(1)+'-E'+str(show_episode_absolute).zfill(1))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(1)+'-E'+str(int(show_episode_absolute)+1).zfill(1))

	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(1)+'&'+str(show_episode_absolute).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(1)+'&'+str(int(show_episode_absolute)+1).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(2)+'&'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(3)+'&'+str(show_episode_absolute).zfill(3))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(2)+'&'+str(int(show_episode_absolute)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(3)+'&'+str(int(show_episode_absolute)+1).zfill(3))

	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(1)+'&E'+str(show_episode_absolute).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(1)+'&E'+str(int(show_episode_absolute)+1).zfill(1))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(2)+'&E'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(3)+'&E'+str(show_episode_absolute).zfill(3))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(2)+'&E'+str(int(show_episode_absolute)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(3)+'&E'+str(int(show_episode_absolute)+1).zfill(3))

	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(2)+'&'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(3)+'&'+str(show_episode_absolute).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(2)+'&'+str(int(show_episode_absolute)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(3)+'&'+str(int(show_episode_absolute)+1).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(1)+'&'+str(show_episode_absolute).zfill(1))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(1)+'&'+str(int(show_episode_absolute)+1).zfill(1))

	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(2)+'&E'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(3)+'&E'+str(show_episode_absolute).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(2)+'&E'+str(int(show_episode_absolute)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(3)+'&E'+str(int(show_episode_absolute)+1).zfill(3))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(1)+'&E'+str(show_episode_absolute).zfill(1))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(1)+'&E'+str(int(show_episode_absolute)+1).zfill(1))

	episode_list.append('E'+str(show_episode_absolute).zfill(3))
	episode_list.append('E'+str(int(show_episode_absolute)).zfill(3)+'&E'+str(int(show_episode_absolute)+1).zfill(3))
	episode_list.append('E'+str(int(show_episode_absolute)-1).zfill(3)+'&E'+str(int(show_episode_absolute)).zfill(3))
	return episode_list
	
def season_list_episode_list_2(episode_list=None, season_list=None,show_season=None, show_episode=None, show_episode_absolute=None, first_season=None, last_season=None):
	season_list.append('Complete')
	season_list.append('The Complete Series')
	season_list.append('Season '+str(first_season).zfill(1) + '-'+str(last_season).zfill(1))
	season_list.append('Season '+str(first_season).zfill(2) + '-'+str(last_season).zfill(2))
	season_list.append('Season '+str(first_season).zfill(1) + ' - '+str(last_season).zfill(1))
	season_list.append('Season '+str(first_season).zfill(2) + ' - '+str(last_season).zfill(2))
	season_list.append('Season '+str(first_season).zfill(1) + ' to '+str(last_season).zfill(1))
	season_list.append('Season '+str(first_season).zfill(2) + ' to '+str(last_season).zfill(2))
	season_list.append('S'+str(first_season).zfill(1) + '-S'+str(last_season).zfill(1))
	season_list.append('S'+str(first_season).zfill(2) + '-S'+str(last_season).zfill(2))
	season_list.append('S'+str(first_season).zfill(1) + ' - S'+str(last_season).zfill(1))
	season_list.append('S'+str(first_season).zfill(2) + ' - S'+str(last_season).zfill(2))
	return season_list


def next_ep_play(show_title, show_season, show_episode, tmdb):
	from resources.lib.TheMovieDB import get_tmdb_data
	from resources.lib.TheMovieDB import single_tvshow_info
	from resources.lib.TheMovieDB import get_tvshow_info

	xbmc_plugin = 'True'
	#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	if not xbmc.Player().isPlaying():
		xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
		xbmc.executebuiltin('ActivateWindow(busydialog)')
	li = None
	clear_next_ep_props()
	
	try:
		if int(tmdb) > 1:
			tmdb_id = tmdb
			tmdb_response = extended_tvshow_info(tvshow_id=tmdb_id, cache_time=0.001)
			show_title = tmdb_response[0]['TVShowTitle']
	except:
		tmdb_response = None
		pass
	
	
	show_title = show_title.replace('+', ' ')
	kodi_send_command = 'kodi-send --action="RunScript(%s,info=diamond_rd_player,type=tv,show_title=%s,show_season=%s,show_episode=%s,tmdb=%s,test=True)"' % (addon_ID(), show_title, show_season, show_episode, tmdb)
	print_log(kodi_send_command,'___kodi_send_command')
	if not xbmc.Player().isPlaying():
		xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
		xbmc.executebuiltin('ActivateWindow(busydialog)')

	season_list, episode_list = season_list_episode_list_1(show_season, show_episode)

	x265_enabled = xbmcaddon.Addon(addon_ID()).getSetting('x265_setting')
	#try:
	#	processor = get_processor_info()
	#	if 'linux' in str(sys.platform):
	#		if 'vero' in str(processor).lower() or 'pi 4' in str(processor).lower():
	#			print_log(str('VERO!!!'),'===>OPENINFO')
	#			x265_enabled = 'True'
	#except:
	#	print_log('processor_ERROR')
	#	x265_enabled = 'True'
	
	show_title_clean = regex.sub(' ', show_title.replace('\'s','s').replace('&','and')).replace('  ',' ').lower()
	tmdb_id = tmdb
	response = get_tvshow_info(tvshow_label=show_title, year=None, use_dialog=False)
	tmdb_id2 = response['id']
	try:
		if int(tmdb) > 1:
			tmdb_id = tmdb
	except:
		pass

	if tmdb_response:
		response = tmdb_response
	else:
		response = extended_tvshow_info(tvshow_id=tmdb_id, cache_time=0.001)
	extended_tvshow_info_response = response
	try: runtime_seconds = int(response[0]['duration(m)']) * 60
	except: runtime_seconds = 50 * 60
	tvdb_id = response[0]['tvdb_id']
	imdb_id = response[0]['imdb_id']

	response = get_tmdb_data(url='tv/'+str(tmdb_id)+'/alternative_titles?language=en-US&')
	alternate_titles = []
	y = 0
	for i in response['results']:
		try:
			alternate_titles.append(response['results'][y]['title'])
		except:
			alternate_titles.append(str(u''.join(response['results'][y]['title']).encode('utf-8').strip()))
		y = y + 1

	tot_episodes = 0
	show_episode_absolute = 0
	season_ep_titles = []
	i = int(show_season)
	response = get_tmdb_data(url='tv/'+str(tmdb_id)+'/season/'+str(i)+'?language=en-US&')
	while response and not 'The resource you requested could not be found' in str(response):
	#for i in range(int(show_season), int(show_season)+2):
		last_season = int(i)
		for xi in response['episodes']:
			next_tot_episode = xi['episode_number']
			if i == int(show_season):
				season_ep_titles.append(xi['name'])
			if i < int(show_season):
				show_episode_absolute = show_episode_absolute + 1
			elif i == int(show_season) and xi['episode_number'] <= int(show_episode):
				show_episode_absolute = show_episode_absolute + 1
		last_episode = int(xi['episode_number'])
		i = int(i) + 1
		response = get_tmdb_data(url='tv/'+str(tmdb_id)+'/season/'+str(i)+'?language=en-US&')
	i = int(i) -1

	last_episode_number = 's%se%s' % (str(i),str(xi['episode_number']))
	curr_episode_number = 's%se%s' % (str(show_season),str(show_episode))
	if last_episode_number == curr_episode_number:
		last_episode_flag = True
	else:
		last_episode_flag = False

	if int(show_season) == int(last_season) and int(show_episode) > int(last_episode):
		show_season = str(int(show_season) - 1)
		show_episode = str(int(show_episode) - int(last_episode))

	tmdb_response = extended_episode_info(tvshow_id=tmdb_id, season=show_season, episode=show_episode, cache_time=7)
	try: tmdb_rating = str(tmdb_response[0]['Rating'])
	except: tmdb_rating = str(0)

	special_correction = False
	if int(last_season) == 1 and int(show_season) == 0:
		special_correction = True
		original_show_season = show_season
		original_show_episode = show_episode
		show_season = str(1)
		show_episode = str(int(last_episode) + int(show_episode))
		curr_episode_number = 's%se%s' % (str(show_season),str(show_episode))
		season_list, episode_list = season_list_episode_list_1(show_season, show_episode)
		original_show_season = show_season
		original_show_episode = show_episode

	trakt_progress = get_trakt_playback('tv')
	resume_progress_seconds = 0
	if trakt_progress:
		for i in trakt_progress:
			if str(i['show']['ids']['tmdb']) == str(tmdb_id):
				if str(i['episode']['season']) == str(show_season) and str(i['episode']['number']) == str(show_episode):
					resume_progress = i['progress']
					resume_progress_seconds = int(float(runtime_seconds) * float(resume_progress/100))
					break

	season_list = season_list_episode_list_2(episode_list=episode_list, season_list=season_list,show_season=show_season, show_episode=show_episode, show_episode_absolute=show_episode_absolute, first_season=None, last_season=last_season)


	url = 'http://api.tvmaze.com/lookup/shows?thetvdb='+str(tvdb_id)
	response = get_JSON_response(url=url, cache_days=7.0, folder='TVMaze')
	show_id = response['id']

	url = 'http://api.tvmaze.com/shows/'+str(show_id)+'/episodes'
	response = get_JSON_response(url=url, cache_days=7.0, folder='TVMaze')

	first_season = ''
	last_season = ''
	for i in response:
		if first_season == '':
			first_season = i['season']
		last_season = i['season']
		if int(i['season']) == int(show_season) and int(i['number']) == int(show_episode):
			episode_id =  i['id']
			

	season_list = season_list_episode_list_2(episode_list=episode_list, season_list=season_list,show_season=show_season, show_episode=show_episode, show_episode_absolute=show_episode_absolute, first_season=first_season, last_season=last_season)

	try: 
		url = 'http://api.tvmaze.com/episodes/'+str(episode_id)+'?embed=show'
		response = get_JSON_response(url=url, cache_days=7.0, folder='TVMaze')
	except: response = ''

	try: 
		try:
			episode_name = response['name']
		except:
			episode_name = str(u''.join(response['name']).encode('utf-8').strip())
	except: episode_name = ''
	if episode_name == '':
		episode_name = tmdb_response[0]['title']
		episode_name.replace('(Original Pilot)','')
		episode_name.replace('(Extended Version)','')
		episode_name.replace('(Extended Cut)','')
		response = {}
		response['rating'] = {}
		response['rating']['average'] = tmdb_response[0]['Rating']
		response['airdate'] = tmdb_response[0]['release_date']
		response['summary'] = tmdb_response[0]['Plot']

	if episode_name[-1] == '\'' and episode_name[:2] == 'b\'':
		episode_name = episode_name[:-1]
		episode_name = episode_name[2:]
	clean_episode_name = regex.sub(' ', episode_name.replace('\'s','s').replace('&','and')).replace('  ',' ').lower()
	clean_episode_name2 = str(clean_episode_name).lower().replace('part viii','').replace('part vii','').replace('part vi','').replace('part v','').replace('part iv','').replace('part ix','').replace('part x','').replace('part iii','').replace('part ii','').replace('part i','').replace('part 1','').replace('part 2','').replace('part 3','').replace('part 4','').replace('part 5','').replace('part 6','').replace('part 7','').replace('part 8','').replace('part 9','').replace('part 10','').strip()
	tv_maze_rating = response['rating']['average']
	if clean_episode_name2 != clean_episode_name:
		if '2' in clean_episode_name.lower() or ('ii' in clean_episode_name.lower() and 'iii' not in clean_episode_name.lower()):
			part1_part2_flag = 2
		elif 'iii' in clean_episode_name.lower():
			part1_part2_flag = 0
		else:
			part1_part2_flag = 1
	else:
		part1_part2_flag = 0
	clean_episode_name = clean_episode_name2
	try: air_date = response['airdate']
	except: air_date = ''
	try: year = response['airdate'][0:4]
	except: year = ''
	try: 
		try:
			plot = str(response['summary']).replace('<i>','').replace('</i>','').replace('<p>','').replace('</p>','').replace('\n','').replace('\r','')
		except:
			plot = str(u''.join(response['summary'].replace('<i>','').replace('</i>','').replace('<p>','').replace('</p>','').replace('\n','').replace('\r','')).encode("utf-8").strip())
	except: plot = ''
	if plot[-1] == '\'' and plot[:2] == 'b\'':
		plot = plot[:-1]
		plot = plot[2:]
	try:
		try:
			genre = response['_embedded']['show']['genres']
		except:
			genre = str(u''.join(response['_embedded']['show']['genres']).encode('utf-8').strip())
	except: genre = ''
	if genre != '':
		if genre[-1] == '\'' and genre[:2] == 'b\'':
			genre = genre[:-1]
			genre = genre[2:]
	try: 
		rating = float(tv_maze_rating)
	except: 
		try: rating =  float(tmdb_rating)
		except: rating = float(0.0)
	try: runtime = response['_embedded']['show']['runtime']
	except: runtime = ''
	try:
		tvmaze_thumb_medium = response['image']['medium']
		tvmaze_thumb_large = response['image']['medium'].replace('medium','large')
		tvmaze_thumb_original = response['image']['original'].replace('medium','large')
		episode_thumb = tvmaze_thumb_medium
	except:
		episode_thumb = ''

	if rating == '' or str(rating) == '0.0' or air_date == '' or episode_thumb == '':
		imdb_url = 'https://www.imdb.com/title/'+str(imdb_id)+'/episodes?season=' + str(show_season)
		imdb_response = requests.get(imdb_url)

		from bs4 import BeautifulSoup
		html_soup = BeautifulSoup(imdb_response.text, 'html.parser')
		episode_containers = html_soup.find_all('div', class_='info')

		#show_season = url.split('=')[1]
		episode_images = html_soup.find_all('div', class_='image')

		x = 0
		for i in episode_containers:
			if str(episode_containers[x].meta['content']) == str(show_episode):
				#print_log('imdb_id = ' + str(imdb_id))
				try:
					imdb_title = episode_containers[x].a['title']
				except:
					imdb_title = ''
				try: 
					imdb_SxxExx = 'S' + str(format(int(show_season), '02d')) + 'E' + str(format(int(episode_containers[x].meta['content']), '02d'))
				except:
					imdb_SxxExx = ''
				try: 
					imdb_airdate = episode_containers[x].find('div', class_='airdate').text.strip()
				except:
					imdb_airdate = ''
				try:
					imdb_rating = episode_containers[x].find('span', class_='ipl-rating-star__rating').text
				except:
					imdb_rating = ''
				try:
					imdb_plot = episode_containers[x].find('div', class_='item_description').text.strip().encode("utf-8")
				except:
					imdb_plot = ''
				if rating == '' or str(rating) == '0.0':
					rating = imdb_rating
				if air_date == '':
					air_date = imdb_airdate
				y = 0
				for j in episode_images:
					try:
						if episode_images[y].find('img', class_='zero-z-index').attrs['alt'] == episode_containers[x].a['title']:
							#print_log(show_episode_images[y].find('img', class_='zero-z-index').attrs['src'])
							#print_log(show_episode_images[y].find('img', class_='zero-z-index').attrs['src'].split('._')[0]+'._V1_UY504_CR0,0,896,504_AL_.jpg')
							try:
								imdb_thumb = episode_images[y].find('img', class_='zero-z-index').attrs['src'].split('._')[0]+'.jpg'
							except:
								imdb_thumb = ''
							if episode_thumb == '':
								episode_thumb = imdb_thumb
							break
					except: pass
					y = y + 1
			x = x + 1

		#ORIGINAL THUMB SIZE
		#._V1_UY126_CR0,0,224,126_AL_.jpg

		#x4 THUMB SIZE
		#._V1_UY504_CR0,0,896,504_AL_.jpg

	#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	#header = {'Authorization': 'Bearer ' + RD_api()}
	#x265_enabled = 'True'
	downloads_fail = 'False'
	torrents_fail = 'False'
	download_found = 0
	torrent_found = 0
	meta_info = {'show_season': show_season, 'show_episode': show_episode, 'x265_enabled': x265_enabled, 'episode_name': episode_name, 'clean_episode_name': clean_episode_name, 'part1_part2_flag': part1_part2_flag,'show_title': show_title, 'show_title_clean': show_title_clean, 'alternate_titles': alternate_titles, 'episode_list': episode_list, 'season_list': season_list, 'last_episode_flag': last_episode_flag, 'last_episode_number': last_episode_number, 'curr_episode_number': curr_episode_number, 'season_ep_titles': season_ep_titles}
	#print_log(meta_info,'meta_info')

	for x in range(99):
		if downloads_fail == 'False' and download_found == 0:
			try: data = RD_get_page(x, 'downloads')
			except: downloads_fail = 'True'
		if downloads_fail == 'False' and download_found == 0:
			for i in data:
				if 'bad token' in str(data):
					try: print_log(str(data)+'===>bad token')
					except: print_log(data,'EXCEPTION')
					return
				i['filename'] = i['filename'].replace('\'s','s').replace('_','.').replace('-',' ').replace('.',' ').lower()
				meta_info_flags = download_tv_test(meta_info=meta_info, filename=i['filename'])
				#print_log(i['filename'], 'download_filename')
				#print_log(meta_info_flags, 'download_meta_info_flags')
				down_test = 0
				for xi in meta_info_flags:
					if xi != 'x265_match_pass' and meta_info_flags[xi] == True:
						#print_log(i['filename'], 'TRUE_download_filename')
						down_test = down_test + 1
				if meta_info_flags['season_list_flag'] == True and meta_info_flags['episode_name_flag'] == True and meta_info_flags['x265_match_pass'] == True and meta_info_flags['part1_part2_match_flag'] == True:
					down_test = down_test + 2
				if down_test > 3 and meta_info_flags['x265_match_pass']:
					#print_log(meta_info, 'DOWNLOAD')
					#print_log(meta_info_flags, 'DOWNLOAD')
					PTN_link = i['link']
					PTN_download = i['download']
					PTN_size = str(int(i['filesize'])/(1024*1024))+'Mb'
					headers=requests.head(PTN_download).headers
					if not str('attachment') in headers.get('Content-Disposition',''):
						download_found = 0
					else:
						download_found = 1
					if download_found == 1:
						PTN_episode = show_episode
						PTN_season = show_season
						PTN_title = show_title
						PTN_res = ''
						print_log(str('[' + str(PTN_size) + '][' + str(PTN_title) + '][' + str(PTN_season) + '][' + str(PTN_episode)+ '][' + str(episode_name) + '][' + str(PTN_res) + '][' + str(PTN_download) + ']'),'download_found===>OPENINFO')
						break
		if int(torrent_found) == 1 or int(download_found) == 1:
			break
		try:
			if torrents_fail == 'False' and torrent_found == 0:
				data2 = RD_get_page(x, 'torrents')
		except:
			torrents_fail = 'True'
			pass
		if torrents_fail == 'False' and torrent_found == 0:
			for k in data2:
				if torrent_found == 0:
					torr_response = ''
					count = 0
					k['filename'] = k['filename'].replace('_','.').replace('-',' ').replace('.',' ').replace('\'s','s').lower()
					meta_info_flags = download_tv_test(meta_info=meta_info, filename=k['filename'])
					torr_test = False

					if meta_info_flags['x265_match_pass'] == True and (meta_info_flags['show_title_flag'] == True or meta_info_flags['alternate_titles_flag'] == True):
						#print_log(k['filename'])
						#print_log(meta_info, str(k['filename'])+str(x)+'_TORRENT')
						#print_log(meta_info_flags, str(x)+'TORRENT')
						torr_test = True
						#print_log(k['filename'], 'page==' + str(x) + ',torr_test==TRUE')

					if torrent_found == 0 and torr_test == True:
						try:
							torr_data = RD_instantAvailability(torr_hash=k['hash'])
						except:
							while torr_response == '' and count < 5:
								torr_data = RD_instantAvailability(torr_hash=k['hash'])
								count = count + 1
								if torr_response != '':
									break
							if torr_response == '':
								continue
					elif torrent_found == 1:
						break
					elif torr_test == False:
						continue

				if torrent_found == 1:
					break

				torr_data2 = {}
				torr_data3 = {}
				try: test_var = torr_data[k['hash']]['rd']
				except: continue
				for j in torr_data[k['hash']]['rd']:
					for x in j:
						torr_data2[x] = j[x]
						torr_data3[x] = j[x]
				for y in torr_data3.keys():
					if int(torr_data2[str(y)]['filesize']/(1024*1024)) < 20:
							torr_data2.pop(str(y), None)
				list1 = sorted(torr_data2, key = lambda z: int(z))
				for j in list1:
					original_filename = torr_data2[str(j)]['filename']
					torr_data2[str(j)]['filename'] = torr_data2[str(j)]['filename'].replace('_','.').replace('-',' ').replace('.',' ').replace('\'s','s')

					if 'sample' in original_filename:
						continue

					test_file = torr_data2[str(j)]['filename'].lower()
					if torr_test:
						test_file = meta_info['show_title_clean'] + ' ' + test_file
					meta_info_flags = download_tv_test(meta_info=meta_info, filename=test_file)
					torr_test2 = 0
					for xi in meta_info_flags:
						if xi != 'x265_match_pass' and meta_info_flags[xi] == True:
							#print_log(torr_data2[str(j)]['filename'], 'TRUE_torrent_filename')
							#print_log(meta_info_flags, 'TRUE_torrent_meta')
							torr_test2 = torr_test2 + 1
					if meta_info_flags['season_list_flag'] == True and meta_info_flags['episode_name_flag'] == True and meta_info_flags['x265_match_pass'] == True and meta_info_flags['part1_part2_match_flag'] == True:
						torr_test2 = torr_test2 + 2
					if torr_test == True and torr_test2 > 3 and meta_info_flags['x265_match_pass']:
						id = k['id']
						torr_response3 = RD_torrents_info(id)
						#print_log(torr_data2[str(j)]['filename'],'torr_data2')
						for xi in torr_response3['files']:
							torr_data2[str(j)]['filename'] = original_filename

							if str(torr_data2[str(j)]['filename']) in str(xi['path']) or str(torr_data2[str(j)]['filename']).lower() in str(xi['path']).lower():
								file_id = xi['id']
								PTN_episode = show_episode
								PTN_season = show_season
								PTN_title = show_title
								PTN_res = ''
								PTN_size = str(int(xi['bytes'])/(1024*1024))+'Mb'
								while torrent_found == 0 and file_id >=1:
									try:
										file_link = torr_response3['links'][int(file_id)-1]
									except:
										file_id = int(file_id) - 1
										continue
									torr_unrestricted = RD_unrestrict_link(file_link=file_link)
									try: 
										PTN_download = torr_unrestricted['download']
									except: 
										torrent_found = 0
										torr_test = False
										meta_info_flags['x265_match_pass'] = False
										file_id = -1
										continue
									RD_link = str(PTN_download).split('/')[4]
									PTN_link = RD_link
									ptn_data2 = ''
									if not str(torr_data2[str(j)]['filename']).lower() in str(torr_unrestricted).lower():
										file_id = int(file_id) - 1
										continue
									try: 
										ptn_data2 = PTN.parse(urllib.parse.unquote((PTN_download)).replace('-',' ').replace('.',' '))
										file_name = str(urllib.parse.unquote(PTN_download)).split('/')[5].replace('.',' ')
									except: 
										file_name = ''
										pass
									if str(file_name.replace(' ','.')) == str(torr_data2[str(j)]['filename']) or str(torr_data2[str(j)]['filename'].replace('.',' ')) == str(file_name):
										torrent_found = 1
									elif str(file_name.replace(' ','.')).lower() == str(torr_data2[str(j)]['filename']).lower() or str(torr_data2[str(j)]['filename'].replace('.',' ')).lower() == str(file_name).lower():
										torrent_found = 1
									else:
										torrent_found = 0
									headers=requests.head(PTN_download).headers
									if str('attachment') in headers.get('Content-Disposition',''):
										torrent_found = 1
										print_log(str('[' + str(PTN_size) + '][' + str(PTN_title) + '][' + str(PTN_season) + '][' + str(PTN_episode)+ '][' + str(episode_name) + '][' + str(PTN_res) + '][' + str(PTN_download) + ']'),'torrent_found===>OPENINFO')
										#print_log(str('[' + str(PTN_size) + '][' + str(PTN_title) + '][' + str(PTN_season) + '][' + str(PTN_episode) + '][' + str(PTN_res) + '][' + str(PTN_download) + ']'),'torrent_found===>OPENINFO')
									else:
										torrent_found = 0
									if torrent_found == 1:
										break
									if torrent_found == 0:
										try: 
											torr_link = RD_downloads_delete(RD_link)
										except: 
											pass
										file_id = int(file_id) - 1
						if torrent_found == 1:
							break


		if torrents_fail == 'True' and downloads_fail == 'True':
			break
		if torrent_found == 1 or download_found == 1:
			break

	print_log('END','__END__')

	#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	if torrent_found == 0 and download_found == 0:
		PTN_download = ''
		print_log(str('Not found1'),'===>OPENINFO')
		xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
		rd_seren_prescrape = xbmcaddon.Addon(addon_ID()).getSetting('rd_seren_prescrape')
		if xbmc.getCondVisibility('System.HasAddon(plugin.video.seren)') and xbmc.Player().isPlaying() and rd_seren_prescrape == 'true':
			prescrape_seren(tmdb=tmdb, season=show_season, episode=show_episode)
			xbmcgui.Window(10000).setProperty('plugin.video.seren.runtime.tempSilent', 'True')
			try: seren_version = xbmcaddon.Addon('plugin.video.seren').getAddonInfo("version")
			except: seren_version = ''
			xbmcgui.Window(10000).setProperty('plugin.video.seren.%s.runtime.tempSilent' % (str(seren_version)), 'True')
		return

	hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = get_fanart_results(tvdb_id, media_type='tv_tvdb')

	con = db_connection()
	cur = con.cursor()
	sql_result1 = cur.execute("SELECT idepisode, * from files,episode,tvshow where episode.idfile = files.idfile and episode.idshow = tvshow.idshow and tvshow.c00 = '"+str(show_title).replace("'","''")+"' and episode.c12 = '"+str(show_season)+"' and episode.c13 = '"+str(show_episode)+"' order by dateadded asc").fetchall()
	
	#print_log(sql_result)
	try: dbid = sql_result1[0][0]
	except: dbid = 0
	if dbid == 0:
		regex_new = re.compile('[^a-zA-Z0-9]')
		cur.execute("select idshow,c00 from tvshow order by 2")
		sql_result1 = cur.fetchall()
		for i in sql_result1:
			title = regex_new.sub(' ', i[1].replace('\'','').replace('\'','').replace('&','and')).replace('  ',' ').lower()
			if title == show_title_clean:
				show_id = i[0]
				break
		cur.execute("select idepisode from episode where idshow = " + str(show_id) + " and C12 = " + str(show_season) + " and c13 = " + str(show_episode))
		sql_result1 = cur.fetchall()
		try: dbid = sql_result1[0][0]
		except: dbid = 0

	#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	sql_result = cur.execute("SELECT resumeTimeInSeconds,C11 from episode_view where idepisode = " + str(dbid)).fetchall()
	try: resumeTimeInSeconds = sql_result[0][0]
	except: resumeTimeInSeconds = ''
	try: duration = sql_result[0][1]
	except: duration = runtime
	if duration == '' or duration == None:
		duration = runtime
	if resumeTimeInSeconds == None:
		resumeTimeInSeconds = 0
	#try:
	#	file_name = PTN_download.split('/')[5]
	#	#delete_result = cur.execute("DELETE FROM files WHERE strFilename = '"+str(file_name)+"' ;")
	#	#con.commit()
	#except:
	#	pass
	cur.close()

	if special_correction == True:
		show_season = original_show_season
		show_episode = original_show_episode
		PTN_season = show_season
		PTN_episode = show_episode

	#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	next_ep_play_details = {}
	next_ep_play_details['ResolvedUrl'] = True
	next_ep_play_details['show_title'] = show_title
	next_ep_play_details['PTN_title'] = PTN_title
	next_ep_play_details['PTN_season'] = PTN_season
	next_ep_play_details['PTN_episode'] = PTN_episode
	next_ep_play_details['PTN_res'] = PTN_res
	next_ep_play_details['PTN_link'] = PTN_link
	next_ep_play_details['PTN_size'] = PTN_size
	next_ep_play_details['PTN_download'] = PTN_download
	next_ep_play_details['dbid'] = dbid
	next_ep_play_details['dbtype'] = 'episode'
	next_ep_play_details['episode_name'] = episode_name
	next_ep_play_details['plot'] = plot
	next_ep_play_details['air_date'] = air_date
	next_ep_play_details['episode_thumb'] = episode_thumb
	next_ep_play_details['genre'] = genre
	next_ep_play_details['year'] = year
	next_ep_play_details['rating'] = rating
	next_ep_play_details['hdclearart'] = hdclearart
	next_ep_play_details['seasonposter'] = seasonposter
	next_ep_play_details['seasonthumb'] = seasonthumb
	next_ep_play_details['seasonbanner'] = seasonbanner
	next_ep_play_details['tvthumb'] = tvthumb
	next_ep_play_details['thumb'] = tvthumb
	next_ep_play_details['tvbanner'] = tvbanner
	next_ep_play_details['banner'] = tvbanner
	next_ep_play_details['showbackground'] = showbackground
	next_ep_play_details['fanart'] = showbackground
	next_ep_play_details['landscape'] = showbackground
	next_ep_play_details['clearlogo'] = clearlogo
	next_ep_play_details['characterart'] = characterart
	next_ep_play_details['tvposter'] = tvposter
	next_ep_play_details['poster'] = tvposter
	if tvposter == '':
		next_ep_play_details['poster'] = seasonposter
	next_ep_play_details['clearart'] = clearart
	next_ep_play_details['hdtvlogo'] = hdtvlogo
	if clearlogo == '':
		next_ep_play_details['clearlogo'] = hdtvlogo
	next_ep_play_details['resumeTimeInSeconds'] = resumeTimeInSeconds
	next_ep_play_details['duration'] = duration
	next_ep_play_details['sql_result1'] = sql_result1
	if next_ep_play_details['thumb'] == '':
		next_ep_play_details['thumb'] = next_ep_play_details['episode_thumb']
		if next_ep_play_details['episode_thumb'] == '':
			next_ep_play_details['thumb'] = next_ep_play_details['fanart']

	print_log(next_ep_play_details)

	#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	if xbmc_plugin == 'True' and (torrent_found == 1 or download_found == 1):
		#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
		if seasonposter != '':
			poster = seasonposter 
		elif tvposter != '':
			poster = tvposter
		else:
			poster = tvposter
		xbmcgui.Window(10000).setProperty('Next_EP.poster', poster)
		fanart = showbackground
		xbmcgui.Window(10000).setProperty('Next_EP.fanart', fanart)
		if clearlogo == '' :
			clearlogo = hdtvlogo
		else:
			clearlogo = clearlogo
		xbmcgui.Window(10000).setProperty('Next_EP.clearlogo', clearlogo)
		landscape = showbackground
		xbmcgui.Window(10000).setProperty('Next_EP.landscape', landscape)
		banner = tvbanner
		xbmcgui.Window(10000).setProperty('Next_EP.banner', banner)
		thumb = episode_thumb
		xbmcgui.Window(10000).setProperty('Next_EP.thumb', thumb)
		#director = xbmc.getInfoLabel('listitem.Director')
		#cast = xbmc.getInfoLabel('listitem.Cast')
		#cast_role = xbmc.getInfoLabel('listitem.CastAndRole')
		duration = str(duration)
		xbmcgui.Window(10000).setProperty('Next_EP.duration', duration)
		dbid = str(dbid)
		xbmcgui.Window(10000).setProperty('Next_EP.dbid', dbid)
		dbtype = 'episode'
		xbmcgui.Window(10000).setProperty('Next_EP.dbtype', dbtype)
		if genre != '':
			if (genre[-1] == '\'' and genre[:2] == 'b\'') or (genre[-1] == '"' and genre[:2] == 'b"'):
				genre = genre[:-1]
				genre = genre[2:]
		if (episode_name[-1] == '\'' and episode_name[:2] == 'b\'') or (episode_name[-1] == '"' and episode_name[:2] == 'b"'):
			episode_name = episode_name[:-1]
			episode_name = episode_name[2:]
		if (show_title[-1] == '\'' and show_title[:2] == 'b\'') or (show_title[-1] == '"' and show_title[:2] == 'b"'):
			show_title = show_title[:-1]
			show_title = show_title[2:]
		if (plot[-1] == '\'' and plot[:2] == 'b\'') or (plot[-1] == '"' and plot[:2] == 'b"'):
			plot = plot[:-1]
			plot = plot[2:]

		genre = genre
		xbmcgui.Window(10000).setProperty('Next_EP.genre', str(genre))
		imdb = imdb_id 
		xbmcgui.Window(10000).setProperty('Next_EP.imdb', imdb)
		icon = episode_thumb
		xbmcgui.Window(10000).setProperty('Next_EP.icon', icon)
		label = episode_name
		xbmcgui.Window(10000).setProperty('Next_EP.label', label)
		label2 = episode_name
		xbmcgui.Window(10000).setProperty('Next_EP.label2', label2)
		#MPAA = xbmc.getInfoLabel('listitem.MPAA')
		originaltitle = show_title
		xbmcgui.Window(10000).setProperty('Next_EP.originaltitle', originaltitle)
		plot = plot
		xbmcgui.Window(10000).setProperty('Next_EP.plot', plot)
		plotoutline = plot
		xbmcgui.Window(10000).setProperty('Next_EP.plotoutline', plotoutline)
		premiered = air_date
		xbmcgui.Window(10000).setProperty('Next_EP.premiered', premiered)
		rating = rating
		xbmcgui.Window(10000).setProperty('Next_EP.rating', str(rating))
		tv_show_title = show_title
		xbmcgui.Window(10000).setProperty('Next_EP.tv_show_title', tv_show_title)
		#rating_votes = xbmc.getInfoLabel('listitem.RatingAndVotes')
		#set = xbmc.getInfoLabel('listitem.Set')
		#setid = xbmc.getInfoLabel('listitem.SetID')
		#studio = xbmc.getInfoLabel('listitem.Studio')
		#tagline = xbmc.getInfoLabel('listitem.Tagline')
		title = episode_name
		xbmcgui.Window(10000).setProperty('Next_EP.title', title)
		#votes = xbmc.getInfoLabel('listitem.Votes')
		#writer = xbmc.getInfoLabel('listitem.Writer')
		year = str(year)
		xbmcgui.Window(10000).setProperty('Next_EP.year', year)
		#percent_played = xbmc.getInfoLabel('ListItem.PercentPlayed')
		resumetime = resumeTimeInSeconds
		xbmcgui.Window(10000).setProperty('Next_EP.resumetime', str(resumetime))
		xbmcgui.Window(10000).setProperty('Next_EP.Episode', str(show_episode)) 
		xbmcgui.Window(10000).setProperty('Next_EP.Season', str(show_season))
		xbmcgui.Window(10000).setProperty('Next_EP.tmdb_id', str(tmdb_id))
		
		if xbmc.Player().isPlaying():
			if PTN_download == '':
				return

		handle = -1
		infolabels = {'episode': None, 'sortepisode': None, 'season': None, 'sortseason': None, 'year': None, 'premiered': None, 'aired': None, 'imdbnumber': None, 'duration': None, 'dateadded': None, 'rating': None, 'votes': None, 'mediatype': None, 'title': None, 'originaltitle': None, 'sorttitle': None, 'plot': None, 'plotoutline': None, 'tvshowtitle': None, 'playcount': None, 'director': None, 'writer': None, 'mpaa': None, 'genre': None, 'studio': None}
		#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
		xbmcplugin.setContent(handle, 'episodes')
		if xbmc.Player().isPlaying() == False:
			if (resumetime == None or resumetime == '' or resumetime == 0) and resume_progress_seconds > 0:
				resumetime = resume_progress_seconds
				resumeTimeInSeconds = resume_progress_seconds
				xbmcgui.Window(10000).setProperty('Next_EP.resumetime', str(resumetime))

		try:
			li = xbmcgui.ListItem(label, iconImage=thumb)
		except:
			li = xbmcgui.ListItem(label, thumb)
		#li.setProperty('fanart_image', fanart)
		li.setProperty('startoffset', str(resumeTimeInSeconds))
		#li.setProperty('DBTYPE', 'episode')
		#li.setProperty('mediatype', 'episode')
		#li.setProperty('plot', plot)
		#li.setProperty('TVShowTitle', show_title)
		#li.setProperty('EpisodeName', episode_name)
		#li.setProperty('Episode', str(show_episode))
		#li.setProperty('Season', str(show_season))
		#li.setProperty('Duration', duration)
		#li.setProperty('Content', 'episodes')
		#li.setProperty('premiered', str(premiered)+'T00:00:00.000Z')
		#li.setProperty('DBID', None)
		#li.setProperty('mediatype', 'episode')
		#li.setProperty('DBTYPE', 'episode')
		#li.setProperty('duration', str(duration))
		#li.setProperty('IMDBNumber', imdb)
		#li.setProperty('rating', str(rating))
		#li.setProperty('sortseason', str(show_season))
		#li.setProperty('plotoutline', plot)
		#li.setProperty('FileNameAndPath', PTN_download)
		#li.setProperty('plot', str(plot))
		#li.setProperty('sortepisode', show_episode)
		#li.setProperty('title', episode_name)
		#li.setProperty('EpisodeName', episode_name)
		#li.setProperty('aired', str(premiered)+'T00:00:00.000Z')
		#li.setProperty('season', show_season)
		#li.setProperty('tvshowtitle', show_title)
		#li.setProperty('genre', str(genre))
		#li.setProperty('dateadded', str(premiered)+'T00:00:00.000Z')
		#li.setProperty('episode', show_episode)
		##li.setProperty('originaltitle', episode_name)
		#li.setProperty('sorttitle', episode_name)
		#li.setProperty('path', PTN_download)

		li.setArt({ 'poster': poster, 'fanart': fanart, 'banner': banner, 'clearlogo': clearlogo, 'landscape': landscape, 'thumb': thumb})

		li.setProperty('IsPlayable', 'true')
		li.setProperty('IsFolder', 'false')
		li.setPath(PTN_download)

		#li.setInfo('video', {'title': title,'genre': genre, 'plotoutline': plotoutline, 'plot': plot, 'path': PTN_download,'premiered': premiered, 'dbid': dbid, 'mediatype': dbtype, 'writer': writer, 'director': director, 'duration': duration, 'IMDBNumber': imdb, 'MPAA': MPAA, 'Rating': rating, 'Studio': studio, 'Year': year, 'Tagline': tagline, 'Set': set, 'SetID': setid})
		#li.setInfo('video', {'title': title, 'TVShowTitle': show_title, 'Episode': str(show_episode), 'Season': show_season,'genre': genre, 'plotoutline': plotoutline, 'plot': plot, 'path': PTN_download,'premiered': premiered, 'dbid': dbid, 'mediatype': dbtype, 'duration': duration, 'IMDBNumber': imdb, 'Rating': rating, 'Year': year})

		print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
		if str(dbid) != '0':
			li.setProperty('DBID', dbid)
			try:
				json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "VideoLibrary.GetEpisodeDetails", "params": {"episodeid": '+str(dbid)+', "properties": ["title","plot","votes","rating","writer","firstaired","playcount","runtime","director","productioncode","season","episode","originaltitle","showtitle","cast","streamdetails","lastplayed","fanart","thumbnail","file","resume","tvshowid","dateadded","uniqueid","art","specialsortseason","specialsortepisode","userrating","seasonid","ratings"]}}')
				#json_result = unicode(json_result, 'utf-8', errors='ignore')
				json_result = json.loads(json_result)
				json_result['result']['episodedetails']['mediatype'] = 'episode'
				json_result['result']['episodedetails']['dbid'] = int(json_result['result']['episodedetails']['episodeid'])
				json_result['result']['episodedetails']['path'] = PTN_download
				li.setCast(json_result['result']['episodedetails']['cast'])
				li.setArt(json_result['result']['episodedetails']['art'])
				#li.setInfo(type='Video', infoLabels=unicode(json_result['result']['episodedetails']))
				try:
					info_tag = ListItemInfoTag(li, 'video')
					info_tag.set_info(json_result['result']['episodedetails'])
				except:
					li.setInfo(type='Video', infoLabels=unicode(json_result['result']['episodedetails']))
			except:
				try: 
					#li.setInfo('video', {'sortseason': int(show_season), 'rating': str(rating), 'plotoutline': str(plot), 'year': int(year), 'duration': int(duration), 'FileNameAndPath': str(PTN_download), 'plot': str(plot), 'votes': 0, 'sortepisode': int(show_episode), 'title': str(episode_name), 'aired': str(premiered)+'T00:00:00.000Z', 'season': int(show_season), 'tvshowtitle': str(show_title), 'mediatype': 'episode', 'genre': [], 'dateadded': str(premiered)+'T00:00:00.000Z', 'episode': int(show_episode), 'premiered': str(premiered)+'T00:00:00.000Z', 'originaltitle': str(episode_name), 'sorttitle': str(episode_name)})
					try: 
						info_tag = ListItemInfoTag(li, 'video')
						info_tag.set_info({'sortseason': int(show_season), 'rating': str(rating), 'plotoutline': str(plot), 'year': int(year), 'duration': int(duration), 'FileNameAndPath': str(PTN_download), 'plot': str(plot), 'votes': 0, 'sortepisode': int(show_episode), 'title': str(episode_name), 'aired': str(premiered)+'T00:00:00.000Z', 'season': int(show_season), 'tvshowtitle': str(show_title), 'mediatype': 'episode', 'genre': [], 'dateadded': str(premiered)+'T00:00:00.000Z', 'episode': int(show_episode), 'premiered': str(premiered)+'T00:00:00.000Z', 'originaltitle': str(episode_name), 'sorttitle': str(episode_name)})
					except:
						li.setInfo('video', {'sortseason': int(show_season), 'rating': str(rating), 'plotoutline': str(plot), 'year': int(year), 'duration': int(duration), 'FileNameAndPath': str(PTN_download), 'plot': str(plot), 'votes': 0, 'sortepisode': int(show_episode), 'title': str(episode_name), 'aired': str(premiered)+'T00:00:00.000Z', 'season': int(show_season), 'tvshowtitle': str(show_title), 'mediatype': 'episode', 'genre': [], 'dateadded': str(premiered)+'T00:00:00.000Z', 'episode': int(show_episode), 'premiered': str(premiered)+'T00:00:00.000Z', 'originaltitle': str(episode_name), 'sorttitle': str(episode_name)})
				except: 
					try:
						#li.setInfo('video', {'title': title, 'TVShowTitle': show_title, 'Episode': str(show_episode), 'Season': show_season,'genre': genre, 'plotoutline': plotoutline, 'plot': plot, 'path': PTN_download,'premiered': premiered, 'dbid': dbid, 'mediatype': dbtype, 'duration': duration, 'IMDBNumber': imdb, 'Rating': rating, 'Year': year})
						try:
							info_tag = ListItemInfoTag(li, 'video')
							info_tag.set_info({'title': title, 'TVShowTitle': show_title, 'Episode': str(show_episode), 'Season': show_season,'genre': genre, 'plotoutline': plotoutline, 'plot': plot, 'path': PTN_download,'premiered': premiered, 'dbid': dbid, 'mediatype': dbtype, 'duration': duration, 'IMDBNumber': imdb, 'Rating': rating, 'Year': year})
						except:
							li.setInfo('video', {'title': title, 'TVShowTitle': show_title, 'Episode': str(show_episode), 'Season': show_season,'genre': genre, 'plotoutline': plotoutline, 'plot': plot, 'path': PTN_download,'premiered': premiered, 'dbid': dbid, 'mediatype': dbtype, 'duration': duration, 'IMDBNumber': imdb, 'Rating': rating, 'Year': year})
					except:
						try: 
							print_log(str('['+str(title)+']'+'['+str(show_title)+']'+'['+str(show_episode)+']'+'['+str(show_season)+']'+'['+str(genre)+']'+'['+str(plotoutline)+']'+'['+str(plot)+']'+'['+str(PTN_download)+']'+'['+str(premiered)+']'+'['+str(dbid)+']'+'['+str(dbtype)+']'+'['+str(duration)+']'+'['+str(imdb)+']'+'['+str(rating)+']'+'['+str(year)+']'),'===>OPENINFO')
						except: 
							pass
		else:
			li.setProperty('DBID', None)
			actors = []
			actor_name = []
			actor_role = []
			actor_thumbnail = []
			actor_order = []
			idx = 0
			for idx, i in enumerate(tmdb_response[1]['actors']):
				actor = {'name': i['name'], 'role': i['character'],'thumbnail': i.get('thumb'), 'order': idx+1}
				actors.append(actor)
				actor_name.append(i['name'])
				actor_role.append(i['character'])
				actor_thumbnail.append(i.get('thumb'))
				actor_order.append(idx+1)
			start = idx+1
			for idx, i in enumerate(tmdb_response[1]['guest_stars']):
				actor = {'name': i['name'], 'role': i['character'],'thumbnail': i.get('thumb'), 'order': start+idx+1}
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
			for i in tmdb_response[1]['crew']:
				if 'Director' in str(i):
					director.append(i['name'])
				if 'Writer' in str(i):
					writer.append(i['name'])
			studio = []
			for i in extended_tvshow_info_response[1]['studios']:
				studio.append(i['title'])

			infolabels['episode'] = int(show_episode)
			infolabels['sortepisode'] = int(show_episode)
			infolabels['season'] = int(show_season)
			infolabels['sortseason'] = int(show_season)
			infolabels['year'] = str(year)
			infolabels['premiered'] = str(premiered)+'T00:00:00'
			infolabels['aired'] = str(premiered)+'T00:00:00'
			infolabels['imdbnumber'] = imdb
			try: infolabels['duration'] = int(duration)
			except: infolabels['duration'] = int(runtime_seconds)
			infolabels['dateadded'] = str(premiered)+'T00:00:00'
			infolabels['rating'] = float(rating)
			infolabels['votes'] = int(extended_tvshow_info_response[0]['Votes'])
			infolabels['mediatype'] = 'episode'
			infolabels['title'] = episode_name
			infolabels['originaltitle'] = episode_name
			infolabels['sorttitle'] = episode_name
			infolabels['plot'] = plot
			infolabels['plotoutline'] = plot
			infolabels['tvshowtitle'] = show_title
			infolabels['playcount'] = 0
			infolabels['director'] = director
			infolabels['writer'] = writer
			infolabels['mpaa'] = extended_tvshow_info_response[0]['mpaa']
			infolabels['genre'] = genre
			infolabels['studio'] = studio
			infolabels['FileNameAndPath'] = PTN_download
			infolabels['EpisodeName'] = episode_name
			infolabels['path'] = PTN_download

			#li.setInfo(type='Video', infoLabels = infolabels)
			try:
				info_tag = ListItemInfoTag(li, 'video')
				info_tag.set_info(infolabels)
			except:
				li.setInfo(type='Video', infoLabels = infolabels)
			#info_tag.set_cast(str(actors))
			#print_log(infolabels,'infolabels')

		xbmcplugin.setContent(handle, 'episodes')
		xbmcgui.Window(10000).setProperty('diamond_player_time', str(int(time.time())+30))
		if 'test=True' in str(sys.argv):
			#print_log(sys.argv)
			#print_log(next_ep_play_details,'next_ep_play_details')
			xbmc.executebuiltin('Dialog.Close(busydialog)')
			xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
			exit()
		if xbmc.Player().isPlaying():
			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

			print_log('['+str(title)+']'+'[E'+str(show_episode)+']'+'[S'+str(show_season)+']'+'['+str(show_title)+']'+'['+str(PTN_download)+']','_PRESCRAPE_ADDED===>OPENINFO')
			xbmcgui.Window(10000).setProperty('Next_EP.ResolvedUrl', 'true')
			xbmcgui.Window(10000).setProperty('Next_EP.Url', PTN_download)
			xbmcgui.Window(10000).clearProperty('Next_EP.TMDB_action')
			playlist.add(PTN_download, li)
			#xbmcplugin.addDirectoryItem(handle=handle, url=PTN_download , listitem=li, isFolder=False)
			xbmcplugin.setResolvedUrl(handle, True, li)
			xbmcplugin.endOfDirectory(handle)
			return next_ep_play_details
		else:
			xbmc.executebuiltin('Dialog.Close(busydialog)')
			xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
			playlist.clear()
			current_action = xbmcgui.Window(10000).getProperty('Next_EP.TMDB_action')
			xbmcgui.Window(10000).clearProperty('Next_EP.TMDB_action')
			xbmcgui.Window(10000).setProperty('Next_EP.current_file',PTN_download)

			playlist.add(PTN_download, li)
			#xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=li)
			#print_log(sys.argv)

			xbmcplugin.addDirectoryItem(handle=handle, url=PTN_download , listitem=li, isFolder=False)
			#tmdbhelper needs Resolved URL to be FALSE when PLAYER "is_resolvable" : "true"
			#OPENINFO===OPENINFO
			xbmcplugin.setResolvedUrl(handle, True, li)
			#xbmcplugin.setResolvedUrl(0, False, li)
			xbmcplugin.endOfDirectory(handle)
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
			processor = get_processor_info()

			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
			xbmc.Player().play(playlist)
			#xbmc.executebuiltin('PlayMedia('+PTN_download+')')

			exit()
			#return


def next_ep_play_movie(movie_year, movie_title, tmdb):
	from resources.lib.TheMovieDB import get_tmdb_data
	from resources.lib.TheMovieDB import single_movie_info
	from resources.lib.TheMovieDB import extended_movie_info
	from resources.lib.TheMovieDB import get_movie_info

	xbmc_plugin = 'True'
	li = None
	clear_next_ep_props()
	movie_title = movie_title.replace("'",'').replace('&','and')
	kodi_send_command = 'kodi-send --action="RunScript(%s,info=diamond_rd_player,type=movie,movie_title=%s,movie_year=%s,tmdb=%s,test=True)"' % (addon_ID(), movie_title, movie_year, tmdb)
	print_log(kodi_send_command,' ===>OPENINFO')

	#x265_enabled = 'False'
	#try:
	#	processor = get_processor_info()
	#	if 'linux' in str(sys.platform):
	#		if 'vero' in str(processor).lower() or 'pi 4' in str(processor).lower():
	#			print_log(str('VERO!!!'),'===>OPENINFO')
	#			x265_enabled = 'True'
	#except:
	#	x265_enabled = 'True'

	x265_enabled = xbmcaddon.Addon(addon_ID()).getSetting('x265_setting')
	#if x265_setting == 'true':
	#	x265_setting = True
	#else:
	#	x265_setting = False
	#if x265_enabled == 'True' and x265_setting == False:
	#	x265_enabled = 'False'

	movie_title_clean = regex.sub(' ', movie_title).replace('  ',' ').lower()

	print_log(x265_enabled)
	#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename),'===>OPENINFO')
	response = get_movie_info(movie_label=movie_title, year=movie_year, use_dialog=False)

	try: 
		i = response['results'][0]
	except: 
		response2 = response
		response = {}
		response['results'] = []
		response['results'].append(response2)
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
	#print_log(movie_genre,i['genre_ids'])
	#response = requests.get('https://api.themoviedb.org/3/movie/'+str(tmdb_id)+'/external_ids?api_key='+str(tmdb_api())+'&language=en-US').json()
	session_str = ''
	response = get_tmdb_data('movie/%s?append_to_response=external_ids,runtime,alternative_titles&language=%s&%s' % (tmdb_id, xbmcaddon.Addon().getSetting('LanguageID'), session_str), 14)
	imdb_id = response['external_ids']['imdb_id']
	#print_log(response)
	runtime = response['runtime']
	runtime_seconds = response['runtime']* 60

	#response = requests.get('https://api.themoviedb.org/3/movie/'+str(tmdb_id)+'/alternative_titles?api_key='+str(tmdb_api())+'&language=en-US').json()
	response = single_movie_info(movie_id=tmdb_id)

	#print_log(response)
	alternate_titles = []
	y = 0
	#print_log(response)
	for i in response['alternative_titles']['titles']:
		try:
			alternate_titles.append(response['alternative_titles']['titles'][y]['title'])
		except:
			alternate_titles.append(str(u''.join(response['alternative_titles']['titles'][y]['title']).encode('utf-8').strip()))
		y = y + 1

	trakt_progress = get_trakt_playback('movie')
	resume_progress_seconds = 0
	for i in trakt_progress:
		if str(i['movie']['ids']['tmdb']) == str(tmdb):
			resume_progress = i['progress']
			resume_progress_seconds = int(float(runtime_seconds) * float(resume_progress/100))
			break

	#print_log(alternate_titles)
	#x265_enabled = 'True'
	downloads_fail = 'False'
	torrents_fail = 'False'
	download_found = 0
	torrent_found = 0
	meta_info = {'movie_title_clean': movie_title_clean, 'alternate_titles': alternate_titles, 'x265_enabled': x265_enabled, 'movie_original_title': movie_original_title, 'movie_year': movie_year}
	
	for x in range(99):
		try:
			if downloads_fail == 'False' and download_found == 0:
				data = RD_get_page(x, 'downloads')
		except:
			downloads_fail = 'True'
			pass
		if downloads_fail == 'False' and download_found == 0:
			for i in data:
				if 'bad token' in str(data):
					try: print_log(str(data),'===>OPENINFO')
					except: print_log(data)
					return
				meta_info_flags = download_movie_test(meta_info, i['filename'])
				PTN_link = i['link']
				PTN_download = i['download']
				PTN_size = str(int(i['filesize'])/(1024*1024))+'Mb'
				try: PTN_season = meta_info_flags['PTN_season']
				except: PTN_season = ''
				try: PTN_episode = eta_info_flags['PTN_episode']
				except: PTN_episode = ''
				PTN_title = meta_info_flags['PTN_title']
				PTN_res = meta_info_flags['PTN_res']
				try:
					if str(meta_info_flags['PTN_title']) == str(movie_title_clean) and str(PTN_season) == '' and str(PTN_episode) == '' and meta_info_flags['x265_flag'] == 'False':
						download_found = 1
						headers=requests.head(PTN_download).headers
						if str('attachment') in headers.get('Content-Disposition',''):
							download_found = 1
							print_log('[' + str(PTN_size) + '][' + str(PTN_title) + '][' + str(PTN_season) + '][' + str(PTN_episode) + '][' + str(PTN_res) + '][' + str(PTN_download) + ']')
							break
						else:
							download_found = 0
				except:
					pass
		if torrent_found == 1 or download_found == 1:
			break
		try:
			if torrents_fail == 'False' and torrent_found == 0:
				data2 = RD_get_page(x, 'torrents')
				#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
		except:
			torrents_fail = 'True'
			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
			pass
		if torrents_fail == 'False' and torrent_found == 0:
			for k in data2:
				if torrent_found == 0:
					torr_response = ''
					count = 0
					meta_info_flags = download_movie_test(meta_info, k['filename'])
					if str(meta_info_flags['PTN_title']) == str(movie_title_clean) and str(meta_info_flags['PTN_season']) == '' and str(meta_info_flags['PTN_episode']) == '' and meta_info_flags['x265_flag'] == 'False':
						torr_test = True
					else:
						torr_test = False
					if torr_test == False:
						continue
					if torrent_found == 0:
						try:
							torr_data = RD_instantAvailability(torr_hash=k['hash'])
						except:
							while torr_response == '' and count < 5:
								torr_data = RD_instantAvailability(torr_hash=k['hash'])
								count = count + 1
								if torr_response != '':
									break
							if torr_response == '':
								continue
				if torrent_found == 1:
					break
				if 1==1:
					torr_data2 = {}
					torr_data3 = {}
					try: test = torr_data[k['hash']]['rd']
					except TypeError: continue
					for j in torr_data[k['hash']]['rd']:
						for x in j:
							torr_data2[x] = j[x]
							torr_data3[x] = j[x]
					for y in torr_data3.keys():
						if int(torr_data2[str(y)]['filesize']/(1024*1024)) < 20:
								torr_data2.pop(str(y), None)
					list1 = sorted(torr_data2, key = lambda z: int(z))
					y = 0
					for j in list1:
					
						try:
							test_var = str(torr_data2[str(j)]['filename'].encode('utf-8').decode('utf-8')).lower()
						except:
							test_var = str(u''.join(torr_data2[str(j)]['filename']).encode('utf-8').strip()).lower()
						torr_data2[str(j)]['filename'] = test_var
						if 'sample' in test_var:
							continue
						meta_info_flags = download_movie_test(meta_info, torr_data2[str(j)]['filename'])
						PTN_size = str(torr_data2[str(j)]['filesize']/(1024*1024)) + 'Mb'
						PTN_title = meta_info_flags['PTN_title']
						PTN_season = meta_info_flags['PTN_season']
						PTN_episode = meta_info_flags['PTN_episode']
						x265_flag = meta_info_flags['x265_flag']

						try:
							if str(PTN_title) == str(movie_title_clean) and str(PTN_season) == '' and str(PTN_episode) == '' and x265_flag == 'False':
								#PTN_link = k['links'][y]
								y = 0
								for xi in k['links']:
									PTN_link = k['links'][y]
									torr_unrestricted = RD_unrestrict_link(file_link=PTN_link)
									PTN_download = torr_unrestricted['download']
									RD_link = str(PTN_download).split('/')[4]
									ptn_data2 = ''
									try: 
										ptn_data2 = PTN.parse(urllib.parse.unquote((PTN_download)).replace('-',' ').replace('.',' '))
										file_name = str(urllib.parse.unquote(PTN_download)).split('/')[5].replace('.',' ')
									except: 
										file_name = ''
										pass
									if str(file_name.replace(' ','.')).lower() == str(torr_data2[str(j)]['filename']).lower() or str(torr_data2[str(j)]['filename'].replace('.',' ')).lower() == str(file_name).lower():
										torrent_found = 1
									else:
										torrent_found = 0
									headers=requests.head(PTN_download).headers
									if torrent_found == 1 and not str('attachment') in headers.get('Content-Disposition',''):
										torrent_found = 0
									if torrent_found == 1:
										print_log('[' + str(PTN_size) + '][' + str(PTN_title) + '][' + str(PTN_season) + '][' + str(PTN_episode) + '][' + str(PTN_res) + '][' + str(k['filename']) + '][' + str(PTN_download) + ']')
										break
									if torrent_found == 0:
										try: 
											torr_link = RD_downloads_delete(RD_link)
										except: 
											pass

									y = y + 1
							if torrent_found == 1:
								break
						except:
							pass
						y = y +1
					try:
						if str(PTN_title) == str(movie_title_clean) and str(PTN_season) == '' and str(PTN_episode) == '' and x265_flag == 'False':
							break
					except:
						pass
				#except: 
				#	pass
		if torrents_fail == 'True' and downloads_fail == 'True':
			break
		if torrent_found == 1 or download_found == 1:
			break

	print_log('END','____END____')

	#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	if torrent_found == 0 and download_found == 0:
		print_log(str('Not found1'),'===>OPENINFO')
		xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
		#exit()
		return

	movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = get_fanart_results(tvdb_id=tmdb, media_type='movie')

	con = db_connection()
	cur = con.cursor()
	movie_title2 = movie_title.replace("'","''")
	print_log(str(movie_title2),'===>OPENINFO')
	sql_result1 = cur.execute("SELECT * from files,movie where movie.idfile = files.idfile and movie.c00 = '"+str(movie_title2.replace("'","''"))+"' order by dateadded asc").fetchall()
	
	#print_log(sql_result)
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
	#	file_name = PTN_download.split('/')[5]
	#	delete_result = cur.execute("DELETE FROM files WHERE strFilename = '"+str(file_name)+"' ;")
	#	con.commit()
	#except:
	#	pass
	cur.close()

	try: movie_release_date = str(movie_release_date).replace('b\'','').replace('\'','')
	except: pass
	if xbmc_plugin == 'False' and str(PTN_title) == str(movie_title_clean) and str(PTN_season) == '' and str(PTN_episode) == '':
		print_log(movie_title)
		print_log(PTN_title)
		print_log(PTN_season)
		print_log(PTN_episode)
		print_log(PTN_res)
		print_log(PTN_link)
		print_log(PTN_size)
		print_log(PTN_download)
		print_log(dbid)

		print_log(movie_original_title)
		print_log(movie_plot)
		print_log(movie_release_date)
		print_log(movie_backdrop)
		print_log(movie_genre)
		print_log(movie_release_date[0:4])
		print_log(movie_vote_average)

		print_log(movielogo)
		print_log(hdmovielogo)
		print_log(movieposter)
		print_log(hdmovieclearart)
		print_log(movieart)
		print_log(moviedisc)
		print_log(moviebanner)
		print_log(moviethumb)
		print_log(moviebackground)
		print_log(resumeTimeInSeconds)
		print_log(duration)
		print_log(sql_result1)
	else:
		print_log('Not found')

	if xbmc_plugin == 'True' and str(PTN_title) == str(movie_title_clean) and str(PTN_season) == '' and str(PTN_episode) == '':
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


		if (movie_genre[-1] == '\'' and movie_genre[:2] == 'b\'') or (movie_genre[-1] == '"' and movie_genre[:2] == 'b"'):
			movie_genre = movie_genre[:-1]
			movie_genre = movie_genre[2:]
		if (movie_title[-1] == '\'' and movie_title[:2] == 'b\'') or (movie_title[-1] == '"' and movie_title[:2] == 'b"'):
			movie_title = movie_title[:-1]
			movie_title = movie_title[2:]
		if (movie_original_title[-1] == '\'' and movie_original_title[:2] == 'b\'') or (movie_original_title[-1] == '"' and movie_original_title[:2] == 'b"'):
			movie_original_title = movie_original_title[:-1]
			movie_original_title = movie_original_title[2:]
		if (movie_plot[-1] == '\'' and movie_plot[:2] == 'b\'') or (movie_plot[-1] == '"' and movie_plot[:2] == 'b"'):
			movie_plot = movie_plot[:-1]
			movie_plot = movie_plot[2:]


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

		if (resumetime == None or resumetime == '' or resumetime == 0) and resume_progress_seconds > 0:
			resumetime = resume_progress_seconds
			resumeTimeInSeconds = resume_progress_seconds
			xbmcgui.Window(10000).setProperty('Next_EP.resumetime', str(resumetime))

		xbmcplugin.setContent(0, 'movies')

		try:
			li = xbmcgui.ListItem(label, iconImage=thumb)
		except:
			li = xbmcgui.ListItem(label, thumb)
		li.setProperty('fanart_image', fanart)
		li.setProperty('startoffset', str(resumeTimeInSeconds))
		li.setProperty('DBID', dbid)
		li.setProperty('MovieTitle', movie_title)
		#li.setProperty('Cast', cast)
		#li.setProperty('CastAndRole', cast_role)
		li.setProperty('Duration', duration)
		li.setArt({ 'poster': poster, 'fanart': fanart, 'banner': banner, 'clearlogo': clearlogo, 'landscape': landscape, 'thumb': thumb})
		
		try:
			json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "VideoLibrary.GetMovieDetails", "params": {"movieid": '+str(dbid)+', "properties": ["art"]}}')
			json_result = json.loads(json_result)
			#print_log(str(json_result['result']['episodedetails']['art']),'===>OPENINFO')
			li.setArt(json_result['result']['moviedetails']['art'])
		except:
			pass

		try:
			json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id":1, "method": "VideoLibrary.GetMovieDetails", "params": {"movieid": '+str(dbid)+', "properties": ["title","genre","year","rating","director","trailer","tagline","plot","plotoutline","originaltitle","lastplayed","playcount","writer","studio","mpaa","cast","country","imdbnumber","runtime","set","showlink","streamdetails","top250","votes","fanart","thumbnail","file","sorttitle","resume","setid","dateadded","tag","userrating","ratings","premiered","uniqueid"]}}')
			json_result = json.loads(json_result)
			#print_log(str(json_result['result']['episodedetails']['art']),'===>OPENINFO')
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
		"""
		#li.setInfo('video', {'title': title,'genre': genre, 'plotoutline': plotoutline, 'plot': plot, 'path': PTN_download,'premiered': premiered, 'dbid': dbid, 'mediatype': dbtype, 'writer': writer, 'director': director, 'duration': duration, 'IMDBNumber': imdb, 'MPAA': MPAA, 'Rating': rating, 'Studio': studio, 'Year': year, 'Tagline': tagline, 'Set': set, 'SetID': setid})
		li.setInfo('video', {'title': title, 'MovieTitle': movie_title, 'genre': genre, 'plotoutline': plotoutline, 'plot': plot, 'path': PTN_download,'premiered': premiered, 'dbid': dbid, 'mediatype': dbtype, 'duration': duration, 'IMDBNumber': imdb, 'Rating': rating, 'Year': year})
		"""
		li.setPath(PTN_download)

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
		infolabels['FileNameAndPath'] = PTN_download
		infolabels['path'] = PTN_download

		#li.setInfo(type='Video', infoLabels = infolabels)
		try:
			info_tag = ListItemInfoTag(li, 'video')
			info_tag.set_info(infolabels)
		except:
			li.setInfo(type='Video', infoLabels = infolabels)
		#info_tag.set_cast(infolabels['Cast'])
		#info_tag.set_cast(infolabels['CastAndRole'])

		if 'test=True' in str(sys.argv):
			#print_log(sys.argv)
			#print_log(next_ep_play_details,'next_ep_play_details')
			xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
			exit()

		playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		current_action = xbmcgui.Window(10000).getProperty('Next_EP.TMDB_action')
		#if 'seren' not in current_action and current_action != '': 
		#	print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename),'===>OPENINFO')
		#	xbmcgui.Window(10000).setProperty('Next_EP.ResolvedUrl', 'true')
		#	xbmcgui.Window(10000).setProperty('Next_EP.Url', PTN_download)
		#	xbmcgui.Window(10000).clearProperty('Next_EP.TMDB_action')
		#	playlist.clear()
		#	playlist.add(PTN_download, li)
		#	print_log('['+str(title)+']'+'[E'+str(show_episode)+']'+'[S'+str(show_season)+']'+'['+str(show_title)+']'+'['+str(PTN_download)+']','_PRESCRAPE_ADDED===>OPENINFO')
		#if 'seren' not in current_action and current_action == '':
		#	print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename),'===>OPENINFO')
		#	xbmcgui.Window(10000).setProperty('Next_EP.ResolvedUrl', 'true')
		#	xbmcgui.Window(10000).setProperty('Next_EP.Url', PTN_download)
		#	xbmcgui.Window(10000).clearProperty('Next_EP.TMDB_action')
		#	playlist.add(PTN_download, li)		
		#	print_log('['+str(title)+']'+'[E'+str(show_episode)+']'+'[S'+str(show_season)+']'+'['+str(show_title)+']'+'['+str(PTN_download)+']','_PRESCRAPE_ADDED===>OPENINFO')
		playlist.clear()
		xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
		playlist.add(PTN_download, li)
		#xbmcplugin.addDirectoryItem(handle=0, url=PTN_download , listitem=li, isFolder=False)
		xbmcplugin.setResolvedUrl(0, True, li)
		xbmcplugin.endOfDirectory(0)
		#xbmc.Player().play(item=PTN_download, listitem=li)
		xbmc.Player().play(playlist)
		"""
		count = 0
		kodi_playback_stopped = 'RunScript('+str(script_path)+'/kodi_playback_stopped.py)'
		xbmc.executebuiltin(kodi_playback_stopped)
		while xbmc.Player().isPlaying()==1 and count < 5001:
					xbmc.sleep(100)
					count = count + 100
		json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":8,"params":{"addonid":"plugin.video.realizer","enabled":true}}')
		print_log(str(json_result)+'plugin.video.realizer_ENABLED===>service.next_playlist2')
		"""
		exit()
		#return
