# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import sys
import codecs
import os
import time
import hashlib
import requests
import json
from urllib.parse import quote_plus

import xbmcaddon
import xbmcvfs
import xbmc

HEADERS = {'User-agent': 'Mozilla/5.0'}

ADDON = xbmcaddon.Addon()
SETTING = ADDON.getSetting
ADDON_PATH = os.path.join(os.path.dirname(__file__), "..")
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_DATA_PATH = xbmcvfs.translatePath("special://profile/addon_data/%s" % ADDON_ID)
CACHE_PATH = xbmcvfs.translatePath('special://profile/addon_data/'+str(ADDON_ID)+'/cache.db')

MONITOR = xbmc.Monitor()


def get_autocomplete_items(search_str, limit=10, provider=None):
	"""
	get dict list with autocomplete
	"""
	if xbmc.getCondVisibility("System.HasHiddenInput"):
		return []
	if SETTING("autocomplete_provider") == "youtube":
		provider = GoogleProvider(youtube=True, limit=limit)
	elif SETTING("autocomplete_provider") == "google":
		provider = GoogleProvider(limit=limit)
	elif SETTING("autocomplete_provider") == "IMDB":
		provider = IMDBProvider(limit=limit)
	elif SETTING("autocomplete_provider") == "bing":
		provider = BingProvider(limit=limit)
	else:
		provider = LocalDictProvider(limit=limit)
	provider.limit = limit
	return provider.get_predictions(search_str)


def prep_search_str(text):
	for char in text:
		if 1488 <= ord(char) <= 1514:
			return text[::-1]
	return text


class BaseProvider(object):

	def __init__(self, *args, **kwargs):
		self.limit = int(kwargs.get("limit", 10))

	def get_predictions(self, search_str):
		if not search_str:
			return []
		items = []
		result = self.fetch_data(search_str)
		for i, item in enumerate(result):
			li = {"label": item,
				  "search_string": prep_search_str(item)}
			items.append(li)
			if i > int(self.limit):
				break
		return items

	def get_prediction_listitems(self, search_str):
		for item in self.get_predictions(search_str):
			li = {"label": item,
				  "search_string": search_str}
			yield li


class GoogleProvider(BaseProvider):

	BASE_URL = "http://clients1.google.com/complete/"

	def __init__(self, *args, **kwargs):
		super(GoogleProvider, self).__init__(*args, **kwargs)
		self.youtube = kwargs.get("youtube", False)

	def fetch_data(self, search_str):
		url = "search?hl=%s&q=%s&json=t&client=serp" % (SETTING("autocomplete_lang"), quote_plus(search_str))
		if self.youtube:
			url += "&ds=yt"
		result = get_JSON_response(url=self.BASE_URL + url,
								   headers=HEADERS,
								   folder="Google")
		if not result or len(result) <= 1:
			return []
		else:
			return result[1]


class BingProvider(BaseProvider):

	BASE_URL = "http://api.bing.com/osjson.aspx?"

	def __init__(self, *args, **kwargs):
		super(BingProvider, self).__init__(*args, **kwargs)

	def fetch_data(self, search_str):
		url = "query=%s" % (quote_plus(search_str))
		result = get_JSON_response(url=self.BASE_URL + url,
								   headers=HEADERS,
								   folder="Bing")
		if not result:
			return []
		else:
			return result[1]

class IMDBProvider(BaseProvider):

	BASE_URL = "https://v2.sg.media-imdb.com/"

	def __init__(self, *args, **kwargs):
		super(IMDBProvider, self).__init__(*args, **kwargs)

	def fetch_data(self, search_str):
		url = "suggests/%s/%s.json" % (search_str[0],quote_plus(search_str))
		result = get_JSON_response(url=self.BASE_URL + url,
								   headers=HEADERS,
								   folder="IMDB")
		imdb_response = result
		result = [search_str, []]
		try:
			for i in imdb_response['d']:
				if 'trailers' in str(i).lower() and 'Trailers' not in result[1]:
					result[1].append('Trailers')
				if i.get('q') in ('feature', 'TV series','tvSeries', 'movie') and i.get('qid') in ('feature', 'TV series','tvSeries', 'movie'):
					result[1].append(i['l'])
			if not result:
				return []
			else:
				return result[1]
		except TypeError:
			return []

class LocalDictProvider(BaseProvider):

	def __init__(self, *args, **kwargs):
		super(LocalDictProvider, self).__init__(*args, **kwargs)

	def get_predictions(self, search_str):
		"""
		get dict list with autocomplete labels from locally saved lists
		"""
		listitems = []
		k = search_str.rfind(" ")
		if k >= 0:
			search_str = search_str[k + 1:]
		local = SETTING("autocomplete_lang_local")
		path = os.path.join(ADDON_PATH, "resources", "data", "common_%s.txt" % (local if local else "en"))
		with codecs.open(path, encoding="utf8") as f:
			for line in f.readlines():
				if not line.startswith(search_str) or len(line) <= 2:
					continue
				li = {"label": line,
					  "search_string": line}
				listitems.append(li)
				if len(listitems) > self.limit:
					break
		return listitems


db_con = None
def test_db():
	import sqlite3
	if not os.path.exists(ADDON_DATA_PATH):
		os.makedirs(ADDON_DATA_PATH)
	db_con = sqlite3.connect(CACHE_PATH, check_same_thread=False)
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

def clear_db(connection=None,table_name=None):
	if db_con == None:
		connection = db_start()
	cur = connection.cursor()
	#[('Trakt',), ('TheMovieDB',), ('rss',), ('IMDB',), ('TasteDive',), ('FanartTV',), ('YouTube',), ('TVMaze',), ('show_filters',), ('Google',)]
	#dbfile = '/home/osmc/.kodi/userdata/addon_data/script.extendedinfo/cache.db'
	#con = sqlite3.connect(dbfile)
	#cur = con.cursor()

	table_list = [a for a in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
	for i in table_list:
		#cur.execute("SELECT * from %s" % (i)).fetchall()
		if table_name:
			i = table_name#
		tools.log(str(i))
		result = cur.execute('SELECT * FROM %s' % (i)).fetchall()
		tools.log(str(len(result)))
		cur.execute('DELETE FROM %s' % (i))
		tools.log(str('DELETE FROM %s ' % (i))) 
		if table_name:
			break
	connection.commit()
	cur.execute('VACUUM')
	cur.close()

def tools_log(*args, **kwargs):
	for i in args:
		try:
			import xbmc
			xbmc.log(str(i)+'===>AUTOCOMPLETION', level=xbmc.LOGINFO)
		except:
			print(i)


def write_db(connection=None,url=None, cache_days=7.0, folder=False,cache_val=None, headers=False):
	if db_con == None:
		connection = db_start()
	try: cur = connection.cursor()
	except: connection = db_start()
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
	try: 
		connection.commit()
	except:
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
	try: 
		connection.commit()
	except:
		try: connection.commit()
		except: pass
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
			return None, None
		else:
			tools.log(str(ex))
	if len(sql_result) ==0:
		cur.close()
		return None, None

	#if cache_days <=0.00001:
	#	tools.log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	#	tools.log(str(url))
	#	tools.log(str(int(time.time()))+str('<><>')+str(int(sql_result[0][1])))
	
	expire = round(time.time() + cache_seconds,0)
	cache_type = sql_result[0][2]
	if cache_type == 'str':
		cache_val = decode_db(sql_result[0][0])
	elif cache_type == 'list':
		cache_val = eval(decode_db(sql_result[0][0]))
	elif cache_type == 'json':
		cache_val = json.loads(decode_db(sql_result[0][0]))

	if int(time.time()) >= int(sql_result[0][1]) or expire <= int(sql_result[0][1]) :
		sql_query = """DELETE FROM %s
		where url = '%s'
		""" % (folder, hashed_url)
		sql_result = cur.execute(sql_query).fetchall()
		connection.commit()
		cur.close()
		return None, cache_val
	else:
		cur.close()
		return cache_val, None

def db_delete_expired(connection=None):
	if db_con == None:
		connection = db_start()
	cur = connection.cursor()
	curr_time = int(time.time())
	db_delete_expired_query = """SELECT * FROM sqlite_master WHERE type='table'
	"""  
	sql_result = cur.execute(db_delete_expired_query).fetchall()
	tools_log('DELETE____')
	for i in sql_result:
		folder = i[1]
		#tools_log(folder)
		#tools_log(str(folder))
		#db_delete_expired_query = """select * FROM %s
		#where expire < %s
		#""" % (folder, curr_time)
		#sql_result = cur.execute(db_delete_expired_query).fetchall()
		#tools_log(str(len(sql_result))+str(folder))
		db_delete_expired_query = """select * FROM %s
		where expire < %s
		""" %  (folder, curr_time)
		sql_result1 = cur.execute(db_delete_expired_query).fetchall()
		if len(sql_result1) == 0:
			continue
		tools_log(folder)
		db_delete_expired_query = """DELETE FROM %s
		where expire < %s
		""" % (folder, curr_time)
		sql_result2 = cur.execute(db_delete_expired_query).fetchall()
		tools_log(str(len(sql_result1))+str(folder),'===>DELETED')
	connection.commit()
	try: cur.execute('VACUUM')
	except Exception as ex:
		if 'SQL statements in progress' in str(ex):
			return None
		else:
			tools_log(str(ex))
	cur.close()
	tools_log('DELETED')
	return None


db_start = test_db()
db_con = db_start

def get_JSON_response(url='', cache_days=7.0, folder=False, headers=False):
	now = time.time()
	url = url.encode('utf-8')
	hashed_url = hashlib.md5(url).hexdigest()
	cache_seconds = int(cache_days * 86400.0)

	try: 
		db_result, expired_db_result = query_db(connection=db_con,url=url, cache_days=cache_days, folder=folder, headers=headers)
	except:
		db_result, expired_db_result = None, None
	try: 
		db_result_flag = True if len(db_result)> 0 else False
	except: 
		db_result_flag = False
	if db_result_flag:
		return db_result
	else:
		if folder == 'IMDB':
			response = get_imdb_http(url, headers)
		else:
			response = get_http(url, headers)

		try:
			if folder == 'IMDB':
				results = response
			else:
				results = json.loads(response)
		except: results = []
	if not results or len(results) == 0:
		if expired_db_result == None:
			return []
		if len(expired_db_result) > 0:
			write_db(connection=db_con,url=url, cache_days=0.25, folder=folder,cache_val=expired_db_result)
			return expired_db_result
		return []
	else:
		write_db(connection=db_con,url=url, cache_days=cache_days, folder=folder,cache_val=results)
	return results

'''
def get_JSON_response(url="", cache_days=7.0, folder=False, headers=False):
	"""
	get JSON response for *url, makes use of file cache.
	"""
	now = time.time()
	hashed_url = hashlib.md5(url.encode()).hexdigest()
	if folder:
		cache_path = xbmcvfs.translatePath(os.path.join(ADDON_DATA_PATH, folder))
	else:
		cache_path = xbmcvfs.translatePath(os.path.join(ADDON_DATA_PATH))
	path = os.path.join(cache_path, hashed_url + ".txt")
	cache_seconds = int(cache_days * 86400.0)
	if xbmcvfs.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
		results = read_from_file(path)
		log("loaded file for %s. time: %f" % (url, time.time() - now))
	else:
		if folder == 'IMDB':
			response = get_imdb_http(url, headers)
		else:
			response = get_http(url, headers)
		try:
			if folder == 'IMDB':
				results = response
			else:
				results = json.loads(response)
			log("download %s. time: %f" % (url, time.time() - now))
			save_to_file(results, hashed_url, cache_path)
		except Exception:
			log("Exception: Could not get new JSON data from %s. Tryin to fallback to cache" % url)
			log(response)
			if xbmcvfs.exists(path):
				results = read_from_file(path)
			else:
				results = []
	if results:
		return results
	else:
		return []
'''

def get_imdb_http(url=None, headers=False):
	"""
	fetches data from *url, returns it as a string
	"""
	succeed = 0
	if not headers:
		headers = HEADERS
	while succeed < 2 and not MONITOR.abortRequested():
		try:
			r = requests.get(url, headers=headers)
			if r.status_code != 200:
				raise Exception
			r = json.loads(r.text[r.text.index('(')+1:-1])
			return r
		except Exception:
			log("get_http: could not get data from %s" % url)
			xbmc.sleep(1000)
			succeed += 1
	return None

def get_http(url=None, headers=False):
	"""
	fetches data from *url, returns it as a string
	"""
	succeed = 0
	if not headers:
		headers = HEADERS
	while succeed < 2 and not MONITOR.abortRequested():
		try:
			r = requests.get(url, headers=headers)
			if r.status_code != 200:
				raise Exception
			return r.text
		except Exception:
			log("get_http: could not get data from %s" % url)
			xbmc.sleep(1000)
			succeed += 1
	return None


def read_from_file(path="", raw=False):
	"""
	return data from file with *path
	"""
	if not xbmcvfs.exists(path):
		return False
	try:
		with open(path) as f:
			log("opened textfile %s." % (path))
			if raw:
				return f.read()
			else:
				return json.load(f)
	except Exception:
		log("failed to load textfile: " + path)
		return False


def log(txt):
	message = u'%s: %s' % (ADDON_ID, txt)
	xbmc.log(msg=message, level=xbmc.LOGDEBUG)


def save_to_file(content, filename, path=""):
	"""
	dump json and save to *filename in *path
	"""
	if not xbmcvfs.exists(path):
		xbmcvfs.mkdirs(path)

	text_file_path = os.path.join(path, filename + ".txt")
	now = time.time()

	with open(text_file_path, 'w') as f:
		json.dump(content, f)

	log("saved textfile %s. Time: %f" % (text_file_path, time.time() - now))
	return True
