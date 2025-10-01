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
		listitem = {
			'title': Utils.fetch(movie, 'title'),
			'Label': Utils.fetch(movie, 'title'),
			'OriginalTitle': original_title,
			'id': tmdb_id,
			'imdb_id': Utils.fetch(movie, 'imdb_id'),
			'path': path,
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
	movies = local_db.merge_with_local_movie_info(movies, local_first, sortkey)
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

def get_tmdb_data(url='', cache_days=14, folder='TheMovieDB'):
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

def get_tastedive_shows_items(show_name: str, imdb_id: str) -> list:
	import requests
	search_url = "https://tastedive.com/api/search"
	search_params = {
		"query": show_name,
		"take": "9",
		"page": "1",
		"searchCategory": "default",
		"types": "urn:entity:tv_show"
	}
	headers = {
		"accept": "application/json, text/plain, */*",
		"referer": "https://tastedive.com/",
		"user-agent": "Mozilla/5.0"
	}
	cookies = {
		"__Host-next-auth.csrf-token": "1a7f094e800bdcd2074e094cbab6696019fd0de132a31c5d5544dddc40f0f273|3b43c936976ca42110e7e4811d23fa0c735b42e7f2a9b59d7c32b7382fe8fef9",
		"__Secure-next-auth.callback-url": "https://tastedive.com"
	}

	search_response = requests.get(search_url, headers=headers, params=search_params, cookies=cookies)
	search_data = search_response.json()

	# Step 2: Find the correct entity by IMDb ID
	entity_id = None
	for result in search_data.get("results", []):
		external = result.get("properties", {}).get("external", {})
		if external.get("imdb", {}).get("id") == imdb_id:
			entity_id = result.get("entity_id")
			#print(result)
			break
	if not entity_id:
		raise ValueError("IMDb ID not found in search results.")

	# Step 3: Use entity ID to get similar movies

	recs_url = "https://tastedive.com/api/getRecsByCategory"

	recs_params = {
		"page": "1",
		"entityId": entity_id,
		"category": "shows",
		"limit": "18"
	}

	recs_headers = {
		"accept": "*/*",
		"accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
		"priority": "u=1, i",
		"referer": "https://tastedive.com/",
		"sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
		"sec-ch-ua-mobile": "?0",
		"sec-ch-ua-platform": '"Windows"',
		"sec-fetch-dest": "empty",
		"sec-fetch-mode": "cors",
		"sec-fetch-site": "same-origin",
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
	}

	recs_response = requests.get(recs_url, headers=recs_headers, params=recs_params, cookies=cookies)
	#print(recs_response)
	recs_data = recs_response.json()
	#print(recs_data)

	# Step 4: Extract IMDb IDs and movie names
	similar_shows = []
	for item in recs_data:
		similar_shows.append((item.get("properties", {}).get("release_year", ''), item.get("entityName"), item.get("slug")))

	recs_params = {
		"page": "2",
		"entityId": entity_id,
		"category": "shows",
		"limit": "18"
	}
	recs_response = requests.get(recs_url, headers=recs_headers, params=recs_params, cookies=cookies)
	#print(recs_response)
	recs_data = recs_response.json()
	for item in recs_data:
		similar_shows.append((item.get("properties", {}).get("release_year", ''), item.get("entityName"), item.get("slug")))

	return similar_shows

def get_tastedive_shows(item_id, cache_days=14, folder='TasteDive'):
	import time, hashlib, xbmcvfs, os
	import re, json, requests, html

	from urllib.parse import quote_plus
	url = 'https://tastedive.com/%s/%s/api_taste' % (item_id,'show')
	show_info = single_tvshow_info(tvshow_id=item_id, cache_time=7 )

	now = time.time()
	url = url.encode('utf-8')
	hashed_url = hashlib.md5(url).hexdigest()

	cache_path = xbmcvfs.translatePath(os.path.join(Utils.ADDON_DATA_PATH, folder)) if folder else xbmcvfs.translatePath(os.path.join(Utils.ADDON_DATA_PATH))
	cache_seconds = int(cache_days * 86400.0)
	path = os.path.join(cache_path, '%s.txt' % hashed_url)

	try: 
		db_result = Utils.query_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder, headers=None)
	except:
		db_result = None
	db_result = None
	if db_result:
		return db_result
	else:
		response = get_tastedive_shows_items(show_name = show_info['title'], imdb_id = show_info['imdb_id'])
		results = []
		for i in response:
			show_response = get_tvshow_info(tvshow_label=i[1], year=i[0],use_dialog=False)
			if show_response:
				#results.append(show_response['id'])
				results.append({'name': show_response['original_name'], 'year': show_response['first_air_date'][:4], 'media_type':  'tv', 'item_id': show_response['id']})

	Utils.write_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder,cache_val=results)
	if not results:
		return []
	else:
		return results

def get_tastedive_movies_items(movie_name: str, imdb_id: str) -> list:
	import requests
	"""
	Given a movie name and IMDb ID, this function:
	1. Searches Tastedive for the movie.
	2. Identifies the correct entity using the IMDb ID.
	3. Uses the entity ID to query similar movies.
	4. Returns a list of tuples with IMDb IDs and movie names of similar items.
	"""
	# Step 1: Search for the movie
	search_url = "https://tastedive.com/api/search"
	search_params = {
		"query": movie_name,
		"take": "9",
		"page": "1",
		"searchCategory": "default",
		"types": "urn:entity:movie"
	}
	headers = {
		"accept": "application/json, text/plain, */*",
		"referer": "https://tastedive.com/",
		"user-agent": "Mozilla/5.0"
	}
	cookies = {
		"__Host-next-auth.csrf-token": "1a7f094e800bdcd2074e094cbab6696019fd0de132a31c5d5544dddc40f0f273|3b43c936976ca42110e7e4811d23fa0c735b42e7f2a9b59d7c32b7382fe8fef9",
		"__Secure-next-auth.callback-url": "https://tastedive.com"
	}

	search_response = requests.get(search_url, headers=headers, params=search_params, cookies=cookies)
	search_data = search_response.json()

	# Step 2: Find the correct entity by IMDb ID
	entity_id = None
	for result in search_data.get("results", []):
		external = result.get("properties", {}).get("external", {})
		if external.get("imdb", {}).get("id") == imdb_id:
			entity_id = result.get("entity_id")
			#print(result)
			break
	if not entity_id:
		raise ValueError("IMDb ID not found in search results.")

	# Step 3: Use entity ID to get similar movies

	recs_url = "https://tastedive.com/api/getRecsByCategory"

	recs_params = {
		"page": "1",
		"entityId": entity_id,
		"category": "movies",
		"limit": "18"
	}

	recs_headers = {
		"accept": "*/*",
		"accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
		"priority": "u=1, i",
		"referer": "https://tastedive.com/",
		"sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
		"sec-ch-ua-mobile": "?0",
		"sec-ch-ua-platform": '"Windows"',
		"sec-fetch-dest": "empty",
		"sec-fetch-mode": "cors",
		"sec-fetch-site": "same-origin",
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
	}

	recs_response = requests.get(recs_url, headers=recs_headers, params=recs_params, cookies=cookies)
	#print(recs_response)
	recs_data = recs_response.json()
	#print(recs_data)

	# Step 4: Extract IMDb IDs and movie names
	similar_movies = []
	for item in recs_data:
		similar_movies.append((item.get("properties", {}).get("release_year", ''), item.get("entityName"), item.get("slug")))

	recs_params = {
		"page": "2",
		"entityId": entity_id,
		"category": "movies",
		"limit": "18"
	}
	recs_response = requests.get(recs_url, headers=recs_headers, params=recs_params, cookies=cookies)
	#print(recs_response)
	recs_data = recs_response.json()
	for item in recs_data:
		similar_movies.append((item.get("properties", {}).get("release_year", ''), item.get("entityName"), item.get("slug")))

	return similar_movies

def get_tastedive_movies(item_id, cache_days=14, folder='TasteDive'):
	import time, hashlib, xbmcvfs, os
	import re, json, requests, html

	from urllib.parse import quote_plus
	url = 'https://tastedive.com/%s/%s/api_taste' % (item_id,'movie')
	movie_info = single_movie_info(movie_id=item_id, cache_time=7, notify=False)

	now = time.time()
	url = url.encode('utf-8')
	hashed_url = hashlib.md5(url).hexdigest()

	cache_path = xbmcvfs.translatePath(os.path.join(Utils.ADDON_DATA_PATH, folder)) if folder else xbmcvfs.translatePath(os.path.join(Utils.ADDON_DATA_PATH))
	cache_seconds = int(cache_days * 86400.0)
	path = os.path.join(cache_path, '%s.txt' % hashed_url)

	try: 
		db_result = Utils.query_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder, headers=None)
	except:
		db_result = None
	if db_result:
		return db_result
	else:
		response = get_tastedive_movies_items(movie_name = movie_info['title'], imdb_id = movie_info['imdb_id'])
		results = []
		for i in response:
			movie_response = get_movie_info(movie_label=i[1], year=i[0],use_dialog=False, notify = False)
			if movie_response:
				#results.append(movie_response['id'])
				results.append({'name': movie_response['title'], 'year': movie_response['release_date'][:4], 'media_type':  'movie', 'item_id': movie_response['id']})
			else:
				movie_response = get_movie_info(movie_label=i[1],use_dialog=False, notify = False)
				if movie_response:
					#results.append(movie_response['id'])
					results.append({'name': movie_response['title'], 'year': movie_response['release_date'][:4], 'media_type':  'movie', 'item_id': movie_response['id']})

	Utils.write_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder,cache_val=results)
	if not results:
		return []
	else:
		return results

def get_tastedive_data_scrape(url='', query='', year='', limit=20, media_type=None, cache_days=14, folder='TasteDive', item_id=None):
	if media_type == 'movie' or media_type == 'movies':
		results = get_tastedive_movies(item_id=item_id)
	else: 
		results = get_tastedive_shows(item_id=item_id)

	return results

def get_tastedive_data_scrape_old(url='', query='', year='', limit=20, media_type=None, cache_days=14, folder='TasteDive', item_id=None):
	import time, hashlib, xbmcvfs, os
	import re, json, requests, html
	
	from urllib.parse import quote_plus

	if item_id:
		url = 'https://tastedive.com/%s/%s' % (item_id,media_type)
	else:
		if 'show' in media_type or 'tv' in media_type:
			response = get_tvshow_info(tvshow_label=query,year=year,use_dialog=False)
			item_id = response['id']
		else:
			response = get_movie_info(movie_label=query,year=year,use_dialog=False, notify = False)
			item_id = response['id']
		url = 'https://tastedive.com/%s' % (item_id,media_type)

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
		db_result = Utils.query_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder, headers=None)
	except:
		db_result = None
	if db_result:
		return db_result
	else:
	#if xbmcvfs.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
	#	results = Utils.read_from_file(path)
	#	results_id = []
	#	results_out = []
	#	for i in results:
	#		if not i['item_id'] in results_id:
	#			results_id.append(i['item_id'])
	#			results_out.append(i)
	#	results = results_out
	#else:
		if item_id:
			if 'show' in media_type or 'tv' in media_type:
				#response = extended_tvshow_info(item_id)
				response = single_tvshow_info(tvshow_id=item_id, cache_time=7)
				type = 'show'
			else:
				#response = extended_movie_info(item_id)
				response = single_movie_info(movie_id=item_id, cache_time=7, notify = False)
				type = 'movie'
		else:
			if 'show' in media_type or 'tv' in media_type:
				response = get_tvshow_info(tvshow_label=query,year=year,use_dialog=False)
				item_id = response['id']
				#response = extended_tvshow_info(item_id)
				response = single_tvshow_info(tvshow_id=item_id, cache_time=7)
				type = 'show'
			else:
				response = get_movie_info(movie_label=query,year=year,use_dialog=False, notify = False)
				item_id = response['id']
				#response = extended_movie_info(item_id)
				response = single_movie_info(movie_id=item_id, cache_time=7, notify = False)
				type = 'movie'
		imdb_response = get_imdb_recommendations(imdb_id=response['imdb_id'], return_items=True)
		#xbmc.log(str(imdb_response)+'query_get_tastedive_data_scrape===>OPENINFO', level=xbmc.LOGINFO)
		results = []
		results_id = []
		for i in response['similar']['results']:
			#xbmc.log(str(i)+'query_get_tastedive_data_scrape===>OPENINFO', level=xbmc.LOGINFO)
			#xbmc.log(str(i['title'])+'query_get_tastedive_data_scrape===>OPENINFO', level=xbmc.LOGINFO)
			#xbmc.log(str(i.get('poster_path',''))+'query_get_tastedive_data_scrape===>OPENINFO', level=xbmc.LOGINFO)
			if i.get('poster_path','') == '' or i.get('poster_path','') == None or i.get('poster_path','') == 'None':
				continue
			try: votes = i['Votes']
			except: votes = i.get('vote_count',0)
			if votes >= 100:
				try: title = i['title']
				except: title = i['name']
				try: year = i['year']
				except: 
					try: year = int(i['first_air_date'][0:4])
					except: 
						try: 
							year = int(i['Premiered'][0:4])
						except: 
							try: year = int(i['release_date'][0:4])
							except: continue
				if not i['id'] in results_id:
					results.append({'name': title, 'year': year, 'media_type':  i['media_type'], 'item_id': i['id']})
					results_id.append(i['id'])
		for i in imdb_response:
			#xbmc.log(str(i)+'query_get_tastedive_data_scrape===>OPENINFO', level=xbmc.LOGINFO)
			if i.get('poster','') == '' or i.get('poster','') == None or i.get('poster','') == 'None':
				continue
			try: title = i['title']
			except: title = i['name']
			try: year = i['year']
			except: 
				try: year = int(i['first_air_date'][0:4])
				except: 
					try: 
						year = int(i['Premiered'][0:4])
					except: 
						try: year = int(i['release_date'][0:4])
						except: continue
			if not str("'item_id': %s" % (i['id'])) in str(results):
				try: votes = i['Votes']
				except: votes = i['vote_count']
				if votes >= 100:
					#results.append({'name': title, 'year': year, 'media_type':  i['media_type'], 'item_id': i['id']})
					if not i['id'] in results_id:
						results.append({'name': title, 'year': year, 'media_type':  i['media_type'], 'item_id': i['id']})
						results_id.append(i['id'])


		Utils.write_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder,cache_val=results)
		#try:
		#	Utils.write_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder,cache_val=results)
		#	Utils.save_to_file(results, hashed_url, cache_path)
		#except:
		#	Utils.log('Exception: Could not get new JSON data from %s. Tryin to fallback to cache' % url)
		#	Utils.log(response)
		#	results = Utils.read_from_file(path) if xbmcvfs.exists(path) else []

	if not results:
		return []

	#xbmcgui.Window(10000).setProperty('%s_timestamp' % hashed_url, str(now))
	#xbmcgui.Window(10000).setProperty('%s_timestamp' % hashed_url, str(now))
	#xbmcgui.Window(10000).setProperty(hashed_url, json.dumps(results))

	return results


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
	genres = [i['id'] for i in response['genres']]
	results = {
			'media_type': 'movie',
			'mediatype': 'movie',
			'adult': response['adult'],
			'backdrop_path': response['backdrop_path'],
			'genre_ids': genres,
			'id': response['id'],
			'imdb_id': Utils.fetch(Utils.fetch(response, 'external_ids'), 'imdb_id'),
			'original_language': response['original_language'],
			'original_title': response['original_title'],
			'alternative_titles': response.get('alternative_titles',[]),
			'overview': response['overview'],
			'similar': response.get('recommendations',{'page': 1, 'results': []}),
			'Rating': Utils.fetch(response, 'vote_average'),
			'Votes': Utils.fetch(response, 'vote_count'),
			'popularity': response['popularity'],
			'poster_path': response['poster_path'],
			'release_date': response['release_date'],
			'title': response['title'],
			'video': response['video'],
			'vote_average': response['vote_average'],
			'vote_count': response['vote_count']
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
		'similar': response.get('recommendations',{'page': 1, 'results': []}),
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
	try:
		for idx, i in enumerate(response['recommendations']['results']):
			if int(i.get('vote_count',0)) < 250:
				pop_list.append(idx)
		for i in reversed(pop_list):
			response['recommendations']['results'].pop(i)
	except:
		response['recommendations'] = {'page': 1, 'results': []}

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
	try:
		for idx, i in enumerate(response['recommendations']['results']):
			if int(i.get('vote_count',0)) < 150:
				pop_list.append(idx)
		for i in reversed(pop_list):
			response['recommendations']['results'].pop(i)
	except:
		response['recommendations'] = {'page': 1, 'results': []}

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

def get_trakt_userlists():
	trakt_userlist = xbmcaddon.Addon().getSetting('trakt_userlist')
	from resources.lib.library import get_trakt_data
	trakt_slug = xbmcaddon.Addon().getSetting('trakt_slug')
	trakt_user_name = xbmcaddon.Addon().getSetting('trakt_user_name')
	if trakt_userlist == 'false':
		if trakt_slug != '':
			xbmcaddon.Addon().setSetting('trakt_slug','')
			xbmcaddon.Addon().setSetting('trakt_user_name','')
		return None
	if trakt_slug == '':
		url = 'https://api.trakt.tv/users/settings'
		response = get_trakt_data(url=url, cache_days=14, folder='Trakt')
		trakt_slug = response['user']['ids']['slug']
		try: trakt_slug = response['user']['ids']['slug']
		except: return None
		if trakt_user_name == '':
			trakt_user_name = response['user']['username']
		xbmcaddon.Addon().setSetting('trakt_slug',trakt_slug)
		xbmcaddon.Addon().setSetting('trakt_user_name',trakt_user_name)
	url = 'https://api.trakt.tv/users/'+str(trakt_slug)+'/lists'
	response = get_trakt_data(url=url, cache_days=0.0001, folder='Trakt')

	trakt_list = {}
	trakt_list['trakt_list'] = []
	trakt_watchlist = "Trakt - %s's Watchlist" % (trakt_user_name)
	trakt_list['trakt_list'].append({"name" : trakt_watchlist, "user_id": trakt_slug, "list_slug": "watchlist", "sort_by": "rank", "sort_order": "asc"} )
	if response:
		for i in response:
			trakt_list['trakt_list'].append({'name': i['name'], 'user_id': trakt_slug, 'list_slug': i['ids']['slug'], 'sort_by': i['sort_by'], 'sort_order': i['sort_how']})

	url = 'https://api.trakt.tv/users/likes/lists?limit=600'
	response = get_trakt_data(url=url, cache_days=0.0001, folder='Trakt')
	response = sorted(response, key=lambda k: k['list']['item_count'], reverse=True)

	if response:
		for i in response:
			if (i['list']['user']['private'] == True or str( i['list']['user']['private']) == 'true') or (i['list']['privacy'] != 'public'):
				continue
			if 'latest' in str(i['list']['name']).lower():
				i['list']['sort_by'] = 'listed_at'
				i['list']['sort_how'] = 'desc'
			#i['list']['sort_by'] = 'rank'
			#i['list']['sort_by'] = 'popularity'
			#i['list']['sort_how'] = 'asc'
			trakt_list['trakt_list'].append({'name': 'Trakt - ' + i['list']['name'] + '('+str(i['list']['item_count'])+')', 'user_id': i['list']['user']['ids']['slug'], 'list_slug': i['list']['ids']['trakt'], "sort_by": i['list']['sort_by'], "sort_order": i['list']['sort_how']})
	return trakt_list

def get_trakt_lists(list_name=None,user_id=None,list_slug=None,sort_by=None,sort_order=None,limit=0):
	from resources.lib.library import trakt_lists
	movies = trakt_lists(list_name,user_id,list_slug,sort_by,sort_order)
	listitems = None
	x = 0
	if movies == None:
		return listitems
	for i in movies:
		imdb_id = i['ids']['imdb']
		response = get_tmdb_data('find/%s?language=%s&external_source=imdb_id&' % (imdb_id, xbmcaddon.Addon().getSetting('LanguageID')), 13)
		result_type = False
		try:
			response['movie_results'][0]['media_type'] = 'movie'
			result_type = 'movie_results'
		except:
			try:
				response['tv_results'][0]['media_type'] = 'tv'
				result_type = 'tv_results'
			except:
				result_type = False
				pass
		if listitems == None and result_type != False:
			listitems = handle_tmdb_multi_search(response[result_type])
		elif result_type != False:
			listitems += handle_tmdb_multi_search(response[result_type])
		if x + 1 == int(limit) and limit != 0:
			break
		x = x + 1
	Utils.show_busy()
	return listitems

def get_trakt(trakt_type=None,info=None,limit=0):
	import sys
	if trakt_type == 'movie':
		if info == 'trakt_watched':
			from resources.lib.library import trakt_watched_movies
			movies = trakt_watched_movies()
			#self.type = 'movie'
		if info == 'trakt_coll':
			from resources.lib.library import trakt_collection_movies
			movies = trakt_collection_movies()
			#self.type = 'movie'
		if info == 'trakt_trend':
			from resources.lib.library import trakt_trending_movies
			movies = trakt_trending_movies()
		if info == 'trakt_popular':
			from resources.lib.library import trakt_popular_movies
			movies = trakt_popular_movies()
	else:
		if info == 'trakt_watched':
			from resources.lib.library import trakt_watched_tv_shows
			movies = trakt_watched_tv_shows()
			#self.type = 'tv'
		if info == 'trakt_unwatched':
			from resources.lib.library import trakt_unwatched_tv_shows
			movies = trakt_unwatched_tv_shows()
		if info == 'trakt_coll':
			from resources.lib.library import trakt_collection_shows
			movies = trakt_collection_shows()
			#self.type = 'tv'
		if info == 'trakt_trend':
			from resources.lib.library import trakt_trending_shows
			movies = trakt_trending_shows()
		if info == 'trakt_popular':
			from resources.lib.library import trakt_popular_shows
			movies = trakt_popular_shows()
		if info == 'trakt_progress':
			from resources.lib.library import trakt_watched_tv_shows_progress
			movies = trakt_watched_tv_shows_progress()

	if 'script=False' in str(sys.argv):
		script = False
	else:
		script = True

	if script:
		listitems = None
		x = 0
		for i in movies:
			try:
				try:
					imdb_id = i['movie']['ids']['imdb']
				except:
					imdb_id = i['show']['ids']['imdb']
			except:
				imdb_id = i['ids']['imdb']
			response = get_tmdb_data('find/%s?language=%s&external_source=imdb_id&' % (imdb_id, xbmcaddon.Addon().getSetting('LanguageID')), 13)
			result_type = False
			try:
				response['movie_results'][0]['media_type'] = 'movie'
				result_type = 'movie_results'
			except:
				try:
					response['tv_results'][0]['media_type'] = 'tv'
					result_type = 'tv_results'
				except:
					result_type = False
					pass
			if listitems == None and result_type != False:
				#listitems = handle_tmdb_multi_search(response[result_type])
				listitems = []
				if result_type == 'movie_results':
					listitems.append(single_movie_info(response[result_type][0]['id']))
				else:
					listitems.append(single_tvshow_info(response[result_type][0]['id']))
			elif result_type != False:
				#listitems += handle_tmdb_multi_search(response[result_type])
				if result_type == 'movie_results':
					#try: 
					#	listitems.append(single_movie_info(response[result_type][0]['id']))
					#except: 
					#	xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
					#	xbmc.log(str(response[result_type][0])+'===>EXCEPTION', level=xbmc.LOGINFO)
					listitems.append(single_movie_info(response[result_type][0]['id']))
				else:
					listitems.append(single_tvshow_info(response[result_type][0]['id']))
		#Utils.show_busy()
			if x + 1 == int(limit) and limit != 0:
				break
			x = x + 1
		return listitems
	else:
		listitems = None
		x = 0
		for i in movies:
			try:
				try:
					imdb_id = i['movie']['ids']['imdb']
				except:
					imdb_id = i['show']['ids']['imdb']
			except:
				imdb_id = i['ids']['imdb']
			response = get_tmdb_data('find/%s?language=%s&external_source=imdb_id&' % (imdb_id, xbmcaddon.Addon().getSetting('LanguageID')), 13)
			result_type = False
			try:
				response['movie_results'][0]['media_type'] = 'movie'
				result_type = 'movie_results'
			except:
				try:
					response['tv_results'][0]['media_type'] = 'tv'
					result_type = 'tv_results'
				except:
					result_type = False
					pass
			if listitems == None and result_type != False:
				listitems = handle_tmdb_multi_search(response[result_type])
			elif result_type != False:
				listitems += handle_tmdb_multi_search(response[result_type])
			if x + 1 == int(limit) and limit != 0:
				break
			x = x + 1
		Utils.show_busy()
		return listitems

def google_similar(search_str=None, search_year=None, cache_days=7, folder = 'Google'):

	import requests, re
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
	}
	search_str = re.sub('[^0-9a-zA-Z]+', ' ', search_str)
	#search_str = Utils.clean_text(search_str)
	query = '%s %s similar movies' % (search_str,search_year)
	query1 = '%s similar' % (search_str)
	test_query = 'If you like %s' % (search_str) 

	params = {
		"q": query,		  # query example
		"hl": "en",		  # language
		"gl": "uk",		  # country of the search, UK -> United Kingdom
		#"start": 0,		  # number page by default up to 0
		#"num": 10		  # parameter defines the maximum number of results to return.
	} 

	import time, hashlib, xbmcvfs, os

	now = time.time()
	url = "https://www.google.com/search?q=" + query
	url = url.encode('utf-8')
	hashed_url = hashlib.md5(url).hexdigest()

	url1 = "https://www.google.com/search?q=" + query1
	url1 = url1.encode('utf-8')
	hashed_url1 = hashlib.md5(url1).hexdigest()

	cache_path = xbmcvfs.translatePath(os.path.join(Utils.ADDON_DATA_PATH, folder)) if folder else xbmcvfs.translatePath(os.path.join(Utils.ADDON_DATA_PATH))
	cache_seconds = int(cache_days * 86400.0)

	path = os.path.join(cache_path, '%s.txt' % hashed_url)

	try: 
		db_result = Utils.query_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder, headers=None)
	except:
		db_result = None
	try:
		db_result1 = Utils.query_db(connection=Utils.db_con,url=url1, cache_days=cache_days, folder=folder, headers=None)
	except:
		db_result1 = None
	if db_result and len(db_result) > 0:
		return db_result
	elif db_result1 and len(db_result1) > 0:
		return db_result1
	else:
	#if 1==1:

		response = requests.get("https://www.google.com/search", params=params, headers=headers)
		response2 = response.text.encode().decode('unicode_escape').encode().decode("utf-8", "replace")
		similar_movies = []
		
		#xbmc.log(str(len(response2.split('data-original-name=')))+'===>1OPENINFO', level=xbmc.LOGINFO)
		if len(response2.split('data-original-name=')) == 1:
			response2 = "".join(c for c in response2 if ord(c)<128)
			#xbmc.log(str(response2.split('<body ')[1])+'===>2OPENINFO', level=xbmc.LOGINFO)
			params = {
				"q": query1,		  # query example
				"hl": "en",		  # language
				"gl": "uk",		  # country of the search, UK -> United Kingdom
				#"start": 0,		  # number page by default up to 0
				#"num": 10		  # parameter defines the maximum number of results to return.
			} 
			response = requests.get("https://www.google.com/search", params=params, headers=headers)
			response2 = response.text.encode().decode('unicode_escape').encode().decode("utf-8", "replace")
			#response2 = "".join(c for c in response2 if ord(c)<128)
			#xbmc.log(str(response2.split('<body '))+'===>2OPENINFO', level=xbmc.LOGINFO)

		#xbmc.log(str(len(response2.split('data-original-name=')))+'===>2OPENINFO', level=xbmc.LOGINFO)
		for i in response2.split('data-original-name='):
			title = i.split('href')[0]
			year = None
			curr = {}
			if title[0:1] == '"' and not 'class=' in title:
				curr['title'] = title.split('"')[1]
			else:
				title = None
			try: year = i.split('cwxQAd')[1].split('cwxQAd')[0].split('<div>')[1].split('</div>')[0]
			except: year = None
			if year and not 'class=' in year:
				curr['year'] = year
			else:
				curr['year'] = None
			if title and not curr in similar_movies:
				similar_movies.append(curr)
		
		responses = {'page': 1, 'results': [],'total_pages': 1, 'total_results': 0}
		for i in similar_movies:
			year_string = '&primary_release_year=' + str(i['year'])
			response = get_tmdb_data('search/movie?query=%s%s&include_adult=%s&' % (Utils.url_quote(i['title']), year_string, xbmcaddon.Addon().getSetting('include_adults')), 30)
			try:
				response['results'][0]['media_type'] = 'movie'
				responses['results'].append(response['results'][0])
			except: continue
		listitems = handle_tmdb_multi_search(responses['results'])

		Utils.write_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder,cache_val=listitems)
		#try:
		#	Utils.save_to_file(listitems, hashed_url, cache_path)
		#except:
		#	Utils.log('Exception: Could not get new JSON data from %s. Tryin to fallback to cache' % url)
		#	Utils.log(response)
		#	results = Utils.read_from_file(path) if xbmcvfs.exists(path) else []

	if not listitems:
		return []

	return listitems


def get_imdb_language_api(imdb_id=None, cache_days=14, folder='IMDB'):
	import requests
	import json
	url = "https://api.graphql.imdb.com/"
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"User-Agent": "Mozilla/5.0"
	}
	query = """
	query ($id: ID!) {
		title(id: $id) {
			spokenLanguages {
				spokenLanguages {
					id
					text
				}
			}
			countriesOfOrigin {
				countries(limit: 1) {
					id
				}
			}
		}
	}
	"""
	variables = {"id": imdb_id}
	payload = {"query": query, "variables": variables}
	imdb_url = ('https://www.imdb.com/title/' + str(imdb_id) + '/get_imdb_language').encode('utf-8')
	imdb_header = headers
	try:
		db_result = Utils.query_db(connection=Utils.db_con,url=imdb_url, cache_days=cache_days, folder=folder, headers=imdb_header)
	except:
		db_result = None
	if db_result:
		return db_result
	else:
		response = requests.post(url, headers=headers, data=json.dumps(payload))
		if response.status_code != 200:
			return []
		data = response.json()
		spoken = data.get("data", {}).get("title", {}).get("spokenLanguages", {}).get("spokenLanguages", [])
		countries = data.get("data", {}).get("title", {}).get("countriesOfOrigin", {}).get("countries", [])
		language_list = [lang.get("text") for lang in spoken if "text" in lang]
		english_speaking_countries = {"US", "UK", "GB", "CA", "AU", "NZ", "IE", "ZA"}
		country_id = countries[0].get("id") if countries else ""
		if "English" in language_list and country_id in english_speaking_countries:
			language_list = ["English"] + [l for l in language_list if l != "English"]
		results = language_list
		Utils.write_db(connection=Utils.db_con,url=imdb_url, cache_days=cache_days, folder=folder,cache_val=results)
		if not results:
			return []
		return results

def imdb_base_title_card(imdb_id: str):
	url = "https://api.graphql.imdb.com/"
	headers = {
		"Content-Type": "application/json",
		"User-Agent": "Mozilla/5.0"
	}
	query = """
	query Title_Summary_Prompt_From_Base($id: ID!) {
		title(id: $id) {
			...BaseTitleCard
		}
	}
	fragment BaseTitleCard on Title {
		id
		titleText { text }
		titleType {
			id
			text
			canHaveEpisodes
			displayableProperty { value { plainText } }
		}
		originalTitleText { text }
		primaryImage {
			id
			width
			height
			url
			caption { plainText }
		}
		releaseYear { year endYear }
		ratingsSummary { aggregateRating voteCount }
		runtime { seconds }
		certificate { rating }
		canRate { isRatable }
		titleGenres {
			genres(limit: 3) {
				genre { text }
			}
		}
	}
	"""
	variables = {
		"id": imdb_id
	}
	response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
	if response.status_code == 200:
		return response.json()
	else:
		raise Exception(f"Query failed with status code {response.status_code}: {response.text}")

def get_imdb_language(imdb_id=None, cache_days=14, folder='IMDB'):

	if 1==1:
		Utils.log('get_imdb_language_api')
		results = get_imdb_language_api(imdb_id=imdb_id, cache_days=cache_days, folder='IMDB')
		return results

"""
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
		db_result = Utils.query_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder, headers=imdb_header)
	except:
		db_result = None
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

		Utils.write_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder,cache_val=results)
		#try:
		#	Utils.save_to_file(results, hashed_url, cache_path)
		#except:
		#	Utils.log('Exception: Could not get new JSON data from %s. Tryin to fallback to cache' % url)
		#	Utils.log(response)
		#	results = Utils.read_from_file(path) if xbmcvfs.exists(path) else []

		if not results:
			return []
		#xbmcgui.Window(10000).setProperty('%s_timestamp' % hashed_url, str(now))
		#xbmcgui.Window(10000).setProperty(hashed_url, json.dumps(results))
		return results
"""

def get_imdb_season_episodes(imdb_id, season, first=99):
	import requests
	import json
	url = "https://api.graphql.imdb.com/"
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"User-Agent": "Mozilla/5.0"
	}
	query = """
	query SeasonEpisodes($id: ID!, $season: String!, $first: Int!, $originalTitleText: Boolean!) {
		title(id: $id) {
			episodes {
				episodes(
					first: $first
					filter: { includeSeasons: [$season] }
					sort: { by: EPISODE_THEN_RELEASE, order: ASC }
				) {
					edges {
						node {
							id
							titleText {
								text
							}
							plot {
								plotText {
									plaidHtml(showOriginalTitleText: $originalTitleText)
								}
							}
							releaseDate {
								year
								month
								day
							}
							ratingsSummary {
								aggregateRating
								voteCount
							}
							primaryImage {
								url
							}
							series {
								displayableEpisodeNumber {
									episodeNumber {
										displayableProperty {
											value {
												plainText
											}
										}
									}
									displayableSeason {
										displayableProperty {
											value {
												plainText
											}
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
	"""
	variables = {
		"id": imdb_id,
		"season": str(season),
		"first": first,
		"originalTitleText": True
	}
	payload = {
		"query": query,
		"variables": variables
	}
	response = requests.post(url, headers=headers, data=json.dumps(payload))
	response.raise_for_status()
	data = response.json()
	edges = data.get("data", {}).get("title", {}).get("episodes", {}).get("episodes", {}).get("edges", [])
	episodes = []
	for edge in edges:
		try: 
			node = edge.get("node", {})
			displayable_episode_number = node.get("series", {}).get("displayableEpisodeNumber", {})
			episode_number = displayable_episode_number.get("episodeNumber", {}).get("displayableProperty", {}).get("value", {}).get("plainText")
			season_number = displayable_episode_number.get("displayableSeason", {}).get("displayableProperty", {}).get("value", {}).get("plainText")
			plot_html = node.get("plot", {}).get("plotText", {}).get("plaidHtml")
			episodes.append({
				"id": node.get("id"),
				"title": node.get("titleText", {}).get("text"),
				"plot": plot_html,
				"release_date": node.get("releaseDate"),
				"rating": node.get("ratingsSummary", {}).get("aggregateRating"),
				"vote_count": node.get("ratingsSummary", {}).get("voteCount"),
				"image_url": node.get("primaryImage", {}).get("url"),
				"episode_number": episode_number,
				"season_number": season_number
			})
		except: continue
	return episodes

def get_imdb_recommendations_api(imdb_id=None, return_items=False, cache_days=14, folder='IMDB'):
	import requests
	import json
	url = "https://api.graphql.imdb.com/"
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"User-Agent": "Mozilla/5.0"
	}
	base_title_card = """
	fragment BaseTitleCard on Title {
		id
		titleText {
			text
		}
		primaryImage {
			url
		}
		releaseYear {
			year
		}
		titleType {
			text
		}
	}
	"""
	query = f"""
	query MoreLikeThis($id: ID!) {{
		title(id: $id) {{
			...TMD_MoreLikeThis
		}}
	}}
	fragment TMD_MoreLikeThis on Title {{
		id
		isAdult
		moreLikeThisTitles(first: 12) {{
			edges {{
				node {{
					...BaseTitleCard
				}}
			}}
		}}
	}}
	{base_title_card}
	"""
	variables = {
		"id": imdb_id
	}
	payload = {
		"query": query,
		"variables": variables
	}

	imdb_url = 'https://www.imdb.com/title/' + str(imdb_id)
	imdb_url2 = 'https://www.imdb.com/title/' + str(imdb_id) + '[2]'
	imdb_url = str(imdb_url + '/get_imdb_recommendations').encode('utf-8')
	imdb_url2 = str(imdb_url2 + '/get_imdb_recommendations').encode('utf-8')
	imdb_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

	try: 
		db_result = Utils.query_db(connection=Utils.db_con,url=imdb_url, cache_days=cache_days, folder=folder, headers=imdb_header)
	except:
		db_result = None
	if db_result:
		return db_result
	else:
		response = requests.post(url, headers=headers, data=json.dumps(payload))
		if response.status_code != 200:
			raise Exception(f"Query failed with status code {response.status_code}: {response.text}")
		data = response.json()
		edges = data.get("data", {}).get("title", {}).get("moreLikeThisTitles", {}).get("edges", [])
		movies = [edge["node"]["id"] for edge in edges if "node" in edge and "id" in edge["node"]]

		if return_items == False:
			results2 = movies
			Utils.write_db(connection=Utils.db_con,url=imdb_url, cache_days=cache_days, folder=folder,cache_val=results)
			if not results2:
				return []
			return results2
		else:
			results = get_imdb_watchlist_items(movies=movies, limit=0, imdb_url=imdb_url.decode('utf-8'))
			Utils.write_db(connection=Utils.db_con,url=imdb_url, cache_days=cache_days, folder=folder,cache_val=results)
			if not results:
				return []
			return results


def get_imdb_recommendations(imdb_id=None, return_items=False, cache_days=14, folder='IMDB'):

	if 1==1:
		Utils.log('get_imdb_recommendations_api')
		movies = get_imdb_recommendations_api(imdb_id, return_items=return_items, cache_days=cache_days, folder='IMDB')
		return movies
"""
	import time, hashlib, xbmcvfs, os
	import re, json, requests, html
	
	imdb_url = 'https://www.imdb.com/title/' + str(imdb_id)
	imdb_url2 = 'https://www.imdb.com/title/' + str(imdb_id) + '[2]'
	url = imdb_url + '/get_imdb_recommendations'
	url2 = imdb_url2 + '/get_imdb_recommendations'
	imdb_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
	
	now = time.time()
	url = url.encode('utf-8')
	hashed_url = hashlib.md5(url).hexdigest()
	cache_path = xbmcvfs.translatePath(os.path.join(Utils.ADDON_DATA_PATH, folder)) if folder else xbmcvfs.translatePath(os.path.join(Utils.ADDON_DATA_PATH))
	url2 = url2.encode('utf-8')
	hashed_url2 = hashlib.md5(url2).hexdigest()
	cache_path2 = xbmcvfs.translatePath(os.path.join(Utils.ADDON_DATA_PATH, folder)) if folder else xbmcvfs.translatePath(os.path.join(Utils.ADDON_DATA_PATH))
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
	path2 = os.path.join(cache_path2, '%s[2].txt' % hashed_url2)

	try: 
		db_result = Utils.query_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder, headers=imdb_header)
		#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
	except:
		db_result = None
		xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
	if db_result:
		#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
		return db_result
	else:

	#if xbmcvfs.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
	#	results = Utils.read_from_file(path)
	#	results2 = Utils.read_from_file(path2)
	#	if return_items == False:
	#		if not results2:
	#			return []
	#		#xbmcgui.Window(10000).setProperty('%s_timestamp' % hashed_url2, str(now))
	#		#xbmcgui.Window(10000).setProperty(hashed_url2, json.dumps(results2))
	#		return results2
	#	else:
	#		if not results:
	#			return []
	#		#xbmcgui.Window(10000).setProperty('%s_timestamp' % hashed_url, str(now))
	#		#xbmcgui.Window(10000).setProperty(hashed_url, json.dumps(results))
	#		return results

	#else:
		imdb_response = requests.get(imdb_url, headers=imdb_header)
		try: 
			imdb_response = imdb_response.text.split('<span>Storyline</span>')[0].split('<span>More like this</span>')[1]
		except:
			Utils.log('IMDB_ERROR with URL =  %s. RETUNR_NONE_TheMovieDB.py_get_imdb_recommendations()' % imdb_url)
			return []
		list_container = str(imdb_response).split('poster-card__title--clickable" aria-label="')
		toggle = False
		movies = []
		for i in list_container:
			if 'href="/title/' in str(i):
				imdb_id = i.split('href="/title/')[1].split('/?ref_')[0]
				if imdb_id.replace('tt','').isnumeric():
					movies.append(imdb_id)

		if return_items == False:
			results2 = movies

			Utils.write_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder,cache_val=results)
			#try:
			#	Utils.save_to_file(results2, hashed_url2, cache_path2)
			#except:
			#	Utils.log('Exception: Could not get new JSON data from %s. Tryin to fallback to cache' % url)
			#	Utils.log(response)
			#	results2 = Utils.read_from_file(path2) if xbmcvfs.exists(path2) else []

			if not results2:
				return []
			#xbmcgui.Window(10000).setProperty('%s_timestamp' % hashed_url2, str(now))
			#xbmcgui.Window(10000).setProperty(hashed_url2, json.dumps(results2))
			return results2
		else:
			results = get_imdb_watchlist_items(movies=movies, limit=0, imdb_url=imdb_url)

			Utils.write_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder,cache_val=results)
			#try:
			#	Utils.save_to_file(results, hashed_url, cache_path)
			#except:
			#	Utils.log('Exception: Could not get new JSON data from %s. Tryin to fallback to cache' % url)
			#	Utils.log(response)
			#	results = Utils.read_from_file(path) if xbmcvfs.exists(path) else []

			if not results:
				return []
			#xbmcgui.Window(10000).setProperty('%s_timestamp' % hashed_url, str(now))
			#xbmcgui.Window(10000).setProperty(hashed_url, json.dumps(results))
			return results
"""

def get_imdb_list_ids_api2(list_str=None):
	import requests, json
	url = "https://api.graphql.imdb.com/"
	headers = {
		"Content-Type": "application/json",
		"User-Agent": "Mozilla/5.0",
		"x-imdb-client-name": "imdb-web-next"
	}

	base_title_card = """
	fragment BaseTitleCard on Title {
		id
		titleText { text }
		primaryImage { url }
		releaseYear { year }
		titleType { text }
	}
	"""

	query = f"""
	query VideoPlaylistWidgetList($id: ID!, $first: Int!, $after: ID) {{
	  list(id: $id) {{
		items(first: $first, after: $after) {{
		  total
		  pageInfo {{
			endCursor
			hasNextPage
		  }}
		  edges {{
			node {{
			  listItem {{
				... on Title {{
				  ...BaseTitleCard
				}}
			  }}
			}}
		  }}
		}}
	  }}
	}}
	{base_title_card}
	"""

	all_items = []
	after_cursor = None
	total = None

	

	while True:
		variables = {
			"id": list_str,
			"first": 1000,
			"after": after_cursor
		}
		payload = {"query": query,"variables": variables}
		#response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
		response = requests.post(url, headers=headers, data=json.dumps(payload))
		if response.status_code != 200:
			raise Exception(f"Query failed with status code {response.status_code}: {response.text}")

		data = response.json()
		items_data = data.get("data", {}).get("list", {}).get("items", {})
		if total is None:
			total = items_data.get("total", 0)

		edges = items_data.get("edges", [])
		for edge in edges:
			node = edge.get("node", {})
			title = node.get("listItem", {})
			if title:
				all_items.append({
					"id": title.get("id"),
					"title": title.get("titleText", {}).get("text"),
					"image": title.get("primaryImage", {}).get("url"),
					"year": title.get("releaseYear", {}).get("year"),
					"type": title.get("titleType", {}).get("text")
				})

		page_info = items_data.get("pageInfo", {})
		if not page_info.get("hasNextPage"):
			break
		after_cursor = page_info.get("endCursor")
	movies = []
	for i in all_items:
		movies.append(i['id'])
	#return {"total": total,"fetched": len(all_items),"items": all_items}
	return movies

"""
def get_imdb_list_ids_api(list_str=None, limit=0):
	import requests
	import json

	url = "https://api.graphql.imdb.com/"

	headers = {
		"Content-Type": "application/json",
		"User-Agent": "Mozilla/5.0",
		"Accept": "application/json"
	}

	jumpToPosition = 1
	payload = {
		"operationName": "TitleListMainPage",
		"variables": {
			"first": 1000,
			"isInPace": False,
			"jumpToPosition": jumpToPosition,  # or 1, 251, 501, etc. for pagination
			"locale": "en-US",
			"lsConst": list_str,  # list ID (this one is the IMDb Top 1000)
			"sort": {
				"by": "LIST_ORDER",
				"order": "ASC"
			}
		},
		"extensions": {
			"persistedQuery": {
				"version": 1,
				"sha256Hash": "4ce93fcade18588c948023788c0e42ee5c602148d417c828cd1712726dd24082"
			}
		}
	}

	response = requests.post(url, headers=headers, data=json.dumps(payload))

	data = response.json()

	movies = []
	for i in data['data']['list']['titleListItemSearch']['edges']:
		movies.append(i['listItem']['id'])

	jumpToPosition = 1
	total_items = data['data']['list']['items']['total']
	while jumpToPosition + 1000 < total_items:
		jumpToPosition = jumpToPosition + 1000
		payload['variables']['jumpToPosition'] = jumpToPosition
		response = requests.post(url, headers=headers, data=json.dumps(payload))
		data = response.json()
		for i in data['data']['list']['titleListItemSearch']['edges']:
			movies.append(i['listItem']['id'])
	return movies
"""

def get_imdb_list_ids(list_str=None, limit=0):
	Utils.log(list_str)
	if 'ls_top_1000' == list_str:
		movies = imdb_top_1000()
		return movies

	if 'ls_imdb_coming_soon' == list_str:
		country = xbmcaddon.Addon().getSetting('imdb_country')
		movies = imdb_coming_soon(country=country, coming_soon_type="MOVIE")
		return movies

	if list_str in ['ls_popular','ls_trending','ls_anticipated','ls_recent']:
		Utils.log(list_str)
		movies = imdb_multi(list_str)
		return movies

	if 'ls_imdb_movies_near_you' == list_str:
		from datetime import date
		from dateutil.relativedelta import relativedelta
		today = date.today()
		one_month_later = today + relativedelta(months=1)
		one_month_earlier = today + relativedelta(months=-1)

		start_date = one_month_earlier.strftime("%Y-%m-%d")
		end_date = one_month_later.strftime("%Y-%m-%d")

		imdb_lat = xbmcaddon.Addon().getSetting('imdb_lat')
		imdb_long = xbmcaddon.Addon().getSetting('imdb_long')
		imdb_radius = xbmcaddon.Addon().getSetting('imdb_radius')
		movies = imdb_movies_near_you(latitude=float(imdb_lat),longitude=float(imdb_long),radius_meters=int(imdb_radius),start_date=start_date,end_date=end_date)
		return movies

	else:
		Utils.log('get_imdb_list_ids_api2  ' + str(list_str))
		movies = get_imdb_list_ids_api2(list_str)
		return movies
	"""
	import requests
	page_curr = 1
	imdb_url = 'https://www.imdb.com/list/'+str(list_str)+'/?page=1'
	Utils.log(imdb_url)
	imdb_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
	imdb_response = requests.get(imdb_url, headers=imdb_header)
	movies = []
	list_container = str(imdb_response.text).split('"listItem":{"id":"')
	for i in list_container:
		if '","titleText":' in i:
			y = i.split('","titleText":')[0]
			movies.append(y)
	try:
		page_label = imdb_response.text.split('listPagination')[1].split('>')[1].split('<')[0]
		page_curr = page_label.split(' of ')[0]
		page_next = int(page_curr) + 1
		page_tot = page_label.split(' of ')[1]
	except:
		page_next ,page_curr, page_tot = 2, 1, 1
	while page_next <= int(page_tot):
		imdb_url = 'https://www.imdb.com/list/'+str(list_str)+'/?page=' + str(page_next)
		Utils.log(imdb_url)
		page_curr = page_next
		imdb_response = requests.get(imdb_url, headers=imdb_header)
		list_container = str(imdb_response.text).split('"listItem":{"id":"')
		for i in list_container:
			if '","titleText":' in i:
				y = i.split('","titleText":')[0]
				movies.append(y)
		page_next = int(page_curr) + 1
	return movies
	"""



def imdb_top_1000():
	import requests
	API_URL = "https://graphql.prod.api.imdb.a2z.com/"
	HEADERS = {
		'Referer': 'https://www.imdb.com/',
		'Origin': 'https://www.imdb.com',
		'User-Agent': 'Mozilla/5.0',
		'Content-Type': 'application/json'
	}

	query = '''
	query AdvancedTitleSearch(
		$first: Int!,
		$after: String,
		$originCountryConstraint: OriginCountrySearchConstraint,
		$rankedTitleListConstraint: RankedTitleListSearchConstraint,
		$sortBy: AdvancedTitleSearchSortBy!,
		$sortOrder: SortOrder!
	) {
		advancedTitleSearch(
			first: $first,
			after: $after,
			constraints: {
				originCountryConstraint: $originCountryConstraint,
				rankedTitleListConstraint: $rankedTitleListConstraint
			},
			sort: {
				sortBy: $sortBy,
				sortOrder: $sortOrder
			}
		) {
			...AdvancedTitleSearchConnection
		}
	}

	fragment AdvancedTitleSearchConnection on AdvancedTitleSearchConnection {
		total
		pageInfo {
			endCursor
			hasNextPage
		}
		edges {
			node {
				title {
					id
					titleText { text }
					originalTitleText { text }
					ratingsSummary { aggregateRating voteCount }
					releaseYear { year }
					primaryImage { url }
				}
			}
		}
	}
	'''

	variables = {
		"first": 1000,
		"after": None,
		"locale": "en-US",
		"originCountryConstraint": {
			"excludeCountries": ["IN"]
		},
		"rankedTitleListConstraint": {
			"allRankedTitleLists": [{
				"rankRange": {"max": 1000},
				"rankedTitleListType": "TOP_RATED_MOVIES"
			}],
			"excludeRankedTitleLists": []
		},
		"sortBy": "USER_RATING",
		"sortOrder": "DESC"
	}

	all_titles = []
	while True:
		response = requests.post(API_URL, headers=HEADERS, json={
			"operationName": "AdvancedTitleSearch",
			"query": query,
			"variables": variables
		})
		#print(response.text)
		data = response.json()["data"]["advancedTitleSearch"]

		titles = [edge["node"]["title"]["id"] for edge in data["edges"]]
		all_titles.extend(titles)

		if not data["pageInfo"]["hasNextPage"]:
			break

		variables["after"] = data["pageInfo"]["endCursor"]

	return all_titles


"""
def imdb_top_1000():
	import requests
	import json, time

	url = 'https://caching.graphql.imdb.com/'

	headers = {'Content-Type': 'application/json','User-Agent': 'Mozilla/5.0','Accept': 'application/json',}

	payload = {
		"operationName": "AdvancedTitleSearch",
		"variables": {
			"after": None,
			"first": 1000,
			"locale": "en-US",
			"originCountryConstraint": {
				"excludeCountries": ["IN"]
			},
			"rankedTitleListConstraint": {
				"allRankedTitleLists": [{
					"rankRange": {"max": 1000},
					"rankedTitleListType": "TOP_RATED_MOVIES"
				}],
				"excludeRankedTitleLists": []
			},
			"sortBy": "USER_RATING",
			"sortOrder": "DESC"
		},
		"extensions": {
			"persistedQuery": {
				"version": 1,
				"sha256Hash": "81b46290a78cc1e8b3d713e6a43c191c55b4dccf3e1945d6b46668945846d832"
			}
		}
	}

	response = requests.post(url, headers=headers, data=json.dumps(payload))
	x = 0
	if 'PersistedQueryNotFound' in str(response.text):
		while 'PersistedQueryNotFound' in str(response.text):
			response = requests.post(url, headers=headers, data=json.dumps(payload))
			time.sleep(0.3)
			x = x + 1
			if x == 5:
				break
	if "errorType" in str(response.text):
		xbmc.log(str(response.text)+'get_first_page'+str(x)+'===>imdb_top_1000', level=xbmc.LOGINFO)

	data = response.json()
	movies = []
	for i in data['data']['advancedTitleSearch']['edges']:
		movies.append(i['node']['title']['id'])
	return movies
"""

"""
def imdb_userListSearch_api(ur_id=None):
	import requests
	import json

	url = 'https://caching.graphql.imdb.com/'

	headers = {'Content-Type': 'application/json','User-Agent': 'Mozilla/5.0','Accept': 'application/json',}

	all_items = []
	cursor = None
	has_next_page = True

	while has_next_page:
		payload = {
			"operationName": "ListsPage",
			"variables": {
				"anyListTypes": ["TITLES"],
				"first": 1000,
				"locale": "en-GB",
				"sort": {"by": "DATE_MODIFIED", "order": "DESC"},
				"urConst": ur_id,
				"after": cursor
			},
			"extensions": {
				"persistedQuery": {
					"version": 1,
					"sha256Hash": "65f7594228f90dd121598ee9c4dfd05f95fb6f0d47d453501aef99cf331434d1"
				}
			}
		}

		response = requests.post(url, headers=headers, data=json.dumps(payload))
		x = 0
		if 'PersistedQueryNotFound' in str(response.text):
			while 'PersistedQueryNotFound' in str(response.text):
				response = requests.post(url, headers=headers, data=json.dumps(payload))
				time.sleep(0.3)
				x = x + 1
				if x == 5:
					break
		if "errorType" in str(response.text):
			print_log(response.text,'get_first_page'+str(x))

		data = response.json()

		#try:
		if 1==1:
			edges = data['data']['userListSearch']['edges']
			page_info = data['data']['userListSearch']['pageInfo']
			all_items.extend(edges)
			has_next_page = page_info['hasNextPage']
			cursor = page_info['endCursor']
		#except Exception as e:
		#	print("Error:", e)
		#	break

	#imdb_list = {'imdb_list': [{'urXXXXX': 'IMDB - USER Watchlist'}, {'ls562384988': 'IMDB - Nowtfilx'}, ]}
	imdb_list = {'imdb_list': []}
	imdb_list['imdb_list'].append({ur_id: 'IMDB - %s Watchlist' % str(data.get('data', {}).get('userProfile',{}).get('username','').get('text','')) })
	results = []
	for i in all_items:
		imdb_list['imdb_list'].append({i['node']['id']: 'IMDB - ' + str(i['node']['name']['originalText']) + ' - ' + str(i['node']['items']['total'])})
		#xbmc.log(str({'list_id': i['node']['id'], 'list_name': i['node']['name']['originalText'], 'list_count': i['node']['items']['total']})+'===>OPENINFO', level=xbmc.LOGINFO)
	return imdb_list
"""

"""
def get_imdb_userlists_search(imdb_id=None):
	imdb_id = imdb_id
	if imdb_id == '':
		return None
	import requests
	imdb_url = 'https://www.imdb.com/user/'+str(imdb_id)+'/lists'
	#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
	#xbmc.log(str(imdb_url)+'===>OPENINFO', level=xbmc.LOGINFO)
	imdb_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
	imdb_response = requests.get(imdb_url, headers=imdb_header)
	list_container = str(imdb_response.text,).split('<')
	#xbmc.log(str(list_container)+'===>OPENINFO', level=xbmc.LOGINFO)
	imdb_list = {}
	imdb_list['imdb_list'] = []
	processed_list = []
	imdb_user_name = None

	for i in list_container:
		if 'meta property=\'og:title\' content="' in i:
			imdb_user_name = i.split('"')[1].replace('Lists - IMDb','')
			imdb_user_name = 'IMDB - %s Watchlist' % (imdb_user_name)
			imdb_list['imdb_list'].append({imdb_id: imdb_user_name})
		if 'title>' in i and imdb_user_name == None:
			imdb_user_name = html.unescape(i.split('title>')[1]).replace("'s Lists",'')
			imdb_user_name = 'IMDB - %s Watchlist' % (imdb_user_name)
			imdb_list['imdb_list'].append({imdb_id: imdb_user_name})

		if 'href="/list/ls' in i:
			list_number = 'ls' + i.split('href="/list/ls')[1].split('/?r')[0]
			if list_number in processed_list:
				continue
			processed_list.append(list_number)
			#list_name = 'IMDB - ' + i.split('/')[3].replace('">','')
			list_name = 'IMDB - ' + i.split('View list page for ')[1].split('">')[0]
			imdb_list['imdb_list'].append({list_number: list_name})

	if len(imdb_list['imdb_list']) == 0:
		xbmc.log(str(imdb_url)+'===>OPENINFO', level=xbmc.LOGINFO)
		xbmc.log(str(list_container)+'===>OPENINFO', level=xbmc.LOGINFO)
		xbmc.log(str(imdb_url)+'===>OPENINFO', level=xbmc.LOGINFO)
	return imdb_list
"""

def imdb_userListSearch_api(ur_id=None):
	Utils.log('imdb_userListSearch_api')
	import requests
	import time

	API_URL = "https://graphql.prod.api.imdb.a2z.com/"
	HEADERS = {
		'Referer': 'https://www.imdb.com/',
		'Origin': 'https://www.imdb.com',
		'User-Agent': 'Mozilla/5.0',
		'Content-Type': 'application/json',
		'Accept': 'application/json',
	}

	query = '''
	query ListsPage(
		$first: Int!,
		$after: ID,
		$anyListTypes: [ListTypeId!],
		$anyVisibilities: [ListVisibilityId!],
		$sort: ListSearchSort,
		$urConst: ID
	) {
		userProfile(input: { userId: $urConst }) {
			username { text }
		}
		userListSearch(
			after: $after,
			filter: {
				anyClassTypes: [LIST],
				anyListTypes: $anyListTypes,
				anyVisibilities: $anyVisibilities
			},
			first: $first,
			listOwnerUserId: $urConst,
			sort: $sort
		) {
			edges {
				node {
					...UserListListItemMetadata
				}
			}
			pageInfo {
				endCursor
				hasNextPage
				hasPreviousPage
			}
			total
		}
	}

	fragment UserListListItemMetadata on List {
		author {
			nickName
			userId
		}
		id
		name {
			originalText
		}
		listType {
			id
		}
		listClass {
			id
			name { text }
		}
		description {
			originalText {
				plainText
			}
		}
		items(first: 0) {
			total
		}
		createdDate
		lastModifiedDate
		primaryImage {
			image {
				id
				caption { plainText }
				height
				width
				url
			}
		}
		visibility { id }
	}
	'''

	variables = {
		"first": 1000,
		"after": None,
		"anyListTypes": ["TITLES"],
		"anyVisibilities": ["PUBLIC", "PRIVATE"],
		"sort": {"by": "DATE_MODIFIED", "order": "DESC"},
		"urConst": ur_id
	}

	all_items = []
	has_next_page = True
	cursor = None

	while has_next_page:
		variables["after"] = cursor
		payload = {
			"operationName": "ListsPage",
			"query": query,
			"variables": variables
		}

		response = requests.post(API_URL, headers=HEADERS, json=payload)
		response.raise_for_status()
		data = response.json()

		edges = data.get("data", {}).get("userListSearch", {}).get("edges", [])
		page_info = data.get("data", {}).get("userListSearch", {}).get("pageInfo", {})
		username = data.get("data", {}).get("userProfile", {}).get("username", {}).get("text", "")

		all_items.extend(edges)
		has_next_page = page_info.get("hasNextPage", False)
		cursor = page_info.get("endCursor")

		time.sleep(0.3)

	imdb_list = {"imdb_list": []}
	#imdb_list["imdb_list"].append({ur_id: f"IMDB - {username} Watchlist"})
	watchlist_dict = get_user_watchlist_id(ur_list_str=ur_id,return_dict=True)
	watchlist_dict['name'] = watchlist_dict['name'].replace(ur_id,username)
	imdb_list["imdb_list"].append({watchlist_dict['watchlist_id']: watchlist_dict['name']})

	for item in all_items:
		node = item.get("node", {})
		list_id = node.get("id")
		list_name = node.get("name", {}).get("originalText", "")
		list_count = node.get("items", {}).get("total", 0)
		imdb_list["imdb_list"].append({list_id: f"IMDB - {list_name} - {list_count}"})


	return imdb_list

def get_imdb_userlists():
	imdb_id = xbmcaddon.Addon().getSetting('imdb_ur_id')
	Utils.log(imdb_id)
	if imdb_id == '':
		return None
	#imdb_list = get_imdb_userlists_search(imdb_id=imdb_id)
	#Utils.log(imdb_id)
	imdb_list = imdb_userListSearch_api(ur_id=imdb_id)
	return imdb_list

def get_user_watchlist_id(ur_list_str=None,return_dict=False):
	Utils.log('get_user_watchlist_id')
	import requests, json

	API_URL = "https://graphql.prod.api.imdb.a2z.com/"

	HEADERS = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
		"Accept": "application/json",
		"Content-Type": "application/json",
		"Referer": "https://www.imdb.com/user/%s/" % (str(ur_list_str)),
		"Origin": "https://www.imdb.com",
		"x-imdb-client-name": "imdb-web-next",
		"x-imdb-user-language": "en-GB",
		"x-imdb-user-country": "GB"
	}

	GRAPHQL_QUERY = """

	query YourPredefinedListsSidebar($userId: ID!) {
	  watchlist: predefinedList(classType: WATCH_LIST, userId: $userId) {
		...ListPreviewCard
	  }
	}

	fragment ListPreviewCard on List {
	  id
	  lastModifiedDate
	  createdDate
	  name { originalText }
	  listType { id }
	  primaryImage {
		image {
		  url height width
		  caption { plainText }
		}
	  }
	  items(first: 0) { total }
	}

	"""

	response = requests.post(API_URL, headers=HEADERS, json={"query": GRAPHQL_QUERY, "variables": {"userId": ur_list_str}})
	#print("Status Code:", response.status_code)
	#print("Response JSON:")
	#print(response.text)
	data = response.json()
	watchlist_id = data['data']['watchlist']['id']
	if return_dict == False:
		return watchlist_id
	else:
		watchlist_dict = {}
		watchlist_dict['watchlist_id'] = watchlist_id
		watchlist_dict['ur_list_str'] = ur_list_str
		watchlist_dict['total'] = data['data']['watchlist']['items']['total']
		watchlist_dict['name'] = f"IMDB - {ur_list_str} Watchlist - " + str(data['data']['watchlist']['items']['total'])
		return watchlist_dict


def get_imdb_watchlist_ids_api2(ur_list_str=None, limit=0):
	"""
	import requests, json
	url_user = 'https://www.imdb.com/user/%s/?ref_=wl_usr_ov' % (ur_list_str)
	headers = {
		"Content-Type": "application/json",
		"User-Agent": "Mozilla/5.0",
		"x-imdb-client-name": "imdb-web-next"
	}
	response = requests.get(url_user, headers=headers)
	#watchlist_data = str(response.text.split('watchlistData')[1].split('"TitleListItemSearchEdge"}]')[0])
	#xbmc.log(str(watchlist_data)+'===>OPENINFO', level=xbmc.LOGINFO)
	list_id = 'ls' + str(response.text.split('watchlistData":{"id":"ls')[1].split('","')[0])
	"""
	list_id = get_user_watchlist_id(ur_list_str=ur_list_str)

	url = "https://api.graphql.imdb.com/"
	movies = get_imdb_list_ids_api2(list_str=list_id)
	return movies

"""
def get_imdb_watchlist_ids_api(ur_list_str=None, limit=0):
	list_str = ur_list_str
	import requests
	import json
	url = "https://api.graphql.imdb.com/"
	headers = {
		"Content-Type": "application/json",
		"User-Agent": "Mozilla/5.0",
		"Accept": "application/json"
	}
	jumpToPosition = 1
	payload = {
		"operationName": "WatchListPageRefiner",
		"variables": {
			"first": 1000,
			"jumpToPosition": jumpToPosition,  # You can change this to 1, 251, 501, etc.
			"locale": "en-US",
			"sort": {
				"by": "LIST_ORDER",
				"order": "ASC"
			},
			"urConst": list_str
		},
		"extensions": {
			"persistedQuery": {
				"version": 1,
				"sha256Hash": "36d16110719e05e125798dec569721248a88835c64a7e853d3a80be8775eea92"
			}
		}
	}
	response = requests.post(url, headers=headers, data=json.dumps(payload))
	data = response.json()
	movies = []
	for i in data['data']['predefinedList']['titleListItemSearch']['edges']:
		movies.append(i['listItem']['id'])
	jumpToPosition = 1
	total_items = data['data']['predefinedList']['titleListItemSearch']['total']
	while jumpToPosition + 1000 < total_items:
		jumpToPosition = jumpToPosition + 1000
		payload['variables']['jumpToPosition'] = jumpToPosition
		response = requests.post(url, headers=headers, data=json.dumps(payload))
		data = response.json()
		for i in data['data']['predefinedList']['titleListItemSearch']['edges']:
			movies.append(i['listItem']['id'])
	return movies
"""

def get_imdb_watchlist_ids(ur_list_str=None, limit=0):
	if ur_list_str:
		Utils.log('get_imdb_watchlist_ids_api2')
		movies = get_imdb_watchlist_ids_api2(ur_list_str)
		return movies
	"""
	import requests
	list_str=ur_list_str

	page_curr = 1
	imdb_url = 'https://www.imdb.com/user/'+str(list_str)+'/watchlist?page=1'
	Utils.log(imdb_url)
	imdb_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
	imdb_response = requests.get(imdb_url, headers=imdb_header)
	movies = []
	list_container = str(imdb_response.text).split('"listItem":{"id":"')
	for i in list_container:
		if '","titleText":' in i:
			y = i.split('","titleText":')[0]
			movies.append(y)
	try:
		page_label = imdb_response.text.split('listPagination')[1].split('>')[1].split('<')[0]
		page_curr = page_label.split(' of ')[0]
		page_next = int(page_curr) + 1
		page_tot = page_label.split(' of ')[1]
	except:
		page_next ,page_curr, page_tot = 2, 1, 1
	while page_next <= int(page_tot):
		imdb_url = 'https://www.imdb.com/user/'+str(list_str)+'/watchlist?page=' +  str(page_next)
		Utils.log(imdb_url)
		page_curr = page_next
		imdb_response = requests.get(imdb_url, headers=imdb_header)
		list_container = str(imdb_response.text).split('"listItem":{"id":"')
		for i in list_container:
			if '","titleText":' in i:
				y = i.split('","titleText":')[0]
				movies.append(y)
		page_next = int(page_curr) + 1
	return movies
	"""


def imdb_coming_soon(country: str, coming_soon_type: str):
	#titles = imdb_coming_soon(country="GB", coming_soon_type="MOVIE")
	import requests, datetime
	API_URL = "https://graphql.prod.api.imdb.a2z.com/"
	HEADERS = {
		'Referer': 'https://www.imdb.com/',
		'Origin': 'https://www.imdb.com',
		'User-Agent': 'Mozilla/5.0',
		'Content-Type': 'application/json'
	}

	fragment = """
	fragment CalendarCard on Title {
		id
		titleText { text }
		originalTitleText { text }
		titleType { id text canHaveEpisodes }
		isAdult
		releaseDate {
			year
			month
			day
			country { id }
			displayableProperty {
				qualifiersInMarkdownList { plaidHtml }
			}
		}
		releaseDates(
			first: 10,
			filter: {
				countries: [$countryOverride],
				wideRelease: WIDE_RELEASE_ONLY
			}
		) {
			edges {
				node {
					year
					month
					day
					country { id }
					displayableProperty {
						qualifiersInMarkdownList { plaidHtml }
					}
				}
			}
		}
		primaryImage {
			url
			height
			width
			caption { plainText }
		}
		titleGenres {
			genres(limit: 3) {
				genre {
					displayableProperty {
						value { plainText }
					}
				}
			}
		}
		principalCredits(filter: { categories: ["cast"] }) {
			credits {
				name {
					id
					nameText { text }
				}
			}
		}
		releaseYear { endYear year }
		series {
			displayableEpisodeNumber {
				episodeNumber { text }
				displayableSeason { season }
			}
			series {
				titleText { text }
				originalTitleText { text }
			}
		}
	}
	"""

	query = f"""
	query CalendarPage(
		$comingSoonType: ComingSoonType!,
		$regionOverride: String!,
		$countryOverride: ID!,
		$releasingOnOrAfter: Date!,
		$releasingOnOrBefore: Date!,
		$disablePopularityFilter: Boolean!,
		$after: ID
	) {{
		comingSoon(
			comingSoonType: $comingSoonType,
			first: 250,
			regionOverride: $regionOverride,
			releasingOnOrAfter: $releasingOnOrAfter,
			releasingOnOrBefore: $releasingOnOrBefore,
			disablePopularityFilter: $disablePopularityFilter,
			after: $after,
			sort: [
				{{ sortBy: RELEASE_DATE, sortOrder: ASC }},
				{{ sortBy: POPULARITY, sortOrder: ASC }}
			]
		) {{
			pageInfo {{
				endCursor
				hasNextPage
			}}
			edges {{
				node {{
					...CalendarCard
				}}
			}}
		}}
	}}
	{fragment}
	"""

	today = datetime.datetime.utcnow().date()
	end_date = today + datetime.timedelta(days=360)

	variables = {
		"comingSoonType": coming_soon_type,
		"regionOverride": country,
		"countryOverride": country,
		"releasingOnOrAfter": today.isoformat(),
		"releasingOnOrBefore": end_date.isoformat(),
		"disablePopularityFilter": False,
		"isInPace": False,
		"after": None
	}

	all_titles = []
	while True:
		response = requests.post(API_URL, headers=HEADERS, json={
			"operationName": "CalendarPage",
			"query": query,
			"variables": variables
		})
		#print(response.text)
		data = response.json()["data"]["comingSoon"]
		titles = [edge["node"]["id"] for edge in data["edges"]]
		all_titles.extend(titles)
		if not data["pageInfo"]["hasNextPage"]:
			break
		variables["after"] = data["pageInfo"]["endCursor"]

	return all_titles

def imdb_multi(list_name):
	import requests
	import json
	import datetime

	HEADERS = {
		"Content-Type": "application/json",
		"User-Agent": "Mozilla/5.0",
		"x-imdb-client-name": "imdb-web-next"
	}
	API_URL = "https://api.graphql.imdb.com/"

	BASE_TITLE_CARD_FRAGMENT = """
	fragment BaseTitleCard on Title {
		id
		titleText { text }
		titleType {
			id
			text
			canHaveEpisodes
			displayableProperty { value { plainText } }
		}
		originalTitleText { text }
		primaryImage {
			id
			width
			height
			url
			caption { plainText }
		}
		releaseYear { year endYear }
		ratingsSummary { aggregateRating voteCount }
		runtime { seconds }
		certificate { rating }
		canRate { isRatable }
		titleGenres {
			genres(limit: 3) {
				genre { text }
			}
		}
	}
	"""

	def gqlmin(q):
		return q.replace("	", "")

	def fetch_imdb_ids(category):
		if category not in ["trending", "anticipated", "popular", "recent"]:
			raise ValueError("Invalid category")

		today = datetime.date.today().isoformat()
		variables = {"limit": 600}
		if category == "anticipated":
			variables["queryFilter"] = {"releaseDateRange": {"start": today}}
		elif category == "popular":
			variables["queryFilter"] = {"releaseDateRange": {"end": today}}
		elif category == "recent":
			variables["queryFilter"] = {"contentTypes": ["TRAILER"]}

		if category == "trending":
			opname = "TrendingTitles"
			query = """
			query TrendingTitles($limit: Int!, $paginationToken: String) {
				trendingTitles(limit: $limit, paginationToken: $paginationToken) {
					titles {
						...BaseTitleCard
					}
					paginationToken
				}
			}
			"""
		elif category == "recent":
			opname = "RecentVideos"
			query = """
			query RecentVideos($limit: Int!, $paginationToken: String, $queryFilter: RecentVideosQueryFilter!) {
				recentVideos(limit: $limit, paginationToken: $paginationToken, queryFilter: $queryFilter) {
					videos {
						primaryTitle {
							...BaseTitleCard
						}
					}
					paginationToken
				}
			}
			"""
		else:
			opname = "PopularTitles"
			query = """
			query PopularTitles($limit: Int!, $paginationToken: String, $queryFilter: PopularTitlesQueryFilter!) {
				popularTitles(limit: $limit, paginationToken: $paginationToken, queryFilter: $queryFilter) {
					titles {
						...BaseTitleCard
					}
					paginationToken
				}
			}
			"""

		query += BASE_TITLE_CARD_FRAGMENT
		items = []
		pages = 0
		pagination_token = None
		while len(items) < 600 and pages < 5:
			if pagination_token:
				variables["paginationToken"] = pagination_token
			payload = {
				"operationName": opname,
				"query": gqlmin(query),
				"variables": variables
			}
			response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
			print(response.text)
			if response.status_code != 200:
				raise Exception(f"Query failed: {response.status_code} - {response.text}")
			data = response.json().get("data", {})
			if category == "trending":
				result = data.get("trendingTitles", {})
				titles = result.get("titles", [])
				items.extend([t["id"] for t in titles if "id" in t])
				for t in titles:
					print(t)
			elif category == "recent":
				result = data.get("recentVideos", {})
				videos = result.get("videos", [])
				items.extend([v["primaryTitle"]["id"] for v in videos if v.get("primaryTitle")])
				for t in videos:
					print(t)
			else:
				result = data.get("popularTitles", {})
				titles = result.get("titles", [])
				items.extend([t["id"] for t in titles if "id" in t])
				for t in titles:
					print(t)
			pagination_token = result.get("paginationToken")
			if not pagination_token:
				break
			pages += 1
		return items

	def imdb_movies_near_you(latitude,longitude,radius_meters,start_date,end_date,first=1000,sort_by="POPULARITY",sort_order="ASC"):
		import requests
		API_URL = "https://graphql.prod.api.imdb.a2z.com/"
		HEADERS = {
			'Referer': 'https://www.imdb.com/',
			'Origin': 'https://www.imdb.com',
			'User-Agent': 'Mozilla/5.0',
			'Content-Type': 'application/json'
		}

		query = '''
		query MoviesNearYou($first: Int!, $sort: AdvancedTitleSearchSort!, $constraints: AdvancedTitleSearchConstraints!) {
		  advancedTitleSearch(first: $first, sort: $sort, constraints: $constraints) {
			edges {
			  node {
				title {
				  id
				  titleText { text }
				  ratingsSummary { aggregateRating voteCount }
				  releaseYear { year }
				  primaryImage { url }
				}
			  }
			}
			total
		  }
		}
		'''

		variables = {
			"first": first,
			"sort": {
				"sortBy": sort_by,
				"sortOrder": sort_order
			},
			"constraints": {
				"inTheatersConstraint": {
					"dateTimeRange": {
						"start": f"{start_date}T00:00:00.000Z",
						"end": f"{end_date}T00:00:00.000Z"
					},
					"location": {
						"latLong": {
							"lat": str(latitude),
							"long": str(longitude)
						},
						"radiusInMeters": radius_meters
					}
				}
			}
		}

		response = requests.post(API_URL, headers=HEADERS, json={
			"operationName": "MoviesNearYou",
			"query": query,
			"variables": variables
		})

		def image_url(title_info):
			try:
				if "primaryImage" in title_info and "url" in title_info["primaryImage"]:
					image_url = title_info["primaryImage"]["url"]
				else:
					image_url = ''
				return image_url
			except: return ''

		data = response.json().get("data", {}).get("advancedTitleSearch", {})
		#print(response.text)
		movies = []
		movies_list = []
		for edge in data.get("edges", []):
			title_info = edge["node"]["title"]
			#print(title_info)
			movies_list.append(title_info.get("id"))
			movie = {
				"id": title_info.get("id"),
				"title": title_info.get("titleText", {}).get("text"),
				"rating": title_info.get("ratingsSummary", {}).get("aggregateRating"),
				"vote_count": title_info.get("ratingsSummary", {}).get("voteCount"),
				"release_year": title_info.get("releaseYear", {}).get("year"),
				"image_url": image_url(title_info)

			}
			movies.append(movie)

		return movies_list

	if list_name == 'ls_trending':
		movies_list = fetch_imdb_ids("trending")
	elif list_name == 'ls_anticipated':
		movies_list = fetch_imdb_ids("anticipated")
	elif list_name == 'ls_popular':
		movies_list = fetch_imdb_ids("popular")
	elif list_name == 'ls_recent':
		movies_list = fetch_imdb_ids("recent")
	return movies_list


"""
def get_imdb_watchlist_ids_1(ur_list_str=None, limit=0):
	import requests
	list_str=ur_list_str

	imdb_url = 'https://www.imdb.com/user/'+str(list_str)+'/watchlist'
	imdb_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
	imdb_response = requests.get(imdb_url, headers=imdb_header)

	list_container = str(imdb_response.text,).split('<')
	#xbmc.log(str(list_container)+'===>OPENINFO', level=xbmc.LOGINFO)
	processed_list = []
	movies = []
	for i in list_container:
		if 'href="/title/tt' in i:
			imdb_number = 'tt' + i.split('href="/title/tt')[1].split('/?r')[0]
			if imdb_number in processed_list:
				continue
			processed_list.append(imdb_number)
			movies.append(imdb_number)

	return movies
"""

def get_imdb_watchlist_items(movies=None, limit=0, cache_days=14, folder='IMDB', imdb_url=None):
	import time, hashlib, xbmcvfs, os
	import re, json, requests, html

	if imdb_url:
		url = imdb_url +'/get_imdb_watchlist_items'
	else:
		url = 'imdb_'
		for i in movies:
			url = url + str(i) +'/get_imdb_watchlist_items'

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
		db_result = Utils.query_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder, headers=None)
	except:
		db_result = None
	if db_result and len(db_result) > 0:
		return db_result
	else:
	#if xbmcvfs.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
	#	listitems = Utils.read_from_file(path)
	#else:

		listitems = None
		x = 0
		if not movies:
			return None
		for y in movies:
			imdb_id = y
			response = get_tmdb_data('find/%s?language=%s&external_source=imdb_id&' % (imdb_id, xbmcaddon.Addon().getSetting('LanguageID')), 13)
			try:
				response['movie_results'][0]['media_type'] = 'movie'
				if listitems == None:
					listitems = handle_tmdb_multi_search(response['movie_results'])
				else:
					listitems += handle_tmdb_multi_search(response['movie_results'])
			except:
				try:
					response['tv_results'][0]['media_type'] = 'tv'
					if listitems == None:
						listitems = handle_tmdb_multi_search(response['tv_results'])
					else:
						listitems += handle_tmdb_multi_search(response['tv_results'])
				except:
					continue
			if x + 1 == int(limit) and limit != 0:
				break
			x = x + 1

		Utils.write_db(connection=Utils.db_con,url=url, cache_days=cache_days, folder=folder,cache_val=listitems)
		#try:
		#	Utils.save_to_file(listitems, hashed_url, cache_path)
		#except:
		#	Utils.log('Exception: Could not get new JSON data from %s. Tryin to fallback to cache' % url)
		#	Utils.log(response)
		#	results = Utils.read_from_file(path) if xbmcvfs.exists(path) else []

	if not listitems:
		return []
	#xbmcgui.Window(10000).setProperty('%s_timestamp' % hashed_url, str(now))
	#xbmcgui.Window(10000).setProperty(hashed_url, json.dumps(listitems))

	return listitems





"""
def get_imdb_list(list_str=None, limit=0):
	list_str=list_str
	from imdb import IMDb, IMDbError
	ia = IMDb()
	movies = ia.get_movie_list(list_str)
	listitems = None
	x = 0
	for i in str(movies).split(', <'):
		imdb_id = str('tt' + i.split(':')[1].split('[http]')[0])
		movie_title = str(i.split(':_')[1].split('_>')[0])
		response = get_tmdb_data('find/%s?language=%s&external_source=imdb_id&' % (imdb_id, xbmcaddon.Addon().getSetting('LanguageID')), 13)
		try:
			response['movie_results'][0]['media_type'] = 'movie'
			if listitems == None:
				listitems = handle_tmdb_multi_search(response['movie_results'])
			else:
				listitems += handle_tmdb_multi_search(response['movie_results'])
		except:
			try:
				response['tv_results'][0]['media_type'] = 'tv'
				if listitems == None:
					listitems = handle_tmdb_multi_search(response['tv_results'])
				else:
					listitems += handle_tmdb_multi_search(response['tv_results'])
			except:
				continue
		if x + 1 == int(limit) and limit != 0:
			break
		x = x + 1
	return listitems
"""

