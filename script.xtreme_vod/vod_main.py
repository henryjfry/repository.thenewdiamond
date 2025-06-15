import sys
import os
import shutil
from inspect import currentframe, getframeinfo
#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

folder = str(os.path.split(str(getframeinfo(currentframe()).filename))[0])
current_directory = folder
sys.path.append(current_directory)

import os
import sys
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Subliminal'))
#sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

#from resources.lib.library import get_fanart_results_full
#from resources.lib.TheMovieDB import get_trakt_playback
#from resources.lib.TheMovieDB import extended_season_info
#from resources.lib.TheMovieDB import extended_episode_info
#from resources.lib.TheMovieDB import extended_tvshow_info
#from resources.lib.TheMovieDB import get_tvshow_ids
#from resources.lib.TheMovieDB import get_vod_alltv
 
#from resources.lib.TheMovieDB import extended_movie_info
#from resources.lib.TheMovieDB import single_movie_info
#from resources.lib.TheMovieDB import get_vod_allmovies
#from resources.lib.TheMovieDB import handle_tmdb_movies

import time, sys
from resources.lib import Utils
import tools
from get_meta import get_episode_meta
from get_meta import get_movie_meta
from urllib.parse import quote, urlencode, quote_plus, unquote, unquote_plus
import requests

import importlib
try:
	from importlib import reload as reload_module  # pylint: disable=no-name-in-module
except ImportError:
	# Invalid version of importlib
	from imp import reload as reload_module


def get_vod_data(action= None,series_ID = None, cache_days=1, folder='VOD'):
	#url = 'https://api.themoviedb.org/3/%sapi_key=%s' % (url, API_key)
	xtreme_codes_password = Utils.xtreme_codes_password
	xtreme_codes_username = Utils.xtreme_codes_username
	xtreme_codes_server_path = Utils.xtreme_codes_server_path

	actions = ['get_series','get_series_categories','get_series_info','get_vod_categories','get_vod_streams','get_live_categories','get_live_streams',]
	url = '%s/player_api.php?username=%s&password=%s&action=%s' % (xtreme_codes_server_path,xtreme_codes_username,xtreme_codes_password,action)
	if series_ID:
		action = 'get_series_info'
		url = '%s/player_api.php?username=%s&password=%s&action=%s&series=%s' % (xtreme_codes_server_path,xtreme_codes_username,xtreme_codes_password,action,str(series_ID)) 
	#xbmc.log(str(url)+'===>PHIL', level=xbmc.LOGINFO)
	return Utils.get_JSON_response(url, cache_days, folder)

def get_vod_allmovies(category = None):
	#from resources.lib.TheMovieDB import get_vod_data
	if category == None:
		movies = get_vod_data(action= 'get_vod_streams' ,cache_days=1) 
	else:
		movies = get_vod_data(action= 'get_vod_streams&category_id=%s' % (str(category)) ,cache_days=1) 
	search_str = []
	for i in movies:
		if i['name'][:7].lower() == 'movie: ':
			i['name'] = i['name'][7:]
		elif i['name'][:6].lower() == 'movie:':
			i['name'] = i['name'][6:]
		full_url = '%s%s/%s/%s/%s.%s' % (Utils.xtreme_codes_server_path,i['stream_type'],Utils.xtreme_codes_username,Utils.xtreme_codes_password,str(i['stream_id']),str(i['container_extension']))
		search_str.append({'type': 'movie','title':i['name'],'tmdb':i['tmdb'], 'full_url': full_url,'stream_id': i['stream_id'], 'stream_type': i['stream_type'],'stream_icon': i['stream_icon'], 'rating': i['rating'],'category_ids': i['category_ids']})
	#Utils.tools_log(i)
	#Utils.tools_log('get_vod_allmovies')
	return search_str

def get_vod_alltv(category = None):
	#from resources.lib.TheMovieDB import get_vod_data
	if category == None:
		movies = get_vod_data(action= 'get_series' ,cache_days=1) 
	else:
		movies = get_vod_data(action= 'get_series&category_id=%s' % (str(category)) ,cache_days=1) 
	search_str = []
	for i in movies:
		#full_url = '%s%s/%s/%s/%s.%s' % (Utils.xtreme_codes_server_path,i['stream_type'],Utils.xtreme_codes_username,Utils.xtreme_codes_password,str(i['stream_id']),str(i['container_extension']))
		full_url = ''
		#Utils.tools_log(i)
		search_str.append({'type': 'tv','title':i['name'],'tmdb':i['tmdb'], 'full_url': full_url, 'series_id': i['series_id'],'stream_type': 'tv','stream_icon': i['cover'], 'rating': i['rating'],'category_ids': i['category_ids']})
	return search_str


def run_downloader(magnet_list, download_path):
	curr_download = tools.get_download_line(magnet_list)
	from tools import log
	start_time = time.time()
	active_magnets = []
	processed_files = []
	tools.original_start_time = time.time()

	tot_bytes = 0
	with open(magnet_list, 'r') as fp:
		for line in fp:
			try: 
				curr_tot_bytes = eval(line)['tot_bytes']
				if curr_tot_bytes == 0:
					curr_tot_bytes = int(requests.get(curr_download['full_url'], stream=True).headers['Content-length'])
				tot_bytes = tot_bytes + curr_tot_bytes
			except: 
				continue
	
	original_tot_bytes = tot_bytes
	tools.original_tot_bytes = original_tot_bytes
	tools.remaining_tot_bytes = original_tot_bytes
	while time.time() < start_time + 300 and curr_download:
		tot_bytes = 0
		with open(magnet_list, 'r') as fp:
			num_lines = sum(1 for line in fp if line.rstrip())
			for line in fp:
				try: 
					curr_tot_bytes = eval(line)['tot_bytes']
					if curr_tot_bytes == 0:
						curr_tot_bytes = int(requests.get(curr_download['full_url'], stream=True).headers['Content-length'])
					tot_bytes = tot_bytes + curr_tot_bytes
				except: continue
		log('REMAINING_LINES_MAGNET_LIST =   '+str(num_lines))
		try: 
			download_type = curr_download.get('download_type', None)
			download_link =  curr_download.get('full_url', None)
		except:
			download_type, download_link = None, None
			tools.delete_download_line(magnet_list, curr_download)
		if download_type and download_link:
			if tools.tools_stop_downloader == True:
				tools.tools_stop_downloader = False
				return
			if download_type == 'movie':
				download_http_rd_link(download_path, curr_download)
				start_time = time.time()
				curr_download = tools.get_download_line(magnet_list)
			else:
				download_cached_episode(download_path, curr_download, tools.remaining_tot_bytes)
				start_time = time.time()
				curr_download = tools.get_download_line(magnet_list)
		else:
			continue
		tools.delete_download_line(magnet_list, curr_download)
		tools.log(processed_files)
		tools.log('sleep')
		time.sleep(10)
		curr_download = tools.get_download_line(magnet_list)
		sleep_count = 0
		while not curr_download:
			if sleep_count > 90:
				break
			tools.log('NO CONTENT SLEEP ' + str(100-sleep_count) + '  remaining')
			time.sleep(10)
			sleep_count = sleep_count + 10
			curr_download = tools.get_download_line(magnet_list)

def extract_values(d, key):
	values = []
	
	# Check if the current dictionary contains the key
	if isinstance(d, dict):
		for k, v in d.items():
			if k == key:
				values.append(v)
			# Recursively check nested dictionaries
			elif isinstance(v, dict):
				values.extend(extract_values(v, key))
			# If the value is a list, check each element
			elif isinstance(v, list):
				for item in v:
					values.extend(extract_values(item, key))
	
	return values

def download_http_rd_link(download_path, curr_download):
	unrestrict_link = curr_download
	download_folder = download_path

	log(unrestrict_link, download_path)
	#download_link = rd_api.resolve_hoster(unrestrict_link)
	#download_id = rd_api.UNRESTRICT_FILE_ID
	#log(download_link, download_id)
	file_name = os.path.basename(download_link)
	file_name = unquote(file_name)
	download_path2 = os.path.join(download_path, file_name)

	if not os.path.exists(download_folder):
		os.makedirs(download_folder)
	before_download = tools.remaining_tot_bytes
	try: tools.download_progressbar(rd_api, download_link, download_path2)
	except: tools.tools_stop_downloader = True
	#rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE
	if tools.remaining_tot_bytes == before_download:
		tools.remaining_tot_bytes = tools.remaining_tot_bytes - tools.UNRESTRICT_FILE_SIZE

def download_cached_episode(download_path, curr_download, remaining_tot_bytes):
	tools.log('download_cached_episode')
	#tools.log(curr_download)
	from tools import log
	#from source_tools import get_guess

	folder = curr_download['show_title'].replace(':','')
	download_folder = os.path.join(download_path, folder)

	simple_info = tools._build_simple_show_info(curr_download['info'])
	info = curr_download['info']

	info['aliases'] = info['show_aliases']
	info['tvshowtitle'] = curr_download['show_title']
	info['aliases'].append(info['tvshowtitle'])

	curr_download['file_name'] = unquote(curr_download['file_name'])
	curr_download['filename'] = unquote(curr_download['filename'])
	curr_download['title'] = ''
	curr_download['info']['title'] = ''
	curr_download['info']['info']['title'] = ''
	#curr_download['info']['season_number'] = curr_download['season']
	#curr_download['info']['episode'] = curr_download['episode']
	#curr_download['info']['season'] = curr_download['season']
	#curr_download['info']['title'] = ''
	#curr_download['info']['episode_air_date'] = ''
	tools.log(curr_download)

	show_folder = os.path.join(download_path, str(curr_download['show_title']) + ' (' + str(curr_download['info']['year'] + ')')).replace(':','')
	poster_path = os.path.join(show_folder, 'poster' + os.path.splitext(curr_download['poster'])[1])

	if not os.path.exists(show_folder):
		os.makedirs(show_folder)
	if not os.path.exists(poster_path):
		tools.download_progressbar(curr_download['poster'], poster_path, 0, 0)

	season_folder = os.path.join(show_folder, str(curr_download['show_title']) + ' - Season ' + str(curr_download['season']).zfill(2)).replace(':','')
	if not os.path.exists(season_folder):
		os.makedirs(season_folder)

	download_folder = season_folder
	download_link = curr_download['full_url']
	download_path = os.path.join(download_folder, curr_download['filename']).replace(':','')
	log(download_link, download_path)
	before_download = tools.remaining_tot_bytes

	tools.UNRESTRICT_FILE_SIZE = curr_download['tot_bytes']
	if curr_download['tot_bytes'] == 0:
		tools.UNRESTRICT_FILE_SIZE  = int(requests.get(curr_download['full_url'], stream=True).headers['Content-length'])

	#file_path, tools.remaining_tot_bytes =  tools.download_progressbar(download_link, download_path, remaining_tot_bytes, tools.UNRESTRICT_FILE_SIZE)

	try: file_path, tools.remaining_tot_bytes =  tools.download_progressbar(download_link, download_path, remaining_tot_bytes, tools.UNRESTRICT_FILE_SIZE)
	except: tools.tools_stop_downloader = True

	if tools.remaining_tot_bytes == before_download:
		tools.remaining_tot_bytes = tools.remaining_tot_bytes - tools.UNRESTRICT_FILE_SIZE

	if tools.tools_stop_downloader == True:
		return

	download_folder1 = os.path.dirname(download_path)
	sub_path1 = os.path.join(download_folder1,unquote(str(os.path.splitext(os.path.basename(download_path))[0] + '.srt'))).replace(':','')
	sub_path2 = os.path.join(download_folder1,unquote(str(os.path.splitext(os.path.basename(download_path))[0] + '.eng.FORCED.srt'))).replace(':','')
	sub_path3 = os.path.join(download_folder1,unquote(str(os.path.splitext(os.path.basename(download_path))[0] + '.eng.srt'))).replace(':','')

	tools.log(sub_path1)
	tools.log(sub_path2)
	tools.log(sub_path3)
	os.environ['sub_logs'] = 'False'
	exists_flag = False
	if os.path.exists(sub_path1) or os.path.exists(sub_path2) or os.path.exists(sub_path3):
		exists_flag = True

	if exists_flag == False:
		#try: subs = importlib.import_module("subs")
		#except: subs = reload_module(importlib.import_module("subs"))
		#subs.META = curr_download
		#input_guess = get_guess(curr_download['filename'])
		#title = input_guess.get('episode_title','')
		#if title == None or title == '':
		#	import get_meta
		#	meta = get_meta.get_episode_meta(season=curr_download['season'], episode=curr_download['episode'],tmdb=curr_download['tmdb'], show_name=curr_download['show_title'], year=curr_download['info']['year'], interactive=False)
		#	title = meta['episode_meta']['title']
		#info['title'] = title
		#info['info']['title'] = title

		#subs_list = subs.get_subtitles_list(info, download_path)
		#file_path = "/home/osmc/Movies/Star Trek Deep Space Nine (1993)/Star Trek Deep Space Nine - Season 01/Star Trek Deep Space Nine - S01E01 - Emissary (1).mkv"
		import sub_lim
		subs_out_ENG, subs_out_FORCED = sub_lim.get_subs_file(cache_directory=tools.ADDON_USERDATA_PATH, video_path = download_path, same_folder=False)
		subs_list = [subs_out_ENG]
		if subs_out_FORCED:
			subs_list.append(subs_out_FORCED)
		#if len(subs_list) == 0:
		#	subs_list = subs.get_subtitles_list(info, download_path)
		#del subs

		if len(subs_list) > 0:
			from subcleaner import clean_file
			from pathlib import Path
			for i in subs_list:
				sub = Path(i)
				try: clean_file.clean_file(sub)
				except: tools.log('EXCEPTION', i)
			tools.sub_cleaner_log_clean()
			clean_file.files_handled = []

		for i in subs_list:
			#os.rename(i, os.path.join(download_folder, os.path.basename(i)))
			#tools.log(i, os.path.join(download_folder, os.path.basename(i)))
			out_path = os.path.join(download_folder1, os.path.basename(i))
			if os.path.splitext(out_path)[1].lower() == '.eng':
				out_path = out_path + '.srt'

			shutil.copyfile(i, out_path)
			tools.log(out_path)

	curr_percent_val = tools.curr_percent(tools.remaining_tot_bytes, tools.original_tot_bytes, tools.original_start_time)
	tools.log('\n\n'+str(curr_percent_val)+'% total remaining on file')
	#try: 
	#	curr_percent_val = os.environ['DOWNLOAD_CURR_PERCENT']
	#	tools.log('\n\n'+str(curr_percent_val)+'% total remaining on file')
	#except:
	#	pass


def run_tv_search():
	#print(get_vod_alltv())
	import get_meta

	try: 
		tv_show_title = input('Enter TV Show Title (MAGNET???):  ')
		#season_number = input('Enter Season Number:  ')
		#episode_number = input('Enter Episode Number:  ')
		season_number = 1
		episode_number = 1
	except:
		tools.log('EXIT')
		return
	meta = get_meta.get_episode_meta(season=season_number, episode=episode_number,tmdb=None, show_name=tv_show_title, year=None, interactive=True)
	info = meta['episode_meta']
	tools.log(info)
	search_str = get_vod_alltv()
	tmdb = info['tmdb_id']
	info['tvdb_id'] = info['info']['tvdb_id']
	for i in search_str:
		if str(i['tmdb']) == str(tmdb):
			series_id = i['series_id']
			poster = i['stream_icon']
			break
	movies = get_vod_data(action= 'get_series_info&series_id=%s' % (str(series_id)) ,cache_days=1)

	files_dict = {}
	files_dict['NUMBER_EPISODES'] = 0
	files_dict['NUMBER_SEASONS'] = 0
	files_dict['EPISODE_AVERAGE'] = 0
	files_dict['seasons'] = {}
	abs_num = 0
	hevc_flag = False
	for i in movies['episodes']:
		for x in i:
			files_dict['seasons'][x] = {}
			files_dict['seasons'][x]['SEASON_AVERAGE'] = 0
			files_dict['seasons'][x]['SEASON_EPISODES'] = 0
			files_dict['NUMBER_SEASONS'] = files_dict['NUMBER_SEASONS']+1
			for y in movies['episodes'][x]:
				abs_num = abs_num + 1
				curr_info = {'absoluteNumber': abs_num,'download_type': 'episode','episode': y['episode_num'],'episode_air_date': '','episode_count': '','imdb_id': info['imdb_id'],'imdbnumber': info['imdb_id'],'info': {'episode': y['episode_num'],'episode_air_date': '','imdb_id': info['imdb_id'],'imdbnumber': info['imdb_id'],'mediatype': 'episode','season': str(x),'season_number': x,'show_aliases': info['show_aliases'],'show_title': info['show_title'],'title': '','tmdb_id': info['tmdb_id'],'tmdb_show_id': info['tmdb_id'],'tvdb_id': info['tvdb_id'],'tvdb_show_id': info['tvdb_id'],'tvshow': info['show_title'],'tvshow.imdb_id':info['imdb_id'],'tvshow.tmdb_id': info['tmdb_id'],'tvshow.tvdb_id': info['tvdb_id'],'tvshow.year': info['year'],'tvshowtitle': info['show_title'],'year': info['year']},'is_airing': info['is_airing'],'is_movie': False,'is_tvshow': True,'media_type': 'episode','mediatype': 'episode','season': str(x),'season_count': info['season_count'],'season_number': x,'show_aliases': info['show_aliases'],'show_episode_count': info['show_episode_count'],'show_title': info['show_title'],'title': '','tmdb_id': info['tmdb_id'],'tvshow': info['show_title'],'tvshow_year': info['year'],'year': info['year']}
				files_dict['NUMBER_EPISODES'] = files_dict['NUMBER_EPISODES']+1
				files_dict['seasons'][x][y['episode_num']] = {}
				file_name = y['title'] +'.'+ y['container_extension']
				files_dict['seasons'][x][y['episode_num']]['file_name'] = file_name
				files_dict['seasons'][x][y['episode_num']]['filename'] = file_name
				files_dict['seasons'][x][y['episode_num']]['filename_without_ext'] = y['title']
				files_dict['seasons'][x][y['episode_num']]['release_title'] = y['title']
				files_dict['seasons'][x][y['episode_num']]['CURR_LABEL'] = y['title']
				full_url = '%s%s/%s/%s/%s.%s' % (Utils.xtreme_codes_server_path,'series',Utils.xtreme_codes_username,Utils.xtreme_codes_password,str(y['id']),str(y['container_extension']))
				files_dict['seasons'][x][y['episode_num']]['full_url'] = full_url
				files_dict['seasons'][x][y['episode_num']]['url'] = full_url
				#Utils.tools_log(full_url)
				NUMBER_OF_BYTES_list = extract_values(y,'NUMBER_OF_BYTES-eng')
				NUMBER_OF_BYTES = 0
				for i in NUMBER_OF_BYTES_list:
					NUMBER_OF_BYTES = int(i) + NUMBER_OF_BYTES
				if NUMBER_OF_BYTES == 0:
					try: NUMBER_OF_BYTES = int(y['info']['video']['tags']['NUMBER_OF_BYTES'])
					except: NUMBER_OF_BYTES = 0


				size = round(NUMBER_OF_BYTES/1024/1024,2)
				files_dict['seasons'][x]['SEASON_AVERAGE'] = files_dict['seasons'][x]['SEASON_AVERAGE'] + size
				files_dict['EPISODE_AVERAGE'] = files_dict['EPISODE_AVERAGE'] + size
				files_dict['seasons'][x]['SEASON_EPISODES'] = files_dict['seasons'][x]['SEASON_EPISODES'] + 1
				files_dict['seasons'][x][y['episode_num']]['size'] = size
				files_dict['seasons'][x][y['episode_num']]['filesize'] = size
				files_dict['seasons'][x][y['episode_num']]['filehash'] = ''
				files_dict['seasons'][x][y['episode_num']]['series_id'] = series_id
				files_dict['seasons'][x][y['episode_num']]['poster'] = poster
				files_dict['seasons'][x][y['episode_num']]['tmdb'] = tmdb
				files_dict['seasons'][x][y['episode_num']]['show_title'] = info['show_title']
				files_dict['seasons'][x][y['episode_num']]['codec_name'] = y['info']['video']['codec_name']
				files_dict['seasons'][x][y['episode_num']]['width'] = y['info']['video']['width']
				files_dict['seasons'][x][y['episode_num']]['height'] = y['info']['video']['height']
				codec_name = y['info']['video']['codec_name']
				width = y['info']['video']['width']
				height = y['info']['video']['height']
				size = files_dict['seasons'][x][y['episode_num']]['size']
				if 'hevc' in str(y['info']['video']['codec_name']).lower():
					hevc_flag = True
				files_dict['seasons'][x][y['episode_num']]['season'] = x
				files_dict['seasons'][x][y['episode_num']]['episode'] = y['episode_num']
				files_dict['seasons'][x][y['episode_num']]['download_type'] = 'episode'
				files_dict['seasons'][x][y['episode_num']]['tot_bytes'] = NUMBER_OF_BYTES
				files_dict['seasons'][x][y['episode_num']]['info'] = curr_info

			files_dict['seasons'][x]['SEASON_AVERAGE'] = files_dict['seasons'][x]['SEASON_AVERAGE']/ files_dict['seasons'][x]['SEASON_EPISODES']
	files_dict['EPISODE_AVERAGE'] = files_dict['EPISODE_AVERAGE']/files_dict['NUMBER_EPISODES']

	#tools.log(files_dict)
	#tools.log('')
	#tools.log('')
	#tools.log(str({'codec_name': codec_name,'width': width,'height': height}))
	#tools.log('')
	#tools.log('')
	torrent_choices = {
	'Download Whole Show': 1,
	'Download Season': 2,
	'Download Episode ': 3
	}
	result = tools.selectFromDict(torrent_choices, 'Torrent' + str({'codec_name': codec_name,'width': width,'height': height, 'EPISODE_AVERAGE': round(size,2)}))
	if hevc_flag:
		hevc_check = input('HEVC_FLAG==TRUE:  ADD DOWNLOADS Y/N?  ')
		if hevc_check.lower() != 'y':
			tools.log('EXIT')
			return
	if not result:
		tools.log('EXIT')
		return
	if result == 1:
		tools.log('EPISODE_AVERAGE:  ' + str(files_dict['EPISODE_AVERAGE']))
		season_number = 0
		episode_number = 0
	if result == 2:
		tools.log('NUMBER_SEASONS:  ' + str(files_dict['NUMBER_SEASONS']))
		season_number = input('Enter Season Number:  ')
		tools.log('NUMBER_EPISODES_SEASON:  ' + str(files_dict['seasons'][season_number]['SEASON_EPISODES']))
		tools.log('SEASON_AVERAGE:  ' + str(files_dict['seasons'][season_number]['SEASON_AVERAGE']))
		episode_number = 0
	if result == 3:
		tools.log('NUMBER_SEASONS:  ' + str(files_dict['NUMBER_SEASONS']))
		season_number = input('Enter Season Number:  ')
		tools.log('NUMBER_EPISODES_SEASON:  ' + str(files_dict['seasons'][season_number]['SEASON_EPISODES']))
		tools.log('SEASON_AVERAGE:  ' + str(files_dict['seasons'][season_number]['SEASON_AVERAGE']))
		episode_number = input('Enter Episode Number:  ')

	magnet_list = tools.get_setting('magnet_list')
	file1 = open(magnet_list, "a") 
	for i in files_dict['seasons']:
		for j in i:
			SEASON_EPISODES = files_dict['seasons'][j]['SEASON_EPISODES']
			for x in range(1, SEASON_EPISODES+1):
				if season_number == 0 or j == season_number:
					if episode_number == 0 or x == int(episode_number):
						try: files_dict['seasons'][j][x]['tot_bytes']
						except: continue
						if files_dict['seasons'][j][x]['tot_bytes'] == 0:
							files_dict['seasons'][j][x]['tot_bytes'] = int(requests.get(full_url, stream=True).headers['Content-length'])
							size = round(files_dict['seasons'][j][x]['tot_bytes']/1024/1024,2)
							files_dict['seasons'][j][x]['size'] = size
							files_dict['seasons'][j][x]['filesize'] = size
						tools.log(files_dict['seasons'][j][x])

						#os.environ['sub_logs'] = str('False')
						#try: subs = importlib.import_module("subs")
						#except: subs = reload_module(importlib.import_module("subs"))
						#subs.META = files_dict['seasons'][j][x]
						#subs_list = subs.get_subtitles_list(info, '/home/osmc/.kodi/userdata/addon_data/script.extendedinfo/temp/The.X-Files.S01E13.Beyond.the.Sea.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-NOGRP.eng')
						#del subs
						#os.environ['sub_logs'] = str('True')
						#return

						file1.write(str(files_dict['seasons'][j][x]))
						file1.write("\n")
	file1.close()


program_choices = {
	'Search Download (episode) 				"main.py -search \'foundation\' -episode 1 -season 2 -interactive False"': 1 ,
	'Search Download (movie)				"main.py -search \'batman begins\' -year 2005"': 2,
	'Start downloader service (if not running)		"main.py -downloader -start"': 3,
	'manage downloader list				"main.py -downloader -status"': 4,
	'Get Subtitles for File			""': 15
}

program_choices2 = {
	'Search Subtitles (episode) 				" "': 1 ,
	'Search Subtitles (movie)				" "': 2,
}


#print(current_directory)

def downloader_daemon():
	import daemon
	magnet_list = tools.get_setting('magnet_list')
	download_path = tools.get_setting('download_path')
	with daemon.DaemonContext():
		run_downloader(magnet_list, download_path)

def copy_and_replace(source_path, destination_path):
	if os.path.exists(destination_path):
		if source_path == destination_path:
			return
		os.remove(destination_path)
	shutil.copy2(source_path, destination_path)

def main():
	#program_choices = tools.program_choices

	try: result = tools.selectFromDict(program_choices, 'CHOOSE')
	except KeyboardInterrupt: 
		print('\nEXIT')
		return

	if result == 1:
		run_tv_search()
		
	if result == 3:
		magnet_list = tools.get_setting('magnet_list')
		download_path = tools.get_setting('download_path')
		run_downloader(magnet_list, download_path)
 
if __name__ == "__main__":
	print(sys.argv)
	if 'downloader' in str(sys.argv):
		downloader_daemon()
	else:
		main()
