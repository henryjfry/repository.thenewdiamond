# -*- coding: utf-8 -*-
import sys
from apis.simkl_api import simkl_search_my_lists
from modules import settings
from modules.kodi_utils import add_items, set_content, set_category, end_directory, build_url, make_listitem, get_icon, get_addon_fanart, set_view_mode, MENU_FOLDER_CONTENT
# from modules.kodi_utils import logger

def search_simkl_lists(params):
	def _builder():
		for item in results:
			try:
				media_ids = item.get('media_ids') or {}
				tmdb_id = media_ids.get('tmdb')
				if not tmdb_id: continue
				title = item.get('title') or 'Unknown'
				status_label = item.get('status_label', '')
				media_kind = item.get('media_kind', 'movies')
				display = '%s | [I]%s[/I]' % (title, status_label)
				if media_kind == 'movies':
					url = build_url({'mode': 'extras_menu_choice', 'media_type': 'movie', 'tmdb_id': tmdb_id})
				else:
					url = build_url({'mode': 'build_season_list', 'tmdb_id': tmdb_id})
				listitem = make_listitem()
				listitem.setLabel(display)
				listitem.setArt({'icon': simkl_icon, 'poster': simkl_icon, 'thumb': simkl_icon, 'fanart': fanart, 'banner': fanart})
				info_tag = listitem.getVideoInfoTag(True)
				info_tag.setPlot('Simkl %s' % status_label)
				yield (url, listitem, True)
			except: pass
	handle = int(sys.argv[1])
	simkl_icon, fanart = get_icon('simkl'), get_addon_fanart()
	search_title = params.get('key_id') or params.get('query') or ''
	try:
		if not settings.simkl_user_active(): results = []
		else: results = simkl_search_my_lists(search_title)
		add_items(handle, list(_builder()))
	except: pass
	set_content(handle, MENU_FOLDER_CONTENT)
	set_category(handle, search_title.capitalize())
	end_directory(handle)
	set_view_mode('view.main', MENU_FOLDER_CONTENT)
