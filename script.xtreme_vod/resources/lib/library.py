import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import os
import shutil

import datetime
from datetime import date, datetime, timedelta
import time
from pathlib import Path

from inspect import currentframe, getframeinfo
#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)

def addon_ID():
	addonID = xbmcaddon.Addon().getAddonInfo('id')
	return addonID

def addon_ID_short():
	addonID = xbmcaddon.Addon().getAddonInfo('id')
	addonID_short = addonID.replace('script.','')
	return addonID_short

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

def get_processor_info():
	import platform, subprocess
	if platform.system() == "Windows":
		return platform.processor()
	elif platform.system() == "Darwin":
		return subprocess.check_output(['/usr/sbin/sysctl', "-n", "machdep.cpu.brand_string"]).strip()
	elif platform.system() == "Linux":
		command = "cat /proc/cpuinfo"
		return subprocess.check_output(command, shell=True).strip()
	return ""

def tmdb_traktapi_path():
	tmdb_traktapi_path1 = Path(main_file_path().replace(addon_ID(),'plugin.video.themoviedb.helper') + 'resources/lib/traktapi.py')
	tmdb_traktapi_path2 = Path(main_file_path().replace(addon_ID(),'plugin.video.themoviedb.helper') + 'resources/lib/trakt/api.py')
	tmdb_traktapi_path3 = Path(main_file_path().replace(addon_ID(),'plugin.video.themoviedb.helper') + 'resources/lib/api/trakt/api.py')
	tmdb_traktapi_path4 = Path(main_file_path().replace(addon_ID(),'plugin.video.themoviedb.helper') + 'resources/tmdbhelper/lib/api/api_keys/trakt.py')
	if xbmcvfs.exists(str(tmdb_traktapi_path1)):
		return tmdb_traktapi_path1
	elif xbmcvfs.exists(str(tmdb_traktapi_path2)):
		return tmdb_traktapi_path2
	elif xbmcvfs.exists(str(tmdb_traktapi_path3)):
		return tmdb_traktapi_path3
	elif xbmcvfs.exists(str(tmdb_traktapi_path4)):
		return tmdb_traktapi_path4


def basedir_tv_path():
	root_dir = xbmcaddon.Addon(addon_ID()).getSetting('library_folder')
	if root_dir == '':
		addon = xbmcaddon.Addon()
		addon_path = addon.getAddonInfo('path')
		addonID = addon.getAddonInfo('id')
		addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
		return Path(addonUserDataFolder + '/TVShows')
	else:
		if root_dir[-1] != '/' and '/' in str(root_dir):
			root_dir += '/'
		return Path(root_dir + 'TVShows')

def basedir_movies_path():
	root_dir = xbmcaddon.Addon(addon_ID()).getSetting('library_folder')
	if root_dir == '':
		addon = xbmcaddon.Addon()
		addon_path = addon.getAddonInfo('path')
		addonID = addon.getAddonInfo('id')
		addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
		return Path(addonUserDataFolder + '/Movies')
	else:
		if root_dir[-1] != '/' and '/' in str(root_dir):
			root_dir += '/'
		return Path(root_dir + 'Movies')

def library_source_exists_tv():
	xml_file = xbmcvfs.translatePath('special://profile/sources.xml')
	blank_sources_xml = xbmcvfs.translatePath(str(main_file_path()+'/blank_sources_xml'))
	if xbmcvfs.exists(str(xml_file)) == False:
		shutil.copyfile(blank_sources_xml, xml_file)
	root_dir = str(basedir_tv_path())
	f = open(xml_file, "r")
	string_f = str(f.read())
	test_var = root_dir in string_f
	f.close() 
	return test_var

def library_source_exists_movies():
	xml_file = xbmcvfs.translatePath('special://profile/sources.xml')
	blank_sources_xml = xbmcvfs.translatePath(str(main_file_path()+'/blank_sources_xml'))
	if xbmcvfs.exists(str(xml_file)) == False:
		shutil.copyfile(blank_sources_xml, xml_file)
	root_dir = str(basedir_movies_path())
	f = open(xml_file, "r")
	string_f = str(f.read())
	test_var = root_dir in string_f
	f.close() 
	return test_var

def get_file(url=None,file_path=None):
	import requests
	try:
		r = requests.get(url)
		with open(file_path, 'wb') as outfile:
			outfile.write(r.content)
	except:
		pass

def db_path():
	import glob
	db_name = 'MyVideos*.db'
	path_db = 'special://profile/Database/%s' % db_name
	filelist = sorted(glob.glob(xbmcvfs.translatePath(path_db)))
	if filelist:
		return filelist[-1]

def db_connection():
	import sqlite3
	con = sqlite3.connect(db_path())
	return con

def icon_path():
	icon_path = Path(main_file_path() + 'icon2.png')
	return str(icon_path)

def tmdb_api_key():
	#return xbmcaddon.Addon('plugin.video.seren').getSetting('tmdb.apikey')#
	tmdb_API_key = xbmcaddon.Addon(addon_ID()).getSetting('tmdb_api')
	if len(tmdb_API_key) != 32:
		tmdb_API_key = 'edde6b5e41246ab79a2697cd125e1781'
	return tmdb_API_key

def fanart_api_key():
	fanart_api_key = xbmcaddon.Addon(addon_ID()).getSetting('fanart_api')
	if str(fanart_api_key) == '':
		fanart_api_key = xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('fanarttv_clientkey')
	if len(fanart_api_key) != 32:
		fanart_api_key = '184e1a2b1fe3b94935365411f919f638'
	return fanart_api_key

def show_settings_menu():
	if xbmcaddon.Addon(addon_ID()).getSetting('settings_user_config') == 'Settings Selection Menu':
		return True
	if xbmcaddon.Addon(addon_ID()).getSetting('settings_user_config') == 'TMDBHelper Context Menu':
		return False



#OPENMETA METHOD => AddSource.py
def setup_library_tv():
	from resources.lib import AddSource
	
	library_root_folder = str(xbmcaddon.Addon(addon_ID()).getSetting('library_folder'))
	if library_root_folder == '':
		addon = xbmcaddon.Addon()
		addon_path = addon.getAddonInfo('path')
		addonID = addon.getAddonInfo('id')
		addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
		library_root_folder = addonUserDataFolder
		library_root_folder = str(Path(library_root_folder))
	
	if '/' in str(library_root_folder) and str(library_root_folder)[-1] != '/':
		library_root_folder += '/'
		library_root_folder = str(library_root_folder)
	if '\\' in str(library_root_folder) and str(library_root_folder)[-1] != '\\':
		library_root_folder += '\\'
		library_root_folder = str(library_root_folder)
	
	library_folder = str(Path(basedir_tv_path()))
	if '/' in str(library_folder) and str(library_folder)[-1] != '/':
		library_folder += '/'
		library_folder = str(library_folder)
	if '\\' in str(library_folder) and str(library_folder)[-1] != '\\':
		library_folder += '\\'
		library_folder = str(library_folder)

	if not xbmcvfs.exists(library_root_folder):
		xbmcvfs.mkdir(library_root_folder)
	if not xbmcvfs.exists(library_folder):
		xbmcvfs.mkdir(library_folder)
	source_thumbnail = str(Path(icon_path()))
	source_name = 'XtremeVOD TVShows'
	source_content = """('%s','tvshows','metadata.tvshows.themoviedb.org.python',NULL,0,0,'<settings version="2"><setting id="language" default="true">en-US</setting><setting id="tmdbcertcountry" default="true">us</setting><setting id="usecertprefix" default="true">true</setting><setting id="certprefix" default="true">Rated </setting><setting id="keeporiginaltitle" default="true">false</setting><setting id="cat_landscape" default="true">true</setting><setting id="studio_country" default="true">false</setting><setting id="enab_trailer" default="true">true</setting><setting id="players_opt" default="true">Tubed</setting><setting id="ratings" default="true">TMDb</setting><setting id="imdbanyway" default="true">false</setting><setting id="traktanyway" default="true">false</setting><setting id="tmdbanyway" default="true">true</setting><setting id="enable_fanarttv" default="true">true</setting><setting id="fanarttv_clientkey" default="true" /><setting id="verboselog" default="true">false</setting><setting id="lastUpdated" default="true">0</setting><setting id="originalUrl" default="true" /><setting id="previewUrl" default="true" /></settings>',0,0,NULL,NULL)""" % library_folder

	AddSource.add_source(source_name, library_folder, source_content, source_thumbnail)
	return xbmcvfs.translatePath(library_folder)

#OPENMETA METHOD => AddSource.py
def setup_library_movies():
	from resources.lib import AddSource
	
	library_root_folder = xbmcaddon.Addon(addon_ID()).getSetting('library_folder')
	if library_root_folder == '':
		addon = xbmcaddon.Addon()
		addon_path = addon.getAddonInfo('path')
		addonID = addon.getAddonInfo('id')
		addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
		library_root_folder = addonUserDataFolder
		library_root_folder = str(Path(library_root_folder))

	if '/' in str(library_root_folder) and str(library_root_folder)[-1] != '/':
		library_root_folder += '/'
		library_root_folder = str(library_root_folder)
	if '\\' in str(library_root_folder) and str(library_root_folder)[-1] != '\\':
		library_root_folder += '\\'
		library_root_folder = str(library_root_folder)

	library_folder = str(Path(basedir_movies_path()))
	if '/' in str(library_folder) and str(library_folder)[-1] != '/':
		library_folder += '/'
		library_folder = str(library_folder)
	if '\\' in str(library_folder) and str(library_folder)[-1] != '\\':
		library_folder += '\\'
		library_folder = str(library_folder)

	if not xbmcvfs.exists(library_root_folder):
		xbmcvfs.mkdir(library_root_folder)
	if not xbmcvfs.exists(library_folder):
		xbmcvfs.mkdir(library_folder)
	source_thumbnail = str(Path(icon_path()))
	source_name = 'XtremeVOD Movies'
	source_content = """('%s','movies','metadata.themoviedb.org',NULL,2147483647,0,'<settings version="2"><setting id="keeporiginaltitle" default="true">false</setting><setting id="fanart">true</setting><setting id="landscape">true</setting><setting id="trailer">true</setting><setting id="language" default="true">en-US</setting><setting id="tmdbcertcountry" default="true">us</setting><setting id="certprefix" default="true">Rated </setting><setting id="RatingS" default="true">TMDb</setting><setting id="imdbanyway" default="true">false</setting><setting id="traktanyway" default="true">false</setting><setting id="multiple_studios" default="true">false</setting><setting id="add_tags">true</setting><setting id="lastUpdated" default="true">0</setting><setting id="originalUrl" default="true" /><setting id="previewUrl" default="true" /><setting id="enable_fanarttv_artwork">true</setting><setting id="fanarttv_language" default="true">en</setting><setting id="fanarttv_clientkey" default="true" /></settings>',0,0,NULL,NULL)""" % library_folder
	AddSource.add_source(source_name, library_folder, source_content, source_thumbnail)
	return xbmcvfs.translatePath(library_folder)

def auto_setup_xml_filenames():
	from pathlib import Path
	import os
	skin_xml = Path(str(main_file_path()) + '/resources/skins/Default/1080i/' + str(addon_ID()) + '-DialogInfo.xml')
	if not os.path.exists(skin_xml):
		setup_xml_filenames()
	else:
		return

def setup_xml_filenames():
	import fileinput

	dir_path = Path(str(main_file_path()) + '/resources/skins/Default/1080i/')
	for dirpath, dnames, fnames in os.walk(dir_path):
		for f in fnames:
			if '.xml' in f and 'script.' in f:
				old_name = f
				name1 = str(f).split('script.')[0]
				name2 = str(f).split('script.')[1].split('-')[0]
				old_addonID = 'script.' + name2
				name = ''
				for i in str(f).split('-')[1:]:
					if name == '':
						name =  i
					else:
						name = name + '-' + i
				new_name = name1 + str(addon_ID()) + '-' + name
				new_path = Path(str(dir_path) +'/'+ new_name)
				old_path = Path(str(dir_path) +'/'+ old_name)
				filename = old_path
				if 'Netflix' in str(filename):
					xbmc.log(str(old_addonID)+'= REPLACE OLD ADDONID,' + str(addon_ID()) + ' = NEW ADDONID -- DIAMONDINFO_MOD', level=xbmc.LOGINFO)
					with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
						for line in file:
							print(line.replace(old_addonID, str(addon_ID())), end='')
				if old_name != new_name and not os.path.exists(new_path):
					os.rename(old_path, new_path)
					xbmc.log(str(old_name)+'= OLD NAME,' + str(new_name) + ' = NEW NAME -- DIAMONDINFO_MOD', level=xbmc.LOGINFO)

def get_art_fanart_movie(tmdb_id, fanart_api, show_file_path, art_path,tmdb_api):
	from resources.lib.TheMovieDB import get_fanart_data
	from resources.lib.TheMovieDB import get_tmdb_data
	show_file_path = str(show_file_path)

	try: 
		response = get_fanart_data(tmdb_id=tmdb_id,media_type='movie')
	except: 
		response = ''
		

	d1 = {}
	for i in response:
	#	print(i)
		for j in response[i]:
			try: 
				lang = j['lang']
				if j['lang'] == 'en' or (i == 'movielogo' and j['lang'] == ''):
					if i == 'movielogo':
						d1['movielogo'] = j['url']
						break
				if j['lang'] == 'en' or (i == 'hdmovielogo' and j['lang'] == ''):
					if i == 'hdmovielogo':
						d1['hdmovielogo'] = j['url']
						break
				if i == 'movieposter':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['movieposter'] = k['url']
							break
				if i == 'hdmovieclearart':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['hdmovieclearart'] = k['url']
							break
				if i == 'movieart':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['movieart'] = k['url']
							break
				if i == 'moviedisc':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['moviedisc'] = k['url']
							break
				if i == 'moviebanner':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['moviebanner'] = k['url']
							break
				if i == 'moviethumb':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['moviethumb'] = k['url']
							break
				if i == 'moviebackground':
					for k in response[i]:
						if k['lang'] == 'en' or k['lang'] == '':
							d1['moviebackground'] = k['url']
							break
			except:
				pass
	#TMDB_ID - poster, fanart, season posters
	#tvposter, showbackground, seasonposters
	if not d1.__contains__('moviebackground') or not d1.__contains__('movieposter'):
		url = 'movie/'+str(tmdb_id) + '?'
		response = get_tmdb_data(url=url)

		if not d1.__contains__('moviebackground'):
			try: 
				#d1['moviebackground'] = str('https://image.tmdb.org/t/p/original') + response.json()['backdrop_path']
				d1['moviebackground'] = str('https://image.tmdb.org/t/p/w500') + response.json()['backdrop_path']
			except:
				pass

		if not d1.__contains__('movieposter'):
			try:
				#d1['movieposter'] = str('https://image.tmdb.org/t/p/original') + response.json()['poster_path']
				d1['movieposter'] = str('https://image.tmdb.org/t/p/w500') + response.json()['poster_path']
			except:
				pass

	if d1.__contains__('moviebanner'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/banner.jpg')):
			get_file(d1['moviebanner'].replace(' ', '%20'), Path(show_file_path + '/banner.jpg'))

	if d1.__contains__('hdmovielogo'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/clearlogo.png')):
			get_file(d1['hdmovielogo'].replace(' ', '%20'), Path(show_file_path + '/clearlogo.png'))
	elif d1.__contains__('movielogo'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/clearlogo.png')):
			get_file(d1['movielogo'].replace(' ', '%20'), Path(show_file_path + '/clearlogo.png'))

	if d1.__contains__('moviethumb'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/landscape.jpg')):
			get_file(d1['moviethumb'].replace(' ', '%20'), Path(show_file_path + '/landscape.jpg'))
	elif d1.__contains__('moviebackground'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/landscape.jpg')):
			get_file(d1['moviebackground'].replace(' ', '%20'), Path(show_file_path + '/landscape.jpg'))

	if d1.__contains__('moviebackground'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/fanart.jpg')):
			get_file(d1['moviebackground'].replace(' ', '%20'), Path(show_file_path + '/fanart.jpg'))
	elif d1.__contains__('moviethumb'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/fanart.jpg')):
			get_file(d1['moviethumb'].replace(' ', '%20'), Path(show_file_path + '/fanart.jpg'))

	if d1.__contains__('movieposter'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/poster.jpg')):
			get_file(d1['movieposter'].replace(' ', '%20'), Path(show_file_path + '/poster.jpg'))

def get_art_fanart_tv(tvdb_id, fanart_api, show_file_path, art_path,tmdb_id,tmdb_api):
	from resources.lib.TheMovieDB import get_fanart_data
	from resources.lib.TheMovieDB import get_tmdb_data
	d1 = {}
	show_file_path = str(show_file_path)
	try: 
		response = get_fanart_data(tmdb_id=tvdb_id,media_type='tv_tvdb')
	except: 
		response = ''

	d1 = {}
	for i in response:
		for j in response[i]:
			try: 
				lang = j['lang']
				if j['lang'] in ('en','00','')  or (i == 'showbackground' and j['lang'] == ''):
					if i == 'hdclearart' and i not in d1:
						d1['hdclearart'] = j['url']
						break
					if i == 'seasonposter' and 'seasonposters' not in d1:
						d1['seasonposters'] = {}
						for k in response[i]:
							if k['season'] != 'all':
								if k['lang'] in ('en','00','') and not d1['seasonposters'].__contains__(int(k['season'])):
									d1['seasonposters'][int(k['season'])] = k['url']
						break
					if i == 'seasonthumb' and i not in d1:
						d1['seasonthumb'] = {}
						for k in response[i]:
							if k['season'] != 'all':
								if k['lang'] in ('en','00','') and not d1['seasonthumb'].__contains__(int(k['season'])):
									d1['seasonthumb'][int(k['season'])] = k['url']
						break
					if i == 'seasonbanner' and i not in d1:
						d1['seasonbanner'] = {}
						for k in response[i]:
							if k['season'] != 'all':
								if k['lang'] in ('en','00','') and not d1['seasonbanner'].__contains__(int(k['season'])):
									d1['seasonbanner'][int(k['season'])] = k['url']
						break
					if i == 'tvthumb' and i not in d1:
						d1['tvthumb'] = j['url']
						break
					if i == 'tvbanner' and i not in d1:
						d1['tvbanner'] = j['url']
						break
					if i == 'showbackground' and i not in d1:
						d1['showbackground'] = j['url']
						break
					if i == 'clearlogo' and i not in d1:
						d1['clearlogo'] = j['url']
						break
					if i == 'characterart' and i not in d1:
						d1['characterart'] = j['url']
						break
					if i == 'tvposter' and i not in d1:
						d1['tvposter'] = j['url']
						break
					if i == 'clearart' and i not in d1:
						d1['clearart'] = j['url']
						break
					if i == 'hdtvlogo' and i not in d1:
						d1['hdtvlogo'] = j['url']
						break
			except:
				pass
				

	#TVDB_ID - poster, banner, fanart
	#tvposter, tvbanner, showbackground
	if not d1.__contains__('showbackground') or not d1.__contains__('tvposter') or not d1.__contains__('tvbanner'):
		try:
			response = requests.get('https://api.thetvdb.com/series/'+str(tvdb_id))

			if not d1.__contains__('showbackground'):
				try: 
					d1['showbackground'] = str('https://artworks.thetvdb.com/banners/') + response.json()['data']['fanart']
				except:
					pass

			if not d1.__contains__('tvposter'):
				try:
					d1['tvposter'] = str('https://artworks.thetvdb.com/banners/') + response.json()['data']['poster']
				except:
					pass
				
			if not d1.__contains__('tvbanner'):
				try:
					d1['tvbanner'] = str('https://artworks.thetvdb.com/banners/') + response.json()['data']['banner']
				except:
					pass
		except:
			pass

	#TMDB_ID - poster, fanart, season posters
	#tvposter, showbackground, seasonposters
	if not d1.__contains__('showbackground') or not d1.__contains__('tvposter') or not d1.__contains__('seasonposters'):
		url = 'tv/'+str(tmdb_id) + '?'
		response = get_tmdb_data(url=url)

		if not d1.__contains__('showbackground'):
			try: 
				d1['showbackground'] = str('https://image.tmdb.org/t/p/w500') + response.json()['backdrop_path']
				#d1['showbackground'] = str('https://image.tmdb.org/t/p/original') + response.json()['backdrop_path']
			except:
				pass

		if not d1.__contains__('tvposter'):
			try:
				d1['tvposter'] = str('https://image.tmdb.org/t/p/w500') + response.json()['poster_path']
				#d1['tvposter'] = str('https://image.tmdb.org/t/p/original') + response.json()['poster_path']
			except:
				pass
			
		if not d1.__contains__('seasonposters'):
			d1['seasonposters'] = {}
			try:
				for k in response.json()['seasons']:
					try:
						d1['seasonposters'][int(k['season_number'])] = str('https://image.tmdb.org/t/p/w500') + k['poster_path']
						#d1['seasonposters'][int(k['season_number'])] = str('https://image.tmdb.org/t/p/original') + k['poster_path']
					except:
						pass
			except:
				pass

	if d1.__contains__('tvbanner'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/banner.jpg')):
			get_file(d1['tvbanner'].replace(' ', '%20'), Path(show_file_path + '/banner.jpg'))

	if d1.__contains__('hdtvlogo'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/clearlogo.png')):
			get_file(d1['hdtvlogo'].replace(' ', '%20'), Path(show_file_path + '/clearlogo.png'))
	elif d1.__contains__('clearlogo'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/clearlogo.png')):
			get_file(d1['clearlogo'].replace(' ', '%20'), Path(show_file_path + '/clearlogo.png'))

	if d1.__contains__('tvthumb'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/landscape.jpg')):
			get_file(d1['tvthumb'].replace(' ', '%20'), Path(show_file_path + '/landscape.jpg'))
	elif d1.__contains__('showbackground'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/landscape.jpg')):
			get_file(d1['showbackground'].replace(' ', '%20'), Path(show_file_path + '/landscape.jpg'))

	if d1.__contains__('showbackground'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/fanart.jpg')):
			get_file(d1['showbackground'].replace(' ', '%20'), Path(show_file_path + '/fanart.jpg'))
	elif d1.__contains__('tvthumb'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/fanart.jpg')):
			get_file(d1['tvthumb'].replace(' ', '%20'), Path(show_file_path + '/fanart.jpg'))


	if d1.__contains__('tvposter'):
		if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/poster.jpg')):
			get_file(d1['tvposter'].replace(' ', '%20'), Path(show_file_path + '/poster.jpg'))

	if d1.__contains__('seasonbanner'):
		for i in d1['seasonbanner']:
			if i != 0:
				if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/season' + format(i, '02d') + '-banner.jpg')):
					get_file(d1['seasonbanner'][i].replace(' ', '%20'), Path(show_file_path + '/season' + format(i, '02d') + '-banner.jpg'))

	if d1.__contains__('seasonthumb'):
		for i in d1['seasonthumb']:
			if i != 0:
				if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/season' + format(i, '02d') + '-landscape.jpg')):
					get_file(d1['seasonthumb'][i].replace(' ', '%20'), Path(show_file_path + '/season' + format(i, '02d') + '-landscape.jpg'))

	if d1.__contains__('seasonposters'):
		for i in d1['seasonposters']:
			if i != 0:
				if not os.path.exists(art_path) or not os.path.exists(Path(show_file_path + '/season' + format(i, '02d') + '-poster.jpg')):
					get_file(d1['seasonposters'][i].replace(' ', '%20'), Path(show_file_path + '/season' + format(i, '02d') + '-poster.jpg'))
	return


def get_fanart_results(tvdb_id, media_type=None, show_season = None):
	from resources.lib.TheMovieDB import get_fanart_data
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
			if i == 'name' or i == 'thetvdb_id':
				continue
			for j in response[i]:
				try:
					#tools.log(j)
					if j['lang'] == 'en' or (i in ['showbackground','tvposter','tvthumb'] and j['lang'] == ''):
						if i in ('seasonposter', 'seasonthumb', 'seasonbanner'):
							for k in response[i]:
								if int(k['season']) == int(show_season) and k['lang'] == 'en':
									tv_dict[i] = k['url']
									break
					if i in ('hdclearart', 'tvthumb', 'tvbanner', 'showbackground', 'clearlogo', 'characterart', 'tvposter', 'clearart', 'hdtvlogo'):
						if i == 'clearlogo' or i == 'hdtvlogo':
							tv_dict['clearlogo'] = j['url']
							tv_dict['hdtvlogo'] = j['url']
							break
						else:
							tv_dict[i] = j['url']
							break
				except:
					continue
		#return hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo

		for i in tv_dict:
			if tv_dict[i] == None and i in ('seasonposter', 'seasonthumb', 'seasonbanner'):
				for k in response.get(i,[]):
					if str(k['season']) == 'all':
						tv_dict[i] = k['url']
						break
					if int(k['season']) == int(show_season):
						tv_dict[i] = k['url']
						break
		#tools.log(tv_dict)
		return tv_dict['hdclearart'], tv_dict['seasonposter'], tv_dict['seasonthumb'], tv_dict['seasonbanner'], tv_dict['tvthumb'], tv_dict['tvbanner'], tv_dict['showbackground'], tv_dict['clearlogo'], tv_dict['characterart'], tv_dict['tvposter'], tv_dict['clearart'], tv_dict['hdtvlogo']
	else:
		movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = '', '', '', '', '', '', '', '', ''
		movie_dict = {'movielogo': None,'hdmovielogo': None,'movieposter': None,'hdmovieclearart': None,'movieart': None,'moviedisc': None,'moviebanner': None,'moviethumb': None,'moviebackground': None}
		for i in response:
			#print_log(i)
			for j in response[i]:
				try:
					lang = j['lang']
					if j['lang'] == 'en' or (i in ['movielogo','hdmovielogo','moviebackground','moviethumb','movieposter'] and j['lang'] == ''): 
						if i in ('movielogo', 'hdmovielogo'):
							movie_dict[i] = j['url']
							break
						if i in ('movieposter','hdmovieclearart','movieart','moviedisc','moviebanner','moviethumb','moviebackground'):
							for k in response[i]:
								if k['lang'] == 'en' or (i in ['movielogo','hdmovielogo','moviebackground','moviethumb','movieposter'] and j['lang'] == ''): 
									movie_dict[i] = k['url']
									break
				except:
					pass

		#return movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground
		#tools.log(movie_dict)
		return movie_dict['movielogo'], movie_dict['hdmovielogo'], movie_dict['movieposter'], movie_dict['hdmovieclearart'], movie_dict['movieart'], movie_dict['moviedisc'], movie_dict['moviebanner'], movie_dict['moviethumb'], movie_dict['moviebackground']

def get_fanart_results_full(tvdb_id, media_type=None, show_season = None):
	#from a4kscrapers_wrapper import get_meta
	#get_fanart_results(tvdb_id, media_type=None, show_season = None)

	if 'tv_tvdb' == media_type:
		hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = '', '', '', '', '', '', '', '', '', '', '', '';
		hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo = get_fanart_results(tvdb_id, media_type='tv_tvdb', show_season = show_season)
		return hdclearart, seasonposter, seasonthumb, seasonbanner, tvthumb, tvbanner, showbackground, clearlogo, characterart, tvposter, clearart, hdtvlogo
	else:
		movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = '', '', '', '', '', '', '', '', ''
		movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground = get_fanart_results(tvdb_id, media_type='movie', show_season = None)
		return movielogo, hdmovielogo, movieposter, hdmovieclearart, movieart, moviedisc, moviebanner, moviethumb, moviebackground


def delete_folder_contents(path, delete_subfolders=False):
	"""
	Delete all files in a folder
	:param path: Path to perform delete contents
	:param delete_subfolders: If True delete also all subfolders
	"""
	directories = []
	files = []
	for path2, subdirs2, files2 in os.walk(path):
		for filename in files2:
			files.append(filename)
		for directory in subdirs2:
			directories.append(directory)
	#directories, files = list_dir(path)
	for filename in files:
		xbmcvfs.delete(os.path.join(path, filename))
	if not delete_subfolders:
		return
	for directory in directories:
		delete_folder_contents(os.path.join(path, directory), True)
		# Give time because the system performs previous op. otherwise it can't delete the folder
		xbmc.sleep(80)
		xbmcvfs.rmdir(os.path.join(path, directory)) 


def next_episode_show(tmdb_id_num=None,dbid_num=None):
	import sqlite3
	import re

	temp_dbid = dbid_num
	tmdb_id=tmdb_id_num
	regex = re.compile('[^0-9a-zA-Z]')

	con = sqlite3.connect(db_path())
	cur = con.cursor()

	temp_show_id = temp_dbid
	sql_var = (
	"""
	select * from 
	(select c00, strtitle, cast(c12 as int) as c12, cast(c13 as int) as c13, c05, strPath, strFilename,ROW_NUMBER() OVER (PARTITION BY idshow ORDER BY cast(c12 as int), cast(c13 as int)) as EN,lastplayed,playcount from episode_view 
	where idshow = {temp_show_id}) as ep_nums
	left join

	(select max(en)+1 as en from 
	(select c00, strtitle, cast(c12 as int) as c12, cast(c13 as int) as c13, c05, strPath, strFilename,ROW_NUMBER() OVER (PARTITION BY idshow ORDER BY cast(c12 as int), cast(c13 as int)) as EN,lastplayed,playcount from episode_view 
	where idshow = {temp_show_id}) as max_ep_num
	where playcount is not null and playcount <> 0
	group by strtitle) as max_ep_num
	on max_ep_num.en = ep_nums.en

	left join

	(select (en)+1 as en, lastPlayed, lastPlayed_num from 
	(select *,ROW_NUMBER() OVER (ORDER BY lastPlayed desc) as lastPlayed_num from 
	(select c00, strtitle, cast(c12 as int) as c12, cast(c13 as int) as c13, c05, strPath, strFilename,ROW_NUMBER() OVER (PARTITION BY idshow ORDER BY cast(c12 as int), cast(c13 as int)) as EN,lastplayed,playcount from episode_view 
	where idshow = {temp_show_id}) as max_lastPlayed
	) as max_lastPlayed
	where en  <> 1 and lastPlayed_num = 1 and lastPlayed is not null and lastPlayed is not 'None') as max_lastPlayed
	on max_lastPlayed.en = ep_nums.en

	where max_lastPlayed.en is not null or max_ep_num.en is not null
	--order by ep_nums.en desc
	--order by lastPlayed_num
	order by lastPlayed_num desc

	""".format(temp_show_id=temp_show_id)
	)
	sql_result = cur.execute(sql_var).fetchall()

	#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
	tmdb_id = ''
	url = ''
	nfo = ''
	try: 
		episode_title = sql_result[0][0]
		episode_title = regex.sub(' ', episode_title.replace('\'','').replace('&','and')).replace('  ',' ')
		tvshow_title = sql_result[0][1]
		tvshow_title = regex.sub(' ', tvshow_title.replace('\'','').replace('&','and')).replace('  ',' ')
		season = sql_result[0][2]
		episode = sql_result[0][3]
		nfo = sql_result[0][5].replace(sql_result[0][5].split('/')[9]+'/','')+'tvshow.nfo'
		file_path = str(sql_result[0][5]) + str(sql_result[0][6])
		#file_path = str(sql_result[0][6])
		#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
	except: 
		sql_result2 = None
		cur.execute("select c00 from tvshow where idshow = '"+str(temp_show_id)+"'")
		sql_result2 = cur.fetchall()
		tvshow_title = sql_result2[0][0]
		tvshow_title = regex.sub(' ', tvshow_title.replace('\'','').replace('&','and')).replace('  ',' ')
		season = 1
		episode = 1
		sql_result2 = None
		cur.execute("select strpath, strFilename,c00 from episode_view where c12 = 1 and c13 = 1 and idshow = '"+str(temp_show_id)+"'")
		sql_result2 = cur.fetchall()
		try: nfo = sql_result2[0][0].replace(sql_result2[0][0].split('/')[9]+'/','')+'tvshow.nfo'
		except: nfo = ''
		episode_title = sql_result2[0][2]
		episode_title = regex.sub(' ', episode_title.replace('\'','').replace('&','and')).replace('  ',' ')
		file_path = str(sql_result2[0][0]) + str(sql_result2[0][1])
		#file_path = str(sql_result2[0][1])
		#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)

	tvdb_id = ''
	if nfo != '':
		f = open(str(nfo), 'r')
		for line in f:
			if 'https://www.themoviedb.org/tv/' in line:
				tmdb_id = line.replace('https://www.themoviedb.org/tv/','')
				break
		f.close()
		url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id='+ str(tmdb_id) + '&amp;season='+str(season)+'&amp;episode='+str(episode)
		try:
			tvdb_id = nfo.split('/')[-2]
		except:
			tvdb_id = ''
	con.close()
	#xbmc.log(str(sql_result)+'===>OPENINFO', level=xbmc.LOGINFO)
	#xbmc.log(str(url)+'===>OPENINFO', level=xbmc.LOGINFO)
	url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id='+ str(tmdb_id) + '&amp;season='+str(season)+'&amp;episode='+str(episode)
	return url

def trakt_next_episode_normal(tmdb_id_num=None):
	#import requests
	#import json

	tmdb_id=tmdb_id_num
	#headers = trak_auth()

	try:
		#response = requests.get('https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show', headers=headers).json()
		response = get_trakt_data(url='https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show', cache_days=0.5)
	except:
		xbmc.executebuiltin('Dialog.Close(busydialog)')

	id = response[0]['show']['ids']['trakt']
	title = response[0]['show']['title']

	response1 = ''
	i = 0
	while response1 == '' and i < 11:
		try:
			#response1 = requests.get('https://api.trakt.tv/shows/'+str(id)+'/progress/watched',headers=headers).json()
			response1 = get_trakt_data(url='https://api.trakt.tv/shows/'+str(id)+'/progress/watched', cache_days=0.00001)
		except:
			i = i + 1

	try:
		season = response1['next_episode']['season']
		episode = response1['next_episode']['number']
	except:
		season = '1'
		episode = '1'

	response2 = ''
	i = 0
	while response2 == '' and i < 22:
		try:
			#response2 = requests.get('https://api.trakt.tv/shows/'+str(id)+'/seasons/'+str(season)+'/episodes/'+str(episode)+'?extended=full', headers=headers).json()
			response2 = get_trakt_data(url='https://api.trakt.tv/shows/'+str(id)+'/seasons/'+str(season)+'/episodes/'+str(episode)+'?extended=full', cache_days=0.00001)
		except:
			i = i + 1

	first_aired = response2['first_aired']
	try:
			first_aired2 = datetime.strptime(first_aired, '%Y-%m-%dT%H:%M:%S.%fZ')
	except TypeError:
			first_aired2 = datetime(*(time.strptime(first_aired, '%Y-%m-%dT%H:%M:%S.%fZ')[0:6]))

	now = datetime.now()

	if first_aired2 < now:
		#url = 'RunPlugin(plugin://plugin.video.themoviedb.helper?info=play&amp;query='+str(title)+'&amp;type=episode&amp;season='+str(season)+'&amp;episode='+str(episode)+')'
		#url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id='+ str(tmdb_id) + '&amp;season='+str(season)+'&amp;episode='+str(episode)
		xbmc.executebuiltin('Dialog.Close(busydialog)')
		
		return tmdb_id, season, episode
	else:
		xbmcgui.Dialog().notification(heading='Trakt Next Episode Normal', message='Next Episode Not aired yet', icon=icon_path(),time=1000,sound=False)

def trakt_next_episode_rewatch(tmdb_id_num=None):
	#import requests
	#import json

	tmdb_id=tmdb_id_num
	#headers = trak_auth()

	#response = requests.get('https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show', headers=headers).json()
	response = get_trakt_data(url='https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show', cache_days=0.5)
	id = response[0]['show']['ids']['trakt']
	title = response[0]['show']['title']

	response1 = ''
	i = 0
	while response1 == '' and i < 11:
		try:
			#response1 = requests.get('https://api.trakt.tv/shows/'+str(id)+'/progress/watched',headers=headers).json()
			response1 = get_trakt_data('https://api.trakt.tv/shows/'+str(id)+'/progress/watched', cache_days=0.00001)
		except:
			i = i + 1

	last_watched_at = ''
	next_season_to_watch  = ''
	next_ep_to_watch = ''
	try:
		for i in response1['seasons']:
			for j in i['episodes']:
				if last_watched_at == '':
					last_watched_at = j['last_watched_at']
				if j['last_watched_at'] != None:
					if last_watched_at != '' and last_watched_at <= j['last_watched_at']:
						last_watched_at  = j['last_watched_at']
						next_season_to_watch = i['number']
						next_ep_to_watch = j['number']
	except:
		last_watched_at = ''
		next_season_to_watch  = ''
		next_ep_to_watch = ''
		import sqlite3
		#import ast
		addon = xbmcaddon.Addon()
		addon_path = addon.getAddonInfo('path')
		addonID = addon.getAddonInfo('id')
		addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
		con = sqlite3.connect(str(Path(addonUserDataFolder + '/trakt_tv_watched.db')))
		cur = con.cursor()
		sql_query = "select * from trakt where trakt  like '%" + str(title) + "%'"
		sql_result = cur.execute(sql_query).fetchall()
		#try: response1 = ast.literal_eval(sql_result[0][1].replace('\'\'','"'))
		#except: response1= None
		try: response1 = eval(sql_result[0][1].replace("'overview': ''",'\'overview\': "').replace("'', 'first_aired':",'", \'first_aired\':').replace("'title': ''",'\'title\': "').replace("'', 'year':",'", \'year\':'))
		except: response1 = None
		try:
			for i in response1['seasons']:
				for j in i['episodes']:
					if last_watched_at == '':
						last_watched_at = j['last_watched_at']
					if last_watched_at != '' and last_watched_at <= j['last_watched_at']:
						last_watched_at  = j['last_watched_at']
						next_season_to_watch = i['number']
						next_ep_to_watch = j['number']
		except:
			xbmc.executebuiltin('Dialog.Close(busydialog)')
			xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
			xbmcgui.Dialog().notification(heading='Trakt Next Episode Rewatch', message='Not REWATCHING!', icon=icon_path(),time=1000,sound=False)
			return

	next_flag = 'false'
	for i in response1['seasons']:
		for j in i['episodes']:
			if next_flag == 'true':
				last_watched_at  = j['last_watched_at']
				next_season_to_watch = i['number']
				next_ep_to_watch = j['number']
				next_flag = 'false'
				break
			try:
				if int(i['number']) == int(next_season_to_watch) and int(j['number']) == int(next_ep_to_watch):
					next_flag = 'true'
			except:
				xbmc.executebuiltin('Dialog.Close(busydialog)')
				xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
				xbmcgui.Dialog().notification(heading='Trakt Next Episode Rewatch', message='Not REWATCHING!', icon=icon_path(),time=1000,sound=False)
				return

	try:	
		season = int(next_season_to_watch)
		episode = int(next_ep_to_watch)
	except:
		season = '1'
		episode = '1'

	response2 = ''
	i = 0
	while response2 == '' and i < 22:
		try:
			#response2 = requests.get('https://api.trakt.tv/shows/'+str(id)+'/seasons/'+str(season)+'/episodes/'+str(episode)+'?extended=full', headers=headers).json()
			response2 = get_trakt_data('https://api.trakt.tv/shows/'+str(id)+'/seasons/'+str(season)+'/episodes/'+str(episode)+'?extended=full', cache_days=0.00001)
		except:
			i = i + 1

	first_aired = response2['first_aired']
	#first_aired2 = datetime.datetime.strptime(first_aired, '%Y-%m-%dT%H:%M:%S.%fZ')
	import time
	try:
		first_aired2 = datetime.strptime(first_aired, '%Y-%m-%dT%H:%M:%S.%fZ')
	except TypeError:
		first_aired2 = datetime(*(time.strptime(first_aired, '%Y-%m-%dT%H:%M:%S.%fZ')[0:6]))

	now = datetime.now()

	if first_aired2 < now:
		#url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id='+ str(tmdb_id) + '&amp;season='+str(season)+'&amp;episode='+str(episode)
		xbmc.executebuiltin('Dialog.Close(busydialog)')
		return tmdb_id, season, episode
	else:
		xbmcgui.Dialog().notification(heading='Trakt Next Episode Rewatch', message='Next Episode Not aired yet', icon=icon_path(),time=1000,sound=False)

def get_trakt_data(url='', cache_days=14, folder='Trakt'):
	from resources.lib.Utils import get_JSON_response
	headers = trak_auth()
	return get_JSON_response(url, cache_days, folder,headers=headers)

def trakt_refresh_all():
	try:
		trakt_watched_movies(cache_days=0.00001)
		trakt_watched_movies_full()
		trakt_watched_tv_shows_full()
		trakt_watched_tv_shows(cache_days=0.00001)
		#trakt_popular_shows(cache_days=0.00001)
		#trakt_popular_movies(cache_days=0.00001)
		#trakt_trending_shows(cache_days=0.00001)
		#trakt_trending_movies(cache_days=0.00001)
		#trakt_collection_shows(cache_days=0.00001)
		#trakt_collection_movies(cache_days=0.00001)
	except TypeError: 
		pass

def trakt_watched_movies(cache_days=None):
	#import requests
	#import json
	#headers = trak_auth()
	url = 'https://api.trakt.tv/sync/watched/movies'
	#response = requests.get(url, headers=headers).json()
	if cache_days:
		response = get_trakt_data(url, cache_days)
		#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
	else:
		response = get_trakt_data(url, 1)
	reverse_order = True
	response = sorted(response, key=lambda k: k['last_updated_at'], reverse=reverse_order)
	return response
  
def trakt_watched_movies_full():
	#import requests
	#import json
	from pathlib import Path
	headers = trak_auth()
	addon = xbmcaddon.Addon()
	addon_path = addon.getAddonInfo('path')
	addonID = addon.getAddonInfo('id')
	addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
	url = 'https://api.trakt.tv/sync/watched/movies'
	trakt_watched_stats = xbmcaddon.Addon(addon_ID()).getSetting('trakt_watched_stats')
	if trakt_watched_stats == 'true':
		#response = requests.get(url, headers=headers).json()
		response = get_trakt_data(url=url, cache_days=0.000001)
	else:
		trakt_data = None
		return None
	import os
	if os.path.exists(Path(addonUserDataFolder + '/trakt_movies_watched.db')):
		try: os.remove(Path(addonUserDataFolder + '/trakt_movies_watched.db'))
		except PermissionError: return

	import sqlite3
	con = sqlite3.connect(str(Path(addonUserDataFolder + '/trakt_movies_watched.db')))
	cur = con.cursor()

	sql_result = cur.execute("""
	CREATE TABLE trakt (
		tmdb_id INTEGER PRIMARY KEY,
		trakt VARCHAR NOT NULL
	);
	""").fetchall()
	con.commit()

	for i in response:
		sql_result = """
		INSERT INTO trakt (tmdb_id,trakt)
		VALUES( %s,%s);
		""" % (i['movie']['ids']['tmdb'],'"'+str(i).replace('"','\'\'')+'"')
		sql_result = cur.execute(sql_result).fetchall()
		con.commit()
	cur.close()
	con.close()

def trakt_watched_tv_shows_full():
	import requests
	import json
	from pathlib import Path
	headers = trak_auth()
	addon = xbmcaddon.Addon()
	addon_path = addon.getAddonInfo('path')
	addonID = addon.getAddonInfo('id')
	addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
	url = 'https://api.trakt.tv/sync/watched/shows?extended=full'
	trakt_watched_stats = xbmcaddon.Addon(addon_ID()).getSetting('trakt_watched_stats')
	if trakt_watched_stats == 'true':
		#response = requests.get(url, headers=headers).json()
		response = get_trakt_data(url=url, cache_days=0.000001)
	else:
		trakt_data = None
		return
	import os
	if os.path.exists(Path(addonUserDataFolder + '/trakt_tv_watched.db')):
		try: os.remove(Path(addonUserDataFolder + '/trakt_tv_watched.db'))
		except PermissionError: return

	import sqlite3
	con = sqlite3.connect(str(Path(addonUserDataFolder + '/trakt_tv_watched.db')))
	cur = con.cursor()

	sql_result = cur.execute("""
	CREATE TABLE trakt (
		tmdb_id INTEGER PRIMARY KEY,
		trakt VARCHAR NOT NULL
	);
	""").fetchall()
	con.commit()

	for i in response:
		sql_result = """
		INSERT INTO trakt (tmdb_id,trakt)
		VALUES( %s,%s);
		""" % (i['show']['ids']['tmdb'],'"'+str(i).replace('"','\'\'')+'"')
		sql_result = cur.execute(sql_result).fetchall()
		con.commit()
	cur.close()
	con.close()


def trakt_watched_tv_shows_progress(cache_days=None):
	#import requests
	#import json
	#headers = trak_auth()
	url = 'https://api.trakt.tv/sync/watched/shows?extended=full'
	#response = requests.get(url, headers=headers).json()
	response = get_trakt_data(url, 0.125)

	response2 = []
	for i in response:
		x = 0
		aired_episodes = i['show']['aired_episodes']
		tmdb_id = i['show']['ids']['tmdb']
		show_title = i['show']['title']
		for j in i['seasons']:
			for k in j['episodes']:
				if int(k['plays']) >= 1:
					x = x + 1
		played_episodes = x
		if aired_episodes > played_episodes:
			response2.append(i)
			print(show_title, tmdb_id, aired_episodes, played_episodes)

	#reverse_order = True
	#response = sorted(response2, key=lambda k: k['updated_at'], reverse=reverse_order)
	return response2


def trakt_watched_tv_shows(cache_days=None):
	#import requests
	#import json
	#headers = trak_auth()
	url = 'https://api.trakt.tv/sync/watched/shows?extended=noseasons'
	#response = requests.get(url, headers=headers).json()
	response = get_trakt_data(url, 0)
	reverse_order = True
	response = sorted(response, key=lambda k: k['last_updated_at'], reverse=reverse_order)
	return response

def trak_auth():
	import time
	trakt_token = None
	try: trakt_token = xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('trakt_token')
	except: trakt_token = None
	diamond_trakt_notice = xbmcgui.Window(10000).getProperty('diamond_trakt_notice')
	if diamond_trakt_notice == '':
		diamond_trakt_notice = None
	if not trakt_token and diamond_trakt_notice:
		return
	if not trakt_token:
		xbmcgui.Dialog().notification(heading='Trakt NOT AUTHENTICATED', message='Please go to the settings and authenticate TMDB Helper Trakt', icon=str(Path(icon_path())),time=1000,sound=False)
		xbmcgui.Window(10000).setProperty('diamond_trakt_notice', str(int(time.time())))
		return None

	#import xml.etree.ElementTree as ET
	#import json

	file_path = main_file_path()
	tmdb_settings = tmdb_settings_path()
	tmdb_traktapi = tmdb_traktapi_path()

	import html
	trakt_token = xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('trakt_token')
	trakt_token = eval(html.unescape(trakt_token))
	del html

	#tree = ET.parse(tmdb_settings)
	#root = tree.getroot()

	#for child in root:
	#	if (child.attrib)['id'] == 'trakt_token':
	#		token = json.loads(child.text)
	token = trakt_token

	inFile = open(tmdb_traktapi)
	client_id = ''
	client_secret = ''
	for line in inFile:
		
		if ('self.client_id = ' in line or 'CLIENT_ID = ' in line) and client_id == '':
			client_id = line.split("'")[1]
		if ('self.client_secret = ' in line or 'CLIENT_SECRET = ' in line) and client_secret == '':
			client_secret = line.split("'")[1]

	inFile.close()

	headers = {'trakt-api-version': '2', 'trakt-api-key': client_id, 'Content-Type': 'application/json'}
	headers['Authorization'] = 'Bearer {0}'.format(token.get('access_token'))
	return headers

def library_auto_tv(single_item=None):
	import fnmatch
	import urllib
	import urllib.request
	import requests
	import json
	import os

	library_auto_sync = xbmcaddon.Addon(addon_ID()).getSetting('library_auto_sync')
	xbmc.log(str('TRAKT_SYNC_TV_library_auto_tv')+'===>OPEN_INFO', level=xbmc.LOGFATAL)
	headers = trak_auth()
	basedir_tv = basedir_tv_path()
	file_path = basedir_tv

	if not os.path.exists(file_path):
		try:
			os.mkdir(file_path)
		except:
			os.makedirs(file_path)

	x = 0
	response = ''
	while response == '' and x <11:
		try: 
			#response = requests.get('https://api.trakt.tv/sync/collection/shows', headers=headers).json()
			response = get_trakt_data(url='https://api.trakt.tv/sync/collection/shows', cache_days=0.00001)
		except: 
			x = x + 1
	collection = sorted(response, key=lambda i: i['show']['title'], reverse=False)
	for i in collection:
		if single_item:
			if i['show']['ids']['trakt'] == single_item['trakt_id']:
				process_flag_show = True
			else:
				process_flag_show = False
			if i['show']['ids']['tvdb'] == 'None' or i['show']['ids']['tvdb'] == None:
				process_flag_show = False
		else:
			process_flag_show = True
			if i['show']['ids']['tvdb'] == 'None' or i['show']['ids']['tvdb'] == None:
				process_flag_show = False
		if process_flag_show == True:
			nfo = 'https://thetvdb.com/?tab=series&id=' + str(i['show']['ids']['tvdb'])
			if str(i['show']['ids']['tmdb']) == 'None':
				nfo = 'https://thetvdb.com/?tab=series&id=' + str(i['show']['ids']['tvdb'])
			else:
				nfo = 'https://www.themoviedb.org/tv/' + str(i['show']['ids']['tmdb'])
			nfo_path = Path(str(file_path) + '/' + str(i['show']['ids']['tvdb']) + '/' + 'tvshow.nfo')
			clear_logo = Path(str(file_path) + '/' + str(i['show']['ids']['tvdb']) + '/' + 'clearlogo.png')
			tvthumb_path = Path(str(file_path) + '/' + str(i['show']['ids']['tvdb']) + '/' + 'landscape.jpg')

			if not os.path.exists(Path(str(file_path) + '/' + str(i['show']['ids']['tvdb']))):
				os.mkdir(Path(str(file_path) + '/' + str(i['show']['ids']['tvdb'])))

			if not os.path.exists(nfo_path):
				file = open(nfo_path, 'w')
				file.write(nfo)
				file.close()

			try:
				tvdb_id = i['show']['ids']['tvdb']
				tvdb_path = Path(str(file_path) + '/' + str(i['show']['ids']['tvdb']) + '/' +str(tvdb_id)+ '.tvdb')
				if not os.path.exists(tvdb_path) and str(tvdb_id).isnumeric():
					Path(tvdb_path).touch()
			except:
				pass

			try:
				tmdb_id = i['show']['ids']['tmdb']
				tmdb_path = Path(str(file_path) + '/' + str(i['show']['ids']['tvdb']) + '/' +str(tmdb_id)+ '.tmdb')
				if not os.path.exists(tmdb_path) and str(tmdb_id).isnumeric():
					Path(tmdb_path).touch()
			except:
				pass

			try:
				imdb_id = i['show']['ids']['imdb']
				imdb_path = Path(str(file_path) + '/' + str(i['show']['ids']['tvdb']) + '/' +str(imdb_id)+ '.imdb')
				if not os.path.exists(imdb_path) and str(imdb_id[2:]).isnumeric():
					Path(imdb_path).touch()
			except:
				pass

			try:
				trakt_id = i['show']['ids']['trakt']
				trakt_path = Path(str(file_path) + '/' + str(i['show']['ids']['tvdb']) + '/' +str(trakt_id)+ '.trakt')
				if not os.path.exists(trakt_path) and str(trakt_id).isnumeric():
					Path(trakt_path).touch()
			except:
				pass

			art_path = Path(str(file_path) + '/' + str(i['show']['ids']['tvdb']) + '/' + 'tvshow.fanart')
			if not os.path.exists(art_path):
				tmdb_api = tmdb_api_key()
				fanart_api = fanart_api_key()
				show_file_path = Path(str(basedir_tv) + '/' + str(i['show']['ids']['tvdb']) + '/')
				get_art_fanart_tv(str(i['show']['ids']['tvdb']), fanart_api, show_file_path, art_path, str(i['show']['ids']['tmdb']),tmdb_api)
				
				show_title = i['show']['title']
				for c in r'[]/\;,><&*:%=+@!#^()|?^':
					show_title = show_title.replace(c,'')

				file = open(art_path, 'w')
				file.write(str(i['show']['ids']['tvdb']) + ' - '+str(show_title))
				file.close()

			"""
		###OVERWRITE NFO
			if os.path.exists(nfo_path):
				file = open(nfo_path, 'w')
				file.write(nfo)
				file.close()
			"""

			for s in i['seasons']:
				if single_item:
					if single_item['season'] == 0:
						process_flag_season = True
					elif int(single_item['season']) == int(s['number']):
						process_flag_season = True
					else:
						process_flag_season = False
				else:
					process_flag_season = True
				if process_flag_season == True:
					if not os.path.exists(Path(str(file_path) + '/' + str(i['show']['ids']['tvdb']) + '/Season ' + str(s['number']))):
						os.mkdir(Path(str(file_path) + '/' + str(i['show']['ids']['tvdb']) + '/Season ' + str(s['number'])))


					for e in s['episodes']:
						if single_item:
							if single_item['episode'] == 0:
								process_flag_episode = True
							elif int(single_item['episode']) == int(e['number']):
								process_flag_episode = True
							else: 
								process_flag_episode = False
						else:
							process_flag_episode = True
						if process_flag_episode == True:
							url = "plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=" + str(i['show']['ids']['tmdb']) + "&amp;season=" + str(s['number']) + "&amp;episode=" + str(e['number'])
							if str(i['show']['ids']['tmdb']) == 'None':
								url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;query=' + str(i['show']['title']) + '&amp;type=episode&amp;season=' + str(s['number']) + '&amp;episode=' + str(e['number'])
							file_name = str(i['show']['title']) +' - S' + format(s['number'], '02d') + 'E' + format(e['number'], '02d') + '.strm'

							for c in r'[]/\;,><&*:%=+@!#^()|?^':
								file_name = file_name.replace(c,'')

							strm_path = Path(str(file_path) + '/' + str(i['show']['ids']['tvdb']) + '/Season ' + str(s['number']) + '/' + file_name)

							"""
							###Overwrite existing strm files.
							file = open(strm_path, 'w')
							file.write(url)
							file.close()
							"""
							dir = Path(str(file_path) + '/' + str(i['show']['ids']['tvdb']) + '/Season ' + str(s['number']) + '/')
							match = "*S"+format(s['number'],'02d')+"E"+format(e['number'], '02d')+'.strm'
							n_match = ''
							if not os.path.exists(strm_path):
								for n in fnmatch.filter(os.listdir(dir), match):
									n_match = n
								if n_match == '':
									file = open(strm_path, 'w')
									file.write(url)
									file.close()

	add_calendar = 1
	x = 0
	response = ''
	while response == '' and x <11:
		try: 
			#response = requests.get('https://api.trakt.tv/calendars/my/shows/'+start_date+'/'+str(days), headers=headers).json()
			response = get_trakt_data(url='https://api.trakt.tv/calendars/my/shows/'+start_date+'/'+str(days), cache_days=1)
		except: 
			x = x + 1
	calendar_eps = sorted(response, key=lambda i: i['show']['title'], reverse=False)

	for n in calendar_eps:
	##Shows can be hidden on the trakt calendar, current config will add all new episodes which show up on calendar so hide any shows not in collection
	##required to add episodes before they appear in Trakt Collection, hide on calendar any shows you dont want to see auto added.
		if add_calendar == 1:
			if single_item:
				if n['show']['ids']['trakt'] == single_item['trakt_id']:
					process_flag_calendar = True
				else:
					process_flag_calendar = False
			else:
				process_flag_calendar = True
			if process_flag_calendar == True:
				if str(n['show']['ids']['tmdb']) == 'None':
					nfo = 'https://thetvdb.com/?tab=series&id=' + str(n['show']['ids']['tvdb'])
				else:
					nfo = 'https://www.themoviedb.org/tv/' + str(n['show']['ids']['tmdb'])
				nfo_path = Path(str(file_path) + '/' + str(n['show']['ids']['tvdb']) + '/' + 'tvshow.nfo')
				
				if not os.path.exists(Path(str(file_path) + '/' + str(n['show']['ids']['tvdb']))):
					os.mkdir(Path(str(file_path) + '/' + str(n['show']['ids']['tvdb'])))

				if not os.path.exists(nfo_path):
					file = open(nfo_path, 'w')
					file.write(nfo)
					file.close()

				try:
					tvdb_id = n['show']['ids']['tvdb']
					tvdb_path = Path(str(file_path) + '/' + str(n['show']['ids']['tvdb']) + '/' +str(tvdb_id)+ '.tvdb')
					if not os.path.exists(tvdb_path) and str(tvdb_id).isnumeric():
						Path(tvdb_path).touch()
				except:
					pass

				try:
					tmdb_id = n['show']['ids']['tmdb']
					tmdb_path = Path(str(file_path) + '/' + str(n['show']['ids']['tvdb']) + '/' +str(tmdb_id)+ '.tmdb')
					if not os.path.exists(tmdb_path) and str(tmdb_id).isnumeric():
						Path(tmdb_path).touch()
				except:
					pass

				try:
					imdb_id = n['show']['ids']['imdb']
					imdb_path = Path(str(file_path) + '/' + str(n['show']['ids']['tvdb']) + '/' +str(imdb_id)+ '.imdb')
					if not os.path.exists(imdb_path) and str(imdb_id[2:]).isnumeric():
						Path(imdb_path).touch()
				except:
					pass

				try:
					trakt_id = n['show']['ids']['trakt']
					trakt_path = Path(str(file_path) + '/' + str(n['show']['ids']['tvdb']) + '/' +str(trakt_id)+ '.trakt')
					if not os.path.exists(trakt_path) and str(trakt_id).isnumeric():
						Path(trakt_path).touch()
				except:
					pass


				if single_item:
					if single_item['season'] == 0:
						process_flag_calendar_season = True
					elif int(single_item['season']) == int(n['episode']['season']):
						process_flag_calendar_season = True
					else:
						process_flag_calendar_season = False
				else:
					process_flag_calendar_season = True

				if process_flag_calendar_season == True:
					if not os.path.exists(Path(str(file_path) + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season']))):
						os.mkdir(Path(str(file_path) + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season'])))

					if single_item:
						if single_item['episode'] == 0:
							process_flag_calendar_episode = True
						elif int(single_item['episode']) == int(n['episode']['number']):
							process_flag_calendar_episode = True
						else: 
							process_flag_calendar_episode = False
					else:
						process_flag_calendar_episode = True
					if process_flag_calendar_episode == True:

						url = "plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=" + str(n['show']['ids']['tmdb']) + "&amp;season=" + str(n['episode']['season']) + "&amp;episode=" + str(n['episode']['number'])
						if str(n['show']['ids']['tmdb']) == 'None':
							url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;query=' + str(n['show']['title']) + '&amp;type=episode&amp;season=' + str(n['episode']['season']) + '&amp;episode=' + str(n['episode']['number'])
						file_name = str(n['show']['title']) +' - S' + format(n['episode']['season'], '02d') + 'E' + format(n['episode']['number'], '02d') + '.strm'
						thumb_file_name = str(n['show']['title']) +' - S' + format(n['episode']['season'], '02d') + 'E' + format(n['episode']['number'], '02d') + '-thumb.jpg'
						for c in r'[]/\;,><&*:%=+@!#^()|?^':
							file_name = file_name.replace(c,'')
							thumb_file_name = thumb_file_name.replace(c,'')

						strm_path = Path(str(file_path) + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season']) + '/' + file_name)
						thumb_path = Path(str(file_path) + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season']) + '/' + thumb_file_name)
						dir = Path(str(file_path) + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season']) + '/')
						match = "*S"+format(n['episode']['season'],'02d')+"E"+format(n['episode']['number'], '02d')+'.strm'
						n_match = ''
						if not os.path.exists(strm_path):
							for n in fnmatch.filter(os.listdir(dir), match):
								n_match = n
							if n_match == '':
									file = open(strm_path, 'w')
									file.write(url)
									file.close()

						if not os.path.exists(thumb_path) and n_match == '':
							tvdb_url = str('https://api.thetvdb.com/series/' + str(n['show']['ids']['tvdb']) + '/episodes/query?airedSeason=' + str(n['episode']['season']) + '&airedEpisode=' + str(n['episode']['number']))
							request = requests.get(tvdb_url).json()
							try:
								thumbnail_image = 'https://thetvdb.com/banners/' + request['data'][0]['filename']
							except:
								thumbnail_image = 'https://thetvdb.com/banners/'
							if thumbnail_image != 'https://thetvdb.com/banners/':
								get_file(thumbnail_image, thumb_path)
							else:
								response = requests.get('http://api.tvmaze.com/lookup/shows?thetvdb='+str(n['show']['ids']['tvdb'])).json()
								show_id = response['id']
								response = requests.get('http://api.tvmaze.com/shows/'+str(show_id)+'/episodes').json()
								for x in response:
									if x['season'] == int(n['episode']['season']) and x['number'] == int(n['episode']['number']):
										episode_id =  x['id']
								try:
									response = requests.get('http://api.tvmaze.com/episodes/'+str(episode_id)).json()
								except:
									response = {}
									response['image'] = None
									response['airdate'] = None
									response['summary'] = None
								image_test = response['image'] == None
								air_date = response['airdate']
								plot = response['summary']
								if image_test != True:
									tvmaze_thumb_medium = response['image']['medium']
									tvmaze_thumb_large = response['image']['medium'].replace('medium','large')
									tvmaze_thumb_original = response['image']['original'].replace('medium','large')
									get_file(tvmaze_thumb_large, thumb_path)

	return


def library_auto_movie(single_item=None):
	import fnmatch
	import requests
	import json

	xbmc.log(str('TRAKT_SYNC_MOVIE_library_auto_movie')+'===>OPEN_INFO', level=xbmc.LOGFATAL)
	headers = trak_auth()
	basedir_tv = basedir_movies_path()
	file_path = basedir_tv

	if not os.path.exists(file_path):
		try:
			os.mkdir(file_path)
		except:
			os.makedirs(file_path)

	x = 0
	response = ''
	while response == '' and x <11:
		try: 
			#response = requests.get('https://api.trakt.tv/sync/collection/movies', headers=headers).json()
			response = get_trakt_data(url='https://api.trakt.tv/sync/collection/movies', cache_days=0.0001)
		except: 
			x = x + 1
	collection = sorted(response, key=lambda i: i['movie']['title'], reverse=False)

	for i in collection:
		if single_item:
			if i['movie']['ids']['trakt'] == single_item['trakt_id']:
				process_flag_movie = True
			else:
				process_flag_movie = False
		else:
			process_flag_movie = True
		if process_flag_movie == True:
			nfo = 'https://www.themoviedb.org/tv/' + str(i['movie']['ids']['tmdb'])
			nfo_path = Path(str(file_path) + '/' + str(i['movie']['ids']['tmdb']) + '/' + 'movie.nfo')
			clear_logo = Path(str(file_path) + '/' + str(i['movie']['ids']['tmdb']) + '/' + 'clearlogo.png')
			tvthumb_path = Path(str(file_path) + '/' + str(i['movie']['ids']['tmdb']) + '/' + 'landscape.jpg')

			try:
				tmdb_id = i['movie']['ids']['tmdb']
				tmdb_path = Path(str(file_path) + '/' + str(i['movie']['ids']['tmdb']) + '/' +str(tmdb_id)+ '.tmdb')
				if not os.path.exists(tmdb_path) and str(tmdb_id).isnumeric():
					Path(tmdb_path).touch()
			except:
				pass

			try:
				imdb_id = i['movie']['ids']['imdb']
				imdb_path = Path(str(file_path) + '/' + str(i['movie']['ids']['tmdb']) + '/' +str(imdb_id)+ '.imdb')
				if not os.path.exists(imdb_path) and str(imdb_id[2:]).isnumeric():
					Path(imdb_path).touch()
			except:
				pass

			try:
				trakt_id = i['movie']['ids']['trakt']
				trakt_path = Path(str(file_path) + '/' + str(i['movie']['ids']['tmdb']) + '/' +str(trakt_id)+ '.trakt')
				if not os.path.exists(trakt_path) and str(trakt_id).isnumeric():
					Path(trakt_path).touch()
			except:
				pass

			if not os.path.exists(Path(str(file_path) + '/' + str(i['movie']['ids']['tmdb']))):
				os.mkdir(Path(str(file_path) + '/' + str(i['movie']['ids']['tmdb'])))

			if not os.path.exists(nfo_path):
				file = open(nfo_path, 'w')
				file.write(nfo)
				file.close()

			art_path = Path(str(file_path) + '/' + str(i['movie']['ids']['tmdb']) + '/' + 'movie.fanart')
			movie_title = i['movie']['title']
			for c in r'[]/\;,><&*:%=+@!#^()|?^':
				movie_title = movie_title.replace(c,'')
			if not os.path.exists(art_path):
				tmdb_api = tmdb_api_key()
				fanart_api = fanart_api_key()
				show_file_path = Path(str(basedir_tv) + '/' + str(i['movie']['ids']['tmdb']) + '/')

				get_art_fanart_movie(str(i['movie']['ids']['tmdb']), fanart_api, show_file_path, art_path, tmdb_api)

				file = open(art_path, 'w')
				try: file.write(str(i['movie']['ids']['tmdb']) + ' - '+str(movie_title))
				except: file.write(str(i['movie']['ids']['tmdb']))
				file.close()

			file_name = str(movie_title) +' - ' + str(i['movie']['year']) + '.strm'
			for c in r'[]/\;,><&*:%=+@!#^()|?^':
				file_name = file_name.replace(c,'')
			url = "plugin://plugin.video.themoviedb.helper?info=play&amp;type=movie&amp;tmdb_id=" + str(i['movie']['ids']['tmdb'])

			strm_path = Path(str(file_path) + '/' + str(i['movie']['ids']['tmdb']) + '/' + file_name)
			"""
			###OVERWRITE NFO
			if os.path.exists(nfo_path):
				file = open(nfo_path, 'w')
				file.write(nfo)
				file.close()
			"""

			n_match = ''
			dir = Path(str(file_path) + '/' + str(i['movie']['ids']['tmdb']) + '/')
			match = file_name
			if not os.path.exists(strm_path):
				try:
					for n in fnmatch.filter(os.listdir(dir), match):
						n_match = n
					if n_match == '':
						file = open(strm_path, 'w')
						file.write(url)
						file.close()
				except:
					pass
					

			"""
			###Overwrite existing strm files.
			file = open(strm_path, 'w')
			file.write(url)
			file.close()
			"""
	return
