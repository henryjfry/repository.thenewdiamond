# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

#from __future__ import absolute_import, division, unicode_literals

import copy
import importlib
import os
import random
import re
import sys
import time
from collections import OrderedDict, Counter

#from database.torrentCache import TorrentCache
try:
	from thread_pool import ThreadPool
	import real_debrid
	import get_meta
	import source_tools
	import tools, distance
	from tools import log
except:
	from a4kscrapers_wrapper.thread_pool import ThreadPool
	from a4kscrapers_wrapper import real_debrid
	from a4kscrapers_wrapper import get_meta
	from a4kscrapers_wrapper import source_tools
	from a4kscrapers_wrapper import tools, distance
	from a4kscrapers_wrapper.tools import log

import urllib
from urllib.parse import unquote

#tools.get_pid()
import shutil

import inspect

from inspect import currentframe, getframeinfo
#log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

##SUPPRESS MESSAGES
os.environ['A4KSCRAPERS_TEST_TOTAL'] = '1'


"""
Handling of scraping and cache checking for sources
"""
"""
TEST
import getSources, real_debrid, tools, source_tools, get_meta
from getSources import Sources
rd_api = real_debrid.RealDebrid()
meta = get_meta.get_episode_meta(season=1,episode=1,show_name='Deep Space Nine')
info = meta['episode_meta']
info = meta['tmdb_seasons']['episodes'][11]
uncached, sources_list, item_information= Sources(info).get_sources()
torrent = getSources.choose_torrent(sources_list)
sources_list = tools.SourceSorter(info).sort_sources(sources_list)

response = rd_api.add_magnet(torrent['magnet'])
torr_id = response['id']
response = rd_api.torrent_select_all(torr_id)
torr_info = rd_api.torrent_info(torr_id)
torr_info = rd_api.torrent_info_files(torr_info)
sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
simple_info = tools._build_simple_show_info(info)
for i in sorted_torr_info:
	test = source_tools.run_show_filters(simple_info, release_title = i['pack_path'])
	if ': True' in str(test):
#		log(test)

###
import getSources, get_meta
meta = get_meta.get_episode_meta(season=1,episode=1,show_name='The Flash', year=2014)
meta = get_meta.get_episode_meta(season=1,episode=1,show_name='DeepSpace Nine')
info = meta['episode_meta']
from getSources import Sources
uncached, sources_list, item_information= Sources(info).get_sources()

for i in reversed(sorted(uncached, key=lambda x: x['seeds'])):
	i


torrent = getSources.choose_torrent(sources_list)

import real_debrid
rd_api = real_debrid.RealDebrid()
response = rd_api.add_magnet(torrent['magnet'])
torr_id = response['id']
#response = rd_api.torrent_select(torr_id,'all')
#torr_info = rd_api.torrent_info(torr_id)

#download_folder = tools.DOWNLOAD_FOLDER
#release_name = torr_info['filename']

#files = []
#for i in torr_info['files']:
#	if i['selected'] == 1:
#		files.append(i)

#files_links = []
#for idx,i in enumerate(files):
#	file_path = os.path.join(download_folder,release_name + i['path'])
#	download_dir = os.path.join(download_folder,release_name)
#	files_links.append({'unrestrict_link': torr_info['links'][idx], 'pack_file_id': i['id'], 'pack_path': i['path'], 'download_path': file_path, 'download_dir': download_dir})

response = rd_api.torrent_select_all(torr_id)
torr_info = rd_api.torrent_info(torr_id)
torr_info = rd_api.torrent_info_files(torr_info)
sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])


test = rd_api.resolve_hoster('https://real-debrid.com/d/GYLXXXXXXX')
download_id = test['id']

response = rd_api.delete_download(test['id'])
download_id = test['download'].split('/')[4]


response = rd_api.delete_torrent(torr_id)
####

import getSources, real_debrid, tools, source_tools, get_meta
meta = get_meta.get_episode_meta(season=1,episode=1,show_name='The Flash', year=2014)
info = meta['episode_meta']
from getSources import Sources
uncached, sources_list, item_information= Sources(info).get_sources()

torrent = getSources.choose_torrent(sources_list)

rd_api = real_debrid.RealDebrid()
response = rd_api.add_magnet(torrent['magnet'])
torr_id = response['id']

response = rd_api.torrent_select_all(torr_id)
torr_info = rd_api.torrent_info(torr_id)
torr_info = rd_api.torrent_info_files(torr_info)

####

import getSources, source_tools, tools, get_meta
meta = get_meta.get_episode_meta(season=1,episode=1,show_name='The Flash', year=2014)

meta['tmdb_seasons']['episodes'][0]
meta['tvmaze_seasons']['episodes'][0]

#from getSources import Sources
#uncached, sources_list, item_information= Sources(meta['episode_meta']).get_sources()
#torrent = getSources.choose_torrent(sources_list)

#getSources.get_subtitles(meta['tmdb_seasons']['episodes'][0], '')

simple_info = tools._build_simple_show_info(meta['tmdb_seasons']['episodes'][0])

clean_t = 'The.Flash.S01E01.City.of.Heroes.1080p.10.bit.BluRay.5.1.x265.HEVC-MZABI.mkv'
pack_t = 'The.Flash.Complete.1080p.10bit.BluRay.5.1.x265.HEVC-MZABI'
results = source_tools.run_show_filters(simple_info, pack_title=pack_t, release_title=clean_t) 


meta = get_meta.get_episode_meta(season=1,episode=12,show_name='Babylon 5', year=1994)
simple_info = tools._build_simple_show_info(meta['tmdb_seasons']['episodes'][11])

for i in range(1,99):
	result = rd_api.list_downloads_page(int(i))
	if '<Response [204]>' == result:
		break
	for x in result:
		test = source_tools.run_show_filters(simple_info, release_title = x['filename'])
		if ': True' in str(test):
#			log(test)
			break
	if ': True' in str(test):
		break

for i in range(1,99):
	result = rd_api.list_torrents_page(int(i))
	if '<Response [204]>' == result:
		break
	for x in result:
		test = source_tools.run_show_filters(simple_info, pack_title=x['filename'])
		if ': True' in str(test):
#			log(test)
			break
	if ': True' in str(test):
		break
		

##match multi episodes to season pack
meta = get_meta.get_episode_meta(season=6,episode=1,show_name='Deep Space Nine')
import time
start_time = time.time()
simple_info_list = []
for idx, x in enumerate(meta['tmdb_seasons']['episodes']):
	simple_info = tools._build_simple_show_info(x)
	simple_info_list.append(simple_info)

#simple_info1 = tools._build_simple_show_info(meta['tmdb_seasons']['episodes'][0])
#simple_info2 = tools._build_simple_show_info(meta['tmdb_seasons']['episodes'][-1])
simple_info1 = simple_info_list[0]
simple_info2 = simple_info_list[-1]
start_index = -1
end_index = -1
for idx, i in enumerate(sorted_torr_info):
	test1 = source_tools.run_show_filters(simple_info1, release_title = i['pack_path'])
	test2 = source_tools.run_show_filters(simple_info2, release_title = i['pack_path'])
	if ': True' in str(test1) or ': True' in str(test2):
		if start_index == -1:
			start_index = idx
		if start_index != -1:
			end_index = idx

output_list = []
output_ep = {}
missing_list = []
pop_ep = 0
for iidx, i in enumerate(sorted_torr_info):
	if iidx < start_index or iidx > end_index:
		continue
	for idx, x in enumerate(meta['tmdb_seasons']['episodes']):
		if idx < pop_ep:
			continue
		#simple_info = tools._build_simple_show_info(x)
		simple_info = simple_info_list[idx]
		test = source_tools.run_show_filters(simple_info, release_title = i['pack_path'])
		if ': True' in str(test):
			output = str('ep='+str(int(idx)+1)+'='+i['pack_path'])
			if str('ep='+str(int(idx)+1)+'=') in str(output_list):
				if not i['pack_path'] in str(output_list) and not i['pack_path'] in str(missing_list):
					missing_list.append(i['pack_path'])
				continue
			output_list.append(output)
			output_ep[int(idx)+1] = i['pack_path']
			pop_ep = idx

for i in missing_list:
	if i in str(output_ep):
		continue
	if not i in str(output_ep):
		for j in sorted_torr_info:
			if j['pack_path'] == i:
				for idx, x in enumerate(meta['tmdb_seasons']['episodes']):
					#simple_info = tools._build_simple_show_info(x)
					simple_info = simple_info_list[idx]
					test = source_tools.run_show_filters(simple_info, release_title = j['pack_path'])


for idx, i in enumerate(meta['tmdb_seasons']['episodes']):
	test = output_ep.get(idx+1)
	if test:
#		tools.log(idx+1,test)

#tools.log(time.time()-start_time)
#tools.log(time.time()-start_time)
##match multi episodes to season pack

###
import getSources
getSources.setup_userdata_folder()
getSources.setup_providers('https://bit.ly/a4kScrapers')

getSources.enable_disable_providers()
getSources.rd_auth()


import getSources, get_meta
meta = get_meta.get_movie_meta(movie_name='Point Break',year=1991)
info = meta

from getSources import Sources
uncached, sources_list, item_information= Sources(info).get_sources()

##
movie_meta = meta
simple_info = tools._build_simple_movie_info(movie_meta)
test = source_tools.filter_movie_title(release_title, clean_release_title, movie_title, simple_info)

##FILEPATH!!
getSources.get_subtitles(info , '')

sources_dict = {}
for idx, i in enumerate(sources_list):
	source_name = '%s SIZE=%s SEEDS=%s PACK=%s' % (i['release_title'], i['size'], i['seeds'], i['pack_size'])
#	log(i, '\n')
	sources_dict[source_name] = str(idx)

tools.selectFromDict(sources_dict, 'Torrent')

"""


try:
	from importlib import reload as reload_module  # pylint: disable=no-name-in-module
except ImportError:
	# Invalid version of importlib
	from imp import reload as reload_module



def patch_ak4_requests():
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


	file_path = os.path.join(os.path.join(tools.ADDON_USERDATA_PATH, 'providerModules', 'a4kScrapers') , 'request.py')
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
		file1 = open(file_path, 'w')
		file1.writelines(new_file)
		file1.close()


def run_downloader(magnet_list, download_path):
	rd_api = real_debrid.RealDebrid()
	curr_download = tools.get_download_line(magnet_list)
	start_time = time.time()
	active_magnets = []
	processed_files = []
	
	while time.time() < start_time + 300 and curr_download:
		with open(magnet_list, 'r') as fp:
			num_lines = sum(1 for line in fp if line.rstrip())
		log('REMAINING_LINES_MAGNET_LIST =   '+str(num_lines))

		try: 
			download_type = curr_download.get('download_type', None)
			magnet =  curr_download.get('magnet', None)
		except:
			download_type, magnet = None, None

		if download_type and magnet:
			#filename = curr_download['filename']
			#filename_without_ext = curr_download['filename_without_ext']
			#url = curr_download['url']
			
			#release_title = curr_download['release_title']
			#CURR_LABEL = curr_download['CURR_LABEL']
			#package = curr_download['package']
			#file_name = curr_download['file_name']
			#log(download_type, filename, filename_without_ext, url, magnet, release_title, CURR_LABEL, package, file_name)

			response = rd_api.add_magnet(magnet)
			torr_id = response['id']
			response = rd_api.torrent_select_all(torr_id)
			torr_info = rd_api.torrent_info(torr_id)

			if magnet in active_magnets:
				download_type = 'uncached'
			if download_type == 'pack':
				#response = rd_api.add_magnet(magnet)
				#torr_id = response['id']
				#response = rd_api.torrent_select_all(torr_id)
				#torr_info = rd_api.torrent_info(torr_id)
				if torr_info['status'] == 'downloaded':
					download_cached_magnet_pack(rd_api, download_path, curr_download, torr_id, torr_info)
					
					start_time = time.time()
					curr_download = tools.get_download_line(magnet_list)
					tools.delete_download_line(magnet_list, curr_download)
					curr_download = tools.get_download_line(magnet_list)
			if download_type == 'movie':
				#response = rd_api.add_magnet(magnet)
				#torr_id = response['id']
				#response = rd_api.torrent_select_all(torr_id)
				#torr_info = rd_api.torrent_info(torr_id)
				if torr_info['status'] == 'downloaded':
					download_cached_movie(rd_api, download_path, curr_download, torr_id, torr_info)
					
					start_time = time.time()
					curr_download = tools.get_download_line(magnet_list)
					tools.delete_download_line(magnet_list, curr_download)
					curr_download = tools.get_download_line(magnet_list)
			if download_type == 'episode':
				#response = rd_api.add_magnet(magnet)
				#torr_id = response['id']
				#response = rd_api.torrent_select_all(torr_id)
				#torr_info = rd_api.torrent_info(torr_id)
				if torr_info['status'] == 'downloaded':
					download_cached_episode(rd_api, download_path, curr_download, torr_id, torr_info)

					start_time = time.time()
					curr_download = tools.get_download_line(magnet_list)
					tools.delete_download_line(magnet_list, curr_download)
					curr_download = tools.get_download_line(magnet_list)
			if download_type == 'uncached':
				processed_files = download_uncached_magnet(rd_api, download_path, curr_download, torr_id, torr_info, processed_files, magnet_list, True)
				start_time = time.time()
				curr_download = tools.get_download_line(magnet_list)
			elif torr_info['status'] != 'downloaded':
				active_magnets.append(magnet)
				processed_files = download_uncached_magnet(rd_api, download_path, curr_download, torr_id, torr_info, processed_files, magnet_list, False)
				start_time = time.time()
				curr_download = tools.get_download_line(magnet_list)
		else:
			if str(curr_download).strip()[:4] == 'http':
				download_http_rd_link(rd_api, download_path, curr_download)
				tools.delete_download_line(magnet_list, curr_download)
				rd_api.delete_download(rd_api.UNRESTRICT_FILE_ID)
				start_time = time.time()
				curr_download = tools.get_download_line(magnet_list)
			elif str(curr_download).strip()[:6] == 'magnet':
				response = rd_api.add_magnet(str(curr_download).strip())
				torr_id = response['id']
				response = rd_api.torrent_select_all(torr_id)
				torr_info = rd_api.torrent_info(torr_id)
				if curr_download in active_magnets:
					processed_files = download_uncached_magnet(rd_api, download_path, curr_download, torr_id, torr_info, processed_files, magnet_list, True)
					start_time = time.time()
					curr_download = tools.get_download_line(magnet_list)
				elif torr_info['status'] != 'downloaded':
					active_magnets.append(curr_download)
					processed_files = download_uncached_magnet(rd_api, download_path, curr_download, torr_id, torr_info, processed_files, magnet_list, False)
					start_time = time.time()
					curr_download = tools.get_download_line(magnet_list)
				elif torr_info['status'] == 'downloaded':
					active_magnets.append(curr_download)
					processed_files = download_uncached_magnet(rd_api, download_path, curr_download, torr_id, torr_info, processed_files, magnet_list, True)
					start_time = time.time()
					curr_download = tools.get_download_line(magnet_list)
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
			

def run_tv_search():
	try: 
		tv_show_title = input('Enter TV Show Title:  ')
		season_number = input('Enter Season Number:  ')
		episode_number = input('Enter Episode Number:  ')
	except:
		tools.log('EXIT')
		return
	meta = get_meta.get_episode_meta(season=season_number, episode=episode_number,tmdb=None, show_name=tv_show_title, year=None, interactive=True)
	info = meta['episode_meta']
	uncached, sources_list, item_information= Sources(info).get_sources()
	torrent_choices = tools.torrent_choices
	magnet_list = tools.get_setting('magnet_list')
	download_path = tools.get_setting('download_path')
	torrent_choices_test = []
	if len(sources_list) == 0:
		tools.log('UNCACHED_NO_CACHED TORENTS FOUND!!')
		sources_list = uncached
		for i in torrent_choices:
			if not 'uncached' in str(i).lower():
				torrent_choices_test.append(i)
	else:
		for i in torrent_choices:
			if 'uncached' in str(i).lower():
				torrent_choices_test.append(i)
	for i in torrent_choices_test:
		torrent_choices.pop(i)
	torrent = choose_torrent(sources_list)
	if not torrent:
		tools.log('EXIT')
		return
	result = tools.selectFromDict(torrent_choices, 'Torrent')
	if not result:
		tools.log('EXIT')
		return
	rd_api = real_debrid.RealDebrid()

	if result == 1 or result == 8:#'Add to RD Cache (whole pack)': 1,#'(Uncached) Add to RD (whole pack) ': 8,
		tools.log(torrent)
		response = rd_api.add_magnet(torrent['magnet'])
		tools.log(response)
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)
		tools.log(torr_info)
	elif result == 2:#'Add to RD Cache + Unrestrict (whole pack)': 2,
		tools.log(torrent)
		response = rd_api.add_magnet(torrent['magnet'])
		tools.log(response)
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)
		tools.log(torr_info)
		for i in torr_info['links']:
			unrestrict_link = i
			download_link = rd_api.resolve_hoster(unrestrict_link)
			download_id = rd_api.UNRESTRICT_FILE_ID
			log(download_link, download_id)
	elif result == 3:#'Unrestrict specific files': 3,
		tools.log(torrent)
		response = rd_api.add_magnet(torrent['magnet'])
		tools.log(response)
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)
		tools.log(torr_info)
		#sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
		for i in torr_info['links']:
			unrestrict_link = i
			result = input('Unrestrict %s:  ' % i['pack_path'])
			if result and result.strip() != '':
				download_link = rd_api.resolve_hoster(unrestrict_link)
				download_id = rd_api.UNRESTRICT_FILE_ID
				log(download_link, download_id)
	elif result == 9:#'(Uncached) Add to RD (individual files) ': 9
		tools.log(torrent)
		response = rd_api.add_magnet(torrent['magnet'])
		tools.log(response)
		torr_id = response['id']
		torr_info = rd_api.torrent_info(torr_id)
		tools.log(torr_info)
		#sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
		for i in torr_info['files']:
			unrestrict_link = i
			result = input('Unrestrict %s:  ' % i['file'])
			if result and result.strip() != '':
				response = rd_api.torrent_select(torr_id, i['id'])
	elif result == 4:#'Add to downloader list (whole pack)': 4,
		tools.log(torrent)

		meta['download_type'] = 'pack'
		meta['download_type'] = 'movie'

		meta['magnet'] = torrent['magnet']

	elif result == 7:#'Add to downloader list (specific files)': 5,
		meta['download_type'] = 'episode'
		meta['magnet'] = torrent['magnet']
		tools.log(torrent)
	elif result == 6:#'Add to downloader list (whole pack + subtitles)': 6,
		tools.log(torrent)
		meta['download_type'] = 'pack'
		meta['download_type'] = 'movie'

		meta['magnet'] = torrent['magnet']
	elif result == 7:#'Add to downloader list (specific files + subtitles)': 7,
		meta['download_type'] = 'episode'
		meta['magnet'] = torrent['magnet']
		tools.log(torrent)

	return

def run_movie_search():
	try: 
		movie_title = input('Enter Movie Title:  ')
	except:
		tools.log('EXIT')
		return

	meta = get_meta.get_movie_meta(movie_name=movie_title,year=None, interactive=True)
	info = meta
	uncached, sources_list, item_information= Sources(info).get_sources()
	torrent_choices = tools.torrent_choices
	magnet_list = tools.get_setting('magnet_list')
	download_path = tools.get_setting('download_path')
	
	torrent_choices_test = []
	for i in torrent_choices:
		if 'individual' in str(i).lower() or 'file' in str(i).lower():
			torrent_choices_test.append(i)
	for i in torrent_choices_test:
		torrent_choices.pop(i)
	torrent_choices_test = []
	if len(sources_list) == 0:
		tools.log('UNCACHED_NO_CACHED TORENTS FOUND!!')
		sources_list = uncached
		for i in torrent_choices:
			if not 'uncached' in str(i).lower():
				torrent_choices_test.append(i)
	else:
		for i in torrent_choices:
			if 'uncached' in str(i).lower():
				torrent_choices_test.append(i)
	for i in torrent_choices_test:
		torrent_choices.pop(i)
	torrent = choose_torrent(sources_list)
	
	if torrent == None:
		return
	
	result = tools.selectFromDict(torrent_choices, 'Torrent')
	if result == None:
		return
	
	rd_api = real_debrid.RealDebrid()

	if result == 1 or result == 8:#'Add to RD Cache (whole pack)': 1,#'(Uncached) Add to RD (whole pack) ': 8,
		tools.log(torrent)
		response = rd_api.add_magnet(torrent['magnet'])
		tools.log(response)
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)
		tools.log(torr_info)
	elif result == 2:#'Add to RD Cache + Unrestrict (whole pack)': 2,
		tools.log(torrent)
		response = rd_api.add_magnet(torrent['magnet'])
		tools.log(response)
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)
		tools.log(torr_info)
		for i in torr_info['links']:
			unrestrict_link = i
			download_link = rd_api.resolve_hoster(unrestrict_link)
			download_id = rd_api.UNRESTRICT_FILE_ID
			log(download_link, download_id)
	elif result == 4:#'Add to downloader list (whole pack)': 4,
		tools.log(torrent)

		meta['download_type'] = 'pack'
		meta['download_type'] = 'movie'

		meta['magnet'] = torrent['magnet']

	elif result == 6:#'Add to downloader list (whole pack + subtitles)': 6,
		tools.log(torrent)
		meta['download_type'] = 'pack'
		meta['download_type'] = 'movie'

		meta['magnet'] = torrent['magnet']

	return

def choose_torrent(sources_list):
	sources_dict = {}
	for idx, i in enumerate(sources_list):
		source_name = '%s SIZE=%s SEEDS=%s PACK=%s   %s' % (i['release_title'], i['size'], i['seeds'], i['pack_size'], i['info'])
		source_name = str("{:<90}		{:<10}	{:<10}	{:<10}	{:<10}".format(str(i['release_title'][:95]), 'SIZE='+str(int(i['size'])), 'SEEDS='+str(i['seeds']), 'PACK='+str(int(i['pack_size'])), str(i['info'])))
		#log(i, '\n')
		sources_dict[source_name] = str(idx)

	result = tools.selectFromDict(sources_dict, 'Torrent')
	try: torrent = sources_list[int(result)]
	except: return None
	#log(torrent)
	return torrent


def cloud_get_ep_season(rd_api, meta, torr_id, torr_info):
	from source_tools import get_guess
	torr_info = rd_api.torrent_info_files(torr_info)
	sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
	info = meta['episode_meta']
	simple_info = tools._build_simple_show_info(info)

	result_dict = source_tools.match_episodes_season_pack(meta, sorted_torr_info)

	download_link = None
	new_meta = meta
	#log(result_dict)
	#log(meta['episode_meta']['title'])
	try: meta_source = result_dict['concat'][0]['meta_source']
	except: meta_source = None
	if meta_source == None:
		return download_link, new_meta
	tvmaze_adjusted_eps = []
	jdx = 0
	if meta_source == 'tmdb_seasons' and len(meta['tmdb_seasons']['episodes']) < len(meta['tvmaze_seasons']['episodes']):
		for idx, i in enumerate(meta['tvmaze_seasons']['episodes']):
			try:
				try: curr_tmdb_name = meta['tmdb_seasons']['episodes'][idx]['name']
				except: curr_tmdb_name = ''
				#tools.log(i['name'], curr_tmdb_name)
				if i['name'] != curr_tmdb_name and not (str(i['name']) in str(curr_tmdb_name) or str(curr_tmdb_name) in str(i['name'])):
					for jdx, ji in enumerate(meta['tmdb_seasons']['episodes']):
						if i['name'] == meta['tmdb_seasons']['episodes'][jdx]['name'] or str(i['name']) in str(meta['tmdb_seasons']['episodes'][jdx]['name']) or str(meta['tmdb_seasons']['episodes'][jdx]['name']) in str(i['name']) :
							tvmaze_adjusted_eps.append(jdx+1)
							#log(i['name'], jdx+1, 111)
							#log(curr_tmdb_name)
							break
						elif distance.jaro_similarity(i['name'],meta['tmdb_seasons']['episodes'][jdx]['name']) > 0.925:
							tvmaze_adjusted_eps.append(jdx+1)
							#log(i['name'], jdx+1,222)
							#log(curr_tmdb_name)
							break
						elif distance.jaro_similarity(i['name'],meta['tmdb_seasons']['episodes'][jdx]['name']) > 0.8:
							dummy_file1 = '%s S%sE%s - %s.mkv' % (str(simple_info['show_title']), str(simple_info['season_number']).zfill(2), str(idx+1).zfill(2), str(i['name']))
							dummy_file2 = '%s S%sE%s - %s.mkv' % (str(simple_info['show_title']), str(simple_info['season_number']).zfill(2), str(idx+1).zfill(2), str(meta['tmdb_seasons']['episodes'][jdx]['name']))
							options = {'type': 'episode'}
							guess1 = get_guess(dummy_file1, options)
							guess2 = get_guess(dummy_file2, options)
							#log(guess1,guess2)
							if guess1['episode_title'] == guess2['episode_title']:
								tvmaze_adjusted_eps.append(jdx+1)
								#log(i['name'], jdx+1,2a2a2a)
								#log(curr_tmdb_name)
								break
				elif i['name'] == curr_tmdb_name or str(i['name']) in str(curr_tmdb_name) or str(curr_tmdb_name) in str(i['name']):
					tvmaze_adjusted_eps.append(idx+1)
					#log(i['name'], idx+1,333)
					#log(curr_tmdb_name)
				elif distance.jaro_similarity(i['name'],curr_tmdb_name) > 0.925:
					tvmaze_adjusted_eps.append(idx+1)
					#log(i['name'], idx+1,444)
					#log(curr_tmdb_name)
				elif distance.jaro_similarity(i['name'],curr_tmdb_name) > 0.8:
					dummy_file1 = '%s S%sE%s - %s.mkv' % (str(simple_info['show_title']), str(simple_info['season_number']).zfill(2), str(idx+1).zfill(2), str(i['name']))
					dummy_file2 = '%s S%sE%s - %s.mkv' % (str(simple_info['show_title']), str(simple_info['season_number']).zfill(2), str(idx+1).zfill(2), str(curr_tmdb_name))
					options = {'type': 'episode'}
					guess1 = get_guess(dummy_file1, options)
					guess2 = get_guess(dummy_file2, options)
					if guess1['episode_title'] == guess2['episode_title']:
						tvmaze_adjusted_eps.append(idx+1)
						#log(i['name'], idx+1,444)
						#log(curr_tmdb_name)
			except: 
				except_no = idx+1
				log('EXCEPTIUON__cloud_get_ep_season',i['name'], idx+1, meta['tvmaze_seasons']['episodes'][idx]['name'])
				pass
	#log(tvmaze_adjusted_eps, simple_info)
	original_ep_no = int(simple_info['episode_number'])
	for i in result_dict['episode_numbers']:
		if not int(i) in tvmaze_adjusted_eps:
			tvmaze_adjusted_eps.append(int(i))
	try: simple_info['episode_number'] = str(tvmaze_adjusted_eps[ int(simple_info['episode_number'])-1 ])
	except: pass

	#log(simple_info['episode_number'])

	#mode = 'tmdb'
	#result_dict2 = source_tools.match_episodes_season_pack(meta, sorted_torr_info)
	#log(result_dict2)
	#if len(result_dict1['episode_numbers']) > len(result_dict2['episode_numbers']):
	#	result_dict = result_dict1
	#else:
	#	result_dict = result_dict2
	messed_up_numbering_flag = False
	if original_ep_no != int(simple_info['episode_number']):
		test_ep = original_ep_no
	else:
		test_ep = int(simple_info['episode_number'])

	for ijx, ij in enumerate(result_dict['alt_ep_num']):
		torr_ep_index = ijx
		if 'list' in str(type(ij)):
			for ijix, iji in enumerate(ij):
				if int(iji) == int(test_ep):
					if int(iji) != int(result_dict['episode_numbers'][ijx+ ijix]):
						if int(iji) == int(result_dict['episode_numbers'][ijx - ijix]) or int(iji) != int(result_dict['episode_numbers'][ijx + ijix]):
							continue
						messed_up_numbering_flag = True
						new_info = meta[meta_source]['episodes'][int(result_dict['episode_numbers'][ijx])-1]
						#tools.log(new_info)
						new_meta = get_meta.get_episode_meta(season=new_info['season'],episode=new_info['episode'],tmdb=new_info['tmdb'])
						break
			if messed_up_numbering_flag:
				break

		else:
			if int(ij) == int(test_ep):
				if int(ij) != int(result_dict['episode_numbers'][ijx]):
					messed_up_numbering_flag = True
					new_info = meta[meta_source]['episodes'][int(result_dict['episode_numbers'][ijx])-1]
					#tools.log(new_info)
					new_meta = get_meta.get_episode_meta(season=new_info['season'],episode=new_info['episode'],tmdb=new_info['tmdb'])
					break


	if messed_up_numbering_flag == True:
		for ijx, ij in enumerate(result_dict['alt_ep_num']):
			if int(ij) == int(test_ep):
				pack_path = result_dict['pack_paths'][ijx]
				for ik in sorted_torr_info:
					#tools.log(ik)
					if pack_path == ik['pack_path'] or ik['pack_path'] in str(pack_path) or pack_path in str(ik['pack_path']):
						unrestrict_link = ik['unrestrict_link']
						response = rd_api.resolve_hoster(unrestrict_link)
						download_link = response
						download_link = rd_api.test_download_link(download_link)
						if download_link:
							download_id = download_link.split('/')[4]
							file_name = unquote(download_link).split('/')[-1]
						#log(download_link, download_id, pack_path, file_name)
						break
	else:

		for ijx, ij in enumerate(result_dict['episode_numbers']):
			if int(ij) == int(simple_info['episode_number']):
				pack_path = result_dict['pack_paths'][ijx]
				for ik in sorted_torr_info:
					#tools.log(ik)
					if pack_path == ik['pack_path'] or ik['pack_path'] in str(pack_path) or pack_path in str(ik['pack_path']):
						unrestrict_link = ik['unrestrict_link']
						response = rd_api.resolve_hoster(unrestrict_link)
						download_link = response
						download_link = rd_api.test_download_link(download_link)
						if download_link:
							download_id = download_link.split('/')[4]
							file_name = unquote(download_link).split('/')[-1]
						#log(download_link, download_id, pack_path, file_name)
						new_meta = meta
						break
	return download_link, new_meta

def auto_scrape_rd(meta):
	rd_api = real_debrid.RealDebrid()
	if meta.get('download_type',False) == 'movie':
		info = meta
		download_type = meta.get('download_type',False)
		meta['episode_meta'] = {}
	else:
		info = meta['episode_meta']
		download_type = meta.get('download_type',False)
	special_flag = False
	special_meta = None
	if meta['episode_meta'].get('special',False) == True:
		special_flag = True
		special_movie_name = '%s: %s' % (info['tvshow'],info['title'])
		special_meta = get_meta.get_movie_meta(movie_name=special_movie_name,year=info['year'])
		if special_meta:
			special_simple_info = tools._build_simple_movie_info(special_meta)

	uncached, sources_list, item_information = Sources(info).get_sources()
	#torrent = getSources.choose_torrent(sources_list)
	idx = 0
	sources_list = tools.SourceSorter(info).sort_sources(sources_list)
	uncached = tools.SourceSorter(info).sort_sources(uncached)
	if special_flag == True and(len(sources_list) == 0 or len(sources_list)+len(uncached)<5):
		info2 = info
		info2['episode'] = str(meta['episode_meta']['alt_episode'])
		info2['season'] = str(meta['episode_meta']['alt_season'])
		info2['info']['episode'] = str(meta['episode_meta']['alt_episode'])
		info2['info']['season'] = str(meta['episode_meta']['alt_season'])
		tools.log('NO SOURCES_LENGTH_SOURCES_LIST_UNCACHED==',len(sources_list)+len(uncached))
		uncached, sources_list, item_information = Sources(info2).get_sources()
		sources_list = tools.SourceSorter(info2).sort_sources(sources_list)
		uncached = tools.SourceSorter(info2).sort_sources(uncached)
	if special_meta and(len(sources_list) == 0 or len(sources_list)+len(uncached)<5):
		info2 = special_meta
		tools.log('NO SOURCES_LENGTH_SOURCES_LIST_UNCACHED==',len(sources_list)+len(uncached))
		uncached, sources_list, item_information = Sources(info2).get_sources()
		sources_list = tools.SourceSorter(info2).sort_sources(sources_list)
		uncached = tools.SourceSorter(info2).sort_sources(uncached)

	download_link = None
	torrent = None
	while download_link == None:
		try: 
			torrent = sources_list[idx]
		except: 
			try:
				tools.log('UNCACHED')
				torrent = uncached[idx]
				idx = idx + 1
				response = rd_api.add_magnet(torrent['magnet'])
				#tools.log(response)
				torr_id = response['id']
				response = rd_api.torrent_select_all(torr_id)
				torr_info = rd_api.torrent_info(torr_id)
				#torr_info = rd_api.torrent_info_files(torr_info)
				if torr_info['status'] == 'downloaded':
					if download_type == 'movie':
						download_link, new_meta = cloud_movie(rd_api, meta, torr_id, torr_info)
					if download_link:
						return download_link, new_meta
					if download_type != 'movie':
						download_link, new_meta = cloud_single_ep(rd_api, meta, torr_id, torr_info)
					if download_link:
						return download_link, new_meta
					if special_meta:
						download_link, special_meta = cloud_movie(rd_api, special_meta, torr_id, torr_info)
					if download_link:
						return download_link, meta
					if download_type != 'movie':
						download_link, new_meta = cloud_get_ep_season(rd_api, meta, torr_id, torr_info)
					if download_link:
						return download_link, meta
				#tools.log(response)
				tools.log('UNCACHED_ADDED_1ST_LINK_TO_RD')
				return None, meta
			except:
				tools.log(torrent, 'EXCEPTION_auto_scrape_rd')
				return None, meta

		torrent = sources_list[idx]
		idx = idx + 1
		response = rd_api.add_magnet(torrent['magnet'])
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)
		if torr_info['status'] != 'downloaded':
			continue
		#torr_info = rd_api.torrent_info_files(torr_info)
		#sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
		#simple_info = tools._build_simple_show_info(info)
		#for i in sorted_torr_info:
		#	test = source_tools.run_show_filters(simple_info, release_title = i['pack_path'])
		#	if ': True' in str(test):
		#		log(test)
		if download_type == 'movie':
			download_link, new_meta = cloud_movie(rd_api, meta, torr_id, torr_info)
		if download_link:
			return download_link, new_meta
		if special_meta:
			download_link, special_meta = cloud_movie(rd_api, special_meta, torr_id, torr_info)
		if download_link:
			return download_link, meta
		if download_type != 'movie':
			download_link, new_meta = cloud_single_ep(rd_api, meta, torr_id, torr_info)
		if download_link:
			return download_link, new_meta
		if download_type != 'movie':
			download_link, new_meta = cloud_get_ep_season(rd_api, meta, torr_id, torr_info)
		if download_link:
			return download_link, new_meta


#	"""
#	torr_info = rd_api.torrent_info_files(torr_info)
#	sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
#	simple_info = tools._build_simple_show_info(info)
#
########################DEF
#	result_dict = source_tools.match_episodes_season_pack(meta, sorted_torr_info)
#
#	#log(result_dict)
#	#log(meta['episode_meta']['title'])
#	meta_source = result_dict['concat'][0]['meta_source']
#	tvmaze_adjusted_eps = []
#	jdx = 0
#	if meta_source == 'tmdb_seasons' and len(meta['tmdb_seasons']['episodes']) < len(meta['tvmaze_seasons']['episodes']):
#		for idx, i in enumerate(meta['tvmaze_seasons']['episodes']):
#			try:
#				if i['name'] != meta['tmdb_seasons']['episodes'][idx]['name'] and not (str(i['name']) in str(meta['tmdb_seasons']['episodes'][idx]['name']) or str(meta['tmdb_seasons']['episodes'][idx]['name']) in str(i['name'])):
#					for jdx, ji in enumerate(meta['tvmaze_seasons']['episodes']):
#						if i['name'] == meta['tmdb_seasons']['episodes'][jdx]['name'] or str(i['name']) in str(meta['tmdb_seasons']['episodes'][jdx]['name']) or str(meta['tmdb_seasons']['episodes'][jdx]['name']) in str(i['name']) :
#							tvmaze_adjusted_eps.append(jdx+1)
#							#log(i['name'], jdx+1)
#							#log(meta['tmdb_seasons']['episodes'][idx]['name'])
#							break
#				if i['name'] == meta['tmdb_seasons']['episodes'][idx]['name'] or str(i['name']) in str(meta['tmdb_seasons']['episodes'][idx]['name']) or str(meta['tmdb_seasons']['episodes'][idx]['name']) in str(i['name']):
#					tvmaze_adjusted_eps.append(jdx+1)
#					#log(i['name'], jdx+1)
#					#log(meta['tmdb_seasons']['episodes'][idx]['name'])
#			except: 
#				except_no = jdx+1
#				#log(meta['tvmaze_seasons']['episodes'][idx]['name'])
#				pass
#	#log(tvmaze_adjusted_eps)
#	for i in result_dict['episode_numbers']:
#		if not int(i) in tvmaze_adjusted_eps:
#			tvmaze_adjusted_eps.append(int(i))
#	simple_info['episode_number'] = str(tvmaze_adjusted_eps[ int(simple_info['episode_number'])-1 ])
#
#	#log(simple_info['episode_number'])
#
#	#mode = 'tmdb'
#	#result_dict2 = source_tools.match_episodes_season_pack(meta, sorted_torr_info)
#	#log(result_dict2)
#	#if len(result_dict1['episode_numbers']) > len(result_dict2['episode_numbers']):
#	#	result_dict = result_dict1
#	#else:
#	#	result_dict = result_dict2
#	messed_up_numbering_flag = False
#	for ijx, ij in enumerate(result_dict['alt_ep_num']):
#		torr_ep_index = ijx
#		if int(ij) == int(simple_info['episode_number']):
#			if int(ij) != int(result_dict['episode_numbers'][ijx]):
#				messed_up_numbering_flag = True
#				new_info = meta[meta_source]['episodes'][int(ij)-1]
#				new_meta = get_meta.get_episode_meta(season=new_info['season'],episode=new_info['episode'],tmdb=new_info['tmdb'])
#		break
#
#	if messed_up_numbering_flag == True:
#		for ijx, ij in enumerate(result_dict['alt_ep_num']):
#			if int(ij) == int(simple_info['episode_number']):
#				pack_path = result_dict['pack_paths'][ijx]
#				for ik in sorted_torr_info:
#					#tools.log(ik)
#					if pack_path == ik['pack_path'] or ik['pack_path'] in str(pack_path) or pack_path in str(ik['pack_path']):
#						unrestrict_link = ik['unrestrict_link']
#						response = rd_api.resolve_hoster(unrestrict_link)
#						download_link = response
#						download_id = download_link.split('/')[4]
#						file_name = unquote(download_link).split('/')[-1]
#						log(download_link, download_id, pack_path, file_name)
#						break
#	else:
#
#		for ijx, ij in enumerate(result_dict['episode_numbers']):
#			if int(ij) == int(simple_info['episode_number']):
#				pack_path = result_dict['pack_paths'][ijx]
#				for ik in sorted_torr_info:
#					#tools.log(ik)
#					if pack_path == ik['pack_path'] or ik['pack_path'] in str(pack_path) or pack_path in str(ik['pack_path']):
#						unrestrict_link = ik['unrestrict_link']
#						response = rd_api.resolve_hoster(unrestrict_link)
#						download_link = response
#						download_id = download_link.split('/')[4]
#						file_name = unquote(download_link).split('/')[-1]
#						log(download_link, download_id, pack_path, file_name)
#						new_meta = meta
#						break
########################DEF
#
#	#for i in torr_info['files_links']:
#	#	if info['file_name'] in str(i):
#	#		unrestrict_link = i['unrestrict_link']
#
#	#log(unrestrict_link, download_path)
#	#download_link = rd_api.resolve_hoster(unrestrict_link)
#	#download_id = rd_api.UNRESTRICT_FILE_ID
#	#log(download_link, download_id)
#
#	##info = get_subtitles(info, download_path)
#	##sub_out = os.path.basename(tools.SUB_FILE)
#	##sub_path = os.path.join(download_folder, sub_out)
#	##log(sub_path)
#
#	##rd_api.delete_download(rd_api.UNRESTRICT_FILE_ID)
#
#	##rd_api.delete_torrent(torr_id)
#	return download_link, new_meta
#	"""

def cloud_movie(rd_api, meta, torr_id, torr_info):
	download_link = None

	torr_info = rd_api.torrent_info_files(torr_info)
	sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
	simple_info = tools._build_simple_movie_info(meta)
	
	simple_info['imdb_id'] = meta['imdb_id']
	#tools.log(sorted_torr_info)
	pack_path = None
	for i in sorted_torr_info:
		test1 = source_tools.filter_movie_title(torr_info['filename'], source_tools.clean_title(torr_info['filename']), meta['title'], simple_info)
		test2 = source_tools.filter_movie_title(i['pack_path'], source_tools.clean_title( i['pack_path']), meta['title'], simple_info)
		if test1 or test2:
			pack_path = i['pack_path']
			break

	if pack_path == None:
		return download_link, meta 

	for x in torr_info['files_links']:
		if pack_path == x['pack_path']:
			unrestrict_link = x['unrestrict_link']
			break

	#log(unrestrict_link, pack_path)
	download_link = rd_api.resolve_hoster(unrestrict_link)
	download_id = rd_api.UNRESTRICT_FILE_ID
	download_link = rd_api.test_download_link(download_link)
	#log(download_link, download_id)
	
	return download_link, meta


def cloud_single_ep(rd_api, meta, torr_id, torr_info):
	torr_info = rd_api.torrent_info_files(torr_info)
	sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
	simple_info = tools._build_simple_show_info(meta['episode_meta'])
	info = meta['episode_meta']

	for i in sorted_torr_info:
		pack_path = os.path.basename(i['pack_path'])
		test2 = source_tools.run_show_filters(simple_info, release_title = pack_path)
		if ': True' in str(test2):
			unrestrict_link = i['unrestrict_link']

	download_link = rd_api.resolve_hoster(unrestrict_link)
	download_id = rd_api.UNRESTRICT_FILE_ID
	download_link = rd_api.test_download_link(download_link)
	#log(download_link, download_id)

	#info = get_subtitles(info, download_path)
	#sub_out = os.path.basename(tools.SUB_FILE)
	#sub_path = os.path.join(download_folder, sub_out)
	#shutil.copyfile(tools.SUB_FILE, sub_path)
	#rd_api.delete_download(rd_api.UNRESTRICT_FILE_ID)
	#log(sub_path)

	#rd_api.delete_torrent(torr_id)
	return download_link, meta


def check_rd_cloud(meta):
	"""
import getSources, get_meta
meta = get_meta.get_episode_meta(season=1,episode=3,show_name='Foundation',year=2021)
getSources.check_rd_cloud(meta)
"""
	download_link = ''
	special_flag = False
	special_meta = None
	if meta.get('download_type',False) == 'movie':
		info = meta
		download_type = meta.get('download_type',False)
		meta['episode_meta'] = {}
	else:
		info = None
		for i in meta['tvmaze_seasons']['episodes']:
			if i['episode'] == meta['episode_meta']['episode']:
				info = i
				break
		if not info:
			info = meta['episode_meta'] ##info = meta['tmdb_seasons']['episodes'][int(meta['episode_meta']['episode'])-1] #info = meta['episode_meta']
		download_type = meta.get('download_type',False)
	if meta['episode_meta'].get('special',False) == True:
		special_flag = True
		special_movie_name = '%s: %s' % (info['tvshow'],info['title'])
		special_meta = get_meta.get_movie_meta(movie_name=special_movie_name,year=info['year'])
		if special_meta:
			special_simple_info = tools._build_simple_movie_info(special_meta)
			special_simple_info['imdb_id'] = special_meta['imdb_id']
	#log(info)
	if download_type == 'movie':
		simple_info = tools._build_simple_movie_info(info)
		simple_info['imdb_id'] = info['imdb_id']
	else:
		simple_info = tools._build_simple_show_info(info)

	rd_api = real_debrid.RealDebrid()
	for i in range(1,99):
		#tools.log('download', i)
		result = rd_api.list_downloads_page(int(i))
		if '[204]' in str(result):
			break
		for x in result:
			#tools.log('download', i, x)
			
			file_info1 = tools.get_info(x['filename'])
			file_info2 = tools.get_info(source_tools.clean_title(x['filename']))
			source_list = []
			source_list.append({'filename': x['filename'], 'info': tools.get_info(x['filename']), 'quality': tools.get_quality(x['filename'])})
			source_list.append({'filename': x['filename'], 'info': tools.get_info(source_tools.clean_title(x['filename'])), 'quality': tools.get_quality(source_tools.clean_title(x['filename']))})
			new_source_list = list(tools.SourceSorter(info).filter_sources2(source_list))

			if download_type == 'movie':
				test = source_tools.filter_movie_title(x['filename'], source_tools.clean_title(x['filename']), meta['title'], simple_info)
				if test:
					test = ': True'
			else:
				test = source_tools.run_show_filters(simple_info, release_title = x['filename'])
			if ': True' in str(test):
				download_link = x['download']
				download_link = rd_api.test_download_link(download_link)
				if download_link:
					log('download',download_link, x['filename'],file_info1,file_info2,len(new_source_list))
					break
			if special_flag == True:

				simple_info2 = simple_info
				if meta['episode_meta']['alt_episode'] != None:
					simple_info2['episode_number'] = str(meta['episode_meta']['alt_episode'])
					simple_info2['season_number'] = str(meta['episode_meta']['alt_season'])

				test = source_tools.run_show_filters(simple_info2, release_title = x['filename'])
				if ': True' in str(test):
					download_link = x['download']
					download_link = rd_api.test_download_link(download_link)
					if download_link:
						log('special_download',download_link, x['filename'],file_info1,file_info2,len(new_source_list))
						break

				if special_meta:
					test = source_tools.filter_movie_title(x['filename'], source_tools.clean_title(x['filename']), special_meta['title'], special_simple_info)
					if test:
						test = ': True'
					if ': True' in str(test):
						download_link = x['download']
						download_link = rd_api.test_download_link(download_link)
						if download_link:
							log('special_download2',download_link, x['filename'],file_info1,file_info2,len(new_source_list))
							break

		if download_link:
			break

	if download_link:
		return download_link, meta
	for i in range(1,99):
		#tools.log('torrent', i)
		result = rd_api.list_torrents_page(int(i))
		if '[204]' in str(result):
			break
		for x in result:
			#tools.log('torrent', i, x)
			file_info1 = tools.get_info(x['filename'])
			file_info2 = tools.get_info(source_tools.clean_title(x['filename']))
			source_list = []
			source_list.append({'filename': x['filename'], 'info': tools.get_info(x['filename']), 'quality': tools.get_quality(x['filename'])})
			source_list.append({'filename': x['filename'], 'info': tools.get_info(source_tools.clean_title(x['filename'])), 'quality': tools.get_quality(source_tools.clean_title(x['filename']))})
			new_source_list = list(tools.SourceSorter(info).filter_sources2(source_list))
			
			if download_type == 'movie':
				test = source_tools.filter_movie_title(x['filename'], source_tools.clean_title(x['filename']), meta['title'], simple_info)
				if test:
					test = ': True'
				#test2 = source_tools.filter_movie_title(x['filename'], source_tools.clean_title(x['filename']), meta['title'], simple_info)
				test2 = {}
			else:
				test = source_tools.run_show_filters(simple_info, pack_title = x['filename'])
				if simple_info['episode_number'] == 'None' or simple_info['episode_number'] == None:
					simple_info1 = simple_info
					simple_info1['episode_number'] = '0'
					test2 = source_tools.run_show_filters(simple_info1, release_title = x['filename'])
				else:
					test2 = source_tools.run_show_filters(simple_info, release_title = x['filename'])
			if ': True' in str(test) or ': True' in str(test2):
				torr_id = x['id']
				torr_info = rd_api.torrent_info(torr_id)
				if download_type == 'movie':
					download_link, meta = cloud_movie(rd_api, meta, torr_id, torr_info)
					if download_link:
						tools.log('cloud_movie',download_link,'download_link',file_info1,file_info2,len(new_source_list))
						return download_link, meta

				download_link, new_meta = cloud_get_ep_season(rd_api, meta, torr_id, torr_info)
				if download_link:
					tools.log('cloud_get_ep_season',download_link,'download_link',file_info1,file_info2,len(new_source_list))
					return download_link, new_meta

			if special_flag == True:
				simple_info2 = simple_info
				simple_info2['episode_number'] = str(meta['episode_meta']['alt_episode'])
				simple_info2['season_number'] = str(meta['episode_meta']['alt_season'])
				test = source_tools.run_show_filters(simple_info, pack_title = x['filename'])
				if simple_info['episode_number'] == 'None' or simple_info['episode_number'] == None:
					simple_info1 = simple_info
					simple_info1['episode_number'] = '0'
					simple_info1['season_number'] = '0'
					test2 = source_tools.run_show_filters(simple_info1, release_title = x['filename'])
				else:
					test2 = source_tools.run_show_filters(simple_info, release_title = x['filename'])
				if ': True' in str(test) or ': True' in str(test2):
					torr_id = x['id']
					torr_info = rd_api.torrent_info(torr_id)

					download_link, new_meta = cloud_get_ep_season(rd_api, meta, torr_id, torr_info)
					if download_link:
						tools.log('SPECIAL_cloud_get_ep_season',download_link,'download_link',file_info1,file_info2,len(new_source_list))
						return download_link, new_meta

				if special_meta:
					test2 = source_tools.filter_movie_title(x['filename'], source_tools.clean_title(x['filename']), special_meta['title'], special_simple_info)
					if test2:
						test2 = ': True'
					if ': True' in str(test) or ': True' in str(test2):
						torr_id = x['id']
						torr_info = rd_api.torrent_info(torr_id)
						download_link, special_meta = cloud_movie(rd_api, special_meta, torr_id, torr_info)
						if download_link:
							tools.log('SPECIAL_cloud_movie',download_link,'download_link',file_info1,file_info2,len(new_source_list))
							return download_link, meta

	return download_link, meta


#def unprocessed_rd_http(magnet_link, file_path, torr_id, download_folder):
#		if magnet_link.startswith('http'):
#			log(f"Downloading RD HTTP link: {magnet_link}")
#			#file_name = os.path.basename(magnet_link)
#			#save_path = os.path.join(download_folder, file_name)
#			#download_file(magnet_link, save_path)
#			#log(magnet_link)
#			new_link = unrestrict_link(api_key, magnet_link)
#			log(new_link)
#			#exit()
#			if new_link:
#				file_name = os.path.basename(new_link['filename'])
#				if new_link['filename'][0:1].lower() == new_link['filename'][0:1]:
#					file_name = getSentenceCase(os.path.basename(new_link['filename']))
#				else:
#					file_name = os.path.basename(new_link['filename'])
#				save_path = os.path.join(download_folder, file_name)
#				download_link = new_link['download']
#				download_file(download_link, save_path)
#				download_bool = True
#				remove_line_from_file(file_path, magnet_link)
#				log(f"Download of '{file_name}' complete! Removed link from the file.")
#			else:
#				download_bool = False
#				log(f"HOSTER FAIL '{magnet_link}'.")
#				remove_line_from_file(file_path, magnet_link)

#def uncached_magnet(magnet_link, torr_id, magnet_added, download_folder):
#	if file_info['status'] != 'downloaded':
#		response = delete_torrent(api_key, torrent_id)
#		ids = [element['id'] for element in data['files']]
#		files = [element['path'] for element in data['files']]
#		files = [x.encode('utf-8') for x in files]
#		files, ids = zip(*sorted(zip(files,ids)))
#		download_count = 0
#		for x in files:
#			if '.mp4' in str(x) or '.avi' in str(x) or '.mkv' in str(x):
#				log('SLEEPING_10_SECONDS!!!')
#				time.sleep(10)
#				log('')
#				log('')
#
#				torrent_id = add_magnet(api_key, magnet_link)
#				params = {'files': ids[files.index(x)]}
#				file_info2 = select_files_individual(api_key, torrent_id, params)
#				if file_info2['status'] == 'downloaded':
#					folder = file_info2['original_filename']
#					if '.mp4' in str(folder) or '.avi' in str(folder) or '.mkv' in str(folder):
#						folder = None
#					for file in file_info2['links']:
#						new_link = unrestrict_link(api_key, file)
#						file_name = os.path.basename(new_link['filename'])
#						if new_link['filename'][0:1].lower() == new_link['filename'][0:1]:
#							file_name = getSentenceCase(os.path.basename(new_link['filename']))
#						else:
#							file_name = os.path.basename(new_link['filename'])
#						if folder:
#							download_folder2 = download_folder + folder + '/'
#							folder = None
#							if not os.path.exists(download_folder2):
#								os.makedirs(download_folder2)
#						save_path = os.path.join(download_folder2, file_name)
#						download_link = new_link['download']
#						if not save_path in str(magnet_download):
#							download_file(download_link, save_path)
#							magnet_download.append(save_path)
#							log(f"Downloaded '{file_name}' successfully!")
#						if save_path in str(magnet_download):
#							download_count = download_count + 1
#				else:
#					if file_info2['filename'] in str(magnet_added):
#						delete_torrent(api_key, torrent_id)
#					else:
#						magnet_added.append(file_info2['filename'])
#		if download_count == file_count:
#			remove_line_from_file(file_path, magnet_link)
#			log("All files downloaded. Removed magnet link from the file.")
#		else:
#			remove_line_from_file(file_path, magnet_link)
#			add_line_to_file(file_path, magnet_link)


def download_http_rd_link(rd_api, download_path, curr_download):
	unrestrict_link = curr_download
	download_folder = download_path

	log(unrestrict_link, download_path)
	download_link = rd_api.resolve_hoster(unrestrict_link)
	download_id = rd_api.UNRESTRICT_FILE_ID
	log(download_link, download_id)
	file_name = os.path.basename(download_link)
	file_name = unquote(file_name)
	download_path2 = os.path.join(download_path, file_name)

	if not os.path.exists(download_folder):
		os.makedirs(download_folder)
	tools.download_progressbar(download_link, download_path2)


def download_uncached_magnet(rd_api, download_path, curr_download, torr_id, torr_info, processed_files, magnet_list, test_download):
	#tools.log('download_uncached_magnet')
	torr_info = rd_api.torrent_info_files(torr_info)
	sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
	number_rd = 0
	for i in sorted_torr_info:
		if '.mp4' in str(i) or '.avi' in str(i) or '.mkv' in str(i):
			number_rd = number_rd + 1
	rd_api.delete_torrent(torr_id)

	def is_tvshow_process(torr_id, torr_info, tot_streams, pack_path):
		#number_rd = tot_streams
		number_tmdb = len(curr_download['tmdb_seasons']['episodes'])
		number_tvmaze = len(curr_download['tvmaze_seasons']['episodes'])
		if number_tvmaze == number_rd:
			mode = 'tvmaze'
		else:
			mode = 'tmdb'
		#tools.log(mode)
		result_dict = source_tools.match_episodes_season_pack(curr_download, sorted_torr_info)
		#tools.log(result_dict)

		for idx, i in enumerate(result_dict['pack_paths']):
			if pack_path in i or pack_path == i:
				if mode == 'tvmaze':
					info = curr_download['tvmaze_seasons']['episodes'][idx]
				else:
					info = curr_download['tmdb_seasons']['episodes'][idx]
		for i in torr_info['links']:
			unrestrict_link = i

		folder = curr_download['CURR_LABEL']
		download_folder = os.path.join(download_path, folder)
		download_path2 = os.path.join(download_folder + pack_path)

		log(unrestrict_link, download_path2)
		download_link = rd_api.resolve_hoster(unrestrict_link)
		download_id = rd_api.UNRESTRICT_FILE_ID
		log(download_link, download_id)
		#file_name = os.path.basename(download_link)

		if not os.path.exists(download_folder):
			os.makedirs(download_folder)
		tools.download_progressbar(download_link, download_path2)
		info = get_subtitles(info, download_path2)
		sub_out = os.path.basename(tools.SUB_FILE)
		sub_path = os.path.join(download_folder, sub_out)
		shutil.copyfile(tools.SUB_FILE, sub_path)
		log(sub_path)

	def is_movie_process(torr_id, torr_info):
		#tools.log('is_movie_process')
		folder = curr_download['CURR_LABEL']
		if '.mp4' in str(folder) or '.avi' in str(folder) or '.mkv' in str(folder):
			folder = None
		for i in torr_info['links']:
			unrestrict_link = i
		download_folder = os.path.join(download_path, folder)
		download_path2 = os.path.join(download_folder + pack_path)

		log(unrestrict_link, download_path2)
		download_link = rd_api.resolve_hoster(unrestrict_link)
		download_id = rd_api.UNRESTRICT_FILE_ID
		log(download_link, download_id)
		#file_name = os.path.basename(download_link)

		if not os.path.exists(download_folder):
			os.makedirs(download_folder)
		tools.download_progressbar(download_link, download_path2)
		info = get_subtitles(curr_download, download_path2)
		sub_out = os.path.basename(tools.SUB_FILE)
		sub_path = os.path.join(download_folder, sub_out)
		shutil.copyfile(tools.SUB_FILE, sub_path)
		log(sub_path)

	def plain_download(torr_id, torr_info):
		#tools.log('DOWNLOAD_TO_MAIN_FOLDER_NO_META')
		#tools.log(torr_info)
		folder = torr_info['original_filename']
		if '.mp4' in str(folder) or '.avi' in str(folder) or '.mkv' in str(folder):
			folder = None
		for i in torr_info['links']:
			unrestrict_link = i
		download_link = rd_api.resolve_hoster(unrestrict_link)
		download_id = rd_api.UNRESTRICT_FILE_ID
		log(download_link, download_id)
		file_name = os.path.basename(download_link)
		download_folder = os.path.join(download_path, folder)
		if not os.path.exists(download_folder):
			os.makedirs(download_folder)
		download_path2 = os.path.join(download_folder, file_name)
		tools.download_progressbar(download_link, download_path2)

	tot_streams = 0
	downloaded_streams = 0
	for i in sorted_torr_info:
		if '.mp4' in str(i) or '.avi' in str(i) or '.mkv' in str(i):
			tot_streams = tot_streams + 1
		else:
			continue

		try: magnet = curr_download['magnet']
		except: magnet = curr_download
		response = rd_api.add_magnet(magnet)
		torr_id = response['id']
		response = rd_api.torrent_select(torr_id, i['pack_file_id'])
		pack_path = i['pack_path']
		if test_download == False:
			log('Added ' + str(pack_path))
			torr_info2 = rd_api.torrent_info(torr_id)
			if torr_info2['status'] == 'downloaded':
				rd_api.delete_torrent(torr_id)

		if str(pack_path) in str(processed_files):
			tools.log('DELETE_TORR_ID')
			rd_api.delete_torrent(torr_id)
			continue
		if test_download:
			torr_info = rd_api.torrent_info(torr_id)
			if torr_info['status'] == 'downloaded':
				#pack_path = i['pack_path']
				try: is_tvshow = curr_download['episode_meta']['is_tvshow']
				except: is_tvshow = False
				try: is_movie = curr_download['episode_meta']['is_movie']
				except: is_movie = False
				if is_tvshow:
					is_tvshow_process(torr_id, torr_info, tot_streams, pack_path)
				if is_movie:
					is_movie_process(torr_id, torr_info)
				if is_tvshow == False and is_movie == False:
					plain_download(torr_id, torr_info)
				rd_api.delete_torrent(torr_id)
				rd_api.delete_download(rd_api.UNRESTRICT_FILE_ID)
				processed_files.append(pack_path)
				downloaded_streams = downloaded_streams + 1
			if torr_info['status'] != 'downloaded':
				log('Added ' + str(pack_path))

				rd_api.delete_torrent(torr_id)

	if int(downloaded_streams) != int(number_rd):
		curr_download = tools.get_download_line(magnet_list)
		tools.delete_download_line(magnet_list, curr_download)
		tools.add_download_line(magnet_list, curr_download)
	if int(downloaded_streams) == int(number_rd):
		curr_download = tools.get_download_line(magnet_list)
		tools.delete_download_line(magnet_list, curr_download)
	return processed_files



def download_cached_movie(rd_api, download_path, curr_download, torr_id, torr_info):
	#tools.log('download_cached_movie')
	folder = curr_download['CURR_LABEL']
	download_folder = os.path.join(download_path, folder)
	torr_info = rd_api.torrent_info_files(torr_info)
	sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
	simple_info = tools._build_simple_show_info(curr_download)
	simple_info['imdb_id'] = curr_download['imdb_id']
	#tools.log(sorted_torr_info)
	for i in sorted_torr_info:
		#test = source_tools.run_show_filters(simple_info, pack_title = i['pack_path'])
		test1 = source_tools.filter_movie_title(curr_download['CURR_LABEL'], source_tools.clean_title(curr_download['CURR_LABEL']), curr_download['title'], simple_info)
		test2 = source_tools.filter_movie_title(curr_download['CURR_LABEL'], source_tools.clean_title( i['pack_path']), curr_download['title'], simple_info)
		if test1 or test2:
			pack_path = i['pack_path']
			break

	for x in torr_info['files_links']:
		if pack_path == x['pack_path']:
			unrestrict_link = x['unrestrict_link']
			break
	download_path = os.path.join(download_folder + pack_path)
	if not os.path.exists(download_folder):
		os.makedirs(download_folder)
	log(unrestrict_link, download_path)
	download_link = rd_api.resolve_hoster(unrestrict_link)
	download_id = rd_api.UNRESTRICT_FILE_ID
	log(download_link, download_id)
	
	tools.download_progressbar(download_link, download_path)
	info = get_subtitles(curr_download, download_path)
	sub_out = os.path.basename(tools.SUB_FILE)
	sub_path = os.path.join(download_folder, sub_out)
	shutil.copyfile(tools.SUB_FILE, sub_path)
	log(sub_path)

	rd_api.delete_torrent(torr_id)
	rd_api.delete_download(rd_api.UNRESTRICT_FILE_ID)

def download_cached_episode(rd_api, download_path, curr_download, torr_id, torr_info):
	#tools.log('download_cached_episode')
	folder = curr_download['CURR_LABEL']
	download_folder = os.path.join(download_path, folder)
	torr_info = rd_api.torrent_info_files(torr_info)
	sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
	simple_info = tools._build_simple_show_info(curr_download['episode_meta'])
	info = curr_download['episode_meta']
	show_folder = os.path.join(download_path, str(curr_download['episode_meta']['tvshow']) + ' (' + str(curr_download['episode_meta']['tvshow_year'] + ')'))
	if not os.path.exists(show_folder):
		os.makedirs(show_folder)
	season_folder = os.path.join(show_folder, str(curr_download['episode_meta']['tvshow']) + ' - Season ' + str(curr_download['episode_meta']['season']).zfill(2))
	if not os.path.exists(season_folder):
		os.makedirs(season_folder)
	download_folder = season_folder
	for i in torr_info['files_links']:
		if curr_download['file_name'] in str(i):
			unrestrict_link = i['unrestrict_link']
	download_path = os.path.join(download_folder, curr_download['filename'])
	log(unrestrict_link, download_path)
	download_link = rd_api.resolve_hoster(unrestrict_link)
	download_id = rd_api.UNRESTRICT_FILE_ID
	log(download_link, download_id)
	tools.download_progressbar(download_link, download_path)
	info = get_subtitles(info, download_path)
	sub_out = os.path.basename(tools.SUB_FILE)
	sub_path = os.path.join(download_folder, sub_out)
	shutil.copyfile(tools.SUB_FILE, sub_path)
	rd_api.delete_download(rd_api.UNRESTRICT_FILE_ID)
	log(sub_path)

	rd_api.delete_torrent(torr_id)



def download_cached_magnet_pack(rd_api, download_path, curr_download, torr_id, torr_info):
	folder = curr_download['CURR_LABEL']
	download_folder = os.path.join(download_path, folder)
	torr_info = rd_api.torrent_info_files(torr_info)
	sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
	number_rd = len(torr_info['files_links'])
	number_tmdb = len(curr_download['tmdb_seasons']['episodes'])
	number_tvmaze = len(curr_download['tvmaze_seasons']['episodes'])
	if number_tvmaze == number_rd:
		mode = 'tvmaze'
	else:
		mode = 'tmdb'
	result_dict = source_tools.match_episodes_season_pack(curr_download, sorted_torr_info)
	#log(torr_info['files_links'])
	#log(result_dict)
	for i in result_dict['concat']:
		episode = i['episode_number']
		season = i['season']
		pack_path = i['pack_path']
		for x in torr_info['files_links']:
			if i['pack_path'] == x['pack_path']:
				unrestrict_link = x['unrestrict_link']
		if mode == 'tmdb':
			info = curr_download['tmdb_seasons']['episodes'][int(episode)-1]
		else:
			info = curr_download['tvmaze_seasons']['episodes'][int(episode)-1]
		download_path = os.path.join(download_folder + pack_path)
		#log(season, episode, pack_path, unrestrict_link, info)
		log(unrestrict_link, download_path)
		download_link = rd_api.resolve_hoster(unrestrict_link)
		download_id = rd_api.UNRESTRICT_FILE_ID
		log(download_link, download_id)
		if not os.path.exists(download_folder):
			os.makedirs(download_folder)
		tools.download_progressbar(download_link, download_path)
		info = get_subtitles(info, download_path)
		sub_out = os.path.basename(tools.SUB_FILE)
		sub_path = os.path.join(download_folder, sub_out)
		shutil.copyfile(tools.SUB_FILE, sub_path)
		rd_api.delete_download(rd_api.UNRESTRICT_FILE_ID)
		log(sub_path)

	rd_api.delete_torrent(torr_id)
	

def cached_magnet(magnet_link, file_path, torr_id, download_folder):
	if file_info['status'] == 'downloaded':
		log(file_info)
		folder = file_info['original_filename']
		if '.mp4' in str(folder) or '.avi' in str(folder) or '.mkv' in str(folder):
			folder = None
		for file in file_info['links']:
			new_link = unrestrict_link(api_key, file)
			log(new_link)
			if new_link['filename'][0:1].lower() == new_link['filename'][0:1]:
				file_name = getSentenceCase(os.path.basename(new_link['filename']))
			else:
				file_name = os.path.basename(new_link['filename'])
			if folder:
				download_folder2 = download_folder + folder + '/'
				if not os.path.exists(download_folder2):
					os.makedirs(download_folder2)
			save_path = os.path.join(download_folder2, file_name)
			download_link = new_link['download']
			download_bool = True
			download_file(download_link, save_path)
			log(f"Downloaded '{file_name}' successfully!")

		remove_line_from_file(file_path, magnet_link)
		log("All files downloaded. Removed magnet link from the file.")


def rd_auth():
	'''
import getSources
getSources.rd_auth()
	'''
	rd_api = real_debrid.RealDebrid()
	rd_api.auth()
	log('AUTH_DONE')
	return
	
def get_providers_dict():
	"""
import getSources
getSources.get_providers_dict()
"""

	providers_dict = {}
	providers_dict['hosters'] = []
	providers_dict['torrent'] = []
	providers_dict['adaptive'] = []

	providers_dict_original = {'hosters': [], 
	'torrent': [
	('providers.a4kScrapers.en.torrent', 'bitlord', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'bitsearch', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'btdig', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'cached', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'glo', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'kickass', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'lime', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'magnetdl', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'piratebay', 'a4kScrapers'), 
	#('providers.a4kScrapers.en.torrent', 'rutor', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'showrss', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'torrentdownload', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'torrentio', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'torrentz2', 'a4kScrapers'), 
	('providers.a4kScrapers.en.torrent', 'yts', 'a4kScrapers')
	], 
	'adaptive': []}

	for root, dirs, files in os.walk(tools.A4KPROVIDERS_PATH, topdown=False):
		for name in files:
			#log(os.path.join(root, name))
			if '.py' == name[-3:] and '__init__.py' != name:
				file = str(os.path.join(root, name).split('providers')[1])
				if '/' in str(file):
					splits = str(file).split('/')
				else:
					splits = str(file).split('\\')
				providers_dict[splits[3]].append(tuple([str('providers.%s.%s.%s') % (splits[1],splits[2],splits[3]), splits[4].replace('.py',''), splits[1], True]))
	#log(providers_dict)
	return providers_dict

def setup_providers(provider_url):
	"""
import getSources
getSources.setup_providers('https://bit.ly/a4kScrapers')
"""
	provider_url = 'https://bit.ly/a4kScrapers'
	temp_zip = tools.temp_file()
	tools.download_file(provider_url, temp_zip)
	dest_dir = tools.ADDON_USERDATA_PATH
	tools.extract_zip(temp_zip, dest_dir)
	tools.delete_file(temp_zip)
	providers_dict = get_providers_dict()
	tools.write_all_text(tools.PROVIDERS_JSON,str(providers_dict))

def get_providers():
	providers_dict = eval(tools.read_all_text(tools.PROVIDERS_JSON))
	providers_dict_test = providers_dict
	for idx, i in enumerate(providers_dict_test):
		for xdx, x in enumerate(providers_dict_test[i]):
			if x[3] == False or str(x[3]) == 'False':
				providers_dict[i].pop(xdx)
	return providers_dict

def setup_userdata_folder():
	"""
import getSources
getSources.setup_userdata_folder()
"""
	tools.setup_userdata()


def enable_disable_providers_kodi():
	import xbmcgui, xbmc

	try: provider_dict = eval(tools.read_all_text(tools.PROVIDERS_JSON))
	except: provider_dict = get_providers_dict()
	if not provider_dict:
		provider_dict = get_providers_dict()

	def open_multi_select_list(provider_dict):
		# Create a list of list items with preselection
		new_provider_dict = {'hosters': [], 'torrent': [], 'adaptive': []}
		labels = []
		preselect = []
		for idx, i in enumerate(provider_dict):
			for xdx, x in enumerate(provider_dict[i]):
				if provider_dict[i][xdx][3] == True or str(provider_dict[i][xdx][3]) == str('True'):
					preselect.append(xdx)
				labels.append(provider_dict[i][xdx][1])
				
		indexes = xbmcgui.Dialog().multiselect(heading='Select Items',options=labels,preselect=preselect)
		selected_labels = []
		if indexes == None:
			return
		for i in indexes:
			selected_labels.append(labels[i])
		for idx, i in enumerate(provider_dict):
			for xdx, x in enumerate(provider_dict[i]):
				selected = False
				for y in selected_labels:
					if provider_dict[i][xdx][1] == y:
						selected = True
				new_provider_dict[i].append ( tuple([provider_dict[i][xdx][0], provider_dict[i][xdx][1], provider_dict[i][xdx][2], selected]) )

		return new_provider_dict

	# Call the function to open the multi-select list
	provider_dict = open_multi_select_list(provider_dict)

	if provider_dict:
		tools.write_all_text(tools.PROVIDERS_JSON,str(provider_dict))
	return


def enable_disable_providers():
	"""
import getSources
getSources.enable_disable_providers()
"""
	providers_dict = eval(tools.read_all_text(tools.PROVIDERS_JSON))
	providers_dict_test = providers_dict
	for idx, i in enumerate(providers_dict_test):
		for xdx, x in enumerate(providers_dict_test[i]):
				curr_status = providers_dict[i][xdx][3]
				if curr_status == False or str(curr_status) == 'False':
					toggle = 'ENABLED'
					curr_status = 'DISABLED'
					update_status = True
				else:
					toggle = 'DISABLED'
					curr_status = 'ENABLED'
					update_status = False
				curr_provider = providers_dict_test[i][xdx][1]
				curr_provider_type = i
				curr_provider_source = providers_dict_test[i][xdx][2]
				update = input(str('%s of type %s from %s is %s, toggle %s by any key, ENTER to pass:  ') % (curr_provider.upper(), curr_provider_type, curr_provider_source, curr_status, toggle))
				if update != '':
					providers_dict[i][xdx] = tuple([providers_dict_test[i][xdx][0], providers_dict_test[i][xdx][1], providers_dict_test[i][xdx][2], update_status])
				update = ''
	#log(providers_dict)
	tools.write_all_text(tools.PROVIDERS_JSON,str(providers_dict))
	for idx, i in enumerate(providers_dict_test):
		for xdx, x in enumerate(providers_dict_test[i]):
			log(x)
	return

def get_subtitles(VIDEO_META, file_path):
	"""
import get_meta, getSources
meta = get_meta.get_movie_meta(movie_name='Point Break',year=1991)
info = meta

import get_meta, getSources
meta = get_meta.get_episode_meta(season=1,episode=1,show_name='The Flash', year=2014)
info = meta['episode_meta']

##FILEPATH!!
getSources.get_subtitles(info , '')

"""
	try:
		VIDEO_META['file_name'] = os.path.basename(file_path)
		VIDEO_META['filename'] = VIDEO_META['file_name']
		VIDEO_META['filename_without_ext'] = os.path.splitext(VIDEO_META['file_name'])[0]
		VIDEO_META['subs_filename'] = VIDEO_META['filename_without_ext'] + '.srt'
		tools.VIDEO_META = VIDEO_META
		if 'http' in str(file_path):
			tools.VIDEO_META = tools.set_size_and_hash_url(tools.VIDEO_META, file_path)
		else:
			tools.VIDEO_META = tools.set_size_and_hash(tools.VIDEO_META, file_path)
	except:
		pass
	#os.environ['A4KSUBTITLES_API_MODE'] = str({'kodi': 'false'})
	try: import subtitles
	except: from a4kscrapers_wrapper import subtitles
	subfile = subtitles.SubtitleService().get_subtitle()
	tools.VIDEO_META['SUB_FILE'] = tools.SUB_FILE
	return tools.VIDEO_META


class Sources(object):
	"""
	Handles fetching and processing of available sources for provided meta data
	"""

	def __init__(self, item_information):
		self.hash_regex = re.compile(r'btih:(.*?)(?:&|$)')
		self.canceled = False
		#self.torrent_cache = TorrentCache()
		self.torrent_threads = ThreadPool()
		#self.hoster_threads = ThreadPool()
		#self.adaptive_threads = ThreadPool()
		self.item_information = item_information
		self.media_type = self.item_information['info']['mediatype']
		self.torrent_providers = []
		#self.hoster_providers = []
		#self.adaptive_providers = []
		#self.cloud_scrapers = []
		self.running_providers = []
		self.language = 'en'
		self.sources_information = {
			"torrentCacheSources": {},
			"cloudFiles": [],
			"allTorrents": {},
			"cached_hashes": set(),
			"statistics": {
				"torrents": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
				"torrentsCached": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
				"cloudFiles": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
				"totals": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
				"filtered": {
					"torrents": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
					"torrentsCached": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
					"cloudFiles": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
					"totals": {"4K": 0, "1080p": 0, "720p": 0, "SD": 0, "total": 0},
				},
				"remainingProviders": []
			}
		}

		#self.hoster_domains = {}
		self.progress = 0
		self.timeout_progress = 0
		self.runtime = 0
		#self.host_domains = []
		#self.host_names = []
		self.timeout = 45
		#self.window = SourceWindowAdapter(self.item_information, self)

		#self.silent = g.get_bool_runtime_setting('tempSilent')

		self.source_sorter = tools.SourceSorter(self.item_information)

		self.preem_enabled = False
		self.preem_waitfor_cloudfiles = True
		self.preem_cloudfiles = False
		#self.preem_adaptive_sources = g.get_bool_setting('preem.adaptiveSources')
		#self.preem_type = 0 #g.get_int_setting('preem.type')
		#self.preem_limit = 9 #g.get_int_setting('preem.limit')
		#self.preem_resolutions = tools.approved_qualities[1:self._get_pre_term_min()]
		#tools.PRE_TERM_BLOCK = False
		#self.PRE_TERM_BLOCK = False
		#self._prem_terminate = True
		#os.environ['data_path'] = os.path.join('./user_data/', 'providers')
		os.environ['data_path'] = tools.A4KPROVIDERS_PATH
		patch_ak4_requests()

	def get_sources(self):
		"""
		Main endpoint to initiate scraping process
		:param overwrite_cache:
		:return: Returns (uncached_sources, sorted playable sources, items metadata)
		:rtype: tuple
		"""
		try:
			log('Starting Scraping', 'debug')
			log("Timeout: {}".format(self.timeout), 'debug')
			#log("Pre-term-enabled: {}".format(self.preem_enabled), 'debug')
			#log("Pre-term-limit: {}".format(self.preem_limit), 'debug')
			#log("Pre-term-res: {}".format(self.preem_resolutions), 'debug')
			#log("Pre-term-type: {}".format(self.preem_type), 'debug')
			#log("Pre-term-cloud-files: {}".format(self.preem_cloudfiles), 'debug')
			#log("Pre-term-adaptive-files: {}".format(self.preem_adaptive_sources), 'debug')

			#self._handle_pre_scrape_modifiers()
			self._get_imdb_info()

			#if overwrite_torrent_cache:
			#	self._clear_local_torrent_results()
			#else:
			#	self._check_local_torrent_database()

			self._update_progress()
			if self._prem_terminate():
				log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				return self._finalise_results()

			self._init_providers()

			# Add the users cloud inspection to the threads to be run
			#self.torrent_threads.put(self._user_cloud_inspection)

			# Load threads for all sources
			self._create_torrent_threads()
			#self._create_hoster_threads()
			#self._create_adaptive_threads()

			start_time = time.time()
			while not ( len(self.torrent_providers) ) > 0:
				self.runtime = time.time() - start_time
				if self.runtime > 5:
					log('No providers enabled', 'warning')
					return

			self._update_progress()

			# Keep alive for gui display and threading
			log('Entering Keep Alive', 'info')

			log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			while self.progress < 100:
				self.runtime = time.time() - start_time

				time.sleep(1)
				log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

				self._update_progress()

				time.sleep(1)

				self.timeout_progress = int(100 - float(1 - (self.runtime / float(self.timeout))) * 100)
				self.progress = int(100 - (	len(self.sources_information['statistics']['remainingProviders']) / float(len(self.torrent_providers)) * 100) )

				log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				time.sleep(1)
				
				if self._prem_terminate() is True or (	len(self.sources_information['statistics']['remainingProviders']) == 0 and self.runtime > 5):
					# Give some time for scrapers to initiate

					log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
					time.sleep(1)

					break
				if self.canceled or self.runtime >= self.timeout:
					log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
					tools.PRE_TERM_BLOCK = True
					self.PRE_TERM_BLOCK = True

					time.sleep(1)

					break

				time.sleep(1)

			log('Exited Keep Alive', 'info')
			return self._finalise_results()

		finally:
			#self.window.close()
			log('EXIT')

	#def _handle_pre_scrape_modifiers(self):
	#	"""
	#	Detects preScrape, disables pre-termination and sets timeout to maximum value
	#	:return:
	#	:rtype:
	#	"""
	#	if g.REQUEST_PARAMS.get('action', '') == "preScrape":
	#		self.silent = True
	#		self.timeout = 180
	#		self._prem_terminate = self._disabled_prem_terminate
	
	#def _disabled_prem_terminate(self):
	#	return False

	def _create_torrent_threads(self):
		random.shuffle(self.torrent_providers)
		for i in self.torrent_providers:
			try: self.torrent_threads.put(self._get_torrent, self.item_information, i)
			except: log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

	def _is_playable_source(self, filtered=False):
		stats = self.sources_information['statistics']
		stats = stats['filtered'] if filtered else stats
		for stype in ["torrentsCached", "cloudFiles"]:
			if stats[stype]["total"] > 0:
				return True
		return False

	def _finalise_results(self):
		#log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		self.allow_provider_requests = False
		self._send_provider_stop_event()
		
		#PRINT TORRENTS
		#log(self.sources_information['allTorrents'].values())
		
		uncached = [i for i in self.sources_information['allTorrents'].values()
					if i['hash'] not in self.sources_information['cached_hashes']]

		# Check to see if we have any playable unfiltered sources, if not do cache assist
		if not self._is_playable_source():
			#if self.silent:
			#	g.notification(g.ADDON_NAME, g.get_language_string(30055))
			return uncached, [], self.item_information

		# Return sources list
		sources_list = (
			list(self.sources_information['torrentCacheSources'].values()) +
			self.sources_information['cloudFiles']
		)
		return uncached, sources_list, self.item_information

	def _get_imdb_info(self):
		if self.media_type == 'movie':
			# Confirm movie year against IMDb's information
			imdb_id = self.item_information['info'].get("imdb_id")
			if imdb_id is None:
				return
			import requests
			try:
				resp = self._imdb_suggestions(imdb_id)
				year = resp.get('y', self.item_information['info']['year'])
				if year is not None and year != self.item_information['info']['year']:
					self.item_information['info']['year'] = str(year)
			except requests.exceptions.ConnectionError as ce:
				log("Unable to obtain IMDB suggestions to confirm movie year", "warning")
				log(ce, "debug")

	@staticmethod
	def _imdb_suggestions(imdb_id):
		import json
		try:
			import requests
			from requests.adapters import HTTPAdapter
			from urllib3 import Retry
			session = requests.Session()
			retries = Retry(
				total=5, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504]
			)
			session.mount("https://", HTTPAdapter(max_retries=retries, pool_maxsize=100))

			resp = session.get('https://v2.sg.media-imdb.com/suggestion/t/{}.json'.format(imdb_id))
			resp = json.loads(resp.text)['d'][0]
			return resp
		except (ValueError, KeyError):
			log("Failed to get IMDB suggestion", "warning")
			return {}

	def _send_provider_stop_event(self):
		for provider in self.running_providers:
			if hasattr(provider, 'cancel_operations') and callable(provider.cancel_operations):
				provider.cancel_operations()

	#def _store_torrent_results(self, torrent_list):
	#	if len(torrent_list) == 0:
	#		return
	#	self.torrent_cache.add_torrent(self.item_information, torrent_list)

	def _init_providers(self):
		sys.path.append(tools.ADDON_USERDATA_PATH)
		try:
			if tools.ADDON_USERDATA_PATH not in sys.path:
				sys.path.append(tools.ADDON_USERDATA_PATH)
				providers = importlib.import_module("providers")
			else:
				providers = reload_module(importlib.import_module("providers"))
		except ValueError:
			log('No providers installed', 'warning')
			return

		#providers_dict = {'hosters': [], 
		#'torrent': [('providers.a4kScrapers.en.torrent', 'bitlord', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'bitsearch', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'btdig', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'cached', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'glo', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'kickass', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'lime', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'magnetdl', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'piratebay', 'a4kScrapers'), 
		##('providers.a4kScrapers.en.torrent', 'rutor', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'showrss', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'torrentdownload', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'torrentio', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'torrentz2', 'a4kScrapers'), 
		#('providers.a4kScrapers.en.torrent', 'yts', 'a4kScrapers')], 
		#'adaptive': []}
		#providers_dict = providers.get_relevant(self.language)
		#log(providers_dict)
		
		#providers_dict = get_providers_dict()
		providers_dict = get_providers()
		

		torrent_providers = providers_dict['torrent']
		for i in torrent_providers:
			tools.log(i)
		try:
			self.torrent_providers = torrent_providers
		except:
			log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

	def _exit_thread(self, provider_name):
		if provider_name in self.sources_information['statistics']['remainingProviders']:
			self.sources_information['statistics']['remainingProviders'].remove(provider_name)

	def _process_provider_torrent(self, torrent, provider_name, info):
		torrent['type'] = 'torrent'

		if not torrent.get('info'):
			torrent['info'] = tools.get_info(torrent['release_title'])

		if torrent.get("quality") not in tools.approved_qualities_set:
			torrent['quality'] = tools.get_quality(torrent['release_title'])

		torrent['hash'] = torrent.get('hash', self.hash_regex.findall(torrent['magnet'])[0]).lower()
		torrent['pack_size'], torrent['size'] = self._torrent_filesize(torrent, info)
		torrent['seeds'] = self._torrent_seeds(torrent)

		if 'provider_name_override' in torrent:
			torrent['provider'] = torrent['provider_name_override']
		else:
			torrent['provider'] = provider_name

	def _get_torrent(self, info, provider):
		# Extract provider name from Tuple
		provider_name = provider[1].upper()

		# Begin Scraping Torrent Sources
		try:
			self.sources_information['statistics']['remainingProviders'].append(provider_name)

			provider_module = importlib.import_module("{}.{}".format(provider[0], provider[1]))
			if not hasattr(provider_module, "sources"):
				log("Invalid provider, Source Class missing", "warning")
				return

			provider_source = provider_module.sources()

			if not hasattr(provider_source, self.media_type):
				log("Skipping provider: {} - Does not support {} types".format(provider_name, self.media_type),
					  "warning")
				return

			self.running_providers.append(provider_source)

			if self.media_type == 'episode':
				simple_info = tools._build_simple_show_info(info)

				torrent_results = provider_source.episode(simple_info, info)
			else:
				simple_info = tools._build_simple_movie_info(info)

				try:
					# new `simple_info`-based call
					torrent_results = provider_source.movie(simple_info, info)
				except TypeError:
					# legacy calls
					try:
						torrent_results = provider_source.movie(
							info['info']['title'],
							str(info['info']['year']),
							info['info'].get('imdb_id'),
						)
					except TypeError:
						torrent_results = provider_source.movie(
							info['info']['title'], str(info['info']['year'])
						)

			if torrent_results is None:
				self.sources_information['statistics']['remainingProviders'].remove(provider_name)
				return

			if self.canceled:
				return

			if len(torrent_results) > 0:
				# Begin filling in optional dictionary returns
				for torrent in torrent_results:
					self._process_provider_torrent(torrent, provider_name, info)

				torrent_results = {value['hash']: value for value in torrent_results}.values()
				start_time = time.time()

				# actually stores torrent in the db cache, later it checks RD cache. WRONG_Check Debrid Providers for cached copies
				#self._store_torrent_results(torrent_results)

				if self.canceled:
					return

				[self.sources_information['allTorrents'].update({torrent['hash']: torrent})
				 for torrent in torrent_results]

				# Check Debrid Providers for cached copies
				TorrentCacheCheck(self).torrent_cache_check([i for i in torrent_results], info)

				log("{} cache check took {} seconds".format(provider_name, time.time() - start_time), "debug")

			self.running_providers.remove(provider_source)

			return

		except:
			pass
		finally:
			self.sources_information['statistics']['remainingProviders'].remove(provider_name)


	def _user_cloud_inspection(self):
		self.sources_information['statistics']['remainingProviders'].append("Cloud Inspection")
		try:
			thread_pool = ThreadPool()
			if self.media_type == 'episode':
				simple_info = tools._build_simple_show_info(self.item_information)
			else:
				simple_info = tools._build_simple_movie_info(self.item_information)

			cloud_scrapers = [
				{"setting": "rd.cloudInspection", "provider": RealDebridCloudScraper,
				 "enabled": g.real_debrid_enabled()},
			]

			self._prem_terminate = False
			for cloud_scraper in cloud_scrapers:
				if cloud_scraper['enabled'] and g.get_bool_setting(cloud_scraper['setting']):
					self.cloud_scrapers.append(cloud_scraper['provider'])
					thread_pool.put(cloud_scraper['provider'](self._prem_terminate).get_sources, self.item_information,
									simple_info)

			sources = thread_pool.wait_completion()
			self.sources_information['cloudFiles'] = sources if sources else []

		finally:
			self.sources_information['statistics']['remainingProviders'].remove("Cloud Inspection")


	def _update_progress(self):
		log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		def _get_quality_count_dict(source_list):
			_4k = 0
			_1080p = 0
			_720p = 0
			_sd = 0

			for source in source_list:
				if source['quality'] == '4K':
					_4k += 1
				elif source['quality'] == '1080p':
					_1080p += 1
				elif source['quality'] == '720p':
					_720p += 1
				elif source['quality'] == 'SD':
					_sd += 1

			return {
				"4K": _4k, "1080p": _1080p, "720p": _720p, "SD": _sd,
				"total": _4k + _1080p + _720p + _sd
			}

		def _get_total_quality_dict(quality_dict_list):
			total_counter = Counter()

			for quality_dict in quality_dict_list:
				total_counter.update(quality_dict)

			return dict(total_counter)

		# Get qualities by source type and store result
		self.sources_information['statistics']['torrents'] = _get_quality_count_dict(
			list(self.sources_information['allTorrents'].values())
		)
		self.sources_information['statistics']['torrentsCached'] = _get_quality_count_dict(
			list(self.sources_information['torrentCacheSources'].values())
		)
		self.sources_information['statistics']['cloudFiles'] = _get_quality_count_dict(
			self.sources_information['cloudFiles']
		)

		self.sources_information['statistics']['totals'] = _get_total_quality_dict(
			[
				self.sources_information['statistics']['torrents'],
				self.sources_information['statistics']['cloudFiles']
			]
		)

		# Get qualities by source type after source filtering and store result
		self.sources_information['statistics']['filtered']['torrents'] = _get_quality_count_dict(
			self.source_sorter.filter_sources(list(self.sources_information['allTorrents'].values()))
		)
		self.sources_information['statistics']['filtered']['torrentsCached'] = _get_quality_count_dict(
			self.source_sorter.filter_sources(list(self.sources_information['torrentCacheSources'].values()))
		)
		self.sources_information['statistics']['filtered']['cloudFiles'] = _get_quality_count_dict(
			self.source_sorter.filter_sources(self.sources_information['cloudFiles'])
		)
		self.sources_information['statistics']['filtered']['totals'] = _get_total_quality_dict(
			[
				self.sources_information['statistics']['filtered']['torrentsCached'],
				self.sources_information['statistics']['filtered']['cloudFiles']
			]
		)

	def _get_pre_term_min(self):
		if self.media_type == 'episode':
			preem_min = tools.get_setting('preem.tvres', 'int') + 1
		else:
			preem_min = tools.get_setting('preem.movieres', 'int') + 1
		return preem_min

	def _get_filtered_count_by_resolutions(self, resolutions, quality_count_dict):
		return sum(quality_count_dict[resolution] for resolution in resolutions)

	
	def _prem_terminate(self):  # pylint: disable=method-hidden
		if self.canceled:
			log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			tools.PRE_TERM_BLOCK = True
			return True

		return False

	"""
		if not self.preem_enabled:
			return False
	

		if (
				self.preem_waitfor_cloudfiles and
				"Cloud Inspection" in self.sources_information['statistics']['remainingProviders']
		):
			return False

		if self.preem_cloudfiles and self.sources_information['statistics']['filtered']['cloudFiles']['total'] > 0:
			self.PRE_TERM_BLOCK = True
			return True
		if self.preem_adaptive_sources and self.sources_information['statistics']['filtered']['adaptive']['total'] > 0:
			self.PRE_TERM_BLOCK = True
			return True

		pre_term_log_string = 'Pre-emptively Terminated'

		try:
			if self.preem_type == 0 and self._get_filtered_count_by_resolutions(
					self.preem_resolutions, self.sources_information['statistics']['filtered']['torrentsCached']
			) >= self.preem_limit:
				log(pre_term_log_string, 'info')
				self.PRE_TERM_BLOCK = True
				return True
			if self.preem_type == 1 and self._get_filtered_count_by_resolutions(
				self.preem_resolutions, self.sources_information['statistics']['filtered']['hosters']
			) >= self.preem_limit:
				log(pre_term_log_string, 'info')
				self.PRE_TERM_BLOCK = True
				return True
			if self.preem_type == 2 and self._get_filtered_count_by_resolutions(
					self.preem_resolutions, self.sources_information['statistics']['filtered']['torrentsCached']
			) + self._get_filtered_count_by_resolutions(
				self.preem_resolutions, self.sources_information['statistics']['filtered']['hosters']
			) >= self.preem_limit:
					log(pre_term_log_string, 'info')
					self.PRE_TERM_BLOCK = True
					return True

		except (ValueError, KeyError, IndexError) as e:
			log("Error getting data for preterm determination: {}".format(repr(e)), "error")
			pass

		return False
	"""

	@staticmethod
	def _torrent_filesize(torrent, info):
		size = torrent.get('size', 0)
		#tools.log(torrent)
		pack_size = size
		try:
			size = float(size)
		except (ValueError, TypeError):
			return 0
		size = int(size)
		episode_size = torrent.get('episode_size', 0)
		if int(episode_size) > 0:
			size = episode_size
		elif torrent['package'] == 'show':
			size = size / int(info['show_episode_count'])
		elif torrent['package'] == 'season':
			size = size / int(info['episode_count'])
		return pack_size, size

	@staticmethod
	def _torrent_seeds(torrent):
		seeds = torrent.get('seeds')
		if seeds is None or isinstance(seeds, str) and not seeds.isdigit():
			return 0

		return int(torrent['seeds'])



class TorrentCacheCheck:
	def __init__(self, scraper_class):
		self.premiumize_cached = []
		self.realdebrid_cached = []
		self.all_debrid_cached = []
		self.threads = ThreadPool()

		self.episode_strings = None
		self.season_strings = None
		self.scraper_class = scraper_class
		self.rd_api = real_debrid.RealDebrid()

	def store_torrent(self, torrent):
		"""
		Pushes cached torrents back up to the calling class
		:param torrent: Torrent to return
		:type torrent: dict
		:return: None
		:rtype: None
		"""
		try:
			sources_information = self.scraper_class.sources_information
			# Compare and combine source meta
			tor_key = torrent['hash'] + torrent['debrid_provider']
			sources_information['cached_hashes'].add(torrent['hash'])
			if tor_key in sources_information['torrentCacheSources']:
				c_size = sources_information['torrentCacheSources'][tor_key].get('size', 0)
				n_size = torrent.get('size', 0)
				info = torrent.get('info', [])

				if c_size < n_size:
					sources_information['torrentCacheSources'].update({tor_key: torrent})

					sources_information['torrentCacheSources'][tor_key]['info'] \
						.extend([i for i in info if
								 i not in sources_information['torrentCacheSources'][tor_key].get('info', [])])
			else:
				sources_information['torrentCacheSources'].update({tor_key: torrent})
		except AttributeError:
			return

	def torrent_cache_check(self, torrent_list, info):
		"""
		Run cache check threads for given torrents
		:param torrent_list: List of torrents to check
		:type torrent_list: list
		:param info: Metadata on item to check
		:type info: dict
		:return: None
		:rtype: None
		"""
		self.threads.put(self._realdebrid_worker, copy.deepcopy(torrent_list), info)
		self.threads.wait_completion()

	def _realdebrid_worker(self, torrent_list, info):
		#try:
		if 1==1:
			hash_list = [i['hash'] for i in torrent_list]
			api = real_debrid.RealDebrid()
			real_debrid_cache = api.check_hash(hash_list)

			for i in torrent_list:
				try:
					if 'rd' not in real_debrid_cache.get(i['hash'], {}):
						continue
					if len(real_debrid_cache[i['hash']]['rd']) >= 1:
						if self.scraper_class.media_type == 'episode':
							self._handle_episode_rd_worker(i, real_debrid_cache, info)
						else:
							self._handle_movie_rd_worker(i, real_debrid_cache)
				except KeyError:
					pass
		#except Exception:
		#	#g.log_stacktrace()
		#	log(Exception)

	def _handle_movie_rd_worker(self, source, real_debrid_cache):
		for storage_variant in real_debrid_cache[source['hash']]['rd']:
			if not self.rd_api.is_streamable_storage_type(storage_variant):
				continue
			else:
				source['debrid_provider'] = 'real_debrid'
				self.store_torrent(source)

	def _handle_episode_rd_worker(self, source, real_debrid_cache, info):
		for storage_variant in real_debrid_cache[source['hash']]['rd']:

			if not self.rd_api.is_streamable_storage_type(storage_variant):
				continue

			if tools.get_best_episode_match('filename', storage_variant.values(), info):
				source['debrid_provider'] = 'real_debrid'
				self.store_torrent(source)
				break