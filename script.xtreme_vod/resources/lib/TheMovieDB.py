import re
import xbmc, xbmcgui, xbmcaddon
from resources.lib import Utils
from resources.lib import local_db
from resources.lib.WindowManager import wm
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib.library import fanart_api_key

import html
from inspect import currentframe, getframeinfo
#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)

ext_key = xbmcaddon.Addon().getSetting('tmdb_api')



if len(ext_key) == 32:
	API_key = ext_key
else:
	API_key = 'edde6b5e41246ab79a2697cd125e1781'

#https://github.com/umbrellaplug/umbrellaplug.github.io/blob/77057a7cf63ab8a628246c986197d3ff88cf0fbf/nexus/plugin.video.umbrella/resources/lib/modules/playcount.py#L8
#https://github.com/umbrellaplug/umbrellaplug.github.io/blob/77057a7cf63ab8a628246c986197d3ff88cf0fbf/nexus/plugin.video.umbrella/resources/lib/context/tmdb.py#L9
#tmdb_api_key = 'edde6b5e41246ab79a2697cd125e1781'
#omdb_api_key = 'd4daa2b'
#tvdb_api_key = '06cff30690f9b9622957044f2159ffae'
#tmdb_API_key = 'bc96b19479c7db6c8ae805744d0bdfe2'

def get_certification_list(media_type):
	response = get_tmdb_data('certification/%s/list?' % media_type, 999999)
	if 'certifications' in response:
		return response['certifications']
	else:
		return []

def merge_with_cert_desc(input_list, media_type):
	cert_list = get_certification_list(media_type)
	for item in input_list:
		if item['iso_3166_1'].upper() not in cert_list:
			continue
		hit = Utils.dictfind(lst=cert_list[item['iso_3166_1'].upper()], key='certification', value=item['certification'])
		if hit:
			item['meaning'] = hit['meaning']
	return input_list

def handle_tmdb_multi_search(results=[]):
	listitems = []
	for item in results:
		if item['media_type'] == 'movie':
			listitem = handle_tmdb_movies([item])[0]
		elif item['media_type'] == 'tv':
			listitem = handle_tmdb_tvshows([item])[0]
		else:
			try: listitem = handle_tmdb_people([item])[0]
			except: continue
		listitems.append(listitem)
	return listitems

def handle_tmdb_movies(results=[], local_first=True, sortkey='year'):
	response = get_tmdb_data('genre/movie/list?language=%s&' % xbmcaddon.Addon().getSetting('LanguageID'), 30)
	id_list = [item['id'] for item in response['genres']]
	label_list = [item['name'] for item in response['genres']]
	movies = []
	for movie in results:
		#Utils.tools_log(Utils.fetch(movie, 'title'))
		if 'genre_ids' in movie:
			genre_list = [label_list[id_list.index(genre_id)] for genre_id in movie['genre_ids'] if genre_id in id_list]
			genres = ' / '.join(genre_list)
		else:
			genres = ''
		tmdb_id = str(Utils.fetch(movie, 'id'))
		artwork = get_image_urls(poster=movie.get('poster_path'), fanart=movie.get('backdrop_path'))
		year = Utils.get_year(Utils.fetch(movie, 'release_date'))
		trailer = 'plugin://'+str(addon_ID())+'?info=playtrailer&&id=%s' % str(tmdb_id)
		path = 'plugin://'+str(addon_ID())+'?info='+str(addon_ID_short())+'&&id=%s&year=%s' % (str(tmdb_id), str(year))
		original_title = Utils.fetch(movie, 'original_title')
		original_title2 = ''
		try:
			for i in movie['alternative_titles']['titles']:
				if i['type'] == 'original title' and i['iso_3166_1'] in {'US','UK'}:
					original_title2 = i['title']
			if original_title2 != original_title and original_title2 != '':
				original_title = original_title2
		except KeyError:
			pass
		except TypeError:
			pass
		listitem = {
			'title': Utils.fetch(movie, 'title'),
			'Label': Utils.fetch(movie, 'title'),
			'OriginalTitle': original_title,
			'id': tmdb_id,
			'imdb_id': Utils.fetch(movie, 'imdb_id'),
			'path': path,
			'full_url': Utils.fetch(movie, 'full_url'),
			'stream_id': Utils.fetch(movie, 'stream_id'),
			'media_type': 'movie',
			'mediatype': 'movie',
			'country': Utils.fetch(movie, 'original_language'),
			'plot': Utils.fetch(movie, 'overview'),
			'Trailer': trailer,
			'Popularity': Utils.fetch(movie, 'popularity'),
			'Rating': Utils.fetch(movie, 'vote_average'),
			'credit_id': Utils.fetch(movie, 'credit_id'),
			'character': Utils.fetch(movie, 'character'),
			'job': Utils.fetch(movie, 'job'),
			'department': Utils.fetch(movie, 'department'),
			'Votes': Utils.fetch(movie, 'vote_count'),
			'User_Rating': Utils.fetch(movie, 'rating'),
			'year': year,
			'genre': genres,
			'Premiered': Utils.fetch(movie, 'release_date')
			}
		listitem.update(artwork)
		date = Utils.fetch(movie, 'release_date')
		movies.append(listitem)
	#movies = local_db.merge_with_local_movie_info(movies, local_first, sortkey)
	#Utils.hide_busy()
	return movies

def handle_tmdb_tvshows(results, local_first=True, sortkey='year'):

	tvshows = []
	response = get_tmdb_data('genre/tv/list?language=%s&' % xbmcaddon.Addon().getSetting('LanguageID'), 30)
	id_list = [item['id'] for item in response['genres']]
	label_list = [item['name'] for item in response['genres']]
	for tv in results:
		tmdb_id = Utils.fetch(tv, 'id')
		artwork = get_image_urls(poster=tv.get('poster_path'), fanart=tv.get('backdrop_path'))
		if 'genre_ids' in tv:
			genre_list = [label_list[id_list.index(genre_id)] for genre_id in tv['genre_ids'] if genre_id in id_list]
			genres = ' / '.join(genre_list)
		else:
			genres = ''
		duration = ''
		if 'episode_run_time' in tv:
			if len(tv['episode_run_time']) > 1:
				duration = '%i - %i' % (min(tv['episode_run_time']), max(tv['episode_run_time']))
			elif len(tv['episode_run_time']) == 1:
				duration = '%i' % tv['episode_run_time'][0]

		newtv = {
			'title': Utils.fetch(tv, 'name'),
			'TVShowTitle': Utils.fetch(tv, 'name'),
			'OriginalTitle': Utils.fetch(tv, 'original_name'),
			'duration': duration,
			'id': tmdb_id,
			'imdb_id': Utils.fetch(tv, 'imdb_id'),
			'genre': genres,
			'country': Utils.fetch(tv, 'original_language'),
			'Popularity': Utils.fetch(tv, 'popularity'),
			'credit_id': Utils.fetch(tv, 'credit_id'),
			'Plot': Utils.fetch(tv, 'overview'),
			'Trailer': 'plugin://'+str(addon_ID())+'?info=tvtrailer&&id=%s' % str(tmdb_id),
			'year': Utils.get_year(Utils.fetch(tv, 'first_air_date')),
			'media_type': 'tv',
			'mediatype': 'tvshow',
			'character': Utils.fetch(tv, 'character'),
			'path': 'plugin://'+str(addon_ID())+'?info=extendedtvinfo&&id=%s' % str(tmdb_id),
			'Rating': Utils.fetch(tv, 'vote_average'),
			'User_Rating': str(Utils.fetch(tv, 'rating')),
			'Votes': Utils.fetch(tv, 'vote_count'),
			'TotalEpisodes': Utils.fetch(tv, 'number_of_episodes'),
			'TotalSeasons': Utils.fetch(tv, 'number_of_seasons'),
			'Release_Date': Utils.fetch(tv, 'first_air_date'),
			'status': Utils.fetch(tv, 'status'),
			'Premiered': Utils.fetch(tv, 'first_air_date')
			}
		newtv.update(artwork)
		date = Utils.fetch(tv, 'first_air_date')
		tvshows.append(newtv)
	tvshows = local_db.merge_with_local_tvshow_info(tvshows, local_first, sortkey)
	return tvshows

def handle_tmdb_seasons(results):
	listitems = []
	for season in results:
		season_number = str(Utils.fetch(season, 'season_number'))
		artwork = get_image_urls(poster=season.get('poster_path'))
		title = 'Specials' if season_number == '0' else 'Season %s' % season_number
		listitem = {
			'media_type': 'season',
			'mediatype': 'season',
			'title': title,
			'season': season_number,
			'air_date': Utils.fetch(season, 'air_date'),
			'year': Utils.get_year(Utils.fetch(season, 'air_date')),
			'id': Utils.fetch(season, 'id')
			}
		listitem.update(artwork)
		listitems.append(listitem)
	return listitems

def handle_tmdb_episodes(results):
	listitems = []
	for item in results:
		title = Utils.clean_text(Utils.fetch(item, 'name'))
		if not title:
			title = '%s %s' % ('Episode', Utils.fetch(item, 'episode_number'))
		try:
			artwork = get_image_urls(still=item.get('still_path'))
		except:
			artwork = []
		try: rating = round(float(Utils.fetch(item, 'vote_average')), 1)
		except: rating = 0
		listitem = {
			'media_type': 'episode',
			'mediatype': 'episode',
			'title': title,
			'release_date': Utils.fetch(item, 'air_date'),
			'episode': Utils.fetch(item, 'episode_number'),
			'production_code': Utils.fetch(item, 'production_code'),
			'season': Utils.fetch(item, 'season_number'),
			'Rating': rating,
			'Votes': Utils.fetch(item, 'vote_count'),
			'Plot': Utils.fetch(item, 'overview'),
			'id': Utils.fetch(item, 'id'),
			'Description': Utils.clean_text(Utils.fetch(item, 'overview'))
			}
		listitem.update(artwork)
		date = Utils.fetch(item, 'air_date')
		listitems.append(listitem)
	return listitems

def handle_tmdb_misc(results):
	listitems = []
	for item in results:
		artwork = get_image_urls(poster=item.get('poster_path'))
		listitem = {
			'title': Utils.clean_text(Utils.fetch(item, 'name')),
			'certification': Utils.fetch(item, 'certification') + Utils.fetch(item, 'rating'),
			'item_count': Utils.fetch(item, 'item_count'),
			'release_date': Utils.fetch(item, 'release_date'),
			'path': 'plugin://'+str(addon_ID())+'?info=listmovies&---id=%s' % Utils.fetch(item, 'id'),
			'year': Utils.get_year(Utils.fetch(item, 'release_date')),
			'iso_3166_1': Utils.fetch(item, 'iso_3166_1').lower(),
			'author': Utils.fetch(item, 'author'),
			'content': Utils.clean_text(Utils.fetch(item, 'content')),
			'id': Utils.fetch(item, 'id'),
			'url': Utils.fetch(item, 'url'),
			'Description': Utils.clean_text(Utils.fetch(item, 'description'))
			}
		listitem.update(artwork)
		listitems.append(listitem)
	return listitems

def handle_tmdb_videos(results):
	listitems = []
	for item in results:
		image = 'https://i.ytimg.com/vi/%s/0.jpg' % Utils.fetch(item, 'key')
		listitem = {
			'thumb': image,
			'title': Utils.fetch(item, 'name'),
			'iso_639_1': Utils.fetch(item, 'iso_639_1'),
			'type': Utils.fetch(item, 'type'),
			'key': Utils.fetch(item, 'key'),
			'youtube_id': Utils.fetch(item, 'key'),
			'site': Utils.fetch(item, 'site'),
			'id': Utils.fetch(item, 'id'),
			'size': Utils.fetch(item, 'size')
			}
		listitems.append(listitem)
	return listitems

def handle_tmdb_people(results):
	people = []
	for person in results:
		artwork = get_image_urls(profile=person.get('profile_path'))
		also_known_as = ' / '.join(Utils.fetch(person, 'also_known_as'))
		newperson = {
			'adult': str(Utils.fetch(person, 'adult')),
			'name': person['name'],
			'title': person['name'],
			'also_known_as': also_known_as,
			'alsoknownas': also_known_as,
			'biography': Utils.clean_text(Utils.fetch(person, 'biography')),
			'birthday': Utils.fetch(person, 'birthday'),
			'age': Utils.calculate_age(Utils.fetch(person, 'birthday'), Utils.fetch(person, 'deathday')),
			'character': Utils.fetch(person, 'character'),
			'department': Utils.fetch(person, 'department'),
			'job': Utils.fetch(person, 'job'),
			'media_type': 'person',
			'id': str(person['id']),
			'cast_id': str(Utils.fetch(person, 'cast_id')),
			'credit_id': str(Utils.fetch(person, 'credit_id')),
			'path': 'plugin://'+str(addon_ID())+'?info=extendedactorinfo&&id=%s' % str(person['id']),
			'deathday': Utils.fetch(person, 'deathday'),
			'place_of_birth': Utils.fetch(person, 'place_of_birth'),
			'placeofbirth': Utils.fetch(person, 'place_of_birth'),
			'homepage': Utils.fetch(person, 'homepage')
			}
		newperson.update(artwork)
		people.append(newperson)
	return people

def handle_tmdb_images(results):
	images = []
	for item in results:
		artwork = get_image_urls(poster=item.get('file_path'))
		image = {
			'aspectratio': item['aspect_ratio'],
			'vote_average': Utils.fetch(item, 'vote_average'),
			'iso_639_1': Utils.fetch(item, 'iso_639_1')
			}
		image.update(artwork)
		images.append(image)
	return images

def handle_tmdb_tagged_images(results):
	images = []
	for item in results:
		artwork = get_image_urls(poster=item.get('file_path'))
		image = {
			'aspectratio': item['aspect_ratio'],
			'vote_average': Utils.fetch(item, 'vote_average'),
			'iso_639_1': Utils.fetch(item, 'iso_639_1'),
			'title': Utils.fetch(item['media'], 'title'),
			'mediaposter': 'https://image.tmdb.org/t/p/w500%s' % Utils.fetch(item['media'], 'poster_path')
			}
		image.update(artwork)
		images.append(image)
	return images

def search_company(company_name):
	regex = re.compile('\(.+?\)')
	company_name = regex.sub('', company_name)
	response = get_tmdb_data('search/company?query=%s&' % Utils.url_quote(company_name), 10)
	if response and 'results' in response:
		return response['results']
	else:
		return ''

def get_movie_info(movie_label, year=None, use_dialog=True, item_id=None, notify = True):
	if item_id:
		return single_movie_info(movie_id=item_id, cache_time=7, notify=notify)
	#movies = movie_label.split(' / ')
	if year:
		year_string = '&primary_release_year=' + str(year)
	else:
		year_string = ''
	response = get_tmdb_data('search/movie?query=%s%s&include_adult=%s&' % (Utils.url_quote(movie_label), year_string, xbmcaddon.Addon().getSetting('include_adults')), 30)
	if not response or 'results' not in response:
		return False
	for i in range(len(response['results'])-1, 0, -1):
		if response['results'][i]['title'] != movie_label:
			del response['results'][i]
	if len(response['results']) > 1 and use_dialog:
		listitem, index = wm.open_selectdialog(listitems=handle_tmdb_movies(response['results']))
		if int(index) == -1:
			return False
		elif index >= 0:
			return listitem
	elif response['results']:
		return response['results'][0]
	return False

def get_tvshow_info(tvshow_label, year=None, use_dialog=True, item_id=None):
	if item_id:
		return single_tvshow_info(tvshow_id=item_id, cache_time=7)
	#tvshow = tvshow_label.split(' / ')
	if year:
		year_string = '&first_air_date_year=' + str(year)
	else:
		year_string = ''
	response = get_tmdb_data('search/tv?query=%s%s&include_adult=%s&' % (Utils.url_quote(tvshow_label), year_string, xbmcaddon.Addon().getSetting('include_adults')), 30)
	if not response or 'results' not in response:
		return False
	for i in range(len(response['results'])-1, 0, -1):
		if response['results'][i]['original_name'] != tvshow_label:
			del response['results'][i]
	if len(response['results']) > 1 and use_dialog:
		listitem, index = wm.open_selectdialog(listitems=handle_tmdb_tvshows(response['results']))#
		if int(index) == -1:
			return False
		elif index >= 0:
			return listitem
	elif response['results']:
		return response['results'][0]
	return False

def get_person_info(person_label):
	persons = person_label.split(' / ')
	response = get_tmdb_data('search/person?query=%s&include_adult=%s&' % (Utils.url_quote(persons[0]), xbmcaddon.Addon().getSetting('include_adults')), 30)
	if not response or 'results' not in response:
		return False
	if len(response['results']) > 1:
		listitem, index = wm.open_selectdialog(listitems=handle_tmdb_people(response['results']))
		if index >= 0:
			return response['results'][index]
	elif response['results']:
		return response['results'][0]
	return False

def get_keyword_id(keyword):
	response = get_tmdb_data('search/keyword?query=%s&include_adult=%s&' % (Utils.url_quote(keyword), xbmcaddon.Addon().getSetting('include_adults')), 30)
	if response and 'results' in response and response['results']:
		if len(response['results']) > 1:
			names = [item['name'] for item in response['results']]
			selection = xbmcgui.Dialog().select('Keyword', names)
			if selection > -1:
				return response['results'][selection]
		elif response['results']:
			return response['results'][0]
	else:
		return False

def get_set_id(set_name):
	set_name = set_name.replace('[', '').replace(']', '').replace('Kollektion', 'Collection')
	response = get_tmdb_data('search/collection?query=%s&language=%s&' % (Utils.url_quote(set_name.encode('utf-8')), xbmcaddon.Addon().getSetting('LanguageID')), 14)
	if 'results' in response and response['results']:
		return response['results'][0]['id']
	else:
		return ''

def sort_nested(data, sort_key, asc=True):
	# Helper to recursively find the sort_key in nested structures
	def find_key(obj):
		if isinstance(obj, dict):
			if sort_key in obj:
				return obj[sort_key]
			for value in obj.values():
				result = find_key(value)
				if result is not None:
					return result
		elif isinstance(obj, list):
			for item in obj:
				result = find_key(item)
				if result is not None:
					return result
		return None

	# Determine if input is a list or dict and sort accordingly
	if isinstance(data, dict):
		sorted_items = sorted(data.items(), key=lambda item: find_key(item[1]), reverse=not asc)
		return dict(sorted_items)
	elif isinstance(data, list):
		return sorted(data, key=lambda item: find_key(item), reverse=not asc)
	else:
		raise TypeError("Input must be a list or dictionary")

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


categories = get_vod_data(action= 'get_vod_categories' ,cache_days=1) 

xtreme_sport_categories = xbmcaddon.Addon().getSetting('xtreme_sport_categories')
bad_categories = [i for  i in xtreme_sport_categories.split(',')]
bad_category_ids = [cat['category_id']  for cat in categories  if any(bad.lower() in cat['category_name'].lower() for bad in bad_categories)]


def get_vod_allmovies(category = None, sort_by = None, order_by = None):
	#from resources.lib.TheMovieDB import get_vod_data
	if category == None:
		movies = get_vod_data(action= 'get_vod_streams' ,cache_days=1) 
	else:
		movies = get_vod_data(action= 'get_vod_streams&category_id=%s' % (str(category)) ,cache_days=1) 
	if order_by:
		if order_by == 'desc':
			order_bool = False
		elif order_by == 'asc':
			order_bool = True
	else:
		order_bool = False
	if sort_by == None:
		#movies = sort_nested(movies,'added',False)
		movies = sort_nested(movies,'added',order_bool)
	else:
		movies = sort_nested(movies,sort_by,order_bool)
	search_str = []
	for i in movies:
		if category == None:
			if str(i.get('category_id',0)) in [str(x) for x in bad_category_ids]:
				continue
		if i['name'][:7].lower() == 'movie: ':
			i['name'] = i['name'][7:]
		elif i['name'][:6].lower() == 'movie:':
			i['name'] = i['name'][6:]
		full_url = '%s%s/%s/%s/%s.%s' % (Utils.xtreme_codes_server_path,i['stream_type'],Utils.xtreme_codes_username,Utils.xtreme_codes_password,str(i['stream_id']),str(i['container_extension']))
		search_str.append({'type': 'movie','title':i['name'],'tmdb':i['tmdb'], 'full_url': full_url,'stream_id': i['stream_id'], 'stream_type': i['stream_type'],'stream_icon': i['stream_icon'], 'rating': i['rating'],'category_ids': i['category_ids']})
	#Utils.tools_log(i)
	#Utils.tools_log('get_vod_allmovies')
	return search_str

def get_vod_alltv(category = None, sort_by = None, order_by = None):
	#from resources.lib.TheMovieDB import get_vod_data
	if category == None:
		movies = get_vod_data(action= 'get_series' ,cache_days=1) 
	else:
		movies = get_vod_data(action= 'get_series&category_id=%s' % (str(category)) ,cache_days=1) 

	if order_by:
		if order_by == 'desc':
			order_bool = False
		elif order_by == 'asc':
			order_bool = True
	else:
		order_bool = False
	if sort_by == None:
		#movies = sort_nested(movies,'last_modified',False)
		movies = sort_nested(movies,'last_modified',order_bool)
	else:
		movies = sort_nested(movies,sort_by,order_bool)

	search_str = []
	for i in movies:
		#full_url = '%s%s/%s/%s/%s.%s' % (Utils.xtreme_codes_server_path,i['stream_type'],Utils.xtreme_codes_username,Utils.xtreme_codes_password,str(i['stream_id']),str(i['container_extension']))
		full_url = ''
		#Utils.tools_log(i)
		search_str.append({'type': 'tv','title':i['name'],'tmdb':i['tmdb'], 'full_url': full_url, 'series_id': i['series_id'],'stream_type': 'tv','stream_icon': i['cover'], 'rating': i['rating'],'category_ids': i['category_ids']})
	return search_str



def get_tmdb_data(url='', cache_days=14, folder='tmdb'):
	url = 'https://api.themoviedb.org/3/%sapi_key=%s' % (url, API_key)
	#xbmc.log(str(url)+'===>PHIL', level=xbmc.LOGINFO)
	return Utils.get_JSON_response(url, cache_days, folder)

def get_fanart_clearlogo(tmdb_id=None, media_type=None):
	fanart_clearlogos = xbmcaddon.Addon().getSetting('fanart_clearlogos')
	if fanart_clearlogos == 'false':
		clearlogo = ''
		return clearlogo
	if media_type !='tv' and media_type != 'movie':
		clearlogo = ''
		return clearlogo
	response = get_fanart_data(tmdb_id=tmdb_id,media_type=media_type)
	if media_type =='tv':
		try:
			for i in response['hdtvlogo']:
				if i['lang'] in ('en','00',''):
					clearlogo = i['url']
					break
		except: 
			try:
				for i in response['clearlogo']:
					if i['lang'] in ('en','00',''):
						clearlogo = i['url']
						break
			except: 
				pass
	if media_type =='movie':
		try:
			for i in response['hdmovielogo']:
				if i['lang'] in ('en','00',''):
					clearlogo = i['url']
					break
		except: 
			try:
				for i in response['clearlogo']:
					if i['lang'] in ('en','00',''):
						clearlogo = i['url']
						break
			except: 
				pass
	return clearlogo

def get_fanart_data(url='', tmdb_id=None, media_type=None, cache_days=14, folder='FanartTV'):
	fanart_api = fanart_api_key()
	import requests,json
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
	return Utils.get_JSON_response(url, cache_days, folder)



def get_company_data(company_id):
	response = get_tmdb_data('company/%s/movies?' % company_id, 30)
	if response and 'results' in response:
		return handle_tmdb_movies(response['results'])
	else:
		return []

def get_credit_info(credit_id):
	return get_tmdb_data('credit/%s?language=%s&' % (credit_id, xbmcaddon.Addon().getSetting('LanguageID')), 30)

def get_image_urls(poster=None, still=None, fanart=None, profile=None):
	images = {}
	if poster:
		images['poster'] = 'https://image.tmdb.org/t/p/w500' + poster
		images['poster_original'] = 'https://image.tmdb.org/t/p/original' + poster
		images['original'] = 'https://image.tmdb.org/t/p/original' + poster
		images['poster_small'] = 'https://image.tmdb.org/t/p/w342' + poster
		images['thumb'] = 'https://image.tmdb.org/t/p/w342' + poster
	if still:
		images['thumb'] = 'https://image.tmdb.org/t/p/w300' + still
		images['still'] = 'https://image.tmdb.org/t/p/w300' + still
		images['still_original'] = 'https://image.tmdb.org/t/p/original' + still
		images['still_small'] = 'https://image.tmdb.org/t/p/w185' + still
	if fanart:
		images['fanart'] = 'https://image.tmdb.org/t/p/w1280' + fanart
		images['fanart_original'] = 'https://image.tmdb.org/t/p/original' + fanart
		images['original'] = 'https://image.tmdb.org/t/p/original' + fanart
		images['fanart_small'] = 'https://image.tmdb.org/t/p/w780' + fanart
	if profile:
		images['poster'] = 'https://image.tmdb.org/t/p/w500' + profile
		images['poster_original'] = 'https://image.tmdb.org/t/p/original' + profile
		images['poster_small'] = 'https://image.tmdb.org/t/p/w342' + profile
		images['thumb'] = 'https://image.tmdb.org/t/p/w342' + profile
	return images

def get_movie_tmdb_id(imdb_id=None, name=None, dbid=None):
	if dbid and (int(dbid) > 0):
		movie_id = local_db.get_imdb_id_from_db('movie', dbid)
		movie_info = local_db.get_info_from_db('movie', dbid)
		try: year = movie_info['year']
		except: year = ''
		try: original_title = movie_info['originaltitle']
		except: original_title = ''
		if name:
			if original_title != '' and original_title != name:
				name = original_title
		Utils.log('IMDB Id from local DB: %s' % movie_id)
		response = get_tmdb_data('find/%s?external_source=imdb_id&language=%s&' % (movie_id, xbmcaddon.Addon().getSetting('LanguageID')), 30)
		if response['movie_results']:
			return response['movie_results'][0]['id']
		elif name:
			movie = get_movie_info(movie_label=name, year=year)
			if movie and movie.get('id'):
				return movie.get('id')
		else:
			Utils.notify('Could not find TMDb-id 1')
			return None
	elif imdb_id:
		response = get_tmdb_data('find/%s?external_source=imdb_id&language=%s&' % (imdb_id, xbmcaddon.Addon().getSetting('LanguageID')), 30)
		if 'movie_results' in response:
			if response['movie_results'] != None and len(response['movie_results']) > 0:
				try:
					return response['movie_results'][0]['id']
				except: 
					if name:
						movie = get_movie_info(movie_label=name, year=year)
						if movie and movie.get('id'):
							return movie.get('id')
					else:
						Utils.notify('Could not find TMDb-id 2')
						return None
			elif name:
				movie = get_movie_info(movie_label=name, year=year)
				if movie and movie.get('id'):
					return movie.get('id')
			else: 
				Utils.notify('Could not find TMDb-id 3')
				return None
	elif name:
		return search_media(name)
	else:
		Utils.notify('Could not find TMDb-id 4')
		return None


def get_show_tmdb_id(tvdb_id=None, db=None, imdb_id=None, source=None):
	if tvdb_id:
		id = tvdb_id
		db = 'tvdb_id'
	elif imdb_id:
		id = 'tt%s' % imdb_id
		id = id.replace('tttt','tt')
		db = 'imdb_id'
	response = get_tmdb_data('find/%s?external_source=%s&language=%s&' % (id, db, xbmcaddon.Addon().getSetting('LanguageID')), 30)
	if response:
		return response['tv_results'][0]['id']
	else:
		Utils.notify('TV Show info not found', time=5000, sound=False)
		return None

def get_trailer(movie_id):
	response = get_tmdb_data('movie/%s?append_to_response=videos,null,%s&language=%s&' % (movie_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID')), 30)
	if response and 'videos' in response and response['videos']['results']:
		return response['videos']['results'][0]['key']
	Utils.notify('Movie trailer not found', sound=False)
	return ''

def get_tvtrailer(tvshow_id):
	response = get_tmdb_data('tv/%s?append_to_response=videos,null,%s&language=%s&' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID')), 30)
	if response and 'videos' in response and response['videos']['results']:
		return response['videos']['results'][0]['key']
	Utils.notify('TV Show trailer not found', sound=False)
	return ''

def play_movie_trailer(id):
	trailer = get_trailer(id)
	xbmc.executebuiltin('PlayMedia(plugin://plugin.video.youtube/play/?video_id=%s,1)' % str(trailer))
	xbmc.executebuiltin('Dialog.Close(busydialog)')

def play_movie_trailer_fullscreen(id):
	trailer = get_trailer(id)
	xbmc.executebuiltin('PlayMedia(plugin://plugin.video.youtube/play/?video_id=%s)' % str(trailer))

def play_tv_trailer(id):
	trailer = get_tvtrailer(id)
	xbmc.executebuiltin('PlayMedia(plugin://plugin.video.youtube/play/?video_id=%s,1)' % str(trailer))
	xbmc.executebuiltin('Dialog.Close(busydialog)')

def play_tv_trailer_fullscreen(id):
	trailer = get_tvtrailer(id)
	xbmc.executebuiltin('PlayMedia(plugin://plugin.video.youtube/play/?video_id=%s)' % str(trailer))

def single_movie_info(movie_id=None, dbid=None, cache_time=14, notify = True):
	if not movie_id:
		return None
	session_str = ''
	response = get_tmdb_data('movie/%s?append_to_response=external_ids,recommendations,rating,alternative_titles&language=%s&%s' % (movie_id, xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
	#response = get_tmdb_data('movie/%s?append_to_response=alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,rating&include_image_language=en,null,%s&language=%s&%s' % (movie_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
	if not response and notify:
		Utils.notify('Could not get movie information', sound=False)
		return {}
	try: genres = [i['id'] for i in response['genres']]
	except KeyError: genres = []
	results = {
			'media_type': 'movie',
			'mediatype': 'movie',
			'adult': Utils.fetch(response,'adult'),
			'backdrop_path': Utils.fetch(response,'backdrop_path'),
			'genre_ids': genres,
			'id': Utils.fetch(response,'id'),
			'imdb_id': Utils.fetch(Utils.fetch(response, 'external_ids'), 'imdb_id'),
			'original_language': Utils.fetch(response,'original_language'),
			'original_title': Utils.fetch(response,'original_title'),
			'alternative_titles': response.get('alternative_titles',[]),
			'overview': Utils.fetch(response,'overview'),
			'similar': Utils.fetch(response,'recommendations'),
			'Rating': Utils.fetch(response, 'vote_average'),
			'Votes': Utils.fetch(response, 'vote_count'),
			'popularity': Utils.fetch(response,'popularity'),
			'poster_path': Utils.fetch(response,'poster_path'),
			'release_date': Utils.fetch(response,'release_date'),
			'title': Utils.fetch(response,'title'),
			'video': Utils.fetch(response,'video'),
			'vote_average': Utils.fetch(response,'vote_average'),
			'vote_count': Utils.fetch(response,'vote_count')
			}
	return results

def single_tvshow_info(tvshow_id=None, cache_time=7, dbid=None):
	if not tvshow_id:
		return None
	session_str = ''
	response = get_tmdb_data('tv/%s?append_to_response=external_ids,recommendations,rating,alternative_titles&language=%s&%s' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
	#response = get_tmdb_data('tv/%s?append_to_response=alternative_titles,content_ratings,credits,external_ids,images,keywords,rating,similar,translations,videos&language=%s&include_image_language=en,null,%s&%s' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
	if not response:
		return False
	genres = [i['id'] for i in response['genres']]
	alternative_titles =  [i['title'] for i in response['alternative_titles']['results']]
	if response['original_name'] == response['name'] and len(alternative_titles) > 0:
		response['original_name'] = alternative_titles[0]
	results = {
		'media_type': 'tv',
		'mediatype': 'tv',
		'backdrop_path': response['backdrop_path'],
		'first_air_date': response['first_air_date'],
		'genre_ids': genres,
		'id': response['id'],
		'imdb_id': Utils.fetch(Utils.fetch(response, 'external_ids'), 'imdb_id'),
		'name': response['name'],
		'title': response['name'],
		'origin_country': response['origin_country'],
		'original_language': response['original_language'],
		'original_name': response['original_name'],
		'alternative_titles': alternative_titles,
		'overview': response['overview'],
		'similar': response['recommendations'],
		'Rating': Utils.fetch(response, 'vote_average'),
		'Votes': Utils.fetch(response, 'vote_count'),
		'popularity': response['popularity'],
		'poster_path': response['poster_path'],
		'status': response['status'],
		'vote_average': response['vote_average'],
		'vote_count': response['vote_count']
		}
	return results

def extended_movie_info(movie_id=None, dbid=None, cache_time=14, notify=True):
	if not movie_id:
		return None
	session_str = ''
	#response = get_tmdb_data('movie/%s?append_to_response=alternative_titles,credits,images,keywords,releases,videos,translations,recommendations,reviews,rating&include_image_language=en,null,%s&language=%s&%s' % (movie_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
	response = get_tmdb_data('movie/%s?append_to_response=alternative_titles,credits,images,keywords,releases,videos,recommendations,reviews,rating&include_image_language=en,null,%s&language=%s&%s' % (movie_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
	if not response and notify:
		Utils.notify('Could not get movie information', sound=False)
		return {}
	mpaa = ''
	set_name = ''
	set_id = ''
	genres = [i['name'] for i in response['genres']]
	Studio = [i['name'] for i in response['production_companies']]
	authors = [i['name'] for i in response['credits']['crew'] if i['department'] == 'Writing']
	directors = [i['name'] for i in response['credits']['crew'] if i['department'] == 'Directing']
	us_cert = Utils.dictfind(response['releases']['countries'], 'iso_3166_1', 'US')
	if us_cert:
		mpaa = us_cert['certification']
	elif response['releases']['countries']:
		mpaa = response['releases']['countries'][0]['certification']
	movie_set = Utils.fetch(response, 'belongs_to_collection')
	if movie_set:
		set_name = Utils.fetch(movie_set, 'name')
		set_id = Utils.fetch(movie_set, 'id')
	artwork = get_image_urls(poster=response.get('poster_path'), fanart=response.get('backdrop_path'))
	movie = {
		'media_type': 'movie',
		'mediatype': 'movie',
		'title': Utils.fetch(response, 'title'),
		'Label': Utils.fetch(response, 'title'),
		'Tagline': Utils.fetch(response, 'tagline'),
		'duration': Utils.fetch(response, 'runtime'),
		'duration(h)': Utils.format_time(Utils.fetch(response, 'runtime'), 'h'),
		'duration(m)': Utils.format_time(Utils.fetch(response, 'runtime'), 'm'),
		'duration(hm)': Utils.format_time(Utils.fetch(response, 'runtime')),
		'mpaa': mpaa,
		'Director': ' / '.join(directors),
		'writer': ' / '.join(authors),
		'Budget': Utils.millify(Utils.fetch(response, 'budget')),
		'Revenue': Utils.millify(Utils.fetch(response, 'revenue')),
		'Homepage': Utils.fetch(response, 'homepage'),
		'Set': set_name, 'SetId': set_id,
		'id': Utils.fetch(response, 'id'),
		'tmdb_id': Utils.fetch(response, 'id'),
		'imdb_id': Utils.fetch(response, 'imdb_id'),
		'Plot': Utils.clean_text(Utils.fetch(response, 'overview')),
		'OriginalTitle': Utils.fetch(response, 'original_title'),
		'Country': Utils.fetch(response, 'original_language'),
		'genre': ' / '.join(genres),
		'Rating': Utils.fetch(response, 'vote_average'),
		'Votes': Utils.fetch(response, 'vote_count'),
		'Adult': str(Utils.fetch(response, 'adult')),
		'Popularity': Utils.fetch(response, 'popularity'),
		'Status': translate_status(Utils.fetch(response, 'status')),
		'release_date': Utils.fetch(response, 'release_date'),
		'Premiered': Utils.fetch(response, 'release_date'),
		'Studio': ' / '.join(Studio),
		'year': Utils.get_year(Utils.fetch(response, 'release_date')),
		'path': 'plugin://'+str(addon_ID())+'?info='+str(addon_ID_short())+'&&id=%s' % str(movie_id),
		'trailer': 'plugin://'+str(addon_ID())+'?info=playtrailer&&id=%s' % str(movie_id)
		}
	movie.update(artwork)
	videos = handle_tmdb_videos(response['videos']['results']) if 'videos' in response else []
	if dbid:
		local_item = local_db.get_movie_from_db(dbid)
		movie.update(local_item)
	else:
		movie = local_db.merge_with_local_movie_info([movie])[0]
	movie['Rating'] = Utils.fetch(response, 'vote_average')
	pop_list = []
	for idx, i in enumerate(response['recommendations']['results']):
		if int(i.get('vote_count',0)) < 250:
			pop_list.append(idx)
	for i in reversed(pop_list):
		response['recommendations']['results'].pop(i)

	listitems = {
		'actors': handle_tmdb_people(response['credits']['cast']),
		'similar': handle_tmdb_movies(response['recommendations']['results']),
		'studios': handle_tmdb_misc(response['production_companies']),
		'releases': handle_tmdb_misc(response['releases']['countries']),
		'crew': handle_tmdb_people(response['credits']['crew']),
		'genres': handle_tmdb_misc(response['genres']),
		'keywords': handle_tmdb_misc(response['keywords']['keywords']),
		'reviews': handle_tmdb_misc(response['reviews']['results']),
		'videos': videos,
		'images': handle_tmdb_images(response['images']['posters']),
		'backdrops': handle_tmdb_images(response['images']['backdrops'])
		}
	return (movie, listitems)

def extended_tvshow_info(tvshow_id=None, cache_time=7, dbid=None):
	if not tvshow_id:
		return None
	session_str = ''
	#response = get_tmdb_data('tv/%s?append_to_response=alternative_titles,content_ratings,credits,external_ids,images,keywords,rating,recommendations,translations,videos&language=%s&include_image_language=en,null,%s&%s' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
	response = get_tmdb_data('tv/%s?append_to_response=alternative_titles,content_ratings,credits,external_ids,images,keywords,rating,recommendations,videos&language=%s&include_image_language=en,null,%s&%s' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
	if not response:
		return False
	videos = handle_tmdb_videos(response['videos']['results']) if 'videos' in response else []
	tmdb_id = Utils.fetch(response, 'id')
	external_ids = Utils.fetch(response, 'external_ids')
	if external_ids:
		imdb_id = Utils.fetch(external_ids, 'imdb_id')
		freebase_id = Utils.fetch(external_ids, 'freebase_id')
		tvdb_id = Utils.fetch(external_ids, 'tvdb_id')
		tvrage_id = Utils.fetch(external_ids, 'tvrage_id')
	artwork = get_image_urls(poster=response.get('poster_path'), fanart=response.get('backdrop_path'))
	if len(response.get('episode_run_time', -1)) > 1:
		duration = '%i - %i' % (min(response['episode_run_time']), max(response['episode_run_time']))
	elif len(response.get('episode_run_time', -1)) == 1:
		duration = '%i' % response['episode_run_time'][0]
	else:
		duration = ''
	us_cert = Utils.dictfind(response['content_ratings']['results'], 'iso_3166_1', 'US')
	if us_cert:
		mpaa = us_cert['rating']
	elif response['content_ratings']['results']:
		mpaa = response['content_ratings']['results'][0]['rating']
	else:
		mpaa = ''
	genres = [item['name'] for item in response['genres']]
	tvshow = {
		'title': Utils.fetch(response, 'name'),
		'TVShowTitle': Utils.fetch(response, 'name'),
		'OriginalTitle': Utils.fetch(response, 'original_name'),
		'duration': duration,
		'duration(h)': Utils.format_time(duration, 'h'),
		'duration(m)': Utils.format_time(duration, 'm'),
		'id': tmdb_id,
		'tmdb_id': tmdb_id,
		'imdb_id': imdb_id,
		'freebase_id': freebase_id,
		'tvdb_id': tvdb_id,
		'tvrage_id': tvrage_id,
		'mpaa': mpaa,
		'genre': ' / '.join(genres),
		'credit_id': Utils.fetch(response, 'credit_id'),
		'Plot': Utils.clean_text(Utils.fetch(response, 'overview')),
		'year': Utils.get_year(Utils.fetch(response, 'first_air_date')),
		'media_type': 'tv',
		'mediatype': 'tvshow',
		'Popularity': Utils.fetch(response, 'popularity'),
		'Rating': Utils.fetch(response, 'vote_average'),
		'country': Utils.fetch(response, 'original_language'),
		'User_Rating': str(Utils.fetch(response, 'rating')),
		'Votes': Utils.fetch(response, 'vote_count'),
		'Status': translate_status(Utils.fetch(response, 'status')),
		'path': 'plugin://'+str(addon_ID())+'?info=extendedtvinfo&&id=%s' % str(tvshow_id),
		'trailer': 'plugin://'+str(addon_ID())+'?info=playtvtrailer&&id=%s' % str(tvshow_id),
		'ShowType': Utils.fetch(response, 'type'),
		'homepage': Utils.fetch(response, 'homepage'),
		'last_air_date': Utils.fetch(response, 'last_air_date'),
		'first_air_date': Utils.fetch(response, 'first_air_date'),
		'TotalEpisodes': Utils.fetch(response, 'number_of_episodes'),
		'TotalSeasons': Utils.fetch(response, 'number_of_seasons'),
		'in_production': Utils.fetch(response, 'in_production'),
		'Release_Date': Utils.fetch(response, 'first_air_date'),
		'Premiered': Utils.fetch(response, 'first_air_date')
		}
	tvshow.update(artwork)
	if dbid:
		local_item = local_db.get_tvshow_from_db(dbid)
		tvshow.update(local_item)
	else:
		tvshow = local_db.merge_with_local_tvshow_info([tvshow])[0]
	tvshow['Rating'] = Utils.fetch(response, 'vote_average')

	pop_list = []
	for idx, i in enumerate(response['recommendations']['results']):
		if int(i.get('vote_count',0)) < 150:
			pop_list.append(idx)
	for i in reversed(pop_list):
		response['recommendations']['results'].pop(i)

	listitems = {
		'actors': handle_tmdb_people(response['credits']['cast']),
		'similar': handle_tmdb_tvshows(response['recommendations']['results']),
		'studios': handle_tmdb_misc(response['production_companies']),
		'networks': handle_tmdb_misc(response['networks']),
		'certifications': handle_tmdb_misc(response['content_ratings']['results']),
		'crew': handle_tmdb_people(response['credits']['crew']),
		'genres': handle_tmdb_misc(response['genres']),
		'keywords': handle_tmdb_misc(response['keywords']['results']),
		'videos': videos,
		'seasons': handle_tmdb_seasons(response['seasons']),
		'images': handle_tmdb_images(response['images']['posters']),
		'backdrops': handle_tmdb_images(response['images']['backdrops'])
		}
	return (tvshow, listitems)

def extended_season_info(tvshow_id, season_number):
	if not tvshow_id or not season_number:
		return None
	session_str = ''
	#tvshow = get_tmdb_data('tv/%s?append_to_response=alternative_titles,content_ratings,credits,external_ids,images,keywords,rating,similar,translations,videos&language=%s&include_image_language=en,null,%s&%s' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), 99999)
	tvshow = get_tmdb_data('tv/%s?append_to_response=alternative_titles,content_ratings,credits,external_ids,images,keywords,rating,similar,videos&language=%s&include_image_language=en,null,%s&%s' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), 99999)
	response = get_tmdb_data('tv/%s/season/%s?append_to_response=videos,images,external_ids,credits&language=%s&include_image_language=en,null,%s&' % (tvshow_id, season_number, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID')), 7)
	dbid = Utils.fetch(tvshow, 'dbid')
	tmdb_id = Utils.fetch(tvshow, 'id')
	external_ids = Utils.fetch(tvshow, 'external_ids')
	year = Utils.get_year(Utils.fetch(tvshow, 'first_air_date'))
	if external_ids:
		imdb_id = Utils.fetch(external_ids, 'imdb_id')
		freebase_id = Utils.fetch(external_ids, 'freebase_id')
		tvdb_id = Utils.fetch(external_ids, 'tvdb_id')
		tvrage_id = Utils.fetch(external_ids, 'tvrage_id')
	if not response:
		Utils.notify('Could not find season info')
		return None
	if response.get('name', False):
		title = response['name']
	else:
		title = 'Specials' if season_number == '0' else 'Season %s' % season_number
	season = {
		'SeasonDescription': Utils.clean_text(response['overview']),
		'Plot': Utils.clean_text(response['overview']),
		'TVShowTitle': Utils.fetch(tvshow, 'name'),
		'title': title,
		'dbid': dbid,
		'imdb_id': imdb_id,
		'tmdb_id': tmdb_id,
		'tvdb_id': tvdb_id,
		'tvrage_id': tvrage_id,
		'year': year,
		'season': season_number,
		'path': 'plugin://'+str(addon_ID())+'?info=seasoninfo&tvshow=%s&season=%s' % (Utils.fetch(tvshow, 'name'), season_number),
		'release_date': response['air_date'],
		'AirDate': response['air_date']
		}
	artwork = get_image_urls(poster=response.get('poster_path'))
	season.update(artwork)
	videos = handle_tmdb_videos(response['videos']['results']) if 'videos' in response else []
	listitems = {
		'actors': handle_tmdb_people(response['credits']['cast']),
		'crew': handle_tmdb_people(response['credits']['crew']),
		'videos': videos,
		'episodes': handle_tmdb_episodes(response['episodes']),
		'images': handle_tmdb_images(response['images']['posters'])
		}
	return (season, listitems)

def extended_episode_info(tvshow_id, season, episode, cache_time=7):
	if not tvshow_id or not episode:
		return None
	if not season:
		season = 0
	session_str = ''
	#tvshow = get_tmdb_data('tv/%s?append_to_response=alternative_titles,content_ratings,credits,external_ids,images,keywords,rating,similar,translations,videos&language=%s&include_image_language=en,null,%s&%s' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), 99999)
	tvshow = get_tmdb_data('tv/%s?append_to_response=alternative_titles,content_ratings,credits,external_ids,images,keywords,rating,similar,videos&language=%s&include_image_language=en,null,%s&%s' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), 99999)
	response = get_tmdb_data('tv/%s/season/%s/episode/%s?append_to_response=credits,runtime,external_ids,images,rating,videos&language=%s&include_image_language=en,null,%s&%s&' % (tvshow_id, season, episode, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
	tmdb_id = Utils.fetch(tvshow, 'id')
	TVShowTitle = Utils.fetch(tvshow, 'name')
	external_ids = Utils.fetch(tvshow, 'external_ids')
	year = Utils.get_year(Utils.fetch(tvshow, 'first_air_date')),
	if external_ids:
		imdb_id = Utils.fetch(external_ids, 'imdb_id')
		freebase_id = Utils.fetch(external_ids, 'freebase_id')
		tvdb_id = Utils.fetch(external_ids, 'tvdb_id')
		tvrage_id = Utils.fetch(external_ids, 'tvrage_id')
	videos = handle_tmdb_videos(response['videos']['results']) if 'videos' in response else []
	try:
		actors = handle_tmdb_people(response['credits']['cast'])
	except:
		actors = []
	try:
		crew = handle_tmdb_people(response['credits']['crew'])
	except:
		crew = []
	try:
		guest_stars = handle_tmdb_people(response['credits']['guest_stars'])
	except:
		guest_stars = []
	try:
		images = handle_tmdb_images(response['images']['stills'])
	except:
		images = []
	try: overview = Utils.clean_text(response['overview'])
	except KeyError: overview = ''
	try: runtime = response['runtime']
	except KeyError: runtime = None
	answer = {
		'SeasonDescription': overview,
		'Plot': overview,
		'TVShowTitle': TVShowTitle,
		'tvshow_id': tmdb_id,
		'tvdb_id': tvdb_id,
		'actors': actors,
		'path': 'plugin://'+str(addon_ID())+'?info=extendedepisodeinfo&tvshow_id=%s&season=%s&episode=%s' % (tvshow_id, season, episode),
		'crew': crew,
		'runtime': runtime,
		'guest_stars': guest_stars,
		'videos': videos,
		'images': images
		}
	#response = {'status_code': 7, 'status_message': 'Invalid API key: You must be granted a valid key.', 'success': False}
	ep = (handle_tmdb_episodes([response])[0], answer)
	ep[0]['poster'] = 'https://image.tmdb.org/t/p/w342' + tvshow['poster_path']
	ep[0]['thumb'] = 'https://image.tmdb.org/t/p/w342' + tvshow['poster_path']
	try: 
		ep[0]['fanart'] = ep[0]['still_original']
	except: 
		ep[0]['fanart'] = 'https://image.tmdb.org/t/p/w342' + tvshow['backdrop_path']
		#xbmc.log(str(ep[0])+'===>PHIL', level=xbmc.LOGINFO)
		#xbmc.log(str(tvshow)+'===>PHIL', level=xbmc.LOGINFO)
		pass
	ep[0]['TVShowTitle'] = TVShowTitle
	ep[0]['status'] = tvshow['status']
	#xbmc.log(str(response)+'===>get_trakt_playback', level=xbmc.LOGINFO)
	#xbmc.log(str(tvshow)+'===>get_trakt_playback', level=xbmc.LOGINFO)
	if ep[0]['episode'] == '':
		season_dict = extended_season_info(tvshow_id, season)
		ep[1]['actors'] = season_dict[1]['actors']
		ep[1]['crew'] = season_dict[1]['crew']
		#ep[1]['guest_stars'] = season[1]['guest_stars']
		ep[0]['season'] = int(season)
		ep[0]['episode'] = int(episode)
		ep[0]['Plot'] = season_dict[1]['episodes'][int(episode)-1]['Description']
		ep[0]['Description'] = season_dict[1]['episodes'][int(episode)-1]['Description']
		ep[0]['Votes'] = season_dict[1]['episodes'][int(episode)-1]['Votes']
		ep[0]['Rating'] = season_dict[1]['episodes'][int(episode)-1]['Rating']
		ep[0]['id'] = season_dict[1]['episodes'][int(episode)-1]['id']
		ep[0]['production_code'] = season_dict[1]['episodes'][int(episode)-1]['production_code']
		ep[0]['release_date'] = season_dict[1]['episodes'][int(episode)-1]['release_date']
		ep[0]['title'] = season_dict[1]['episodes'][int(episode)-1]['title']
		ep[0]['still'] = season_dict[1]['episodes'][int(episode)-1]['still'] 
		ep[0]['still_original'] = season_dict[1]['episodes'][int(episode)-1]['still_original'] 
		ep[0]['still_small'] = season_dict[1]['episodes'][int(episode)-1]['still_small'] 
		ep[0]['thumb'] = season_dict[1]['episodes'][int(episode)-1]['thumb'] 
		ep[0]['poster'] = 'https://image.tmdb.org/t/p/w342/' + tvshow['poster_path']
		ep[1]['images'] = []
		ep[1]['images'].append({'aspectratio': 1.778,
			'iso_639_1': None,
			'original': season_dict[1]['episodes'][int(episode)-1]['still_original'] ,
			'poster': season_dict[1]['episodes'][int(episode)-1]['still'],
			'poster_original': season_dict[1]['episodes'][int(episode)-1]['still_original'],
			'poster_small': season_dict[1]['episodes'][int(episode)-1]['still_small'], 
			'thumb': season_dict[1]['episodes'][int(episode)-1]['thumb'],
			'vote_average': 0.0})
	#return (handle_tmdb_episodes([response])[0], answer)
	ep[0]['year'] = ep[0]['release_date'][:4]
	return ep

def extended_actor_info(actor_id):
	if not actor_id:
		return None
	response = get_tmdb_data('person/%s?append_to_response=tv_credits,movie_credits,combined_credits,images,tagged_images&' % actor_id, 1)
	tagged_images = []
	if 'tagged_images' in response:
		tagged_images = handle_tmdb_tagged_images(response['tagged_images']['results'])
	listitems = {
		'movie_roles': handle_tmdb_movies(response['movie_credits']['cast']),
		'tvshow_roles': handle_tmdb_tvshows(response['tv_credits']['cast']),
		'movie_crew_roles': handle_tmdb_movies(response['movie_credits']['crew']),
		'tvshow_crew_roles': handle_tmdb_tvshows(response['tv_credits']['crew']),
		'tagged_images': tagged_images,
		'images': handle_tmdb_images(response['images']['profiles'])
		}
	info = handle_tmdb_people([response])[0]
	info['DBMovies'] = str(len([d for d in listitems['movie_roles'] if 'dbid' in d]))
	return (info, listitems)

def translate_status(status_string):
	translations = {
		'released': 'Released',
		'post production': 'Post production',
		'in production': 'In production',
		'ended': 'Ended',
		'returning series': 'Continuing',
		'planned': 'Planned'
		}
	if status_string.lower() in translations:
		return translations[status_string.lower()]
	else:
		return status_string

def get_keywords(movie_id):
	response = get_tmdb_data('movie/%s?append_to_response=alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,rating&include_image_language=en,null,%s&language=%s&' % (movie_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID')), 30)
	keywords = []
	if 'keywords' in response:
		for keyword in response['keywords']['keywords']:
			keyword_dict = {
				'id': Utils.fetch(keyword, 'id'),
				'name': keyword['name']
				}
			keywords.append(keyword_dict)
	return keywords

def get_tmdb_shows(tvshow_type):
	response = get_tmdb_data('tv/%s?language=%s&' % (tvshow_type, xbmcaddon.Addon().getSetting('LanguageID')), 0.3)
	if 'results' in response:
		return handle_tmdb_tvshows(response['results'], False, None)
	else:
		return []

def get_tmdb_movies(movie_type):
	response = get_tmdb_data('movie/%s?language=%s&' % (movie_type, xbmcaddon.Addon().getSetting('LanguageID')), 0.3)
	if 'results' in response:
		return handle_tmdb_movies(response['results'], False, None)
	else:
		return []

def get_set_movies(set_id):
	response = get_tmdb_data('collection/%s?language=%s&append_to_response=images&include_image_language=en,null,%s&' % (set_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID')), 14)
	if response['parts'] == []:
		response2 = get_tmdb_data('collection/%s?' % (set_id), 14)
		response['parts'] = response2['parts']
	if response['parts'] == []:
		response2 = get_tmdb_data('collection/%s?&language=NULL&' % (set_id), 14)
		response['parts'] = response2['parts']
	if response:
		artwork = get_image_urls(poster=response.get('poster_path'), fanart=response.get('backdrop_path'))
		info = {
			'label': response['name'],
			'overview': response['overview'],
			'id': response['id']
			}
		info.update(artwork)
		return handle_tmdb_movies(response.get('parts', [])), info
	else:
		return [], {}

def get_imdb_language(imdb_id=None, cache_days=14, folder='IMDB'):

	import time, hashlib, xbmcvfs, os
	import re, json, requests, html
	
	imdb_url = 'https://www.imdb.com/title/' + str(imdb_id)
	url = imdb_url + '/get_imdb_language'
	imdb_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
	
	now = time.time()
	url = url.encode('utf-8')
	hashed_url = hashlib.md5(url).hexdigest()
	cache_path = xbmcvfs.translatePath(os.path.join(Utils.ADDON_DATA_PATH, folder)) if folder else xbmcvfs.translatePath(os.path.join(Utils.ADDON_DATA_PATH))
	cache_seconds = int(cache_days * 86400.0)
	#if not cache_days:
	#	xbmcgui.Window(10000).clearProperty(hashed_url)
	#	xbmcgui.Window(10000).clearProperty('%s_timestamp' % hashed_url)
	#prop_time = xbmcgui.Window(10000).getProperty('%s_timestamp' % hashed_url)
	#if prop_time and now - float(prop_time) < cache_seconds:
	#	try:
	#		prop = json.loads(xbmcgui.Window(10000).getProperty(hashed_url))
	#		if prop:
	#			return prop
	#	except Exception as e:
	#		pass
	path = os.path.join(cache_path, '%s.txt' % hashed_url)
	try: 
		db_result, expired_db_result = Utils.query_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder, headers=imdb_header)
	except:
		db_result, expired_db_result = None, None
	if db_result:
		return db_result
	else:
	#if xbmcvfs.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
	#	results = Utils.read_from_file(path)
	#	if not results:
	#		return []
	#	#xbmcgui.Window(10000).setProperty('%s_timestamp' % hashed_url, str(now))
	#	#xbmcgui.Window(10000).setProperty(hashed_url, json.dumps(results))
	#	return results
	#else:
		imdb_response = requests.get(imdb_url, headers=imdb_header)
		details_section = imdb_response.text.split('<span>Details</span>')[1].split('</section>')[0]
		language_list = []
		for i in details_section.split('primary_language='):
			try: language_list.append(i.split('ref_=tt_dt_ln">')[1].split('</a>')[0])
			except: continue
		
		
		country = details_section.split('?country_of_origin=')[1].split('&amp;')[0]
		
		results = language_list
		if country == 'US' or country == 'UK' and results[1] == 'English':
			results[0] = 'English'

	#Utils.write_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder,cache_val=results)
	#if not results:
	#	return []
	#else:
	#	return results

	if not results or len(results) == 0:
		if expired_db_result == None:
			return []
		if len(expired_db_result) > 0:
			Utils.write_db(connection=db_con,url=url, cache_days=0.25, folder=folder,cache_val=expired_db_result)
			return expired_db_result
		return []
	else:
		Utils.write_db(connection=db_con,url=url, cache_days=cache_days, folder=folder,cache_val=results)
	return results

def get_trakt_playback(trakt_type=None):
	import urllib.parse
	from datetime import datetime
	from datetime import timedelta
	from resources.lib.library import get_trakt_data
	date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
	now = datetime.strftime(datetime.now() + timedelta(days=1), date_format)
	year_minus_one = datetime.strftime(datetime.now() - timedelta(days=1*180), date_format)
	if trakt_type == 'tv':
		url = 'https://api.trakt.tv/sync/playback/episodes?start_at=%s&end_at=%s' % (urllib.parse.quote(year_minus_one),urllib.parse.quote(now))
		response = get_trakt_data(url=url, cache_days=0.0001, folder='Trakt')
		#xbmc.log(str(response)+'===>get_trakt_playback', level=xbmc.LOGINFO)
		return response
	else:
		url = 'https://api.trakt.tv/sync/playback/movies?start_at=%s&end_at=%s' % (urllib.parse.quote(year_minus_one),urllib.parse.quote(now))
		response = get_trakt_data(url=url, cache_days=0.0001, folder='Trakt')
		#xbmc.log(str(response)+'===>get_trakt_playback', level=xbmc.LOGINFO)
		return response

def update_trakt_playback(trakt_type=None,tmdb_id=None,episode=None,season=None):
	from resources.lib.library import trak_auth
	import requests
	if trakt_type == 'tv':
		response = get_trakt_playback('tv')
		item_id = tmdb_id
		episode = str(episode)
		season = str(season)
		DBTYPE = 'episode'
	else:
		response = get_trakt_playback('movie')
		item_id = tmdb_id
		DBTYPE = 'movie'
	for i in response:
		if DBTYPE == 'episode':
			if str(i['show']['ids']['tmdb']) == str(item_id):
				if str(i['episode']['number']) == str(episode) and str(i['episode']['season']) == str(season):
					play_id = i['id']
					url = 'https://api.trakt.tv/sync/playback/' + str(play_id)
					response = requests.delete(url, headers=trak_auth())
		else:
			if str(i['movie']['ids']['tmdb']) == str(item_id):
				play_id = i['id']
				url = 'https://api.trakt.tv/sync/playback/' + str(play_id)
				response = requests.delete(url, headers=trak_auth())	
	return response

def get_watching_user():
	from resources.lib.library import get_trakt_data
	trakt_slug = xbmcaddon.Addon().getSetting('trakt_slug')
	url = 'https://api.trakt.tv/users/%s/watching' % str(trakt_slug)
	response = get_trakt_data(url=url, cache_days=0.0001, folder='Trakt')
	return response


def get_person_movies(person_id):
	response = get_tmdb_data('person/%s/credits?language=%s&' % (person_id, xbmcaddon.Addon().getSetting('LanguageID')), 14)
	if 'crew' in response:
		return handle_tmdb_movies(response['crew'])
	else:
		return []

def get_person(person_id):
	response = get_tmdb_data('person/%s?language=%s&append_to_response=combined_credits&' % (person_id, xbmcaddon.Addon().getSetting('LanguageID')), 14)
	listitems = handle_tmdb_multi_search(response['combined_credits']['cast'])
	listitems += handle_tmdb_multi_search(response['combined_credits']['crew'])
	return listitems

def search_media(media_name=None, year='', media_type='movie'):
	search_query = Utils.url_quote('%s %s' % (media_name, year))
	if not search_query:
		return None
	response = get_tmdb_data('search/%s?query=%s&language=%s&include_adult=%s&' % (media_type, search_query, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('include_adults')), 1)
	if not response == 'Empty':
		for item in response['results']:
			if item['id']:
				return item['id']
	return None

def get_imdb_id_from_movie_id(movie_id=None, cache_time=14):
	if not movie_id:
		return None
	session_str = ''
	response = get_tmdb_data('movie/%s?&language=%s,null,%s&%s' % (movie_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
	if not response:
		return False
	imdb_id = Utils.fetch(response, 'imdb_id')
	return imdb_id

def get_tvshow_ids(tvshow_id=None, cache_time=14):
	if not tvshow_id:
		return None
	session_str = ''
	response = get_tmdb_data('tv/%s?append_to_response=external_ids&language=%s&include_image_language=en,null,%s&%s' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
	if not response:
		return False
	external_ids = Utils.fetch(response, 'external_ids')
	return external_ids
