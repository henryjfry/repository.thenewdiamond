# -*- coding: utf-8 -*-
import sys
from modules.metadata import tvshow_meta
from modules.utils import get_datetime, get_current_timestamp, paginate_list, TaskPool, manual_function_import
from modules import kodi_utils, settings, watched_status
# logger = kodi_utils.logger

class TVShows:
	main = ('tmdb_tv_popular', 'tmdb_tv_popular_today', 'tmdb_tv_premieres', 'tmdb_tv_airing_today','tmdb_tv_on_the_air', 'tmdb_tv_upcoming',
	'tmdb_anime_popular', 'tmdb_anime_popular_recent', 'tmdb_anime_premieres', 'tmdb_anime_upcoming', 'tmdb_anime_on_the_air')
	special = ('tmdb_tv_languages', 'tmdb_tv_networks', 'tmdb_tv_providers', 'tmdb_tv_year', 'tmdb_tv_decade', 'tmdb_tv_recommendations', 'tmdb_tv_genres',
	'tmdb_tv_search', 'tmdb_tv_keyword_results', 'tmdb_tv_keyword_results_direct', 'tmdb_anime_year', 'tmdb_anime_decade', 'tmdb_anime_genres',
	'tmdb_anime_providers')
	personal = {'in_progress_tvshows': ('modules.watched_status', 'get_in_progress_tvshows'),
				'watched_tvshows': ('modules.watched_status', 'get_watched_items'),
				'recent_watched_tvshows': ('modules.watched_status', 'get_recently_watched'),
				'favorites_tvshows': ('modules.favorites', 'get_favorites')}
	trakt_main = ('trakt_tv_trending', 'trakt_tv_trending_recent', 'trakt_tv_most_watched', 'trakt_tv_most_favorited',
	'trakt_anime_trending', 'trakt_anime_trending_recent', 'trakt_anime_most_watched', 'trakt_anime_most_favorited')
	trakt_special = ('trakt_tv_certifications', 'trakt_anime_certifications')
	trakt_personal = ('trakt_collection', 'trakt_watchlist', 'trakt_collection_lists', 'trakt_watchlist_lists', 'trakt_favorites')
	
	def __init__(self, params):
		self.params = params
		self.params_get = self.params.get
		self.category_name = self.params_get('category_name', None) or self.params_get('name', None) or 'TV Shows'
		self.id_type, self.list, self.action = self.params_get('id_type', 'tmdb_id'), self.params_get('list', []), self.params_get('action', None)
		self.items, self.new_page, self.total_pages, self.is_external = [], {}, None, kodi_utils.external()
		if 'is_anime_list' in params: self.is_anime_list = params['is_anime_list'] == 'true'
		elif self.action in self.personal: self.is_anime_list = False
		else:self.is_anime_list = None
		if self.is_external:
			self.widget_hide_next_page = settings.widget_hide_next_page()
			self.widget_hide_watched = self.action not in ('watched_tvshows', 'recent_watched_tvshows') and settings.widget_hide_watched()
		else: self.widget_hide_next_page, self.widget_hide_watched = False, False
		self.custom_order = self.params_get('custom_order', 'false') == 'true'
		self.paginate_start = int(self.params_get('paginate_start', '0'))
		self.append = self.items.append

	def fetch_list(self):
		handle = int(sys.argv[1])
		try:
			is_random = self.params_get('random', 'false') == 'true'
			try: page_no = int(self.params_get('new_page', '1'))
			except: page_no = self.params_get('new_page')
			if page_no == 1 and not self.is_external:
				folder_path = kodi_utils.folder_path()
				if not any([x in folder_path for x in ('build_season_list', 'build_episode_list')]): kodi_utils.set_property('fenlight.exit_params', folder_path)
			if self.action in self.personal: var_module, import_function = self.personal[self.action]
			else: var_module, import_function = 'apis.%s_api' % self.action.split('_')[0], self.action
			try: function = manual_function_import(var_module, import_function)
			except: pass
			if self.action in self.main:
				data = function(page_no)
				results = data['results']
				self.list = [i['id'] for i in results]
				if not is_random and data['total_pages'] > page_no: self.new_page = {'new_page': str(page_no + 1)}
			elif self.action in self.special:
				key_id = self.params_get('key_id') or self.params_get('query')
				if not key_id: return
				data = function(key_id, page_no)
				results = data['results']
				self.list = [i['id'] for i in results]
				if not is_random and data['total_pages'] > page_no: self.new_page = {'new_page': str(page_no + 1), 'key_id': key_id}
			elif self.action in self.personal:
				data = function('tvshow', page_no)
				data, total_pages = self.paginate_list(data, page_no)
				self.list = [i['media_id'] for i in data]
				if total_pages > 2: self.total_pages = total_pages
				if total_pages > page_no: self.new_page = {'new_page': str(page_no + 1), 'paginate_start': self.paginate_start}
			elif self.action in self.trakt_main:
				self.id_type = 'trakt_dict'
				data = function(page_no)
				try: self.list = [i['show']['ids'] for i in data]
				except: self.list = [i['ids'] for i in data]
				if not is_random and self.action != 'trakt_recommendations': self.new_page = {'new_page': str(page_no + 1)}
			elif self.action in self.trakt_special:
				key_id = self.params_get('key_id', None)
				if not key_id: return
				self.id_type = 'trakt_dict'
				data = function(key_id, page_no)
				self.list = [i['show']['ids'] for i in data]
				if not is_random: self.new_page = {'new_page': str(page_no + 1), 'key_id': key_id}
			elif self.action in self.trakt_personal:
				self.id_type = 'trakt_dict'
				data = function('shows', page_no)
				if self.action in ('trakt_collection_lists', 'trakt_watchlist_lists', 'trakt_favorites'): total_pages = 1
				else: data, total_pages = self.paginate_list(data, page_no)
				self.list = [i['media_ids'] for i in data]
				if total_pages > 2: self.total_pages = total_pages
				try:
					if total_pages > page_no: self.new_page = {'new_page': str(page_no + 1), 'paginate_start': self.paginate_start}
				except: pass
			elif self.action == 'trakt_recommendations':
				self.id_type = 'trakt_dict'
				data = function('shows')
				data, total_pages = self.paginate_list(data, page_no)
				self.list = [i['ids'] for i in data]
				if total_pages > 2: self.total_pages = total_pages
				try:
					if total_pages > page_no: self.new_page = {'new_page': str(page_no + 1), 'paginate_start': self.paginate_start}
				except: pass
			elif self.action == 'tmdb_tv_discover':
				url = self.params_get('url')
				data = function(url, page_no)
				results = data['results']
				self.list = [i['id'] for i in results]
				if data['total_pages'] > page_no: self.new_page = {'url': url, 'new_page': str(data['page'] + 1)}
			elif self.action == 'imdb_more_like_this':
				from apis.imdb_api import imdb_more_like_this
				if self.params_get('get_imdb'):
					self.params['key_id'] = tvshow_meta('tmdb_id', self.params_get('key_id'), settings.tmdb_api_key(), settings.mpaa_region(),
											get_datetime(), get_current_timestamp())['imdb_id']
				self.id_type = 'imdb_id'
				self.list = imdb_more_like_this(self.params_get('key_id'))
			kodi_utils.add_items(handle, self.worker())
			if self.new_page and not self.widget_hide_next_page:
						self.new_page.update({'mode': 'build_tvshow_list', 'action': self.action, 'category_name': self.category_name})
						kodi_utils.add_dir(handle, self.new_page, 'Next Page (%s) >>' % self.new_page['new_page'], 'nextpage', kodi_utils.get_icon('nextpage_landscape'))
		except: pass
		kodi_utils.set_content(handle, 'tvshows')
		kodi_utils.set_category(handle, self.category_name)
		kodi_utils.end_directory(handle, cacheToDisc=False if self.is_external else True)
		if not self.is_external:
			if self.params_get('refreshed') == 'true': kodi_utils.sleep(1000)
			kodi_utils.set_view_mode('view.tvshows', 'tvshows', self.is_external)

	def build_tvshow_content(self, _position, _id):
		# try:
		meta = tvshow_meta(self.id_type, _id, self.tmdb_api_key, self.mpaa_region, self.current_date, self.current_time, self.is_anime_list)
		if not meta or 'blank_entry' in meta: return
		cm = []
		cm_append = cm.append
		listitem = self.make_listitem()
		set_properties = listitem.setProperties
		meta_get = meta.get
		premiered = meta_get('premiered')
		trailer, title, year = meta_get('trailer'), meta_get('title'), meta_get('year') or '2050'
		tvdb_id, imdb_id = meta_get('tvdb_id'), meta_get('imdb_id')
		if self.rpdb_api_key:
			try: poster = meta_get('rpdb_poster') % self.rpdb_api_key
			except: poster = meta_get('poster') or self.poster_empty
		else: poster = meta_get('poster') or self.poster_empty
		fanart = meta_get('fanart') or self.fanart_empty
		clearlogo, landscape = meta_get('clearlogo') or '', meta_get('landscape') or ''
		thumb = poster or landscape or fanart
		tmdb_id, total_seasons, total_aired_eps = meta_get('tmdb_id'), meta_get('total_seasons'), meta_get('total_aired_eps')
		unaired = total_aired_eps == 0
		if unaired: progress, playcount, total_watched, total_unwatched = 0, 0, 0, total_aired_eps
		else:
			playcount, total_watched, total_unwatched = watched_status.get_watched_status_tvshow(self.watched_info.get(str(tmdb_id), None), total_aired_eps)
			if total_watched: progress = watched_status.get_progress_status_tvshow(total_watched, total_aired_eps)
			else: progress = 0
			visible_progress = '0' if progress == 100 else progress
		extras_params = self.build_url({'mode': 'extras_menu_choice', 'tmdb_id': tmdb_id, 'media_type': 'tvshow', 'is_external': self.is_external})
		options_params = self.build_url({'mode': 'options_menu_choice', 'content': 'tvshow', 'tmdb_id': tmdb_id, 'poster': poster,
									'is_external': self.is_external})
		browse_recommended_params = self.build_url({'mode': 'build_tvshow_list', 'action': 'tmdb_tv_recommendations', 'key_id': tmdb_id, 'is_external': self.is_external,
			'name': 'Recommended based on %s' % title})
		browse_more_like_this_params = self.build_url({'mode': 'build_tvshow_list', 'action': 'imdb_more_like_this', 'key_id': imdb_id, 'is_external': self.is_external,
										'name': 'More Like This based on %s' % title, 'is_external': self.is_external})
		
		trakt_manager_params = self.build_url({'mode': 'trakt_manager_choice', 'tmdb_id': tmdb_id, 'imdb_id': imdb_id, 'tvdb_id': tvdb_id, 'media_type': 'tvshow', 'icon': poster})
		personal_manager_params = self.build_url({'mode': 'personallists_manager_choice', 'list_type': 'tvshow', 'tmdb_id': tmdb_id, 'title': title,
										'premiered': premiered, 'current_time': self.current_time, 'icon': poster})
		tmdb_manager_params = self.build_url({'mode': 'tmdblists_manager_choice', 'media_type': 'tv', 'tmdb_id': tmdb_id, 'icon': poster})
		favorites_manager_params = self.build_url({'mode': 'favorites_manager_choice', 'media_type': 'tvshow', 'tmdb_id': tmdb_id, 'title': title})
		if self.all_episodes:
			if self.all_episodes == 1 and total_seasons > 1: url_params = self.build_url({'mode': 'build_season_list', 'tmdb_id': tmdb_id})
			else: url_params = self.build_url({'mode': 'build_episode_list', 'tmdb_id': tmdb_id, 'season': 'all'})
		else: url_params = self.build_url({'mode': 'build_season_list', 'tmdb_id': tmdb_id})
		if self.open_extras:
			cm_append(['extras', ('[B]Browse[/B]', 'Container.Update(%s)' % url_params)])
			url_params = extras_params
		else: cm_append(['extras', ('[B]Extras[/B]', 'RunPlugin(%s)' % extras_params)])
		cm_append(['options', ('[B]Options[/B]', 'RunPlugin(%s)' % options_params)])
		cm_append(['recommended', ('[B]Browse Recommended[/B]', self.window_command % browse_recommended_params)])
		cm_append(['more_like_this', ('[B]Browse More Like This[/B]', self.window_command % browse_more_like_this_params)])
		if imdb_id: cm_append(['in_trakt_list', ('[B]In Trakt Lists[/B]', self.window_command % \
						self.build_url({'mode': 'trakt.list.in_trakt_lists', 'media_type': 'tvshow', 'imdb_id': imdb_id, 'category_name': '%s In Trakt Lists' % title}))])
		cm_append(['trakt_manager', ('[B]Trakt Lists Manager[/B]', 'RunPlugin(%s)' % trakt_manager_params)])
		cm_append(['personal_manager', ('[B]Personal Lists Manager[/B]', 'RunPlugin(%s)' % personal_manager_params)])
		cm_append(['tmdb_manager', ('[B]TMDb Lists Manager[/B]', 'RunPlugin(%s)' % tmdb_manager_params)])
		cm_append(['favorites_manager', ('[B]Favorites Manager[/B]', 'RunPlugin(%s)' % favorites_manager_params)])
		if playcount:
			if self.widget_hide_watched: return
		elif not unaired:
			cm_append(['mark_watched', ('[B]Mark Watched %s[/B]' % self.watched_title, 'RunPlugin(%s)' % \
						self.build_url({'mode': 'watched_status.mark_tvshow', 'action': 'mark_as_watched',
																		'title': title,'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id}))])
		if progress:
			cm_append(['mark_watched', ('[B]Mark Unwatched %s[/B]' % self.watched_title, 'RunPlugin(%s)' % \
						self.build_url({'mode': 'watched_status.mark_tvshow', 'action': 'mark_as_unwatched',
																		'title': title, 'tmdb_id': tmdb_id, 'tvdb_id': tvdb_id}))])
		set_properties({'watchedepisodes': str(total_watched), 'unwatchedepisodes': str(total_unwatched)})
		set_properties({'watchedprogress': visible_progress, 'totalepisodes': str(total_aired_eps), 'totalseasons': str(total_seasons)})
		if not self.is_external: cm_append(['exit', ('[B]Exit TV Show List[/B]', 'RunPlugin(%s)' % self.build_url({'mode': 'navigator.exit_media_menu'}))])
		if self.is_external:
			cm.extend([['refresh', ('[B]Refresh Widgets[/B]', 'RunPlugin(%s)' % self.build_url({'mode': 'refresh_widgets'}))],
					['reload', ('[B]Reload Widgets[/B]', 'RunPlugin(%s)' % self.build_url({'mode': 'kodi_refresh'}))]])
		cm = self.sort_context_menu(cm)
		listitem.setLabel(title)
		listitem.addContextMenuItems(cm)
		listitem.setArt({'poster': poster, 'fanart': fanart, 'icon': poster, 'clearlogo': clearlogo, 'landscape': landscape, 'thumb': thumb, 'icon': landscape,
						'tvshow.poster': poster, 'tvshow.clearlogo': clearlogo})
		info_tag = listitem.getVideoInfoTag()
		info_tag.setMediaType('tvshow'), info_tag.setTitle(title), info_tag.setTvShowTitle(title), info_tag.setOriginalTitle(meta_get('original_title'))
		info_tag.setUniqueIDs({'imdb': imdb_id, 'tmdb': str(tmdb_id), 'tvdb': str(tvdb_id)}), info_tag.setIMDBNumber(imdb_id)
		info_tag.setPlot(meta_get('plot')), info_tag.setPlaycount(playcount), info_tag.setGenres(meta_get('genre')), info_tag.setYear(int(year))
		info_tag.setTagLine(meta_get('tagline')), info_tag.setStudios(meta_get('studio')), info_tag.setWriters(meta_get('writer')), info_tag.setDirectors(meta_get('director'))
		info_tag.setVotes(meta_get('votes')), info_tag.setMpaa(meta_get('mpaa')), info_tag.setDuration(meta_get('duration')), info_tag.setCountries(meta_get('country'))
		info_tag.setTrailer(meta_get('trailer')), info_tag.setPremiered(premiered)
		info_tag.setTvShowStatus(meta_get('status')), info_tag.setRating(meta_get('rating'))
		cast = meta_get('short_cast', []) or meta_get('cast', []) or []
		info_tag.setCast([self.kodi_actor(name=item['name'], role=item['role'], thumbnail=item['thumbnail']) for item in cast])
		set_properties({
			'fenlight.extras_params': extras_params,
			'fenlight.options_params': options_params,
			'fenlight.browse_recommended_params': browse_recommended_params,
			'fenlight.browse_more_like_this_params': browse_more_like_this_params,
			'fenlight.trakt_manager_params': trakt_manager_params,
			'fenlight.personal_manager_params': personal_manager_params,
			'fenlight.tmdb_manager_params': tmdb_manager_params,
			'fenlight.favorites_manager_params': favorites_manager_params
			})
		self.append(((url_params, listitem, self.is_folder), _position))
		# except: pass

	def worker(self):
		self.kodi_actor, self.make_listitem, self.build_url = kodi_utils.kodi_actor(), kodi_utils.make_listitem, kodi_utils.build_url
		self.poster_empty, self.fanart_empty = kodi_utils.get_icon('box_office'), kodi_utils.addon_fanart()
		self.current_date, self.current_time = get_datetime(), get_current_timestamp()
		self.tmdb_api_key, self.mpaa_region = settings.tmdb_api_key(), settings.mpaa_region()
		self.rpdb_api_key = settings.rpdb_api_key('tvshow')
		self.all_episodes, self.open_extras = settings.default_all_episodes(), settings.media_open_action('tvshow') == 1
		self.cm_sort_order = settings.cm_sort_order()
		self.perform_cm_sort = self.cm_sort_order != settings.cm_default_order()
		self.is_folder = False if self.open_extras else True
		self.watched_indicators = settings.watched_indicators()
		self.watched_title = 'Trakt' if self.watched_indicators == 1 else 'FENLAM'
		self.watched_info = watched_status.watched_info_tvshow(watched_status.get_database(self.watched_indicators))
		self.window_command = 'ActivateWindow(Videos,%s,return)' if self.is_external else 'Container.Update(%s)'
		if self.custom_order:
			threads = TaskPool().tasks(self.build_tvshow_content, self.list, min(len(self.list), settings.max_threads()))
			[i.join() for i in threads]
		else:
			threads = TaskPool().tasks_enumerate(self.build_tvshow_content, self.list, min(len(self.list), settings.max_threads()))
			[i.join() for i in threads]
			self.items.sort(key=lambda k: k[1])
			self.items = [i[0] for i in self.items]
		return self.items

	def sort_context_menu(self, context_menu_items):
		if self.perform_cm_sort:
			try: context_menu_items = sorted([i for i in context_menu_items if i[0] in self.cm_sort_order], key=lambda k: self.cm_sort_order[k[0]])
			except: pass
		return [i[1] for i in context_menu_items]

	def paginate_list(self, data, page_no):
		if settings.paginate(self.is_external):
			limit = settings.page_limit(self.is_external)
			data, total_pages = paginate_list(data, page_no, limit, self.paginate_start)
			if self.is_external: self.paginate_start = limit
		else: total_pages = 1
		return data, total_pages
