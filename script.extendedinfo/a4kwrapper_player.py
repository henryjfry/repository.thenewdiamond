#!/usr/bin/python3
import requests
import time, datetime

import urllib
from urllib.parse import quote, unquote

import xbmc, xbmcgui, xbmcplugin, xbmcaddon, json
import sqlite3
import re
import sys

from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib.library import trak_auth
#from resources.lib.TheMovieDB import get_tvshow_ids
from resources.lib.TheMovieDB import extended_episode_info
from resources.lib.TheMovieDB import extended_tvshow_info
from resources.lib.TheMovieDB import get_trakt_playback


from a4kscrapers_wrapper import getSources, real_debrid, tools, source_tools, get_meta, distance
from a4kscrapers_wrapper.getSources import Sources
rd_api = real_debrid.RealDebrid()

import importlib
try:
	from importlib import reload as reload_module  # pylint: disable=no-name-in-module
except ImportError:
	# Invalid version of importlib
	from imp import reload as reload_module

from pathlib import Path
import os.path
import subprocess
from inspect import currentframe, getframeinfo
script_path = os.path.dirname(os.path.abspath(getframeinfo(currentframe()).filename))
#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))

current_directory = str(getframeinfo(currentframe()).filename.replace(os.path.basename(getframeinfo(currentframe()).filename),'').replace('','')[:-1])
sys.path.append(current_directory)
sys.path.append(current_directory.replace('a4kscrapers_wrapper',''))

from resources.lib.library import db_connection

#from resources.lib.Utils import get_JSON_response
#from resources.lib.TheMovieDB import get_fanart_data
#from resources.lib.TheMovieDB import get_tmdb_data

#from resources.lib.library import get_processor_info

try:
	from infotagger.listitem import ListItemInfoTag
except:
	pass

import sys
if sys.version_info[0] >= 3:
	unicode = str
	basestring = str

#from resources import PTN
import re
regex = re.compile('[^a-zA-Z0-9]')

from os.path import expanduser
home = expanduser("~")



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
	next_ep_props_list = ['Next_EP.ResolvedUrl', 'Next_EP.ResolvedUrl_playlist', 'Next_EP.Url', 'Next_EP.poster', 'Next_EP.fanart', 'Next_EP.clearlogo', 'Next_EP.landscape', 'Next_EP.banner', 'Next_EP.thumb', 'Next_EP.duration', 'Next_EP.dbid', 'Next_EP.dbtype', 'Next_EP.genre', 'Next_EP.imdb', 'Next_EP.icon', 'Next_EP.label', 'Next_EP.label2', 'Next_EP.originaltitle', 'Next_EP.plot', 'Next_EP.plotoutline', 'Next_EP.premiered', 'Next_EP.rating', 'Next_EP.movie_title', 'Next_EP.title', 'Next_EP.year', 'Next_EP.resumetime', 'diamond_player_time']
	for i in next_ep_props_list:
		xbmcgui.Window(10000).clearProperty(i)
	#print_log(sys.argv)


def print_log(log_item1, log_item2=None):
	xbmc.log(str(log_item1)+str(log_item2)+'===>OPENINFO', level=xbmc.LOGFATAL)

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


def get_next_ep_details(show_title, season_num, ep_num, tmdb):
	meta = get_meta.get_episode_meta(season=season_num,episode=ep_num,show_name=show_title, tmdb=tmdb, interactive=False)
	info = meta['episode_meta']

	daily_show_flag = False
	if info['episode_air_date'][-2:] in info['title'] and info['episode_air_date'][:4] in info['title']:
		if datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%B %d, %Y') in info['title']:
			daily_show_flag = True

	xbmcgui.Window(10000).clearProperty('Next_EP.ResolvedUrl')

	tvdb_id = meta['tvdb']
	tmdb_id = tmdb

	show_id = meta['tvmaze_show_id']
	curr_ep_flag = False
	air_date_timestamp = 0
	if daily_show_flag == False:
		meta_source = 'tvmaze_seasons'
	else:
		meta_source = 'tmdb_seasons'
	for i in meta[meta_source]['episodes']:
		i_air_date = str(i.get('air_date','1901-01-01'))
		try: i_air_date = datetime.datetime.strptime(i_air_date, "%Y-%m-%d")
		except TypeError: i_air_date = datetime.datetime(*(time.strptime(i_air_date, "%Y-%m-%d")[0:6]))
		i_air_date = i_air_date.timetuple()
		air_date_timestamp = time.mktime(i_air_date)
		if int(i['episode']) == int(ep_num) and int(i['season']) == int(season_num):
			curr_ep_flag = True
			curr_air_date_timestamp = air_date_timestamp

		if int(i['episode']) > int(ep_num) and int(i['season']) == int(season_num) and curr_ep_flag == True:
			curr_ep_flag = False
			next_ep_episode = i['episode']
			next_ep_season = i['season']
			break

	#tools.log('curr_air_date_timestamp',curr_air_date_timestamp,'air_date_timestamp',air_date_timestamp)
	if curr_ep_flag == True:
		next_ep_episode = 1
		next_ep_season = int(i['season']) + 1
		if meta_source == 'tmdb_seasons':
			if next_ep_season > (meta['total_seasons']):
				print_log(str('ENDED')+'===>PHIL')
				return None
		else:
			if next_ep_season > (meta['tvmaze_total_seasons']):
				print_log(str('ENDED')+'===>PHIL')
				return None
		meta = get_meta.get_episode_meta(season=next_ep_season,episode=next_ep_episode,show_name=show_title, tmdb=tmdb, interactive=False)
	else:
		if air_date_timestamp > ( time.time()+60*60*36): #air_date > tomorrow
			print_log(str('NET_EP_NOT_AIRED')+'===>PHIL')
			return None
		if air_date_timestamp == None or str(air_date_timestamp) == '' and curr_air_date_timestamp >= ( time.time()-(60*60*24*2.5)): #air_date > today- 2.5days
			print_log(str('NET_EP_NOT_AIRED')+'===>PHIL')
			return None

	for i in meta[meta_source]['episodes']:
		if int(i['episode']) == int(next_ep_episode) and int(i['season']) == int(next_ep_season):
			next_ep_show = i['tvshowtitle']
			next_ep_thumbnail = i['still_path']
			next_ep_title = i['name']
			next_ep_rating = i['vote_average']
			next_ep_year = i['year']
			if daily_show_flag == False:
				next_ep_id = i['tvmaze_ep_id']
			air_date = i.get('airdate','')

	if daily_show_flag:
		response = {'id': None, 'summary': None, '_embedded': {'show': {'genres': []}}}
	else:
		url = 'http://api.tvmaze.com/episodes/'+str(next_ep_id)+'?embed=show'
		#response = get_JSON_response(url=url, cache_days=7.0, folder='TVMaze')
		response = get_meta.get_response_cache(url=url, cache_days=7.0, folder='TVMaze')
	next_ep_genre = response['_embedded']['show']['genres']
	strm_title = '%s - S%sE%s - %s' % (next_ep_show, str(next_ep_season).zfill(2),str(next_ep_episode).zfill(2), next_ep_title)
	
	#plot = response['summary'].replace('<p>','').replace('</p>','')
	#runtime = response['runtime']
	#tvmaze_thumb_large = response['image']['medium'].replace('medium','large')
	#tvmaze_thumb_original = response['image']['original'].replace('medium','large')
	strm_title = str(next_ep_show)+' - S'+str(next_ep_season)+'E'+str(next_ep_episode)+' - '+str(next_ep_title)
	print_log(str(strm_title)+'strm_title===NEW_diamond_rd_player.py')
	next_ep_details = {}
	next_ep_details['next_ep_show'] = next_ep_show
	next_ep_details['next_ep_season'] = next_ep_season
	next_ep_details['next_ep_episode'] = next_ep_episode
	next_ep_details['next_ep_title'] = next_ep_title
	next_ep_details['next_ep_thumbnail'] = next_ep_thumbnail
	next_ep_details['next_ep_thumb2'] = next_ep_thumbnail
	#if next_ep_thumbnail:
	#	next_ep_details['next_ep_thumbnail'] = next_ep_thumbnail
	#else:
	#	next_ep_details['next_ep_thumbnail'] = next_ep_thumb2
	next_ep_details['tmdb_id'] = tmdb_id
	next_ep_details['tvdb_id'] = tvdb_id
	next_ep_details['next_ep_genre'] = next_ep_genre
	next_ep_details['next_ep_year'] = next_ep_year
	next_ep_details['air_date'] = air_date
	next_ep_details['strm_title'] = strm_title
	#next_ep_details['next_ep_thumb2'] = next_ep_thumb2
	next_ep_details['next_ep_rating'] = next_ep_rating
	#next_ep_details['next_ep_rating2'] = next_ep_rating2
	print_log(next_ep_details, 'next_ep_details')
	return next_ep_details



def next_ep_play(show_title, show_season, show_episode, tmdb, auto_rd=True, prescrape_test=None):
	#from resources.lib.TheMovieDB import get_tmdb_data
	#from resources.lib.TheMovieDB import single_tvshow_info
	#from resources.lib.TheMovieDB import get_tvshow_info

	xbmc_plugin = 'True'
	#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	if not xbmc.Player().isPlaying():
		xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
		xbmc.executebuiltin('ActivateWindow(busydialog)')
	li = None
	clear_next_ep_props()
	
	#try:
	#	if int(tmdb) > 1:
	#		tmdb_id = tmdb
	#		tmdb_response = extended_tvshow_info(tvshow_id=tmdb_id, cache_time=0.001)
	#		show_title = tmdb_response[0]['TVShowTitle']
	#except:
	#	tmdb_response = None
	#	pass
	show_title = show_title.replace(' s ', 's ')
	kodi_send_command = 'kodi-send --action="RunScript(%s,info=a4kwrapper_player,type=tv,show_title=%s,show_season=%s,show_episode=%s,tmdb=%s,test=True)"' % (addon_ID(), show_title, show_season, show_episode, tmdb)
	if 'select_dialog=True' in str(sys.argv):
		kodi_send_command = kodi_send_command.replace(',test=True',',select_dialog=True,test=True')
	if 'unrestrict=True' in str(sys.argv):
		kodi_send_command = kodi_send_command.replace(',test=True',',unrestrict=True,test=True')
	print_log(kodi_send_command,'___kodi_send_command')
	meta = get_meta.get_episode_meta(season=show_season,episode=show_episode,show_name=show_title, tmdb=tmdb, interactive=False)
	def meta_process(meta):
		show_title = meta['episode_meta']['info']['tvshowtitle']
		show_season = int(meta['episode_meta']['info']['season'])
		try: 
			show_episode = int(meta['episode_meta']['info']['episode'])
		except ValueError: 
			show_episode = 0
			meta['episode_meta']['info']['episode'] = 0
		for i in meta['tmdb_seasons']['episodes']:
			if int(i['episode']) == int(show_episode) and int(i['season']) == int(show_season):
				info1 = i
		for i in meta['tvmaze_seasons']['episodes']:
			if meta['episode_meta'].get('special',False):
				for x in meta['tmdb_seasons']['episodes']:
					if str(x['name']) in str(i.get('name')) or distance.jaro_similarity(str(x['name']),str(i.get('name'))) > 0.85:
						tmdb_season = x['season']
						tmdb_episode = x['episode']
						if int(tmdb_episode) == int(show_episode) and int(tmdb_season) == int(show_season) and show_episode != 0:
							info2 = i
							break
						if show_episode == 0 and (str(x['name']) in str(i.get('name')) or distance.jaro_similarity(str(x['name']),str(i.get('name'))) > 0.85):
							info2 = i
							break
			elif int(i['episode']) == int(show_episode) and int(i['season']) == int(show_season):
				info2 = i
		try: 
			info1['tvmaze_ep_id'] = info2['tvmaze_ep_id']
		except: 
			info1['tvmaze_ep_id'] = False
			tools.log('missing on TMDB!!!')
		try: info = info2
		except: info = info1
		meta_info = info

		show_title = show_title.replace('+', ' ')
		if not xbmc.Player().isPlaying():
			xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
			xbmc.executebuiltin('ActivateWindow(busydialog)')


		show_title_clean = regex.sub(' ', show_title.replace('\'s','s').replace('&','and')).replace('  ',' ').lower().replace(' s ','s ')
		tmdb_id = tmdb
		#response = get_tvshow_info(tvshow_label=show_title, year=None, use_dialog=False)
		#tmdb_id2 = response['id']
		#try:
		#	if int(tmdb) > 1:
		#		tmdb_id = tmdb
		#except:
		#	pass

		#if tmdb_response:
		#	response = tmdb_response
		#else:
		#	response = extended_tvshow_info(tvshow_id=tmdb_id, cache_time=0.001)
		#extended_tvshow_info_response = response

		tvdb_id = info['tvdb']
		imdb_id = info['imdb_id']

		#response = get_tmdb_data(url='tv/'+str(tmdb_id)+'/alternative_titles?language=en-US&')
		alternate_titles = []
		y = 0
		for i in info['aliases']:
			try:
				alternate_titles.append(i)
			except:
				alternate_titles.append(str(u''.join(i).encode('utf-8').strip()))
			y = y + 1

		tv_maze_rating = info['vote_average']
		episode_name = info['title']
		year = info['year']
		air_date = info['air_date']
		if info['tvmaze_ep_id']:
			episode_id = info['tvmaze_ep_id']
			url = 'http://api.tvmaze.com/episodes/'+str(episode_id)+'?embed=show'
			#response = get_JSON_response(url=url, cache_days=7.0, folder='TVMaze')
			response = get_meta.get_response_cache(url=url, cache_days=7.0, folder='TVMaze')
		else:
			episode_id = 0
			response = {'id': None, 'summary': None, '_embedded': {'show': {'genres': []}}}
		try: 
			tmdb_response = extended_episode_info(tvshow_id=tmdb_id, season=show_season, episode=show_episode, cache_time=3)
			extended_tvshow_info_response = extended_tvshow_info(tvshow_id=tmdb_id, cache_time=3)
			#tools.log(tmdb_response, extended_tvshow_info_response)
		except:
			tmdb_response = None
			extended_tvshow_info_response = None

		#try:
		#	if not (tmdb_response['runtime'] and info1['runtime']):
		#		runtime2 = int(extended_tvshow_info_response['runtime'].split('-')[0])
		#	elif tmdb_response['runtime']:
		#		runtime2 = int(tmdb_response['runtime'])
		#	elif info1['runtime']:
		#		runtime2 = int(info1['runtime'])
		#	else:
		#		runtime2 = 0
		#except:
		#	runtime2 = 0
		
		try: test = response['id']
		except: response = eval(str(response).replace('null','"null"'))

		plot = response['summary']
		try: plot = re.sub('<[^<]+?>', '', plot)
		except: plot = ''
		genre = response['_embedded']['show']['genres']
		if tv_maze_rating:
			rating = float(tv_maze_rating)
		else:
			rating = None

		#tools.log(response)
		#tools.log(tmdb_response)
		#tools.log(extended_tvshow_info_response)
		#tools.log(info1)
		#tools.log(info)
		try: runtime = int(info['runtime'])
		except: runtime = 0

		runtime_list = []
		try: runtime_list.append(response.get('runtime',0))
		except: pass
		try: runtime_list.append(tmdb_response[1].get('runtime',0))
		except: pass
		try: runtime_list.append(extended_tvshow_info_response[0].get('duration','0').split(' -')[0])
		except: pass
		try: runtime_list.append(info1.get('runtime',0))
		except: pass
		try: runtime_list.append(info.get('runtime',0))
		except: pass
		
		#try: runtime_list = [tmdb_response[1].get('runtime',0),extended_tvshow_info_response[0].get('duration','0').split(' -')[0], info1.get('runtime',0), info.get('runtime',0)]
		#except: runtime_list = [tmdb_response[1].get('runtime',0),extended_tvshow_info_response[0].get('duration','0').split(' -')[0], info.get('runtime',0)]
		runtime_list = [i for i in   [int(x or 0) for x in runtime_list]   if i != 0]
		runtime = min(runtime_list)
		#if runtime2 < runtime and runtime2 != 0:
		#	runtime = runtime2
		episode_thumb = info['still_path']

		try: runtime_seconds = int(runtime) * 60
		except: runtime_seconds = 30 * 60

		trakt_progress = get_trakt_playback('tv')
		resume_progress_seconds = 0
		if trakt_progress:
			for i in trakt_progress:
				if str(i['show']['ids']['tmdb']) == str(tmdb_id):
					if str(i['episode']['season']) == str(show_season) and str(i['episode']['number']) == str(show_episode):
						resume_progress = i['progress']
						resume_progress_seconds = int(float(runtime_seconds) * float(resume_progress/100))
						break

		if (rating == '' or str(rating) == '0.0' or rating == None) or (air_date == '' or air_date == None) or (episode_thumb == '' or episode_thumb == None):
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
					if rating == '' or str(rating) == '0.0' or rating == None:
						rating = imdb_rating
					if air_date == '' or air_date == None:
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
								if episode_thumb == '' or episode_thumb == None:
									episode_thumb = imdb_thumb
								break
						except: pass
						y = y + 1
				x = x + 1

				#ORIGINAL THUMB SIZE
				#._V1_UY126_CR0,0,224,126_AL_.jpg

				#x4 THUMB SIZE
				#._V1_UY504_CR0,0,896,504_AL_.jpg
		if rating == '' or str(rating) == '0.0' or rating == None:
			try: rating = info1['vote_average']
			except: rating = ''
		if episode_thumb == '' or episode_thumb == None:
			try: episode_thumb = info1['still_path']
			except: episode_thumb = ''
		if air_date == '' or air_date == None:
			try: air_date = info1['air_date']
			except: air_date = ''
		return meta_info, show_title, episode_thumb, air_date, resume_progress_seconds, runtime, rating, genre, plot, episode_id, year, episode_name, tv_maze_rating, alternate_titles, imdb_id, tvdb_id, tmdb_id, show_title_clean, show_title, info, tmdb_response, extended_tvshow_info_response

	##SCRAPE CLOUD
	tools.log('prescrape_test',prescrape_test)
	#tools.log(sys.argv)
	if 'cloud_scrape=False' in str(sys.argv):
		cloud_scrape = False
	else:
		cloud_scrape = True

	if xbmc.Player().isPlaying() == True:
		player_playing = True
	else:
		player_playing = False

	PTN_download = ''
	if cloud_scrape:
		tools.log('SCRAPE_CLOUD')
		PTN_download, new_meta = getSources.check_rd_cloud(meta)
	#exit()

	print_log('END__SCRAPE_CLOUD__END__')
	if 'select_dialog=True' in str(sys.argv):
		select_dialog = True
	else:
		select_dialog = False
	if 'unrestrict=True' in str(sys.argv):
		unrestrict = True
	else:
		unrestrict = False

	if 'prescrape=True' in str(sys.argv):
		if not 'http' in str(PTN_download):
			print_log(str('Not found_CLOUD'),'===>OPENINFO')
			##AUTO_SCRAPE_TORRENTS
			
			PTN_download, new_meta = getSources.auto_scrape_rd(meta,select_dialog=select_dialog,unrestrict=unrestrict)
			xbmcgui.Window(10000).setProperty('diamond_download_link',str(PTN_download))
			if not 'http' in str(PTN_download):
				print_log(str('Not found_AUTO_SCRAPE'),'===>OPENINFO')
				return
		if 'http'  in str(PTN_download):
			tools.log('prescrape_DOWNLOAD_FOUND!!',PTN_download)
			xbmcgui.Window(10000).setProperty('diamond_download_link',str(PTN_download))
			return

	if auto_rd == True:
		if not 'http' in str(PTN_download):
			print_log(str('Not found_CLOUD'),'===>OPENINFO')
			##AUTO_SCRAPE_TORRENTS
			
			PTN_download, new_meta = getSources.auto_scrape_rd(meta,select_dialog=select_dialog,unrestrict=unrestrict)
			
			if not 'http' in str(PTN_download):
				print_log(str('Not found_AUTO_SCRAPE'),'===>OPENINFO')
				return
		if 'http'  in str(PTN_download):
			tools.log('prescrape_DOWNLOAD_FOUND!!',PTN_download)

	if not 'http' in str(PTN_download) and prescrape_test:
		PTN_download = prescrape_test
		new_meta = meta
		tools.log('prescrape_DOWNLOAD_FOUND!!',PTN_download)
	

	#print_log('SUBTITLES_____________')
	#from a4kscrapers_wrapper import subs
	#meta = getSources.get_subtitles_meta(meta, PTN_download)
	#tools.VIDEO_META = meta

	#subfile = subs.SubtitleService(meta).get_subtitle()
	#tools.SUB_FILE = subfile
	#tools.VIDEO_META['SUB_FILE'] = subfile
	#tools.log('SUBTITLES_____________',tools.VIDEO_META)
	#print_log('SUBTITLES_____________')
	#SUB_FILE = tools.VIDEO_META['SUB_FILE']
	#SUB_FILE_FORCED = tools.VIDEO_META['SUB_FILE_FORCED']
	#subs_list = []
	#if str(SUB_FILE) != '' and SUB_FILE != None:
	#	subs_list.append(SUB_FILE)
	#if str(SUB_FILE_FORCED) != '' and SUB_FILE_FORCED != None:
	#	subs_list.append(SUB_FILE_FORCED)

	meta_info, show_title, episode_thumb, air_date, resume_progress_seconds, runtime, rating, genre, plot, episode_id, year, episode_name, tv_maze_rating, alternate_titles, imdb_id, tvdb_id, tmdb_id, show_title_clean, show_title, info, tmdb_response, extended_tvshow_info_response = meta_process(new_meta)
	hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = get_fanart_results(tvdb_id, media_type='tv_tvdb',show_season=show_season )

	#tools.log('a4kw_meta_info',meta_info)
	#subs_list = getSources.get_subtitles_list(meta_info, PTN_download)
	#from getSources import get_subtitles_list
	RD_player_subs = xbmcaddon.Addon(addon_ID()).getSetting('RD_player_subs')
	RD_player_subs_clean = xbmcaddon.Addon(addon_ID()).getSetting('RD_player_subs_clean')
	if RD_player_subs == True or RD_player_subs == 'true':
		try: subs = importlib.import_module("subs")
		except: subs = reload_module(importlib.import_module("subs"))
		subs.META = meta_info
		subs_list = subs.get_subtitles_list(meta_info, PTN_download)
		del subs
		#exit()
		if len(subs_list) > 0:
			if RD_player_subs_clean == True or RD_player_subs_clean == 'true':
				from subcleaner import clean_file
				from pathlib import Path
				for i in subs_list:
					sub = Path(i)
					clean_file.clean_file(sub)
				tools.sub_cleaner_log_clean()
				clean_file.files_handled = []
	else:
		subs_list = []


	con = db_connection()
	cur = con.cursor()
	sql_result1 = cur.execute("SELECT idepisode, * from files,episode,tvshow where episode.idfile = files.idfile and episode.idshow = tvshow.idshow and tvshow.c00 = '"+str(show_title).replace("'","''")+"' and episode.c12 = '"+str(show_season)+"' and episode.c13 = '"+str(show_episode)+"' order by dateadded asc").fetchall()


	try: dbid = sql_result1[0][0]
	except: dbid = 0
	if dbid == 0 and len(sql_result1)>0:
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

	try:
		file_name = PTN_download.split('/')[5]
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


	#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	next_ep_play_details = {}
	next_ep_play_details['ResolvedUrl'] = True
	next_ep_play_details['show_title'] = show_title
	next_ep_play_details['PTN_title'] = episode_name
	next_ep_play_details['PTN_season'] = show_season
	next_ep_play_details['PTN_episode'] = show_episode
	#next_ep_play_details['PTN_res'] = PTN_res
	#next_ep_play_details['PTN_link'] = PTN_link
	#next_ep_play_details['PTN_size'] = PTN_size
	next_ep_play_details['PTN_download'] = PTN_download
	next_ep_play_details['dbid'] = dbid
	next_ep_play_details['dbtype'] = 'episode'
	next_ep_play_details['episode_name'] = episode_name
	next_ep_play_details['plot'] = plot
	next_ep_play_details['air_date'] = air_date
	next_ep_play_details['episode_thumb'] = episode_thumb
	next_ep_play_details['next_ep_thumb2'] = episode_thumb
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
	if showbackground == '' or showbackground == None:
		try: showbackground = extended_tvshow_info_response[0]['fanart_original']
		except: showbackground = tvthumb
	next_ep_play_details['showbackground'] = showbackground
	next_ep_play_details['fanart'] = showbackground
	next_ep_play_details['landscape'] = showbackground
	next_ep_play_details['clearlogo'] = clearlogo
	next_ep_play_details['characterart'] = characterart
	next_ep_play_details['tvposter'] = tvposter
	next_ep_play_details['poster'] = tvposter
	if tvposter == '' or tvposter == None:
		next_ep_play_details['poster'] = seasonposter
	if tvposter == '' or tvposter == None:
		try: tvposter = extended_tvshow_info_response[0]['poster_original']
		except: tvposter = seasonposter
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

	#print_log(next_ep_play_details)

	#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	if xbmc_plugin == 'True' and (PTN_download):
		#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
		if seasonposter != '' and seasonposter != None:
			poster = seasonposter 
		elif tvposter != '' and tvposter != None:
			poster = tvposter
		else:
			poster = extended_tvshow_info_response[0]['poster_original']
		xbmcgui.Window(10000).setProperty('Next_EP.poster', poster)
		fanart = showbackground
		xbmcgui.Window(10000).setProperty('Next_EP.fanart', fanart)
		if clearlogo == '' :
			clearlogo = hdtvlogo
		else:
			clearlogo = clearlogo
		xbmcgui.Window(10000).setProperty('Next_EP.clearlogo', clearlogo)
		landscape = showbackground
		if landscape == '' or  landscape == None:
			try: landscape = extended_tvshow_info_response[0]['fanart_original']
			except: landscape = tvthumb
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
		#if genre != '':
		#	if (genre[-1] == '\'' and genre[:2] == 'b\'') or (genre[-1] == '"' and genre[:2] == 'b"'):
		#		genre = genre[:-1]
		#		genre = genre[2:]
		#if (episode_name[-1] == '\'' and episode_name[:2] == 'b\'') or (episode_name[-1] == '"' and episode_name[:2] == 'b"'):
		#	episode_name = episode_name[:-1]
		#	episode_name = episode_name[2:]
		#if (show_title[-1] == '\'' and show_title[:2] == 'b\'') or (show_title[-1] == '"' and show_title[:2] == 'b"'):
		#	show_title = show_title[:-1]
		#	show_title = show_title[2:]
		#if (plot[-1] == '\'' and plot[:2] == 'b\'') or (plot[-1] == '"' and plot[:2] == 'b"'):
		#	plot = plot[:-1]
		#	plot = plot[2:]

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
		if not rating:
			rating = '0.0'
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
			if PTN_download == '' or not 'http' in str(PTN_download):
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

		if len(subs_list) > 0:
			li.setSubtitles(subs_list)

		li.setProperty('IsPlayable', 'true')
		li.setProperty('IsFolder', 'false')
		li.setPath(PTN_download)

		#li.setInfo('video', {'title': title,'genre': genre, 'plotoutline': plotoutline, 'plot': plot, 'path': PTN_download,'premiered': premiered, 'dbid': dbid, 'mediatype': dbtype, 'writer': writer, 'director': director, 'duration': duration, 'IMDBNumber': imdb, 'MPAA': MPAA, 'Rating': rating, 'Studio': studio, 'Year': year, 'Tagline': tagline, 'Set': set, 'SetID': setid})
		#li.setInfo('video', {'title': title, 'TVShowTitle': show_title, 'Episode': str(show_episode), 'Season': show_season,'genre': genre, 'plotoutline': plotoutline, 'plot': plot, 'path': PTN_download,'premiered': premiered, 'dbid': dbid, 'mediatype': dbtype, 'duration': duration, 'IMDBNumber': imdb, 'Rating': rating, 'Year': year})

		#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
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
			info_tag_flag = False
			if tmdb_response:
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
						info_tag_flag = True
						info_tag.set_cast(actors)
					except:
						li.setCast(actors)
					li.setProperty('Cast', str(actors))
					li.setProperty('CastAndRole', str(actors))
					#infolabels['Cast'] = list(zip(actor_name,actor_role,actor_thumbnail,actor_order))
					#infolabels['CastAndRole'] = list(zip(actor_name,actor_role,actor_thumbnail,actor_order))
					#li.setInfo('video', {'Cast': list(zip(actor_name,actor_role,actor_thumbnail,actor_order)), 'CastAndRole': list(zip(actor_name,actor_role,actor_thumbnail,actor_order)) })
				director = []
				writer = []
				for i in tmdb_response[1]['crew']:
					if 'Director' in str(i):
						director.append(i['name'])
					if 'Writer' in str(i):
						writer.append(i['name'])
			studio = []
			if extended_tvshow_info_response:
				for i in extended_tvshow_info_response[1]['studios']:
					studio.append(i['title'])

			if extended_tvshow_info_response:
				infolabels['votes'] = int(extended_tvshow_info_response[0]['Votes'])
				infolabels['mpaa'] = extended_tvshow_info_response[0]['mpaa']
				infolabels['studio'] = studio
			if tmdb_response:
				infolabels['director'] = director
				infolabels['writer'] = writer


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
			infolabels['mediatype'] = 'episode'
			infolabels['title'] = episode_name
			infolabels['originaltitle'] = episode_name
			infolabels['sorttitle'] = episode_name
			infolabels['plot'] = plot
			infolabels['plotoutline'] = plot
			infolabels['tvshowtitle'] = show_title
			infolabels['playcount'] = 0

			infolabels['genre'] = genre

			#infolabels['FileNameAndPath'] = PTN_download
			#infolabels['EpisodeName'] = episode_name

			li.setProperty('FileNameAndPath', str(PTN_download))
			li.setProperty('EpisodeName', str(episode_name))

			infolabels['path'] = PTN_download

			#li.setInfo(type='Video', infoLabels = infolabels)
			try:
				if info_tag_flag == False:
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
			print_log('EXIT')
			#print_log(infolabels)
			print_log({ 'poster': poster, 'fanart': fanart, 'banner': banner, 'clearlogo': clearlogo, 'landscape': landscape, 'thumb': thumb})
			#print_log(next_ep_play_details,'next_ep_play_details')
			print_log(str(infolabels)[:750].replace('\'','"'),'===>OPENINFO')
			#exit()
			return
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
		elif player_playing == True and xbmc.Player().isPlaying() == False:
			print_log(str('Play_State_Changed_During_Execution_RETURN'),'===>OPENINFO')
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
			#processor = get_processor_info()

			#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
			xbmc.Player().play(playlist)
			#xbmc.executebuiltin('PlayMedia('+PTN_download+')')

			#exit()
			#return


def next_ep_play_movie(movie_year, movie_title, tmdb):
	from resources.lib.TheMovieDB import get_tmdb_data
	from resources.lib.TheMovieDB import single_movie_info
	from resources.lib.TheMovieDB import extended_movie_info
	from resources.lib.TheMovieDB import get_movie_info

	#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	xbmc_plugin = 'True'
	li = None
	clear_next_ep_props()
	movie_title = movie_title.replace("'",'').replace('&','and')
	kodi_send_command = 'kodi-send --action="RunScript(%s,info=a4kwrapper_player,type=movie,movie_title=%s,movie_year=%s,tmdb=%s,test=True)"' % (addon_ID(), movie_title, movie_year, tmdb)
	if 'select_dialog=True' in str(sys.argv):
		kodi_send_command = kodi_send_command.replace(',test=True',',select_dialog=True,test=True')
	#if 'unrestrict=True' in str(sys.argv):
	#	kodi_send_command = kodi_send_command.replace(',test=True',',unrestrict=True,test=True')
	print_log(kodi_send_command,' ===>OPENINFO')

	x265_enabled = xbmcaddon.Addon(addon_ID()).getSetting('x265_setting')

	meta = get_meta.get_movie_meta(tmdb=tmdb, movie_name=movie_title, year=movie_year, interactive=False)
	#tools.log(meta)

	def meta_process(meta):

		tmdb_id = meta['tmdb_id']
		movie_title = meta['title']
		movie_year = meta['year']
		#tools.log(tmdb_id, meta)
		movie_title_clean = regex.sub(' ', movie_title).replace('  ',' ').lower()

		#print_log(x265_enabled,'x265_enabled')
		#print_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename),'===>OPENINFO')
		response = get_movie_info(movie_label=meta['title'], year=meta['year'], use_dialog=False, item_id=meta['tmdb_id'])
		

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

		return movie_title_clean, tmdb_id, runtime_seconds, resume_progress_seconds, movie_year, movie_vote_count, movie_vote_average, movie_title, movie_release_date, movie_poster, movie_popularity, movie_plot, movie_original_title, movie_original_language, movie_genre, movie_backdrop, imdb_id, genres, alternate_titles

	##SCRAPE CLOUD
	if 'cloud_scrape=False' in str(sys.argv):
		cloud_scrape = False
	else:
		cloud_scrape = True

	PTN_download = ''
	if cloud_scrape:
		tools.log('SCRAPE_CLOUD')
		PTN_download, new_meta = getSources.check_rd_cloud(meta)

	#exit()
	print_log('END__SCRAPE_CLOUD__END__')

	if 'select_dialog=True' in str(sys.argv):
		select_dialog = True
	else:
		select_dialog = False

	if not 'http' in str(PTN_download):
		print_log(str('Not found_CLOUD'),'===>OPENINFO')
		##AUTO_SCRAPE_TORRENTS
		
		PTN_download, new_meta = getSources.auto_scrape_rd(meta,select_dialog=select_dialog)
		
		if not 'http' in str(PTN_download):
			print_log(str('Not found_AUTO_SCRAPE'),'===>OPENINFO')
			return

	#print_log('SUBTITLES_____________')
	#from a4kscrapers_wrapper import subs
	#meta = getSources.get_subtitles_meta(meta, PTN_download)
	#tools.VIDEO_META = meta

	#subfile = subs.SubtitleService(meta).get_subtitle()
	#tools.SUB_FILE = subfile
	#tools.VIDEO_META['SUB_FILE'] = subfile
	#tools.log(tools.VIDEO_META)
	#tools.log('SUBTITLES_____________',tools.VIDEO_META)
	#SUB_FILE = tools.VIDEO_META['SUB_FILE']
	#SUB_FILE_FORCED = tools.VIDEO_META['SUB_FILE_FORCED']
	#subs_list = []
	#if str(SUB_FILE) != '' and SUB_FILE != None:
	#	subs_list.append(SUB_FILE)
	#if str(SUB_FILE_FORCED) != '' and SUB_FILE_FORCED != None:
	#	subs_list.append(SUB_FILE_FORCED)

	#from a4kscrapers_wrapper import subs
	#subs_list = subs.get_subtitles_list(meta, PTN_download)
	#del get_subtitles_list

	RD_player_subs = xbmcaddon.Addon(addon_ID()).getSetting('RD_player_subs')
	RD_player_subs_clean = xbmcaddon.Addon(addon_ID()).getSetting('RD_player_subs_clean')
	if RD_player_subs == True or RD_player_subs == 'true':
		try: subs = importlib.import_module("subs")
		except: subs = reload_module(importlib.import_module("subs"))
		subs.META = meta
		subs_list = subs.get_subtitles_list(meta, PTN_download)
		del subs
		#exit()
		if len(subs_list) > 0:
			if RD_player_subs_clean == True or RD_player_subs_clean == 'true':
				from subcleaner import clean_file
				from pathlib import Path
				for i in subs_list:
					sub = Path(i)
					tools.log('CLEANING',sub)
					clean_file.clean_file(sub)
				tools.sub_cleaner_log_clean()
				clean_file.files_handled = []
	else:
		subs_list = []

	movie_title_clean, tmdb_id, runtime_seconds, resume_progress_seconds, movie_year, movie_vote_count, movie_vote_average, movie_title, movie_release_date, movie_poster, movie_popularity, movie_plot, movie_original_title, movie_original_language, movie_genre, movie_backdrop, imdb_id, genres, alternate_titles = meta_process(new_meta)

	movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = get_fanart_results(tvdb_id=tmdb, media_type='movie')

	con = db_connection()
	cur = con.cursor()
	movie_title2 = movie_title.replace("'","''")
	#print_log(str(movie_title2),'===>OPENINFO')
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
	try:
		file_name = PTN_download.split('/')[5]
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
	if PTN_download:
		PTN_title = meta['title']
		movie_title_clean = PTN_title
		PTN_season, PTN_episode, PTN_res, PTN_size = '', '', None, None
		PTN_link = PTN_download

	try: movie_release_date = str(movie_release_date).replace('b\'','').replace('\'','')
	except: pass
	if xbmc_plugin == 'False' and str(PTN_title) == str(movie_title_clean) and str(PTN_season) == '' and str(PTN_episode) == '':
		tools.log(movie_title,PTN_title,PTN_season,PTN_episode,PTN_res,PTN_link,PTN_size,PTN_download,dbid)

		tools.log(movie_original_title,movie_plot,movie_release_date,movie_backdrop,movie_genre,movie_release_date[0:4],movie_vote_average)

		tools.log(movielogo,hdmovielogo,movieposter,hdmovieclearart,movieart,moviedisc,moviebanner,moviethumb,moviebackground,resumeTimeInSeconds,duration,sql_result1)
	#else:
		#print_log('xbmc_plugin == True')

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
			#infolabels['Cast'] = list(zip(actor_name,actor_role,actor_thumbnail,actor_order))
			#infolabels['CastAndRole'] = list(zip(actor_name,actor_role,actor_thumbnail,actor_order))
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
		#infolabels['FileNameAndPath'] = PTN_download
		li.setProperty('FileNameAndPath', str(PTN_download))
		infolabels['path'] = PTN_download

		#li.setInfo(type='Video', infoLabels = infolabels)
		try:
			info_tag = ListItemInfoTag(li, 'video')
			info_tag.set_info(infolabels)
		except:
			li.setInfo(type='Video', infoLabels = infolabels)
		#info_tag.set_cast(infolabels['Cast'])
		#info_tag.set_cast(infolabels['CastAndRole'])
		li.setArt({ 'poster': poster, 'fanart': fanart, 'banner': banner, 'clearlogo': clearlogo, 'landscape': landscape, 'thumb': thumb})

		if len(subs_list) > 0:
			li.setSubtitles(subs_list)

		if 'test=True' in str(sys.argv):
			#print_log(sys.argv)
			print_log('EXIT')
			#print_log(infolabels)
			print_log({ 'poster': poster, 'fanart': fanart, 'banner': banner, 'clearlogo': clearlogo, 'landscape': landscape, 'thumb': thumb})
			#print_log(next_ep_play_details,'next_ep_play_details')
			print_log(str(infolabels)[:750].replace('\'','"'),'===>OPENINFO')
			xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
			#exit()
			return

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
		#exit()
		#return
