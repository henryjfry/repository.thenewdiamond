# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import importlib
import os, json
import sys
import shutil
import re

import tools, source_tools
#import queue
#import threading, time, random
from a4kSubtitles.lib import utils


from inspect import currentframe, getframeinfo
#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))


from source_tools import get_guess
import distance 

import importlib
try:
	from importlib import reload as reload_module  # pylint: disable=no-name-in-module
except ImportError:
	# Invalid version of importlib
	from imp import reload as reload_module

META = None

import struct, os
#import urllib
__64k = 65536
__longlong_format_char = 'q'
__byte_size = struct.calcsize(__longlong_format_char)

def first_last_64kb(url):
	import requests
	import tempfile
	from urllib3.exceptions import IncompleteRead

	def download_last_64kb(url):
		# Create a temporary file to store the content
		with tempfile.NamedTemporaryFile(delete=False) as temp_file:
			try:
				# Make the request with the Range header to download the last 64 KB
				headers = {'Range': 'bytes=%s' % str(__64k*-1)}
				with requests.get(url, headers=headers, stream=True) as response:
					response.raise_for_status()
					# Write the content to the temporary file
					for chunk in response.iter_content(chunk_size=1024):
						temp_file.write(chunk)
				# Return the path to the temporary file
				return temp_file.name
			except IncompleteRead as e:
				# Handle the incomplete read error
				print(f"IncompleteRead error: {e}")
				if os.path.exists(temp_file.name):
					os.remove(temp_file.name)

	def download_last_64kb_2(url):
		# Create a temporary file to store the content
		with tempfile.NamedTemporaryFile(delete=False) as temp_file:
			try:
				# Make the request with the Range header to download the last 64 KB
				response = requests.head(url, verify=False)
				filesize = int(response.headers['content-length'])
				if filesize < __64k * 2:
					try: filesize = int(str(response.headers['content-range']).split('/')[1])
					except: pass
				headers = {"Range": 'bytes=%s-%s' % (filesize - __64k, filesize)}
				with requests.get(url, headers=headers, stream=True) as response:
					response.raise_for_status()
					# Write the content to the temporary file
					for chunk in response.iter_content(chunk_size=1024):
						temp_file.write(chunk)
				# Return the path to the temporary file
				return temp_file.name
			except IncompleteRead as e:
				# Handle the incomplete read error
				print(f"IncompleteRead error: {e}")
				if os.path.exists(temp_file.name):
					os.remove(temp_file.name)

	def download_first_64kb(url):
		# Create a temporary file to store the content
		with tempfile.NamedTemporaryFile(delete=False) as temp_file:
			try:
				# Make the request with the Range header to download the last 64 KB
				headers = {'Range': 'bytes=0-%s' % str(__64k)}
				with requests.get(url, headers=headers, stream=True) as response:
					response.raise_for_status()
					# Write the content to the temporary file
					for chunk in response.iter_content(chunk_size=1024):
						temp_file.write(chunk)
				# Return the path to the temporary file
				return temp_file.name
			except IncompleteRead as e:
				# Handle the incomplete read error
				print(f"IncompleteRead error: {e}")
				if os.path.exists(temp_file.name):
					os.remove(temp_file.name)
	try: 
		last_64kb = download_last_64kb(url)
	except: 
		last_64kb = download_last_64kb_2(url)
	first_64kb = download_first_64kb(url)
	return first_64kb, last_64kb


def temp_file():
	import tempfile
	file = tempfile.NamedTemporaryFile()
	filename = file.name
	return filename
	
def is_local(_str):
	from urllib.parse import urlparse
	if os.path.exists(_str):
		return True
	elif urlparse(_str).scheme in ['','file']:
		return True
	return False

def hashFile_url(filepath): 
	#https://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
	#filehash = filesize + 64bit sum of the first and last 64k of the file
	name = filepath.strip()
	filepath = filepath.strip()
	if is_local(filepath):
		local_file = True
	else:
		local_file = False

	tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	if local_file == True and filepath[:4] == 'http':
		tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		local_file = False
	if local_file == False:
		f = None
		url = name
		#from urllib import request
		#request.urlcleanup()
		import requests

		response = requests.head(url)#, verify=False)
		filesize = int(response.headers['content-length'])

		if filesize < __64k * 2:
			try: filesize = int(str(response.headers['content-range']).split('/')[1])
			except: pass

		first_64kb = temp_file()
		last_64kb = temp_file()

		headers = {"Range": 'bytes=0-%s' % (str(__64k -1 ))}
		r = requests.get(url, headers=headers)#, verify=False)
		with open(first_64kb, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024): 
				if chunk: # filter out keep-alive new chunks
					f.write(chunk)

		if filesize > 0:
			headers = {"Range": 'bytes=%s-%s' % (filesize - __64k, filesize-1)}
		else:
			f.close()
			os.remove(first_64kb)
			return "SizeError", 0

		try:
			r = requests.get(url, headers=headers)#, verify=False)
			with open(last_64kb, 'wb') as f:
				for chunk in r.iter_content(chunk_size=1024): 
					if chunk: # filter out keep-alive new chunks
						f.write(chunk)
		except:
			f.close()
			if os.path.exists(last_64kb):
				os.remove(last_64kb)
			if os.path.exists(first_64kb):
				os.remove(first_64kb)
			return 'IOError', 0
		f = open(first_64kb, 'rb')

	try:
		longlongformat = '<q'  # little-endian long long
		bytesize = struct.calcsize(longlongformat) 

		if local_file:
			f = open(name, "rb") 
			filesize = os.path.getsize(name) 
		hash = filesize 

		if filesize < __64k * 2: 
			f.close()
			if local_file == False:
				os.remove(last_64kb)
				os.remove(first_64kb)
			return "SizeError", 0

		range_value = __64k / __byte_size
		range_value = round(range_value)

		for x in range(range_value): 
			buffer = f.read(bytesize) 
			(l_value,)= struct.unpack(longlongformat, buffer)  
			hash += l_value 
			hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  

		if local_file:
			f.seek(max(0,filesize-__64k),0) 
		else:
			f.close() 
			f = open(last_64kb, 'rb')
		for x in range(range_value): 
			buffer = f.read(bytesize) 
			(l_value,)= struct.unpack(longlongformat, buffer)  
			hash += l_value 
			hash = hash & 0xFFFFFFFFFFFFFFFF 
		
		f.close() 
		if local_file == False:
			os.remove(last_64kb)
			os.remove(first_64kb)
		returnedhash =  "%016x" % hash 
		return returnedhash, filesize

	except(IOError): 
		if local_file == False:
			os.remove(last_64kb)
			os.remove(first_64kb)
		return 'IOError', 0

def set_size_and_hash_url(meta, filepath):
	if meta == None and META != None:
		meta = META
	#f = xbmcvfs.File(filepath)
	#https://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
	#filehash = filesize + 64bit sum of the first and last 64k of the file
	#tools.log(hashFile_url('https://static.opensubtitles.org/addons/avi/breakdance.avi'))
	returnedhash, filesize = hashFile_url(filepath)
	meta['filehash'] = returnedhash
	meta['filesize'] = filesize
	return meta

def set_size_and_hash(meta, filepath):
	if meta == None and META != None:
		meta = META
	#f = xbmcvfs.File(filepath)
	returnedhash, filesize = hashFile_url(filepath)
	meta['filehash'] = returnedhash
	meta['filesize'] = filesize
	return meta


def get_subtitles_meta(VIDEO_META, file_path):
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
	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	#try:
	from urllib.parse import unquote
	if 1==1:
		VIDEO_META['season'] = str(VIDEO_META['season'] )
		VIDEO_META['episode'] = str(VIDEO_META['episode'])
	#except:
	#	pass
	#try:
	download_type = VIDEO_META.get('download_type',False)

	#daily_show_flag = False
	#if download_type != 'movie':
	#	if VIDEO_META['air_date'][-2:] in VIDEO_META['name'] and VIDEO_META['air_date'][:4] in VIDEO_META['name']:
	#		import datetime
	#		if datetime.datetime.strptime(VIDEO_META['air_date'], '%Y-%m-%d').strftime('%B %d, %Y') in VIDEO_META['name']:
	#			daily_show_flag = True

	#if daily_show_flag:
	#	VIDEO_META['name'] = VIDEO_META['name'].replace(datetime.datetime.strptime(VIDEO_META['air_date'], '%Y-%m-%d').strftime('%B %d, %Y'), datetime.datetime.strptime(VIDEO_META['air_date'], '%Y-%m-%d').strftime('%Y.%m.%d'))
	#	VIDEO_META['originaltitle'] = VIDEO_META['name']
	#	VIDEO_META['title'] = VIDEO_META['name']
	#	VIDEO_META['info']['title'] = VIDEO_META['name']
	#	VIDEO_META['info']['originaltitle'] = VIDEO_META['name']
	#	

	if 1==1:
		VIDEO_META['file_name'] = unquote(os.path.basename(file_path))
		VIDEO_META['filename'] = unquote(VIDEO_META['file_name'])
		VIDEO_META['filename_without_ext'] = unquote(os.path.splitext(VIDEO_META['file_name'])[0])
		VIDEO_META['subs_filename'] = unquote(VIDEO_META['filename_without_ext'] + '.srt')
		#tools.VIDEO_META = VIDEO_META
		#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		#tools.log('VIDEO_META',VIDEO_META, 'file_path',file_path)
		if 'http' in str(file_path):
			VIDEO_META2 = set_size_and_hash_url(meta=VIDEO_META, filepath=file_path)
		else:
			VIDEO_META2 = set_size_and_hash(meta=VIDEO_META, filepath=file_path)
		#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		#tools.log('VIDEO_META2',VIDEO_META2, 'file_path',file_path)
	#except:
	#	pass
	#os.environ['A4KSUBTITLES_API_MODE'] = str({'kodi': 'false'})
	#try: import subtitles
	#except: from a4kscrapers_wrapper import subtitles
	#subfile = subtitles.SubtitleService().get_subtitle()
	#VIDEO_META['SUB_FILE'] = tools.SUB_FILE
	#tools.VIDEO_META = VIDEO_META
	
	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	#tools.log('VIDEO_META', VIDEO_META,'json.dumps???????????????????????')
	VIDEO_META = VIDEO_META2
	if VIDEO_META.get('tvshowtitle','') != '':
		if (VIDEO_META['tvshowtitle'] in VIDEO_META['aliases']) == False:
			VIDEO_META['aliases'].append(VIDEO_META['tvshowtitle'])
		VIDEO_META['aliases'] = VIDEO_META['aliases'][::-1]
	#tools.VIDEO_META['SUB_FILE'] = tools.SUB_FILE
	#json_data = json.dumps(VIDEO_META, indent=2)
	#curr_meta = os.path.join(tools.ADDON_USERDATA_PATH, 'curr_meta.json')
	#tools.log('write_all_text')
	#tools.log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	#tools.write_all_text(curr_meta, json_data)
	#tools.log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	return VIDEO_META



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
	if 1==1:
		VIDEO_META['season'] = str(VIDEO_META['season'] )
		VIDEO_META['episode'] = str(VIDEO_META['episode'])

	if 1==1:
		VIDEO_META['file_name'] = os.path.basename(file_path)
		VIDEO_META['filename'] = VIDEO_META['file_name']
		VIDEO_META['filename_without_ext'] = os.path.splitext(VIDEO_META['file_name'])[0]
		VIDEO_META['subs_filename'] = VIDEO_META['filename_without_ext'] + '.srt'
		#tools.VIDEO_META = VIDEO_META
		if 'http' in str(file_path):
			VIDEO_META = set_size_and_hash_url(meta=VIDEO_META, filepath=file_path)
		else:
			VIDEO_META = set_size_and_hash(meta=VIDEO_META, filepath=file_path)
	tools.VIDEO_META = VIDEO_META
	os.environ['A4KSUBTITLES_API_MODE'] = str({'kodi': 'false'})
	from a4kscrapers_wrapper import subtitles
	subfile = subtitles.SubtitleService().get_subtitle()
	tools.VIDEO_META['SUB_FILE'] = tools.SUB_FILE

	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	#tools.log('tools.VIDEO_META', tools.VIDEO_META)
	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	#tools.log(META, VIDEO_META)
	return tools.VIDEO_META


def get_subtitles_list(VIDEO_META, file_path):
	#from a4kscrapers_wrapper import subs

	meta = get_subtitles_meta(VIDEO_META, file_path)
	#tools.VIDEO_META = VIDEO_META
	META = meta
	VIDEO_META = meta
	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	#tools.log('META',META,'VIDEO_META', VIDEO_META,'meta',meta)
	#tools.VIDEO_META = meta
	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	#tools.log('tools.VIDEO_META', tools.VIDEO_META)

	subfile = SubtitleService(meta).get_subtitle()
	tools.SUB_FILE = subfile
	#tools.VIDEO_META['SUB_FILE'] = subfile
	#tools.log('SUBTITLES_____________',tools.VIDEO_META)
	#SUB_FILE = tools.VIDEO_META['SUB_FILE']
	try: 
		SUB_FILE = tools.VIDEO_META['SUB_FILE']
	except: 
		SUB_FILE = meta['SUB_FILE']
		tools.VIDEO_META = meta
	#tools.log(tools.VIDEO_META,meta)
	try: 
		SUB_FILE_FORCED = tools.VIDEO_META['SUB_FILE_FORCED']
	except: 
		SUB_FILE_FORCED = meta['SUB_FILE_FORCED']
		tools.VIDEO_META = meta
	subs_list = []
	if str(SUB_FILE) != '' and SUB_FILE != None:
		subs_list.append(SUB_FILE)
	if str(SUB_FILE_FORCED) != '' and SUB_FILE_FORCED != None:
		subs_list.append(SUB_FILE_FORCED)
	return subs_list



class SubtitleService(object):
	"""
	Connects to available subtitle services and retrieves available subtitles for media
	"""

	def __init__(self, meta):
		#self.task_queue = queue.Queue()
		#self.subtitle_languages = g.get_kodi_subtitle_languages()
		#self.preferred_language = g.get_kodi_preferred_subtitle_language()
		#self.base_request = {
		#	"languages": ",".join(self.subtitle_languages),
		#	"preferredlanguage": self.preferred_language,
		#}

		if meta == None and META != None:
			meta = META
		self.VIDEO_META = meta
		#tools.VIDEO_META = self.VIDEO_META
		#tools.log('SUBS.PY',meta, tools.VIDEO_META)
		self.base_request = {'action': 'search', 'languages': 'English', 'preferredlanguage': 'forced_only'}
		self.base_request = {'action': 'search', 'languages': 'English', 'preferredlanguage': 'English'}
		self.base_request['VIDEO_META'] = meta
		tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), self.base_request)

		self.sources = [A4kSubtitlesAdapter(self.VIDEO_META)]

	def get_subtitle(self):
		"""
		Fetch subtitle source
		:return: Url to subtitle
		:rtype: str
		"""
		#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		#if self.VIDEO_META == None:
		#	self.VIDEO_META = json.loads(tools.read_all_text(os.path.join(tools.ADDON_USERDATA_PATH, 'curr_meta.json')))
		#	#tools.VIDEO_META = self.VIDEO_META
		#	self.base_request['VIDEO_META'] = self.VIDEO_META
		#	tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), self.base_request)

		result = None
		sources = [A4kSubtitlesAdapter(self.VIDEO_META)]
		if sources is None:
			return None
		result_store = []
		total_result = 0
		for r in sources:
			#self.base_request['VIDEO_META'] = self.VIDEO_META
			result = r.search(self.base_request)
			#tools.log(result)
			if total_result > 99:
				break
			for i in result:
				i['VIDEO_META'] = self.VIDEO_META
				if not "impaired': 'true" in str(i):
					result_store.append(i)
					total_result = total_result + 1
				if total_result > 99:
					break

		#tools.log(result_store)
		download_type = self.VIDEO_META.get('download_type',False)

		sources = [A4kSubtitlesAdapter(self.VIDEO_META)]
		#result_store[0]['VIDEO_META'] = self.VIDEO_META
		#tools.log(result_store)
		foreign_parts = []
		normal_subs = []
		foreign_parts_flag = False
		result_foreign = None
		sub_result = None
		for i in result_store:
			if 'foreign' in str(i).lower() or 'forced' in str(i).lower() or 'non english' in str(i).lower():
				foreign_parts.append(i)
				foreign_parts_flag = True
			else:
				normal_subs.append(i)
		if foreign_parts_flag:
			shutil.rmtree(utils.temp_dir2, ignore_errors=True)
			if not os.path.exists(utils.temp_dir2):
				os.mkdir(utils.temp_dir2)
			for r in sources:
				for i in foreign_parts:
					sub_result = r.download(i)
					sub_size = os.path.getsize(sub_result)
					print(foreign_parts)
					if sub_result and sub_size > 0:
						break
				try: tools.log(foreign_parts[0]['action_args']['filename'], foreign_parts[0]['service'])
				except: tools.log(foreign_parts[0]['name'], foreign_parts[0]['service'])
				
			#result_foreign = os.path.splitext(sub_result)[0] + '.FOREIGN.PARTS' +os.path.splitext(sub_result)[1]
			result_foreign = os.path.splitext(sub_result)[0] + '.FORCED' +os.path.splitext(sub_result)[1]
			result_foreign = os.path.basename(result_foreign)
			result_foreign1 = os.path.join(utils.temp_dir2, result_foreign)
			result_foreign2 = os.path.join(utils.temp_dir, result_foreign)

			os.rename(sub_result, result_foreign1)
		for r in sources:
			try: 
				for i in normal_subs:
					sub_result = r.download(i)
					sub_size = os.path.getsize(sub_result)
					if sub_size > 0:
						break

				try: tools.log(normal_subs[0]['action_args']['filename'], normal_subs[0]['service'])
				except: tools.log(normal_subs[0]['name'], normal_subs[0]['service'])
			except Exception as e: 
				if 'zipfile.BadZipFile' in str(e):
					pass
			if sub_result:
				break
		if foreign_parts_flag:
			os.rename(result_foreign1, result_foreign2)
			result_foreign = result_foreign2
			shutil.rmtree(utils.temp_dir2, ignore_errors=True)

		self.VIDEO_META['SUB_FILE'] = ''
		self.VIDEO_META['SUB_FILE_FORCED'] = ''
		tools.log(sub_result)
		if sub_result:
			if os.path.exists(sub_result):
				self.VIDEO_META['SUB_FILE'] = sub_result
			else:
				self.VIDEO_META['SUB_FILE'] = ''
		if result_foreign:
			if os.path.exists(result_foreign):
				self.VIDEO_META['SUB_FILE_FORCED'] = result_foreign
			else:
				self.VIDEO_META['SUB_FILE_FORCED'] = ''
		#tools.VIDEO_META['SUB_FILE_FORCED'] = result_foreign
		tools.VIDEO_META = self.VIDEO_META
		#tools.log(self.VIDEO_META)
		#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		#tools.log('self.VIDEO_META',self.VIDEO_META,'result_foreign',result_foreign,'result',sub_result)
		tools.log('result_foreign',result_foreign,'result',sub_result)#
		if os.path.exists(utils.temp_dir2):
			shutil.rmtree(utils.temp_dir2, ignore_errors=True)
		#tools.log('normal_subs[0]', normal_subs[0])
		return sub_result


class A4kSubtitlesAdapter(object):
	"""
	Ease of use adapter for A4kSubtitles
	"""

	def __init__(self, meta):

		#path = tools.translate_path(
		#	os.path.join(g.ADDONS_PATH, "/plugin.video.seren_downloader/resources/lib/modules")
		#)
		#try:
		#	sys.path.append(path)
		#	self.service = importlib.import_module("a4kSubtitles.api").A4kSubtitlesApi(
		#		{"kodi": tools.is_stub()}
		#	)
		#	self.enabled = True
		#except ImportError:
		#	self.enabled = False
		try: api = importlib.import_module("a4kSubtitles.api")
		except: api = reload_module(importlib.import_module("a4kSubtitles.api"))
		#from a4kSubtitles import api

		self.VIDEO_META = meta
		self.service = api.A4kSubtitlesApi(
			{"kodi": False}
		)
		self.service.VIDEO_META = meta

		self.enabled = True

	def search(self, request, **extra):
		"""
		Search for a subtitle
		:param request: Dictionary containing currently available subtitles and the preferred language
		:type request: dict
		:param extra: Kwargs to provide video meta and settings to A4kSubtitles
		:type extra: dict
		:return: Available subtitle matches
		:rtype: list
		"""
		video_meta = extra.pop("video_meta", None)
		settings = extra.pop("settings", None)
		return self.service.search(request, video_meta=self.VIDEO_META, settings=settings)

	def download(self, request, **extra):
		"""
		Downloads requested subtitle
		:param request: Selected subtitle from search results
		:type request: dict
		:param extra: Kwargs, set settings to settings to request to use
		:type extra: dict
		:return: Path to subtitle
		:rtype: str
		"""
		settings = extra.pop("settings", None)
		return self.service.download(request, settings)
		#try:
		#	
		#except (OSError, IOError):
		#	tools.log("Unable to download subtitle, file already exists", "error")
		#except Exception as e:
		#	tools.log("Unknown error acquiring subtitle: {}".format(e), "error")
		#	#g.log_stacktrace()
