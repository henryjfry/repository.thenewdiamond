import unicodedata
import hashlib, json

import copy
import importlib
import json
import random
import re
import sys
import time
#from collections import OrderedDict, Counter

import inspect
import requests
import string
import os
try:
	unicode = unicode  # noqa # pylint: disable=undefined-variable
except NameError:
	unicode = str

from inspect import currentframe, getframeinfo
#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

folder = str(os.path.split(str(getframeinfo(currentframe()).filename))[0])
current_directory = folder
sys.path.append(current_directory)
sys.path.append(current_directory.replace('a4kscrapers_wrapper',''))

#current_directory = str(getframeinfo(currentframe()).filename.replace(os.path.basename(getframeinfo(currentframe()).filename),'').replace('','')[:-1])
#sys.path.append(current_directory)
#sys.path.append(current_directory.replace('a4kscrapers_wrapper',''))

BROWSER_AGENTS = [
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537."
	"36 Edge/12.246",
	"Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) "
	"Version/9.0.2 Safari/601.3.9"
	"Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
	"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
]

tools_stop_downloader = None

#ADDON_USERDATA_PATH = './user_data'
try:
	#from resources.lib import Utils
	import xbmc,xbmcvfs
	from resources.lib.library import addon_ID
	ADDON_PATH = xbmcvfs.translatePath('special://home/addons/'+str(addon_ID()))
	ADDON_DATA_PATH = xbmcvfs.translatePath('special://profile/addon_data/'+str(addon_ID()))
	ADDON_USERDATA_PATH = ADDON_DATA_PATH
	ADDON_USERDATA_PATH_1 = ADDON_USERDATA_PATH
	ADDON_NAME = addon_ID()
	A4KPROVIDERS_PATH = os.path.join(ADDON_USERDATA_PATH, 'providers2')
	A4KPROVIDERS_PATH_original = os.path.join(ADDON_USERDATA_PATH, 'providers')
	SETTING_XML = os.path.join(ADDON_USERDATA_PATH, 'settings.xml')
	PROVIDERS_JSON = os.path.join(ADDON_USERDATA_PATH, 'provider.json')
	OPENSUB_USERNAME = 'username'
	OPENSUB_PASSWORD = 'password'
	PID_FILE = os.path.join(ADDON_USERDATA_PATH, 'pid')
	diamond = True

except:
	ADDON_PATH = folder.replace('a4kscrapers_wrapper','')
	ADDON_USERDATA_PATH = os.path.join(folder, 'user_data')
	ADDON_USERDATA_PATH_1 = ADDON_USERDATA_PATH
	if not os.path.exists(ADDON_USERDATA_PATH):
		ADDON_USERDATA_PATH = folder.replace('.kodi/addons', '.kodi/userdata/addon_data').replace('.kodi\\addons', '.kodi\\userdata\\addon_data').replace('a4kscrapers_wrapper','')
	elif not os.path.exists(ADDON_USERDATA_PATH) or not 'user' in str(ADDON_USERDATA_PATH):
		ADDON_USERDATA_PATH = os.path.join(folder, 'user_data')
	ADDON_NAME = 'plugin.video.a4kWrapper'
	A4KPROVIDERS_PATH = os.path.join(ADDON_USERDATA_PATH, 'providers2')
	A4KPROVIDERS_PATH_original = os.path.join(ADDON_USERDATA_PATH, 'providers')
	SETTING_XML = os.path.join(ADDON_USERDATA_PATH, 'settings.xml')
	PROVIDERS_JSON = os.path.join(ADDON_USERDATA_PATH, 'provider.json')
	OPENSUB_USERNAME = 'username'
	OPENSUB_PASSWORD = 'password'
	PID_FILE = os.path.join(ADDON_USERDATA_PATH, 'pid')
	diamond = False

if not os.path.exists(SETTING_XML):
	ADDON_USERDATA_PATH = ADDON_USERDATA_PATH_1
	A4KPROVIDERS_PATH = os.path.join(ADDON_USERDATA_PATH, 'providers2')
	A4KPROVIDERS_PATH_original = os.path.join(ADDON_USERDATA_PATH, 'providers')
	SETTING_XML = os.path.join(ADDON_USERDATA_PATH, 'settings.xml')
	PID_FILE = os.path.join(ADDON_USERDATA_PATH, 'pid')
	PROVIDERS_JSON = os.path.join(ADDON_USERDATA_PATH, 'provider.json')
	diamond = False

sort_method_names = {
	0: 'None',
	1: '_get_quality_sort_key',
	2: '_get_type_sort_key',
	3: '_get_debrid_priority_key',
	4: '_get_size_sort_key',
	5: '_get_low_cam_sort_key',
	6: '_get_hevc_sort_key',
	7: '_get_hdr_sort_key',
	8: '_get_audio_channels_sort_key'
}
sort_method_list = {
	'0': 'None',
	'1': 'Quality Priority',
	'2': 'Service Type Priority',
	'3': 'Debrid Service Priority',
	'4': 'Size Sort (GB''s)',
	'5': 'Low Quality Cam Sort',
	'6': 'HEVC Sort',
	'7': 'HDR Sort',
	'8': 'Audio Channels Sort'
}

type_priority_settings = {
	0: None,
	1: "cloud",
	2: "adaptive",
	3: "torrent",
	4: "hoster"
}

true_false = {
	'true': 1,
	'false': 0
}

torrent_choices = {
	'Add to RD Cache (whole pack)': 1,
	'Add to RD Cache + Unrestrict (whole pack)': 2,
	'Unrestrict specific files': 3,
	'Add to downloader list (whole pack)': 4,
	'Add to downloader list (episode)': 5,
	'Add to downloader list (whole pack + subtitles)': 6,
	'Add to downloader list (episode + subtitles)': 7,
	'(Uncached) Add to RD (whole pack) ': 8,
	'(Uncached) Add to RD (individual files) ': 9
}

program_choices = {
	'Search Torrent (episode)': 1,
	'Search Torrent (movie)': 2,
	'Start downloader service (if not running)': 3,
	'check downloader status': 4,
	'Setup Providers': 5,
	'enable_disable_providers': 6,
	'setup_userdata_folder': 7,
	'rd_auth': 8,
	'auto_clean_caches': 9,
	'default settings.xml': 10,
	'setup filters/limits/sorting': 11,
	'get current filters/limits/sorting ': 12
}

class global_var:
	
	def __init__(self):
		self.VIDEO_META = None
		self.tools_stop_downloader = None

def setup_userdata():
	import shutil
	if not os.path.exists(ADDON_USERDATA_PATH):
		os.mkdir(ADDON_USERDATA_PATH)
	blank_settings_xml = os.path.join(folder,'blank_settings_xml')
	if not os.path.exists(SETTING_XML):
		shutil.copy(blank_settings_xml, SETTING_XML)

db_con = None
def test_db():
	import sqlite3
	if not os.path.exists(ADDON_USERDATA_PATH):
		setup_userdata()
	cache_path = os.path.join(ADDON_USERDATA_PATH, 'cache.db')
	db_con = sqlite3.connect(cache_path, check_same_thread=False)
	return db_con

def encode_db(sample_string):
	import base64
	sample_string_bytes = sample_string.encode("ascii")
	base64_bytes = base64.b64encode(sample_string_bytes)
	base64_string = base64_bytes.decode("ascii")
	return base64_string

def decode_db(base64_string):
	import base64
	base64_bytes = base64_string.encode("ascii")
	sample_string_bytes = base64.b64decode(base64_bytes)
	sample_string = sample_string_bytes.decode("ascii")
	return sample_string

def write_db(connection=None,url=None, cache_days=7.0, folder=False,cache_val=None, headers=False):
	if db_con == None:
		connection = db_start()
	cur = connection.cursor()
	try: url = url.encode('utf-8')
	except: pass
	hashed_url = hashlib.md5(url).hexdigest()
	cache_seconds = int(cache_days * 86400.0)
	if isinstance(cache_val, str) == True:
		cache_val = encode_db(cache_val)
		cache_type = 'str'
	elif isinstance(cache_val, list) == True or isinstance(cache_val, dict) == True:
		try: 
			cache_val = encode_db(json.dumps(cache_val))
			cache_type = 'json'
		except: 
			cache_val = encode_db(str(cache_val))
			cache_type = 'list'

	expire = round(time.time() + cache_seconds,0)
	sql_query = """
	CREATE TABLE IF NOT EXISTS %s (
		url VARCHAR PRIMARY KEY,
		cache_val BLOB NOT NULL,
		cache_type VARCHAR NOT NULL,
		expire INT NOT NULL
	); 
	""" % (folder)
	sql_result = cur.execute(sql_query).fetchall()
	connection.commit()
	sql_query = """
	INSERT INTO %s (url,cache_val,cache_type,expire)
	VALUES( '%s','%s','%s',%s);
	""" % (folder, hashed_url,cache_val,cache_type,int(expire))
	#sql_result = cur.execute(sql_query).fetchall()
	try: 
		sql_result = cur.execute(sql_query).fetchall()
	except Exception as ex:
		if 'UNIQUE constraint failed' in str(ex):
			sql_query = """
			REPLACE INTO %s (url,cache_val,cache_type,expire)
			VALUES( '%s','%s','%s',%s);
			""" % (folder, hashed_url,cache_val,cache_type,int(expire))
			sql_result = cur.execute(sql_query).fetchall()
	connection.commit()
	cur.close()

def query_db(connection=None,url=None, cache_days=7.0, folder=False, headers=False):
	if db_con == None:
		connection = db_start()
	cur = connection.cursor()
	#if cache_days == 0:
	#	cache_days = 7
	try: url = url.encode('utf-8')
	except: pass
	cache_val = None
	cache_seconds = int(cache_days * 86400.0)
	hashed_url = hashlib.md5(url).hexdigest()

	sql_query = """select cache_val, expire,cache_type from %s
	where url = '%s'
	""" % (folder, hashed_url)

	try: 
		sql_result = cur.execute(sql_query).fetchall()
	except Exception as ex:
		if 'no such table' in str(ex):
			return None
		else:
			xbmc.log(str(ex)+'===>OPENINFO', level=xbmc.LOGINFO)
	if len(sql_result) ==0:
		cur.close()
		return None

	expire = round(time.time() + cache_seconds,0)
	if int(time.time()) >= int(sql_result[0][1]) or expire <= int(sql_result[0][1]) :
		sql_query = """DELETE FROM %s
		where url = '%s'
		""" % (folder, hashed_url)
		sql_result = cur.execute(sql_query).fetchall()
		connection.commit()
		cur.close()
		return None
	else:
		cache_type = sql_result[0][2]
		if cache_type == 'str':
			cache_val = decode_db(sql_result[0][0])
		elif cache_type == 'list':
			cache_val = eval(decode_db(sql_result[0][0]))
		elif cache_type == 'json':
			cache_val = json.loads(decode_db(sql_result[0][0]))
		cur.close()
		return cache_val

db_start = test_db()
db_con = db_start


def findReplace(directory, find, replace, filePattern):
	import os, fnmatch
	for path, dirs, files in os.walk(os.path.abspath(directory)):
		for filename in fnmatch.filter(files, filePattern):
			filepath = os.path.join(path, filename)
			with open(filepath) as f:
				s = f.read()
			s = s.replace(find, replace)
			with open(filepath, "w") as f:
				f.write(s)


def set_setting(setting_name, setting_value):
	#setting_line = '    <setting id="%s">%s</setting>' % (setting_name, setting_value)
	new_setting_file = ''
	update = False
	with open(SETTING_XML) as f:
		lines = f.readlines()
		for line in lines:
			if setting_name in str(line):
				line_split_1 = line.split('"')[0] + '"'
				line_split_2 = setting_name
				line_split_3 = '"' + line.split('"',2)[2].split('>')[0] + '>'
				line_split_4 = setting_value
				try: line_split_5 = '<' + line.split('"',2)[2].split('<')[1]
				except: line_split_5 = '</setting>\n'
				setting_line = str(line_split_1) + str(line_split_2) + str(line_split_3) + str(line_split_4) + str(line_split_5)
				setting_line = setting_line.replace('default="true" />','default="true">')
				setting_line = setting_line.replace(' />','>')
				new_setting_file = new_setting_file + setting_line
				if setting_line != line:
					update = True
			else:
				new_setting_file = new_setting_file + line
	if update == True:
		with open(SETTING_XML, 'w') as file:
			# Write new content to the file
			file.write(new_setting_file)

def get_setting(setting_name, var_type = 'string'):
	return_var = None
	setting_name = setting_name + '"'
	if diamond == False:
		if not os.path.exists(SETTING_XML):
			setup_userdata()

	try:
		with open(SETTING_XML) as f:
			lines = f.readlines()
			for line in lines:
				if setting_name in str(line):
					return_var = line.split('>')[1].split('</')[0]
		if var_type == 'string':
			return_var = str(return_var)
		elif var_type == 'bool':
			if str(return_var).lower() == 'true':
				return_var = True
			if str(return_var).lower() == 'false':
				return_var = False
		elif var_type == 'int':
			return_var = int(return_var)
		elif var_type == 'float':
			return_var = float(return_var)
		return return_var
	except:
		from resources.lib.library import addon_ID
		import xbmcaddon
		return_var = xbmcaddon.Addon(addon_ID()).getSetting(setting_name)
		if var_type == 'string':
			return_var = str(return_var)
		elif var_type == 'bool':
			if str(return_var).lower() == 'true':
				return_var = True
			if str(return_var).lower() == 'false':
				return_var = False
		elif var_type == 'int':
			return_var = int(return_var)
		elif var_type == 'float':
			return_var = float(return_var)
		return return_var


DOWNLOAD_FOLDER = get_setting("DOWNLOAD_FOLDER", 'string')
if diamond:
	fanart_api_key = get_setting("fanart_api", 'string')
	tmdb_API_key = get_setting("tmdb_api", 'string')
	#tvdb_apikey =  get_setting("tvdb_api", 'string')
if diamond == False:
	fanart_api_key = get_setting("fanart.apikey", 'string')
	tmdb_API_key = get_setting("tmdb.apikey", 'string')
	#tvdb_apikey =  get_setting("tvdb.apikey", 'string')
	if tmdb_API_key == None or tmdb_API_key == 'None' or tmdb_API_key == '':
		fanart_api_key = get_setting("fanart_api", 'string')
		tmdb_API_key = get_setting("tmdb_api", 'string')
		#tvdb_apikey =  get_setting("tvdb_api", 'string')

if len(fanart_api_key) != 32:
	fanart_api_key = '184e1a2b1fe3b94935365411f919f638'
if len(tmdb_API_key) != 32:
	tmdb_API_key = 'edde6b5e41246ab79a2697cd125e1781'



VIDEO_META = ''
SUB_FILE = ''

filter_string = 'HI10,DV,HDR,HC,WMV,3D,HEVC,HYBRID,SCR,CAM'


PRE_TERM_BLOCK = False

exclusions = ["soundtrack", "gesproken"]
_APOSTROPHE_SUBS = re.compile(r"\\'s|'s|&#039;s| 039 s")
_SEPARATORS = re.compile(r'[:|/,!?()"[\]\-\\_.{}]|(?<![:|/,!?()"[\]\-\\_.{}\s]dd)\+')
_WHITESPACE = re.compile(r'\s+')
_SINGLE_QUOTE = re.compile(r"['`]")
_AMPERSAND = re.compile(r'&#038;|&amp;|&')
_EPISODE_NUMBERS = re.compile(r'.*((?:s\d+ ?e\d+ )|(?:season ?\d+ ?(?:episode|ep) ?\d+)|(?: \d+ ?x ?\d+ ))')
_ASCII_NON_PRINTABLE = re.compile(r'[^{}]'.format(re.escape(string.printable)))

approved_qualities = ["4K", "1080p", "720p", "SD"]
approved_qualities_set = set(approved_qualities)

INFO_TYPES = {
	"AVC": ["x264", "x 264", "h264", "h 264", "avc"],
	"HEVC": ["x265", "x 265", "h265", "h 265", "hevc"],
	"XVID": ["xvid"],
	"DIVX": ["divx"],
	"MP4": ["mp4"],
	"WMV": ["wmv"],
	"MPEG": ["mpeg"],
	"REMUX": ["remux", "bdremux"],
	"DV": [" dv ", "dovi", "dolby vision", "dolbyvision"],
	"HDR": [
		" hdr ",
		"hdr10",
		"hdr 10",
		"uhd bluray 2160p",
		"uhd blu ray 2160p",
		"2160p uhd bluray",
		"2160p uhd blu ray",
		"2160p bluray hevc truehd",
		"2160p bluray hevc dts",
		"2160p bluray hevc lpcm",
		"2160p us bluray hevc truehd",
		"2160p us bluray hevc dts",
	],
	"SDR": [" sdr"],
	"AAC": ["aac"],
	"DTS-HDMA": ["hd ma", "hdma"],
	"DTS-HDHR": ["hd hr", "hdhr", "dts hr", "dtshr"],
	"DTS-X": ["dtsx", " dts x"],
	"ATMOS": ["atmos"],
	"TRUEHD": ["truehd", "true hd"],
	"DD+": ["ddp", "eac3", " e ac3", " e ac 3", "dd+", "digital plus", "digitalplus"],
	"DD": [" dd ", "dd2", "dd5", "dd7", " ac3", " ac 3", "dolby digital", "dolbydigital", "dolby5"],
	"MP3": ["mp3"],
	"WMA": [" wma"],
	"2.0": ["2 0 ", "2 0ch", "2ch"],
	"5.1": ["5 1 ", "5 1ch", "6ch"],
	"7.1": ["7 1 ", "7 1ch", "8ch"],
	"BLURAY": ["bluray", "blu ray", "bdrip", "bd rip", "brrip", "br rip"],
	"WEB": [" web ", "webrip", "webdl", "web rip", "web dl", "webmux"],
	"HD-RIP": [" hdrip", " hd rip"],
	"DVDRIP": ["dvdrip", "dvd rip"],
	"HDTV": ["hdtv"],
	"PDTV": ["pdtv"],
	"CAM": [
		" cam ", "camrip", "cam rip",
		"hdcam", "hd cam",
		" ts ", " ts1", " ts7",
		"hd ts", "hdts",
		"telesync",
		" tc ", " tc1", " tc7",
		"hd tc", "hdtc",
		"telecine",
		"xbet",
		"hcts", "hc ts",
		"hctc", "hc tc",
		"hqcam", "hq cam",
	],
	"SCR": ["scr ", "screener"],
	"HC": [
		"korsub", " kor ",
		" hc ", "hcsub", "hcts", "hctc", "hchdrip",
		"hardsub", "hard sub",
		"sub hard",
		"hardcode", "hard code",
		"vostfr", "vo stfr",
	],
	"3D": [" 3d"],
}


def log(*args, **kwargs):
	for i in args:
		try:
			import xbmc
			xbmc.log(str(i)+'===>A4K_Wrapper', level=xbmc.LOGINFO)
		except:
			print(i)

def auto_clean_cache(days=None):
	import os 
	import datetime
	import glob

	path = ADDON_USERDATA_PATH
	if days==None:
		days = -30
	else:
		days = int(days)*-1

	today = datetime.datetime.today()#gets current time
	if not os.path.exists(path):
		os.mkdir(path)
	os.chdir(path) #changing path to current path(same as cd command)

	#we are taking current folder, directory and files 
	#separetly using os.walk function
	for root,directories,files in os.walk(path,topdown=False): 
		for name in files:
			#this is the last modified time
			t = os.stat(os.path.join(root, name))[8] 
			filetime = datetime.datetime.fromtimestamp(t) - today
			#checking if file is more than 7 days old 
			#or not if yes then remove them
			if filetime.days <= days:
				if len(name) == 36 and '.txt' == name[-4:]:
					#print(os.path.join(root, name), filetime.days)
					log(str(os.path.join(root, name))+'===>DELETE')
					os.remove(os.path.join(root, name))

def sub_cleaner_log_clean():
	try:
		from resources.lib import Utils
		subcleaner_log = os.path.join(Utils.ADDON_PATH, 'subcleaner', 'settings', 'logs', 'subcleaner.log')
		if os.path.exists(subcleaner_log):
			os.remove(subcleaner_log)
	except:
		subcleaner_log = os.path.join(ADDON_PATH, 'subcleaner', 'settings', 'logs', 'subcleaner.log')
		if os.path.exists(subcleaner_log):
			os.remove(subcleaner_log)

def get_download_line(file_path):
	try: lines = read_all_text(file_path).split('\n')
	except: return None
	for line in lines:
		if line.strip() == '':
			continue
		try: 
			line = eval(line)
			return line
		except: 
			return line

def add_download_line(file_path, curr_download):
	lines = read_all_text(file_path).split('\n')
	out_file = ''
	for i in lines:
		out_file = out_file + i + '\n'
	out_file = out_file + str(curr_download) + '\n'
	write_all_text(file_path, out_file)

def delete_download_line(file_path, curr_download):
	lines = read_all_text(file_path).split('\n')
	out_file = ''
	for i in lines:
		if i.strip() == '':
			continue
		i_ep_meta, i_tmdb, i_movie, i_imdb, curr_download_magnet, curr_download_ep_meta, curr_download_tmdb, curr_download_movie, curr_download_imdb = None, None, None, None, None, None, None, None, None
		i_dict = None
		try: i_dict = eval(i)
		except: i_dict = i
		try:
			i_magnet = i_dict.get('magnet')
		except:
			i_magnet = None
		if i_magnet:
			i_ep_meta = i_dict.get('episode_meta')
			i_tmdb = i_dict.get('tmdb_seasons')
			i_movie = i_dict.get('is_movie')
			i_imdb = i_dict.get('imdb')

			curr_download_magnet = curr_download.get('magnet')
			curr_download_ep_meta = curr_download.get('episode_meta')
			curr_download_tmdb = curr_download.get('tmdb_seasons')
			curr_download_movie = curr_download.get('is_movie')
			curr_download_imdb = curr_download.get('imdb')

			if i_magnet ==  curr_download_magnet and i_ep_meta ==  curr_download_ep_meta and i_tmdb ==  curr_download_tmdb and i_movie ==  curr_download_movie and i_imdb ==  curr_download_imdb:
				#print('skip')
				continue
		if str(i) == str(curr_download) or str(i).strip() == '':
			#print('skip')
			continue
		else:
			#print('write')
			out_file = out_file + i + '\n'
	write_all_text(file_path, out_file)
	time.sleep(1)


def getSentenceCase(source: str):
	file_type = source.split('.')[-1]
	source = source.replace('.'+file_type,'')
	output = ""
	isFirstWord = True
	for c in source:
		if isFirstWord and not c.isspace():
			c = c.upper()
			isFirstWord = False
		elif not isFirstWord and c in ".!?":
			isFirstWord = True
		else:
			if c.upper() != c:
				c = c.lower()
		output = output + c
	output = output + '.' + file_type
	output = output.replace(re.search('[S][0-9]*[e][0-9]*', output)[0],re.search('[S][0-9]*[e][0-9]*', output)[0].upper())
	return output

def strip_non_ascii_and_unprintable(text):
	"""
	Stirps non ascii and unprintable characters from string
	:param text: text to clean
	:return: cleaned text
	"""
	return _ASCII_NON_PRINTABLE.sub("", text)

def deaccent_string(text):
	"""Deaccent the provided text leaving other unicode characters intact
	Example: Mîxéd ДљфӭЖ Tëst -> Mixed ДљфэЖ Test
	:param: text: Text to deaccent
	:type text: str|unicode
	:return: Deaccented string
	:rtype:str|unicode
	"""
	nfkd_form = unicodedata.normalize('NFKD', text)  # pylint: disable=c-extension-no-member
	deaccented_text = str("").join(
		[c for c in nfkd_form if not unicodedata.combining(c)]  # pylint: disable=c-extension-no-member
	)
	return deaccented_text

def clean_title(title, broken=None):
	"""
	Returns a cleaned version of the provided title
	:param title: title to be cleaned
	:param broken: set to 1 to remove apostophes, 2 to replace with spaces
	:return: cleaned title
	"""
	title = deaccent_string(title)
	title = strip_non_ascii_and_unprintable(title)
	title = title.lower()

	apostrophe_replacement = "s"
	if broken == 1:
		apostrophe_replacement = ""
	elif broken == 2:
		apostrophe_replacement = " s"

	title = _APOSTROPHE_SUBS.sub(apostrophe_replacement, title)

	title = _SINGLE_QUOTE.sub("", title)
	title = _SEPARATORS.sub(" ", title)
	title = _WHITESPACE.sub(" ", title)
	title = _AMPERSAND.sub("and", title)

	return title.strip()

from difflib import SequenceMatcher

def get_accepted_resolution_set():
	"""
	Fetches set of accepted resolutions per settings
	:return: set of resolutions
	:rtype set
	"""
	resolutions = approved_qualities
	max_res = get_setting("general.maxResolution", 'int')
	min_res = get_setting("general.minResolution", 'int')

	return set(resolutions[max_res:min_res+1])
	#return set(resolutions)



def full_meta_episode_regex(args):
	"""
	Takes an episode items full meta and returns a regex object to use in title matching
	:param args: Full meta of episode item
	:return: compiled regex object
	"""
	episode_info = args["info"]
	show_title = clean_title(episode_info["tvshowtitle"])
	country = episode_info.get("country", "")
	if isinstance(country, (list, set)):
		country = '|'.join(country)
	country = country.lower()
	year = episode_info.get("year", "")
	episode_title = clean_title(episode_info.get("title", ""))
	season = str(episode_info.get("season", ""))
	episode = str(episode_info.get("episode", ""))

	if episode_title == show_title or len(re.findall(r"^\d+$", episode_title)) > 0:
		episode_title = None

	reg_string = (
		r"(?#SHOW TITLE)(?:{show_title})"
		r"? ?"
		r"(?#COUNTRY)(?:{country})"
		r"? ?"
		r"(?#YEAR)(?:{year})"
		r"? ?"
		r"(?:(?:[s[]?)0?"
		r"(?#SEASON){season}"
		r"[x .e]|(?:season 0?"
		r"(?#SEASON){season} "
		r"(?:episode )|(?: ep ?)))(?:\d?\d?e)?0?"
		r"(?#EPISODE){episode}"
		r"(?:e\d\d)?\]? "
	)

	reg_string = reg_string.format(show_title=show_title, country=country, year=year, season=season, episode=episode)

	if episode_title:
		reg_string += "|{eptitle}".format(eptitle=episode_title)

	reg_string = reg_string.replace("*", ".")

	return re.compile(reg_string)


def get_best_episode_match(dict_key, dictionary_list, item_information):
	"""
	Attempts to identify the best matching file/s for a given item and list of source files
	:param dict_key: internal key of dictionary in dictionary list to run checks against
	:param dictionary_list: list of dictionaries containing source title
	:param item_information: full meta of episode object
	:return: dictionaries that best matched requested episode
	"""
	regex = full_meta_episode_regex(item_information)
	files = []

	for i in dictionary_list:
		i.update(
			{
				"regex_matches": regex.findall(
					clean_title(i[dict_key].split("/")[-1].replace("&", " ").lower())
				)
			}
		)
		files.append(i)
	files = [i for i in files if len(i["regex_matches"]) > 0]

	if len(files) == 0:
		return None

	files = sorted(files, key=lambda x: len(" ".join(x["regex_matches"])), reverse=True)

	return files[0]


def copy2clip(txt):
	"""
	Takes a text string and attempts to copy it to the clipboard of the device
	:param txt: Text to send to clipboard
	:type txt: str
	:return: None
	:rtype: None
	"""
	import subprocess

	platform = sys.platform
	if platform == "win32":
		try:
			cmd = "echo " + txt.strip() + "|clip"
			return subprocess.check_call(cmd, shell=True)
		except Exception as e:
			log("Failure to copy to clipboard, \n{}".format(e), "error")
	elif platform.startswith("linux") or platform == "darwin":
		try:
			from subprocess import Popen, PIPE

			cmd = "pbcopy" if platform == "darwin" else ["xsel", "-pi"]
			kwargs = {"stdin": PIPE, "text": True} if PYTHON3 else {"stdin": PIPE}
			p = Popen(cmd, **kwargs)
			p.communicate(input=str(txt))
		except Exception as e:
			log("Failure to copy to clipboard, \n{}".format(e), "error")


def extract_zip(zip_file, dest_dir):
	import zipfile
	import shutil
	archive = zipfile.ZipFile(zip_file)
	archive_folder = None
	for file in archive.namelist():
		if file[-1] == '/':
			if archive_folder == None:
				archive_folder = file
		archive.extract(file, dest_dir)
	source = os.path.join(dest_dir, archive_folder)
	destination = dest_dir
	files = os.listdir(source)
	for file in files:
		file_name = os.path.join(source, file)
		out_file_name = os.path.join(destination, file)
		if os.path.exists(out_file_name):
			try: delete_file(out_file_name)
			except: shutil.rmtree(out_file_name)
			shutil.move(file_name, destination)
		else:
			shutil.move(file_name, destination)
	try: delete_file(source)
	except: shutil.rmtree(source)

def delete_file(source):
	try: os.rmdir(source)
	except NotADirectoryError: os.remove(source)

#class PreemptiveCancellation(Exception):
#	pass

def _monkey_check(method):

	def do_method(*args, **kwargs):
		"""
		Wrapper method
		:param args: args
		:param kwargs: kwargs
		:return: func results
		"""
		#if (any([True for i in inspect.stack() if "providerModules" in i[1]]) or
		#	any([True for i in inspect.stack() if "providers" in i[1]])) and PRE_TERM_BLOCK:
		#	raise PreemptiveCancellation('Pre-emptive termination has stopped this request111')

		try:
			#log(*args)
			return method(*args, **kwargs)
		except Exception as exc:
			if 'ConnectionResetError' in str(exc):
				if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
					log(args[1], exc)
				#log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				#raise PreemptiveCancellation('ConnectionResetError')
				log(args[1],'ConnectionResetError')
			else:
				log(exc)

	return do_method

# Monkey patch the common requests calls

requests.get = _monkey_check(requests.get)
requests.post = _monkey_check(requests.post)
requests.head = _monkey_check(requests.head)
requests.delete = _monkey_check(requests.delete)
requests.put = _monkey_check(requests.put)

requests.Session.get = _monkey_check(requests.Session.get)
requests.Session.post = _monkey_check(requests.Session.post)
requests.Session.head = _monkey_check(requests.Session.head)
requests.Session.delete = _monkey_check(requests.Session.delete)
requests.Session.put = _monkey_check(requests.Session.put)

def selectFromDict(options, name):
	print('\n\n')
	index = 0
	indexValidList = []
	log('\nSelect a ' + str(name) + ':\n')
	for optionName in options:
		index = index + 1
		indexValidList.extend([options[optionName]])
		log(str(index) + ') ' + optionName)
	inputValid = False
	while not inputValid:
		try: 
			inputRaw = input('\n' + name + ': ')
			if 'magnet:' in inputRaw:
				return inputRaw
		except: 
			print('EXIT\n')
			return
		inputNo = int(inputRaw) - 1
		if inputNo > -1 and inputNo < len(indexValidList):
			selected = indexValidList[inputNo]
			for i in options:
				if options[i] == selected:
					selection = i
					break
			log('\nSelected ' +  str(name) + ': ' + str(selection)+'\n')
			inputValid = True
			break
		else:
			log('Please select a valid ' + str(name) + ' number')
	return selected

def get_http(url, headers=False):
	succeed = 0
	if not headers:
		headers = {'User-agent': 'Kodi/21.0 ( phil65@kodi.tv )'}
	while (succeed < 2) :
		try:
			request = requests.get(url, headers=headers)
			return request.text
		except Exception as e:
			log('get_http: could not get data from %s' % url)
			xbmc.sleep(500)
			succeed += 1
	return None

def get_response_cache(url='', cache_days=7.0, folder=False, headers=False):
	now = time.time()
	url = url.encode('utf-8')
	hashed_url = hashlib.md5(url).hexdigest()
	cache_path = os.path.join(ADDON_USERDATA_PATH, folder)

	if not os.path.exists(cache_path):
		os.mkdir(cache_path)
	cache_seconds = int(cache_days * 86400.0)
	path = os.path.join(cache_path, '%s.txt' % hashed_url)
	if os.path.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
		results = read_all_text(path)
		try: results = eval(results)
		except: pass
	else:
		response = get_http(url, headers)
		try:
			results = json.loads(response)
			#save_to_file(results, hashed_url, cache_path)
			#file_path = os.path.join(cache_path, hashed_url)
			write_all_text(path, str(results))
		except:
			log('Exception: Could not get new JSON data from %s. Tryin to fallback to cache' % url)
			log(response)
			results = read_all_text(path) if os.path.exists(path) else []
	if not results:
		return None
	return results


def get_tmdb_from_imdb(imdb, media_type):
	response = get_tmdb_data('find/%s?external_source=%s&language=%s&' % (imdb, 'imdb_id', 'en'), 30)
	if media_type == 'movie':
		tmdb = response['movie_results'][0]['id']
	else:
		tmdb = response['tv_results'][0]['id']
	return tmdb

def get_tmdb_data(url='', cache_days=14, folder='TheMovieDB'):
	url = 'https://api.themoviedb.org/3/%sapi_key=%s' % (url, tmdb_API_key)
	return get_response_cache(url, cache_days, folder)

def get_tvshow_ids(tvshow_id=None, cache_time=14):
	if not tvshow_id:
		return None
	session_str = ''
	response = get_tmdb_data('tv/%s?append_to_response=external_ids&language=%s&include_image_language=en,null,%s&%s' % (tvshow_id, 'en', 'en', session_str), cache_time)
	if not response:
		return False
	external_ids = response.get('external_ids')
	return external_ids

def get_fanart_data(url='', tmdb_id=None, media_type=None, cache_days=14, folder='FanartTV'):
	fanart_api = fanart_api_key
	if media_type =='tv':
		tvdb_id = get_tvshow_ids(tmdb_id)
		tvdb_id = tvdb_id['tvdb_id']
		url = 'http://webservice.fanart.tv/v3/tv/'+str(tvdb_id)+'?api_key=' + fanart_api
		#response = requests.get(url).json()
	elif media_type =='tv_tvdb':
		url = 'http://webservice.fanart.tv/v3/tv/'+str(tmdb_id)+'?api_key=' + fanart_api
		#response = requests.get(url).json()
	else:
		url = 'http://webservice.fanart.tv/v3/movies/'+str(tmdb_id)+'?api_key=' + fanart_api
		#response = requests.get(url).json()
	return get_response_cache(url, cache_days, folder)


def episodes_parts_lists():
	parts_roman = []
	parts_numbers = []
	parts_words = []
	parts_numbers2 = []
	for i in range(1,5):
		parts_numbers.append(' ('+str(i)+')')
		parts_roman.append(' Part '+str(int_to_roman(i)))
		parts_words.append(' Part ' + str(int_to_en(i)))
		parts_numbers2.append(' Part ' + str(i))
	return parts_roman, parts_numbers, parts_words, parts_numbers2

def episodes_parts_lists_multi(number_one, number_two):
	multi_dict = {}
	start = max(int(number_one)-1,1)
	end = int(number_two)+1
	for i in range(start, end):
		#test_dict = {'roman': [int_to_roman(i), int_to_roman(i+1)], 'numbers': ['('+str(i)+')','('+str(i+1)+')'], 'words': [int_to_en(i), int_to_en(i+1)], 'numbers2': [i, i+1], 'numbers3': ['('+str(i).zfill(2)+')','('+str(i+1).zfill(2)+')'],'numbers3': [str(i).zfill(2), str(i+1).zfill(2)],}
		test_dict = {'numbers': ['('+str(i)+')','('+str(i+1)+')'], 'words': [int_to_en(i), int_to_en(i+1)], 'numbers2': [i, i+1], 'numbers3': ['('+str(i).zfill(2)+')','('+str(i+1).zfill(2)+')'],'numbers3': [str(i).zfill(2), str(i+1).zfill(2)],}
		multi_dict[i] = []
		for j in test_dict:
			multi_dict[i].append( str(('%s+%s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )
			multi_dict[i].append( str(('%s + %s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )
			multi_dict[i].append( str(('%sand%s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )
			multi_dict[i].append( str(('%s and %s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )

			multi_dict[i].append( str(('E%sE%s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )
			multi_dict[i].append( str(('E%s E%s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )

			multi_dict[i].append( str(('%s&%s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )
			multi_dict[i].append( str(('%s & %s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )
			#multi_dict[i].append( str((' Part %s %s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )
			#multi_dict[i].append( str((' Part %s-%s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )
			#multi_dict[i].append( str((' Part %s - %s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )
			#multi_dict[i].append( str((' Parts %s %s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )
			#multi_dict[i].append( str((' Parts %s-%s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )
			#multi_dict[i].append( str((' Parts %s - %s') % (str(test_dict[j][0]), str(test_dict[j][1]))) )
			
	return multi_dict

def int_to_en(num):
	d = { 0 : 'Zero', 1 : 'One', 2 : 'Two', 3 : 'Three', 4 : 'Four', 5 : 'Five',
		  6 : 'Six', 7 : 'Seven', 8 : 'Eight', 9 : 'Nine', 10 : 'Ten',
		  11 : 'Eleven', 12 : 'Twelve', 13 : 'Thirteen', 14 : 'Fourteen',
		  15 : 'Fifteen', 16 : 'Sixteen', 17 : 'Seventeen', 18 : 'Eighteen',
		  19 : 'Nineteen', 20 : 'Twenty',
		  30 : 'Thirty', 40 : 'Forty', 50 : 'Fifty', 60 : 'Sixty',
		  70 : 'Seventy', 80 : 'Eighty', 90 : 'Ninety' }
	k = 1000
	m = k * 1000
	b = m * 1000
	t = b * 1000

	assert(0 <= num)

	if (num < 20):
		return d[num]

	if (num < 100):
		if num % 10 == 0: return d[num]
		else: return d[num // 10 * 10] + ' ' + d[num % 10]

	if (num < k):
		if num % 100 == 0: return d[num // 100] + ' Hundred'
		else: return d[num // 100] + ' Hundred and ' + int_to_en(num % 100)

	if (num < m):
		if num % k == 0: return int_to_en(num // k) + ' Thousand'
		else: return int_to_en(num // k) + ' Thousand, ' + int_to_en(num % k)

	if (num < b):
		if (num % m) == 0: return int_to_en(num // m) + ' Million'
		else: return int_to_en(num // m) + ' Million, ' + int_to_en(num % m)

	if (num < t):
		if (num % b) == 0: return int_to_en(num // b) + ' Billion'
		else: return int_to_en(num // b) + ' Billion, ' + int_to_en(num % b)

	if (num % t == 0): return int_to_en(num // t) + ' Trillion'
	else: return int_to_en(num // t) + ' Trillion, ' + int_to_en(num % t)

	raise AssertionError('num is too large: %s' % str(num))

def int_to_roman(number):
	""" Convert an integer to a Roman numeral. """

	if not 0 < int(number) < 4000:
		raise ValueError
	ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
	nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
	result = []
	for i in range(len(ints)):
		count = int(number / ints[i])
		result.append(nums[i] * count)
		number -= ints[i] * count
	return ''.join(result)


def download_file(url, save_as):
	from urllib.request import urlopen
	# Download from URL
	with urlopen(url) as file:
		content = file.read()
	# Save to file
	with open(save_as, 'wb') as download:
		download.write(content)

def curr_percent(rd_api):
	if rd_api.original_tot_bytes == 0:
		return
	curr_percent = round((rd_api.remaining_tot_bytes/rd_api.original_tot_bytes) * 100,2)

	os.environ['DOWNLOAD_CURR_PERCENT'] = str(int(curr_percent))
	#log('\n\n'+str(curr_percent)+'% total remaining on file')
	percent_done = 100 - curr_percent
	if percent_done == 0:
		return
	time_running = time.time() - rd_api.original_start_time
	seconds_per_percent = time_running / percent_done
	seconds_remaining = int(curr_percent * seconds_per_percent)
	minutes_remaining = int((curr_percent * seconds_per_percent) / 60)
	hours_remaining = round((curr_percent * seconds_per_percent) / (60*60),2)
	#log('\n\n'+str(seconds_remaining)+' seconds_remaining')
	#log('\n\n'+str(minutes_remaining)+' minutes_remaining')
	#log('\n\n'+str(hours_remaining)+' hours_remaining')
	#log('REMAINING_LINES_MAGNET_LIST =   '+str(rd_api.num_lines))
	if rd_api.xbmc_gui:
		import xbmcgui
		xbmcgui.Window(10000).setProperty('curr_percent', str(curr_percent))
		xbmcgui.Window(10000).setProperty('percent_done', str(percent_done))
		xbmcgui.Window(10000).setProperty('seconds_remaining', str(seconds_remaining))
		xbmcgui.Window(10000).setProperty('minutes_remaining', str(minutes_remaining))
		xbmcgui.Window(10000).setProperty('hours_remaining', str(hours_remaining))
		xbmcgui.Window(10000).setProperty('num_lines_remaining', str(rd_api.num_lines))

def download_progressbar(rd_api, url, file_path):
	#from urllib.request import urlretrieve
	stop_downloader = get_setting('magnet_list').replace('magnet_list.txt','stop_downloader')
	final_remaining_tot_bytes = rd_api.remaining_tot_bytes - rd_api.UNRESTRICT_FILE_SIZE
	if os.path.exists(file_path):
		rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - os.path.getsize(file_path)
	
	if os.path.exists(stop_downloader):
		delete_file(stop_downloader)
		tools_stop_downloader = True
		#exit()
		return
	
	if not os.path.exists(os.path.dirname(file_path)):
		from pathlib import Path
		Path(os.path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
		
	from resumable import urlretrieve, sha256, DownloadError
	
	from urllib.parse import unquote
	import sys
	global rem_file # global variable to be used in dlProgress
	rem_file = url.split('/')[-1]

	start = time.time()
	def dlProgress(count, blockSize, totalSize):
		percent = int(count*blockSize*100/totalSize)
		rd_api.remaining_tot_bytes = rd_api.remaining_tot_bytes - blockSize
		curr_percent(rd_api)
		done = int(50 * count*blockSize / totalSize)
		suffix = "\r[%s%s] %s   %s  %s   Kbps" % ('=' * done, ' ' * (50-done),str(percent)+'%',unquote(rem_file), (1/1000)*count*blockSize//(time.time() - start))
		message = "\r" + rem_file + "...%d%%" % percent
		message = message + suffix
		#sys.stdout.write("\r" + rem_file + "...%d%%" % percent)
		sys.stdout.write(message)
		sys.stdout.flush()
		if os.path.exists(stop_downloader):
			delete_file(stop_downloader)
			sys.stdout.write('\n')
			sys.stdout.flush()
			tools_stop_downloader = True
			#exit()
			raise DownloadError
			return file_path
	urlretrieve(url, file_path, reporthook=dlProgress)
	if final_remaining_tot_bytes < rd_api.remaining_tot_bytes:
		rd_api.remaining_tot_bytes = final_remaining_tot_bytes
	rd_api.UNRESTRICT_FILE_SIZE = 0
	sys.stdout.write('\n')
	sys.stdout.flush()
	return file_path

def progressbar(it, prefix="", size=60, out=sys.stdout): # Python3.3+
	count = len(it)
	def show(j):
		x = int(size*j/count)
		log("{}[{}{}] {}/{}".format(prefix, "#"*x, "."*(size-x), j, count), 
				end='\r', file=out, flush=True)
	show(0)
	for i, item in enumerate(it):
		yield item
		show(i+1)
	log("\n", flush=True, file=out)



def get_quality(release_title):
	"""
	Identifies resolution based on release title information
	:param release_title: sources release title
	:return: stringed resolution
	"""
	release_title = release_title.lower()

	if any(q in release_title for q in ["720", "72o"]):
		return "720p"
	if any(q in release_title for q in ["1080", "1o80", "108o", "1o8o"]):
		return "1080p"
	if any(q in release_title for q in ["2160", "216o"]):
		return "4K"
	try:
		if not release_title[release_title.index("4k") + 2].isalnum():
			return "4K"
	except (ValueError, IndexError):
		pass

	return "SD"


def get_info(release_title):
	"""
	Identifies and retrieves a list of information based on release title of source
	:param release_title: Release title of source
	:return: List of info meta
	"""
	title = clean_title(release_title) + " "
	info = {
		info_prop for info_prop, string_list in INFO_TYPES.items()
		if any(i in title for i in string_list)
	}
	if all(i in info for i in ["SDR", "HDR"]):
		info.remove("HDR")
	elif all(i in title for i in ["2160p", "remux"]) and all(i not in info for i in ["HDR", "SDR"]):
		info.add("HDR")
	elif "DV" in info and "hybrid" in title and all(i not in info for i in ["HDR", "SDR"]):
		info.add("HDR")
	if all(i in info for i in ["HDR", "DV"]) and all(i not in title for i in ["hybrid", " hdr"]):
		info.remove("HDR")
	if all(i in info for i in ["HDR", "DV"]):
		info.add("HYBRID")
	if any(i in info for i in ["HDR", "DV"]) and all(i not in info for i in ["HEVC", "AVC"]):
		info.add("HEVC")
	if all(i in info for i in ["DD", "DD+"]):
		info.remove("DD")
	elif any(i in title for i in ["dtshd", "dts hd"]) and all(i not in info for i in ["DTS-HDMA", "DTS-HDHR"]):
		info.add("DTS-HD")
	elif " dts" in title and all(i not in info for i in ["DTS-HDMA", "DTS-HDHR", "DTS-X", "DTS-HD"]):
		info.add("DTS")
	if all(i in title for i in ["sub", "forced"]):
		info.add("HC")
	return info


def smart_merge_dictionary(dictionary, merge_dict, keep_original=False, extend_array=True):
	"""Method for merging large multi typed dictionaries, it has support for handling arrays.

	:param dictionary:Original dictionary to merge the second on into.
	:type dictionary:dict
	:param merge_dict:Dictionary that is used to merge into the original one.
	:type merge_dict:dict
	:param keep_original:Boolean that indicates if there are duplicated values to keep the original one.
	:type keep_original:bool
	:param extend_array:Boolean that indicates if we need to extend existing arrays with the enw values..
	:type extend_array:bool
	:return:Merged dictionary
	:rtype:dict
	"""
	if not isinstance(dictionary, dict) or not isinstance(merge_dict, dict):
		return dictionary
	for new_key, new_value in merge_dict.items():
		original_value = copy.deepcopy(dictionary.get(new_key))
		if isinstance(new_value, (dict, Mapping)):
			if original_value is None:
				original_value = {}
			new_value = smart_merge_dictionary(original_value, new_value, keep_original, extend_array)
		else:
			if original_value and keep_original:
				continue
			if extend_array and isinstance(original_value, (list, set)) and isinstance(
					new_value, (list, set)
			):
				if isinstance(original_value, set):
					original_value.update(x for x in new_value if x not in original_value)
					try:
						new_value = set(sorted(original_value))
					except TypeError:  # Sorting of complex array doesn't work.
						new_value = original_value
				else:
					original_value.extend(x for x in new_value if x not in original_value)
					try:
						new_value = sorted(original_value)
					except TypeError:  # Sorting of complex array doesn't work.
						new_value = original_value
		if new_value or new_value == 0 or isinstance(new_value, bool):
			# We want to skip empty lists / dicts / sets
			dictionary[new_key] = new_value
	return dictionary

def _build_simple_show_info(info):
	simple_info = {'show_title': info['info'].get('tvshowtitle', ''),
				   'episode_title': info['info'].get('originaltitle', ''),
				   'year': str(info['info'].get('tvshow.year', info['info'].get('year', ''))),
				   'season_number': str(info['info']['season']),
				   'episode_number': str(info['info']['episode']),
				   'show_aliases': info['info'].get('aliases', []),
				   'country': info['info'].get('country_origin', ''),
				   'no_seasons': str(info.get('season_count', '')),
				   'absolute_number': str(info.get('absoluteNumber', '')),
				   'is_airing': info.get('is_airing', False),
				   'no_episodes': str(info.get('episode_count', '')),
				   'isanime': False}

	if '.' in simple_info['show_title']:
		simple_info['show_aliases'].append(clean_title(simple_info['show_title'].replace('.', '')))
	if any(x in i.lower() for i in info['info'].get('genre', ['']) for x in ['anime', 'animation']):
		simple_info['isanime'] = True

	return simple_info

def _build_simple_movie_info(info):
	simple_info = {
		'title': info['info'].get('title', ''),
		'year': str(info['info'].get('year', '')),
		'aliases': info['info'].get('aliases', []),
		'country': info['info'].get('country_origin', ''),
	}

	if '.' in simple_info['title']:
		simple_info['aliases'].append(
			clean_title(simple_info['title'].replace('.', ''))
		)

	return simple_info


PYTHON3 = True if sys.version_info.major == 3 else False

import struct
__64k = 65536
__longlong_format_char = 'q'
__byte_size = struct.calcsize(__longlong_format_char)

def sum_64k_bytes(file, filehash):
	range_value = __64k / __byte_size
	from a4kSubtitles.lib import utils
	if utils.py3:
		range_value = round(range_value)

	for _ in range(range_value):
		try: chunk = file.readBytes(__byte_size)
		except: chunk = file.read(__byte_size)
		(value,) = struct.unpack(__longlong_format_char, chunk)
		filehash += value
		filehash &= 0xFFFFFFFFFFFFFFFF
		return filehash

def set_size_and_hash(meta, filepath):
	#f = xbmcvfs.File(filepath)
	if 'http' in str(filepath):
		meta = set_size_and_hash_url(meta, filepath)
		return meta
	f = open(filepath, 'rb')
	try:
		#filesize = f.size()
		filesize = os.path.getsize(filepath)
		meta['filesize'] = filesize

		if filesize < __64k * 2:
			return

		# ref: https://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
		# filehash = filesize + 64bit sum of the first and last 64k of the file
		filehash = lambda: None
		filehash = filesize

		filehash = sum_64k_bytes(f, filehash)
		f.seek(filesize - __64k, os.SEEK_SET)
		filehash = sum_64k_bytes(f, filehash)

		meta['filehash'] = "%016x" % filehash
	finally:
		f.close()
	return meta


def temp_file():
	import tempfile
	file = tempfile.NamedTemporaryFile()
	filename = file.name
	return filename

def set_size_and_hash_url(meta, filepath):
	import urllib.request
	url = filepath
	f = urllib.request.urlopen(url)
	filesize = int(f.headers['Content-Length'])
	opener = urllib.request.build_opener()
	opener.addheaders = [('Range', 'bytes=%s-%s' % (0, __64k-1))]
	first_64kb = temp_file()
	last_64kb = temp_file()
	urllib.request.install_opener(opener)
	urllib.request.urlretrieve(url, first_64kb)
	
	opener = urllib.request.build_opener()
	opener.addheaders = [('Range', 'bytes=%s-%s' % (filesize - __64k, 0))]
	urllib.request.install_opener(opener)
	urllib.request.urlretrieve(url, last_64kb)

	#f = xbmcvfs.File(filepath)
	f = open(first_64kb, 'rb')
	try:
		#filesize = f.size()
		meta['filesize'] = filesize

		if filesize < __64k * 2:
			return

		# ref: https://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
		# filehash = filesize + 64bit sum of the first and last 64k of the file
		filehash = lambda: None
		filehash = filesize

		filehash = sum_64k_bytes(f, filehash)
		#f.seek(filesize - __64k, os.SEEK_SET)
		#log(first_64kb, 'size='+str(os.path.getsize(first_64kb)),'set_size_and_hash_url')
		f.close()
		f = open(last_64kb, 'rb')
		filehash = sum_64k_bytes(f, filehash)
		#log(last_64kb, 'size='+str(os.path.getsize(last_64kb)),'set_size_and_hash_url')
		meta['filehash'] = "%016x" % filehash
	finally:
		f.close()
		delete_file(first_64kb)
		delete_file(last_64kb)
	return meta

def md5_hash(value):
	"""
	Returns MD5 hash of given value
	:param value: object to hash
	:type value: object
	:return: Hexdigest of hash
	:rtype: str
	"""
	if isinstance(value, (tuple, dict, list, set)):
		value = json.dumps(value, sort_keys=True, default=serialize_sets)
	return hashlib.md5(unicode(value).encode("utf-8")).hexdigest()

def serialize_sets(obj):
	if isinstance(obj, set):
		return sorted([unicode(i) for i in obj])
	return obj

def read_all_text(file_path):
	try:
		f = open(file_path, "r")
		return f.read()
	except IOError:
		return None
	finally:
		try:
			f.close()
		except Exception:
			pass

def write_all_text(file_path, content):
	try:
		f = open(file_path, "w")
		return f.write(content)
	except IOError:
		return None
	finally:
		try:
			f.close()
		except Exception:
			pass

def get_pid():
	with open(PID_FILE, 'w', encoding='utf-8') as f:
		f.write(str(os.getpid()))


class StackTraceException(Exception):
	def __init__(self, msg):
		log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		tb = traceback.format_exc()
		log("{} \n{}".format(tb, msg) if not tb.startswith("NoneType: None") else msg, "error")

class UnexpectedResponse(StackTraceException):
	def __init__(self, api_response):
		log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		message = "API returned an unexpected response: \n{}".format(api_response)
		super(UnexpectedResponse, self).__init__(message)

class RanOnceAlready(RuntimeError):
	#log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	pass

Running = None
RunOnce = None
CheckSum = None


class GlobalLock(object):
	def __init__(self, lock_name, run_once=False, check_sum=None):
		self._lock_name = lock_name
		self._run_once = run_once
		self._lock_format = "{}.GlobalLock.{}.{}"
		self._check_sum = check_sum or 'global'

	def _create_key(self, value):
		return self._lock_format.format(ADDON_NAME, self._lock_name, value)

	def _run(self):
		while self._running():
			time.sleep(0.1)
		Running = True
		self._check_ran_once_already()

	def _running(self):
		return Running

	def _check_ran_once_already(self):
		if RunOnce and CheckSum == self._check_sum:
			Running = None
			raise RanOnceAlready("Lock name: {}, Checksum: {}".format(self._lock_name, self._check_sum))

	def __enter__(self):
		self._run()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self._run_once:
			RunOnce = True
			CheckSum = self._check_sum
		Running = None



class FixedSortPositionObject(object):
	"""
	A class that always returns equality for a comparison with any other object
	"""
	def __lt__(self, other):
		return False

	def __eq__(self, other):
		return True

	def __neg__(self):
		return self


class SourceSorter:
	"""
	Handles sorting of sources according to users preferences
	"""

	FIXED_SORT_POSITION_OBJECT = FixedSortPositionObject()

	def __init__(self, item_information):
		"""
		Handles sorting of sources according to users preference
		"""
		self.item_information = item_information
		#log(self.item_information)
		self.mediatype = self.item_information['info']['mediatype']

		# Filter settings
		self.resolution_set = get_accepted_resolution_set()
		self.disable_dv = False
		self.disable_hdr = False
		self.disable_hevc = False
		self.filter_set = self._get_filters()

		# Size filter settings
		self.enable_size_limit = get_setting("general.enablesizelimit", 'bool')
		setting_mediatype = 'episode' if self.mediatype == 'episode' else 'movie'

		self.size_limit = get_setting("general.sizelimit.{}".format(setting_mediatype), 'float') * 1024
		self.size_minimum = get_setting("general.sizeminimum.{}".format(setting_mediatype), 'float') * 1024

		# Sort Settings
		self.quality_priorities = {
			"4K": 3,
			"1080p": 2,
			"720p": 1,
			"SD": 0
		}

		# Sort Methods
		self._get_sort_methods()

	def _get_filters(self):
		filter_string = get_setting('general.filters')
		current_filters = set() if filter_string is None else set(filter_string.split(","))

		# Set HR filters and remove from set before returning due to HYBRID
		self.disable_dv = "DV" in current_filters
		self.disable_hdr = "HDR" in current_filters
		self.disable_hevc = "HEVC" in current_filters

		return current_filters.difference({"HDR", "DV"})

	def filter_sources2(self, source_list):
		#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		# Iterate sources, yielding only those that are not filtered
		for source in source_list:
			# Quality filter
			if source['quality'] not in self.resolution_set:
				continue
			# Info Filter
			if self.filter_set & source['info']:
				continue
			# DV filter
			if self.disable_dv and "DV" in source['info'] and "HYBRID" not in source['info']:
				continue
			# HDR Filter
			if self.disable_hdr and "HDR" in source['info'] and "HYBRID" not in source['info']:
				continue
			# Hybrid Filter
			if self.disable_dv and self.disable_hdr and "HYBRID" in source['info']:
				continue
			if self.disable_hevc and "HEVC" in source['info']:
				continue
			# File size limits filter
			#if self.enable_size_limit and not (
			#		self.size_limit >= float(source.get("size", 0)) >= self.size_minimum
			#):
			#	continue

			# If not filtered, yield source
			yield source

	def filter_sources(self, source_list):
		#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		# Iterate sources, yielding only those that are not filtered
		for source in source_list:
			# Quality filter
			#log(source)
			if source['quality'] not in self.resolution_set:
				#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				continue
			# Info Filter
			if self.filter_set & source['info']:
				#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				continue
			# DV filter
			if self.disable_dv and "DV" in source['info'] and "HYBRID" not in source['info']:
				#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				continue
			# HDR Filter
			if self.disable_hdr and "HDR" in source['info'] and "HYBRID" not in source['info']:
				#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				continue
			# Hybrid Filter
			if self.disable_dv and self.disable_hdr and "HYBRID" in source['info']:
				#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				continue
			if self.disable_hevc and "HEVC" in source['info']:
				continue
			# File size limits filter
			if self.enable_size_limit and not (
					self.size_limit >= float(source.get("size", 0)) >= self.size_minimum
			):
				#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				continue

			# If not filtered, yield source
			yield source

	def sort_sources(self, sources_list):
		#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		"""Takes in a list of sources and filters and sorts them according to Seren's sort settings

		 :param sources_list: list of sources
		 :type sources_list: list
		 :return: sorted list of sources
		 :rtype: list
		 """

		filtered_sources = list(self.filter_sources(sources_list))
		#filtered_sources = list(sources_list)
		if (len(filtered_sources) == 0 and len(sources_list) > 0):
			#response = None
			#if not g.get_bool_runtime_setting('tempSilent'):
			#	response = xbmcgui.Dialog().yesno("Your filters appear to be too restrictive for this item, would you like to try again without them?")
			#if response or g.get_bool_runtime_setting('tempSilent'):
			#	return self._sort_sources(sources_list)
			#else:
			#	return []
			return self._sort_sources(sources_list)
		return self._sort_sources(filtered_sources)

	def _get_sort_methods(self):
		"""
		Get Seren settings for sort methods
		"""
		sort_methods = []
		sort_method_settings = {
			0: None,
			1: self._get_quality_sort_key,
			2: self._get_type_sort_key,
			3: self._get_debrid_priority_key,
			4: self._get_size_sort_key,
			5: self._get_low_cam_sort_key,
			6: self._get_hevc_sort_key,
			7: self._get_hdr_sort_key,
			8: self._get_audio_channels_sort_key
		}

		#if self.mediatype == 'episode' and g.get_bool_setting("general.lastreleasenamepriority"):
		#	self.last_release_name = g.get_runtime_setting(
		#		"last_resolved_release_title.{}".format(self.item_information['info']['trakt_show_id'])
		#	)
		#	if self.last_release_name:
		#		sort_methods.append((self._get_last_release_name_sort_key, False))

		for i in range(1, 9):
			sm = get_setting("general.sortmethod.{}".format(i),'int')
			reverse = get_setting("general.sortmethod.{}.reverse".format(i),'bool')

			if sort_method_settings[sm] is None:
				break

			if sort_method_settings[sm] == self._get_type_sort_key:
				self._get_type_sort_order()
			if sort_method_settings[sm] == self._get_debrid_priority_key:
				self._get_debrid_sort_order()
			if sort_method_settings[sm] == self._get_hdr_sort_key:
				self._get_hdr_sort_order()

			sort_methods.append((sort_method_settings[sm], reverse))

		self.sort_methods = sort_methods

	def sizeof_fmt(self, num, suffix="B"):
		for unit in ("", " Ki", " Mi", " Gi", " Ti", " Pi", " Ei", " Zi"):
			if abs(num) < 1024.0:
				return f"{num:3.1f}{unit}{suffix}"
			num /= 1024.0
		return f"{num:.1f}Yi{suffix}"

	def default_sort_methods(self):
		"""
import getSources, get_meta, tools
info = get_meta.blank_meta()
tools.SourceSorter(info).default_sort_methods()
"""
		set_setting("general.sortmethod.1",'5') #CAM_LOW
		set_setting("general.sortmethod.1.reverse",'false')
		set_setting("general.sortmethod.2",'1') #Quality
		set_setting("general.sortmethod.2.reverse",'false')
		set_setting("general.sortmethod.3",'4') #Size
		set_setting("general.sortmethod.3.reverse",'false')
		set_setting("general.sortmethod.4",'0')
		set_setting("general.sortmethod.4.reverse",'false')
		set_setting("general.sortmethod.4",'0')
		set_setting("general.sortmethod.5.reverse",'false')
		set_setting("general.sortmethod.6",'0')
		set_setting("general.sortmethod.6.reverse",'false')
		set_setting("general.sortmethod.7",'0')
		set_setting("general.sortmethod.7.reverse",'false')
		set_setting("general.sortmethod.8",'0')
		set_setting("general.sortmethod.8.reverse",'false')
		set_setting("general.minResolution",'3') #SD_MIN
		set_setting("general.maxResolution",'0') #4k_MAX
		set_setting("general.enablesizelimit",'false')
		set_setting("general.sizelimit.movie",'30')
		set_setting("general.sizelimit.episode",'3')
		set_setting("general.sizeminimum.movie",'0')
		set_setting("general.sizeminimum.episode",'0')
		set_setting("general.filters",'HI10,HC,WMV,3D,HYBRID,SCR,CAM')
		set_setting("general.sourcetypesort.1",'1') #cloud
		set_setting("general.sourcetypesort.2",'0') 
		set_setting("general.sourcetypesort.3",'0') 
		set_setting("general.sourcetypesort.4",'0') 
		set_setting("general.hdrsort.1",'2') #HDR
		set_setting("general.hdrsort.2",'0') 
		set_setting("general.debridsort.1",'2') #rd
		set_setting("general.debridsort.2",'0') 
		set_setting("general.debridsort.3",'0') 
		

	def get_sort_methods(self):
		"""
import getSources, get_meta, tools
info = get_meta.blank_meta()
tools.SourceSorter(info).get_sort_methods()
"""
		print('FILTERS=',self._get_filters())
		print('')
		print('FILTERS=disable_hdr=',self.disable_hdr)
		print('FILTERS=disable_dv=',self.disable_dv)
		print('')
		min_res = approved_qualities[get_setting("general.minResolution", 'int')]
		max_res = approved_qualities[get_setting("general.maxResolution", 'int')]
		print('RESOLUTION_MIN=',min_res)
		print('RESOLUTION_MAX=',max_res)
		print('')
		self._get_type_sort_order()
		self._get_hdr_sort_order()
		self._get_debrid_sort_order()
		print('SOURCE_TYPE_SORT=',list(self.type_priorities)[0])
		print('HDR_SORT=',list(self.hdr_priorities)[0])
		print('DEBRID_SORT=',list(self.debrid_priorities)[0])
		print('enablesizelimit=',get_setting("general.enablesizelimit", 'bool'))
		for i in ('episode','movie'):
				size_limit = get_setting("general.sizelimit.{}".format(i), 'float') * 1024
				size_minimum = get_setting("general.sizeminimum.{}".format(i), 'float') * 1024
				print('SIZE_MIN=', i,self.sizeof_fmt(size_minimum*1024*1024))
				print('SIZE_MAX=', i,self.sizeof_fmt(size_limit*1024*1024))
				print('')
		for i in self.sort_methods:
			for x in sort_method_names:
				if sort_method_names[x] in str(i):
					print(sort_method_list[str(x)], '	REVERSE=',i[1])
		print('')

	def _set_quality_sort_key(self):
		#print('_set_quality_sort_key')
		set_setting("general.sortmethod.{}".format(self.sort_int),self.setting_int)
		#print('REVERSE/TRUE/FALSE')
		result = selectFromDict(true_false, 'REVERSE Source Types Sort')
		set_setting("general.sortmethod.{}.reverse".format(self.sort_int), result)
		self._set_quality_sort_method()

	def _set_quality_sort_method(self):
		#print('RESOLUTION_MAX_MIN')
		sort_method_list = {
			'4K': '0',
			'1080p': '1',
			'720p': '2',
			'SD': '3',
		}
		for i in ('minResolution','maxResolution'):
			result = selectFromDict(true_false, 'Select ' + i)
			set_setting("general.{}".format(i), str(result))

	def _set_type_sort_key(self):
		#print('_set_type_sort_key')
		set_setting("general.sortmethod.{}".format(self.sort_int),self.setting_int)
		#print('REVERSE/TRUE/FALSE')
		result = selectFromDict(true_false, 'REVERSE Source Types Sort')
		set_setting("general.sortmethod.{}.reverse".format(self.sort_int), result)
		self._set_type_sort_method()

	def _set_type_sort_method(self):
		#print('SOURCE_TYPE_SORT')
		set_setting("general.sourcetypesort.1",'1') #cloud
		set_setting("general.sourcetypesort.2",'0') 
		set_setting("general.sourcetypesort.3",'0') 
		set_setting("general.sourcetypesort.4",'0') 
		"""
		type_priority_settings_list = {
			'None': 0,
			'cloud': 1,
			'adaptive': 2,
			'torrent': 3,
			'hoster': 4,
		}
		for i in range(1, 5):
			message = 'Set Types Sort Filter: ' + str(i)
			result = selectFromDict(type_priority_settings_list, 'Pick Source Types Sort')
			if result == '0':
				for x in range(i, 5):
					set_setting("general.sourcetypesort.{}".format(x),'0')
				break
			else:
				set_setting("general.sourcetypesort.{}".format(x),result)
		"""

	def _set_debrid_priority_key(self):
		#print('_set_debrid_priority_key')
		set_setting("general.sortmethod.{}".format(self.sort_int),self.setting_int)
		#print('REVERSE/TRUE/FALSE')
		result = selectFromDict(true_false, 'REVERSE Debrid Types Sort')
		set_setting("general.sortmethod.{}.reverse".format(self.sort_int), result)
		self._set_debrid_priority_method()

	def _set_debrid_priority_method(self):
		#print('DEBRID_TYPE_SORT')
		set_setting("general.debridsort.1",'2') #rd
		set_setting("general.debridsort.2",'0') 
		set_setting("general.debridsort.3",'0') 
		"""
		debrid_priority_settings = {
			'None': 0,
			'premiumize': 1,
			'real_debrid': 2,
			'all_debrid': 3,
		}
		for i in range(1, 4):
			message = 'Set Debrid Sort Filter: ' + str(i)
			result = selectFromDict(type_priority_settings_list, 'Pick Debrid Types Sort')
			if result == '0':
				for x in range(i, 4):
					set_setting("general.debridsort.{}".format(x),'0')
				break
			else:
				set_setting("general.debridsort.{}".format(x),result)
		"""


	def _set_size_sort_key(self):
		#print('_set_size_sort_key')
		set_setting("general.sortmethod.{}".format(self.sort_int),self.setting_int)
		#print('REVERSE/TRUE/FALSE')
		result = selectFromDict(true_false, 'REVERSE Sizes Sort')
		set_setting("general.sortmethod.{}.reverse".format(self.sort_int), result)
		self._set_size_sort_method()

	def _set_size_sort_method(self):
		#print('SIZE_LIMIT_ENABLE')
		result = selectFromDict(true_false, 'Size Limit enable')
		set_setting("general.enablesizelimit", result)
		if result == 'true':
			#print('SIZE_MAX_MIN')
			for i in ('episode','movie'):
					size_limit = input('Set size upper limit for ' + i + ' in Gb:  ')
					size_minimum = input('Set size lower limit for ' + i + ' in Gb:  ')
					set_setting("general.sizelimit.{}".format(i), str(size_limit))
					set_setting("general.sizeminimum.{}".format(i), str(size_minimum))

	def _set_low_cam_sort_key(self):
		#print('_set_low_cam_sort_key')
		#print(self.sort_int)
		#print(self.setting_int)
		#exit()
		set_setting("general.sortmethod.{}".format(self.sort_int),self.setting_int)
		#print('REVERSE/TRUE/FALSE')
		result = selectFromDict(true_false, 'REVERSE Low Quality Cam Sort')
		set_setting("general.sortmethod.{}.reverse".format(self.sort_int), result)

	def _set_hevc_sort_key(self):
		#print('_set_hevc_sort_key')
		set_setting("general.sortmethod.{}".format(self.sort_int),self.setting_int)
		#print('REVERSE/TRUE/FALSE')
		result = selectFromDict(true_false, 'REVERSE HEVC Sort')
		set_setting("general.sortmethod.{}.reverse".format(self.sort_int), result)

	def _set_hdr_sort_key(self):
		#print('_set_hdr_sort_key')
		set_setting("general.sortmethod.{}".format(self.sort_int),self.setting_int)
		#print('REVERSE/TRUE/FALSE')
		result = selectFromDict(true_false, 'REVERSE HDR Sort')
		set_setting("general.sortmethod.{}.reverse".format(self.sort_int), result)
		self._set_hdr_sort_method()


	def _set_hdr_sort_method(self):
		#print('HDR_SORT')
		hdr_priority_settings = {
			'None': 0,
			'DV': 1,
			'HDR': 2,
		}
		for i in range(1, 3):
			message = 'Set HDR Sort Filter: ' + str(i)
			result = selectFromDict(type_priority_settings_list, 'Pick Debrid Types Sort')
			if result == '0':
				for x in range(i, 3):
					set_setting("general.hdrsort.{}".format(x),'0')
				break
			else:
				set_setting("general.hdrsort.{}".format(x),result)


	def _set_audio_channels_sort_key():
		#print('_set_audio_channels_sort_key')
		set_setting("general.sortmethod.{}".format(self.sort_int),self.setting_int)
		#print('REVERSE/TRUE/FALSE')
		result = selectFromDict(true_false, 'REVERSE AUDIO Sort')
		set_setting("general.sortmethod.{}.reverse".format(self.sort_int), result)

	def _set_filters():
		#print('_set_filters')
		filter_string = ''
		curr_filters = self._get_filters()
		if len(curr_filters) == 1:
			filter_string = curr_filters[0]
		else:
			for i in curr_filters:
				filter_string = filter_string + i + ','
			filter_string = filter_string[:-1]
		result = selectFromDict(true_false, 'HDR Disable')
		if result == 'true':
			filter_string = filter_string + 'HDR'
		#print('HDR_DISABLE')
		#print('DV_DISABLE')
		result = selectFromDict(true_false, 'DV Disable')
		if result == 'true':
			filter_string = filter_string + 'DV'
		set_setting("general.filters" , filter_string)


	def set_sort_method_settings(self):
		"""
import getSources, get_meta, tools
info = get_meta.blank_meta()
tools.SourceSorter(info).set_sort_method_settings()
"""
		sort_method_settings = {
				0: None,
				1: self._set_quality_sort_key,
				2: self._set_type_sort_key,
				3: self._set_debrid_priority_key,
				4: self._set_size_sort_key,
				5: self._set_low_cam_sort_key,
				6: self._set_hevc_sort_key,
				7: self._set_hdr_sort_key,
				8: self._set_audio_channels_sort_key
			}
		self.get_sort_methods()
		sort_method_list2 = {}
		for i in sort_method_list:
			sort_method_list2[sort_method_list[i]] = i
		for i in range(1, 9):
			message = 'Set Sort Filter Number: ' + str(i) + '	(DEFAULT=CAM_LOW//QUALITY//SIZE)'
			print(message)
			result = selectFromDict(sort_method_list2, ' Sorting method')
			if result == '0':
				for x in range(i, 9):
					set_setting("general.sortmethod.{}".format(x),'0')
					set_setting("general.sortmethod.{}.reverse".format(x), 'false')
				break
			else:
				self.setting_int = result
				self.sort_int = i
				sort_method_settings[int(result)]()
		sort_method_settings = {
			'None (Exit)': 0,
			'HDR Sorting': 1,
			'Size limits': 2,
			#'Debrid Type Sorting': 3,
			#'Source Type Sorting': 4,
			'Quality Limits': 5,
			'Set Filters': 6,
			'Defaults': 7
			}
		for i in range(1, 7):
			result = selectFromDict(sort_method_settings, 'Setup Further Sorts/Filters/Limits')
			if result == 0:
				break
			if result == 1:
				self._set_hdr_sort_method
			if result == 2:
				self._set_size_sort_method
			if result == 3:
				self._set_debrid_priority_method
			if result == 4:
				self._set_type_sort_method
			if result == 5:
				self._set_quality_sort_method
			if result == 6:
				self._set_filters
			if result == 7:
				self.default_sort_methods()
		self.get_sort_methods()

	def _get_type_sort_order(self):
		"""
		Get seren settings for type sort priority
		"""
		type_priorities = {}

		for i in range(1, 5):
			tp = type_priority_settings.get(
				get_setting("general.sourcetypesort.{}".format(i), 'int')
			)
			if tp is None:
				break
			type_priorities[tp] = -i
		self.type_priorities = type_priorities

	def _get_hdr_sort_order(self):
		"""
		Get seren settings for type sort priority
		"""
		hdr_priorities = {}
		hdr_priority_settings = {
			0: None,
			1: "DV",
			2: "HDR",
		}

		for i in range(1, 3):
			hdrp = hdr_priority_settings.get(get_setting("general.hdrsort.{}".format(i), 'int'))
			if hdrp is None:
				break
			hdr_priorities[hdrp] = -i
		self.hdr_priorities = hdr_priorities

	def _get_debrid_sort_order(self):
		"""
		Get seren settings for debrid sort priority
		"""
		debrid_priorities = {}
		debrid_priority_settings = {
			0: None,
			1: "premiumize",
			2: "real_debrid",
			3: "all_debrid",
		}

		for i in range(1, 4):
			debridp = debrid_priority_settings.get(
				get_setting("general.debridsort.{}".format(i),'int')
			)
			if debridp is None:
				break
			debrid_priorities[debridp] = -i
		self.debrid_priorities = debrid_priorities

	def _sort_sources(self, sources_list):
		"""
		Sort a source list based on sort_methods defined by settings
		All sort method key methods should return key values for *descending* sort.  If a reversed sort is required,
		reverse is specified as a boolean for the second item of each tuple in sort_methods
		:param sources_list: The list of sources to sort
		:return: The list of sorted sources
		:rtype: list
		"""
		sources_list = sorted(sources_list, key=lambda s: s['release_title'])
		return sorted(sources_list, key=self._get_sort_key_tuple, reverse=True)

	def _get_sort_key_tuple(self, source):
		return tuple(
			-sm(source) if reverse else sm(source)
			for (sm, reverse) in self.sort_methods
			if sm
		)

	def _get_type_sort_key(self, source):
		return self.type_priorities.get(source.get("type"), -99)

	def _get_quality_sort_key(self, source):
		return self.quality_priorities.get(source.get("quality"), -99)

	def _get_debrid_priority_key(self, source):
		return self.debrid_priorities.get(source.get("debrid_provider"), self.FIXED_SORT_POSITION_OBJECT)

	def _get_size_sort_key(self, source):
		size = source.get("size", None)
		if size == "Variable":
			return self.FIXED_SORT_POSITION_OBJECT
		if size is None or not isinstance(size, (int, float)) or size < 0:
			size = 0
		return size

	@staticmethod
	def _get_low_cam_sort_key(source):
		return "CAM" not in source.get("info", {})

	@staticmethod
	def _get_hevc_sort_key(source):
		return "HEVC" in source.get("info", {})

	def _get_hdr_sort_key(self, source):
		hdrp = -99
		dvp = -99

		if "HDR" in source.get("info", {}):
			hdrp = self.hdr_priorities.get("HDR", -99)
		if "DV" in source.get("info", {}):
			dvp = self.hdr_priorities.get("DV", -99)

		return max(hdrp, dvp)

	def _get_last_release_name_sort_key(self, source):
		sm = SequenceMatcher(None, self.last_release_name, source['release_title'], autojunk=False)
		if sm.real_quick_ratio() < 1:
			return 0
		ratio = sm.ratio()
		if ratio < 0.85:
			return 0
		return ratio

	@staticmethod
	def _get_audio_channels_sort_key(source):
		audio_channels = None
		info = source['info']
		if info:
			audio_channels = {"2.0", "5.1", "7.1"} & info
		return float(max(audio_channels)) if audio_channels else 0



def get_fanart_results(tvdb_id, media_type=None, show_season = None):
	hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = '', '', '', '', '', '', '', '', '', '', '', '';
	tv_dict = {'hdclearart': None,'seasonposter': None,'seasonthumb': None,'seasonbanner': None,'tvthumb': None,'tvbanner': None,'showbackground': None,'clearlogo': None,'characterart': None,'tvposter': None,'clearart': None,'hdtvlogo': None}

	if 'tv_tvdb' == media_type:
		try: 
			response = get_fanart_data(tmdb_id=tvdb_id,media_type='tv_tvdb')
		except: 
			response = None
	else:
		response = get_fanart_data(tmdb_id=tvdb_id,media_type='movie')
	
	if 'tv_tvdb' == media_type:
		for i in response:
			#print_log(i)
			for j in response[i]:
				try:
					lang = j['lang']
					if j['lang'] == 'en' or (i == 'showbackground' and j['lang'] == ''):
						if i in ('seasonposter', 'seasonthumb', 'seasonbanner'):
							for k in response[i]:
								if int(k['season']) == show_season and k['lang'] == 'en':
									tv_dict[i] = k['url']
							break
						if i in ('hdclearart', 'tvthumb', 'tvbanner', 'showbackground', 'clearlogo', 'characterart', 'tvposter', 'clearart', 'hdtvlogo'):
							tv_dict[i] = j['url']
							break
				except:
					pass
		#return hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo
		return tv_dict['hdclearart'], tv_dict['seasonposter'], tv_dict['seasonthumb'], tv_dict['seasonbanner'], tv_dict['tvthumb'], tv_dict['tvbanner'], tv_dict['showbackground'], tv_dict['clearlogo'], tv_dict['characterart'], tv_dict['tvposter'], tv_dict['clearart'], tv_dict['hdtvlogo']
	else:
		movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = '', '', '', '', '', '', '', '', ''
		movie_dict = {'movielogo': None,'hdmovielogo': None,'movieposter': None,'hdmovieclearart': None,'movieart': None,'moviedisc': None,'moviebanner': None,'moviethumb': None,'moviebackground': None}
		for i in response:
			#print_log(i)
			for j in response[i]:
				try:
					lang = j['lang']
					if j['lang'] == 'en' or (i == 'movielogo' and j['lang'] == '') or (i == 'hdmovielogo' and j['lang'] == ''):
						if i in ('movielogo', 'hdmovielogo'):
							tv_dict[i] = j['url']
							break
						if i in ('movieposter','hdmovieclearart','movieart','moviedisc','moviebanner','moviethumb','moviebackground'):
							for k in response[i]:
								if k['lang'] == 'en':
									tv_dict[i] = k['url']
				except:
					pass

		#return movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground
		return movie_dict['movielogo'], movie_dict['hdmovielogo'], movie_dict['movieposter'], movie_dict['hdmovieclearart'], movie_dict['movieart'], movie_dict['moviedisc'], movie_dict['moviebanner'], movie_dict['moviethumb'], movie_dict['moviebackground']