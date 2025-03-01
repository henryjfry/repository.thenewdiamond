import requests
import unicodedata
import hashlib
import time

import glob
import os

import get_meta, tools, real_debrid, source_tools
import urllib
from urllib.parse import unquote

def rarbg_4k_magnets():
	tools.log('Starting_rapbg_2160')
	rd_api = real_debrid.RealDebrid()

	#list_of_files = glob.glob(os.path.join(tools.ADDON_USERDATA_PATH, 'TheMovieDB','*') # * means all if need specific format then *.csv
	#for i in sorted(list_of_files, key=os.path.getctime, reverse=True):
	#	found_flag = False
	#	with open(i, 'r') as fp:
	#		for l_no, line in enumerate(fp):
	#			# search string
	#			if 'show_id' in line:
	#				#print('string found in a file')
	#				#print('Line Number:', l_no)
	#				#print('Line:', line)
	#				# don't look for next lines
	#				found_flag = True
	#				tmdb_id = line.split('show_id')[1].split(',')[0].split(': ')[1]
	#				break
	#	if found_flag:
	#		break


	cache_days = 30

	meta = get_meta.get_episode_meta(season=1,episode=1,tmdb=68001)
	info = meta['episode_meta']

	#response = requests.get('https://therarbg.com/latest/rss/tv')

	response = requests.get('https://therarbg.com/get-posts/keywords:2160p:category:TV:time:1D')

	magnets_list = response.text.split('"table1head"')[1].split('</tbody>')[0].split('<div class="wrapper">\n')

	magnets_results = []
	for i in magnets_list:
		if 'href="/post-detail/' in i:
			sub_url = i.split('href="')[1].split('"\n')[0]
			sub_response = requests.get('https://therarbg.com/' + sub_url)
			#print(sub_response)
			magnet = sub_response.text.split('<button onclick=\"copy(\'')[1].split('\',\'#copy_magnet')[0]
			title = i.split('style="font-weight:')[1].split('>')[1].split('</a')[0]
			if '264' in title:
				continue
			try: size = unicodedata.normalize('NFKD', i.split('"sizeCell">')[1].split('</td>')[0])
			except: size = unicodedata.normalize('NFKD', i.split('"sizeCell"')[1].split('>')[1].split('</td')[0])
			seeds = i.split('"color: green">')[1].split('</td>')[0]
			leechers = i.split('"color: red">')[1].split('</td>')[0]
			title2 = unquote(magnet.split('&amp;tr=')[0].split('&amp;dn=')[1])
			curr_dict = {'title2': title2, 'title': title, 'size': size, 'seeds': seeds, 'leechers': leechers, 'magnet': magnet, 'info': tools.get_info(title2), 'quality': tools.get_quality(title2)}

			#source_list = []
			#source_list.append({'filename': title, 'pack_size': size, 'size': size, 'info': tools.get_info(title2), 'quality': tools.get_quality(title2)})
			#source_list.append({'filename': title, 'pack_size': size, 'size': size, 'info': tools.get_info(source_tools.clean_title(title2)), 'quality': tools.get_quality(source_tools.clean_title(title2))})
			#new_source_list = list(tools.SourceSorter(info).filter_sources2(source_list))
			#if len(new_source_list) == 0:
			#	continue

			magnets_results.append(curr_dict)


	new_magnets_results = list(tools.SourceSorter(info).filter_sources2(magnets_results))
	for i in new_magnets_results:
		magnet = i['magnet']
		url = magnet.split('&amp;dn=')[0]
		now = time.time()
		url = url.encode('utf-8')
		hashed_url = hashlib.md5(url).hexdigest()
		#try: cache_path = os.path.join(g.ADDON_USERDATA_PATH, folder)
		#except: cache_path = os.path.join(tools.ADDON_USERDATA_PATH, folder)
		cache_path = os.path.join(tools.ADDON_USERDATA_PATH, 'rss')

		if not os.path.exists(cache_path):
			os.mkdir(cache_path)
		cache_seconds = int(cache_days * 86400.0)
		path = os.path.join(cache_path, '%s.txt' % hashed_url)
		torr_info = None
		if os.path.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
			torr_info = tools.read_all_text(path)
			try: torr_info = eval(torr_info)
			except: pass
		else:
			response = rd_api.add_magnet(magnet)
			try: torr_id = response['id']
			except: continue
			response = rd_api.torrent_select_all(torr_id)
			torr_info = rd_api.torrent_info(torr_id)
			try:
				#magnet = json.loads(response)
				#save_to_file(results, hashed_url, cache_path)
				#file_path = os.path.join(cache_path, hashed_url)
				tools.write_all_text(path, str(torr_info))
				#tools.log('RSS_ADDED_MAGNET',torr_info['filename'])
			except:
				tools.log('Exception: Could not get new JSON data from %s. Tryin to fallback to cache' % url)
				tools.log(torr_info)
				torr_info = tools.read_all_text(path) if os.path.exists(path) else []
			try: test = str(response.text)
			except: test = str(response)
			if '{files} is missing' in test:
				rd_api.delete_torrent(torr_id)
			try:
				if response.status_code > 200 and  response.status_code < 300:
					tools.log(i['title2'], 'ADDED_RARBG')
			except:
				continue
			if not torr_info:
				continue



	meta = get_meta.get_movie_meta(movie_name='Point Break',year=1991)
	info = meta

	response = requests.get('https://therarbg.com/get-posts/keywords:2160p:category:Movies:time:1D')

	magnets_list = response.text.split('"table1head"')[1].split('</tbody>')[0].split('<div class="wrapper">\n')

	magnets_results = []
	for i in magnets_list:
		if 'href="/post-detail/' in i:
			sub_url = i.split('href="')[1].split('"\n')[0]
			sub_response = requests.get('https://therarbg.com/' + sub_url)
			#print(sub_response)
			magnet = sub_response.text.split('<button onclick=\"copy(\'')[1].split('\',\'#copy_magnet')[0]
			title = i.split('style="font-weight:')[1].split('>')[1].split('</a')[0]
			if '264' in title:
				continue
			try: size = unicodedata.normalize('NFKD', i.split('"sizeCell">')[1].split('</td>')[0])
			except: size = unicodedata.normalize('NFKD', i.split('"sizeCell"')[1].split('>')[1].split('</td')[0])
			seeds = i.split('"color: green">')[1].split('</td>')[0]
			leechers = i.split('"color: red">')[1].split('</td>')[0]
			title2 = unquote(magnet.split('&amp;tr=')[0].split('&amp;dn=')[1])
			curr_dict = {'title2': title2, 'title': title, 'size': size, 'seeds': seeds, 'leechers': leechers, 'magnet': magnet, 'info': tools.get_info(title2), 'quality': tools.get_quality(title2)}

			#source_list = []
			#source_list.append({'filename': title, 'pack_size': size, 'size': size, 'info': tools.get_info(title2), 'quality': tools.get_quality(title2)})
			#source_list.append({'filename': title, 'pack_size': size, 'size': size, 'info': tools.get_info(source_tools.clean_title(title2)), 'quality': tools.get_quality(source_tools.clean_title(title2))})
			#new_source_list = list(tools.SourceSorter(info).filter_sources2(source_list))
			#if len(new_source_list) == 0:
			#	continue

			magnets_results.append(curr_dict)

	new_magnets_results = list(tools.SourceSorter(info).filter_sources2(magnets_results))
	for i in new_magnets_results:
		magnet = i['magnet']
		url = magnet.split('&amp;dn=')[0]
		now = time.time()
		url = url.encode('utf-8')
		hashed_url = hashlib.md5(url).hexdigest()
		#try: cache_path = os.path.join(g.ADDON_USERDATA_PATH, folder)
		#except: cache_path = os.path.join(tools.ADDON_USERDATA_PATH, folder)
		cache_path = os.path.join(tools.ADDON_USERDATA_PATH, 'rss')

		if not os.path.exists(cache_path):
			os.mkdir(cache_path)
		cache_seconds = int(cache_days * 86400.0)
		path = os.path.join(cache_path, '%s.txt' % hashed_url)
		torr_info = None
		if os.path.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
			torr_info = tools.read_all_text(path)
			try: torr_info = eval(torr_info)
			except: pass
		else:
			response = rd_api.add_magnet(magnet)
			try: torr_id = response['id']
			except: continue
			response = rd_api.torrent_select_all(torr_id)
			torr_info = rd_api.torrent_info(torr_id)
			try:
				#magnet = json.loads(response)
				#save_to_file(results, hashed_url, cache_path)
				#file_path = os.path.join(cache_path, hashed_url)
				tools.write_all_text(path, str(torr_info))
				#tools.log('RSS_ADDED_MAGNET',torr_info['filename'])
			except:
				tools.log('Exception: Could not get new JSON data from %s. Tryin to fallback to cache' % url)
				tools.log(torr_info)
				torr_info = tools.read_all_text(path) if os.path.exists(path) else []
			try: test = str(response.text)
			except: test = str(response)
			if '{files} is missing' in test:
				rd_api.delete_torrent(torr_id)
				continue
			if response.status_code > 200 and  response.status_code < 300:
				tools.log(i['title2'], 'ADDED_RARBG')
			if not torr_info:
				continue

