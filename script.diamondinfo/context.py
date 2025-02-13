import sys
import xbmc
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib import process

if __name__ == '__main__':
	base = 'RunScript('+str(addon_ID())+',info='
	info = sys.listitem.getVideoInfoTag()
	dbid = info.getDbId() if info.getDbId() else sys.listitem.getProperty('dbid')
	type = info.getMediaType()

	if not type in ['movie','tvshow','season','episode','actor','director']:
		if xbmc.getInfoLabel('listitem.DBTYPE') == 'movie':
			type = 'movie'
		elif xbmc.getInfoLabel('listitem.DBTYPE') in ['tv', 'tvshow', 'season', 'episode']:
			type = 'tvshow'

	try: imdb_id = info.getUniqueID('imdb')
	except: imdb_id = None
	try: tmdb_id = info.getUniqueID('tmdb')
	except: tmdb_id = None
	try: tvdb_id = info.getUniqueID('tvdb')
	except: tvdb = None
	if tmdb_id:
		remote_id = tmdb_id
	else:
		remote_id = sys.listitem.getProperty('id')
	params = {}
	infos = []
	if type   == 'movie':
		base = 'RunScript('+str(addon_ID())+',info='+str(addon_ID_short())
		infos.append(str(addon_ID_short()))
		params['dbid'] = dbid
		if tmdb_id:
			params['id'] = tmdb_id
		else:
			params['id'] = remote_id
		if imdb_id:
			params['imdb_id'] = imdb_id
		else:
			params['imdb_id'] = info.getIMDBNumber()
		params['name'] = info.getTitle()
		url = '%s,dbid=%s,id=%s,imdb_id=%s,name=%s)' % (base, params['dbid'], params['id'], params['imdb_id'], params['name'])
		#xbmc.executebuiltin(url)
	elif type == 'tvshow':
		infos.append('extendedtvinfo')
		params['dbid'] = dbid
		if tmdb_id:
			params['id'] = tmdb_id
		else:
			params['id'] = remote_id
		if imdb_id:
			params['imdb_id'] = imdb_id
		else:
			params['imdb_id'] = info.getIMDBNumber()
		params['name'] = info.getTitle()
		#xbmc.executebuiltin('%sextendedtvinfo,dbid=%s,id=%s,name=%s)' % (base, dbid, remote_id, info.getTVShowTitle()))
	elif type == 'season':
		infos.append('seasoninfo')
		params['dbid'] = dbid
		if tmdb_id:
			params['id'] = tmdb_id
		else:
			params['id'] = remote_id
		params['tvshow'] = info.getTVShowTitle()
		params['season'] = info.getSeason()
		#xbmc.executebuiltin('%sseasoninfo,dbid=%s,id=%s,tvshow=%s,season=%s)' % (base, dbid, remote_id, info.getTVShowTitle(), info.getSeason()))
	elif type == 'episode':
		infos.append('extendedepisodeinfo')
		params['dbid'] = dbid
		if tmdb_id:
			params['id'] = tmdb_id
		else:
			params['id'] = remote_id
		params['tvshow'] = info.getTVShowTitle()
		params['season'] = info.getSeason()
		params['episode'] = info.getEpisode()
		#xbmc.executebuiltin('%sextendedepisodeinfo,dbid=%s,id=%s,tvshow=%s,season=%s,episode=%s)' % (base, dbid, remote_id, info.getTVShowTitle(), info.getSeason(), info.getEpisode()))
	elif type in ['actor', 'director']:
		infos.append('extendedactorinfo')
		params['name'] = sys.listitem.getLabel()
		#xbmc.executebuiltin('%sextendedactorinfo,name=%s)' % (base, sys.listitem.getLabel()))
	if infos:
		process.start_info_actions(infos, params)