# -*- coding: utf-8 -*-

#from __future__ import absolute_import, division, unicode_literals

import copy
import importlib
import os
import random
import re
import sys
import time
import json
from collections import OrderedDict, Counter

#from database.torrentCache import TorrentCache
from a4kscrapers_wrapper.thread_pool import ThreadPool
from a4kscrapers_wrapper import real_debrid
from a4kscrapers_wrapper import get_meta
from a4kscrapers_wrapper import source_tools
from a4kscrapers_wrapper import tools, distance
from a4kscrapers_wrapper.tools import log

import requests, json
#from a4kscrapers_wrapper import subs

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


def patch_ak4_core_find_url():

	patch_line_434 = """if self.caller_name in ['anirena'"""
	patch_update_434 = """        if self.caller_name in ['anirena', 'btdig', 'bt4g', 'btscene', 'glo', 'eztv', 'lime', 'rutor', 'torrentapi', 'torrentz2', 'showrss', 'scenerls', 'piratebay', 'magnetdl', 'torrentio', 'elfhosted']: ## PATCH
"""
	file_path = os.path.join(os.path.join(tools.ADDON_USERDATA_PATH, 'providerModules', 'a4kScrapers') , 'core.py')
	file1 = open(file_path, 'r')
	lines = file1.readlines()
	new_file = ''
	update_flag = False
	for idx, line in enumerate(lines):
		if '## PATCH' in str(line):
			update_flag = False
			break
		if patch_line_434 in str(line):
			new_file = new_file + patch_update_434
			update_flag = True
		else:
			new_file = new_file + line
	file1.close()
	if update_flag:
		file1 = open(file_path, 'w')
		file1.writelines(new_file)
		file1.close()


def patch_ak4_requests():
	#tools.log('NO_PATCH')
	#return
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

def curr_percent(rd_api):
	if rd_api.original_tot_bytes == 0:
		return
	curr_percent = round((rd_api.remaining_tot_bytes/rd_api.original_tot_bytes) * 100,2)
	if curr_percent < 0:
		curr_percent = 0
	os.environ['DOWNLOAD_CURR_PERCENT'] = str(int(curr_percent))
	tools.log('\n\n'+str(curr_percent)+'% total remaining on file')
	percent_done = 100 - curr_percent
	if percent_done == 0:
		return
	time_running = time.time() - rd_api.original_start_time
	seconds_per_percent = time_running / percent_done
	seconds_remaining = int(curr_percent * seconds_per_percent)
	minutes_remaining = int((curr_percent * seconds_per_percent) / 60)
	hours_remaining = round((curr_percent * seconds_per_percent) / (60*60),2)
	tools.log('\n\n'+str(seconds_remaining)+' seconds_remaining')
	tools.log('\n\n'+str(minutes_remaining)+' minutes_remaining')
	tools.log('\n\n'+str(hours_remaining)+' hours_remaining')
	tools.log('REMAINING_LINES_MAGNET_LIST =   '+str(rd_api.num_lines))
	if rd_api.xbmc_gui:
		import xbmcgui
		xbmcgui.Window(10000).setProperty('curr_percent', str(curr_percent))
		xbmcgui.Window(10000).setProperty('percent_done', str(percent_done))
		xbmcgui.Window(10000).setProperty('seconds_remaining', str(seconds_remaining))
		xbmcgui.Window(10000).setProperty('minutes_remaining', str(minutes_remaining))
		xbmcgui.Window(10000).setProperty('hours_remaining', str(hours_remaining))
		xbmcgui.Window(10000).setProperty('num_lines_remaining', str(rd_api.num_lines))

def run_downloader(magnet_list, download_path):
	rd_api = real_debrid.RealDebrid()
	curr_download = tools.get_download_line(magnet_list)
	start_time = time.time()
	active_magnets = []
	processed_files = []
	rd_api.original_start_time = time.time()
	try:
		rd_api.xbmc_gui = True
		import xbmcgui
	except:
		rd_api.xbmc_gui = False

	tot_bytes = 0
	with open(magnet_list, 'r') as fp:
		for line in fp:
			try: tot_bytes = tot_bytes + eval(line)['tot_bytes']
			except: continue
	original_tot_bytes = tot_bytes
	rd_api.original_tot_bytes = original_tot_bytes
	rd_api.remaining_tot_bytes = original_tot_bytes
	while time.time() < start_time + 300 and curr_download:
		tot_bytes = 0
		with open(magnet_list, 'r') as fp:
			num_lines = sum(1 for line in fp if line.rstrip())
			for line in fp:
				try: tot_bytes = tot_bytes + eval(line)['tot_bytes']
				except: continue
		log('REMAINING_LINES_MAGNET_LIST =   '+str(num_lines))
		rd_api.num_lines = num_lines
		curr_percent(rd_api)

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
			log(magnet)
			if 'too_many_active_downloads' in str(response):
				tools.log(response)
				tools.log('sleep_20')
				time.sleep(20)
				continue
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
					if tools.tools_stop_downloader == True:
						tools.tools_stop_downloader = False
						return
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
					if tools.tools_stop_downloader == True:
						tools.tools_stop_downloader = False
						return
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
					if tools.tools_stop_downloader == True:
						tools.tools_stop_downloader = False
						return

					start_time = time.time()
					curr_download = tools.get_download_line(magnet_list)
					tools.delete_download_line(magnet_list, curr_download)
					curr_download = tools.get_download_line(magnet_list)
			if download_type == 'uncached':
				processed_files = download_uncached_magnet(rd_api, download_path, curr_download, torr_id, torr_info, processed_files, magnet_list, True)
				if tools.tools_stop_downloader == True:
					tools.tools_stop_downloader = False
					return
				start_time = time.time()
				curr_download = tools.get_download_line(magnet_list)
			elif torr_info['status'] != 'downloaded':
				active_magnets.append(magnet)
				processed_files = download_uncached_magnet(rd_api, download_path, curr_download, torr_id, torr_info, processed_files, magnet_list, False)
				if tools.tools_stop_downloader == True:
					tools.tools_stop_downloader = False
					return
				start_time = time.time()
				curr_download = tools.get_download_line(magnet_list)
		else:
			if str(curr_download).strip()[:4] == 'http':
				download_http_rd_link(rd_api, download_path, curr_download)
				if tools.tools_stop_downloader == True:
					tools.tools_stop_downloader = False
					return
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
					if tools.tools_stop_downloader == True:
						tools.tools_stop_downloader = False
						return
					start_time = time.time()
					curr_download = tools.get_download_line(magnet_list)
				elif torr_info['status'] != 'downloaded':
					active_magnets.append(curr_download)
					processed_files = download_uncached_magnet(rd_api, download_path, curr_download, torr_id, torr_info, processed_files, magnet_list, False)
					if tools.tools_stop_downloader == True:
						tools.tools_stop_downloader = False
						return
					start_time = time.time()
					curr_download = tools.get_download_line(magnet_list)
				elif torr_info['status'] == 'downloaded':
					active_magnets.append(curr_download)
					processed_files = download_uncached_magnet(rd_api, download_path, curr_download, torr_id, torr_info, processed_files, magnet_list, True)
					if tools.tools_stop_downloader == True:
						tools.tools_stop_downloader = False
						return
					start_time = time.time()
					curr_download = tools.get_download_line(magnet_list)
		tools.log(processed_files)
		tools.log('sleep')
		time.sleep(10)
		curr_download = tools.get_download_line(magnet_list)
		sleep_count = 0
		if not curr_download:
			rd_api.num_lines = 0
			if rd_api.remaining_tot_bytes < 0:
				rd_api.remaining_tot_bytes = 0
			curr_percent(rd_api)
		while not curr_download:
			if sleep_count > 90:
				break
			tools.log('NO CONTENT SLEEP ' + str(100-sleep_count) + '  remaining')
			time.sleep(10)
			sleep_count = sleep_count + 10
			curr_download = tools.get_download_line(magnet_list)
			

def run_tv_search():
	try: 
		tv_show_title = input('Enter TV Show Title (MAGNET???):  ')
		if 'magnet:' in tv_show_title:
			custom = {'provider_name_override': 'CUSTOM', 'hash': 'CUSTOM', 'package': 'CUSTOM', 'release_title': 'CUSTOM', 'size': 0, 'seeds': 0, 'magnet': tv_show_title, 'type': 'CUSTOM', 'provider_name': 'CUSTOM', 'info': {'CUSTOM'}, 'quality': 'CUSTOM', 'pack_size': 0, 'provider': 'CUSTOM', 'debrid_provider': 'CUSTOM'}
			tv_show_title = input('Enter TV Show Title:  ')
		else:
			custom = None

		season_number = input('Enter Season Number:  ')
		episode_number = input('Enter Episode Number:  ')
	except:
		tools.log('EXIT')
		return
	meta = get_meta.get_episode_meta(season=season_number, episode=episode_number,tmdb=None, show_name=tv_show_title, year=None, interactive=True)
	info = meta['episode_meta']
	#tools.log(info)
	scrapper = Sources(info)

	if custom:
		uncached = []
		uncached.append(custom)
		sources_list = []
		sources_list.append(custom)
		item_information = info
	else:
		uncached, sources_list, item_information= Sources(info).get_sources()
	#uncached, sources_list, item_information = scrapper.get_sources()
	print(scrapper.progress)
	if len(uncached) == 0 and len(sources_list) == 0:
		for i in info['show_aliases']:
			info['show_title'] = i
			info['tvshow'] = i
			info['tvshowtitle'] = i
			info['info']['show_title'] = i
			info['info']['tvshow'] = i
			info['info']['tvshowtitle'] = i
			#tools.log(info)
			scrapper = Sources(info)
			uncached, sources_list, item_information = scrapper.get_sources()
			print(scrapper.progress)
			if len(uncached) == 0 and len(sources_list) == 0:
				continue
			else:
				break
	sources_list = tools.SourceSorter(item_information).sort_sources(sources_list)
	#sources_list, uncached = pack_sort(sources_list=sources_list, uncached=uncached, item_information=item_information)
	
	torrent_choices = tools.torrent_choices
	magnet_list = tools.get_setting('magnet_list')
	download_path = tools.get_setting('download_path')
	torrent_choices_test = []
	uncached_choice = {'provider_name_override': 'UNCACHED', 'hash': 'UNCACHED', 'package': 'UNCACHED', 'release_title': 'UNCACHED', 'size': 0, 'seeds': 0, 'magnet': 'UNCACHED', 'type': 'UNCACHED', 'provider_name': 'UNCACHED', 'info': {'UNCACHED'}, 'quality': 'UNCACHED', 'pack_size': 0, 'provider': 'UNCACHED', 'debrid_provider': 'UNCACHED'}
	if len(sources_list) == 0:
		tools.log('UNCACHED_NO_CACHED TORENTS FOUND!!')
		sources_list = []
		sources_list.append(uncached_choice)
		sources_list = sources_list + uncached
		uncached_choice = None
		for i in torrent_choices:
			if not 'uncached' in str(i).lower():
				torrent_choices_test.append(i)
	else:
		for i in torrent_choices:
			if 'uncached' in str(i).lower():
				torrent_choices_test.append(i)
	for i in torrent_choices_test:
		torrent_choices.pop(i)
	if uncached_choice:
		sources_list.append(uncached_choice)
	torrent = choose_torrent(sources_list)
	if not torrent:
		tools.log('EXIT')
		return

	if torrent['release_title'] == 'UNCACHED':
		torrent_choices = {
	'Add to downloader list (whole pack)': 4,
	'Add to downloader list (episode)': 5,
	#'Add to downloader list (whole pack + subtitles)': 6,
	#'Add to downloader list (episode + subtitles)': 7,
	'(Uncached) Add to RD (whole pack) ': 8,
	'(Uncached) Add to RD (individual files) ': 9
}

		tools.log('UNCACHED_NO_CACHED TORENTS FOUND!!')
		sources_list = uncached

		sources_list = tools.SourceSorter(item_information).sort_sources(sources_list)
		torrent = choose_torrent(sources_list)
		if torrent == None:
			return

	result = tools.selectFromDict(torrent_choices, 'Torrent')
	if not result:
		tools.log('EXIT')
		return
	rd_api = real_debrid.RealDebrid()

	if result == 1 or result == 8:#'Add to RD Cache (whole pack)': 1,#'(Uncached) Add to RD (whole pack) ': 8,
		tools.log(torrent)
		response = None
		while response == None:
			response = rd_api.add_magnet(torrent['magnet'])
			for idx, i in enumerate(sources_list):
				if i['hash'] == torrent['hash']:
					break
			sources_list.pop(idx)
			if response == None:
				torrent = choose_torrent(sources_list)
				response = None
				continue
			if response.get('error',False):
				tools.log(response)
				torrent = choose_torrent(sources_list)
				#result = tools.selectFromDict(torrent_choices, 'Torrent')
				#if not result:
				#	tools.log('EXIT')
				#	return
				response = None
		tools.log(response)
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)
		tools.log(torr_info)
	elif result == 2:#'Add to RD Cache + Unrestrict (whole pack)': 2,
		tools.log(torrent)
		#response = rd_api.add_magnet(torrent['magnet'])
		response = None
		while response == None:
			response = rd_api.add_magnet(torrent['magnet'])
			for idx, i in enumerate(sources_list):
				if i['hash'] == torrent['hash']:
					break
			sources_list.pop(idx)
			if response.get('error',False):
				tools.log(response)
				torrent = choose_torrent(sources_list)
				#result = tools.selectFromDict(torrent_choices, 'Torrent')
				#if not result:
				#	tools.log('EXIT')
				#	return
				response = None
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
		torr_info = rd_api.torrent_info_files(torr_info)
		tools.log(torr_info)
		#sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
		for i in torr_info['files_links']:
			unrestrict_link = i['unrestrict_link']
			result = input('Unrestrict %s:  ' % i['pack_path'])
			if result and result.strip() != '':
				if unrestrict_link == '':
					response2 = rd_api.add_magnet(torrent['magnet'])
					torr_id2 = response2['id']
					response2 = rd_api.torrent_select(torr_id2, i['pack_file_id'])
					torr_info2 = rd_api.torrent_info(torr_id2)
					unrestrict_link = torr_info2['links'][0]
					tools.log(torr_info2)
					download_link = rd_api.resolve_hoster(unrestrict_link)
					download_id = rd_api.UNRESTRICT_FILE_ID
					log(download_link, download_id)
				else:
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
			#try: result = input('Unrestrict %s:  ' % i['file'])
			#except: result = input('Unrestrict %s:  ' % i['path'])
			try: print('Unrestrict %s:  ' % i['file'])
			except: print('Unrestrict %s:  ' % i['path'])
			if 1==1:
				time.sleep(1)
				response = rd_api.torrent_select(torr_id, i['id'])
				response = rd_api.add_magnet(torrent['magnet'])
				try: 
					torr_id = response['id']
				except: 
					tools.log(response)
					continue
				torr_info = rd_api.torrent_info(torr_id)
		#response = rd_api.add_magnet(torrent['magnet'])
		#tools.log(response)
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		#torr_info = rd_api.torrent_info(torr_id)
	elif result == 4:#'Add to downloader list (whole pack)': 4,

		tools.log(torrent)
		#response = rd_api.add_magnet(torrent['magnet'])
		response = None
		while response == None:
			response = rd_api.add_magnet(torrent['magnet'])
			for idx, i in enumerate(sources_list):
				if i['hash'] == torrent['hash']:
					break
			sources_list.pop(idx)
			if response == None:
				torrent = choose_torrent(sources_list)
				response = None
				continue
			if response.get('error',False):
				tools.log(response)
				torrent = choose_torrent(sources_list)
				#result = tools.selectFromDict(torrent_choices, 'Torrent')
				#if not result:
				#	tools.log('EXIT')
				#	return
				response = None
		tools.log(response)
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)
		

		meta['download_type'] = 'pack'
		#meta['download_type'] = 'episode'

		meta['magnet'] = torrent['magnet']

		#tools.log(torr_info)

		#for i in torr_info['links']:
		#	unrestrict_link = i
		#	download_link = rd_api.resolve_hoster(unrestrict_link)
		#	download_id = rd_api.UNRESTRICT_FILE_ID
		#	log(download_link, download_id)
		download_link, new_meta = cloud_get_ep_season(rd_api, meta, torr_id, torr_info)
		if download_link == '' or download_link == None:
			tools.log('UNCACHED')
			meta['filename'] = ''
			meta['filename_without_ext'] = ''
			meta['filesize'] = ''
			meta['filehash'] = ''
			meta['url'] = ''
			meta['release_title'] = torrent['release_title']
			meta['CURR_LABEL'] =  torrent['release_title']
			meta['package'] = torrent['package']
			meta['file_name'] = ''

			magnet_list = tools.get_setting('magnet_list')
			file1 = open(magnet_list, "a") 
			file1.write(str(meta))
			file1.write("\n")
			file1.close()
			return
			
		stream_link = download_link
		#file_name = unquote(stream_link).split('/')[-1]
		file_name = os.path.basename(stream_link)
		#filename_without_ext = file_name.replace('.'+file_name.split('.')[-1],'')
		filename_without_ext = os.path.splitext(os.path.basename(stream_link))[0]
		#file_name_ext = file_name.replace(filename_without_ext,'')
		file_name_ext = os.path.splitext(os.path.basename(stream_link))[1]
		tot_bytes = 0
		for i in torr_info['files']:
			if file_name_ext in i['path'] and i['selected'] == 1:
				tot_bytes = tot_bytes + i['bytes']
		meta['tot_bytes'] = tot_bytes

		#if filename_without_ext == g.CURR_SOURCE['release_title'].lower() or filename_without_ext in g.CURR_SOURCE['release_title'].lower():
		#	file_name = g.CURR_SOURCE['release_title'] + file_name_ext
		#	filename_without_ext = g.CURR_SOURCE['release_title']
		subs_filename = filename_without_ext + '.srt'

		#meta['download_type'] = 'movie'
		meta['filename'] = file_name
		meta['filename_without_ext'] = filename_without_ext
		meta['filesize'] = ''
		meta['filehash'] = ''
		meta['url'] = stream_link
		#meta['magnet'] = g.CURR_SOURCE['magnet']
		meta['release_title'] = torrent['release_title']
		meta['CURR_LABEL'] =  torrent['release_title']
		meta['package'] = torrent['package']
		meta['file_name'] = file_name

		#tools.log(meta)

		magnet_list = tools.get_setting('magnet_list')
		file1 = open(magnet_list, "a") 
		file1.write(str(meta))
		file1.write("\n")
		file1.close()




	elif result == 5:#'Add to downloader list (episode)': 5,
		meta['download_type'] = 'episode'
		meta['magnet'] = torrent['magnet']

		response = rd_api.add_magnet(torrent['magnet'])
		#tools.log(response)
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)
		#tools.log(torr_info)

		download_link, new_meta = cloud_get_ep_season(rd_api, meta, torr_id, torr_info)
		
		tools.log(torrent)
		tools.log(download_link)
		#tools.log(new_meta)

		magnet_list = tools.get_setting('magnet_list')

		stream_link = download_link
		file_name = os.path.basename(stream_link)
		tot_bytes = 0
		for i in torr_info['files']:
			if unquote(file_name) in unquote(i['path']) and i['selected'] == 1:
				tot_bytes = tot_bytes + i['bytes']
		meta['tot_bytes'] = tot_bytes

		filename_without_ext = os.path.splitext(os.path.basename(stream_link))[0]
		file_name_ext = os.path.splitext(os.path.basename(stream_link))[1]
		subs_filename = filename_without_ext + '.srt'

		meta['filename'] = file_name
		meta['filename_without_ext'] = filename_without_ext
		meta['filesize'] = ''
		meta['filehash'] = ''
		meta['url'] = stream_link
		#meta['magnet'] = g.CURR_SOURCE['magnet']
		meta['release_title'] = torrent['release_title']
		meta['CURR_LABEL'] =  torrent['release_title']
		meta['package'] = torrent['package']
		meta['file_name'] = file_name

		#tools.log(meta)

		file1 = open(magnet_list, "a") 
		file1.write(str(meta))
		file1.write("\n")
		file1.close()

	elif result == 6:#'Add to downloader list (whole pack + subtitles)': 6,
		tools.log(torrent)
		meta['download_type'] = 'episode'
		#meta['download_type'] = 'movie'

		meta['magnet'] = torrent['magnet']
		response = rd_api.add_magnet(torrent['magnet'])
		#tools.log(response)
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)

		#tools.log(torrent)
		magnet_list = tools.get_setting('magnet_list')
		for i in meta['tvmaze_seasons']['episodes']:
			ep_meta = get_meta.get_episode_meta(season=i['season'],episode=i['episode'],tmdb=i['tmdb'])
			ep_meta['download_type'] = 'episode'
			ep_meta['magnet'] = torrent['magnet']
			download_link, new_ep_meta = cloud_get_ep_season(rd_api, ep_meta, torr_id, torr_info)

			tools.log(download_link)
			tools.log(new_ep_meta)

			stream_link = download_link
			file_name = os.path.basename(stream_link)
			tot_bytes = 0
			for i in torr_info['files']:
				if unquote(file_name) in unquote(i['path']) and i['selected'] == 1:
					tot_bytes = tot_bytes + i['bytes']
			ep_meta['tot_bytes'] = tot_bytes
			filename_without_ext = os.path.splitext(os.path.basename(stream_link))[0]
			file_name_ext = os.path.splitext(os.path.basename(stream_link))[1]
			subs_filename = filename_without_ext + '.srt'

			ep_meta['filename'] = file_name
			ep_meta['filename_without_ext'] = filename_without_ext
			ep_meta['filesize'] = ''
			ep_meta['filehash'] = ''
			ep_meta['url'] = stream_link
			#meta['magnet'] = g.CURR_SOURCE['magnet']
			ep_meta['release_title'] = torrent['release_title']
			ep_meta['CURR_LABEL'] =  torrent['release_title']
			ep_meta['package'] = torrent['package']
			ep_meta['file_name'] = file_name

			#tools.log(ep_meta)

			file1 = open(magnet_list, "a") 
			file1.write(str(ep_meta))
			file1.write("\n")
			file1.close()


	elif result == 7:#'Add to downloader list (episode + subtitles)': 7,
		meta['download_type'] = 'episode'
		meta['magnet'] = torrent['magnet']

		response = rd_api.add_magnet(torrent['magnet'])
		#tools.log(response)
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)
		#tools.log(torr_info)

		download_link, new_meta = cloud_get_ep_season(rd_api, meta, torr_id, torr_info)
		
		tools.log(torrent)
		tools.log(download_link)
		tools.log(new_meta)

		magnet_list = tools.get_setting('magnet_list')

		stream_link = download_link
		file_name = os.path.basename(stream_link)
		tot_bytes = 0
		for i in torr_info['files']:
			if unquote(file_name) in unquote(i['path']) and i['selected'] == 1:
				tot_bytes = tot_bytes + i['bytes']
		meta['tot_bytes'] = tot_bytes

		filename_without_ext = os.path.splitext(os.path.basename(stream_link))[0]
		file_name_ext = os.path.splitext(os.path.basename(stream_link))[1]
		subs_filename = filename_without_ext + '.srt'

		meta['filename'] = file_name
		meta['filename_without_ext'] = filename_without_ext
		meta['filesize'] = ''
		meta['filehash'] = ''
		meta['url'] = stream_link
		#meta['magnet'] = g.CURR_SOURCE['magnet']
		meta['release_title'] = torrent['release_title']
		meta['CURR_LABEL'] =  torrent['release_title']
		meta['package'] = torrent['package']
		meta['file_name'] = file_name

		tools.log(meta)

		file1 = open(magnet_list, "a") 
		file1.write(str(meta))
		file1.write("\n")
		file1.close()

	return

def run_keyword_search():
	info = {'mediatype': 'movie', 'download_type': 'movie', 'episode': '', 'imdb_id': 'tt', 'is_movie': False, 'is_tvshow': False, 'media_type': 'movie', 'season': '', 'title': None, 'tmdb_id': None, 'tvshow': '', 'tvshow_year': '', 'year': '', 'info': {'mediatype': 'movie', 'episode': '', 'imdb_id': 'tt', 'is_movie': False, 'is_tvshow': False, 'media_type': 'movie', 'season': '', 'title': None, 'tmdb_id': None, 'tvshow': '', 'tvshow_year': '', 'year': ''}}
	movie_title = input('Enter Search Term:  ')
	info['title'] = movie_title
	info['info']['title'] = movie_title
	run_movie_search(info)

def run_movie_search(info=None):
	custom = None
	if info == None:
		try: 
			movie_title = input('Enter Movie Title:  ')
		except:
			tools.log('EXIT')
			return
		if 'magnet:' in movie_title:
			custom = {'provider_name_override': 'CUSTOM', 'hash': 'CUSTOM', 'package': 'CUSTOM', 'release_title': 'CUSTOM', 'size': 0, 'seeds': 0, 'magnet': movie_title, 'type': 'CUSTOM', 'provider_name': 'CUSTOM', 'info': {'CUSTOM'}, 'quality': 'CUSTOM', 'pack_size': 0, 'provider': 'CUSTOM', 'debrid_provider': 'CUSTOM'}
			movie_title = input('Enter Movie Title:  ')
		else:
			custom = None

		meta = get_meta.get_movie_meta(movie_name=movie_title,year=None, interactive=True)
		info = meta
	else:
		meta = info


	if custom:
		uncached = None
		sources_list = []
		sources_list.append(custom)
		item_information = info
	else:
		uncached, sources_list, item_information= Sources(info).get_sources()
	torrent_choices = tools.torrent_choices
	torrent_choices_original = str(tools.torrent_choices)

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
	sources_list = tools.SourceSorter(item_information).sort_sources(sources_list)
	sources_list.append({'provider_name_override': 'UNCACHED', 'hash': 'UNCACHED', 'package': 'UNCACHED', 'release_title': 'UNCACHED', 'size': 0, 'seeds': 0, 'magnet': 'UNCACHED', 'type': 'UNCACHED', 'provider_name': 'UNCACHED', 'info': {'UNCACHED'}, 'quality': 'UNCACHED', 'pack_size': 0, 'provider': 'UNCACHED', 'debrid_provider': 'UNCACHED'})
	torrent = choose_torrent(sources_list)
	
	if torrent == None:
		return

	if torrent['release_title'] == 'UNCACHED':
		torrent_choices = {'Add to downloader list (whole pack)': 4,
	'Add to downloader list (whole pack + subtitles)': 6,
	'(Uncached) Add to RD (whole pack) ': 8,
}
		tools.log('UNCACHED_NO_CACHED TORENTS FOUND!!')
		sources_list = uncached

		sources_list = tools.SourceSorter(item_information).sort_sources(sources_list)
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

		response = rd_api.add_magnet(torrent['magnet'])
		#tools.log(response)
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)
		#tools.log(torr_info)

		tot_bytes = 0
		for i in torr_info['links']:
			unrestrict_link = i
			download_link = rd_api.resolve_hoster(unrestrict_link)
			download_id = rd_api.UNRESTRICT_FILE_ID
			log(download_link, download_id)
			for i in torr_info['files']:
				if i['selected'] == 1:
					tot_bytes = tot_bytes + i['bytes']
		meta['tot_bytes'] = tot_bytes

		stream_link = download_link
		#file_name = unquote(stream_link).split('/')[-1]
		file_name = os.path.basename(stream_link)


		#filename_without_ext = file_name.replace('.'+file_name.split('.')[-1],'')
		filename_without_ext = os.path.splitext(os.path.basename(stream_link))[0]
		#file_name_ext = file_name.replace(filename_without_ext,'')
		file_name_ext = os.path.splitext(os.path.basename(stream_link))[1]
		#if filename_without_ext == g.CURR_SOURCE['release_title'].lower() or filename_without_ext in g.CURR_SOURCE['release_title'].lower():
		#	file_name = g.CURR_SOURCE['release_title'] + file_name_ext
		#	filename_without_ext = g.CURR_SOURCE['release_title']
		subs_filename = filename_without_ext + '.srt'

		#meta['download_type'] = 'movie'
		meta['filename'] = file_name
		meta['filename_without_ext'] = filename_without_ext
		meta['filesize'] = ''
		meta['filehash'] = ''
		meta['url'] = stream_link
		#meta['magnet'] = g.CURR_SOURCE['magnet']
		meta['release_title'] = torrent['release_title']
		meta['CURR_LABEL'] =  torrent['release_title']
		meta['package'] = torrent['package']
		if meta['CURR_LABEL'] == 'CUSTOM':
			meta['CURR_LABEL'] = file_name
			meta['package'] = file_name
		meta['file_name'] = file_name

		tools.log(meta)

		magnet_list = tools.get_setting('magnet_list')
		file1 = open(magnet_list, "a") 
		file1.write(str(meta))
		file1.write("\n")
		file1.close()


	elif result == 6:#'Add to downloader list (whole pack + subtitles)': 6,
		tools.log(torrent)

		meta['download_type'] = 'pack'
		meta['download_type'] = 'movie'

		meta['magnet'] = torrent['magnet']

		response = rd_api.add_magnet(torrent['magnet'])
		#tools.log(response)
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)
		#tools.log(torr_info)

		tot_bytes = 0
		for i in torr_info['links']:
			unrestrict_link = i
			download_link = rd_api.resolve_hoster(unrestrict_link)
			download_id = rd_api.UNRESTRICT_FILE_ID
			log(download_link, download_id)
			for i in torr_info['files']:
				if i['selected'] == 1:
					tot_bytes = tot_bytes + i['bytes']
		meta['tot_bytes'] = tot_bytes
		stream_link = download_link
		#file_name = unquote(stream_link).split('/')[-1]
		file_name = os.path.basename(stream_link)
		#filename_without_ext = file_name.replace('.'+file_name.split('.')[-1],'')
		filename_without_ext = os.path.splitext(os.path.basename(stream_link))[0]
		#file_name_ext = file_name.replace(filename_without_ext,'')
		file_name_ext = os.path.splitext(os.path.basename(stream_link))[1]
		#if filename_without_ext == g.CURR_SOURCE['release_title'].lower() or filename_without_ext in g.CURR_SOURCE['release_title'].lower():
		#	file_name = g.CURR_SOURCE['release_title'] + file_name_ext
		#	filename_without_ext = g.CURR_SOURCE['release_title']
		subs_filename = filename_without_ext + '.srt'

		#meta['download_type'] = 'movie'
		meta['filename'] = file_name
		meta['filename_without_ext'] = filename_without_ext
		meta['filesize'] = ''
		meta['filehash'] = ''
		meta['url'] = stream_link
		#meta['magnet'] = g.CURR_SOURCE['magnet']
		meta['release_title'] = torrent['release_title']
		meta['CURR_LABEL'] =  torrent['release_title']
		meta['package'] = torrent['package']
		if meta['CURR_LABEL'] == 'CUSTOM':
			meta['CURR_LABEL'] = file_name
			meta['package'] = file_name
		meta['file_name'] = file_name

		tools.log(meta)

		magnet_list = tools.get_setting('magnet_list')
		file1 = open(magnet_list, "a") 
		file1.write(str(meta))
		file1.write("\n")
		file1.close()

	return

def choose_torrent(sources_list):
	sources_dict = {}
	for idx, i in enumerate(sources_list):
		source_name = '%s SIZE=%s SEEDS=%s PACK=%s   %s' % (i['release_title'], i['size'], i['seeds'], i['pack_size'], i['info'])
		source_name = str("{:<90}		{:<10}	{:<10}	{:<10}	{:<10}".format(str(i['release_title'][:95]), 'SIZE='+str(int(i['size'])), 'SEEDS='+str(i['seeds']), 'PACK='+str(int(i['pack_size'])), str(i['info'])))
		#log(i, '\n')
		sources_dict[source_name] = str(idx)

	result = tools.selectFromDict(sources_dict, 'Torrent')
	if 'magnet:' in result:
		custom =  {'provider_name_override': 'CUSTOM', 'hash': 'CUSTOM', 'package': 'CUSTOM', 'release_title': 'CUSTOM', 'size': 0, 'seeds': 0, 'magnet': result, 'type': 'CUSTOM', 'provider_name': 'CUSTOM', 'info': {'CUSTOM'}, 'quality': 'CUSTOM', 'pack_size': 0, 'provider': 'CUSTOM', 'debrid_provider': 'CUSTOM'}
		return custom
	else:
		try: torrent = sources_list[int(result)]
		except: return None
		#log(torrent)
		return torrent


def cloud_get_ep_season(rd_api, meta, torr_id, torr_info):
	from source_tools import get_guess
	torr_info = rd_api.torrent_info_files(torr_info)
	#tools.log(torr_info)
	sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
	info = meta['episode_meta']
	simple_info = tools._build_simple_show_info(info)

	#tools.log(info)
	daily_show_flag = False
	if info['episode_air_date'][-2:] in str(info.get('title','')) and info['episode_air_date'][:4] in str(info.get('title','')):
		import datetime
		if datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%B %d, %Y') in info['title']:
			daily_show_flag = True
		if datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%Y.%m.%d') in info['title']:
			daily_show_flag = True

	if daily_show_flag:
		info_keyword = {'mediatype': 'movie', 'download_type': 'movie', 'episode': '', 'imdb_id': 'tt', 'is_movie': False, 'is_tvshow': False, 'media_type': 'movie', 'season': '', 'title': None, 'tmdb_id': None, 'tvshow': '', 'tvshow_year': '', 'year': '', 'info': {'mediatype': 'movie', 'episode': '', 'imdb_id': 'tt', 'is_movie': False, 'is_tvshow': False, 'media_type': 'movie', 'season': '', 'title': None, 'tmdb_id': None, 'tvshow': '', 'tvshow_year': '', 'year': ''}}

		info_keyword['title'] = '%s %s' % (info['tvshow'], info['episode_air_date'].replace('-','.'))
		info_keyword['info']['title'] = info_keyword['title']
		info['info']['title'] = info['info']['title'].replace(datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%B %d, %Y'), datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%Y.%m.%d'))
		info['title'] = info['info']['title']
		meta['episode_meta'] = info
		simple_info['show_aliases'] = info['info']['show_aliases']
		simple_info['episode_title'] = info['info']['title']
		#tools.log(meta['episode_meta'])

	result_dict = source_tools.match_episodes_season_pack(meta, sorted_torr_info)
	#tools.log(result_dict)

	download_link = None
	new_meta = meta
	#tools.log(simple_info, meta['episode_meta']['title'])
	#tools.log(result_dict['concat'][0]['meta_source'])
	try: meta_source = result_dict['concat'][0]['meta_source']
	except: meta_source = None
	if meta_source == None:
		return download_link, new_meta
	tvmaze_adjusted_eps = []
	jdx = 0
	#if meta_source == 'tmdb_seasons' and len(meta['tmdb_seasons']['episodes']) < len(meta['tvmaze_seasons']['episodes']):
	#tools.log(meta_source)
	#tools.log(meta['tmdb_seasons']['episodes'])
	#tools.log(meta['tvmaze_seasons']['episodes'])
	result_dict_alt_ep_num_check = False
	if type(result_dict['alt_ep_num'][-1]) == 'list':
		for i in result_dict['alt_ep_num'][-1]:
			if type(result_dict['episode_numbers'][-1]) == 'list':
				for j in list(result_dict['episode_numbers'][-1]):
					if i < j:
						result_dict_alt_ep_num_check = True
			elif type(result_dict['alt_ep_num'][-1]) == 'int':
				if i < result_dict['alt_ep_num'][-1]:
					result_dict_alt_ep_num_check = True
	elif type(result_dict['alt_ep_num'][-1]) == 'int':
		if type(result_dict['episode_numbers'][-1]) == 'list':
			for j in list(result_dict['episode_numbers'][-1]):
				if result_dict['alt_ep_num'][-1] < j:
					result_dict_alt_ep_num_check = True
		elif type(result_dict['episode_numbers'][-1]) == 'int':
			if result_dict['alt_ep_num'][-1] < result_dict['episode_numbers'][-1]:
				result_dict_alt_ep_num_check = True
	if meta_source == 'tmdb_seasons' and (int(meta['tmdb_seasons']['episodes'][-1]['episode']) < int(meta['tvmaze_seasons']['episodes'][-1]['episode']) or result_dict_alt_ep_num_check ):
		for idx, i in enumerate(meta['tvmaze_seasons']['episodes']):
			try:
				try: curr_tmdb_name = meta['tmdb_seasons']['episodes'][idx]['name']
				except: curr_tmdb_name = ''

				if result_dict['alt_ep_num'][-1] < result_dict['episode_numbers'][-1]:
					i['name'] = i['name'].split(', Part ')[0]
					#try: ep_title_part_test = int(curr_tmdb_name.split(' ')[-1].replace(')','').replace('(',''))
					#except: ep_title_part_test = 0
					#if ep_title_part_test > 0:
					#	curr_tmdb_name = curr_tmdb_name.replace(' '+curr_tmdb_name.split(' ')[-1],'')
					#try: ep_title_part_test = int(meta['tmdb_seasons']['episodes'][jdx]['name'].split(' ')[-1].replace(')','').replace('(',''))
					#except: ep_title_part_test = 0
					#if ep_title_part_test > 0:
					#	meta['tmdb_seasons']['episodes'][jdx]['name'] = meta['tmdb_seasons']['episodes'][jdx]['name'].replace(' '+meta['tmdb_seasons']['episodes'][jdx]['name'].split(' ')[-1],'')
				#tools.log(i['name'], 'i[name]')
				#tools.log(curr_tmdb_name, 'curr_tmdb_name')
				#tools.log(meta['tmdb_seasons']['episodes'][jdx]['name'], 'jdx_name')
				#tools.log(distance.jaro_similarity(i['name'],meta['tmdb_seasons']['episodes'][jdx]['name']), curr_tmdb_name)


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
								#log(i['name'], jdx+1,2323232)
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
	#tools.log(tvmaze_adjusted_eps, simple_info)
	try: 
		original_ep_no = int(simple_info['episode_number'])
	except ValueError: 
		original_ep_no = 0
		simple_info['episode_number'] = 0
	#tools.log(original_ep_no, 'original_ep_no')
	#tools.log(result_dict['episode_numbers'], 'result_dict[episode_numbers]')
	for i in result_dict['episode_numbers']:
		if not int(i) in tvmaze_adjusted_eps:
			tvmaze_adjusted_eps.append(int(i))
	tvmaze_adjusted_eps = sorted(tvmaze_adjusted_eps)
	#try: simple_info['episode_number'] = str(tvmaze_adjusted_eps[ int(simple_info['episode_number'])-1 ])
	#except: pass
	try: simple_info['episode_number'] = str(tvmaze_adjusted_eps[ int(simple_info['episode_number'])-tvmaze_adjusted_eps[0] ])
	except: pass

	#tools.log(simple_info['episode_number'])
	#tools.log(tvmaze_adjusted_eps)
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
	#log(simple_info['episode_number'])
	#log(result_dict)

	test_ep_adjust = 0
	counted = []
	for ijx, ij in enumerate(result_dict['alt_ep_num']):
		#tools.log(ij,'alt_ep_num')
		if ij in counted:
			continue
		if ijx > 0 and result_dict['alt_ep_num'][ijx-1] == ij:
			test_ep_adjust = test_ep_adjust + 1 
			counted.append(ij)
		elif ijx == 0 and len(result_dict['alt_ep_num']) >= ijx+2:
			if result_dict['alt_ep_num'][ijx+1] == ij:
				test_ep_adjust = test_ep_adjust + 1 
				counted.append(ij)
		if ij == test_ep:
			break
	test_ep = test_ep - test_ep_adjust
	if test_ep_adjust > 0:
		log('test_ep_adjust - %s, test_ep = %s' % (test_ep_adjust, test_ep))


	for ijx, ij in enumerate(result_dict['alt_ep_num']):
		torr_ep_index = ijx
		if 'list' in str(type(ij)):
			for ijix, iji in enumerate(ij):
				if int(iji) == int(test_ep):
					try: test = result_dict['episode_numbers'][ijx+ ijix]
					except: test = 0
					if int(iji) != int(test):
						if int(iji) == int(result_dict['episode_numbers'][ijx - ijix]) or int(iji) != int(test):
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
					new_info = meta[meta_source]['episodes'][int(result_dict['episode_numbers'][torr_ep_index])-1]
					#tools.log(new_info)
					new_meta = get_meta.get_episode_meta(season=new_info['season'],episode=new_info['episode'],tmdb=new_info['tmdb'])
					break
			#if result_dict['alt_ep_num'][ijx-1] == result_dict['alt_ep_num'][ijx] and int(test_ep) == result_dict['alt_ep_num'][ijx+1]:
			#	if result_dict['alt_ep_num'][-1] < result_dict['episode_numbers'][-1]:
			#		#torr_ep_index = torr_ep_index -1
			#		if int(ij) != int(result_dict['episode_numbers'][ijx]):
			#			messed_up_numbering_flag = True
			#			new_info = meta[meta_source]['episodes'][int(result_dict['episode_numbers'][torr_ep_index])-1]
			#			tools.log(new_info)
			#			test_ep = int(ij)
			#			new_meta = get_meta.get_episode_meta(season=new_info['season'],episode=new_info['episode'],tmdb=new_info['tmdb'])
			#			break
			#		#tools.log('ijx',result_dict['alt_ep_num'][ijx])
			#		#tools.log('torr_ep_index',result_dict['alt_ep_num'][torr_ep_index])
			#		#tools.log('simple_info',simple_info['episode_number'])
			#		#tools.log('test_ep',test_ep)
			#		#tools.log('ij',ij)
			#		#tools.log('ijx',result_dict['episode_numbers'][ijx])

	#tools.log('test_ep',test_ep)
	if messed_up_numbering_flag == True:
		for ijx, ij in enumerate(result_dict['alt_ep_num']):
			try: 
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
			except: 
				for eps in ij:
					if int(eps) == int(test_ep):
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
			try: 
				if int(ij) == int(simple_info['episode_number']):
					#tools.log(simple_info, ij)
					#tools.log(simple_info['episode_number'], ijx)
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
			except: 
				for eps in ij:
					if int(eps) == int(simple_info['episode_number']):
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

	#if not download_link:
	#	rd_api.delete_torrent(torr_id)
	return download_link, new_meta

def pack_sort(sources_list, uncached, item_information):
	new_sources_list = []
	sources_list_single = []
	sources_list_pack = []
	for i in sources_list:
		if i['package'] == 'single':
			sources_list_single.append(i)
		else:
			sources_list_pack.append(i)
	sources_list_pack = tools.SourceSorter(item_information).sort_sources(sources_list_pack)
	sources_list_single = tools.SourceSorter(item_information).sort_sources(sources_list_single)
	for x in tools.approved_qualities:
		for i in sources_list_pack:
			if i['quality'] == x:
				new_sources_list.append(i)
		for i in sources_list_single:
			if i['quality'] == x:
				new_sources_list.append(i)
	sources_list = new_sources_list

	new_uncached = []
	uncached_single = []
	uncached_pack = []
	for i in uncached:
		if i['package'] == 'single':
			uncached_single.append(i)
		else:
			uncached_pack.append(i)
	uncached_pack = tools.SourceSorter(item_information).sort_sources(uncached_pack)
	uncached_single = tools.SourceSorter(item_information).sort_sources(uncached_single)
	for x in tools.approved_qualities:
		for i in uncached_pack:
			if i['quality'] == x:
				new_uncached.append(i)
		for i in uncached_single:
			if i['quality'] == x:
				new_uncached.append(i)
	uncached = new_uncached
	#sources_list = tools.SourceSorter(item_information).sort_sources(sources_list)
	#uncached = tools.SourceSorter(info).sort_sources(uncached)
	return sources_list, uncached

def auto_scrape_rd(meta, select_dialog=False, unrestrict=False):
	rd_api = real_debrid.RealDebrid()
	if meta.get('download_type',False) == 'movie':
		info = meta
		download_type = meta.get('download_type',False)
		meta['episode_meta'] = {}
		daily_show_flag = False
	else:
		info = meta['episode_meta']
		download_type = meta.get('download_type',False)
		daily_show_flag = False
		if info['episode_air_date'][-2:] in info['title'] and info['episode_air_date'][:4] in info['title']:
			import datetime
			if datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%B %d, %Y') in info['title']:
				daily_show_flag = True
			if datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%Y.%m.%d') in info['title']:
				daily_show_flag = True


	special_flag = False
	special_meta = None
	if meta['episode_meta'].get('special',False) == True:
		special_flag = True
		special_movie_name = '%s: %s' % (info['tvshow'],info['title'])
		special_meta = get_meta.get_movie_meta(movie_name=special_movie_name,year=info['year'])
		if special_meta:
			special_simple_info = tools._build_simple_movie_info(special_meta)

	#tools.log(meta)
	#tools.log(info)
	if daily_show_flag:
		info_keyword = {'mediatype': 'movie', 'download_type': 'movie', 'episode': '', 'imdb_id': 'tt', 'is_movie': False, 'is_tvshow': False, 'media_type': 'movie', 'season': '', 'title': None, 'tmdb_id': None, 'tvshow': '', 'tvshow_year': '', 'year': '', 'info': {'mediatype': 'movie', 'episode': '', 'imdb_id': 'tt', 'is_movie': False, 'is_tvshow': False, 'media_type': 'movie', 'season': '', 'title': None, 'tmdb_id': None, 'tvshow': '', 'tvshow_year': '', 'year': ''}}

		info_keyword['title'] = '%s %s' % (info['tvshow'], info['episode_air_date'].replace('-','.'))
		info_keyword['info']['title'] = info_keyword['title']
		info['info']['title'] = info['info']['title'].replace(datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%B %d, %Y'), datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%Y.%m.%d'))
		info['title'] = info['info']['title']
		meta['episode_meta'] = info
		uncached, sources_list, item_information = Sources(info_keyword).get_sources()
		tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		#tools.log(meta['episode_meta'])
		#tools.log(sources_list)
	else:
		#uncached, sources_list, item_information = Sources(info).get_sources()
		scrapper = Sources(info)
		uncached, sources_list, item_information = scrapper.get_sources()
		print(scrapper.progress)
		if meta.get('download_type',False) == 'movie' and len(uncached) == 0 and len(sources_list) == 0:
			scrapper = Sources(info)
			uncached, sources_list, item_information = scrapper.get_sources()
			print(scrapper.progress)
		elif len(uncached) == 0 and len(sources_list) == 0:
			for i in info['show_aliases']:
				info['show_title'] = i
				info['tvshow'] = i
				info['tvshowtitle'] = i
				info['info']['show_title'] = i
				info['info']['tvshow'] = i
				info['info']['tvshowtitle'] = i
				#tools.log(info)
				scrapper = Sources(info)
				uncached, sources_list, item_information = scrapper.get_sources()
				print(scrapper.progress)
				if len(uncached) == 0 and len(sources_list) == 0:
					continue
				else:
					break


	#sources_list = tools.SourceSorter(item_information).sort_sources(sources_list)
	#uncached = tools.SourceSorter(info).sort_sources(uncached)
	if meta.get('download_type',False) != 'movie':
		sources_list, uncached = pack_sort(sources_list=sources_list, uncached=uncached, item_information=item_information)
	else:
		sources_list = tools.SourceSorter(item_information).sort_sources(sources_list)
		uncached = tools.SourceSorter(info).sort_sources(uncached)
	#torrent = getSources.choose_torrent(sources_list)
	idx = 0
	
	
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
	added_uncached = 0
	selection = -1
	if select_dialog:
		import xbmcgui
		tools.log(sources_list)
		tools.log('TORRENTS_FOUND')
		tools.log('TORRENTS_FOUND')
		tools.log('TORRENTS_FOUND')
		#tools.log(info)
		#from resources.lib.TheMovieDB import get_image_urls
		if meta.get('download_type',False) != 'movie':
			from resources.lib.TheMovieDB import extended_season_info
			response = extended_season_info(tvshow_id=meta['tmdb'], season_number=info['season'] )
			#tools.log(response)
			poster = response[1]['images'][1]['poster']
		else:
			from resources.lib.TheMovieDB import extended_movie_info
			response = extended_movie_info(movie_id=meta['tmdb_id'])
			#tools.log(response)
			poster = response[1]['images'][1]['poster']
		
		#for i in response:
		#	tools.log(i)
		#	#tools.log(response[i])
		#artwork = get_image_urls(poster=season.get('poster_path'))
		listitems = []
		for idx, i in enumerate(sources_list):
			source_name = '%s SIZE=%s %s SEEDS=%s PACK=%s ' % ( i['info'], i['size'], i['release_title'], i['seeds'], i['pack_size'])
			#source_name = str("{:<90}		{:<10}	{:<10}	{:<10}	{:<10}".format(str(i['release_title'][:95]), 'SIZE='+str(int(i['size'])), 'SEEDS='+str(i['seeds']), 'PACK='+str(int(i['pack_size'])), str(i['info'])))
			#listitems.append(source_name)
			listitems += [{'label': source_name, 'poster': poster,'label2': i['release_title']}]
			#listitem.update(artwork)
		#selection = xbmcgui.Dialog().select(heading='Choose Torrent', list=listitems, autoclose=30000, preselect=0)
		from resources.lib.WindowManager import wm
		listitem, selection = wm.open_selectdialog_autoclose(listitems=listitems, autoclose=30, autoselect=0)
		if selection == -1:
			return None, meta
		from resources.lib.Utils import show_busy
		show_busy()
		#tools.log(selection)

	if selection >= 0:
		idx = selection
	else:
		idx = 0

	while download_link == None:
		torr_id = None
		try: 
			torrent = sources_list[idx]
		except: 
			try:
				tools.log('UNCACHED')
				tools.log(torrent)
				torrent = uncached[idx]
				curr_idx = idx
				idx = idx + 1
				response = rd_api.add_magnet(torrent['magnet'])
				tools.log(response)
				try: torr_id = response['id']
				except KeyError: continue
				if 'infringing_file' in str(response):
					rd_api.delete_torrent(torr_id)
					continue
				
				response = rd_api.torrent_select_all(torr_id)
				time.sleep(2)
				tools.log(response)
				response = rd_api.torrent_select_all(torr_id)
				torr_info = rd_api.torrent_info(torr_id)
				tools.log(torr_info)
				if 'magnet_error' in str(torr_info) or 'waiting_files_selection' in str(torr_info):
					rd_api.delete_torrent(torr_id)
					continue
				added_uncached = added_uncached + 1
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
				tools.log(idx)
				tools.log('UNCACHED_ADDED_1ST_LINK_TO_RD')
				if added_uncached > 1:
					rd_api.delete_torrent(torr_id)
				if idx >= len(uncached)-1:
					return None, meta
				#continue
				return None, meta
			except:
				if torr_id:
					rd_api.delete_torrent(torr_id)
				else:
					tools.log('NONE___EXCEPTION_auto_scrape_rd')
					return None, meta
				if curr_idx >= len(uncached):
					return None, meta
				uncached.pop(curr_idx)
				idx = idx + 1
				tools.log(torrent, 'EXCEPTION_auto_scrape_rd')
				continue

		torrent = sources_list[idx]
		idx = idx + 1
		response = rd_api.add_magnet(torrent['magnet'])
		torr_id = response['id']
		response = rd_api.torrent_select_all(torr_id)
		torr_info = rd_api.torrent_info(torr_id)
		if torr_info['status'] != 'downloaded':
			continue

		def unrestrict_torr(torrent, torr_id):
			tools.log(torrent)
			torr_info = rd_api.torrent_info(torr_id)
			#tools.log(torr_info['links'])
			for i in torr_info['links']:
				full_unrestrict_link = i
				full_download_link = rd_api.resolve_hoster(full_unrestrict_link)
				full_download_id = rd_api.UNRESTRICT_FILE_ID
				tools.log(full_download_link, full_download_id)
			return

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
			#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			download_link, new_meta = cloud_single_ep(rd_api, meta, torr_id, torr_info)
		if download_link:
			if unrestrict:
				unrestrict_torr(torrent, torr_id)
			return download_link, new_meta
		if download_type != 'movie':
			#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			download_link, new_meta = cloud_get_ep_season(rd_api, meta, torr_id, torr_info)
		if download_link:
			if unrestrict:
				unrestrict_torr(torrent, torr_id)
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
	suppress_list = ['featurette','trailer','sample']
	for i in sorted_torr_info:
		suppress_flag = False
		for x in suppress_list:
			if x in i['pack_path'].lower():
				suppress_flag = True
		if suppress_flag == True:
			continue
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
	if not download_link:
		rd_api.delete_torrent(torr_id)
	
	return download_link, meta


def cloud_single_ep(rd_api, meta, torr_id, torr_info):
	torr_info = rd_api.torrent_info_files(torr_info)
	sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
	simple_info = tools._build_simple_show_info(meta['episode_meta'])
	info = meta['episode_meta']

	daily_show_flag = False
	if info['episode_air_date'][-2:] in info['title'] and info['episode_air_date'][:4] in info['title']:
		import datetime
		if datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%B %d, %Y') in info['title']:
			daily_show_flag = True
		if datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%Y.%m.%d') in info['title']:
			daily_show_flag = True

	if daily_show_flag:
		info_keyword = {'mediatype': 'movie', 'download_type': 'movie', 'episode': '', 'imdb_id': 'tt', 'is_movie': False, 'is_tvshow': False, 'media_type': 'movie', 'season': '', 'title': None, 'tmdb_id': None, 'tvshow': '', 'tvshow_year': '', 'year': '', 'info': {'mediatype': 'movie', 'episode': '', 'imdb_id': 'tt', 'is_movie': False, 'is_tvshow': False, 'media_type': 'movie', 'season': '', 'title': None, 'tmdb_id': None, 'tvshow': '', 'tvshow_year': '', 'year': ''}}

		info_keyword['title'] = '%s %s' % (info['tvshow'], info['episode_air_date'].replace('-','.'))
		info_keyword['info']['title'] = info_keyword['title']
		info['info']['title'] = info['info']['title'].replace(datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%B %d, %Y'), datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%Y.%m.%d'))
		info['title'] = info['info']['title']
		meta['episode_meta'] = info
		simple_info['show_aliases'] = info['info']['show_aliases']
		simple_info['episode_title'] = info['info']['title']
		#tools.log(meta['episode_meta'])

	unrestrict_link = None
	download_link = None
	for i in sorted_torr_info:
		pack_path = os.path.basename(i['pack_path'])
		test2 = source_tools.run_show_filters(simple_info, release_title = pack_path)
		if ': True' in str(test2):
			unrestrict_link = i['unrestrict_link']

	if unrestrict_link:
		download_link = rd_api.resolve_hoster(unrestrict_link)
		download_id = rd_api.UNRESTRICT_FILE_ID
		download_link = rd_api.test_download_link(download_link)
		if not download_link:
			rd_api.delete_torrent(torr_id)
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

	if download_type == 'movie':
		simple_info = tools._build_simple_movie_info(info)
		simple_info['imdb_id'] = info['imdb_id']
		daily_show_flag = False
	else:
		simple_info = tools._build_simple_show_info(info)

		daily_show_flag = False
		if info['episode_air_date'][-2:] in info['title'] and info['episode_air_date'][:4] in info['title']:
			import datetime
			if datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%B %d, %Y') in info['title']:
				daily_show_flag = True
			if datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%Y.%m.%d') in info['title']:
				daily_show_flag = True

	if daily_show_flag:
		info_keyword = {'mediatype': 'movie', 'download_type': 'movie', 'episode': '', 'imdb_id': 'tt', 'is_movie': False, 'is_tvshow': False, 'media_type': 'movie', 'season': '', 'title': None, 'tmdb_id': None, 'tvshow': '', 'tvshow_year': '', 'year': '', 'info': {'mediatype': 'movie', 'episode': '', 'imdb_id': 'tt', 'is_movie': False, 'is_tvshow': False, 'media_type': 'movie', 'season': '', 'title': None, 'tmdb_id': None, 'tvshow': '', 'tvshow_year': '', 'year': ''}}

		info_keyword['title'] = '%s %s' % (info['tvshow'], info['episode_air_date'].replace('-','.'))
		info_keyword['info']['title'] = info_keyword['title']
		info['info']['title'] = info['info']['title'].replace(datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%B %d, %Y'), datetime.datetime.strptime(info['episode_air_date'], '%Y-%m-%d').strftime('%Y.%m.%d'))
		info['title'] = info['info']['title']
		meta['episode_meta'] = info
		simple_info['show_aliases'] = info['info']['show_aliases']
		simple_info['episode_title'] = info['info']['title']
		#tools.log(meta['episode_meta'])
		#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		#tools.log(sources_list)

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
			source_list.append({'filename': x['filename'], 'pack_size': x['filesize'] / 1024 / 1024, 'size': x['filesize']/ 1024 / 1024, 'info': tools.get_info(x['filename']), 'quality': tools.get_quality(x['filename'])})
			source_list.append({'filename': x['filename'], 'pack_size': x['filesize'] / 1024 / 1024, 'size': x['filesize']/ 1024 / 1024, 'info': tools.get_info(source_tools.clean_title(x['filename'])), 'quality': tools.get_quality(source_tools.clean_title(x['filename']))})
			new_source_list = list(tools.SourceSorter(info).filter_sources2(source_list))
			if len(new_source_list) == 0:
				continue

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
					log('download',download_link)
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
						log('special_download',download_link)
						break

				if special_meta:
					test = source_tools.filter_movie_title(x['filename'], source_tools.clean_title(x['filename']), special_meta['title'], special_simple_info)
					if test:
						test = ': True'
					if ': True' in str(test):
						download_link = x['download']
						download_link = rd_api.test_download_link(download_link)
						if download_link:
							log('special_download2',download_link)
							break

		if download_link:
			break

	if download_link:
		return download_link, meta
	for i in range(1,99):
		#tools.log('torrent', i)
		result = rd_api.list_torrents_page(int(i))

		items_changed = False
		for x in result:
			if x['status'] != 'downloaded':
				#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				added_timestamp = time.mktime(time.strptime(x['added'], "%Y-%m-%dT%H:%M:%S.000Z"))
				current_timestamp = time.time()
				time_diff_seconds = current_timestamp - added_timestamp
				if time_diff_seconds > 200:
					if x['status'] == 'waiting_files_selection':
						torr_id = x['id']
						response = rd_api.torrent_select_all(torr_id)
						#tools.log('torrent_torrent_select_all', i, x,response)
						if 'error' in str(response):
							response = rd_api.delete_torrent(torr_id)
							#tools.log('torrent_delete_torrent', i, x,response)
							items_changed = True
					else:
						torr_id = x['id']
						response = rd_api.delete_torrent(torr_id)
						items_changed = True
						#tools.log('torrent_delete_torrent', i, x,response)

		if items_changed:
			result = rd_api.list_torrents_page(int(i))
		if '[204]' in str(result):
			break
		for x in result:
			#tools.log('torrent', i, x)
			#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			if x['status'] == 'downloading':
				continue

			file_info1 = tools.get_info(x['filename'])
			file_info2 = tools.get_info(source_tools.clean_title(x['filename']))
			source_list = []
			try:
				source_list.append({'filename': x['filename'], 'pack_size': x['bytes'] / 1024 / 1024 , 'size': x['bytes'] / 1024 / 1024 / max(1,len(x['links'])), 'info': tools.get_info(x['filename']), 'quality': tools.get_quality(x['filename'])})
				source_list.append({'filename': x['filename'], 'pack_size': x['bytes'] / 1024 / 1024 , 'size': x['bytes'] / 1024 / 1024 / max(1,len(x['links'])), 'info': tools.get_info(source_tools.clean_title(x['filename'])), 'quality': tools.get_quality(source_tools.clean_title(x['filename']))})
			except: 
				#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				continue
			new_source_list = list(tools.SourceSorter(info).filter_sources2(source_list))
			if len(new_source_list) == 0:
				#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				continue

			if download_type == 'movie':
				test = source_tools.filter_movie_title(x['filename'], source_tools.clean_title(x['filename']), meta['title'], simple_info)
				if test:
					test = ': True'
				#test2 = source_tools.filter_movie_title(x['filename'], source_tools.clean_title(x['filename']), meta['title'], simple_info)
				test2 = {}
			else:
				#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				simple_info_original = simple_info
				test = source_tools.run_show_filters(simple_info, pack_title = x['filename'])
				simple_info = simple_info_original
				if simple_info['episode_number'] == 'None' or simple_info['episode_number'] == None:
					simple_info1 = simple_info
					simple_info1['episode_number'] = '0'
					#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
					test2 = source_tools.run_show_filters(simple_info1, release_title = x['filename'])
				else:
					#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
					test2 = source_tools.run_show_filters(simple_info, release_title = x['filename'])
			#tools.log(test2, test)
			if download_type != 'movie':
				if (len(x['links']) >= meta['tvmaze_seasons_episode_tot'] or len(x['links']) >= meta['tmdb_seasons_episode_tot']) and not (': True' in str(test) or ': True' in str(test2)) and download_type != 'movie':
					simple_info['imdb_id'] = meta['episode_meta']['imdbnumber']
					test2['show_match'] = source_tools.filter_movie_title(x['filename'], source_tools.clean_title(x['filename']), simple_info['show_title'], simple_info)

			if ': True' in str(test) or ': True' in str(test2):
				torr_id = x['id']
				torr_info = rd_api.torrent_info(torr_id)
				if download_type == 'movie':
					download_link, meta = cloud_movie(rd_api, meta, torr_id, torr_info)
					if download_link:
						tools.log('cloud_movie',download_link)
						return download_link, meta

				if download_type != 'movie':
					if daily_show_flag:
						tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
						download_link, new_meta = cloud_single_ep(rd_api, meta, torr_id, torr_info)
					else:
						download_link, new_meta = cloud_get_ep_season(rd_api, meta, torr_id, torr_info)
				if download_link:
					tools.log('cloud_get_ep_season',download_link)
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
						tools.log('SPECIAL_cloud_get_ep_season',download_link)
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
							tools.log('SPECIAL_cloud_movie',download_link)
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
	before_download = rd_api.remaining_tot_bytes
	try: tools.download_progressbar(rd_api, download_link, download_path2)
	except: tools.tools_stop_downloader = True
	#rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE
	if rd_api.remaining_tot_bytes == before_download:
		rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE


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
		before_download = rd_api.remaining_tot_bytes
		try: tools.download_progressbar(rd_api, download_link, download_path2)
		except: tools.tools_stop_downloader = True
		#rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE
		if rd_api.remaining_tot_bytes == before_download:
			rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE
		curr_percent(rd_api)
		#info = get_subtitles(info, download_path2)
		#sub_out = os.path.basename(tools.SUB_FILE)
		#sub_path = os.path.join(download_folder, sub_out)
		#shutil.copyfile(tools.SUB_FILE, sub_path)
		#log(sub_path)

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
		before_download = rd_api.remaining_tot_bytes
		try: tools.download_progressbar(rd_api, download_link, download_path2)
		except: tools.tools_stop_downloader = True
		#rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE
		if rd_api.remaining_tot_bytes == before_download:
			rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE
		curr_percent(rd_api)
		#info = get_subtitles(curr_download, download_path2)
		#sub_out = os.path.basename(tools.SUB_FILE)
		#sub_path = os.path.join(download_folder, sub_out)
		#shutil.copyfile(tools.SUB_FILE, sub_path)
		#log(sub_path)

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
		before_download = rd_api.remaining_tot_bytes
		try: tools.download_progressbar(rd_api, download_link, download_path2)
		except: tools.tools_stop_downloader = True
		#rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE
		if rd_api.remaining_tot_bytes == before_download:
			rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE
		curr_percent(rd_api)

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
				if tools.tools_stop_downloader == True:
					tools.tools_stop_downloader = False
					return
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
	folder = curr_download['filename_without_ext']
	
	download_folder = unquote(os.path.join(download_path, folder))
	
	
	torr_info = rd_api.torrent_info_files(torr_info)
	sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
	simple_info = tools._build_simple_show_info(curr_download)
	simple_info['imdb_id'] = curr_download['imdb_id']
	#tools.log(sorted_torr_info)
	for i in sorted_torr_info:
		#test = source_tools.run_show_filters(simple_info, pack_title = i['pack_path'])
		test1 = source_tools.filter_movie_title(curr_download['CURR_LABEL'], source_tools.clean_title(curr_download['CURR_LABEL']), curr_download['title'], simple_info)
		test2 = source_tools.filter_movie_title(curr_download['CURR_LABEL'], source_tools.clean_title( i['pack_path']), curr_download['title'], simple_info)
		if test1 or test2 or curr_download['release_title'] == 'CUSTOM':
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

	before_download = rd_api.remaining_tot_bytes
	try: tools.download_progressbar(rd_api, download_link, download_path)
	except: tools.tools_stop_downloader = True
	#rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE
	if rd_api.remaining_tot_bytes == before_download:
		rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE
	#info = get_subtitles(curr_download, download_path)

	if tools.tools_stop_downloader == True:
		return

	download_folder1 = os.path.dirname(download_path)

	sub_path1 = os.path.join(download_folder1,unquote(str(os.path.splitext(os.path.basename(download_link))[0] + '.srt')))
	sub_path2 = os.path.join(download_folder1,unquote(str(os.path.splitext(os.path.basename(download_link))[0] + '.eng.FORCED.srt')))
	sub_path3 = os.path.join(download_folder1,unquote(str(os.path.splitext(os.path.basename(download_link))[0] + '.eng.srt')))

	#sub_path1 = os.path.join(download_folder, str(curr_download['filename_without_ext'].replace(':','') + '.srt'))
	#sub_path2 = os.path.join(download_folder, str(curr_download['filename_without_ext'].replace(':','') + '.eng.FORCED.srt'))
	#sub_path3 = os.path.join(download_folder, str(curr_download['filename_without_ext'].replace(':','') + '.eng.srt'))
	tools.log(sub_path1)
	tools.log(sub_path2)
	tools.log(sub_path3)

	exists_flag = False
	if os.path.exists(sub_path1) or os.path.exists(sub_path2) or os.path.exists(sub_path3):
		exists_flag = True

	if exists_flag == False:
		try: subs = importlib.import_module("subs")
		except: subs = reload_module(importlib.import_module("subs"))
		subs.META = curr_download
		subs_list = subs.get_subtitles_list(curr_download, download_path)
		del subs
		#exit()
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
			shutil.copyfile(i, out_path)
			tools.log(out_path)
	tmdb_api = tools.get_setting('tmdb_api')
	tmdb_url = 'https://api.themoviedb.org/3/movie/%s?language=en-US&api_key=%s' % (str(curr_download['tmdb_id']),tmdb_api)
	
	meta_info = requests.get(tmdb_url).json()
	movie_poster = 'https://image.tmdb.org/t/p/original' + meta_info['poster_path']
	if '.png' in movie_poster:
		poster_path = os.path.join(download_folder1, 'poster.png')
	elif '.jpg' in movie_poster:
		poster_path = os.path.join(download_folder1,'poster.jpg')
	try:
		tools.download_progressbar(rd_api, movie_poster, poster_path)
	except: 
		tools.log('POSTER_MISSING_OR_OTHER_ERROR!!!!')
	#sub_out = os.path.basename(tools.SUB_FILE)
	#sub_path = os.path.join(download_folder, sub_out)
	#shutil.copyfile(tools.SUB_FILE, sub_path)
	#log(sub_path)

	curr_percent(rd_api)
	rd_api.delete_torrent(torr_id)
	rd_api.delete_download(rd_api.UNRESTRICT_FILE_ID)

def download_cached_episode(rd_api, download_path, curr_download, torr_id, torr_info):
	#tools.log('download_cached_episode')
	folder = curr_download['CURR_LABEL'].replace(':','')
	download_folder = os.path.join(download_path, folder)
	torr_info = rd_api.torrent_info_files(torr_info)
	sorted_torr_info = sorted(torr_info['files_links'], key=lambda x: x['pack_path'])
	simple_info = tools._build_simple_show_info(curr_download['episode_meta'])
	info = curr_download['episode_meta']


	info2 = None
	#tools.log(curr_download)
	for i in curr_download['tvmaze_seasons']['episodes']:
		if i['episode'] == curr_download['episode_meta']['episode'] and curr_download['episode_meta']['season'] == i['season'] and curr_download['episode_meta']['title'] == i['title']: 
			info2 = i
			break
	if not info2:
		for i in curr_download['tmdb_seasons']['episodes']:
			if i['episode'] == curr_download['episode_meta']['episode'] and curr_download['episode_meta']['season'] == i['season'] and curr_download['episode_meta']['title'] == i['title']: 
				info2 = i
				break
	#tools.log(info2)
	#curr_download = info2
	info2['aliases'].append(info2['tvshowtitle'])

	curr_download['file_name'] = unquote(curr_download['file_name'])
	curr_download['filename'] = unquote(curr_download['filename'])
	show_folder = os.path.join(download_path, str(curr_download['episode_meta']['tvshow']) + ' (' + str(curr_download['episode_meta']['tvshow_year'] + ')')).replace(':','')
	if not os.path.exists(show_folder):
		os.makedirs(show_folder)
	season_folder = os.path.join(show_folder, str(curr_download['episode_meta']['tvshow']) + ' - Season ' + str(curr_download['episode_meta']['season']).zfill(2)).replace(':','')
	if not os.path.exists(season_folder):
		os.makedirs(season_folder)
	download_folder = season_folder
	for i in torr_info['files_links']:
		if curr_download['file_name'] in str(i):
			unrestrict_link = i['unrestrict_link']
			download_path = os.path.join(download_folder, curr_download['filename']).replace(':','')
			log(unrestrict_link, download_path)
			download_link = rd_api.resolve_hoster(unrestrict_link)
			download_id = rd_api.UNRESTRICT_FILE_ID
			log(download_link, download_id)
			before_download = rd_api.remaining_tot_bytes
			try: tools.download_progressbar(rd_api, download_link, download_path)
			except: tools.tools_stop_downloader = True
			#rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE
			if rd_api.remaining_tot_bytes == before_download:
				rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE

			if tools.tools_stop_downloader == True:
				return

			#info = get_subtitles(info, download_path)
			#sub_out = os.path.basename(tools.SUB_FILE)
			#sub_path = os.path.join(download_folder, sub_out)
			#shutil.copyfile(tools.SUB_FILE, sub_path)
			
			#tools.log(curr_download)
			download_folder1 = os.path.dirname(download_path)
			sub_path1 = os.path.join(download_folder1,unquote(str(os.path.splitext(os.path.basename(download_link))[0] + '.srt'))).replace(':','')
			sub_path2 = os.path.join(download_folder1,unquote(str(os.path.splitext(os.path.basename(download_link))[0] + '.eng.FORCED.srt'))).replace(':','')
			sub_path3 = os.path.join(download_folder1,unquote(str(os.path.splitext(os.path.basename(download_link))[0] + '.eng.srt'))).replace(':','')

			#sub_path1 = os.path.join(download_folder, str(curr_download['filename_without_ext'].replace(':','') + '.srt'))
			#sub_path2 = os.path.join(download_folder, str(curr_download['filename_without_ext'].replace(':','') + '.eng.FORCED.srt'))
			#sub_path3 = os.path.join(download_folder, str(curr_download['filename_without_ext'].replace(':','') + '.eng.srt'))
			tools.log(sub_path1)
			tools.log(sub_path2)
			tools.log(sub_path3)

			exists_flag = False
			if os.path.exists(sub_path1) or os.path.exists(sub_path2) or os.path.exists(sub_path3):
				exists_flag = True

			if exists_flag == False:
				try: subs = importlib.import_module("subs")
				except: subs = reload_module(importlib.import_module("subs"))
				subs.META = curr_download
				subs_list = subs.get_subtitles_list(info2, download_path)
				del subs
				#exit()
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
					shutil.copyfile(i, out_path)
					tools.log(out_path)

			curr_percent(rd_api)
			rd_api.delete_download(rd_api.UNRESTRICT_FILE_ID)

	#log(sub_path)

	rd_api.delete_torrent(torr_id)



def download_cached_magnet_pack(rd_api, download_path, curr_download, torr_id, torr_info):
	folder = curr_download['CURR_LABEL']
	folder = torr_info['original_filename']

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
		info['aliases'].append(info['tvshowtitle'])
		download_path = os.path.join(download_folder + pack_path)
		#log(season, episode, pack_path, unrestrict_link, info)
		log(unrestrict_link, download_path)
		download_link = rd_api.resolve_hoster(unrestrict_link)
		download_id = rd_api.UNRESTRICT_FILE_ID
		log(download_link, download_id)
		if not os.path.exists(download_folder):
			os.makedirs(download_folder)
		before_download = rd_api.remaining_tot_bytes
		try: tools.download_progressbar(rd_api, download_link, download_path)
		except: tools.tools_stop_downloader = True
		#rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE
		if rd_api.remaining_tot_bytes == before_download:
			rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE

		if tools.tools_stop_downloader == True:
			return

		download_folder1 = os.path.dirname(download_path)
		sub_path1 = os.path.join(download_folder1,unquote(str(os.path.splitext(os.path.basename(download_link))[0] + '.srt'))).replace(':','')
		sub_path2 = os.path.join(download_folder1,unquote(str(os.path.splitext(os.path.basename(download_link))[0] + '.eng.FORCED.srt'))).replace(':','')
		sub_path3 = os.path.join(download_folder1,unquote(str(os.path.splitext(os.path.basename(download_link))[0] + '.eng.srt'))).replace(':','')

		#sub_path1 = os.path.join(download_folder, str(curr_download['filename_without_ext'].replace(':','') + '.srt'))
		#sub_path2 = os.path.join(download_folder, str(curr_download['filename_without_ext'].replace(':','') + '.eng.FORCED.srt'))
		#sub_path3 = os.path.join(download_folder, str(curr_download['filename_without_ext'].replace(':','') + '.eng.srt'))
		tools.log(sub_path1)
		tools.log(sub_path2)
		tools.log(sub_path3)
		exists_flag = False
		if os.path.exists(sub_path1) or os.path.exists(sub_path2) or os.path.exists(sub_path3):
			exists_flag = True

		if exists_flag == False:
			try: subs = importlib.import_module("subs")
			except: subs = reload_module(importlib.import_module("subs"))
			subs.META = curr_download
			subs_list = subs.get_subtitles_list(info, download_path)
			del subs
			#exit()
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
				shutil.copyfile(i, out_path)
				tools.log(out_path)
		if tools.tools_stop_downloader == True:
			tools.tools_stop_downloader = False
			return

		curr_percent(rd_api)
		rd_api.delete_download(rd_api.UNRESTRICT_FILE_ID)
		#log(sub_path)

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

def rd_delete_dupes():
	rd_api = real_debrid.RealDebrid()
	i = 0
	result = None
	names = []
	while result == None:
		i = i + 1
	#for i in range(1,99):
		tools.log('PAGE_NUMBER', i)
		result = rd_api.list_torrents_page(int(i))
		for x in result:
			#tools.log(x)
			if x['status'] != 'downloaded' and x['status'] != 'downloading':
				check_hash = rd_api.check_hash([x['hash']])
				try:
					if len(x['links']) == 0:
						tools.log('ERROR_DELETE=' + x['filename'])
						#tools.log(check_hash)
						delete_torrent = rd_api.delete_torrent(x['id'])
						tools.log(delete_torrent)
						break_flag = True
				except KeyError:
					break_flag = True
					pass
			pass_count = 0
			if x['status'] == 'downloading':
				pass_count = 1
			break_flag = False
			if x['filename'] in names:
				tools.log(x['filename'])
				tools.log('DELETE_DUPLICATE=' + x['filename'])
				delete_torrent = rd_api.delete_torrent(x['id'])
				tools.log(delete_torrent)
				break_flag = True
			if break_flag == False:
				try: 
					for j in x['links']:
						torr_link = rd_api.resolve_hoster(j)
						torr_link = rd_api.test_download_link(torr_link,rar_test=False)
						if torr_link:
							pass_count = pass_count + 1
						UNRESTRICT_FILE_ID = torr_link.split('/')[4]
						rd_api.delete_download(UNRESTRICT_FILE_ID)
				except KeyError:
					pass_count = 1
					pass
				if pass_count == 0:
					tools.log('DELETE_NO_LINKS=' + x['filename'])
					if x['status'] != 'downloaded':
						print(x)
						delete_torrent = rd_api.delete_torrent(x['id'])
						tools.log(delete_torrent)
			if x['status'] != 'downloading':
				names.append(x['filename'])
		if type(result).__name__ == 'list':
			result = None

	try: continue_check = input('Check Downloads:  Y/y to continue\n')
	except: continue_check = None
	if continue_check and str(continue_check).lower() == 'y':
		continue_check = True
	else:
		continue_check = False
		return

	i = 0
	result = None
	names = []
	while result == None:
		i = i + 1
		tools.log('PAGE_NUMBER', i)
		result = rd_api.list_downloads_page(int(i))
		for x in result:
			#PTN_link = x['download']
			#PTN_link_pos = PTN_link.find('/d/')+3
			#PTN_link_pos2 = PTN_link_pos+13
			#PTN_link = PTN_link[0:PTN_link_pos2] + '/'
			tools.log(str(x['download']).split('/')[-1])
			#torr_link = rd_api.resolve_hoster(PTN_link)
			if str(x['download']).split('/')[-1] in names:
				RD_link = str(x['download']).split('/')[4]
				delete_download = rd_api.delete_download(RD_link)
				tools.log(delete_download)
				tools.log('DELETE_DOWNLOAD_DUPLICATE' + x['filename'])
				continue
			torr_link = rd_api.test_download_link(x['download'],rar_test=False)
			tools.log(torr_link)
			if not torr_link:
				RD_link = str(x['download']).split('/')[4]
				delete_download = rd_api.delete_download(RD_link)
				tools.log(delete_download)
				tools.log('DELETE_DOWNLOAD_' + x['filename'])

			names.append(str(x['download']).split('/')[-1])
		if type(result).__name__ == 'list':
			result = None
			#try:
			#	PTN_download = torr_link
			#	RD_link = str(PTN_download).split('/')[4]
			#	delete_download = rd_api.delete_download(RD_link)
			#	tools.log('DELETE_DOWNLOAD_' + x['filename'])
			#except:
			#	RD_link = str(PTN_link).split('/')[4]
			#	delete_download = rd_api.delete_download(RD_link)
			#	tools.log('DELETE_DOWNLOAD_' + x['filename'])


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
	('providers2.a4kScrapers.en.torrent', 'bitlord', 'a4kScrapers'), 
	('providers2.a4kScrapers.en.torrent', 'bitsearch', 'a4kScrapers'), 
	('providers2.a4kScrapers.en.torrent', 'btdig', 'a4kScrapers'), 
	('providers2.a4kScrapers.en.torrent', 'cached', 'a4kScrapers'), 
	('providers2.a4kScrapers.en.torrent', 'glo', 'a4kScrapers'), 
	('providers2.a4kScrapers.en.torrent', 'kickass', 'a4kScrapers'), 
	('providers2.a4kScrapers.en.torrent', 'lime', 'a4kScrapers'), 
	('providers2.a4kScrapers.en.torrent', 'magnetdl', 'a4kScrapers'), 
	('providers2.a4kScrapers.en.torrent', 'piratebay', 'a4kScrapers'), 
	#('providers2.a4kScrapers.en.torrent', 'rutor', 'a4kScrapers'), 
	('providers2.a4kScrapers.en.torrent', 'showrss', 'a4kScrapers'), 
	('providers2.a4kScrapers.en.torrent', 'torrentdownload', 'a4kScrapers'), 
	('providers2.a4kScrapers.en.torrent', 'torrentio', 'a4kScrapers'), 
	('providers2.a4kScrapers.en.torrent', 'torrentz2', 'a4kScrapers'), 
	('providers2.a4kScrapers.en.torrent', 'yts', 'a4kScrapers')
	], 
	'adaptive': []}

	for root, dirs, files in os.walk(tools.A4KPROVIDERS_PATH, topdown=False):
		for name in files:
			#log(os.path.join(root, name))
			if '.py' == name[-3:] and '__init__.py' != name:
				file = str(os.path.join(root, name).split('providers2')[1])
				if '/' in str(file):
					splits = str(file).split('/')
				else:
					splits = str(file).split('\\')
				providers_dict[splits[3]].append(tuple([str('providers2.%s.%s.%s') % (splits[1],splits[2],splits[3]), splits[4].replace('.py',''), splits[1], True]))
	#log(providers_dict)
	return providers_dict

def setup_providers(provider_url):
	"""
import getSources
getSources.setup_providers('https://bit.ly/a4kScrapers')
"""
	if os.path.exists(tools.A4KPROVIDERS_PATH_original):
		shutil.rmtree(tools.A4KPROVIDERS_PATH_original)
	if os.path.exists(tools.A4KPROVIDERS_PATH):
		shutil.rmtree(tools.A4KPROVIDERS_PATH)
	if os.path.exists(tools.PROVIDERS_JSON):
		os.remove(tools.PROVIDERS_JSON)

	tools.log(tools.A4KPROVIDERS_PATH)
	provider_url = 'https://bit.ly/a4kScrapers'
	temp_zip = tools.temp_file()
	tools.download_file(provider_url, temp_zip)
	dest_dir = tools.ADDON_USERDATA_PATH
	tools.extract_zip(temp_zip, dest_dir)
	tools.delete_file(temp_zip)
	shutil.move(tools.A4KPROVIDERS_PATH_original, tools.A4KPROVIDERS_PATH)
	
	from inspect import currentframe, getframeinfo
	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

	folder = str(os.path.split(str(getframeinfo(currentframe()).filename))[0])
	current_directory = folder.replace('a4kscrapers_wrapper','')
	urls_json_path = os.path.join(tools.ADDON_USERDATA_PATH, 'providerModules','a4kScrapers', 'urls.json')

	elf_hosted_path = os.path.join(current_directory, 'elfhosted.py')
	new_elf_hosted_path = os.path.join(tools.A4KPROVIDERS_PATH, 'a4kScrapers', 'en', 'torrent', 'elfhosted.py')
	shutil.copy(elf_hosted_path, new_elf_hosted_path)
	elf_hosted_urls_dict = { "search": "/stream/{{category}}/%s.json", "cat_movie": "movie", "cat_episode": "series", "domains": [ { "base": "https://torrentio.elfhosted.com" } ] }

	with open(urls_json_path,'r+') as file:
		file_data = json.load(file)
		file_data['trackers']["elfhosted"] = elf_hosted_urls_dict
		file.seek(0)
		json.dump(file_data, file, indent = 4)
	patch_ak4_core_find_url()

	"""
	rutor_path = os.path.join(current_directory, 'rutor.py')
	new_rutor_path = os.path.join(tools.A4KPROVIDERS_PATH, 'a4kScrapers', 'en', 'torrent', 'rutor.py')

	#mirrorbay_path = os.path.join(current_directory, 'mirrorbay.py')
	#new_mirrorbay_path = os.path.join(tools.A4KPROVIDERS_PATH, 'a4kScrapers', 'en', 'torrent', 'mirrorbay.py')

	shutil.copy(rutor_path, new_rutor_path)
	#shutil.copy(mirrorbay_path, new_mirrorbay_path)
	rutor_urls_dict = { "search": "/search/0/0/000/0/%s", "cat_movie": "movies", "cat_episode": "tv", "domains": [ { "base": "http://rutor.is" } ] }
	#mirrorbay_urls_dict = {"search": "/get-data-for/%s", "cat_movie": "207,202,201", "cat_episode": "208,205", "domains": [{"base": "https://mirrorbay.org"}]}
	
	with open(urls_json_path,'r+') as file:
		file_data = json.load(file)
		file_data['trackers']["rutor"] = rutor_urls_dict
		#file_data['trackers']["mirrorbay"] = mirrorbay_urls_dict
		file.seek(0)
		json.dump(file_data, file, indent = 4)
	"""
	
	tools.findReplace(tools.A4KPROVIDERS_PATH, "'providers.", "'providers2.", "*.py")
	tools.findReplace(tools.A4KPROVIDERS_PATH, "from providers.a4kScrapers", "from providers2.a4kScrapers", "*.py")
	providers_dict = get_providers_dict()
	tools.write_all_text(tools.PROVIDERS_JSON,str(providers_dict))


def get_providers():
	try: providers_dict = eval(tools.read_all_text(tools.PROVIDERS_JSON))
	except: providers_dict = get_providers_dict()
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

#def get_subtitles_meta(VIDEO_META, file_path):
#	"""
#import get_meta, getSources
#meta = get_meta.get_movie_meta(movie_name='Point Break',year=1991)
#info = meta
#
#import get_meta, getSources
#meta = get_meta.get_episode_meta(season=1,episode=1,show_name='The Flash', year=2014)
#info = meta['episode_meta']
#
###FILEPATH!!
#getSources.get_subtitles(info , '')
#
#"""
#	#try:
#	if 1==1:
#		VIDEO_META['season'] = str(VIDEO_META['season'] )
#		VIDEO_META['episode'] = str(VIDEO_META['episode'])
#	#except:
#	#	pass
#	#try:
#	if 1==1:
#		VIDEO_META['file_name'] = os.path.basename(file_path)
#		VIDEO_META['filename'] = VIDEO_META['file_name']
#		VIDEO_META['filename_without_ext'] = os.path.splitext(VIDEO_META['file_name'])[0]
#		VIDEO_META['subs_filename'] = VIDEO_META['filename_without_ext'] + '.srt'
#		#tools.VIDEO_META = VIDEO_META
#		if 'http' in str(file_path):
#			VIDEO_META = tools.set_size_and_hash_url(VIDEO_META, file_path)
#		else:
#			VIDEO_META = tools.set_size_and_hash(VIDEO_META, file_path)
#	#except:
#	#	pass
#	#os.environ['A4KSUBTITLES_API_MODE'] = str({'kodi': 'false'})
#	#try: import subtitles
#	#except: from a4kscrapers_wrapper import subtitles
#	#subfile = subtitles.SubtitleService().get_subtitle()
#	#VIDEO_META['SUB_FILE'] = tools.SUB_FILE
#	#tools.VIDEO_META = VIDEO_META
#	tools.log(VIDEO_META)
#	#tools.VIDEO_META['SUB_FILE'] = tools.SUB_FILE
#	json_data = json.dumps(VIDEO_META, indent=2)
#	curr_meta = os.path.join(tools.ADDON_USERDATA_PATH, 'curr_meta.json')
#	tools.log('write_all_text')
#	tools.log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
#	tools.write_all_text(curr_meta, json_data)
#	tools.log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
#	return VIDEO_META
#
#
#
#def get_subtitles(VIDEO_META, file_path):
#	"""
#import get_meta, getSources
#meta = get_meta.get_movie_meta(movie_name='Point Break',year=1991)
#info = meta
#
#import get_meta, getSources
#meta = get_meta.get_episode_meta(season=1,episode=1,show_name='The Flash', year=2014)
#info = meta['episode_meta']
#
##FILEPATH!!
#getSources.get_subtitles(info , '')
#
#"""
#	try:
#		VIDEO_META['file_name'] = os.path.basename(file_path)
#		VIDEO_META['filename'] = VIDEO_META['file_name']
#		VIDEO_META['filename_without_ext'] = os.path.splitext(VIDEO_META['file_name'])[0]
#		VIDEO_META['subs_filename'] = VIDEO_META['filename_without_ext'] + '.srt'
#		tools.VIDEO_META = VIDEO_META
#		if 'http' in str(file_path):
#			tools.VIDEO_META = tools.set_size_and_hash_url(tools.VIDEO_META, file_path)
#		else:
#			tools.VIDEO_META = tools.set_size_and_hash(tools.VIDEO_META, file_path)
#	except:
#		pass
#	os.environ['A4KSUBTITLES_API_MODE'] = str({'kodi': 'false'})
#	subfile = subtitles.SubtitleService().get_subtitle()
#	tools.VIDEO_META['SUB_FILE'] = tools.SUB_FILE
#	return tools.VIDEO_META
#
#
#def get_subtitles_list(VIDEO_META, file_path):
#	#from a4kscrapers_wrapper import subs
#	meta = get_subtitles_meta(VIDEO_META, file_path)
#	#tools.VIDEO_META = VIDEO_META
#
#	subfile = subs.SubtitleService(meta).get_subtitle()
#	tools.SUB_FILE = subfile
#	#tools.VIDEO_META['SUB_FILE'] = subfile
#	#tools.log('SUBTITLES_____________',tools.VIDEO_META)
#	#SUB_FILE = tools.VIDEO_META['SUB_FILE']
#	try: 
#		SUB_FILE = tools.VIDEO_META['SUB_FILE']
#	except: 
#		SUB_FILE = meta['SUB_FILE']
#		tools.VIDEO_META = meta
#	#tools.log(tools.VIDEO_META,meta)
#	try: 
#		SUB_FILE_FORCED = tools.VIDEO_META['SUB_FILE_FORCED']
#	except: 
#		SUB_FILE_FORCED = meta['SUB_FILE_FORCED']
#		tools.VIDEO_META = meta
#	subs_list = []
#	if str(SUB_FILE) != '' and SUB_FILE != None:
#		subs_list.append(SUB_FILE)
#	if str(SUB_FILE_FORCED) != '' and SUB_FILE_FORCED != None:
#		subs_list.append(SUB_FILE_FORCED)
#	return subs_list

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
		self.non_working_hashes = []
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
		self.timeout = 145
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
				return self._finalise_results()

			"""
			self._init_providers()
			

			# Add the users cloud inspection to the threads to be run
			self.torrent_threads.put(self._user_cloud_inspection)

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
			"""
			# Keep alive for gui display and threading
			log('Entering Keep Alive', 'info')

			"""
			while self.progress < 100:
				self.runtime = time.time() - start_time

				self._update_progress()

				self.timeout_progress = int(100 - float(1 - (self.runtime / float(self.timeout))) * 100)
				self.progress = int(100 - (	len(self.sources_information['statistics']['remainingProviders']) / float(len(self.torrent_providers)) * 100) )

				if self._prem_terminate() is True or (	len(self.sources_information['statistics']['remainingProviders']) == 0 and self.runtime > 5):
					# Give some time for scrapers to initiate

					break
				if self.canceled or self.runtime >= self.timeout:

					tools.PRE_TERM_BLOCK = True
					self.PRE_TERM_BLOCK = True

					break

			while len(self.running_providers):
				time.sleep(0.1)

			log('Exited Keep Alive', 'info')
			for provider in self.running_providers:
				if hasattr(provider, 'cancel_operations') and callable(provider.cancel_operations):
					provider.cancel_operations()
			if (any([True for i in inspect.stack() if "providerModules" in i[1]]) or
				any([True for i in inspect.stack() if "providers2" in i[1]])):
				raise tools.PreemptiveCancellation('Pre-emptive termination has stopped this request111')
			"""
			self._init_providers_search(simple_info=self.item_information,info=self.item_information)
			return self._finalise_results()

		finally:
			#self.window.close()
			while len(self.running_providers):
				time.sleep(0.1)
			try:
				if tools.ADDON_USERDATA_PATH not in sys.path:
					sys.path.append(tools.ADDON_USERDATA_PATH)
					providers2 = importlib.import_module("providers2")
				else:
					providers2 = reload_module(importlib.import_module("providers2"))
			except ValueError:
				log('No providers installed', 'warning')
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

		for idx,i in enumerate(self.torrent_providers):
			if i[1] == 'cached':
				break
		self.torrent_providers.pop(idx)
		self.torrent_providers.insert(0,i)
		pop_list = []
		#pop_list_items = []
		for idx,i in enumerate(self.torrent_providers):
			if i[3] == False or str(i[3]) == 'False':
				pop_list.append(idx)
				#tools.log(i)
				#pop_list_items.append(i)

		for i in pop_list:
			try:self.torrent_providers.pop(i)
			except: pass
		#for i in pop_list_items:
		#	self.torrent_providers.append(i)

		for i in self.torrent_providers:
			if i[3] == False or str(i[3]) == 'False':
				continue
			tools.log(i)
			try: self.torrent_threads.put(self._get_torrent, self.item_information, i)
			except Exception: log('EXCEPTION:', Exception, str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

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

	def _process_provider_torrent2(self, torrent, provider_name, info):
		torrent['type'] = 'torrent'
		torrent['provider_name'] = provider_name

		if not torrent.get('info'):
			torrent['info'] = tools.get_info(torrent['release_title'])

		if torrent.get("quality") not in tools.approved_qualities_set:
			torrent['quality'] = tools.get_quality(torrent['release_title'])

		torrent['hash'] = torrent.get('hash', self.hash_regex.findall(torrent['magnet'])[0]).lower()
		torrent['pack_size'], torrent['size'] = self._torrent_filesize(torrent, info)
		if len(str(torrent['size'])) == 7 and torrent['size'] == torrent['pack_size']:
			torrent['size'] = torrent['size']/1024
			torrent['pack_size'] = torrent['pack_size']/1024
		torrent['seeds'] = self._torrent_seeds(torrent)

		if 'provider_name_override' in torrent:
			torrent['provider'] = torrent['provider_name_override']
		else:
			torrent['provider'] = provider_name
		return torrent

	def _init_providers_search(self, simple_info=None, info=None):
		start_time = time.time()
		sys.path.append(tools.ADDON_USERDATA_PATH)
		try:
			if tools.ADDON_USERDATA_PATH not in sys.path:
				sys.path.append(tools.ADDON_USERDATA_PATH)
				providers2 = importlib.import_module("providers2")
			else:
				providers2 = reload_module(importlib.import_module("providers2"))
		except ValueError:
			log('No providers installed', 'warning')
			return
		#providers2 = importlib.import_module("providers2")
		providers_dict = get_providers()
		log(providers_dict)
		results_store = []
		for provider in providers_dict['torrent']:
			if provider[3] == False or provider[3] == 'False':
				continue
			provider_module = importlib.import_module("{}.{}".format(provider[0], provider[1]))
			provider_source = provider_module.sources()
			#results = provider_source.episode(simple_info, info)



			if self.media_type == 'episode':
				simple_info = tools._build_simple_show_info(info)
				#results = provider_source.episode(simple_info, info,   auto_query=False, query_seasons=True, query_show_packs=True)
				self.torrent_threads.put(provider_source.episode,simple_info, info)
				results = self.torrent_threads.wait_completion()
			else:
				#simple_info = tools._build_simple_movie_info(info)
				#results = provider_source.movie(simple_info, info)

				simple_info = tools._build_simple_movie_info(info)

				try: results = provider_source.movie(simple_info, info)
				except AttributeError: 
					try: results = provider_source.movie(simple_info, info)
					except AttributeError: pass
				except TypeError:
					try: results = provider_source.movie(info['info']['title'],str(info['info']['year']),info['info'].get('imdb_id'),)
					except (TypeError, AttributeError):
						results = provider_source.movie(info['info']['title'], str(info['info']['year']))


			log(str(provider[1]) + ' - ' + str(len(results)))
			#log(len(results_store))
			for idx,i in enumerate(results):
				results[idx]['provider_name'] =  provider[1].upper()
			results_store.extend(results)
		#print(len(results_store))
		result = []
		seen = set()
		for item in results_store:
			if item['hash'] not in seen:
				result.append(item)
				seen.add(item['hash'])
		for idx,i in enumerate(result):
			#results_store[idx]['quality'] = tools.get_quality(i['release_title'])
			#results_store[idx]['info'] =  tools.get_info(i['release_title'])
			#results_store[idx] = self._process_provider_torrent2( i, i['provider_name'], info)
			#log(i)
			self._process_provider_torrent(i, i['provider_name'], info)
		result = {value['hash']: value for value in result}.values()



		self.runtime = time.time() - start_time
		sources_list = tools.SourceSorter(info).sort_sources(result)
		torrent_results = sources_list
		[self.sources_information['allTorrents'].update({torrent['hash']: torrent}) for torrent in torrent_results]

		log(str(len(torrent_results)) + str('__CACHE_CHECK__'))
		#TorrentCacheCheck._realdebrid_worker(self, torrent_results, info)
		for i in torrent_results:
			self.runtime = time.time() - start_time
			TorrentCacheCheck(self)._realdebrid_worker( [i], info)
			if self.canceled or self.runtime >= self.timeout:
				log('timout')
				break
			#print(TorrentCacheCheck(self).torrent_cache_return())

		#allTorrents = []
		#for i in self.sources_information['allTorrents']:
		#	allTorrents.append(i)
		#for i in reversed(allTorrents):
		#	if i in self.non_working_hashes:
		#		self.sources_information['allTorrents'].pop(i)
		self._update_progress()
		return self._finalise_results()



	def _init_providers(self):
		sys.path.append(tools.ADDON_USERDATA_PATH)
		try:
			if tools.ADDON_USERDATA_PATH not in sys.path:
				sys.path.append(tools.ADDON_USERDATA_PATH)
				providers2 = importlib.import_module("providers2")
			else:
				providers2 = reload_module(importlib.import_module("providers2"))
		except ValueError:
			log('No providers installed', 'warning')
			return

		#providers_dict = {'hosters': [], 
		#'torrent': [('providers2.a4kScrapers.en.torrent', 'bitlord', 'a4kScrapers'), 
		#('providers2.a4kScrapers.en.torrent', 'bitsearch', 'a4kScrapers'), 
		#('providers2.a4kScrapers.en.torrent', 'btdig', 'a4kScrapers'), 
		#('providers2.a4kScrapers.en.torrent', 'cached', 'a4kScrapers'), 
		#('providers2.a4kScrapers.en.torrent', 'glo', 'a4kScrapers'), 
		#('providers2.a4kScrapers.en.torrent', 'kickass', 'a4kScrapers'), 
		#('providers2.a4kScrapers.en.torrent', 'lime', 'a4kScrapers'), 
		#('providers2.a4kScrapers.en.torrent', 'magnetdl', 'a4kScrapers'), 
		#('providers2.a4kScrapers.en.torrent', 'piratebay', 'a4kScrapers'), 
		##('providers2.a4kScrapers.en.torrent', 'rutor', 'a4kScrapers'), 
		#('providers2.a4kScrapers.en.torrent', 'showrss', 'a4kScrapers'), 
		#('providers2.a4kScrapers.en.torrent', 'torrentdownload', 'a4kScrapers'), 
		#('providers2.a4kScrapers.en.torrent', 'torrentio', 'a4kScrapers'), 
		#('providers2.a4kScrapers.en.torrent', 'torrentz2', 'a4kScrapers'), 
		#('providers2.a4kScrapers.en.torrent', 'yts', 'a4kScrapers')], 
		#'adaptive': []}
		#providers_dict = providers.get_relevant(self.language)
		#log(providers_dict)
		
		#providers_dict = get_providers_dict()
		providers_dict = get_providers()

		torrent_providers = providers_dict['torrent']
		#for i in torrent_providers:
		#	tools.log(i)
		try:
			self.torrent_providers = torrent_providers
		except:
			log('EXCEPT__init_providers',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

	def _exit_thread(self, provider_name):
		if provider_name in self.sources_information['statistics']['remainingProviders']:
			self.sources_information['statistics']['remainingProviders'].remove(provider_name)

	def _process_provider_torrent(self, torrent, provider_name, info):
		torrent['type'] = 'torrent'
		torrent['provider_name'] = provider_name

		log(torrent['release_title'])
		if not torrent.get('info'):
			torrent['info'] = tools.get_info(torrent['release_title'])

		if torrent.get("quality") not in tools.approved_qualities_set:
			torrent['quality'] = tools.get_quality(torrent['release_title'])

		torrent['hash'] = torrent.get('hash', self.hash_regex.findall(torrent['magnet'])[0]).lower()
		torrent['pack_size'], torrent['size'] = self._torrent_filesize(torrent, info)
		if len(str(torrent['size'])) == 7 and torrent['size'] == torrent['pack_size']:
			torrent['size'] = torrent['size']/1024
			torrent['pack_size'] = torrent['pack_size']/1024
		torrent['seeds'] = self._torrent_seeds(torrent)

		if 'provider_name_override' in torrent:
			torrent['provider'] = torrent['provider_name_override']
		else:
			torrent['provider'] = provider_name

	def _get_torrent(self, info, provider):
		# Extract provider name from Tuple
		provider_name = provider[1].upper()

		if provider[3] == False or provider[3] == 'False':
			self.sources_information['statistics']['remainingProviders'].remove(provider_name)
			log("Skipping provider: {} - DISABLED".format(provider_name),
				  "warning")
			return

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
				#log(simple_info)
				#log(info)
				torrent_results = provider_source.episode(simple_info, info)
			else:
				log(simple_info)
				log(info)
				simple_info = tools._build_simple_movie_info(info)

				try:
					# new `simple_info`-based call
					torrent_results = provider_source.movie(simple_info, info)
				except AttributeError:
					try: 
						torrent_results = provider_source.movie(simple_info, info)
					except AttributeError: 
						self.sources_information['statistics']['remainingProviders'].remove(provider_name)
						return
				except TypeError:
					# legacy calls
					try:
						torrent_results = provider_source.movie(
							info['info']['title'],
							str(info['info']['year']),
							info['info'].get('imdb_id'),
						)
					except (TypeError, AttributeError):
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
			log(provider_name)
			log('EXCEPTION',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			#raise tools.PreemptiveCancellation('Pre-emptive termination has stopped this request111')
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
		#log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
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
			log('_prem_terminate',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			#tools.PRE_TERM_BLOCK = True
			#return True

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
		#tools.log(len(str(size)), torrent)
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
	def torrent_cache_return(self):
		return self.scraper_class.sources_information

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
			#if 'infringing_file' in str(real_debrid_cache):
			#	#self.scraper_class.non_working_hashes.append(source['hash'])
			#print(real_debrid_cache)
			for i in torrent_list:
				#try:
				if 1==1:
					if 'rd' not in real_debrid_cache.get(i['hash'], {}):
						self.scraper_class.non_working_hashes.append(i['hash'])
						continue
					if len(real_debrid_cache[i['hash']]['rd']) >= 1:
						if self.scraper_class.media_type == 'episode':
							self._handle_episode_rd_worker(i, real_debrid_cache, info)
						else:
							self._handle_movie_rd_worker(i, real_debrid_cache)
					#i['debrid_provider'] = 'real_debrid'
					#self.store_torrent(i)
				#except KeyError:
				#	pass
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
		#log(real_debrid_cache[source['hash']]['rd'])
		#log(source)
		for storage_variant in real_debrid_cache[source['hash']]['rd']:
			if not self.rd_api.is_streamable_storage_type(storage_variant):
				continue

			if tools.get_best_episode_match('filename', storage_variant.values(), info):
				source['debrid_provider'] = 'real_debrid'
				self.store_torrent(source)
				break