import os, re, time, json, urllib.request, urllib.parse, urllib.error, hashlib, requests, threading, sys
from datetime import datetime
import time
from datetime import date
try:
	import xbmc, xbmcgui, xbmcvfs, xbmcaddon, xbmcplugin
	XBMC_RUNNING = True
except: 
	XBMC_RUNNING = False

from functools import wraps
from inspect import currentframe, getframeinfo
#log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

if XBMC_RUNNING:
	from resources.lib.library import addon_ID
	#from resources.lib.library import fanart_api_key

	try: from infotagger.listitem import ListItemInfoTag
	except: pass


	ADDON_PATH = xbmcvfs.translatePath('special://home/addons/'+str(addon_ID()))
	ADDON_DATA_PATH = xbmcvfs.translatePath('special://profile/addon_data/'+str(addon_ID()))
	CACHE_PATH = xbmcvfs.translatePath('special://profile/addon_data/'+str(addon_ID())+'/cache.db')

	IMAGES_DATA_PATH = xbmcvfs.translatePath('special://profile/addon_data/'+str(addon_ID())+'/images')
	SKIN_DIR = xbmc.getSkinDir()
	#AUTOPLAY_TRAILER = xbmcaddon.Addon().getSetting('autoplay_trailer')
	#NETFLIX_VIEW = xbmcaddon.Addon().getSetting('netflix_view')
	#NETFLIX_VIEW2 = xbmcaddon.Addon().getSetting('netflix_info_view')

	window_stack_enable = xbmcaddon.Addon().getSetting('window_stack_enable')
	trakt_kodi_mode = xbmcaddon.Addon().getSetting('trakt_kodi_mode')
	imdb_recommendations = xbmcaddon.Addon().getSetting('imdb_recommendations')
	
	fanart_api_key = xbmcaddon.Addon().getSetting('fanart_api')
	fanart_api = fanart_api_key
	tmdb_API_key = xbmcaddon.Addon().getSetting('tmdb_api')
	tmdb_api = tmdb_API_key

	xtreme_codes_server_path = xbmcaddon.Addon().getSetting('xtreme_codes.base_url')
	xtreme_codes_username = xbmcaddon.Addon().getSetting('xtreme_codes.username')
	xtreme_codes_password = xbmcaddon.Addon().getSetting('xtreme_codes.password')
	xtreme_wanted_groups = xbmcaddon.Addon().getSetting('xtreme_wanted_groups')
	m3u_ts_m3u8_option = xbmcaddon.Addon().getSetting('m3u_ts_m3u8_option')
	pvr_client = xbmcaddon.Addon().getSetting('pvr_client')
	if xbmcaddon.Addon(addon_ID()).getSetting('subtitle_lookup') == 'true':
		subtitle_lookup = True
	else:
		subtitle_lookup = False

	if xbmcaddon.Addon(addon_ID()).getSetting('local_xml_m3u') == 'true':
		local_xml_m3u = True
	else:
		local_xml_m3u = False
	if xbmcaddon.Addon(addon_ID()).getSetting('startup_local_xml_m3u') == 'true':
		startup_local_xml_m3u = True
	else:
		startup_local_xml_m3u = False
else:
	folder = str(os.path.split(str(getframeinfo(currentframe()).filename))[0])
	current_directory = os.path.dirname(os.path.dirname(folder))
	ADDON_PATH = os.path.dirname(os.path.dirname(folder))
	ADDON_DATA_PATH = os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.dirname(current_directory)),'userdata'),'addon_data'),'script.xtreme_vod')
	CACHE_PATH = os.path.join(ADDON_DATA_PATH, 'cache.db')
	IMAGES_DATA_PATH = os.path.join(ADDON_DATA_PATH, 'images')
	ADDON_SETTINGS_PATH = os.path.join(ADDON_DATA_PATH, 'settings.xml')
	channel_order = ''
	f = open(ADDON_SETTINGS_PATH, "r")
	output_folder = ''
	local_xml_m3u = False
	startup_local_xml_m3u = False
	output_folder_select = None
	for i in f:
		if 'xtreme_codes.base_url' in str(i):
			try:xtreme_codes_server_path = i.split('xtreme_codes.base_url"')[1].split('>')[1].split('<')[0]
			except: pass
		if 'xtreme_codes.username' in str(i):
			xtreme_codes_username = i.split('xtreme_codes.username"')[1].split('>')[1].split('<')[0]
		if 'xtreme_codes.password' in str(i):
			xtreme_codes_password = i.split('xtreme_codes.password"')[1].split('>')[1].split('<')[0]
		if 'm3u_ts_m3u8_option' in str(i):
			m3u_ts_m3u8_option = i.split('m3u_ts_m3u8_option"')[1].split('>')[1].split('<')[0]
		if 'pvr_client' in str(i):
			pvr_client = i.split('pvr_client"')[1].split('>')[1].split('<')[0]

		if 'fanart_api"' in str(i):
			fanart_api_key = i.split('fanart_api"')[1].split('>')[1].split('<')[0]
			fanart_api = fanart_api_key
		if 'tmdb_api"' in str(i):
			tmdb_API_key = i.split('tmdb_api"')[1].split('>')[1].split('<')[0]
			tmdb_api = tmdb_API_key

		if 'local_xml_m3u"' in str(i):
			local_xml_m3u = i.split('local_xml_m3u"')[1].split('>')[1].split('<')[0]
		if local_xml_m3u == 'true':
			local_xml_m3u = True
		elif local_xml_m3u == 'false':
			local_xml_m3u = False

		if 'subtitle_lookup"' in str(i):
			subtitle_lookup = i.split('subtitle_lookup"')[1].split('>')[1].split('<')[0]
		if subtitle_lookup == 'true':
			subtitle_lookup = True
		elif subtitle_lookup == 'false':
			subtitle_lookup = False

		if 'startup_local_xml_m3u"' in str(i):
			startup_local_xml_m3u = i.split('startup_local_xml_m3u"')[1].split('>')[1].split('<')[0]
		if startup_local_xml_m3u == 'true':
			startup_local_xml_m3u = True
		elif startup_local_xml_m3u == 'false':
			startup_local_xml_m3u = False

	f.close()

if xtreme_codes_server_path and str(xtreme_codes_server_path) != '':
	if xtreme_codes_server_path[-1] != '/' and len(xtreme_codes_server_path) > 8:
		xtreme_codes_server_path = xtreme_codes_server_path + '/'

def tools_log(*args, **kwargs):
	for i in args:
		try:
			import xbmc
			xbmc.log(str(i)+'===>xtreme_vod', level=xbmc.LOGINFO)
		except:
			print(i)

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
		tools_log(str(i))
		result = cur.execute('SELECT * FROM %s' % (i)).fetchall()
		tools_log(str(len(result)))
		cur.execute('DELETE FROM %s' % (i))
		tools_log(str('DELETE FROM %s ' % (i))) 
		if table_name:
			break
	connection.commit()
	cur.execute('VACUUM')
	cur.close()



def write_db(connection=None,url=None, cache_days=7.0, folder=False,cache_val=None, headers=False):
	if db_con == None:
		connection = db_start()
	try: cur = connection.cursor()
	except: connection = db_start()
	try: url = url.encode('utf-8')
	except: pass
	hashed_url = hashlib.md5(url).hexdigest()
	cache_seconds = int(cache_days * 86400.0)
	#tools_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	#tools_log(str(url))
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
	#	tools_log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))
	#	tools_log(str(url))
	#	tools_log(str(int(time.time()))+str('<><>')+str(int(sql_result[0][1])))
	
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

def show_busy():
	#window_id = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
	#window_id = json.loads(window_id)
	#if not window_id['result']['currentwindow']['id'] == 10025 and not window_id['result']['currentwindow']['id'] > 13000:
	if str(os.environ.get('first_run', 'False')) == 'True':
		os.environ['first_run'] = str('False')
		return
	if 'widget=true' in str(sys.argv) or 'autocomplete' in str(sys.argv) or xbmc.getCondVisibility('Window.IsActive(12000)'):
		return
	elif xbmc.Player().isPlaying():
		return
	elif int(xbmc.getInfoLabel('System.BuildVersion')[:2]) > 17:
		xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
	else:
		xbmc.executebuiltin('ActivateWindow(busydialog)')

def hide_busy():
	if int(xbmc.getInfoLabel('System.BuildVersion')[:2]) > 17:
		xbmc.sleep(250)
		xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
		xbmc.executebuiltin('Dialog.Close(busydialog)')
		xbmc.executebuiltin('Dialog.Close(ExtendedProgressDialog,True)')
		xbmc.executebuiltin('Dialog.Close(progressdialog,True)')
	else:
		xbmc.sleep(250)
		xbmc.executebuiltin('Dialog.Close(busydialog)')


def get_file_age(filepath):
	import os
	import time

	if not os.path.exists(filepath):
		return None

	mod_time = os.path.getmtime(filepath)
	current_time = time.time()
	age_seconds = current_time - mod_time
	age_minutes = age_seconds / 60
	age_hours = age_minutes / 60
	age_days = age_hours / 24

	return {
		"seconds": age_seconds,
		"minutes": age_minutes,
		"hours": age_hours,
		"days": age_days
	}



def tv_db_path():
	#from glob import glob as glog
	import glob
	db_name = 'TV*.db'
	path_db = 'special://profile/Database/%s' % db_name
	filelist = sorted(glob.glob(xbmcvfs.translatePath(path_db)))
	if filelist:
		return filelist[-1]

def pvr_demo_trigger(enabled=None, addonid=None):
	import json
	json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", "params": {"addonid": "pvr.demo", "enabled": true}, "id": 1}')
	json_object  = json.loads(json_result)
	tools_log(json_object)
	json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", "params": {"addonid": "pvr.demo", "enabled": false}, "id": 1}')
	json_object  = json.loads(json_result)
	tools_log(json_object)


def addon_disable_reable(enabled=None, addonid=None):
	import json
	if enabled == False:
		kodi_params = ('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":8,"params":{"addonid":"%s","enabled":false}}' % (addonid))
	elif enabled == True:
		kodi_params = ('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":8,"params":{"addonid":"%s","enabled":true}}' % (addonid))
	json_result = xbmc.executeJSONRPC(kodi_params)
	json_object  = json.loads(json_result)
	tools_log(json_object)

def get_pvr_clients():
	import json
	json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"PVR.GetClients","id":"1"}')
	json_object  = json.loads(json_result)
	pvr_clients = []
	try:
		for i in json_object['result']['clients']:
			pvr_clients.append(i['addonid'])
	except:
		return ['pvr.iptvsimple']
	return pvr_clients

def ResetEPG():
	##https://github.com/xbmc/xbmc/blob/master/xbmc/pvr/PVRDatabase.cpp
	import sqlite3
	from pathlib import Path
	db_path = tv_db_path()
	db_path = Path(db_path)
	tools_log('ResetEPG')
	# Check the database exists
	if not db_path.exists():
		raise FileNotFoundError(f"Database not found at {db_path}")

	# Connect to the database
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	result = cursor.execute("UPDATE channels SET idEpg = 0").fetchall()
	tools_log(result)
	conn.commit()
	cursor.close()
	conn.close()
	return


def context_play(window=None,tmdb_id=None):
	from resources.lib.VideoPlayer import PLAYER
	import json
	hide_busy()
	json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["ListItem.Title", "ListItem.Label",  "ListItem.MovieTitle",    "ListItem.DBTYPE",  "ListItem.Season", "ListItem.Episode", "ListItem.Year",  "ListItem.IMDBNumber", "ListItem.Property(tmdb_id)","ListItem.DBID",   "ListItem.TVShowTitle", "ListItem.FileNameAndPath", "ListItem.UniqueID(tmdb)", "ListItem.UniqueID(imdb)", "Container.ListItem.UniqueID(imdb)"]}, "id":1}')
	json_object  = json.loads(json_result)

	dbid = json_object['result']['ListItem.DBID']
	type = json_object['result']['ListItem.DBTYPE']
	try: type = window.info['media_type']
	except: pass
	episode = json_object['result']['ListItem.Episode']
	try: episode = window.info['episode']
	except: pass
	Season = json_object['result']['ListItem.Season']
	try: Season = window.info['season']
	except: pass
	TVShowTitle = json_object['result']['ListItem.TVShowTitle']
	MovieTitle = json_object['result']['ListItem.MovieTitle']
	Title = json_object['result']['ListItem.Title']
	Label = json_object['result']['ListItem.Label']
	remote_id = json_object['result']['ListItem.UniqueID(tmdb)']
	if remote_id != tmdb_id:
		remote_id = tmdb_id
	tmdb_id2 = json_object['result']['ListItem.Property(tmdb_id)']
	if not tmdb_id or tmdb_id2 != tmdb_id:
		tmdb_id = tmdb_id2
	if tmdb_id and remote_id != tmdb_id:
		remote_id = tmdb_id
	imdb = json_object['result']['ListItem.UniqueID(imdb)']

	#json_object['result']['ListItemTMDBNumber'] = property_value
	if dbid == None or dbid == '':
		dbid = 0

	IMDBNumber = json_object['result']['ListItem.IMDBNumber']
	if (IMDBNumber == '' or IMDBNumber == None):
		IMDBNumber = imdb
	#tools_log(str(json_object))

	if not type in ['movie','tvshow','season','episode','actor','director']:
		if (episode == '' or episode == None) and (TVShowTitle == '' or TVShowTitle == None):
			type = 'movie'
		else:
			type = 'tvshow'

	#tools_log(json_object)
	params = {}
	infos = []
	if (TVShowTitle == '' or TVShowTitle == None):
		TVShowTitle = Title
	if type   == 'movie':
		if (MovieTitle == '' or MovieTitle == None):
			MovieTitle = Title
		PLAYER.prepare_play_VOD_movie(tmdb = remote_id, title = None, stream_id=None, search_str = None, window=window)
		return
	elif type == 'tvshow':
		from resources.lib.library import trakt_next_episode_rewatch
		tmdb_id, season, episode = trakt_next_episode_rewatch(tmdb_id_num=remote_id)
		PLAYER.prepare_play_VOD_episode(tmdb = tmdb_id, series_id=None, search_str = None,episode=episode, season=season, window=window)
		return
	elif type == 'season':
		episode = 1
		PLAYER.prepare_play_VOD_episode(tmdb = remote_id, series_id=None, search_str = None,episode=episode, season=Season, window=window)
		return
	elif type == 'episode':
		PLAYER.prepare_play_VOD_episode(tmdb = remote_id, series_id=None, search_str = None,episode=episode, season=Season, window=window)
		return


def busy_dialog(func):
	@wraps(func)
	def decorator(self, *args, **kwargs):
		show_busy()
		result = func(self, *args, **kwargs)
		hide_busy()
		return result
	return decorator


def run_async(func):
	@wraps(func)
	def async_func(*args, **kwargs):
		func_hl = threading.Thread(target=func, args=args, kwargs=kwargs)
		func_hl.start()
		return func_hl
	return async_func

def translate_path(*args):
	return xbmcvfs.translatePath(os.path.join(*args))


def dictfind(lst, key, value):
	for i, dic in enumerate(lst):
		if dic[key] == value:
			return dic
	return ''

def format_time(time, format=None):
	try:
		intTime = int(time)
	except:
		return time
	hour = str(intTime / 60)
	minute = str(intTime % 60).zfill(2)
	if format == 'h':
		return round(float(hour),2)
	elif format == 'm':
		return minute
	elif intTime >= 60:
		return str(int(float(hour))) + 'h ' + minute + 'm'
	else:
		return minute + 'm'

def url_quote(input_string):
	try:
		return urllib.parse.quote_plus(input_string.encode('utf8', 'ignore'))
	except:
		return urllib.parse.quote_plus(str(input_string, 'utf-8').encode('utf-8'))

def calculate_age(born, died=False):
	if died:
		ref_day = died.split('-')
	elif born:
		date1 = date.today()
		ref_day = [date1.year, date1.month, date1.day]
	else:
		return ''
	actor_born = born.split('-')
	base_age = int(ref_day[0]) - int(actor_born[0])
	if len(actor_born) > 1:
		diff_months = int(ref_day[1]) - int(actor_born[1])
		diff_days = int(ref_day[2]) - int(actor_born[2])
		if diff_months < 0 or (diff_months == 0 and diff_days < 0):
			base_age -= 1
		elif diff_months == 0 and diff_days == 0 and not died:
			notify('Happy Birthday (%i)' % base_age)
	return base_age

def millify(n):
	millnames = [' ', '.000', ' ' + 'Million', ' ' + 'Billion', ' ' + 'Trillion']
	if not n or n <= 100:
		return ''
	n = float(n)
	char_count = len(str(n))
	millidx = int((char_count / 3)) - 1
	if millidx == 3 or char_count == 9:
		return '%.2f%s' % (n / 10 ** (3 * millidx), millnames[millidx])
	else:
		return '%.0f%s' % (n / 10 ** (3 * millidx), millnames[millidx])

def media_streamdetails(filename, streamdetails):
	info = {}
	video = streamdetails['video']
	audio = streamdetails['audio']
	info['VideoCodec'] = ''
	info['VideoAspect'] = ''
	info['VideoResolution'] = ''
	info['AudioCodec'] = ''
	info['AudioChannels'] = ''
	if video:
		if (video[0]['width'] <= 720 and video[0]['height'] <= 480):
			info['VideoResolution'] = '480'
		elif (video[0]['width'] <= 768 and video[0]['height'] <= 576):
			info['VideoResolution'] = '576'
		elif (video[0]['width'] <= 960 and video[0]['height'] <= 544):
			info['VideoResolution'] = '540'
		elif (video[0]['width'] <= 1280 and video[0]['height'] <= 720):
			info['VideoResolution'] = '720'
		elif (video[0]['width'] <= 1920 or video[0]['height'] <= 1080):
			info['VideoResolution'] = '1080'
		elif video[0]['width'] * video[0]['height'] >= 6000000:
			info['VideoResolution'] = '4K'
		else:
			info['videoresolution'] = ''
		info['VideoCodec'] = str(video[0]['codec'])
		if (video[0]['aspect'] < 1.3499):
			info['VideoAspect'] = '1.33'
		elif (video[0]['aspect'] < 1.5080):
			info['VideoAspect'] = '1.37'
		elif (video[0]['aspect'] < 1.7190):
			info['VideoAspect'] = '1.66'
		elif (video[0]['aspect'] < 1.8147):
			info['VideoAspect'] = '1.78'
		elif (video[0]['aspect'] < 2.0174):
			info['VideoAspect'] = '1.85'
		elif (video[0]['aspect'] < 2.2738):
			info['VideoAspect'] = '2.20'
		elif (video[0]['aspect'] < 2.3749):
			info['VideoAspect'] = '2.35'
		elif (video[0]['aspect'] < 2.4739):
			info['VideoAspect'] = '2.40'
		elif (video[0]['aspect'] < 2.6529):
			info['VideoAspect'] = '2.55'
		else:
			info['VideoAspect'] = '2.76'
	elif ((b'dvd') in filename and not (b'hddvd' or b'hd-dvd') in filename) or (filename.endswith(b'.vob' or b'.ifo')):
		info['VideoResolution'] = '576'
	elif ((b'bluray' or b'blu-ray' or b'brrip' or b'bdrip' or b'hddvd' or b'hd-dvd') in filename):
		info['VideoResolution'] = '1080'
	if audio:
		info['AudioCodec'] = audio[0]['codec']
		info['AudioChannels'] = audio[0]['channels']
	return info

def fetch(dictionary, key):
	if key in dictionary:
		if dictionary[key] is not None:
			return dictionary[key]
	else:
		return ''

def get_year(year_string):
	if year_string and len(year_string) > 3:
		return year_string[:4]
	else:
		return ''

def get_http(url, headers=False):
	succeed = 0
	if not headers:
		headers = {'User-agent': 'Kodi/18.0 ( phil65@kodi.tv )'}
	while (succeed < 2) :
		try:
			request = requests.get(url, headers=headers)
			if 'Trakt is down for scheduled' in str(request.text):
				return None
			return request.text
		except Exception as e:
			log('get_http: could not get data from %s' % url)
			xbmc.sleep(500)
			succeed += 1
	return None

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
		response = get_http(url, headers)
		try: results = json.loads(response)
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


class GetFileThread(threading.Thread):
	def __init__(self, url):
		threading.Thread.__init__(self)
		self.url = url

	def run(self):
		self.file = get_file(self.url)

def get_file(url):
	clean_url = translate_path(urllib.parse.unquote(url)).replace('image://', '')
	clean_url = clean_url.rstrip('/')
	cached_thumb = xbmc.getCacheThumbName(clean_url)
	vid_cache_file = os.path.join('special://profile/Thumbnails/Video', cached_thumb[0], cached_thumb)
	cache_file_jpg = os.path.join('special://profile/Thumbnails/', cached_thumb[0], cached_thumb[:-4] + '.jpg').replace('\\', '/')
	cache_file_png = cache_file_jpg[:-4] + '.png'
	if xbmcvfs.exists(cache_file_jpg):
		log('cache_file_jpg Image: %s --> %s' % (url, cache_file_jpg))
		return translate_path(cache_file_jpg)
	elif xbmcvfs.exists(cache_file_png):
		log('cache_file_png Image: %s --> %s' % (url, cache_file_png))
		return cache_file_png
	elif xbmcvfs.exists(vid_cache_file):
		log('vid_cache_file Image: %s --> %s' % (url, vid_cache_file))
		return vid_cache_file
	try:
		r = requests.get(clean_url, stream=True)
		if r.status_code != 200:
			return ''
		data = r.content
		log('image downloaded: %s' % clean_url)
	except Exception as e:
		log('image download failed: %s' % clean_url)
		return ''
	if not data:
		return ''
	image = cache_file_png if url.endswith('.png') else cache_file_jpg
	try:
		with open(translate_path(image), 'wb') as f:
			f.write(data)
		return translate_path(image)
	except Exception as e:
		log('failed to save image %s' % url)
		return ''

def log(txt):
	if isinstance(txt, str):
		message = ''+str(addon_ID())+':  %s' % txt

def get_browse_dialog(default='', heading='Browse', dlg_type=3, shares='files', mask='', use_thumbs=False, treat_as_folder=False):
	value = xbmcgui.Dialog().browse(dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default)
	return value

def save_to_file(content, filename, path=''):
	if path == '':
		text_file_path = '%s%s.txt' % (get_browse_dialog(), filename)
	else:
		if not xbmcvfs.exists(path):
			xbmcvfs.mkdirs(path)
		text_file_path = os.path.join(path, '%s.txt' % filename)
	now = time.time()
	text_file = xbmcvfs.File(text_file_path, 'w')
	json.dump(content, text_file)
	text_file.close()
	log('saved textfile %s. Time: %f' % (text_file_path, time.time() - now))
	return True

def read_from_file(path='', raw=False):
	if path == '':
		path = get_browse_dialog(dlg_type=1)
	if not xbmcvfs.exists(path):
		return False
	try:
		with open(path) as f:
			log('opened textfile  %s' % path)
			if not raw:
				result = json.load(f)
			else:
				result = f.read()
		return result
	except:
		log('failed to load textfile: %s' % path)
		return False

def notify(header='', message='', icon=None, time=5000, sound=True):
	icon = xbmcaddon.Addon().getAddonInfo('icon')
	if not xbmc.Player().isPlaying():
		xbmcgui.Dialog().notification(heading=header, message=message, icon=icon, time=time, sound=sound)

def get_kodi_json(method, params):
	json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "%s", "params": %s, "id": 1}' % (method, params))
	json_query = str(json_query).encode('utf-8')
	return json.loads(json_query)

def pass_dict_to_skin(data=None, prefix='', debug=False, precache=False, window_id=10000):
	if not data:
		return None
	threads = []
	image_requests = []
	
	for (key, value) in data.items():
		if not value:
			continue
		value = str(value)
		if precache:
			if value.startswith('http') and (value.endswith('.jpg') or value.endswith('.png')):
				if value not in image_requests and value:
					thread = GetFileThread(value)
					threads += [thread]
					thread.start()
					image_requests.append(value)
		xbmcgui.Window(window_id).setProperty('%s%s' % (prefix, str(key)), value)
		if debug:
			log('%s%s' % (prefix, str(key)) + value)
	for x in threads:
		x.join()

def merge_dict_lists(items, key='job'):
	crew_id_list = []
	crew_list = []
	for item in items:
		if item['id'] not in crew_id_list:
			crew_id_list.append(item['id'])
			crew_list.append(item)
		else:
			index = crew_id_list.index(item['id'])
			if key in crew_list[index]:
				crew_list[index][key] = '%s / %s' % (crew_list[index][key], item[key])
	return crew_list

def pass_list_to_skin(name='', data=[], prefix='', handle=None, limit=False):
	if data and limit and int(limit) < len(data) and limit not in ("0", 0):
		data = data[:int(limit)]
	if not handle:
		set_window_props(name, data, prefix)
		return None
	xbmcgui.Window(10000).clearProperty(name)
	if data:
		xbmcgui.Window(10000).setProperty('%s.Count' % name, str(len(data)))
		items = create_listitems(data)
		itemlist = [(item.getProperty('path'), item, bool(item.getProperty('directory'))) for item in items]
		xbmcplugin.addDirectoryItems(handle=handle, items=itemlist, totalItems=len(itemlist))
	xbmcplugin.endOfDirectory(handle)

def set_window_props(name, data, prefix='', debug=False):
	if not data:
		xbmcgui.Window(10000).setProperty('%s%s.Count' % (prefix, name), '0')
		log('%s%s.Count = None' % (prefix, name))
		return None
	for (count, result) in enumerate(data):
		if debug:
			log('%s%s.%i = %s' % (prefix, name, count + 1, str(result)))
		for (key, value) in result.items():
			value = str(value)
			xbmcgui.Window(10000).setProperty('%s%s.%i.%s' % (prefix, name, count + 1, str(key)), value)
			if key.lower() in ['poster', 'banner', 'fanart', 'clearart', 'clearlogo', 'landscape', 'discart', 'characterart', 'tvshow.fanart', 'tvshow.poster', 'tvshow.banner', 'tvshow.clearart', 'tvshow.characterart']:
				xbmcgui.Window(10000).setProperty('%s%s.%i.Art(%s)' % (prefix, name, count + 1, str(key)), value)
			if debug:
				log('%s%s.%i.%s --> ' % (prefix, name, count + 1, str(key)) + value)
	xbmcgui.Window(10000).setProperty('%s%s.Count' % (prefix, name), str(len(data)))

def create_listitems(data=None, preload_images=0, enable_clearlogo=True, info=None):
	from resources.lib.TheMovieDB import extended_season_info
	from pathlib import Path
	#tools_log('create_listitems',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

	addon = xbmcaddon.Addon()
	addon_path = addon.getAddonInfo('path')
	addonID = addon.getAddonInfo('id')
	addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
	#fanart_api = fanart_api_key()
	#tools_log(str(enable_clearlogo))
	#tools_log(str('create_listitems'))
	INT_INFOLABELS = ['year', 'episode', 'season', 'tracknumber', 'playcount', 'overlay', 'percentplayed']
	FLOAT_INFOLABELS = ['rating']
	#STRING_INFOLABELS = ['mediatype', 'genre', 'director', 'mpaa', 'plot', 'plotoutline', 'title', 'originaltitle', 'sorttitle', 'duration', 'studio', 'tagline', 'writer', 'tvshowtitle', 'premiered', 'status', 'code', 'aired', 'credits', 'lastplayed', 'album', 'votes', 'trailer', 'dateadded', 'IMDBNumber']
	STRING_INFOLABELS = ['mediatype', 'genre', 'director', 'mpaa', 'plot', 'plotoutline', 'title', 'originaltitle', 'sorttitle', 'duration', 'studio', 'tagline', 'writer', 'tvshowtitle', 'premiered', 'status', 'code', 'aired', 'credits', 'lastplayed', 'album', 'votes', 'trailer', 'dateadded']
	if not data:
		return []
	itemlist = []
	threads = []
	image_requests = []

	try: show_id = info['tmdb_id']
	except: show_id = 0
	trakt_watched_stats = xbmcaddon.Addon(addon_ID()).getSetting('trakt_watched_stats')
	if trakt_watched_stats == 'true':
		import sqlite3, ast
		movie_con = sqlite3.connect(str(Path(addonUserDataFolder + '/trakt_movies_watched.db')))
		tv_con = sqlite3.connect(str(Path(addonUserDataFolder + '/trakt_tv_watched.db')))
		movie_cur = movie_con.cursor()
		tv_cur = tv_con.cursor()
		trakt_tv = True
		trakt_movies = True
	else:
		trakt_tv = False
		trakt_movies = False

	for (count, result) in enumerate(data):
		listitem = xbmcgui.ListItem('%s' % str(count))
		#listitem = xbmcgui.ListItem('%s' % str(count), offscreen=True)
		listitem.setProperty("dateadded", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		listitem.setProperty("nocache", "true")

		try: tmdb_id = result['id']
		except: tmdb_id = 0
		try: media_type = result['media_type']
		except: media_type = 0
		try: mediatype = result['mediatype']
		except: mediatype = 0
		

		#if enable_clearlogo and not 'info=library' in str(sys.argv) and not 'script=False' in str(sys.argv):
		if enable_clearlogo:
			if media_type == 'tv' and tmdb_id != 0:
				from resources.lib.TheMovieDB import get_tvshow_ids
				imdb_id = fetch(get_tvshow_ids(tmdb_id), 'imdb_id')
				result['IMDBNumber'] = imdb_id


			elif media_type == 'movie' and tmdb_id != 0:
				from resources.lib.TheMovieDB import get_imdb_id_from_movie_id
				imdb_id = get_imdb_id_from_movie_id(tmdb_id)
				result['IMDBNumber'] = imdb_id

		if mediatype == 'movie':
			listitem.setProperty("tmdb_id", str(result['id']))
		elif mediatype == 'tvshow':
			listitem.setProperty("tmdb_id", str(result['id']))
		elif mediatype == 'episode':
			#tools_log(str(result))
			listitem.setProperty("tmdb_id", str(show_id))

		if mediatype == 'movie' and tmdb_id != 0 and trakt_movies:
			try: 
				sql_result = movie_cur.execute("select * from trakt where tmdb_id =" + str(result['id'])).fetchall()
				trakt_item = ast.literal_eval(sql_result[0][1].replace('\'\'','"'))
				playcount = trakt_item['plays']
				trakt_tmdb_id = trakt_item['movie']['ids']['tmdb']
				last_watched = trakt_item['last_watched_at'].split('T')[0]
				result['playcount'] = int(playcount)
				result['lastplayed'] = str(last_watched)
			except:
				pass
		if mediatype == 'tvshow' and tmdb_id != 0 and trakt_tv:
			try:
			#if 1==1:
				sql_result = tv_cur.execute("select * from trakt where tmdb_id =" + str(result['id'])).fetchall()
				#try: trakt_item = ast.literal_eval(sql_result[0][1].replace('\'\'','"'))
				#except: trakt_item = ast.literal_eval(sql_result[0][1])
				#try: trakt_item = eval(sql_result[0][1])
				#except: trakt_item = eval(sql_result[0][1].replace("'overview': ''",'\'overview\': "').replace("'', 'first_aired':",'", \'first_aired\':').replace("'title': ''",'\'title\': "').replace("'', 'year':",'", \'year\':').replace('\'\'','"').replace(': ", ',': "", '))
				try:
					try: 
						trakt_item = eval(sql_result[0][1])
					except: 
						try: 
							trakt_item = eval(sql_result[0][1].replace('“','').replace('”','').replace("': ''",'\': "').replace("'', '",'", \'').replace(": ',",": '',").replace("'overview': ''",'\'overview\': "').replace("'', 'first_aired':",'", \'first_aired\':').replace("'title': ''",'\'title\': "').replace("'', 'year':",'", \'year\':'))
						except: 
							trakt_item = eval(sql_result[0][1].replace(" '',",' "",').replace("': ''", '\': "').replace("'', '",'", \''))
				except:
					item = sql_result[0][1].replace("'",'"')
					item = re.sub(r'(?<="")([^"]*?)"([^"]*?)(""|$)', r'\1\2\3', item)
					item = item.replace('""','"').replace('"',"'")
					trakt_item = eval(item)
				aired_episodes = trakt_item['show']['aired_episodes']
				trakt_tmdb_id = trakt_item['show']['ids']['tmdb']
				last_watched = trakt_item['last_watched_at'].split('T')[0]
				
				x = 0
				for j in trakt_item['seasons']:
					for k in j['episodes']:
						if int(k['plays']) >= 1:
							x = x + 1
				played_episodes = x
				unwatched_episodes = int(aired_episodes) - int(played_episodes)
				if int(aired_episodes) <= int(played_episodes):
					playcount = 1
					result['lastplayed'] = str(last_watched)
					result['playcount'] = int(playcount)
				listitem.setProperty('UnWatchedEpisodes', str(unwatched_episodes))
				listitem.setProperty('WatchedEpisodes', str(played_episodes))
				listitem.setProperty('TotalEpisodes', str(aired_episodes))
			except:
				pass

		if mediatype == 'season' and trakt_tv:
			try:
				sql_result = tv_cur.execute("select * from trakt where tmdb_id =" + str(int(show_id))).fetchall()
				#trakt_item = ast.literal_eval(sql_result[0][1].replace('\'\'','"'))
				#try: trakt_item = eval(sql_result[0][1])
				#except: trakt_item = eval(sql_result[0][1].replace("'overview': ''",'\'overview\': "').replace("'', 'first_aired':",'", \'first_aired\':').replace("'title': ''",'\'title\': "').replace("'', 'year':",'", \'year\':'))

				try: 
					trakt_item = eval(sql_result[0][1])
				except: 
					try: trakt_item = eval(sql_result[0][1].replace('“','').replace('”','').replace("': ''",'\': "').replace("'', '",'", \'').replace(": ',",": '',").replace("'overview': ''",'\'overview\': "').replace("'', 'first_aired':",'", \'first_aired\':').replace("'title': ''",'\'title\': "').replace("'', 'year':",'", \'year\':'))
					except: trakt_item = eval(sql_result[0][1].replace(" '',",' "",').replace("': ''", '\': "').replace("'', '",'", \''))

				if int(result['season']) > 0:
					data = extended_season_info(tvshow_id=int(show_id), season_number=int(result['season']))
					ep_count2 = 0
					played_count = 0
					ep_count = 0
					for eps in data[1]['episodes']:
						try: dattime_test = time.mktime(time.strptime(eps['release_date'], "%Y-%m-%d"))
						except: continue
						if dattime_test <= time.time():
							ep_count2 = ep_count2 + 1

				for j in trakt_item['seasons']:
					if int(result['season']) == j['number']:
						played_count = 0
						ep_count = 0
						for k in j['episodes']:
							if int(k['plays']) >= 1:
								played_count = played_count + 1
							last_watched = k['last_watched_at'].split('T')[0]
							ep_count = ep_count + 1
				result['lastplayed'] = str(last_watched)
				if ep_count2 > ep_count:
					ep_count = ep_count2
				if int(ep_count) == int(played_count):
					result['playcount'] = 1
				unwatched_episodes = ep_count - played_count
				listitem.setProperty('UnWatchedEpisodes', str(unwatched_episodes))
				listitem.setProperty('WatchedEpisodes', str(played_count))
				listitem.setProperty('TotalEpisodes', str(ep_count))
			except:
				pass

		if mediatype == 'episode' and trakt_tv:
			try:
				if show_id == 0 or (show_id != result.get('tmdb_id',0) and result.get('tmdb_id',0) != 0):
					show_id = result['tmdb_id']
				sql_result = tv_cur.execute("select * from trakt where tmdb_id =" + str(int(show_id))).fetchall()
				#trakt_item = ast.literal_eval(sql_result[0][1].replace('\'\'','"'))
				try: 
					trakt_item = eval(sql_result[0][1])
				except: 
					try: trakt_item = eval(sql_result[0][1].replace('“','').replace('”','').replace("': ''",'\': "').replace("'', '",'", \'').replace(": ',",": '',").replace("'overview': ''",'\'overview\': "').replace("'', 'first_aired':",'", \'first_aired\':').replace("'title': ''",'\'title\': "').replace("'', 'year':",'", \'year\':'))
					except: trakt_item = eval(sql_result[0][1].replace(" '',",' "",').replace("': ''", '\': "').replace("'', '",'", \''))

				for j in trakt_item['seasons']:
					if int(result['season']) == int(j['number']):
						for k in j['episodes']:
							if int(result['episode']) == int(k['number']):
								result['playcount'] = k['plays']
								result['lastplayed'] = str(k['last_watched_at'].split('T')[0])
			except:
				pass

		if enable_clearlogo and not 'logo\':' in str(result.items()) and tmdb_id != 0 and (media_type != 0 and (media_type == 'tv' or media_type == 'movie')):
			from resources.lib.TheMovieDB import get_fanart_clearlogo
			try: clearlogo = get_fanart_clearlogo(tmdb_id=tmdb_id,media_type=media_type)
			except: clearlogo = ''
			result['clearlogo'] = clearlogo
			result['logo'] = clearlogo

		#tools_log(result)
		try:
			try: 
				#listitem.setUniqueIDs({ 'imdb': result['imdb_id'], 'tmdb' : result['id'] }, "imdb")
				vinfo = listitem.getVideoInfoTag()
				vinfo.setUniqueID( result['imdb_id'], type='imdb',  isdefault=False)
				vinfo.setIMDBNumber( result['imdb_id'])
			except KeyError: 
				pass
			try: 
				vinfo = listitem.getVideoInfoTag()
				vinfo.setUniqueID( str(result['id']), type='tmdb',  isdefault=True)
			except KeyError: 
				pass
		except AttributeError:
			try:
				try: unique_ids = {"imdb": result['imdb_id'], "tmdb": str(result['id'])}
				except KeyError: unique_ids = { "tmdb": str(result['id'])}
				listitem.setUniqueIDs(unique_ids, "tmdb")
			except KeyError: 
				pass
		for (key, value) in result.items():
			if not value:
				continue
			value = str(value)
			if count < preload_images:
				if value.startswith('http://') and (value.endswith('.jpg') or value.endswith('.png')) or value.startswith('image://') and (value.endswith('.jpg/') or value.endswith('.png/')):
					if value not in image_requests:
						thread = GetFileThread(value)
						threads += [thread]
						thread.start()
						image_requests.append(value)
			if key.lower() in ['name', 'label']:
				listitem.setLabel(value)
			elif key.lower() in ['label2']:
				listitem.setLabel2(value)
			elif key.lower() in ['status']:
				#set_key = value + '(' + str(result['TotalSeasons']) + ')'
				listitem.setLabel2(value)
			elif key.lower() in ['title']:
				listitem.setLabel(value)
				#listitem.setInfo('video', {key.lower(): value})

				try: 
					info_tag = ListItemInfoTag(listitem, 'video')
					info_tag.set_info({key.lower(): value})
				except:
					listitem.setInfo('video', {key.lower(): value})

			elif key.lower() in ['thumb']:
				#listitem.setThumbnailImage(value)
				listitem.setArt({key.lower(): value})
				#if mediatype == 'episode':
				#	listitem.setProperty('Fanart_small', value)
			elif key.lower() in ['icon']:
				listitem.setIconImage(value)
				listitem.setArt({key.lower(): value})
				if mediatype == 'episode':
					listitem.setArt({'thumb': value})
			elif key.lower() in ['clearlogo','logo']:
				listitem.setArt({'clearlogo': value})

			#elif key.lower() in ['imdbnumber','IMDBNumber']:
			#	#listitem.setInfo('video', {'IMDBNumber': str(value)})
			#	try: 
			#		info_tag = ListItemInfoTag(listitem, 'video')
			#		info_tag.set_info({'IMDBNumber': str(value)})
			#	except: 
			#		listitem.setInfo('video', {'IMDBNumber': str(value)})
			elif key.lower() in ['dbid']:
				#listitem.setProperty('DBID', str(value))
				#listitem.setInfo('video', {'DBID': str(value)})
				#info_tag = ListItemInfoTag(listitem, 'video')
				#info_tag.set_info({'DBID': str(value)})
				
				try:
					vinfo = listitem.getVideoInfoTag()
					vinfo.setDbId(int(value))
				except:
					try: 
						info_tag = ListItemInfoTag(listitem, 'video')
						info_tag.set_info({'DBID': str(value)})
					except:
						listitem.setInfo('video', {'DBID': str(value)})

			elif key.lower() in ['path']:
				listitem.setPath(path=value)
			elif key.lower() in ['poster', 'banner', 'fanart', 'clearart', 'clearlogo', 'landscape', 'discart', 'characterart', 'tvshow.fanart', 'tvshow.poster', 'tvshow.banner', 'tvshow.clearart', 'tvshow.characterart']:
				listitem.setArt({key.lower(): value})
				if mediatype == 'episode':
					listitem.setProperty('Fanart_small', value)
			elif key.lower() in INT_INFOLABELS:
				try:
					
					if key.lower() == 'percentplayed':
						listitem.setProperty('StartPercent', str(value))
					else:
						#listitem.setInfo('video', {key.lower(): int(value)})
						try: 
						#	info_tag = ListItemInfoTag(listitem, 'video')
							info_tag.set_info({key.lower(): int(value)})
						except: 
							listitem.setInfo('video', {key.lower(): int(value)})
				except:
					pass
			elif key.lower() in STRING_INFOLABELS:
				#listitem.setInfo('video', {key.lower(): value})
				try: 
					info_tag = ListItemInfoTag(listitem, 'video')
					if key.lower() in ['genre', 'director', 'studio','writer']:
						info_tag.set_info({key.lower(): value.split(' / ')})
					else:
						try:
							info_tag.set_info({key.lower(): value})
						except:
							if key.lower() == 'duration':
								try: pt = time.strptime(str(value).lower(),'%Hh%Mm%Ss')
								except: 
									try: pt = time.strptime(str(value).lower(),'%Mm%Ss')
									except: 
										try: pt = time.strptime(str(value).lower(),'%Ss')
										except: 
											try: pt = time.strptime(str(value).lower(),'%Mm')
											except: 
												try: pt = time.strptime(str(value).lower(),'%Hh')
												except: 
													try: pt = time.strptime(str(value).lower(),'%Hh%Mm')
													except: pt = time.strptime(str(value).lower(),'%Hh%Ss')
								total_seconds = pt.tm_sec + pt.tm_min*60 + pt.tm_hour*3600
								info_tag.set_info({key.lower(): total_seconds})
							else:
								#info_tag.set_info({key.lower(): value})
								tools_log(str(key.lower()),'===>EXCEPTION!!')
								tools_log(str(value),'===>EXCEPTION!!')
				except:
					listitem.setInfo('video', {key.lower(): value})
			elif key.lower() in FLOAT_INFOLABELS:
				try:
					#listitem.setInfo('video', {key.lower(): '%1.1f' % float(value)})
					try: 
						info_tag = ListItemInfoTag(listitem, 'video')
						info_tag.set_info({key.lower(): '%1.1f' % float(value)})
					except:
						listitem.setInfo('video', {key.lower(): '%1.1f' % float(value)})
				except:
					pass
			listitem.setProperty('%s' % key, value)
		listitem.setProperty('index', str(count))
		itemlist.append(listitem)
	for x in threads:
		x.join()
	if trakt_tv:
		tv_cur.close()
		tv_con.close()
	if trakt_movies:
		movie_cur.close()
		movie_con.close()
	return itemlist

def clean_text(text):
	if not text:
		return ''
	text = re.sub('(From Wikipedia, the free encyclopedia)|(Description above from the Wikipedia.*?Wikipedia)', '', text)
	text = re.sub('<(.|\n|\r)*?>', '', text)
	text = text.replace('<br \/>', '\n')
	text = text.replace('<em>', '[I]').replace('</em>', '[/I]')
	text = text.replace('&amp;', '&')
	text = text.replace('&gt;', '>').replace('&lt;', '<')
	text = text.replace('&#39;', "'").replace('&quot;', '"')
	text = re.sub('\n\\.$', '', text)
	text = text.replace('User-contributed text is available under the Creative Commons By-SA License and may also be available under the GNU FDL.', '')
	while text:
		s = text[0]
		e = text[-1]
		if s in ['\u200b', ' ', '\n']:
			text = text[1:]
		elif e in ['\u200b', ' ', '\n']:
			text = text[:-1]
		elif s.startswith('.') and not s.startswith('..'):
			text = text[1:]
		else:
			break
	return text.strip()
