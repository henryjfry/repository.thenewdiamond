import re
import xbmc, xbmcgui, xbmcaddon
from resources.lib import Utils
from resources.lib import local_db
from resources.lib.WindowManager import wm
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib.library import fanart_api_key

ext_key = xbmcaddon.Addon().getSetting('tmdb_api')

if len(ext_key) == 32:
    API_key = ext_key
else:
    API_key = '1248868d7003f60f2386595db98455ef'

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
            listitem = handle_tmdb_people([item])[0]
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
        listitem = {
            'media_type': 'episode',
            'mediatype': 'episode',
            'title': title,
            'release_date': Utils.fetch(item, 'air_date'),
            'episode': Utils.fetch(item, 'episode_number'),
            'production_code': Utils.fetch(item, 'production_code'),
            'season': Utils.fetch(item, 'season_number'),
            'Rating': round(float(Utils.fetch(item, 'vote_average')), 1),
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

def get_movie_info(movie_label, year=None, use_dialog=True):
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

def get_tvshow_info(tvshow_label, year=None, use_dialog=True):
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

def get_tastedive_data(url='', query='', limit=20, media_type=None, cache_days=14, folder='TasteDive'):
    url = 'https://tastedive.com/api/similar?info=1&q='+str(query)+'&limit=' + str(limit)
    if media_type:
        if 'movie' in media_type:
            url = url.replace('&q=','&q=movie:') + '&type=' + 'movies'
        else:
            url = url.replace('&q=','&q=show:')  + '&type=' + 'shows'
    response = Utils.get_JSON_response(url, cache_days, folder)
    result = []
    for i in response['Similar']['Results']:
        for x in i['wTeaser'].split(' '):
            if len(x) == 4 and x.isnumeric():
                result.append({'name': i['Name'], 'year': x, 'media_type': i['Type']})
                break
    return result

def get_tastedive_items(movies, page=0):
    responses = {'page': 1, 'results': [],'total_pages': 1, 'total_results': 0}
    for i in movies:
        if (x + 1 <= page * 20 and x + 1 > (page - 1) *  20) or page == 0:
            try: 
                if 'movie' in i['media_type']:
                    response1 = get_movie_info(i['name'], year=i['year'], use_dialog=False)
                    if not response1:
                        response1 = get_movie_info(i['name'], use_dialog=False)
                    response1['media_type'] = 'movie'
                elif 'show' in i['media_type']:
                    response1 = get_tvshow_info(i['name'], year=i['year'], use_dialog=False)
                    if not response1:
                        response1 = get_tvshow_info(i['name'], use_dialog=False)
                    response1['media_type'] = 'tv'
            except TypeError:
                continue
            responses['results'].append(response1)
            x = x + 1
        else:
            x = x + 1
    total_pages = int(x/20) + (1 if x % 20 > 0 else 0)
    total_results = x
    responses['total_pages'] = total_pages
    responses['total_results'] = total_results
    listitems = handle_tmdb_multi_search(responses['results'])
    return listitems

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

def single_movie_info(movie_id=None, dbid=None, cache_time=14):
    if not movie_id:
        return None
    session_str = ''
    response = get_tmdb_data('movie/%s?append_to_response=external_ids,alternative_titles&language=%s&%s' % (movie_id, xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
    #response = get_tmdb_data('movie/%s?append_to_response=alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,rating&include_image_language=en,null,%s&language=%s&%s' % (movie_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
    if not response:
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
        'alternative_titles': response['alternative_titles'],
        'overview': response['overview'],
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
    response = get_tmdb_data('tv/%s?append_to_response=external_ids,alternative_titles&language=%s&%s' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
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
        'origin_country': response['origin_country'],
        'original_language': response['original_language'],
        'original_name': response['original_name'],
        'alternative_titles': alternative_titles,
        'overview': response['overview'],
        'popularity': response['popularity'],
        'poster_path': response['poster_path'],
        'vote_average': response['vote_average'],
        'vote_count': response['vote_count']
        }
    return results

def extended_movie_info(movie_id=None, dbid=None, cache_time=14):
    if not movie_id:
        return None
    session_str = ''
    response = get_tmdb_data('movie/%s?append_to_response=alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,rating&include_image_language=en,null,%s&language=%s&%s' % (movie_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
    if not response:
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
    listitems = {
        'actors': handle_tmdb_people(response['credits']['cast']),
        'similar': handle_tmdb_movies(response['similar']['results']),
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
    response = get_tmdb_data('tv/%s?append_to_response=alternative_titles,content_ratings,credits,external_ids,images,keywords,rating,similar,translations,videos&language=%s&include_image_language=en,null,%s&%s' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
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
    listitems = {
        'actors': handle_tmdb_people(response['credits']['cast']),
        'similar': handle_tmdb_tvshows(response['similar']['results']),
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
    tvshow = get_tmdb_data('tv/%s?append_to_response=alternative_titles,content_ratings,credits,external_ids,images,keywords,rating,similar,translations,videos&language=%s&include_image_language=en,null,%s&%s' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), 99999)
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
    tvshow = get_tmdb_data('tv/%s?append_to_response=alternative_titles,content_ratings,credits,external_ids,images,keywords,rating,similar,translations,videos&language=%s&include_image_language=en,null,%s&%s' % (tvshow_id, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), 99999)
    response = get_tmdb_data('tv/%s/season/%s/episode/%s?append_to_response=credits,external_ids,images,rating,videos&language=%s&include_image_language=en,null,%s&%s&' % (tvshow_id, season, episode, xbmcaddon.Addon().getSetting('LanguageID'), xbmcaddon.Addon().getSetting('LanguageID'), session_str), cache_time)
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
    answer = {
        'SeasonDescription': Utils.clean_text(response['overview']),
        'Plot': Utils.clean_text(response['overview']),
        'TVShowTitle': TVShowTitle,
        'tvshow_id': tmdb_id,
        'tvdb_id': tvdb_id,
        'actors': actors,
        'path': 'plugin://'+str(addon_ID())+'?info=extendedepisodeinfo&tvshow_id=%s&season=%s&episode=%s' % (tvshow_id, season, episode),
        'crew': crew,
        'guest_stars': guest_stars,
        'videos': videos,
        'images': images
        }
    return (handle_tmdb_episodes([response])[0], answer)

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

def get_imdb_recommendations(imdb_id=None, return_items=False):
    import requests
    imdb_url = 'https://www.imdb.com/title/' + str(imdb_id)
    imdb_response = requests.get(imdb_url)
    #imdb_response.text

    list_container = str(imdb_response.text).split('<')
    toggle = False
    movies = []
    for i in list_container:
        if 'StaticFeature_MoreLikeThis' in str(i):
            toggle = True
        if toggle == True:
            if '/title/tt' in str(i):
                for y in str(i).split('"'):
                    if '/title/tt' in str(y):
                        for j in str(y).split('/'):
                            if 'tt' in str(j) and str(j).replace('tt','').isnumeric():
                                if str(j) not in str(movies):
                                    movies.append(j)
        if 'StaticFeature_Storyline' in str(i):
            toggle = False
    if return_items == False:
        return movies
    else:
        return get_imdb_watchlist_items(movies=movies, limit=0)

def get_imdb_watchlist_ids_1(ur_list_str=None, limit=0):
    import requests
    list_str=ur_list_str

    imdb_url = 'https://www.imdb.com/user/'+str(list_str)+'/watchlist'
    imdb_response = requests.get(imdb_url)

    from bs4 import BeautifulSoup

    html_soup = BeautifulSoup(imdb_response.text, 'html.parser')

    episode_containers = html_soup.find_all('div', class_='article')

    list_container = str(episode_containers[0]).split('{')

    movies = []
    x = 0
    for i in list_container:
        if 'TITLE_TYPE' in str(i):
            break
        if 'position' in str(i):
            #i
            imdb_dict = str(list_container[x + 1]).split('"')
            for y in imdb_dict:
                if 'tt' in str(y):
                    movies.append(y)
        x = x + 1
    return movies

def get_imdb_list_ids(list_str=None, limit=0):
    import requests
    import time
    movies = []
    curr_time = time.time()
    if str(list_str) == 'ls_top_1000':
        movies = imdb_top_1000()
        return movies
    imdb_url = 'https://www.imdb.com/list/title/'+str(list_str)+'/_ajax'
    imdb_response = requests.get(imdb_url)

    #from bs4 import BeautifulSoup

    #html_soup = BeautifulSoup(imdb_response.text, 'html.parser')

    #episode_containers = html_soup.find_all('div', class_='article')
    #try: list_container = str(episode_containers[0]).split('<')
    #except: list_container = str(html_soup).split('<')
    movies = []
    page_containers = None
    list_container = str(imdb_response.text,).split('<')
    for i in list_container:
        if '/title/tt' in str(i):
            for y in str(i).split('/'):
                if 'tt' in str(y) and '\n' not in str(y) and '"' not in str(y):
                    if str(y) not in str(movies):
                        movies.append(y)
                        break
        if 'page-next next-page' in str(i):
            page_containers = i
    #page_containers = html_soup.find_all('div', class_='list-pagination')

    while page_containers:
        url = ''
        if 'href' in str(page_containers) and 'page=' in str(page_containers) and not 'prev-page' in str(page_containers):
            for y in str(page_containers).split('"'):
                if 'ls' in y:
                    url = 'https://www.imdb.com' + str(y).replace('/?page=','/_ajax?page=')
                    break
                else:
                    url = ''
        if url != '':
            page_containers = None
            imdb_response = requests.get(url)
            #html_soup = BeautifulSoup(imdb_response.text, 'html.parser')
            #episode_containers = html_soup.find_all('div', class_='article')
            #list_container = str(episode_containers[0]).split('<')
            list_container = str(imdb_response.text).split('<')
            for i in list_container:
                if '/title/tt' in str(i):
                    for y in str(i).split('/'):
                        if 'tt' in str(y) and '\n' not in str(y) and '"' not in str(y):
                            if str(y) not in str(movies):
                                movies.append(y)
                                break
                if 'page-next next-page' in str(i):
                    page_containers = i
            #page_containers = html_soup.find_all('div', class_='list-pagination')
        else:
            page_containers = None
    del list_container
    del imdb_response
    return movies

def imdb_top_1000():
    imdb_1 = 'https://www.imdb.com/search/title/?count=250&groups=top_1000&countries=%21in&sort=user_rating'
    imdb_2 = 'https://www.imdb.com/search/title/?groups=top_1000&countries=%21in&sort=user_rating,desc&count=250&start=251&ref_=adv_nxt'
    imdb_3 = 'https://www.imdb.com/search/title/?groups=top_1000&countries=%21in&sort=user_rating,desc&count=250&start=501&ref_=adv_nxt'
    imdb_4 = 'https://www.imdb.com/search/title/?groups=top_1000&countries=%21in&sort=user_rating,desc&count=250&start=751&ref_=adv_nxt'

    import requests
    imdb_response = requests.get(imdb_1)
    list_container = str(imdb_response.text,).split('<')

    movies = []

    x = 0
    for i in list_container:
        x = x + 1
        if 'title/tt' in str(i) and 'href' in str(i) and 'Delete' not in str(i):
            if len(i.split('/')) >= 3 and len(list_container[x].split('"')) >= 2:
                imdb = i.split('/')[2]
                title = list_container[x].split('"')[1]
                year = list_container[x+9].split('(')[1].split(')')[0]
                movies.append(imdb)

    imdb_response = requests.get(imdb_2)
    list_container = str(imdb_response.text,).split('<')

    x = 0
    for i in list_container:
        x = x + 1
        if 'title/tt' in str(i) and 'href' in str(i) and 'Delete' not in str(i):
            if len(i.split('/')) >= 3 and len(list_container[x].split('"')) >= 2:
                imdb = i.split('/')[2]
                title = list_container[x].split('"')[1]
                year = list_container[x+9].split('(')[1].split(')')[0]
                movies.append(imdb)

    imdb_response = requests.get(imdb_3)
    list_container = str(imdb_response.text,).split('<')

    x = 0
    for i in list_container:
        x = x + 1
        if 'title/tt' in str(i) and 'href' in str(i) and 'Delete' not in str(i):
            if len(i.split('/')) >= 3 and len(list_container[x].split('"')) >= 2:
                imdb = i.split('/')[2]
                title = list_container[x].split('"')[1]
                year = list_container[x+9].split('(')[1].split(')')[0]
                movies.append(imdb)

    imdb_response = requests.get(imdb_4)
    list_container = str(imdb_response.text,).split('<')

    x = 0
    for i in list_container:
        x = x + 1
        if 'title/tt' in str(i) and 'href' in str(i) and 'Delete' not in str(i):
            if len(i.split('/')) >= 3 and len(list_container[x].split('"')) >= 2:
                imdb = i.split('/')[2]
                title = list_container[x].split('"')[1]
                year = list_container[x+9].split('(')[1].split(')')[0]
                movies.append(imdb)

    del list_container
    del imdb_response
    return movies


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
            if 'latest' in str(i['list']['name']).lower():
                i['list']['sort_by'] = 'listed_at'
                i['list']['sort_how'] = 'desc'
            #i['list']['sort_by'] = 'rank'
            #i['list']['sort_by'] = 'popularity'
            #i['list']['sort_how'] = 'asc'
            trakt_list['trakt_list'].append({'name': 'Trakt - ' + i['list']['name'] + '('+str(i['list']['item_count'])+')', 'user_id': i['list']['user']['ids']['slug'], 'list_slug': i['list']['ids']['trakt'], "sort_by": i['list']['sort_by'], "sort_order": i['list']['sort_how']})
    return trakt_list

def get_imdb_userlists():
    imdb_id = xbmcaddon.Addon().getSetting('imdb_ur_id')
    if imdb_id == '':
        return None
    import requests
    imdb_url = 'https://www.imdb.com/user/'+str(imdb_id)+'/lists'
    imdb_response = requests.get(imdb_url)
    list_container = str(imdb_response.text,).split('<')
    imdb_list = {}
    imdb_list['imdb_list'] = []
    

    for i in list_container:
        if 'meta property=\'og:title\' content="' in i:
            imdb_user_name = i.split('"')[1].replace('Lists - IMDb','')
            imdb_user_name = 'IMDB - %s Watchlist' % (imdb_user_name)
            imdb_list['imdb_list'].append({imdb_id: imdb_user_name})
        if 'a class="list-name"' in i:
            list_number = i.split('/')[2]
            list_name = 'IMDB - ' + i.split('/')[3].replace('">','')
            imdb_list['imdb_list'].append({list_number: list_name})
        
            
    return imdb_list

def get_imdb_userlists_search(imdb_id=None):
    imdb_id = imdb_id
    if imdb_id == '':
        return None
    import requests
    imdb_url = 'https://www.imdb.com/user/'+str(imdb_id)+'/lists'
    imdb_response = requests.get(imdb_url)
    list_container = str(imdb_response.text,).split('<')
    imdb_list = {}
    imdb_list['imdb_list'] = []
    

    for i in list_container:
        if 'meta property=\'og:title\' content="' in i:
            imdb_user_name = i.split('"')[1].replace('Lists - IMDb','')
            imdb_user_name = 'IMDB - %s Watchlist' % (imdb_user_name)
            imdb_list['imdb_list'].append({imdb_id: imdb_user_name})
        if 'a class="list-name"' in i:
            list_number = i.split('/')[2]
            list_name = 'IMDB - ' + i.split('/')[3].replace('">','')
            imdb_list['imdb_list'].append({list_number: list_name})
        
            
    return imdb_list


def get_imdb_watchlist_ids(ur_list_str=None, limit=0):
    import requests
    list_str=ur_list_str

    imdb_url = 'https://www.imdb.com/user/'+str(list_str)+'/watchlist'
    imdb_response = requests.get(imdb_url)

    #from bs4 import BeautifulSoup

    #html_soup = BeautifulSoup(imdb_response.text, 'html.parser')

    #episode_containers = html_soup.find_all('div', class_='article')

    list_container = str(imdb_response.text,).split('<')
    for i in list_container:
        if 'IMDbReactWidgets.WatchlistWidget.push' in str(i):
            list_container2 = i
            break

    try: imdb_dict = str(list_container2).split('{')
    except: return None
    movies = []
    x = 0
    for i in imdb_dict:
        if 'TITLE_TYPE' in str(i):
            break
        if 'position' in str(i):
            #i
            imdb_dict2 = str(imdb_dict[x + 1]).split('"')
            for y in imdb_dict2:
                if 'tt' in str(y):
                    movies.append(y)
        x = x + 1
    del list_container
    del list_container2
    del imdb_dict2
    del imdb_dict
    del imdb_response
    return movies

def get_imdb_watchlist_items(movies=None, limit=0):
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

    return listitems


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

def get_trakt_lists(list_name=None,user_id=None,list_slug=None,sort_by=None,sort_order=None,limit=0):
    from resources.lib.library import trakt_lists
    movies = trakt_lists(list_name,user_id,list_slug,sort_by,sort_order)
    listitems = None
    x = 0
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
                listitems.append(single_movie_info(response[result_type][0]['id']))
            else:
                listitems.append(single_tvshow_info(response[result_type][0]['id']))
    #Utils.show_busy()
        if x + 1 == int(limit) and limit != 0:
            break
        x = x + 1
    return listitems


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