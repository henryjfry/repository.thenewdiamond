import sys
import xbmc, xbmcaddon
import requests,json
from resources.lib import TheMovieDB

#ext_key = xbmcaddon.Addon().getSetting('tmdb_api')

#if len(ext_key) == 32:
#	API_key = ext_key
#else:
#	API_key = '1248868d7003f60f2386595db98455ef'


if __name__ == '__main__':
	base = 'RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type='
	info = sys.listitem.getVideoInfoTag()
	type = info.getMediaType()
	year = info.getYear()
	if type == 'movie':
		title = info.getTitle()
		tmdb_type = 'movie'
		year_field = '&primary_release_year=' + str(year)
	elif type == 'tvshow' or type == 'season' or type == 'episode':
		title = info.getTVShowTitle()
		tmdb_type = 'tv'
		if type == 'tvshow':
			year_field = '&first_air_date_year=' + str(year)
		else:
			year_field = ''
	language = xbmcaddon.Addon().getSetting('LanguageID')
	try:
		response = TheMovieDB.get_tmdb_data('search/%s?query=%s%s&language=en-US&include_adult=%s&' % (tmdb_type, title, year_field, xbmcaddon.Addon().getSetting('include_adults')), 30)
		#url = 'https://api.themoviedb.org/3/search/'+str(tmdb_type)+'?api_key='+str(API_key)+'&language='+str(language)+'&page=1&query='+str(title)+'&include_adult=false&first_air_date_year='+str(year)
		#response = requests.get(url).json()
		tmdb_id = response['results'][0]['id']
	except:
		response = TheMovieDB.get_tmdb_data('search/%s?query=%s%s&language=%s&include_adult=%s&' % (tmdb_type, title, year_field, language, xbmcaddon.Addon().getSetting('include_adults')), 30)
		#url = 'https://api.themoviedb.org/3/search/'+str(tmdb_type)+'?api_key='+str(API_key)+'&language='+str(language)+'&page=1&query='+str(title)+'&include_adult=false'
		#response = requests.get(url).json()
		tmdb_id = response['results'][0]['id']

	if type == 'movie':
		xbmc.executebuiltin('%s%s,tmdb_id=%s)' % (base, type, tmdb_id))
	elif type == 'tvshow':
		xbmc.executebuiltin('%s%s,tmdb_id=%s)' % (base, type, tmdb_id))
	elif type == 'season':
		xbmc.executebuiltin('%s%s,tmdb_id=%s,season=%s)' % (base, type, tmdb_id, info.getSeason()))
	elif type == 'episode':
		xbmc.executebuiltin('%s%s,tmdb_id=%s,season=%s,episode=%s)' % (base, type, tmdb_id, info.getSeason(), info.getEpisode()))

