# -*- coding: utf-8 -*-
import sys
from apis.mdblist_api import mdbl_get_lists, mdbl_get_liked_lists, mdbl_top_lists, get_mdbl_list_contents, mdbl_list_media_type, mdbl_unified_item_tmdb_id
from indexers.movies import Movies
from indexers.tvshows import TVShows
from modules import kodi_utils, settings

def _mdbl_parent_exit_path(params=None):
	folder_path = kodi_utils.folder_path()
	parent_tokens = ('navigator.mdblist_lists', 'navigator.my_lists', 'get_mdbl_lists', 'get_mdbl_liked_lists', 'get_mdbl_top_lists')
	if any(token in folder_path for token in parent_tokens): return kodi_utils.sanitize_folder_url(folder_path)
	params = params or {}
	list_type = params.get('list_type', 'my_lists')
	media_type = params.get('media_type', 'movie')
	if list_type == 'liked_lists':
		label = 'Movies Liked Lists' if media_type in ('movie', 'movies') else 'TV Shows Liked Lists'
		return kodi_utils.build_folder_url({'mode': 'mdblist.get_mdbl_liked_lists', 'name': label, 'media_type': media_type})
	if list_type == 'user_lists':
		return kodi_utils.build_folder_url({'mode': 'mdblist.get_mdbl_top_lists', 'name': 'Popular MDBLists', 'media_type': media_type})
	return kodi_utils.build_folder_url({'mode': 'mdblist.get_mdbl_lists', 'name': 'My Lists', 'media_type': media_type})

def _set_mdbl_browse_exit_params():
	if kodi_utils.external(): return
	kodi_utils.set_property('redlight.exit_params', _mdbl_parent_exit_path())

def _set_mdbl_list_exit_params(params):
	if kodi_utils.external(): return
	try: page_no = int(params.get('new_page', '1'))
	except: page_no = 1
	if page_no != 1: return
	kodi_utils.set_property('redlight.exit_params', _mdbl_parent_exit_path(params))

def get_mdbl_lists(params):
	def _process():
		for item in lists:
			try:
				name, list_id = item.get('name', ''), item.get('id')
				list_type = 'external' if item.get('source') else 'my_lists'
				count = item.get('items', '?')
				display = '%s (x%s)' % (name, count)
				if list_type == 'external': display = '[COLOR cyan][I]%s[/I][/COLOR]' % display
				elif item.get('dynamic'): display = '[COLOR magenta][I]%s[/I][/COLOR]' % display
				url = build_url({'mode': 'mdblist.build_mdbl_list', 'list_id': list_id, 'list_type': list_type, 'list_name': name,
					'media_type': mdbl_list_media_type(item, params.get('media_type', 'movie'))})
				listitem = kodi_utils.make_listitem()
				listitem.setLabel(display)
				listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': fanart})
				info_tag = listitem.getVideoInfoTag(True)
				info_tag.setPlot(' ')
				yield (url, listitem, True)
			except: pass
	handle = int(sys.argv[1])
	_set_mdbl_browse_exit_params()
	icon, fanart, build_url = kodi_utils.get_icon('mdblist'), kodi_utils.get_addon_fanart(), kodi_utils.build_url
	lists = mdbl_get_lists('my_lists') + mdbl_get_lists('external')
	kodi_utils.add_items(handle, list(_process()))
	kodi_utils.set_content(handle, kodi_utils.MENU_FOLDER_CONTENT)
	kodi_utils.set_category(handle, params.get('name', 'MDBList Lists'))
	kodi_utils.end_directory(handle)
	kodi_utils.set_view_mode('view.main', kodi_utils.MENU_FOLDER_CONTENT)

def get_mdbl_liked_lists(params):
	def _process():
		for item in lists:
			try:
				name, list_id = item.get('name', ''), item.get('id')
				user = item.get('user_name', '')
				count = item.get('items', '?')
				if user: display = '[B]%s[/B] | [I](x%s) - %s[/I]' % (name, count, user)
				else: display = '%s (x%s)' % (name, count)
				url = build_url({'mode': 'mdblist.build_mdbl_list', 'list_id': list_id, 'list_type': 'liked_lists', 'list_name': name, 'media_type': params.get('media_type', 'movie')})
				listitem = kodi_utils.make_listitem()
				listitem.setLabel(display)
				listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': fanart})
				info_tag = listitem.getVideoInfoTag(True)
				info_tag.setPlot(' ')
				yield (url, listitem, True)
			except: pass
	handle = int(sys.argv[1])
	_set_mdbl_browse_exit_params()
	icon, fanart, build_url = kodi_utils.get_icon('mdblist'), kodi_utils.get_addon_fanart(), kodi_utils.build_url
	media_type = params.get('media_type', 'movie')
	lists = mdbl_get_liked_lists(media_type)
	kodi_utils.add_items(handle, list(_process()))
	kodi_utils.set_content(handle, kodi_utils.MENU_FOLDER_CONTENT)
	label = 'Movies Liked Lists' if media_type in ('movie', 'movies') else 'TV Shows Liked Lists'
	kodi_utils.set_category(handle, params.get('name', label))
	kodi_utils.end_directory(handle)
	kodi_utils.set_view_mode('view.main', kodi_utils.MENU_FOLDER_CONTENT)

def get_mdbl_top_lists(params):
	def _process():
		for item in lists:
			try:
				name, list_id = item.get('name', ''), item.get('id')
				user = item.get('user_name', '')
				count = item.get('items', '?')
				display = '[B]%s[/B] | [I](x%s) - %s[/I]' % (name, count, user)
				url = build_url({'mode': 'mdblist.build_mdbl_list', 'list_id': list_id, 'list_type': 'user_lists', 'list_name': name,
					'media_type': mdbl_list_media_type(item, params.get('media_type', 'movie'))})
				listitem = kodi_utils.make_listitem()
				listitem.setLabel(display)
				listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': fanart})
				info_tag = listitem.getVideoInfoTag(True)
				info_tag.setPlot(' ')
				yield (url, listitem, True)
			except: pass
	handle = int(sys.argv[1])
	_set_mdbl_browse_exit_params()
	icon, fanart, build_url = kodi_utils.get_icon('mdblist'), kodi_utils.get_addon_fanart(), kodi_utils.build_url
	lists = mdbl_top_lists()
	kodi_utils.add_items(handle, list(_process()))
	kodi_utils.set_content(handle, kodi_utils.MENU_FOLDER_CONTENT)
	kodi_utils.set_category(handle, params.get('name', 'Popular MDBLists'))
	kodi_utils.end_directory(handle)
	kodi_utils.set_view_mode('view.main', kodi_utils.MENU_FOLDER_CONTENT)

def _mdbl_item_tmdb_id(item):
	return mdbl_unified_item_tmdb_id(item)

def _mdbl_route_media_type(params, items):
	media_type = params.get('media_type', 'movie')
	if media_type in ('tv', 'tvshow', 'show', 'shows', 'series'):
		return 'tvshow'
	if media_type in ('movie', 'movies') and items:
		from apis.mdblist_api import _mdbl_item_media_kind
		kinds = {_mdbl_item_media_kind(i) for i in items[:10] if isinstance(i, dict)}
		if kinds and kinds <= {'show'}:
			return 'tvshow'
	return 'movie'

def build_mdbl_watchlist(params):
	_set_mdbl_list_exit_params(params)
	media_type = params.get('media_type', 'movie')
	media_kind = 'movies' if media_type in ('movie', 'movies') else 'shows'
	from apis.mdblist_api import mdblist_watchlist
	data, _ = mdblist_watchlist(media_kind, 1)
	id_list = [_mdbl_item_tmdb_id(i) for i in (data or [])]
	id_list = [i for i in id_list if i]
	category = params.get('category_name') or params.get('name') or ('Movies Watchlist' if media_kind == 'movies' else 'TV Shows Watchlist')
	params.update({'list': id_list, 'action': 'mdblist_user_list', 'category_name': category})
	if media_type in ('movie', 'movies'):
		return Movies(params).fetch_list()
	return TVShows(params).fetch_list()

def build_mdbl_library(params):
	_set_mdbl_list_exit_params(params)
	media_type = params.get('media_type', 'movie')
	media_kind = 'movies' if media_type in ('movie', 'movies') else 'shows'
	from apis.mdblist_api import mdblist_collection
	data, _ = mdblist_collection(media_kind, 1)
	id_list = [_mdbl_item_tmdb_id(i) for i in (data or [])]
	id_list = [i for i in id_list if i]
	category = params.get('category_name') or params.get('name') or ('Movies Library' if media_kind == 'movies' else 'TV Shows Library')
	params.update({'list': id_list, 'action': 'mdblist_user_list', 'category_name': category})
	if media_type in ('movie', 'movies'):
		return Movies(params).fetch_list()
	return TVShows(params).fetch_list()

def build_mdbl_list(params):
	_set_mdbl_list_exit_params(params)
	list_id = params.get('list_id')
	list_type = params.get('list_type', 'my_lists')
	items = get_mdbl_list_contents(list_type, list_id)
	media_type = _mdbl_route_media_type(params, items)
	id_list = []
	for i in items:
		tmdb_id = mdbl_unified_item_tmdb_id(i)
		if tmdb_id:
			id_list.append(tmdb_id)
	params.update({'list': id_list, 'action': 'mdblist_user_list', 'category_name': params.get('list_name', 'MDBList')})
	if media_type == 'tvshow':
		return TVShows(params).fetch_list()
	return Movies(params).fetch_list()
