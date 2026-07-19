# -*- coding: utf-8 -*-
import sys
from caches.navigator_cache import navigator_cache as nc
from caches.settings_cache import get_setting, set_setting
from modules import kodi_utils as k, settings as s
# logger = k.logger

class Navigator:
	def __init__(self, params):
		self.params = params
		self.params_get = self.params.get
		self.category_name = self.params_get('name', 'Red Light')
		self.list_name = self.params_get('action', 'RootList')
		self.is_external = k.external()
		self.make_listitem = lambda: k.make_listitem(False)
		self.build_url = k.build_url
		self.add_item = k.add_item
		self.get_icon = k.get_icon
		self.fanart = k.get_addon_fanart()
		self.run_plugin = 'RunPlugin(%s)'

	def main(self):
		def _process():
			for count, item in enumerate(browse_list):
				try:
					folder_params = dict(item)
					url = k.build_folder_url(folder_params)
					cm_items = []
					if can_move:
						cm_items.append(('[B]Move[/B]', self.run_plugin % self.build_url({'mode': 'menu_editor.move', 'active_list': self.list_name, 'position': count})))
					cm_items.extend([
					('[B]Remove[/B]', self.run_plugin % self.build_url({'mode': 'menu_editor.remove', 'active_list': self.list_name, 'position': count})),
					('[B]Add Content[/B]', self.run_plugin % self.build_url({'mode': 'menu_editor.add', 'active_list': self.list_name, 'position': count})),
					('[B]Restore Menu[/B]', self.run_plugin % self.build_url({'mode': 'menu_editor.restore', 'active_list': self.list_name, 'position': count})),
					('[B]Check for New Menu Items[/B]', self.run_plugin % self.build_url({'mode': 'menu_editor.update', 'active_list': self.list_name, 'position': count})),
					('[B]Reload Menu[/B]', self.run_plugin % self.build_url({'mode': 'menu_editor.reload', 'active_list': self.list_name, 'position': count})),
					('[B]Browse Removed items[/B]', self.run_plugin % self.build_url({'mode': 'menu_editor.browse', 'active_list': self.list_name, 'position': count})),
					('[B]Add to Shortcut Folder[/B]', self.run_plugin % self.build_url({'mode': 'menu_editor.shortcut_folder_add_known', 'url': url}))])
					icon = k.resolve_list_icon(item.get('iconImage', ''))
					item['iconImage'] = icon
					listitem = self.make_listitem()
					listitem.setLabel(item.get('name', ''))
					k.set_list_item_art(listitem, icon, fanart=self.fanart)
					info_tag = listitem.getVideoInfoTag(True)
					info_tag.setPlot(' ')
					if not self.is_external: listitem.addContextMenuItems(cm_items)
					yield ((url, listitem, True), count)
				except: pass
		if self.params_get('full_list', 'false') == 'true': browse_list = nc.get_main_lists(self.list_name)[0]
		else: browse_list = nc.currently_used_list(self.list_name)
		if not browse_list:
			browse_list = list(nc.main_menus.get(self.list_name, []))
		can_move = len(browse_list) > 1
		results = sorted(list(_process()), key=lambda k: k[1])
		if not results and browse_list:
			k.logger('Red Light', 'menu build empty for %s (%s items expected)' % (self.list_name, len(browse_list)))
		handle = int(sys.argv[1])
		if results:
			k.add_items(handle, [i[0] for i in results])
		if not self.is_external:
			if self.list_name == 'RootList':
				folder_path = k.folder_path()
				if folder_path: k.set_property('redlight.exit_params', k.sanitize_folder_url(folder_path))
			else:
				k.set_property('redlight.exit_params', k.build_folder_url({'mode': 'navigator.main', 'action': 'RootList'}))
		self.end_directory(cache_to_disc=bool(results), skip_view_mode=(self.list_name == 'RootList'))

	def discover(self):
		self.add({'mode': 'navigator.discover_contents', 'media_type': 'movie'}, 'Movies', 'movies')
		self.add({'mode': 'navigator.discover_contents', 'media_type': 'tvshow'}, 'TV Shows', 'tv')
		self._set_submenu_exit_params()
		self.end_directory()

	def premium(self):
		if s.authorized_debrid_check('ad'): self.add({'mode': 'navigator.alldebrid'}, 'All Debrid', 'alldebrid')
		if s.easynews_authorized(): self.add({'mode': 'navigator.easynews'}, 'EasyNews', 'easynews')
		if s.authorized_debrid_check('oc'): self.add({'mode': 'navigator.offcloud'}, 'Offcloud', 'offcloud')
		if s.authorized_debrid_check('pm'): self.add({'mode': 'navigator.premiumize'}, 'Premiumize', 'premiumize')
		if s.authorized_debrid_check('rd'): self.add({'mode': 'navigator.real_debrid'}, 'Real Debrid', 'realdebrid')
		if s.authorized_debrid_check('tb'): self.add({'mode': 'navigator.torbox'}, 'TorBox', 'torbox')
		self.end_directory()

	def easynews(self):
		self.add({'mode': 'navigator.search_history', 'action': 'easynews_video'}, 'Search Videos', 'search')
		self.add({'mode': 'navigator.search_history', 'action': 'easynews_image'}, 'Search Images', 'search')
		self.add({'mode': 'easynews.account_info', 'isFolder': 'false'}, 'Account Info', 'easynews')
		self.end_directory()

	def real_debrid(self):
		self.add({'mode': 'real_debrid.rd_cloud'}, 'Cloud Storage', 'realdebrid')
		self.add({'mode': 'real_debrid.rd_downloads'}, 'History', 'realdebrid')
		self.add({'mode': 'real_debrid.rd_account_info', 'isFolder': 'false'}, 'Account Info', 'realdebrid')
		self.end_directory()

	def premiumize(self):
		self.add({'mode': 'premiumize.pm_cloud'}, 'Cloud Storage', 'premiumize')
		self.add({'mode': 'premiumize.pm_transfers'}, 'History', 'premiumize')
		self.add({'mode': 'premiumize.pm_account_info', 'isFolder': 'false'}, 'Account Info', 'premiumize')
		self.end_directory()

	def alldebrid(self):
		self.add({'mode': 'alldebrid.ad_cloud'}, 'Cloud Storage', 'alldebrid')
		self.add({'mode': 'alldebrid.ad_downloads'}, 'History', 'alldebrid')
		self.add({'mode': 'alldebrid.ad_saved_links'}, 'Saved Links', 'alldebrid')
		self.add({'mode': 'alldebrid.ad_account_info', 'isFolder': 'false'}, 'Account Info', 'alldebrid')
		self.end_directory()

	def offcloud(self):
		self.add({'mode': 'offcloud.oc_cloud'}, 'Cloud Storage', 'offcloud')
		self.add({'mode': 'offcloud.oc_history'}, 'History', 'offcloud')
		self.add({'mode': 'offcloud.oc_account_info', 'isFolder': 'false'}, 'Account Info', 'offcloud')
		self.end_directory()

	def torbox(self):
		self.add({'mode': 'torbox.tb_cloud'}, 'Cloud Storage', 'torbox')
		self.add({'mode': 'torbox.tb_history'}, 'History', 'torbox')
		self.add({'mode': 'torbox.send_webdl', 'isFolder': 'false'}, 'Send URL to WebDL', 'torbox')
		self.add({'mode': 'torbox.tb_account_info', 'isFolder': 'false'}, 'Account Info', 'torbox')
		self.end_directory()

	def favorites(self):
		self.add({'mode': 'build_movie_list', 'action': 'favorites_movies', 'name': 'Movies'}, 'Movies', 'movies')
		self.add({'mode': 'build_tvshow_list', 'action': 'favorites_tvshows', 'name': 'TV Shows'}, 'TV Shows', 'tv'),
		self.add({'mode': 'build_tvshow_list', 'action': 'favorites_anime', 'is_anime_list': 'true', 'name': 'Anime'}, 'Anime', 'anime'),
		self.add({'mode': 'favorite_people', 'isFolder': 'false', 'name': 'People'}, 'People', 'empty_person')
		self._set_submenu_exit_params()
		self.end_directory()

	def my_content(self):
		return self.my_lists()

	def my_lists(self):
		if s.mdblist_user_active():
			self._safe_add({'mode': 'navigator.mdblist_lists'}, 'MDBList Lists', 'mdblist')
		if s.simkl_user_active():
			self._safe_add(self._simkl_lists_menu(), 'Simkl Lists', 'simkl')
		if s.trakt_user_active(): self._safe_add({'mode': 'navigator.trakt_lists_personal'}, 'Trakt Lists', 'trakt')
		self._safe_add({'mode': 'navigator.trakt_lists_public'}, 'Trakt Public Lists', 'trakt')
		if s.tmdblist_user_active(): self._safe_add({'mode': 'navigator.tmdb_lists_personal'}, 'TMDb Lists', 'tmdb')
		self._safe_add({'mode': 'personal_lists.get_personal_lists'}, 'Personal Lists', 'lists')
		self._safe_add({'mode': 'navigator.discover_contents', 'media_type': 'movie', 'show_new': 'false'}, 'Discover Lists (Movies)', 'movies')
		self._safe_add({'mode': 'navigator.discover_contents', 'media_type': 'tvshow', 'show_new': 'false'}, 'Discover Lists (TV Shows)', 'tv')
		self._set_submenu_exit_params()
		self.end_directory()

	def tmdb_lists_personal(self):
		self.add({'mode': 'navigator.tmdb_watchlists'}, 'Watchlist', 'tmdb')
		self.add({'mode': 'navigator.tmdb_favorites'}, 'Favorites', 'tmdb')
		self.add({'mode': 'navigator.tmdb_recommendations'}, 'Recommendations', 'tmdb')
		self.add({'mode': 'tmdblist.get_tmdb_lists'}, 'My Lists', 'tmdb')
		self._set_exit_params({'mode': 'navigator.my_lists'})
		self.end_directory()

	def tmdb_watchlists(self):
		self.category_name = 'Watchlist'
		self.add({'mode': 'tmdblist.build_tmdb_list', 'list_id': 'watchlist', 'media_type': 'movie', 'list_name': 'Movie Watchlist'}, 'Movies Watchlist', 'tmdb')
		self.add({'mode': 'tmdblist.build_tmdb_list', 'list_id': 'watchlist', 'media_type': 'tv', 'list_name': 'TV Show Watchlist'}, 'TV Shows Watchlist', 'tmdb')
		self._set_exit_params({'mode': 'navigator.tmdb_lists_personal'})
		self.end_directory()

	def tmdb_favorites(self):
		self.category_name = 'Favorites'
		self.add({'mode': 'tmdblist.build_tmdb_list', 'list_id': 'favorites', 'media_type': 'movie', 'list_name': 'Movie Favorites'}, 'Movie Favorites', 'tmdb')
		self.add({'mode': 'tmdblist.build_tmdb_list', 'list_id': 'favorites', 'media_type': 'tv', 'list_name': 'TV Show Favorites'}, 'TV Show Favorites', 'tmdb')
		self._set_exit_params({'mode': 'navigator.tmdb_lists_personal'})
		self.end_directory()

	def tmdb_recommendations(self):
		self.category_name = 'Recommendations'
		self.add({'mode': 'tmdblist.build_tmdb_list', 'list_id': 'recommendations', 'media_type': 'movie', 'list_name': 'Movie Recommendations'}, 'Movie Recommendations', 'tmdb')
		self.add({'mode': 'tmdblist.build_tmdb_list', 'list_id': 'recommendations', 'media_type': 'tv', 'list_name': 'TV Show Recommendations'}, 'TV Show Recommendations', 'tmdb')
		self._set_exit_params({'mode': 'navigator.tmdb_lists_personal'})
		self.end_directory()

	def trakt_lists_personal(self):
		self.add({'mode': 'navigator.trakt_collections'}, 'Collection', 'trakt')
		self.add({'mode': 'navigator.trakt_watchlists'}, 'Watchlist', 'trakt')
		self.add({'mode': 'trakt.list.get_trakt_lists', 'list_type': 'my_lists', 'category_name': 'My Lists'}, 'My Lists', 'trakt')
		self.add({'mode': 'trakt.list.get_trakt_lists', 'list_type': 'liked_lists', 'category_name': 'Liked Lists'}, 'Liked Lists', 'trakt')
		self.add({'mode': 'navigator.trakt_favorites', 'category_name': 'Favorites'}, 'Favorites', 'trakt')
		self.add({'mode': 'navigator.trakt_recommendations', 'category_name': 'Recommended'}, 'Recommended', 'trakt')
		self.add({'mode': 'build_my_calendar'}, 'Calendar', 'trakt')
		if s.trakt_user_active(): self.add({'mode': 'navigator.search_history', 'action': 'trakt_my_lists'}, 'Search My Trakt Lists', 'search')
		self._set_exit_params({'mode': 'navigator.my_lists'})
		self.end_directory()

	def trakt_lists_public(self):
		self.add({'mode': 'trakt.list.get_trakt_user_lists', 'list_type': 'trending', 'category_name': 'Trending User Lists'}, 'Trending User Lists', 'trakt')
		self.add({'mode': 'trakt.list.get_trakt_user_lists', 'list_type': 'popular', 'category_name': 'Popular User Lists'}, 'Popular User Lists', 'trakt')
		self.add({'mode': 'navigator.search_history', 'action': 'trakt_lists'}, 'Search User Lists', 'search')
		self._set_exit_params({'mode': 'navigator.my_lists'})
		self.end_directory()

	def random_lists(self):
		self.add({'mode': 'navigator.build_random_lists', 'menu_type': 'movie'}, 'Random Movie Lists', 'movies')
		self.add({'mode': 'navigator.build_random_lists', 'menu_type': 'tvshow'}, 'Random TV Show Lists', 'tv')
		self.add({'mode': 'navigator.build_random_lists', 'menu_type': 'anime'}, 'Random Anime Lists', 'anime')
		self.add({'mode': 'navigator.build_random_lists', 'menu_type': 'because_you_watched'}, 'Random Because You Watched', 'because_you_watched')
		if s.tmdblist_user_active(): self.add({'mode': 'navigator.build_random_lists', 'menu_type': 'tmdb_lists'}, 'Random TMDb Lists', 'tmdb')
		self.add({'mode': 'navigator.build_random_lists', 'menu_type': 'personal_lists'}, 'Random Personal Lists', 'lists')
		if s.simkl_user_active(): self.add({'mode': 'navigator.build_random_lists', 'menu_type': 'simkl_lists'}, 'Random Simkl Lists', 'simkl')
		if s.trakt_user_active():
			self.add({'mode': 'navigator.build_random_lists', 'menu_type': 'trakt_personal'}, 'Random Trakt Lists (Personal)', 'trakt')
			self.add({'mode': 'navigator.build_random_lists', 'menu_type': 'trakt_public'}, 'Random Trakt Lists (Public)', 'trakt')
		self._set_submenu_exit_params()
		self.end_directory()

	def _simkl_lists_menu(self):
		return {'mode': 'navigator.simkl_lists'}

	def _simkl_list_link(self, list_mode, action, category_name):
		return {'mode': list_mode, 'action': action, 'category_name': category_name}

	def simkl_lists(self):
		"""Flat status lists (v1.3.4 layout) — direct links to each Movies/TV list."""
		self.category_name = 'Simkl Lists'
		for url_params, label in (
			(self._simkl_list_link('build_movie_list', 'simkl_plantowatch', 'Movies Plan to Watch'), 'Movies Plan to Watch'),
			(self._simkl_list_link('build_tvshow_list', 'simkl_plantowatch', 'TV Shows Plan to Watch'), 'TV Shows Plan to Watch'),
			(self._simkl_list_link('build_movie_list', 'simkl_watching', 'Movies Watching'), 'Movies Watching'),
			(self._simkl_list_link('build_tvshow_list', 'simkl_watching', 'TV Shows Watching'), 'TV Shows Watching'),
			(self._simkl_list_link('build_movie_list', 'simkl_completed', 'Movies Completed'), 'Movies Completed'),
			(self._simkl_list_link('build_tvshow_list', 'simkl_completed', 'TV Shows Completed'), 'TV Shows Completed'),
			(self._simkl_list_link('build_movie_list', 'simkl_hold', 'Movies On Hold'), 'Movies On Hold'),
			(self._simkl_list_link('build_tvshow_list', 'simkl_hold', 'TV Shows On Hold'), 'TV Shows On Hold'),
			(self._simkl_list_link('build_movie_list', 'simkl_dropped', 'Movies Dropped'), 'Movies Dropped'),
			(self._simkl_list_link('build_tvshow_list', 'simkl_dropped', 'TV Shows Dropped'), 'TV Shows Dropped'),
		):
			self._safe_add(url_params, label, 'simkl')
		self._safe_add({'mode': 'navigator.search_history', 'action': 'simkl_lists'}, 'Search My Simkl Lists', 'search')
		self.end_directory()

	def simkl_watchlists(self):
		self.category_name = 'Plan to Watch'
		self._safe_add(self._simkl_list_link('build_movie_list', 'simkl_plantowatch', 'Movies Plan to Watch'), 'Movies', 'simkl')
		self._safe_add(self._simkl_list_link('build_tvshow_list', 'simkl_plantowatch', 'TV Shows Plan to Watch'), 'TV Shows', 'simkl')
		self.end_directory()

	def simkl_completed(self):
		self.category_name = 'Completed'
		self._safe_add(self._simkl_list_link('build_movie_list', 'simkl_completed', 'Movies Completed'), 'Movies', 'simkl')
		self._safe_add(self._simkl_list_link('build_tvshow_list', 'simkl_completed', 'TV Shows Completed'), 'TV Shows', 'simkl')
		self.end_directory()

	def simkl_watching(self):
		self.category_name = 'Watching'
		self._safe_add(self._simkl_list_link('build_movie_list', 'simkl_watching', 'Movies Watching'), 'Movies', 'simkl')
		self._safe_add(self._simkl_list_link('build_tvshow_list', 'simkl_watching', 'TV Shows Watching'), 'TV Shows', 'simkl')
		self.end_directory()

	def simkl_hold(self):
		self.category_name = 'On Hold'
		self._safe_add(self._simkl_list_link('build_movie_list', 'simkl_hold', 'Movies On Hold'), 'Movies', 'simkl')
		self._safe_add(self._simkl_list_link('build_tvshow_list', 'simkl_hold', 'TV Shows On Hold'), 'TV Shows', 'simkl')
		self.end_directory()

	def simkl_dropped(self):
		self.category_name = 'Dropped'
		self._safe_add(self._simkl_list_link('build_movie_list', 'simkl_dropped', 'Movies Dropped'), 'Movies', 'simkl')
		self._safe_add(self._simkl_list_link('build_tvshow_list', 'simkl_dropped', 'TV Shows Dropped'), 'TV Shows', 'simkl')
		self.end_directory()

	def mdblist_lists(self):
		self.category_name = 'MDBList Lists'
		self._safe_add({'mode': 'build_movie_list', 'action': 'mdblist_watchlist', 'category_name': 'Movies Watchlist'}, 'Movies Watchlist', 'mdblist')
		self._safe_add({'mode': 'build_tvshow_list', 'action': 'mdblist_watchlist', 'category_name': 'TV Shows Watchlist'}, 'TV Shows Watchlist', 'mdblist')
		self._safe_add({'mode': 'build_movie_list', 'action': 'mdblist_collection', 'category_name': 'Movies Library'}, 'Movies Library', 'mdblist')
		self._safe_add({'mode': 'build_tvshow_list', 'action': 'mdblist_collection', 'category_name': 'TV Shows Library'}, 'TV Shows Library', 'mdblist')
		self._safe_add({'mode': 'build_tvshow_list', 'action': 'mdblist_droplist', 'category_name': 'Dropped TV Shows'}, 'Dropped TV Shows', 'mdblist')
		self._safe_add({'mode': 'mdblist.get_mdbl_lists', 'name': 'My Lists'}, 'My Lists', 'mdblist')
		self._safe_add({'mode': 'mdblist.get_mdbl_liked_lists', 'name': 'Movies Liked Lists', 'media_type': 'movie'}, 'Movies Liked Lists', 'mdblist')
		self._safe_add({'mode': 'mdblist.get_mdbl_liked_lists', 'name': 'TV Shows Liked Lists', 'media_type': 'tvshow'}, 'TV Shows Liked Lists', 'mdblist')
		self._safe_add({'mode': 'mdblist.get_mdbl_top_lists', 'name': 'Popular MDBLists'}, 'Popular MDBLists', 'mdblist')
		self._set_exit_params({'mode': 'navigator.my_lists'})
		self.end_directory()

	def trakt_collections(self):
		self.category_name = 'Collection'
		self.add({'mode': 'build_movie_list', 'action': 'trakt_collection', 'category_name': 'Movies Collection'}, 'Movies Collection', 'trakt')
		self.add({'mode': 'build_tvshow_list', 'action': 'trakt_collection', 'category_name': 'TV Shows Collection'}, 'TV Shows Collection', 'trakt')
		self.add({'mode': 'build_movie_list', 'action': 'trakt_collection_lists', 'new_page': 'recent', 'category_name': 'Recently Added Movies'}, 'Recently Added Movies', 'trakt')
		self.add({'mode': 'build_tvshow_list', 'action': 'trakt_collection_lists', 'new_page': 'recent', 'category_name': 'Recently Added TV Shows'},
					'Recently Added TV Shows', 'trakt')
		self.add({'mode': 'build_my_calendar', 'recently_aired': 'true'}, 'Recently Aired Episodes', 'trakt')
		self._set_exit_params({'mode': 'navigator.trakt_lists_personal'})
		self.end_directory()

	def trakt_watchlists(self):
		self.category_name = 'Watchlist'
		self.add({'mode': 'build_movie_list', 'action': 'trakt_watchlist', 'category_name': 'Movies Watchlist'}, 'Movies Watchlist', 'trakt')
		self.add({'mode': 'build_tvshow_list', 'action': 'trakt_watchlist', 'category_name': 'TV Shows Watchlist'}, 'TV Shows Watchlist', 'trakt')
		self.add({'mode': 'build_movie_list', 'action': 'trakt_watchlist_lists', 'new_page': 'recent', 'category_name': 'Recently Added Movies'}, 'Recently Added Movies', 'trakt')
		self.add({'mode': 'build_tvshow_list', 'action': 'trakt_watchlist_lists', 'new_page': 'recent', 'category_name': 'Recently Added TV Shows'},
					'Recently Added TV Shows', 'trakt')
		self._set_exit_params({'mode': 'navigator.trakt_lists_personal'})
		self.end_directory()

	def trakt_recommendations(self):
		self.category_name = 'Recommended'
		self.add({'mode': 'build_movie_list', 'action': 'trakt_recommendations', 'category_name': 'Recommended Movies'}, 'Movies Recommended', 'trakt')
		self.add({'mode': 'build_tvshow_list', 'action': 'trakt_recommendations', 'category_name': 'Recommended TV Shows'}, 'TV Shows Recommended', 'trakt')
		self._set_exit_params({'mode': 'navigator.trakt_lists_personal'})
		self.end_directory()

	def trakt_favorites(self):
		self.category_name = 'Favorites'
		self.add({'mode': 'build_movie_list', 'action': 'trakt_favorites', 'category_name': 'Favorite Movies'}, 'Movies', 'trakt')
		self.add({'mode': 'build_tvshow_list', 'action': 'trakt_favorites', 'category_name': 'Favorite TV Shows'}, 'TV Shows', 'trakt')
		self._set_exit_params({'mode': 'navigator.trakt_lists_personal'})
		self.end_directory()

	def people(self):
		self.add({'mode': 'build_tmdb_people', 'action': 'popular', 'isFolder': 'false', 'name': 'Popular'}, 'Popular', 'popular')
		self.add({'mode': 'build_tmdb_people', 'action': 'day', 'isFolder': 'false', 'name': 'Trending'}, 'Trending', 'trending')
		self.add({'mode': 'build_tmdb_people', 'action': 'week', 'isFolder': 'false', 'name': 'Trending This Week'}, 'Trending This Week', 'trending_recent')
		self.end_directory()

	def search(self):
		self.add({'mode': 'navigator.search_history', 'action': 'movie', 'name': 'Search History Movies'}, 'Search Movies', 'movies')
		self.add({'mode': 'navigator.search_history', 'action': 'tvshow', 'name': 'Search History TV Shows'}, 'Search TV Shows', 'tv')
		self.add({'mode': 'navigator.search_history', 'action': 'anime', 'name': 'Search History Anime'}, 'Search Anime', 'anime')
		self.add({'mode': 'navigator.search_history', 'action': 'tvshow_anime', 'name': 'Search History TV Show & Anime'}, 'Search TV Show & Anime', 'tv_anime')
		self.add({'mode': 'navigator.search_history', 'action': 'people', 'name': 'Search History People'}, 'Search People', 'people')
		self.add({'mode': 'navigator.search_history', 'action': 'tmdb_keyword_movie', 'name': 'Search History Keywords (Movies)'}, 'Search Keywords (Movies)', 'tmdb')
		self.add({'mode': 'navigator.search_history', 'action': 'tmdb_keyword_tvshow', 'name': 'Search History Keywords (TV Shows)'}, 'Search Keywords (TV Shows)', 'tmdb')
		self.add({'mode': 'navigator.search_history', 'action': 'trakt_lists'}, 'Search Trakt User Lists', 'trakt')
		if s.easynews_authorized():
			self.add({'mode': 'navigator.search_history', 'action': 'easynews_video'}, 'Search EasyNews Videos', 'easynews')
			self.add({'mode': 'navigator.search_history', 'action': 'easynews_image'}, 'Search EasyNews Images', 'easynews')
		self.end_directory()

	def downloads(self):
		self.add({'mode': 'downloader.manager', 'name': 'Download Manager', 'isFolder': 'false'}, 'Download Manager', 'downloads')
		self.add({'mode': 'downloader.viewer', 'folder_type': 'movie', 'name': 'Movies'}, 'Movies', 'movies')
		self.add({'mode': 'downloader.viewer', 'folder_type': 'episode', 'name': 'TV Shows'}, 'TV Shows', 'tv')
		self.add({'mode': 'downloader.viewer', 'folder_type': 'premium', 'name': 'Premium Files'}, 'Premium Files', 'premium')
		self.add({'mode': 'browser_image', 'folder_path': s.download_directory('image'), 'isFolder': 'false'}, 'Images', 'people')
		self.end_directory()

	def tools(self):
		self.add({'mode': 'open_settings', 'isFolder': 'false'}, 'Settings', 'settings')
		if s.configured_external_scraper_slots():
			self.add({'mode': 'open_external_scraper_settings', 'isFolder': 'false'}, s.external_scraper_settings_tools_label(), 'settings')
		self.add({'mode': 'navigator.tips'}, 'Tips for Use', 'settings2')
		if get_setting('redlight.use_viewtypes', 'true') == 'true' and not get_setting('redlight.manual_viewtypes', 'false') == 'true':
			self.add({'mode': 'navigator.set_view_modes'}, 'Set Views', 'settings2')
		self.add({'mode': 'navigator.changelog_utils'}, 'Changelog & Log Utils', 'settings2')
		self.add({'mode': 'build_next_episode_manager'}, 'TV Shows Progress Manager', 'settings2')
		self.add({'mode': 'navigator.shortcut_folders'}, 'Shortcut Folders Manager', 'settings2')
		self.add({'mode': 'navigator.import_export'}, 'Import & Export', 'settings2')
		self.add({'mode': 'navigator.maintenance'}, 'Database & Cache Maintenance', 'settings2')
		self.add({'mode': 'language_invoker_choice', 'isFolder': 'false'}, 'Toggle Language Invoker (ADVANCED!!)', 'settings2')
		self.end_directory()

	def import_export(self):
		self.add({'mode': 'settings_backup.import_settings', 'isFolder': 'false'}, 'Import Red Light Settings', 'settings')
		self.add({'mode': 'settings_backup.export_settings', 'isFolder': 'false'}, 'Export Red Light Settings', 'settings')
		self.add({'mode': 'local_backup.import_data', 'isFolder': 'false'}, 'Import Red Light Favorites & History', 'folder')
		self.add({'mode': 'local_backup.export_data', 'isFolder': 'false'}, 'Export Red Light Favorites & History', 'folder')
		self.add({'mode': 'kodi_favorites.import_favorites', 'isFolder': 'false'}, 'Import Kodi Favorites', 'favorites')
		self.add({'mode': 'kodi_favorites.export_favorites', 'isFolder': 'false'}, 'Export Kodi Favorites', 'favorites')
		self.end_directory()

	def maintenance(self):
		self.add({'mode': 'check_databases_integrity_cache', 'isFolder': 'false'}, 'Check for Corrupt Databases', 'settings')
		self.add({'mode': 'clean_databases_cache', 'isFolder': 'false'}, 'Clean Databases', 'settings')
		self.add({'mode': 'sync_settings', 'silent': 'false', 'isFolder': 'false'}, 'Remake Settings Cache', 'settings')
		self.add({'mode': 'clear_all_cache', 'isFolder': 'false'}, 'Clear All Cache (Excluding Favorites)', 'settings')
		self.add({'mode': 'clear_favorites_choice', 'isFolder': 'false'}, 'Clear Favorites Cache', 'settings')
		self.add({'mode': 'search.clear_search', 'isFolder': 'false'}, 'Clear Search History Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'ai_functions', 'isFolder': 'false'}, 'Clear AI Data Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'list', 'isFolder': 'false'}, 'Clear Lists Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'main', 'isFolder': 'false'}, 'Clear Main Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'meta', 'isFolder': 'false'}, 'Clear Meta Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'tmdb_list', 'isFolder': 'false'}, 'Clear TMDb Personal List Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'imdb', 'isFolder': 'false'}, 'Clear IMDb Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'mdblist', 'isFolder': 'false'}, 'Clear MDBList Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'simkl', 'isFolder': 'false'}, 'Clear Simkl Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'trakt', 'isFolder': 'false'}, 'Clear Trakt Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'subtitles', 'isFolder': 'false'}, 'Clear Subtitles Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'easynews_scrape', 'isFolder': 'false'}, 'Clear EasyNews Scrape Cache', 'settings')
		self.add({'mode': 'search.clear_easynews_search_history', 'isFolder': 'false'}, 'Clear EasyNews Search History', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'external_scrapers', 'isFolder': 'false'}, 'Clear External Scrapers Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'internal_scrapers', 'isFolder': 'false'}, 'Clear Internal Scrapers Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'ad_cloud', 'isFolder': 'false'}, 'Clear All Debrid Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'oc_cloud', 'isFolder': 'false'}, 'Clear Offcloud Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'pm_cloud', 'isFolder': 'false'}, 'Clear Premiumize Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'rd_cloud', 'isFolder': 'false'}, 'Clear Real Debrid Cache', 'settings')
		self.add({'mode': 'clear_cache', 'cache': 'tb_cloud', 'isFolder': 'false'}, 'Clear TorBox Cache', 'settings')
		self.end_directory()

	def set_view_modes(self):
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.main', 'content': k.MENU_FOLDER_CONTENT, 'name': 'menus'}, 'Set Menus', 'folder')
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.movies', 'content': 'movies'}, 'Set Movies', 'movies')
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.tvshows', 'content': 'tvshows'}, 'Set TV Shows', 'tv')
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.seasons', 'content': 'seasons'}, 'Set Seasons', 'ontheair')
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.episodes', 'content': 'episodes'}, 'Set Episodes (show seasons)', 'next_episodes')
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.episodes_single', 'content': 'episodes', 'name': 'episode lists'}, 'Set Episode Lists (Next Episodes, etc.)', 'calender')
		self.add({'mode': 'navigator.choose_view', 'view_type': 'view.premium', 'content': k.MENU_FOLDER_CONTENT, 'name': 'premium files'}, 'Set Premium Files', 'premium')
		self.end_directory()

	def changelog_utils(self):
		log_loc, old_log_loc = k.translate_path('special://logpath/kodi.log'), k.translate_path('special://logpath/kodi.old.log')
		redlight_clogpath = k.translate_path('special://home/addons/plugin.video.redlight/resources/text/changelog.txt')
		self.add({'mode': 'show_text', 'heading': 'Changelog', 'file': redlight_clogpath, 'font_size': 'large', 'isFolder': 'false'}, 'Changelog', 'lists')
		self.add({'mode': 'show_text', 'heading': 'Kodi Log Viewer', 'file': log_loc, 'kodi_log': 'true', 'isFolder': 'false'}, 'Kodi Log Viewer', 'lists')
		self.add({'mode': 'show_text', 'heading': 'Kodi Log Viewer (Old)', 'file': old_log_loc, 'kodi_log': 'true', 'isFolder': 'false'}, 'Kodi Log Viewer (Old)', 'lists')
		self.add({'mode': 'upload_logfile', 'isFolder': 'false'}, 'Upload Kodi Log to Pastebin', 'lists')
		self.end_directory()

	def certifications(self):
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie': from modules.meta_lists import movie_certifications as function
		else: from modules.meta_lists import tvshow_certifications as function
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie': mode, action = 'build_movie_list', 'tmdb_movies_certifications'
		else:
			mode = 'build_tvshow_list'
			if menu_type == 'tvshow': action = 'trakt_tv_certifications'
			else: action = 'trakt_anime_certifications'
		for i in function(): self.add({'mode': mode, 'action': action, 'key_id': i['id'], 'name': i['name']}, i['name'], 'certifications')
		self._set_submenu_exit_params(menu_type)
		self.end_directory()

	def languages(self):
		from modules.meta_lists import languages as function
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie': mode, action = 'build_movie_list', 'tmdb_movies_languages'
		else: mode, action = 'build_tvshow_list', 'tmdb_tv_languages'
		for i in function(): self.add({'mode': mode, 'action': action, 'key_id': i['id'], 'name': i['name']}, i['name'], 'languages')
		self._set_submenu_exit_params(menu_type)
		self.end_directory()

	def years(self):
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie':
			from modules.meta_lists import years_movies as function
			mode, action = 'build_movie_list', 'tmdb_movies_year'
		else:
			mode = 'build_tvshow_list'
			if menu_type == 'tvshow':
				from modules.meta_lists import years_tvshows as function
				action = 'tmdb_tv_year'
			else:
				from modules.meta_lists import years_anime as function
				action = 'tmdb_anime_year'
		for i in function(): self.add({'mode': mode, 'action': action, 'key_id': i['id'], 'name': i['name']}, i['name'], 'calender')
		self._set_submenu_exit_params(menu_type)
		self.end_directory()

	def decades(self):
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie':
			from modules.meta_lists import decades_movies as function
			mode, action = 'build_movie_list', 'tmdb_movies_decade'
		else:
			mode = 'build_tvshow_list'
			if menu_type == 'tvshow':
				from modules.meta_lists import decades_tvshows as function
				action = 'tmdb_tv_decade'
			else:
				from modules.meta_lists import decades_anime as function
				action = 'tmdb_anime_decade'
		for i in function(): self.add({'mode': mode, 'action': action, 'key_id': i['id'], 'name': i['name']}, i['name'], 'calendar_decades')
		self._set_submenu_exit_params(menu_type)
		self.end_directory()

	def networks(self):
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie': return
		from modules.meta_lists import networks
		for i in sorted(networks(), key=lambda k: k['name']): self.add({'mode': 'build_tvshow_list', 'action': 'tmdb_tv_networks', 'key_id': i['id'], 'name': i['name']}, i['name'],
																		self.get_icon(i['logo'], 'network_icons'), original_image=True)
		self._set_submenu_exit_params(menu_type)
		self.end_directory()

	def providers(self):
		menu_type = self.params_get('menu_type')
		tmdb_img = 'https://image.tmdb.org/t/p/original/%s'
		if menu_type == 'movie':
			from modules.meta_lists import watch_providers_movies as function
			mode, action = 'build_movie_list', 'tmdb_movies_providers'
		else:
			from modules.meta_lists import watch_providers_tvshows as function
			mode = 'build_tvshow_list'
			if menu_type == 'tvshow': action = 'tmdb_tv_providers'
			else: action = 'tmdb_anime_providers'
		for i in function(): self.add({'mode': mode, 'action': action, 'key_id': i['id'], 'name': i['name']}, i['name'], tmdb_img % i['logo'], original_image=True)
		self._set_submenu_exit_params(menu_type)
		self.end_directory()

	def genres(self):
		menu_type = self.params_get('menu_type')
		if menu_type == 'movie':
			from modules.meta_lists import movie_genres as function
			mode, action = 'build_movie_list', 'tmdb_movies_genres'
		else:
			mode = 'build_tvshow_list'
			if menu_type == 'tvshow':
				from modules.meta_lists import tvshow_genres as function
				action = 'tmdb_tv_genres'
			else:
				from modules.meta_lists import anime_genres as function
				action = 'tmdb_anime_genres'
		for i in function(): self.add({'mode': mode, 'action': action, 'key_id': i['id'], 'name': i['name']}, i['name'], i['icon'])
		self._set_submenu_exit_params(menu_type)
		self.end_directory()

	def search_history(self):
		from urllib.parse import unquote
		from caches.main_cache import main_cache
		search_mode_dict = {
		'movie': ('movie_queries', {'mode': 'search.get_key_id', 'media_type': 'movie', 'isFolder': 'false'}),
		'tvshow': ('tvshow_queries', {'mode': 'search.get_key_id', 'media_type': 'tv_show', 'isFolder': 'false'}),
		'anime': ('anime_queries', {'mode': 'search.get_key_id', 'media_type': 'anime', 'isFolder': 'false'}),
		'tvshow_anime': ('tvshow_anime_queries', {'mode': 'search.get_key_id', 'media_type': 'tvshow_anime', 'isFolder': 'false'}),
		'people': ('people_queries', {'mode': 'search.get_key_id', 'search_type': 'people', 'isFolder': 'false'}),
		'tmdb_keyword_movie': ('keyword_tmdb_movie_queries', {'mode': 'search.get_key_id', 'search_type': 'tmdb_keyword', 'media_type': 'movie', 'isFolder': 'false'}),
		'tmdb_keyword_tvshow': ('keyword_tmdb_tvshow_queries', {'mode': 'search.get_key_id', 'search_type': 'tmdb_keyword', 'media_type': 'tvshow', 'isFolder': 'false'}),
		'easynews_video': ('easynews_video_queries', {'mode': 'search.get_key_id', 'search_type': 'easynews_video', 'isFolder': 'false'}),
		'easynews_image': ('easynews_image_queries', {'mode': 'search.get_key_id', 'search_type': 'easynews_image', 'isFolder': 'false'}),
		'trakt_lists': ('trakt_list_queries', {'mode': 'search.get_key_id', 'search_type': 'trakt_lists', 'isFolder': 'false'}),
		'trakt_my_lists': ('trakt_my_list_queries', {'mode': 'search.get_key_id', 'search_type': 'trakt_my_lists', 'isFolder': 'false'}),
		'simkl_lists': ('simkl_list_queries', {'mode': 'search.get_key_id', 'search_type': 'simkl_lists', 'isFolder': 'false'})}
		setting_id, action_dict = search_mode_dict[self.list_name]
		url_params = dict(action_dict)
		data = main_cache.get(setting_id) or []
		self.add(action_dict, '[B]NEW SEARCH...[/B]', 'new')
		for i in data:
			try:
				key_id = unquote(i)
				url_params['key_id'] = key_id
				url_params['setting_id'] = setting_id
				cm_items = [('[B]Remove from history[/B]', 'RunPlugin(%s)' % self.build_url({'mode': 'search.remove', 'setting_id':setting_id, 'key_id': key_id})),
							('[B]Clear All History[/B]', 'RunPlugin(%s)' % self.build_url({'mode': 'search.clear_all', 'setting_id':setting_id, 'refresh': 'true'}))]
				self.add(url_params, key_id, 'calender', cm_items=cm_items)
			except: pass
		self.category_name = self.params_get('name') or 'History'
		self.end_directory(cache_to_disc=False)

	def keyword_results(self):
		from apis.tmdb_api import tmdb_keywords_by_query
		media_type, key_id = self.params_get('media_type'), self.params_get('key_id') or self.params_get('query')
		try: page_no = int(self.params_get('new_page', '1'))
		except: page_no = self.params_get('new_page')
		mode = 'build_movie_list' if media_type == 'movie' else 'build_tvshow_list'
		action = 'tmdb_movie_keyword_results' if media_type == 'movie' else 'tmdb_tv_keyword_results'
		data = tmdb_keywords_by_query(key_id, page_no)
		results = data['results']
		for item in results:
			name = item['name'].upper()
			self.add({'mode': mode, 'action': action, 'key_id': item['id'], 'iconImage': 'tmdb', 'category_name': name}, name, iconImage='tmdb')
		if data['total_pages'] > page_no:
			new_page = {'mode': 'navigator.keyword_results', 'key_id': key_id, 'category_name': self.category_name, 'new_page': str(data['page'] + 1)}
			self.add(new_page, 'Next Page (%s) >>' % new_page['new_page'], 'nextpage', False)
		self.category_name = 'Search Results for %s' % key_id.upper()
		self.end_directory()

	def choose_view(self):
		handle = int(sys.argv[1])
		view_type = self.params.get('view_type', 'view.main')
		if view_type in ('view.main', 'view.premium'):
			content = k.MENU_FOLDER_CONTENT
		else:
			content = self.params.get('content', 'files')
		name = self.params.get('name') or content or 'menus'
		self.add({'mode': 'navigator.set_view', 'view_type': view_type, 'name': name, 'isFolder': 'false'}, 'Set view and then click here', 'settings')
		k.set_content(handle, content)
		k.end_directory(handle)
		k.set_view_mode(view_type, content, False)

	def set_view(self):
		view_type = self.params.get('view_type', 'view.main')
		label = (self.params.get('name') or view_type.replace('view.', '').replace('_', ' ')).upper()
		view_id = str(k.current_window_object().getFocusId())
		set_setting(view_type, view_id)
		if view_type == 'view.episodes':
			from caches.settings_cache import default_setting_values
			episodes_single_default = (default_setting_values('view.episodes_single') or {}).get('setting_default', '55')
			if str(get_setting('redlight.view.episodes_single', episodes_single_default)) == str(episodes_single_default):
				set_setting('view.episodes_single', view_id)
		k.notification('%s: %s' % (label, k.get_infolabel('Container.Viewmode').upper()), time=500)

	def shortcut_folders(self):
		folders = nc.get_shortcut_folders()
		if folders:
			for i in folders:
				name = i[0]
				convert_sr = '[B]Remove Random[/B]' if '[COLOR red][RANDOM][/COLOR]' in name else '[B]Make Random[/B]'
				cm_items = [('[B]Rename[/B]', self.run_plugin % self.build_url({'mode': 'menu_editor.shortcut_folder_rename'})),
							('[B]Delete Folder[/B]' , self.run_plugin % self.build_url({'mode': 'menu_editor.shortcut_folder_delete'})),
							('[B]Make New Folder[/B]' , self.run_plugin % self.build_url({'mode': 'menu_editor.shortcut_folder_make'})),
							(convert_sr , self.run_plugin % self.build_url({'mode': 'menu_editor.shortcut_folder_convert', 'name': name}))]
				self.add({'mode': 'navigator.build_shortcut_folder_contents', 'name': name, 'iconImage': 'folder'}, name, 'folder', cm_items=cm_items)
		else: self.add({'mode': 'menu_editor.shortcut_folder_make', 'isFolder': 'false'}, '[I]Make New Folder...[/I]', 'new')
		self.category_name = 'Shortcut Folders'
		self.end_directory()

	def build_shortcut_folder_contents(self):
		list_name = self.params_get('name')
		if not list_name:
			k.notification('Shortcut folder not found.', 2500)
			return self.end_directory()
		is_random = '[COLOR red][RANDOM][/COLOR]' in list_name
		contents = nc.get_shortcut_folder_contents(list_name)
		if not contents and not is_random:
			random_name = '%s [COLOR red][RANDOM][/COLOR]' % list_name
			contents = nc.get_shortcut_folder_contents(random_name)
			if contents:
				list_name, is_random = random_name, True
		folder_icon = self.get_icon('folder')
		if is_random:
			from indexers.random_lists import random_shortcut_folders
			return random_shortcut_folders(list_name.replace(' [COLOR red][RANDOM][/COLOR]', ''), contents)
		if contents:
			can_move = len(contents) > 1
			for count, item in enumerate(contents):
				item_get = item.get
				iconImage = item_get('iconImage', None)
				if iconImage:
					if iconImage.startswith('http') and 'raw.githubusercontent.com' not in iconImage:
						icon, original_image = iconImage, True
					else:
						icon, original_image = k.resolve_list_icon(iconImage), False
				else: icon, original_image = folder_icon, False
				cm_items = []
				if can_move:
					cm_items.append(('[B]Move[/B]', self.run_plugin % self.build_url({'mode': 'menu_editor.shortcut_folder_edit', 'active_list': list_name, 'position': count, 'action': 'move'})))
				cm_items.extend([
				('[B]Remove[/B]' , self.run_plugin % self.build_url({'mode': 'menu_editor.shortcut_folder_edit', 'active_list': list_name, 'position': count, 'action': 'remove'})),
				('[B]Add Content[/B]' , self.run_plugin % self.build_url({'mode': 'menu_editor.shortcut_folder_add', 'name': list_name})),
				('[B]Rename[/B]' , self.run_plugin % self.build_url({'mode': 'menu_editor.shortcut_folder_edit', 'active_list': list_name, 'position': count, 'action': 'rename'})),
				('[B]Clear All[/B]' , self.run_plugin % self.build_url({'mode': 'menu_editor.shortcut_folder_edit', 'active_list': list_name, 'position': count, 'action': 'clear'}))])
				self.add(item, item_get('name'), icon, original_image, cm_items=cm_items)
		elif is_random: pass
		else: self.add({'mode': 'menu_editor.shortcut_folder_add', 'name': list_name, 'isFolder': 'false'}, '[I]Add Content...[/I]', 'new')
		self.end_directory()

	def discover_contents(self):
		from caches.discover_cache import discover_cache
		action, media_type = self.params_get('action', ''), self.params_get('media_type')
		if not action:
			if self.params_get('show_new', 'true') == 'true':
				self.add({'mode': 'discover_choice', 'media_type': media_type, 'isFolder': 'false'}, '[I]Make New Discover List...[/I]', 'new')
			results = discover_cache.get_all(media_type)
			if media_type == 'movie': mode, action = 'build_movie_list', 'tmdb_movies_discover'
			else: mode, action = 'build_tvshow_list', 'tmdb_tv_discover'
			for item in results:
				name, data = item['id'], item['data']
				cm_items = [('[B]Remove from history[/B]', 'RunPlugin(%s)' % self.build_url({'mode': 'navigator.discover_contents', 'action':'delete_one', 'name': name})),
							('[B]Clear All History[/B]', 'RunPlugin(%s)' % self.build_url({'mode': 'navigator.discover_contents', 'action':'clear_cache',
								'media_type': media_type}))]
				if '[random]' in data:
					self.add({'mode': 'random.%s' % mode, 'action': action, 'name': name, 'url': data, 'new_page': 'random', 'random': 'true'},
								name, 'discover', cm_items=cm_items)
				else: self.add({'mode': mode, 'action': action, 'name': name, 'url': data}, name, 'discover', cm_items=cm_items)
			self.end_directory()
		else:
			if action == 'delete_one': discover_cache.delete_one(self.params_get('name'))
			elif action == 'clear_cache': discover_cache.clear_cache(media_type)
			k.container_refresh()

	def exit_media_menu(self):
		params = k.get_property('redlight.exit_params')
		if not params: return
		params = k.sanitize_folder_url(params)
		k.container_refresh_input(params)

	def _set_submenu_exit_params(self, menu_type=None):
		if self.is_external: return
		parent = {'movie': 'MovieList', 'tvshow': 'TVShowList', 'anime': 'AnimeList'}
		if menu_type in parent:
			k.set_property('redlight.exit_params', k.build_folder_url({'mode': 'navigator.main', 'action': parent[menu_type]}))
		else:
			k.set_property('redlight.exit_params', k.build_folder_url({'mode': 'navigator.main', 'action': 'RootList'}))

	def _set_exit_params(self, parent_params):
		if self.is_external: return
		k.set_property('redlight.exit_params', k.build_folder_url(parent_params))

	def tips(self):
		tips_location = 'special://home/addons/plugin.video.redlight/resources/text/tips'
		files = sorted(k.list_dirs(tips_location)[1])
		tips_location += '/%s'
		tips_list = []
		tips_append = tips_list.append
		for item in files:
			tip = item.replace('.txt', '')[4:]
			if '!!HELP!!' in tip: tip, sort_order = tip.replace('!!HELP!!', '[COLOR crimson][B]HELP!!![/B][/COLOR] '), 0
			elif '!!NEW!!' in tip: tip, sort_order = tip.replace('!!NEW!!', '[COLOR chartreuse][B]NEW!![/B][/COLOR] '), 1
			elif '!!SPOTLIGHT!!' in tip: tip, sort_order = tip.replace('!!SPOTLIGHT!!', '[COLOR orange][B]SPOTLIGHT![/B][/COLOR] '), 2
			else: sort_order = 3
			params = {'mode': 'show_text', 'heading': tip, 'file': k.translate_path(tips_location % item), 'font_size': 'large', 'isFolder': 'false'}
			tips_append((params, tip, sort_order))
		item_list = sorted(tips_list, key=lambda x: x[2])
		for c, i in enumerate(item_list, 1): self.add(i[0], '[B]%02d. [/B]%s' % (c, i[1]), 'information')
		self.end_directory()

	def because_you_watched(self):
		from modules.watched_status import get_recently_watched
		from modules.episode_tools import single_last_watched_episodes
		recommend_type = s.recommend_service()
		menu_type = self.params_get('menu_type')
		action_dict = {'movie':
		{'mode': 'build_movie_list', 'action': {0: 'tmdb_movies_recommendations', 1: 'imdb_more_like_this', 2: 'ai_similar', 3: 'trakt_movies_related'}, 'media_type': 'movie'},
						'tvshow':
		{'mode': 'build_tvshow_list', 'action': {0: 'tmdb_tv_recommendations', 1: 'imdb_more_like_this', 2: 'ai_similar', 3: 'trakt_tv_related'}, 'media_type': 'episode'}}
		action_params = action_dict[menu_type]
		mode, action, media_type = action_params['mode'], action_params['action'][recommend_type], action_params['media_type']
		recently_watched = get_recently_watched(media_type)
		if media_type == 'episode': recently_watched = single_last_watched_episodes(recently_watched)
		for item in recently_watched:
			if media_type == 'movie':
				name = item['title']
				key_id = item['media_id'] if recommend_type in (0, 1, 3) else 'movie|%s' % item['media_id']
			else:
				name = '%s - %sx%s' % (item['title'], str(item['season']), str(item['episode']))
				key_id = item['media_ids']['tmdb'] if recommend_type in (0, 1, 3) else 'tvshow|%s' % item['media_ids']['tmdb']
			params = {'mode': mode, 'action': action, 'key_id': key_id, 'name': 'Because You Watched %s' % name}
			if recommend_type == 1: params['get_imdb'] = 'true'
			self.add(params, name, 'because_you_watched')
		self.end_directory()

	def build_random_lists(self):
		random_list_dict = {
		'movie': ('Random Movie Lists', nc.random_movie_lists),
		'tvshow': ('Random TV Show Lists', nc.random_tvshow_lists),
		'anime': ('Random Anime Lists', nc.random_anime_lists),
		'because_you_watched': ('Random Because You Watched Lists', nc.random_because_you_watched_lists),
		'tmdb_lists': ('Random TMDb Lists', nc.random_tmdb_lists),
		'personal_lists': ('Random Personal Lists', nc.random_personal_lists),
		'trakt_personal': ('Random Trakt Lists (Personal)', nc.random_trakt_lists_personal),
		'trakt_public': ('Random Trakt Lists (Public)', nc.random_trakt_lists_public),
		'simkl_lists': ('Random Simkl Lists', nc.random_simkl_lists)}
		self.category_name, function = random_list_dict[self.params_get('menu_type')]
		func = function()
		for item in func: self.add(item, item['name'], item['iconImage'])
		self.end_directory()

	def _safe_add(self, url_params, list_name, iconImage='folder', original_image=False, cm_items=[]):
		try: self.add(url_params, list_name, iconImage, original_image, cm_items)
		except Exception as e: k.logger('Red Light', 'my_lists add failed [%s]: %s' % (list_name, e))

	def add(self, url_params, list_name, iconImage='folder', original_image=False, cm_items=[]):
		isFolder = url_params.get('isFolder', 'true') == 'true'
		try:
			if original_image: icon = iconImage
			else: icon = k.resolve_list_icon(iconImage)
		except: icon = k.get_icon('folder')
		folder_params = dict(url_params)
		folder_params.pop('isFolder', None)
		url = k.build_folder_url(folder_params) if isFolder else k.build_url(folder_params)
		listitem = self.make_listitem()
		listitem.setLabel(list_name)
		k.set_list_item_art(listitem, icon, fanart=self.fanart)
		info_tag = listitem.getVideoInfoTag(True)
		info_tag.setPlot(' ')
		if not self.is_external:
			if isFolder:
				shortcut_params = dict(url_params)
				shortcut_params.update({'iconImage': iconImage, 'name': list_name})
				folder_item = ('[B]Add to Shortcut Folder[/B]', self.run_plugin % self.build_url({'mode': 'menu_editor.shortcut_folder_add_known', 'url': self.build_url(shortcut_params)}))
				if cm_items: cm_items.append(folder_item)
				else: cm_items = [folder_item]
			listitem.addContextMenuItems(cm_items)
		self.add_item(int(sys.argv[1]), url, listitem, isFolder)

	def end_directory(self, cache_to_disc=True, update_listing=False, skip_view_mode=False):
		handle = int(sys.argv[1])
		k.set_content(handle, k.MENU_FOLDER_CONTENT)
		k.set_category(handle, self.category_name)
		k.end_directory(handle, updateListing=update_listing, cacheToDisc=cache_to_disc)
		if not skip_view_mode:
			k.set_view_mode('view.main', k.MENU_FOLDER_CONTENT)
