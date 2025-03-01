import sys
import xbmc, xbmcaddon
import requests,json
from resources.lib.library import addon_ID
from resources.lib import Utils
#ext_key = xbmcaddon.Addon().getSetting('tmdb_api')

#if len(ext_key) == 32:
#	API_key = ext_key
#else:
#	API_key = '1248868d7003f60f2386595db98455ef'


if __name__ == '__main__':
	def context_trakt_in_lists():
		from resources.lib.library import trakt_in_lists
		search_str = sys.listitem.getProperty('title')
		Utils.show_busy()
		info = sys.listitem.getVideoInfoTag()
		type = info.getMediaType()
		year = info.getYear()
		item_id = info.getUniqueID('tmdb')
		imdb_id = info.getUniqueID('imdb')

		imdb_id2 = info.getIMDBNumber()
		if 'tt' in imdb_id:
			imdb_id = imdb_id
		if 'tt' in imdb_id2 and imdb_id2 != imdb_id:
			imdb_id = imdb_id2
		#if xbmc.getInfoLabel('listitem.DBTYPE') == 'movie' or type == 'movie':
		#	self_type = 'movie'
		#elif xbmc.getInfoLabel('listitem.DBTYPE') in ['tv', 'tvshow', 'season', 'episode']:
		#	self_type = 'tv'
		#elif sys.listitem.getProperty('TVShowTitle'):
		#	self_type = 'tv'
		#else:
		#	self_type = 'movie'
		#if self_type == 'tv':
		#	media_type = 'tv'
		#	#imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'imdb_id')
		#else:
		#	media_type = 'movie'
		#	imdb_id = TheMovieDB.get_imdb_id_from_movie_id(item_id)
		xbmc.log(str(imdb_id)+'===>PHIL', level=xbmc.LOGINFO)
		list_name, user_id, list_slug, sort_by, sort_order = trakt_in_lists(type=type,imdb_id=imdb_id,return_var=None)
		if list_name == None or list_name == '':
			Utils.hide_busy()
			return
		#Utils.hide_busy()
		xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=trakt_list,trakt_type=%s,trakt_label=%s,user_id=%s,list_slug=%s,trakt_sort_by=%s,trakt_sort_order=%s,trakt_list_name=%s,keep_stack=True,script=True)' % (type,list_name,user_id,list_slug,sort_by,sort_order,list_name))
	context_trakt_in_lists()
