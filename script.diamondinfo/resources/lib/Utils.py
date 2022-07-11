import os, re, time, json, urllib.request, urllib.parse, urllib.error, hashlib, datetime, requests, threading, sys
import xbmc, xbmcgui, xbmcvfs, xbmcaddon, xbmcplugin
from functools import wraps
from resources.lib.library import addon_ID
from resources.lib.library import basedir_tv_path
from resources.lib.library import basedir_movies_path
#from resources.lib.library import fanart_api_key


ADDON_PATH = xbmcvfs.translatePath('special://home/addons/'+str(addon_ID()))
ADDON_DATA_PATH = xbmcvfs.translatePath('special://profile/addon_data/'+str(addon_ID()))
IMAGES_DATA_PATH = xbmcvfs.translatePath('special://profile/addon_data/'+str(addon_ID())+'/images')
SKIN_DIR = xbmc.getSkinDir()
AUTOPLAY_TRAILER = xbmcaddon.Addon().getSetting('autoplay_trailer')
NETFLIX_VIEW = xbmcaddon.Addon().getSetting('netflix_view')
NETFLIX_VIEW2 = xbmcaddon.Addon().getSetting('netflix_info_view')
DIAMONDPLAYER_TV_FOLDER = basedir_tv_path()
DIAMONDPLAYER_MOVIE_FOLDER = basedir_movies_path()
window_stack_enable = xbmcaddon.Addon().getSetting('window_stack_enable')
trakt_kodi_mode = xbmcaddon.Addon().getSetting('trakt_kodi_mode')
imdb_recommendations = xbmcaddon.Addon().getSetting('imdb_recommendations')

def show_busy():
	#window_id = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
	#window_id = json.loads(window_id)
	#if not window_id['result']['currentwindow']['id'] == 10025 and not window_id['result']['currentwindow']['id'] > 13000:
	if 'widget=true' in str(sys.argv) or 'autocomplete' in str(sys.argv):
		return
	if xbmc.Player().isPlaying():
		return
	if int(xbmc.getInfoLabel('System.BuildVersion')[:2]) > 17:
		xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
	else:
		xbmc.executebuiltin('ActivateWindow(busydialog)')

def hide_busy():
	if int(xbmc.getInfoLabel('System.BuildVersion')[:2]) > 17:
		xbmc.sleep(250)
		xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
		xbmc.executebuiltin('Dialog.Close(busydialog)')
	else:
		xbmc.sleep(250)
		xbmc.executebuiltin('Dialog.Close(busydialog)')

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

def after_add(type=False):
	basepath = os.path.join(ADDON_DATA_PATH, 'TheMovieDB')
	path1 = os.path.join(basepath, '0ec735169a3d0b98719c987580e419e5.txt')
	path2 = os.path.join(basepath, 'c36fcc8e9da1fe1a16fded10581fcc15.txt')
	if os.path.exists(path1):
		os.remove(path1)
	if os.path.exists(path2):
		os.remove(path2)
	empty_list = []
	if not type or type == 'movie':
		xbmcgui.Window(10000).setProperty('id_list.JSON', json.dumps(empty_list))
		xbmcgui.Window(10000).setProperty('title_list.JSON', json.dumps(empty_list))
	if not type or type == 'tv':
		xbmcgui.Window(10000).setProperty('tvshow_id_list.JSON', json.dumps(empty_list))
		xbmcgui.Window(10000).setProperty('tvshow_title_list.JSON', json.dumps(empty_list))
	force = True

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
		date = datetime.date.today()
		ref_day = [date.year, date.month, date.day]
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
	cache_path = translate_path(ADDON_DATA_PATH, folder) if folder else translate_path(ADDON_DATA_PATH)
	cache_seconds = int(cache_days * 86400.0)
	if not cache_days:
		xbmcgui.Window(10000).clearProperty(hashed_url)
		xbmcgui.Window(10000).clearProperty('%s_timestamp' % hashed_url)
	prop_time = xbmcgui.Window(10000).getProperty('%s_timestamp' % hashed_url)
	if prop_time and now - float(prop_time) < cache_seconds:
		try:
			prop = json.loads(xbmcgui.Window(10000).getProperty(hashed_url))
			if prop:
				return prop
		except Exception as e:
			pass
	path = os.path.join(cache_path, '%s.txt' % hashed_url)
	if xbmcvfs.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
		results = read_from_file(path)
	else:
		response = get_http(url, headers)
		try:
			results = json.loads(response)
			save_to_file(results, hashed_url, cache_path)
		except:
			log('Exception: Could not get new JSON data from %s. Tryin to fallback to cache' % url)
			log(response)
			results = read_from_file(path) if xbmcvfs.exists(path) else []
	if not results:
		return None
	xbmcgui.Window(10000).setProperty('%s_timestamp' % hashed_url, str(now))
	xbmcgui.Window(10000).setProperty(hashed_url, json.dumps(results))
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

def notify(header='', message='', icon=xbmcaddon.Addon().getAddonInfo('icon'), time=5000, sound=True):
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
	addon = xbmcaddon.Addon()
	addon_path = addon.getAddonInfo('path')
	addonID = addon.getAddonInfo('id')
	addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
	#fanart_api = fanart_api_key()
	#xbmc.log(str(enable_clearlogo)+'===>PHIL', level=xbmc.LOGINFO)
	#xbmc.log(str('create_listitems')+'===>PHIL', level=xbmc.LOGINFO)
	INT_INFOLABELS = ['year', 'episode', 'season', 'tracknumber', 'playcount', 'overlay']
	FLOAT_INFOLABELS = ['rating']
	STRING_INFOLABELS = ['mediatype', 'genre', 'director', 'mpaa', 'plot', 'plotoutline', 'title', 'originaltitle', 'sorttitle', 'duration', 'studio', 'tagline', 'writer', 'tvshowtitle', 'premiered', 'status', 'code', 'aired', 'credits', 'lastplayed', 'album', 'votes', 'trailer', 'dateadded', 'IMDBNumber']
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
				sql_result = tv_cur.execute("select * from trakt where tmdb_id =" + str(result['id'])).fetchall()
				try: trakt_item = ast.literal_eval(sql_result[0][1].replace('\'\'','"'))
				except: trakt_item = ast.literal_eval(sql_result[0][1])
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
				trakt_item = ast.literal_eval(sql_result[0][1].replace('\'\'','"'))

				from datetime import datetime
				if int(result['season']) > 0:
					data = extended_season_info(tvshow_id=int(show_id), season_number=int(result['season']))
					ep_count2 = 0
					played_count = 0
					ep_count = 0
					for eps in data[1]['episodes']:
						try: datetime_object = datetime.strptime(eps['release_date'], '%Y-%m-%d')
						except: continue
						if datetime_object <= datetime.now():
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
				sql_result = tv_cur.execute("select * from trakt where tmdb_id =" + str(int(show_id))).fetchall()
				trakt_item = ast.literal_eval(sql_result[0][1].replace('\'\'','"'))
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
			elif key.lower() in ['title']:
				listitem.setLabel(value)
				listitem.setInfo('video', {key.lower(): value})
			elif key.lower() in ['thumb']:
				#listitem.setThumbnailImage(value)
				listitem.setArt({key.lower(): value})
			elif key.lower() in ['icon']:
				listitem.setIconImage(value)
				listitem.setArt({key.lower(): value})
			elif key.lower() in ['clearlogo','logo']:
				listitem.setArt({'clearlogo': value})

			elif key.lower() in ['imdbnumber','IMDBNumber']:
				listitem.setInfo('video', {'IMDBNumber': str(value)})
			elif key.lower() in ['dbid']:
				listitem.setProperty('DBID', str(value))
				listitem.setInfo('video', {'DBID': str(value)})

			elif key.lower() in ['path']:
				listitem.setPath(path=value)
			elif key.lower() in ['poster', 'banner', 'fanart', 'clearart', 'clearlogo', 'landscape', 'discart', 'characterart', 'tvshow.fanart', 'tvshow.poster', 'tvshow.banner', 'tvshow.clearart', 'tvshow.characterart']:
				listitem.setArt({key.lower(): value})
			elif key.lower() in INT_INFOLABELS:
				try:
					listitem.setInfo('video', {key.lower(): int(value)})
				except:
					pass
			elif key.lower() in STRING_INFOLABELS:
				listitem.setInfo('video', {key.lower(): value})
			elif key.lower() in FLOAT_INFOLABELS:
				try:
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
