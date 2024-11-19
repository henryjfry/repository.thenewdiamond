import os, shutil, urllib.request, urllib.parse, urllib.error
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import requests, json
from pathlib import Path
from resources.lib import Utils
from resources.lib import TheMovieDB
from resources.lib.WindowManager import wm
from resources.lib.VideoPlayer import PLAYER
from resources.lib.OnClickHandler import OnClickHandler
from resources.lib.DialogBaseList import DialogBaseList
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib.library import basedir_tv_path
from resources.lib.library import basedir_movies_path
from resources.lib.library import trakt_add_movie
from resources.lib.library import trakt_add_tv
from resources.lib.library import next_episode_show
from resources.lib.library import trakt_next_episode_normal
from resources.lib.library import trakt_next_episode_rewatch
from resources.lib.library import trakt_watched_tv_shows
from resources.lib.library import trakt_unwatched_tv_shows
from resources.lib.library import trakt_watched_movies
from resources.lib.library import trakt_collection_shows
from resources.lib.library import trakt_collection_movies
from resources.lib.library import trakt_uncollected_watched_movies
from resources.lib.library import trakt_unwatched_collection_movies
from resources.lib.library import trakt_trending_movies
from resources.lib.library import trakt_trending_shows
from resources.lib.library import trakt_popular_movies
from resources.lib.library import trakt_popular_shows
from resources.lib.library import trakt_lists
from resources.lib.library import trakt_watched_tv_shows_progress
from resources.lib.library import trak_auth
from resources.lib.TheMovieDB import get_trakt_playback
from resources.lib.TheMovieDB import extended_episode_info
#from resources.lib.TheMovieDB import extended_season_info
from resources.lib.TheMovieDB import extended_movie_info
from resources.lib.library import get_trakt_data
from datetime import datetime, timedelta


from inspect import currentframe, getframeinfo
#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
ch = OnClickHandler()
SORTS = {
	'movie': {
		'popularity': 'Popularity',
		'vote_average': 'Vote average',
		'vote_count': 'Vote count',
		'release_date': 'Release date',
		'revenue': 'Revenue',
		'original_title': 'Original title'
		},
	'tv': {
		'popularity': 'Popularity',
		'vote_average': 'Vote average',
		'vote_count': 'Vote count',
		'first_air_date': 'First aired'
		}}
LANGUAGES = [
	{'id': '', 'name': ''},
	{'id': 'bg', 'name': 'Bulgarian'},
	{'id': 'cs', 'name': 'Czech'},
	{'id': 'da', 'name': 'Danish'},
	{'id': 'de', 'name': 'German'},
	{'id': 'el', 'name': 'Greek'},
	{'id': 'en', 'name': 'English'},
	{'id': 'es', 'name': 'Spanish'},
	{'id': 'fi', 'name': 'Finnish'},
	{'id': 'fr', 'name': 'French'},
	{'id': 'he', 'name': 'Hebrew'},
	{'id': 'hi', 'name': 'Hindi'},
	{'id': 'hr', 'name': 'Croatian'},
	{'id': 'hu', 'name': 'Hungarian'},
	{'id': 'it', 'name': 'Italian'},
	{'id': 'ja', 'name': 'Japanese'},
	{'id': 'ko', 'name': 'Korean'},
	{'id': 'nl', 'name': 'Dutch'},
	{'id': 'no', 'name': 'Norwegian'},
	{'id': 'pl', 'name': 'Polish'},
	{'id': 'pt', 'name': 'Portuguese'},
	{'id': 'ru', 'name': 'Russian'},
	{'id': 'sl', 'name': 'Slovenian'},
	{'id': 'sv', 'name': 'Swedish'},
	{'id': 'tr', 'name': 'Turkish'},
	{'id': 'zh', 'name': 'Chinese'}
]

menu = [
	#{'button': 6666, 'position': 1},
	#{'button': 600, 'position': 2},
	#{'button': 700, 'position': 3},
	#{'button': 6667, 'position': 4},
	#{'button': 6668, 'position': 5},
	{'button': 6000, 'position': 1}, #SEARCH
	{'button': 6001, 'position': 2}, #SEARCH_YT
	#{'button': 9000, 'position': 8}, #CONTROL_LIST
	{'button': 5001, 'position': 3}, #TYPE MOVIE/TV
	{'button': 5002, 'position': 4}, #SORT_BY
	{'button': 5003, 'position': 5}, #ORDER_BY
	#{'button': 5004, 'position': 12}, #LABEL____FILTER______LABEL
	{'button': 5005, 'position': 6}, #Original Language
	{'button': 5006, 'position': 7}, #Page Number
	{'button': 5007, 'position': 8}, #Genre
	{'button': 5008, 'position': 9}, #Release date
	{'button': 5009, 'position': 10}, #Certification
	{'button': 5010, 'position': 11}, #Actor / Crew member
	{'button': 5011, 'position': 12}, #Keyword
	{'button': 5012, 'position': 13}, #Studio
	{'button': 5013, 'position': 14}, #Vote count
	{'button': 5014, 'position': 15}, #IMDB_Lists
	{'button': 5015, 'position': 16}, #Trakt_Stuff
	{'button': 5016, 'position': 17}, #User_Lists
	{'button': 5017, 'position': 18}, #Plugin Routes
	{'button': 5018, 'position': 19}, #Edit Filters
	{'button': 5019, 'position': 20} #EXIT
]


def write_fetch_data_dict_file():
	import os
	addon = xbmcaddon.Addon()
	addon_path = addon.getAddonInfo('path')
	addonID = addon.getAddonInfo('id')
	addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
	if not os.path.exists(Path(addonUserDataFolder)):
		os.makedirs(Path(addonUserDataFolder))
	fetch_data_dict_file = open(Path(addonUserDataFolder + '/fetch_data_dict'), "w+", encoding="utf-8")
	return fetch_data_dict_file

def read_fetch_data_dict_file():
	addon = xbmcaddon.Addon()
	addon_path = addon.getAddonInfo('path')
	addonID = addon.getAddonInfo('id')
	addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
	return open(Path(addonUserDataFolder + '/fetch_data_dict'), "r")

def get_tmdb_window(window_type):
	Utils.show_busy()
	class DialogVideoList(DialogBaseList, window_type):

		def setup_filter(self, meta_filters):
			#import urllib.parse
			#meta_filters_encoded  = urllib.parse.quote(str(meta_filters))
			#meta_filters_encoded = meta_filters
			#meta_filters_decoded  = eval(urllib.parse.unquote(meta_filters_encoded))
			meta_filters_decoded = meta_filters

			for i in meta_filters_decoded['filters']:
				if i == 'sort':
					self.order = meta_filters_decoded['filters'][i]
				if i == 'sort_string':
					if self.media_type == 'tv':
						if meta_filters_decoded['filters'][i] in str(SORTS['tv']):
							self.sort_label = SORTS['tv'][meta_filters_decoded['filters'][i]]
							self.sort = meta_filters_decoded['filters'][i]
						else:
							self.sort = 'popularity'
							self.sort_label = SORTS['tv']['popularity']
					else:
						if meta_filters_decoded['filters'][i] in str(SORTS['movie']):
							self.sort_label = SORTS['movie'][meta_filters_decoded['filters'][i]]
							self.sort = meta_filters_decoded['filters'][i]
						else:
							self.sort = 'popularity'
							self.sort_label = SORTS['movie']['popularity']
				if 'genre' in str(i) and i != 'genre_mode':
					response = TheMovieDB.get_tmdb_data('genre/%s/list?language=%s&' % (self.type, xbmcaddon.Addon().getSetting('LanguageID')), 10)
					id_list = [item['id'] for item in response['genres']]
					label_list = [item['name'] for item in response['genres']]
					ids = []
					labels = ', '
					ids_or = '| '
					for genre in meta_filters_decoded['filters'][i]:
						labels = labels + genre.capitalize() + ', '
						for idx, x in enumerate(label_list):
							if str(genre).lower() in str(x).lower():
								ids.append(id_list[idx])
								ids_or = ids_or + str(id_list[idx]) + '| '
					labels = labels[2:-2]
					ids_or = ids_or[2:-2]
					if meta_filters_decoded['filters']['genre_mode'] == 'OR':
						ids = ids_or
						labels = labels.replace(',','|')
					if 'without_genres' == i:
						self.add_filter('without_genres', ids, 'Genres', 'NOT ' + labels)
					if 'with_genres' == i:
						self.add_filter('with_genres', ids, 'Genres', labels)
				if i == 'with_original_language':
					id = meta_filters_decoded['filters'][i]
					id_list = [item['id'] for item in LANGUAGES]
					label_list = [item['name'] for item in LANGUAGES]
					self.add_filter('with_original_language', id, 'Original language', label_list[id_list.index(id)])
				if i == 'vote_count.gte':
					result = meta_filters_decoded['filters'][i]
					self.add_filter('vote_count.gte', result, 'Vote count', ' > %s' % result)
				if i == 'vote_count.lte':
					result = meta_filters_decoded['filters'][i]
					self.add_filter('vote_count.lte', result, 'Vote count', ' < %s' % result)
				if i == 'upper_year' or i == 'lower_year':
					if i == 'upper_year':
						order = 'lte'
						value = '%s-12-31' % meta_filters_decoded['filters'][i] 
						label = ' < ' + meta_filters_decoded['filters'][i] 
					if i == 'lower_year':
						order = 'gte'
						value = '%s-01-01' % meta_filters_decoded['filters'][i] 
						label = ' > ' + meta_filters_decoded['filters'][i] 
					if self.media_type == 'movie':
						self.add_filter('primary_release_date.%s' % order, value, 'Year', label)
					if self.media_type == 'tv':
						self.add_filter('first_air_date.%s' % order, value, 'First aired', label)

		def __init__(self, *args, **kwargs):
			super(DialogVideoList, self).__init__(*args, **kwargs)
			self.type = kwargs.get('type', 'movie')
			self.media_type = self.type
			self.list_id = kwargs.get('list_id', False)
			self.sort = kwargs.get('sort', 'popularity')
			self.sort_label = kwargs.get('sort_label', 'Popularity')
			self.order = kwargs.get('order', 'desc')
			self.mode2 = None
			self.curr_window = None
			self.prev_window = None
			self.filter_url = None
			self.filter = None
			self.control_id2 = None
			self.action2  = None
			self.listitems = []
			self.listitems2 = []
			xbmcgui.Window(10000).clearProperty('ImageFilter')
			xbmcgui.Window(10000).clearProperty('ImageColor')

			#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			if wm.custom_filter:
				self.setup_filter(wm.custom_filter)
				wm.custom_filter = None
				self.update_content(force_update=kwargs.get('force', False))

			if self.listitem_list:
				#xbmc.log(str(wm.page), level=xbmc.LOGINFO)
				#xbmc.log(str(self.page), level=xbmc.LOGINFO)

				#self.listitems = Utils.create_listitems(self.listitem_list)
				#self.total_items = len(self.listitem_list)
				self.update_content(force_update=kwargs.get('force', False))
			elif self.filters == []:
				try:
					import os
					addon = xbmcaddon.Addon()
					addon_path = addon.getAddonInfo('path')
					addonID = addon.getAddonInfo('id')
					addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
					if os.path.exists(str(Path(addonUserDataFolder + '/custom_for_me'))):
						self.add_filter('with_original_language', 'en', 'Original language', 'English')
						self.add_filter('without_genres', '27', 'Genres', 'NOT Horror')
						self.add_filter('vote_count.gte', '1000', '%s (%s)' % ('Vote count', '>'), '1000')
					else:
						self.filters == []
				except:
					self.filters == []
				self.update_content(force_update=kwargs.get('force', False))
			elif self.filters != []:
				self.update_content(force_update=kwargs.get('force', False))

		def update_fetch_data_dict(self, info, fetch_data_dict):
			fetch_data_dict['self.info'] = info
			fetch_data_dict['self.mode'] = self.mode
			fetch_data_dict['self.sort'] = self.sort
			fetch_data_dict['self.sort_label'] = self.sort_label
			fetch_data_dict['self.order'] = self.order
			fetch_data_dict['self.type'] = self.type
			fetch_data_dict['self.search_str'] = self.search_str
			fetch_data_dict['self.page'] = self.page
			fetch_data_dict['self.filter_label'] = self.filter_label
			fetch_data_dict['self.list_id'] = self.list_id
			fetch_data_dict['self.filter_url'] = self.filter_url
			fetch_data_dict['self.total_items'] = self.total_items
			fetch_data_dict['self.total_pages'] = self.total_pages
			fetch_data_dict['self.next_page_token'] = self.next_page_token
			fetch_data_dict['self.prev_page_token'] = self.prev_page_token
			fetch_data_dict['self.filters'] = self.filters
			fetch_data_dict['self.filter'] = self.filter


			return fetch_data_dict

		def get_fetch_data_dict_read(self, fetch_data_dict_read):
			try: self.mode = fetch_data_dict_read['self.mode']
			except: pass
			try: self.type = fetch_data_dict_read['self.type']
			except: pass
			try: self.sort_label = fetch_data_dict_read['self.sort_label']
			except: pass
			try: self.sort = fetch_data_dict_read['self.sort']
			except: pass
			try: info = fetch_data_dict_read['self.info']
			except: pass
			try: self.order = fetch_data_dict_read['self.order']
			except: pass
			try: self.search_str = fetch_data_dict_read['self.search_str']
			except: pass
			try: self.filter_label = fetch_data_dict_read['self.filter_label'].replace('Results for:  ','')
			except: pass
			try: self.page = fetch_data_dict_read['self.page']
			except: pass
			try: self.list_id = fetch_data_dict_read['self.list_id']
			except: pass
			try: self.filter_url = fetch_data_dict_read['self.filter_url']
			except: pass

			try: self.filters = fetch_data_dict_read['self.filters']
			except: pass
			try: self.filter = fetch_data_dict_read['self.filter']
			except: pass

			try: self.total_items = fetch_data_dict_read['self.total_items']
			except: pass
			try: self.total_pages = fetch_data_dict_read['self.total_pages']
			except: pass

			try: self.next_page_token = fetch_data_dict_read['self.next_page_token']
			except: pass
			try: self.prev_page_token = fetch_data_dict_read['self.prev_page_token']
			except: pass

			return info

		def onClick(self, control_id):
			#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			#xbmc.log('%s,%s,%s,%s,' % (control_id,self.focus_id,self.position,self.listitems[self.position].getProperty('tmdb_id'))+'===>OPENINFO', level=xbmc.LOGINFO)
			if (self.search_str == 'Trakt Episodes/Movies in progress' or self.search_str == 'Trakt Calendar Episodes') and xbmc.getInfoLabel('listitem.DBTYPE') == 'episode':
				try: wm.open_tvshow_info(prev_window=self, tmdb_id=self.listitem.getProperty('tmdb_id'), dbid=self.listitem.getProperty('dbid'))
				except: wm.open_tvshow_info(prev_window=self, tmdb_id=self.listitems[self.position].getProperty('tmdb_id'), dbid=self.listitems[self.position].getProperty('dbid'))
			else:
				super(DialogVideoList, self).onClick(control_id)
				self.control_id2 = control_id
				ch.serve(control_id, self)

		def onAction(self, action):
			super(DialogVideoList, self).onAction(action)
			self.action2 = action
			ch.serve_action(action, self.getFocusId(), self)

		def update_ui(self):
			types = {
				'movie': 'Movies',
				'tv': 'TV shows',
				'person': 'Persons'
				}
			self.setProperty('Type', types[self.type])
			#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			self.getControl(5006).setVisible(self.type != 'tv')
			self.getControl(5008).setVisible(self.type != 'tv')
			self.getControl(5009).setVisible(self.type != 'tv')
			self.getControl(5010).setVisible(self.type != 'tv')
			super(DialogVideoList, self).update_ui()

		def go_to_next_page(self):
			if self.page == self.total_pages:
				return
			self.get_column()
			wm.page_position = self.position -16
			if self.page < self.total_pages:
				self.page += 1
				self.prev_page_token = self.page_token
				self.page_token = self.next_page_token
				self.update()

		def go_to_prev_page(self):
			if self.page == 1:
				return
			self.get_column()
			wm.prev_page_flag = True
			wm.prev_page_num = self.page -1 
			wm.page_position = self.position +16
			if self.page > 1:
				self.page -= 1
				self.next_page_token = self.page_token
				self.page_token = self.prev_page_token
				self.update()


		@ch.action('pagedown', 5019)
		def pgdn_5019(self):
			xbmc.executebuiltin('Control.SetFocus('+str(6000)+')')

		@ch.action('pageup', 6000)
		def pgup_6000(self):
			xbmc.executebuiltin('Control.SetFocus('+str(5019)+')')


		@ch.action('pagedown', 6000)
		def pgdn_6000(self):
			xbmc.executebuiltin('Control.SetFocus('+str(5001)+')')

		@ch.action('pageup', 5001)
		def pgup_5001(self):
			xbmc.executebuiltin('Control.SetFocus('+str(5019)+')')




		@ch.action('play', 500)
		def context_play(self):
			Utils.context_play(window=self,tmdb_id=self.listitem.getProperty('id'))

		@ch.action('info', 500)
		@ch.action('contextmenu', 500)
		def context_menu(self):
			self.position = self.getControl(500).getSelectedPosition()
			wm.position = self.position
			xbmcgui.Window(10000).setProperty('focus_id', str(500))
			xbmcgui.Window(10000).setProperty('position', str(self.position))
			if str(xbmcaddon.Addon(addon_ID()).getSetting('trakt_kodi_mode')) == 'Trakt Only':
				trakt_only = True
			else:
				trakt_only = False
			try:
				last_played_tmdb_helper = xbmcgui.Window(10000).getProperty('last_played_tmdb_helper')
				last_played_tmdb_helper2 = xbmcaddon.Addon(addon_ID()).getSetting('last_played_tmdb_helper')
			except:
				last_played_tmdb_helper2 = ''
			if last_played_tmdb_helper =='' or last_played_tmdb_helper2 != '':
				last_played_tmdb_helper = last_played_tmdb_helper2
			if self.listitem.getProperty('dbid') and self.listitem.getProperty('dbid') != 0:
				dbid = self.listitem.getProperty('dbid')
			else:
				dbid = 0
			item_id = self.listitem.getProperty('id')
			if xbmc.getInfoLabel('listitem.DBTYPE') == 'episode':
				item_id = self.listitems[self.position].getProperty('tmdb_id')
			self_type = 'tv'
			if xbmc.getInfoLabel('listitem.DBTYPE') == 'movie':
				self_type = 'movie'
			elif xbmc.getInfoLabel('listitem.DBTYPE') in ['tv', 'tvshow', 'season', 'episode']:
				self_type = 'tv'
				if self.search_str == 'Trakt Episodes/Movies in progress' or self.search_str == 'Trakt Calendar Episodes':
					self_type = 'movie'
			if self_type == 'tv':
				imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'imdb_id')
				tvdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'tvdb_id')
			else:
				imdb_id = TheMovieDB.get_imdb_id_from_movie_id(item_id)
			listitems = []
			if self.listitem.getProperty('dbid'):
				if self_type == 'tv':
					listitems += ['Play Kodi Next Episode']
					listitems += ['Play Trakt Next Episode']
					listitems += ['Play Trakt Next Episode (Rewatch)']
					listitems += ['Play first episode']
				else:
					listitems += ['Play']
				listitems += ['Remove from library']
			else:
				if self_type == 'tv':
					listitems += ['Play Trakt Next Episode']
					listitems += ['Play Trakt Next Episode (Rewatch)']
					listitems += ['Play first episode']
				else:
					listitems += ['Play']
				if trakt_only == False:
					listitems += ['Add to library']
			listitems += ['Search item']
			listitems += ['Trailer']
			listitems += ['TMDBHelper Context']
			if self.search_str == 'Trakt Episodes/Movies in progress':
				listitems += ['Trakt remove playback entry']
			listitems += ['TasteDive Similar Items']
			listitems += ['In Trakt Lists']
			listitems += ['Googles Similar Items']
			if xbmcaddon.Addon(addon_ID()).getSetting('RD_bluray_player') == 'true' or xbmcaddon.Addon(addon_ID()).getSetting('RD_bluray_player2')  == 'true':
				listitems += ['Eject/Load DVD']

			if item_id in str(last_played_tmdb_helper):
				listitems += ['Last Played URL']

			try:
				bluray_cmd = None
				if self_type == 'movie' and 'Collection' in str(self.filter_label):
					import os
					addon = xbmcaddon.Addon()
					addon_path = addon.getAddonInfo('path')
					addonID = addon.getAddonInfo('id')
					addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
					if os.path.exists(str(Path(addonUserDataFolder + '/custom_for_me'))):
						bluray_cmd = 'plugin://service.next_playlist/play_bluray?title='+str(self.listitem.getProperty('Title'))+'&amp;year='+str(self.listitem.getProperty('year'))+'&amp;tmdb='+str(item_id)
						listitems += ['Play Bluray']
			except:
					pass



			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			selection_text = listitems[selection]
			if selection == -1:
				return

			xbmcgui.Window(10000).setProperty('tmdbhelper_tvshow.poster', str(self.listitem.getProperty('poster')))
			if selection_text == 'Last Played URL':
				xbmc.executebuiltin('Dialog.Close(busydialog)')
				xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.play_from_button(last_played_tmdb_helper, listitem=None, window=self, dbid=0)
			if selection_text == 'Play first episode' or selection_text == 'Play':
				if (self.search_str == 'Trakt Episodes/Movies in progress' or self.search_str == 'Trakt Calendar Episodes')and xbmc.getInfoLabel('listitem.DBTYPE') == 'episode':
					item_id = self.listitem.getProperty('tmdb_id')
					episode = str(xbmc.getInfoLabel('listitem.Episode'))
					season = str(xbmc.getInfoLabel('listitem.Season'))
					if season.lower() == 'none' or season == None or season == '':
						season = 0
					url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=%s&amp;episode=%s' % (item_id, season, episode)
					xbmc.log(str(url)+'===>PHIL', level=xbmc.LOGINFO)
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					xbmc.executebuiltin('Dialog.Close(all,true)')
					PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
				elif self.listitem.getProperty('TVShowTitle'):
					url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % item_id
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					xbmc.executebuiltin('Dialog.Close(all,true)')
					PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
				else:
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					if self.listitem.getProperty('dbid'):
						dbid = self.listitem.getProperty('dbid')
						url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=movie&amp;tmdb_id=%s' % item_id
						xbmc.executebuiltin('Dialog.Close(all,true)')
						PLAYER.play_from_button(url, listitem=None, window=self, type='movieid', dbid=dbid)
					else:
						dbid = 0
						url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=movie&amp;tmdb_id=%s' % item_id
						xbmc.executebuiltin('Dialog.Close(all,true)')
						PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
			if selection_text == 'Trakt remove playback entry':
				DBTYPE = xbmc.getInfoLabel('listitem.DBTYPE')
				#xbmc.log(str(self.search_str)+'query_get_tastedive_data_scrape===>OPENINFO', level=xbmc.LOGINFO)
				if DBTYPE == 'episode':
					response = get_trakt_playback('tv')
					item_id = self.listitem.getProperty('tmdb_id')
					#try: item_id = self.listitem.getProperty('tmdb_id')
					#except: item_id = self.listitems[self.position].getProperty('tmdb_id')
					episode = str(xbmc.getInfoLabel('listitem.Episode'))
					season = str(xbmc.getInfoLabel('listitem.Season'))
				else:
					response = get_trakt_playback('movie')
					item_id = self.listitem.getProperty('id')
				for i in response:
					if DBTYPE == 'episode':
						if str(i['show']['ids']['tmdb']) == str(item_id):
							if str(i['episode']['number']) == str(episode) and str(i['episode']['season']) == str(season):
								play_id = i['id']
					else:
						if str(i['movie']['ids']['tmdb']) == str(item_id):
							play_id = i['id']
				url = 'https://api.trakt.tv/sync/playback/' + str(play_id)
				response = requests.delete(url, headers=trak_auth())
				try: xbmc.log(str(response.json)+'Trakt remove playback entry===>OPENINFO', level=xbmc.LOGINFO)
				except: xbmc.log(str(response)+'Trakt remove playback entry===>OPENINFO', level=xbmc.LOGINFO)
				self.fetch_data()
				self.update()

			if selection_text == 'Remove from library' or selection_text == 'Add to library':
				if self.listitem.getProperty('TVShowTitle'):
					TVLibrary = basedir_tv_path()
					if self.listitem.getProperty('dbid'):
						Utils.get_kodi_json(method='VideoLibrary.RemoveTVShow', params='{"tvshowid": %s}' % dbid)
						if os.path.exists(xbmcvfs.translatePath('%s/%s/' % (TVLibrary, tvdb_id))):
							shutil.rmtree(xbmcvfs.translatePath('%s/%s/' % (TVLibrary, tvdb_id)))
							
							trakt_add_tv(item_id,'Remove')
							Utils.after_add(type='tv')
							Utils.notify(header='[B]%s[/B]' % self.listitem.getProperty('TVShowTitle'), message='Removed from library', icon=self.listitem.getProperty('poster'), time=1000, sound=False)
							xbmc.sleep(250)
							self.update(force_update=True)
							self.getControl(500).selectItem(self.position)
					else:
						if xbmcgui.Dialog().yesno(str(addon_ID()), 'Add [B]%s[/B] to library?' % self.listitem.getProperty('TVShowTitle')):
							trakt_add_tv(item_id,'Add')
							Utils.after_add(type='tv')
							Utils.notify(header='[B]%s[/B] added to library' % self.listitem.getProperty('TVShowTitle'), message='Exit & re-enter to refresh', icon=self.listitem.getProperty('poster'), time=1000, sound=False)
				else:
					if self.listitem.getProperty('dbid'):
						if xbmcgui.Dialog().yesno(str(addon_ID()), 'Remove [B]%s[/B] from library?' % self.listitem.getProperty('title')):
							Utils.get_kodi_json(method='VideoLibrary.RemoveMovie', params='{"movieid": %s}' % dbid)
							MovieLibrary = basedir_movies_path()
							if os.path.exists(xbmcvfs.translatePath('%s/%s/' % (MovieLibrary, item_id))):
								shutil.rmtree(xbmcvfs.translatePath('%s/%s/' % (MovieLibrary, item_id)))
								
								trakt_add_movie(item_id,'Remove')
								Utils.after_add(type='movie')
								Utils.notify(header='[B]%s[/B]' % self.listitem.getProperty('title'), message='Removed from library', icon=self.listitem.getProperty('poster'), time=1000, sound=False)
								xbmc.sleep(250)
								self.update(force_update=True)
								self.getControl(500).selectItem(self.position)
					else:
						if xbmcgui.Dialog().yesno(str(addon_ID()), 'Add [B]%s[/B] to library?' % self.listitem.getProperty('title')):
							trakt_add_movie(item_id,'Add')
							Utils.after_add(type='movie')
							Utils.notify(header='[B]%s[/B] added to library' % self.listitem.getProperty('title'), message='Exit & re-enter to refresh', icon=self.listitem.getProperty('poster'), time=1000, sound=False)
			if selection_text == 'Play Kodi Next Episode':
				url = next_episode_show(tmdb_id_num=item_id,dbid_num=dbid)
				xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)

			if selection_text == 'Play Trakt Next Episode':
				url = trakt_next_episode_normal(tmdb_id_num=item_id)
				xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)

			if selection_text == 'Play Trakt Next Episode (Rewatch)':
				url = trakt_next_episode_rewatch(tmdb_id_num=item_id)
				xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)

			if selection_text == 'Search item':
				
				#xbmc.log(str(self.listitems[self.position].getProperty('TVShowTitle'))+'Search===>OPENINFO', level=xbmc.LOGINFO)
				#xbmc.log(str(self.listitems[self.position].getProperty('Title'))+'Search===>OPENINFO', level=xbmc.LOGINFO)
				
				item_title = self.listitem.getProperty('TVShowTitle') or self.listitem.getProperty('Title')
				self.close()
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=search_string,str=%s)' % item_title)

			if selection_text == 'Trailer':
				from resources.lib import YouTube
				item_title = self.listitem.getProperty('TVShowTitle') or self.listitem.getProperty('Title')
				search_str = item_title + ' Trailer'
				results = YouTube.search_youtube(search_str, limit = 1)
				try: youtube_id = results['listitems'][0]['youtube_id']
				except: youtube_id = None
				#xbmc.log(str(results)+'===>OPENINFO', level=xbmc.LOGINFO)
				#PLAYER.playtube(results['listitem'][0]['youtube_id']), listitem=results['listitem'][0], window=self)
				if self.listitem.getProperty('TVShowTitle') or self_type == 'tv':
					url = 'plugin://'+str(addon_ID())+'?info=playtvtrailer&&id=' + str(item_id)
				else:
					url = 'plugin://'+str(addon_ID())+'?info=playtrailer&&id=' + str(item_id)
				#PLAYER.play(url, listitem=None, window=self)
				if youtube_id:
					PLAYER.playtube(results['listitems'][0]['youtube_id'], listitem=None, window=self)
				else:
					PLAYER.play(url, listitem=None, window=self)
			if selection_text == 'TMDBHelper Context':
				if self_type == 'tv':
					xbmc.executebuiltin('RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type=tv,tmdb_id='+str(item_id))
				else:
					xbmc.executebuiltin('RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type=movie,tmdb_id='+str(item_id))
			if selection_text == 'Play Bluray':
				if bluray_cmd:
					#xbmc.executebuiltin('RunPlugin(%s)' % (bluray_cmd))
					url = bluray_cmd
					xbmc.executebuiltin('Dialog.Close(all,true)')
					PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)

			if selection_text == 'Eject/Load DVD':
				xbmc.executebuiltin('RunScript(%s,info=eject_load_dvd)' % (addon_ID()))

			if selection_text == 'Googles Similar Items':
				search_str = self.listitem.getProperty('title')
				search_year = self.listitem.getProperty('year')
				from resources.lib.TheMovieDB import google_similar
				wm.pop_video_list = False
				self.page = 1
				self.mode='google_similar'
				Utils.show_busy()
				self.search_str = google_similar(search_str=search_str, search_year=search_year)
				self.filter_label='Googles Similar ('+str(search_str)+'):'

				self.fetch_data()
				wm.page = -1
				self.update()
				#self.update_content(force_update=False)
				Utils.hide_busy()

			if selection_text == 'TasteDive Similar Items':
				search_str = self.listitem.getProperty('title')
				wm.pop_video_list = False
				limit = 100
				if xbmc.getInfoLabel('listitem.DBTYPE') == 'movie':
					self_type = 'movie'
				elif xbmc.getInfoLabel('listitem.DBTYPE') in ['tv', 'tvshow', 'season', 'episode']:
					self_type = 'tv'
				if self_type == 'tv':
					media_type = 'tv'
				else:
					media_type = 'movie'
				self.page = 1
				self.mode='tastedive&' + str(media_type)
				#self.search_str = TheMovieDB.get_tastedive_data(query=search_str, limit=limit, media_type=media_type)
				Utils.show_busy()
				self.search_str = TheMovieDB.get_tastedive_data_scrape(query=search_str, year=self.listitem.getProperty('year'), limit=limit, media_type=media_type,item_id=item_id)
				if self.search_str == []:
					if media_type == 'movie':
						single_movie_info = TheMovieDB.single_movie_info(movie_id=item_id)
						alternative_titles = []
						for i in single_movie_info['alternative_titles']['titles']:
							if str(i['iso_3166_1']) in ['US','UK','GB']:
								alternative_titles.append(i['title'])
					else:
						single_tvshow_info = TheMovieDB.single_tvshow_info(tvshow_id=item_id)
						alternative_titles = single_tvshow_info['alternative_titles']
					for i in alternative_titles:
						#self.search_str = TheMovieDB.get_tastedive_data(query=self.listitem.getProperty('originaltitle'), limit=limit, media_type=media_type)
						self.search_str = TheMovieDB.get_tastedive_data_scrape(query=i, year=self.listitem.getProperty('year'), limit=limit, media_type=media_type,item_id=item_id)
						#xbmc.log(str(self.search_str)+'query_get_tastedive_data_scrape===>OPENINFO', level=xbmc.LOGINFO)
						if self.search_str != []:
							break
				self.filter_label='TasteDive Similar ('+str(search_str)+'):'
				#return wm.open_video_list(mode='tastedive&' + str(media_type), listitems=[], search_str=response, filter_label='TasteDive Similar ('+str(search_str)+'):')
				#self.fetch_data()
				#self.update()
				xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
				self.fetch_data()
				wm.page = -1
				self.update()
				#self.update_content(force_update=False)
				Utils.hide_busy()
			if selection_text == 'In Trakt Lists':
				from resources.lib.library import trakt_in_lists
				search_str = self.listitem.getProperty('title')
				Utils.show_busy()
				if xbmc.getInfoLabel('listitem.DBTYPE') == 'movie':
					self_type = 'movie'
				elif xbmc.getInfoLabel('listitem.DBTYPE') in ['tv', 'tvshow', 'season', 'episode']:
					self_type = 'tv'
				if self_type == 'tv':
					media_type = 'tv'
					imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'imdb_id')
				else:
					media_type = 'movie'
					imdb_id = TheMovieDB.get_imdb_id_from_movie_id(item_id)
				self.search_str = trakt_in_lists(type=media_type,imdb_id=imdb_id)
				if self.search_str == None or self.search_str == []:
					Utils.hide_busy()
					return
				wm.pop_video_list = False
				self.page = 1
				self.mode = 'trakt'
				self.filter_label='Trakt In Lists ('+str(search_str)+'):'
				xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
				self.fetch_data()
				wm.page = -1
				self.update()
				#self.update_content(force_update=False)
				Utils.hide_busy()

		@ch.click(5002)
		def get_sort_type(self):
			if self.mode in ['list']:
				sort_key = self.mode
			else:
				sort_key = self.type
			listitems = [key for key in list(SORTS[sort_key].values())]
			sort_strings = [value for value in list(SORTS[sort_key].keys())]
			index = xbmcgui.Dialog().select(heading='Sort by', list=listitems)

			if index == -1:
				return None
			if sort_strings[index] == 'vote_average':
				self.add_filter('vote_count.gte', '10', '%s (%s)' % ('Vote count', 'greater than'), '10')
			self.sort = sort_strings[index]
			self.sort_label = listitems[index]
			self.update()

		def add_filter(self, key, value, typelabel, label):
			if '.gte' in key or '.lte' in key:
				super(DialogVideoList, self).add_filter(key=key, value=value, typelabel=typelabel, label=label, force_overwrite=True)
			else:
				super(DialogVideoList, self).add_filter(key=key, value=value, typelabel=typelabel, label=label, force_overwrite=False)

		@ch.click(5003)
		def toggle_order(self):
			self.order = 'desc' if self.order == 'asc' else 'asc'
			self.update()

		@ch.click(5001)
		def toggle_media_type(self):
			self.filters = []
			self.page = 1
			self.mode = 'filter'
			self.type = 'movie' if self.type == 'tv' else 'tv'
			wm.page = -1
			if (self.search_str == 'Trakt Episodes/Movies in progress' or self.search_str == 'Trakt Calendar Episodes'):
				self.search_str = ''
			#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			self.update()

		@ch.click(5007)
		def set_genre_filter(self):
			response = TheMovieDB.get_tmdb_data('genre/%s/list?language=%s&' % (self.type, xbmcaddon.Addon().getSetting('LanguageID')), 10)
			"""
			id_list = [item['id'] for item in response['genres']]
			label_list = [item['name'] for item in response['genres']]
			index = xbmcgui.Dialog().select(heading='Choose genre', list=label_list)
			if index == -1:
				return None
			self.add_filter('with_genres', str(id_list[index]), 'Genres', label_list[index])
			self.mode = 'filter'
			self.page = 1
			self.update()
			
			params = {"language": addon.setting("LanguageID")}
			response = tmdb.get_data(url="genre/%s/list" % (self.type),
									 params=params,
									 cache_days=100)
			"""
			selected = [i["id"] for i in self.filters if i["type"] == "with_genres"]
			ids = [item["id"] for item in response["genres"]]
			labels = [item["name"] for item in response["genres"]]
			preselect = [ids.index(int(i)) for i in str(selected[0]).split(",")] if selected else []

			try: without_genres = 'NOT Genres: ' + str([i["label"] for i in self.filters if i["type"] == "without_genres"][0]).replace(',','+').replace('|',' OR ')
			except: without_genres = ''
			try: with_genres = 'Genres: ' + str([i["label"] for i in self.filters if i["type"] == "with_genres"][0]).replace(',','+').replace('|',' OR ') + ' '
			except: with_genres = ''
			filter_label = with_genres + without_genres
			
			indexes = xbmcgui.Dialog().multiselect(heading='Choose genre: ' + filter_label,options=labels,preselect=preselect)
			if indexes == -1:
				return

			try: selected_indexes = [labels[i] for i in indexes]
			except: return
			preselect_indexes = [labels[i] for i in  [ids.index(int(j)) for j in [ids[i] for i in preselect]]]
			selected_indexes2 = str([i for i in selected_indexes if i not in preselect_indexes]).replace('[','').replace(']','')
			#xbmc.log(str([i["label"] for i in self.filters if i["type"] == "without_genres"])+'without_genres===>OPENINFO', level=xbmc.LOGFATAL)
			#xbmc.log(str([i["label"] for i in self.filters if i["type"] == "with_genres"])+'with_genres===>OPENINFO', level=xbmc.LOGFATAL)

			if indexes is None:
				return None
			indexes2 = xbmcgui.Dialog().yesno('Genres', 'Set with/without genres for newly selected items' + ' ' + selected_indexes2, 'With Genres', 'Without Genres', 3500) 
			if indexes2 == -1:
				return
			indexes3 = str(indexes2)

			#xbmc.log(str([i["label"] for i in self.filters if i["type"] == "without_genres"])+'without_genres===>OPENINFO', level=xbmc.LOGFATAL)
			#xbmc.log(str([i["label"] for i in self.filters if i["type"] == "with_genres"])+'with_genres===>OPENINFO', level=xbmc.LOGFATAL)

			self.filters = [i for i in self.filters if i["type"] != "with_genres"]
			for i in indexes:
				if indexes2 == False:
					self.add_filter('with_genres', ids[i], 'Genres', labels[i])
				else:
					if str(i) in str(preselect):
						self.add_filter('with_genres', ids[i], 'Genres', labels[i])
					else:
						self.add_filter('without_genres', ids[i], 'NOT Genres', labels[i])
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(5013)
		def set_vote_count_filter(self):
			ret = True
			if not self.type == 'tv':
				ret = xbmcgui.Dialog().yesno(heading='Choose option', message='Choose filter behaviour', nolabel='Lower limit', yeslabel='Upper limit')
			result = xbmcgui.Dialog().input(heading='Vote count', type=xbmcgui.INPUT_NUMERIC)
			if result:
				if ret:
					self.add_filter('vote_count.lte', result, 'Vote count', ' < %s' % result)
				else:
					self.add_filter('vote_count.gte', result, 'Vote count', ' > %s' % result)
				self.mode = 'filter'
				self.page = 1
				self.update()

		@ch.click(5008)
		def set_year_filter(self):
			ret = xbmcgui.Dialog().yesno(heading='Choose option', message='Choose filter behaviour', nolabel='Lower limit', yeslabel='Upper limit')
			result = xbmcgui.Dialog().input(heading='Year', type=xbmcgui.INPUT_NUMERIC)
			if not result:
				return None
			if ret:
				order = 'lte'
				value = '%s-12-31' % result
				label = ' < ' + result
			else:
				order = 'gte'
				value = '%s-01-01' % result
				label = ' > ' + result
			if self.type == 'tv':
				self.add_filter('first_air_date.%s' % order, value, 'First aired', label)
			else:
				self.add_filter('primary_release_date.%s' % order, value, 'Year', label)
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(5010)
		def set_actor_filter(self):
			result = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
			if not result or result == -1:
				return None
			response = TheMovieDB.get_person_info(result)
			if not response:
				return None
			self.add_filter('with_people', str(response['id']), 'Person', response['name'])
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(500)
		def open_media(self):
			Utils.show_busy()
			self.last_position = self.control.getSelectedPosition()
			media_type = self.listitem.getProperty('media_type')
			if media_type == 'tvshow':
				media_type = 'tv'
			if 'movie' in str(media_type):
				media_type = 'movie'
			if media_type:
				self.type = media_type
			else:
				self.type = self.media_type
			if self.type == 'tv':
				if str(self.listitem.getProperty('id')) == '':
					response = TheMovieDB.get_tmdb_data('search/%s?query=%s&first_air_date_year=%s&language=%s&include_adult=%s&' % ('tv', str(self.listitem.getProperty('title')), str(self.listitem.getProperty('year')) , str(xbmcaddon.Addon().getSetting('LanguageID')) , xbmcaddon.Addon().getSetting('include_adults')), 30)
					tmdb_id = response['results'][0]['id']
					wm.open_tvshow_info(prev_window=self, tmdb_id=tmdb_id, dbid=self.listitem.getProperty('dbid'))
				else:
					wm.open_tvshow_info(prev_window=self, tmdb_id=self.listitem.getProperty('id'), dbid=self.listitem.getProperty('dbid'))
			elif self.type == 'person':
				wm.open_actor_info(prev_window=self, actor_id=self.listitem.getProperty('id'))
			else:
				if str(self.listitem.getProperty('id')) == '':
					response = TheMovieDB.get_tmdb_data('search/%s?query=%s&primary_release_year=%s&language=%s&include_adult=%s&' % ('movie', str(self.listitem.getProperty('title')), str(self.listitem.getProperty('year')) , str(xbmcaddon.Addon().getSetting('LanguageID')) , xbmcaddon.Addon().getSetting('include_adults')), 30)
					tmdb_id = response['results'][0]['id']
					wm.open_movie_info(prev_window=self, movie_id=tmdb_id, dbid=self.listitem.getProperty('dbid'))
				else:
					wm.open_movie_info(prev_window=self, movie_id=self.listitem.getProperty('id'), dbid=self.listitem.getProperty('dbid'))

		@ch.click(5012)
		def set_company_filter(self):
			result = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
			if not result or len(result) < 1:
				return None
			response = TheMovieDB.search_company(result)
			if len(response) > 1:
				selection = xbmcgui.Dialog().select(heading='Choose studio', list=[item['name'] for item in response])
				if selection > -1:
					response = response[selection]
			elif response:
				response = response[0]
			else:
				Utils.notify('No company found')
			self.add_filter('with_companies', str(response['id']), 'Studios', response['name'])
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(5011)
		def set_keyword_filter(self):
			result = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
			if not result or result == -1:
				return None
			response = TheMovieDB.get_keyword_id(result)
			if not response:
				return None
			self.add_filter('with_keywords', str(response['id']), 'Keyword', response['name'])
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(5009)
		def set_certification_filter(self):
			response = TheMovieDB.get_certification_list(self.type)
			country_list = [key for key in list(response.keys())]
			index = xbmcgui.Dialog().select(heading='Country code', list=country_list)
			if index == -1:
				return None
			country = country_list[index]
			cert_list = ['%s  -  %s' % (i['certification'], i['meaning']) for i in response[country]]
			index = xbmcgui.Dialog().select(heading='Choose certification', list=cert_list)

			if index == -1:
				return None
			cert = cert_list[index].split('  -  ')[0]
			self.add_filter('certification_country', country, 'Certification country', country)
			self.add_filter('certification', cert, 'Certification', cert)
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(5006)
		def set_page_number(self):
			page = xbmcgui.Dialog().input(heading='Page Number', type=xbmcgui.INPUT_NUMERIC)#
			try: self.page = int(page)
			except: return
			self.update()

		@ch.click(5005)
		def set_language_filter(self):
			list = sorted(LANGUAGES, key=lambda k: k['name'])
			ids = [i['id'] for i in list]
			names = [i['name'] for i in list]
			index = xbmcgui.Dialog().select(heading='Choose language', list=names)

			if index == -1:
				return None
			id = ids[index]
			name = names[index]
			if 'with_original_language' in [i['type'] for i in self.filters]:
				self.filters = []
			self.add_filter('with_original_language', id, 'Original language', name)
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(5014)
		def get_IMDB_Lists(self):
			self.page = 1
			file_path = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('path'))
			imdb_json = xbmcaddon.Addon(addon_ID()).getSetting('imdb_json')
			custom_imdb_json = xbmcaddon.Addon(addon_ID()).getSetting('custom_imdb_json')
			#https://raw.githubusercontent.com/henryjfry/repository.thenewdiamond/main/imdb_list.json
			if not '://' in str(imdb_json):
				json_file = open(imdb_json)
				data = json.load(json_file)
				json_file.close()
			elif str(imdb_json) != '' and custom_imdb_json == 'true':
				data = requests.get(imdb_json).json()
			else:
				imdb_json = file_path + 'imdb_list.json'
				json_file = open(imdb_json)
				data = json.load(json_file)
				json_file.close()

			listitems = []
			imdb_list = []
			imdb_list_name = []
			for i in data['imdb_list']:
				list_name = (i[str(list(i)).replace('[\'','').replace('\']','')])
				list_number = (str(list(i)).replace('[\'','').replace('\']',''))
				imdb_list.append(list_number)
				imdb_list_name.append(list_name)
				listitems += [list_name]
			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if selection == -1:
				return
			self.mode = 'imdb'
			Utils.show_busy()
			if 'ls' in str(imdb_list[selection]):
				from resources.lib.TheMovieDB import get_imdb_list_ids
				self.search_str = get_imdb_list_ids(list_str=imdb_list[selection],limit=0)
				self.mode = 'imdb2'

			elif 'ur' in str(imdb_list[selection]):
				from resources.lib.TheMovieDB import get_imdb_watchlist_ids
				self.search_str = get_imdb_watchlist_ids(imdb_list[selection])
				self.mode = 'imdb2'

			self.filter_label = 'Results for:  ' + imdb_list_name[selection]
			self.fetch_data()
			self.update()

		def reload_trakt(self):
			if 'Trakt Watched Movies' in str(self.filter_label):
				self.search_str = trakt_watched_movies()
			if 'Trakt Watched Shows' in str(self.filter_label):
				xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>PHIL', level=xbmc.LOGINFO)
				self.search_str = trakt_watched_tv_shows()
			if 'Trakt Unwatched Shows' in str(self.filter_label):
				self.search_str = trakt_unwatched_tv_shows()
			else:
				return
			self.fetch_data()
			self.update()


		@ch.click(5015)
		def get_trakt_stuff(self):
			self.page = 1
			#https://raw.githubusercontent.com/henryjfry/repository.thenewdiamond/main/trakt_list.json
			trakt_json = xbmcaddon.Addon(addon_ID()).getSetting('trakt_json')
			custom_trakt_json = xbmcaddon.Addon(addon_ID()).getSetting('custom_trakt_json')
			if not '://' in trakt_json:
				json_file = open(trakt_json)
				trakt_data = json.load(json_file)
				json_file.close()
			elif str(trakt_json) != '' and custom_trakt_json == 'true':
				try: trakt_data = requests.get(trakt_json).json()
				except:
					from resources.lib.library import main_file_path
					trakt_json = main_file_path() + 'trakt_list.json'
					json_file = open(trakt_json)
					trakt_data = json.load(json_file)
					json_file.close()
			else:
				trakt_json = file_path + 'trakt_list.json'
				json_file = open(trakt_json)
				trakt_data = json.load(json_file)
				json_file.close()

			listitems = []
			listitems = ['Trakt Watched Shows']
			listitems += ['Trakt Episodes/Movies in progress']
			listitems += ['Trakt Calendar Episodes']
			listitems += ['TasteDive - Last Watched TV']
			listitems += ['Trakt Shows Progress']
			listitems += ['Trakt Unwatched Shows']
			listitems += ['Trakt Watched Movies']
			listitems += ['TasteDive - Last Watched Movies']
			listitems += ['Trakt Collection Shows']
			listitems += ['Trakt Collection Movies']
			listitems += ['Trakt Unwatched Collection Movies']
			listitems += ['Trakt Uncollected Watched Movies']
			listitems += ['Trakt Trending Shows']
			listitems += ['Trakt Trending Movies']
			listitems += ['Trakt Popular Shows']
			listitems += ['Trakt Popular Movies']

			for i in trakt_data['trakt_list']:
				if str(i['name']) != '':
					listitems += [i['name']]



			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)

			if selection == -1:
				return
			self.mode = 'trakt'
			Utils.show_busy()
			if selection == -1:
				Utils.hide_busy()
				return
			try: trakt_token = xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('trakt_token')
			except: trakt_token = None
			if not trakt_token:
				Utils.hide_busy()
				return

			if listitems[selection] == 'Trakt Watched Movies':
				self.search_str = trakt_watched_movies()
				self.type = 'movie'

			elif listitems[selection] == 'Trakt Uncollected Watched Movies':
				self.search_str = trakt_uncollected_watched_movies()
				self.type = 'movie'
			elif listitems[selection] == 'Trakt Unwatched Collection Movies':
				self.search_str = trakt_unwatched_collection_movies()
				self.type = 'movie'

			elif listitems[selection] == 'Trakt Watched Shows':
				xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>PHIL', level=xbmc.LOGINFO)
				self.search_str = trakt_watched_tv_shows()
				self.type = 'tv'
			elif listitems[selection] == 'Trakt Unwatched Shows':
				self.search_str = trakt_unwatched_tv_shows()
				self.type = 'tv'
			elif listitems[selection] == 'Trakt Collection Movies':
				self.search_str = trakt_collection_movies()
				self.type = 'movie'
			elif listitems[selection] == 'Trakt Collection Shows':
				self.search_str = trakt_collection_shows()
				self.type = 'tv'
			elif listitems[selection] == 'Trakt Trending Shows':
				self.search_str = trakt_trending_shows()
				self.type = 'tv'
			elif listitems[selection] == 'Trakt Trending Movies':
				self.search_str = trakt_trending_movies()
				self.type = 'tv'
			elif listitems[selection] == 'Trakt Popular Shows':
				self.search_str = trakt_popular_shows()
				self.type = 'tv'
			elif listitems[selection] == 'Trakt Popular Movies':
				self.search_str = trakt_popular_movies()
				self.type = 'tv'
			elif listitems[selection] == 'Trakt Shows Progress':
				xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>PHIL', level=xbmc.LOGINFO)
				self.search_str = trakt_watched_tv_shows_progress()
				self.type = 'tv'
			elif listitems[selection] == 'Trakt Episodes/Movies in progress':
				self.search_str = 'Trakt Episodes/Movies in progress'
				self.type = 'movie'
			elif listitems[selection] == 'Trakt Calendar Episodes':
				self.search_str = 'Trakt Calendar Episodes'
				self.type = 'movie'


			elif listitems[selection] == 'TasteDive - Last Watched Movies':
				from resources.lib import TheMovieDB
				response = TheMovieDB.get_trakt(trakt_type='movie',info='trakt_watched',limit=100)
				response3 = []
				for i in response:
					#xbmc.log(str(i)+'query_get_tastedive_data_scrape===>OPENINFO', level=xbmc.LOGINFO)
					#response2 = TheMovieDB.get_tastedive_data(query=i['title'], limit=50, media_type='movie')

					try: release_date = i['release_date'][:4]
					except: 
						continue

					#release_date = i['release_date'][:4]
					#single_movie_info = TheMovieDB.single_movie_info(movie_id=i['id'])
					#alternative_titles = []
					#for xi in single_movie_info['alternative_titles']['titles']:
					#	if str(xi['iso_3166_1']) in ['US','UK','GB']:
					#		alternative_titles.append(xi['title'])

					response2 = []
					response2 = TheMovieDB.get_tastedive_data_scrape(query=i['title'], year=i['release_date'][:4], limit=50, media_type='movie',item_id=i['id'])

					#if response2 == []:
					#	for xi in alternative_titles:
					#		response2 = TheMovieDB.get_tastedive_data_scrape(query=xi, year=release_date, limit=50, media_type='movie',item_id=i['id'])
					#		if response2 != []:
					#			break

					"""
					response2 = TheMovieDB.get_tastedive_data_scrape(query=i['title'], year=i['release_date'][:4], limit=50, media_type='movie')
					original_title = i['original_title']
					original_title2 = ''
					try:
						for ix in i['alternative_titles']['titles']:
							if ix['type'] == 'original title' and ix['iso_3166_1'] in {'US','UK'}:
								original_title2 = ix['title']
						if original_title2 != original_title and original_title2 != '':
							original_title = original_title2
					except:
						pass
					if response2 == [] and original_title != i['title']:
						#response2 = TheMovieDB.get_tastedive_data(query=original_title, limit=50, media_type='movie')
						response2 = TheMovieDB.get_tastedive_data_scrape(query=i['title'], year=i['release_date'][:4], limit=50, media_type='movie')
					"""

					curr_item = {'name': i['title'], 'year': int(release_date), 'media_type': i['media_type'], 'item_id': int(i['id'])}
					if not curr_item in response3:
						#xbmc.log(str(curr_item)+'===>OPENINFO', level=xbmc.LOGINFO)
						response3.append(curr_item)
					for x in response2:
						curr_item = {'name': x['name'], 'year': int(x['year']), 'media_type': x['media_type'], 'item_id': int(x['item_id'])}
						if not curr_item in response3:
							#xbmc.log(str(x)+'===>OPENINFO', level=xbmc.LOGINFO)
							response3.append(curr_item)
					"""
					#if not {'name': i['title'], 'year': release_date, 'media_type': i['media_type'], 'item_id': i['id']} in response3:
					if not str("'item_id': %s" % (i['id'])) in str(response3):
						response3.append({'name': i['title'], 'year': release_date, 'media_type': i['media_type'], 'item_id': i['id']})
					for x in response2:
						#if not x in response3:
						if not str("'item_id': %s" % (x['item_id'])) in str(response3):
							response3.append(x)
					"""

				#xbmc.log(str(str(response3)+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
				item_list = []
				response2 = []
				for i in response3:
					if not i['item_id'] in item_list:
						item_list.append(i['item_id'])
						response2.append(i)
				self.mode = mode='tastedive&' + str('movie')
				self.type = 'movie'
				self.search_str = response2
				self.filter_label='TasteDive Based on Recently Watched Movies:'
				self.fetch_data()
				#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
				self.update()
				Utils.hide_busy()
				return

			elif listitems[selection] == 'TasteDive - Last Watched TV':
				from resources.lib import TheMovieDB
				response = TheMovieDB.get_trakt(trakt_type='tv',info='trakt_watched',limit=100)
				response3 = []
				for i in response:
					#response2 = TheMovieDB.get_tastedive_data(query=i['name'], limit=50, media_type='tv')
					response2 = TheMovieDB.get_tastedive_data_scrape(query=i['name'], year=i['first_air_date'][:4], limit=50, media_type='tv',item_id=i['id'])
					for x in response2:
						#if x not in response3:
						if not str("'item_id': %s" % (x['item_id'])) in str(response3):
							response3.append(x)

				item_list = []
				response2 = []
				for i in response3:
					if not i['item_id'] in item_list:
						item_list.append(i['item_id'])
						response2.append(i)

				self.mode = mode='tastedive&' + str('tv')
				self.type = 'tv'
				self.search_str = response2
				self.filter_label='TasteDive Based on Recently Watched TV:'
				self.fetch_data()
				#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
				self.update()
				Utils.hide_busy()
				return

			else:
				for i in trakt_data['trakt_list']:
					if i['name'] == listitems[selection]:
						self.type = 'movie'
						trakt_type = 'movie'
						trakt_list_name = str(i['name'])
						trakt_user_id = str(i['user_id'])
						takt_list_slug = str(i['list_slug'])
						trakt_sort_by = str(i['sort_by'])
						trakt_sort_order = str(i['sort_order'])
						self.search_str = trakt_lists(list_name=trakt_list_name,user_id=trakt_user_id,list_slug=takt_list_slug,sort_by=trakt_sort_by,sort_order=trakt_sort_order)
			self.filter_label = 'Results for:  ' + listitems[selection]
			self.fetch_data()
			self.update()
			Utils.hide_busy()

		@ch.click(5016)
		def get_user_lists(self):
			old_page = self.page
			self.page = 1
			listitems = []
			trakt_data = TheMovieDB.get_trakt_userlists()
			#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			if trakt_data:
				for i in trakt_data['trakt_list']:
					if str(i['name']) != '':
						listitems += [i['name']]

			#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			data = TheMovieDB.get_imdb_userlists()
			imdb_list = []
			imdb_list_name = []
			if data:
				for i in data['imdb_list']:
					list_name = (i[str(list(i)).replace('[\'','').replace('\']','')])
					list_number = (str(list(i)).replace('[\'','').replace('\']',''))
					imdb_list.append(list_number)
					imdb_list_name.append(list_name)
					listitems += [list_name]

			if listitems == []:
				return

			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)

			if selection == -1:
				return

			Utils.show_busy()
			y = 0
			for i in trakt_data['trakt_list']:
				if i['name'] == listitems[selection] and y == selection:
					trakt_type = 'movie'
					trakt_list_name = str(i['name'])
					trakt_user_id = str(i['user_id'])
					takt_list_slug = str(i['list_slug'])
					trakt_sort_by = str(i['sort_by'])
					trakt_sort_order = str(i['sort_order'])
					trakt_search_str = trakt_lists(list_name=trakt_list_name,user_id=trakt_user_id,list_slug=takt_list_slug,sort_by=trakt_sort_by,sort_order=trakt_sort_order)
					if not trakt_search_str:
						self.page = old_page
						Utils.hide_busy()
						return
					self.search_str = trakt_search_str
					self.mode = 'trakt'
					self.type = 'movie'

					
				y = y + 1
			x = 0
			for i in imdb_list_name:
				if i == listitems[selection]:
					list_number = imdb_list[x]
					self.mode = 'imdb'
				x = x + 1

			if self.mode == 'imdb' and 'ls' in str(list_number):
				from resources.lib.TheMovieDB import get_imdb_list_ids
				self.search_str = get_imdb_list_ids(list_str=list_number,limit=0)
				self.mode = 'imdb2'

			elif self.mode == 'imdb' and 'ur' in str(list_number):
				from resources.lib.TheMovieDB import get_imdb_watchlist_ids
				self.search_str = get_imdb_watchlist_ids(list_number)
				self.mode = 'imdb2'

			self.filter_label = 'Results for:  ' + listitems[selection]
			self.fetch_data()
			self.update()
			Utils.hide_busy()

		@ch.click(5017)
		def get_custom_routes(self):
			self.page = 1
			items = [
				('libraryallmovies', 'My Movies (Library)'),
				('libraryalltvshows', 'My TV Shows (Library)'),
				('popularmovies', 'Popular Movies'),
				('topratedmovies', 'Top Rated Movies'),
				('incinemamovies', 'In Theaters Movies'),
				('upcomingmovies', 'Upcoming Movies'),
				('populartvshows', 'Popular TV Shows'),
				('topratedtvshows', 'Top Rated TV Shows'),
				('onairtvshows', 'Currently Airing TV Shows'),
				('airingtodaytvshows', 'Airing Today TV Shows')
				]
			listitems = []
			listitems_key = []
			for key, value in items:
				listitems.append(value)
				listitems_key.append(key)

			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)

			Utils.show_busy()
			if selection == -1:
				Utils.hide_busy()
				return
			self.mode='list_items'
			info = listitems_key[selection]
			self.filter_label = listitems[selection]
			if info == 'libraryallmovies':
				from resources.lib import local_db
				self.media_type = 'movie'
				self.search_str = local_db.get_db_movies('"sort": {"order": "descending", "method": "dateadded", "limit": %s}' % 0)

			elif info == 'libraryalltvshows':
				from resources.lib import local_db
				self.media_type = 'tv'
				self.search_str = local_db.get_db_tvshows('"sort": {"order": "descending", "method": "dateadded", "limit": %s}' % 0)

			elif info == 'popularmovies':
				tmdb_var = 'popular'
				self.media_type = 'movie'
				self.search_str = TheMovieDB.get_tmdb_movies(tmdb_var)

			elif info == 'topratedmovies':
				tmdb_var = 'top_rated'
				self.media_type = 'movie'
				self.search_str = TheMovieDB.get_tmdb_movies(tmdb_var)

			elif info == 'incinemamovies':
				tmdb_var = 'now_playing'
				self.media_type = 'movie'
				self.search_str = TheMovieDB.get_tmdb_movies(tmdb_var)

			elif info == 'upcomingmovies':
				tmdb_var = 'upcoming'
				self.media_type = 'movie'
				self.search_str = TheMovieDB.get_tmdb_movies(tmdb_var)

			elif info == 'populartvshows':
				tmdb_var = 'popular'
				self.media_type = 'tv'
				self.search_str = TheMovieDB.get_tmdb_shows(tmdb_var)

			elif info == 'topratedtvshows':
				tmdb_var = 'top_rated'
				self.media_type = 'tv'
				self.search_str = TheMovieDB.get_tmdb_shows(tmdb_var)

			elif info == 'onairtvshows':
				tmdb_var = 'on_the_air'
				self.media_type = 'tv'
				self.search_str = TheMovieDB.get_tmdb_shows(tmdb_var)

			elif info == 'airingtodaytvshows':
				tmdb_var = 'airing_today'
				self.media_type = 'tv'
				self.search_str = TheMovieDB.get_tmdb_shows(tmdb_var)

			self.fetch_data()
			self.update()
			Utils.hide_busy()

		@ch.click(5019)
		def close_all(self):
			xbmc.executebuiltin('Dialog.Close(all,true)')
			wm.window_stack_empty()

		def fetch_data(self, force=False):
			#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			addon = xbmcaddon.Addon()
			addon_path = addon.getAddonInfo('path')
			addonID = addon.getAddonInfo('id')
			addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
			Utils.show_busy()

			if wm.pop_video_list == True:
				#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
				self.page = int(wm.prev_window['params']['page'])

				self.sort = wm.prev_window['params']['sort']
				self.sort_label  = wm.prev_window['params']['sort_label']

				self.mode = wm.prev_window['params']['mode']
				self.type = wm.prev_window['params']['type']
				self.order = wm.prev_window['params']['order']
				self.search_str =wm.prev_window['params']['search_str']

				if self.search_str == 'Trakt Episodes/Movies in progress':
					#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
					response = get_trakt_playback('tv')
					listitems1 = []
					for i in response:
						ep = extended_episode_info(i['show']['ids']['tmdb'], i['episode']['season'], i['episode']['number'])
						ep[0]['tmdb_id'] = ep[1]['tvshow_id']
						ep[0]['PercentPlayed'] = int(i['progress'])
						listitems1.append(ep[0])
					response = get_trakt_playback('movie')
					for i in response:
						mov = extended_movie_info(i['movie']['ids']['tmdb'])
						mov[0]['PercentPlayed'] = int(i['progress'])
						listitems1.append(mov[0])

					x = 0
					page = int(self.page)
					listitems = []
					for i in listitems1:
						if x + 1 <= page * 20 and x + 1 > (page - 1) *  20:
							listitems.append(i)
							x = x + 1
						else:
							x = x + 1

					wm.prev_window['params']['listitems'] = listitems
					wm.prev_window['params']['total_pages'] = int(x/20) + (1 if x % 20 > 0 else 0)
					wm.prev_window['params']['total_items'] = x
					#xbmc.log(str(listitems)+'===>OPEN_INFO', level=xbmc.LOGINFO)
					self.mode = 'trakt'
					self.type = 'movie'

				self.filter_label =wm.prev_window['params']['filter_label']
				self.list_id = wm.prev_window['params']['list_id']
				self.filter_url = wm.prev_window['params']['filter_url']
				self.media_type = wm.prev_window['params']['media_type']
				self.filters = wm.prev_window['params']['filters']
				self.filter = wm.prev_window['params']['filter']
				info = {
					'listitems': wm.prev_window['params']['listitems'],
					'results_per_page': wm.prev_window['params']['total_pages'],
					'total_results': wm.prev_window['params']['total_items']
					}
				self.focus_id = xbmcgui.Window(10000).getProperty('focus_id')
				self.position = xbmcgui.Window(10000).getProperty('position')
				if str(self.position) != 'No position':
					xbmc.executebuiltin('Control.SetFocus(%s,%s)' % (self.focus_id,self.position))
				wm.pop_video_list = False

				fetch_data_dict_file = write_fetch_data_dict_file()
				fetch_data_dict = {}
				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()

				return info

			if self.mode == 'reopen_window':
				xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
				fetch_data_dict_file = read_fetch_data_dict_file()
				import ast
				fetch_data_dict_read = ast.literal_eval(fetch_data_dict_file.read())
				info = self.get_fetch_data_dict_read(fetch_data_dict_read)

				if self.search_str == 'Trakt Episodes/Movies in progress':
					listitems1 = []
					response = get_trakt_playback('tv')
					for i in response:
						for x in info['listitems']:
							if x['tmdb_id'] == i['show']['ids']['tmdb']:
								if x['episode'] == i['episode']['number'] and x['season'] == i['episode']['season']:
									x['PercentPlayed'] = int(i['progress'])
									listitems1.append(x)
					response = get_trakt_playback('movie')
					for i in response:
						for x in info['listitems']:
							if x['tmdb_id'] == i['movie']['ids']['tmdb']:
								x['PercentPlayed'] = int(i['progress'])
								listitems1.append(x)
					info['listitems'] = listitems1
				reopen_window = True

				fetch_data_dict_file = write_fetch_data_dict_file()
				fetch_data_dict = {}
				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				return info


				if self.mode == 'trakt' and 'Trakt Watched Movies' in str(self.filter_label):
					self.search_str = trakt_watched_movies()
				if self.mode == 'trakt' and 'Trakt Watched Shows' in str(self.filter_label):
					xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>PHIL', level=xbmc.LOGINFO)
					self.search_str = trakt_watched_tv_shows()
				if self.mode == 'trakt' and 'Trakt Unwatched Shows' in str(self.filter_label):
					self.search_str = trakt_unwatched_tv_shows()
			else:
				reopen_window = False

			fetch_data_dict_file = write_fetch_data_dict_file()
			sort_by = self.sort + '.' + self.order
			fetch_data_dict = {}



			if self.type == 'tv':
				temp = 'tv'
				rated = 'Rated TV shows'
				starred = 'Starred TV shows'
			else:
				temp = 'movies'
				rated = 'Rated movies'
				starred = 'Starred movies'


			test_number = 0
			try: test_number = int(self.search_str[2:])
			except: test_number = None
			if self.mode == 'search' and self.search_str[:2] == 'ls' and test_number:
				from resources.lib.TheMovieDB import get_imdb_list_ids
				self.search_str = get_imdb_list_ids(list_str=self.search_str,limit=0)
				self.mode = 'imdb2'

			if self.mode == 'search' and self.search_str[:2] == 'ur' and test_number:
				#fetch_data_dict_file = write_fetch_data_dict_file()
				data = TheMovieDB.get_imdb_userlists_search(imdb_id=self.search_str)
				listitems = []
				imdb_list = []
				imdb_list_name = []
				if data:
					for i in data['imdb_list']:
						list_name = (i[str(list(i)).replace('[\'','').replace('\']','')])
						list_number = (str(list(i)).replace('[\'','').replace('\']',''))
						imdb_list.append(list_number)
						imdb_list_name.append(list_name)
						listitems += [list_name]

				if listitems == []:
					return

				if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
					selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
				else:
					selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)

				if selection == -1:
					return
				Utils.show_busy()
				x = 0
				for i in imdb_list_name:
					if i == listitems[selection]:
						list_number = imdb_list[x]
						self.mode = 'imdb'
					x = x + 1
				if self.mode == 'imdb' and 'ls' in str(list_number):
					from resources.lib.TheMovieDB import get_imdb_list_ids
					self.search_str = get_imdb_list_ids(list_str=list_number,limit=0)
					self.mode = 'imdb2'

				elif self.mode == 'imdb' and 'ur' in str(list_number):
					from resources.lib.TheMovieDB import get_imdb_watchlist_ids
					self.search_str = get_imdb_watchlist_ids(list_number)
					self.mode = 'imdb2'


			if self.mode == 'search':
				#fetch_data_dict_file = write_fetch_data_dict_file()
				url = 'search/multi?query=%s&page=%i&include_adult=%s&' % (urllib.parse.quote_plus(self.search_str), self.page, xbmcaddon.Addon().getSetting('include_adults'))
				if self.search_str:
					self.filter_label = 'Results for:  ' + self.search_str.replace('Results for:  ','')
				else:
					self.filter_label = ''
				fetch_data_dict['self.search_str'] = self.search_str
				fetch_data_dict['self.filter_label'] = self.filter_label
				fetch_data_dict['self.page'] = self.page
				fetch_data_dict['self.sort'] = self.sort
				fetch_data_dict['self.sort_label'] = self.sort_label
				fetch_data_dict['self.order'] = self.order
				
			elif self.mode == 'person':
				#fetch_data_dict_file = write_fetch_data_dict_file()
				self.filter_label = 'Results for:  ' + self.search_str['person']
				listitems = self.search_str['cast_crew']
				info = {
					'listitems': listitems,
					'results_per_page': 1,
					'total_results': len(self.search_str['cast_crew'])
					}
				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				return info

			elif self.mode ==  'google_similar':
				movies = self.search_str
				x = 0
				page = int(self.page)

				listitems = []
				for i in movies:
					if x + 1 <= page * 20 and x + 1 > (page - 1) *  20:
						listitems.append(i)
						x = x + 1
					else:
						x = x + 1

				info = {
					'listitems': listitems,
					'results_per_page': int(int(x/20) + (1 if x % 20 > 0 else 0)),
					'total_results': len(self.search_str)
					}
				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				return info


			elif self.mode == 'list_items':
				#fetch_data_dict_file = write_fetch_data_dict_file()
				if int(self.page) == 1:
					self.filter_label = 'Results for:  ' + self.filter_label.replace('Results for:  ','')
				movies = self.search_str
				x = 0
				page = int(self.page)

				listitems = []
				for i in movies:
					if x + 1 <= page * 20 and x + 1 > (page - 1) *  20:
						listitems.append(i)
						x = x + 1
					else:
						x = x + 1

				info = {
					'listitems': listitems,
					'results_per_page': int(int(x/20) + (1 if x % 20 > 0 else 0)),
					'total_results': len(self.search_str)
					}
				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				return info
			elif self.mode == 'list':
				#fetch_data_dict_file = write_fetch_data_dict_file()
				url = 'list/%s?language=%s&' % (str(self.list_id), xbmcaddon.Addon().getSetting('LanguageID'))
				fetch_data_dict['self.list_id'] = self.list_id
			elif self.mode == 'imdb2':
				#fetch_data_dict_file = write_fetch_data_dict_file()
				movies = self.search_str
				x = 0
				page = int(self.page)
				listitems = None
				if not movies:
					info = {
						'listitems': None,
						'results_per_page': 0,
						'total_results': 0
						}
					return info
				for i in movies:
					if x + 1 <= page * 20 and x + 1 > (page - 1) *  20:
						imdb_id = i
						response = TheMovieDB.get_tmdb_data('find/%s?language=%s&external_source=imdb_id&' % (imdb_id, xbmcaddon.Addon().getSetting('LanguageID')), 13)
						try:
							response['movie_results'][0]['media_type'] = 'movie'
							if listitems == None:
								listitems = TheMovieDB.handle_tmdb_multi_search(response['movie_results'])
							else:
								listitems += TheMovieDB.handle_tmdb_multi_search(response['movie_results'])
							x = x + 1
						except:
							try:
								response['tv_results'][0]['media_type'] = 'tv'
								if listitems == None:
									listitems = TheMovieDB.handle_tmdb_multi_search(response['tv_results'])
								else:
									listitems += TheMovieDB.handle_tmdb_multi_search(response['tv_results'])
								x = x + 1
							except:
								self.search_str.pop(x)
								continue
					else:
						x = x + 1

				#response['total_pages'] = y 
				response['total_pages'] = int(x/20) + (1 if x % 20 > 0 else 0)
				response['total_results'] = x
				info = {
					'listitems': listitems,
					'results_per_page': response['total_pages'],
					'total_results': response['total_results']
					}

				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				return info
			elif self.mode == 'imdb':
				#fetch_data_dict_file = write_fetch_data_dict_file()
				movies = self.search_str
				x = 0
				y = 0
				page = int(self.page)
				listitems = None
				for i in str(movies).split(', <'):
					if x + 1 <= page * 20 and x + 1 > (page - 1) *  20:
						imdb_id = str('tt' + i.split(':')[1].split('[http]')[0])
						movie_title = str(i.split(':_')[1].split('_>')[0])
						response = TheMovieDB.get_tmdb_data('find/%s?language=%s&external_source=imdb_id&' % (imdb_id, xbmcaddon.Addon().getSetting('LanguageID')), 13)
						try:
							response['movie_results'][0]['media_type'] = 'movie'
							if listitems == None:
								listitems = TheMovieDB.handle_tmdb_multi_search(response['movie_results'])
							else:
								listitems += TheMovieDB.handle_tmdb_multi_search(response['movie_results'])
							x = x + 1
						except:
							try:
								response['tv_results'][0]['media_type'] = 'tv'
								if listitems == None:
									listitems = TheMovieDB.handle_tmdb_multi_search(response['tv_results'])
								else:
									listitems += TheMovieDB.handle_tmdb_multi_search(response['tv_results'])
								x = x + 1
							except:
								continue
					else:
						x = x + 1

				#response['total_pages'] = y 
				response['total_pages'] = int(x/20) + (1 if x % 20 > 0 else 0)
				response['total_results'] = x
				info = {
					'listitems': listitems,
					'results_per_page': response['total_pages'],
					'total_results': response['total_results']
					}

				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				return info

			elif 'tastedive' in str(self.mode):
				#fetch_data_dict_file = write_fetch_data_dict_file()
				wm.page = -1
				movies = self.search_str
				media_type = self.mode.replace('tastedive&','')
				self.type = media_type
				x = 0
				page = int(self.page)
				listitems = None
				listitems = []
				responses = {'page': 1, 'results': [],'total_pages': 1, 'total_results': 0}
				for i in movies:
					if x + 1 <= page * 20 and x + 1 > (page - 1) *  20:
						try: 
							if i['media_type'] == 'movie':
								response1 = TheMovieDB.single_movie_info(movie_id=i['item_id'], cache_time=7)
								response1['media_type'] = 'movie'
							else:
								response1 = TheMovieDB.single_tvshow_info(tvshow_id=i['item_id'], cache_time=7)
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
				listitems = TheMovieDB.handle_tmdb_multi_search(responses['results'])
				info = {
					'listitems': listitems,
					'results_per_page': total_pages,
					'total_results': total_results
					}
				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
				return info

			elif self.search_str == 'Trakt Calendar Episodes':
				#url = 'https://api.trakt.tv/sync/playback/type?start_at=2023-09-26T00%3A00%3A00.000Z&end_at=2023-07-01T23%3A59%3A59.000Z'
				past_date = datetime.now() - timedelta(days=12)
				tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
				today = (datetime.now()).strftime('%Y-%m-%d')
				url = 'https://api.trakt.tv/calendars/my/shows/%s/14' % str(past_date.strftime('%Y-%m-%d'))
				response = get_trakt_data(url=url, cache_days=0.0001, folder='Trakt')
				listitems1 = []
				for i in reversed(response):
					ep = extended_episode_info(i['show']['ids']['tmdb'], i['episode']['season'], i['episode']['number'])
					#if ep[0]['episode'] == '':
					#	season = extended_season_info(i['show']['ids']['tmdb'], i['episode']['season'])
					#	ep[1]['actors'] = season[1]['actors']
					#	ep[1]['crew'] = season[1]['crew']
					#	#ep[1]['guest_stars'] = season[1]['guest_stars']
					#	ep[0]['season'] = i['episode']['season']
					#	ep[0]['episode'] = i['episode']['number']
					#	ep[0]['Plot'] = season[1]['episodes'][i['episode']['number']-1]['Description']
					#	ep[0]['Description'] = season[1]['episodes'][i['episode']['number']-1]['Description']
					#	ep[0]['Votes'] = season[1]['episodes'][i['episode']['number']-1]['Votes']
					#	ep[0]['Rating'] = season[1]['episodes'][i['episode']['number']-1]['Rating']
					#	ep[0]['id'] = season[1]['episodes'][i['episode']['number']-1]['id']
					#	ep[0]['production_code'] = season[1]['episodes'][i['episode']['number']-1]['production_code']
					#	ep[0]['release_date'] = season[1]['episodes'][i['episode']['number']-1]['release_date']
					#	ep[0]['title'] = season[1]['episodes'][i['episode']['number']-1]['title']
					#	ep[0]['still'] = season[1]['episodes'][i['episode']['number']-1]['still'] 
					#	ep[0]['still_original'] = season[1]['episodes'][i['episode']['number']-1]['still_original'] 
					#	ep[0]['still_small'] = season[1]['episodes'][i['episode']['number']-1]['still_small'] 
					#	ep[0]['thumb'] = season[1]['episodes'][i['episode']['number']-1]['thumb'] 
					#	ep[1]['images'] = {}
					#	ep[1]['images']['still'] = season[1]['episodes'][i['episode']['number']-1]['still'] 
					#	ep[1]['images']['still_original'] = season[1]['episodes'][i['episode']['number']-1]['still_original'] 
					#	ep[1]['images']['still_small'] = season[1]['episodes'][i['episode']['number']-1]['still_small'] 
					#	ep[1]['images']['thumb'] = season[1]['episodes'][i['episode']['number']-1]['thumb'] 
					if ep[0]['release_date'] == tomorrow:
						ep[0]['title'] = ep[0]['title'] + '**'
					if ep[0]['release_date'] == today:
						ep[0]['title'] = ep[0]['title'] + '*'
					episode_title = str('%s - S%sE%s - %s' % (i['show']['title'], str(ep[0]['season']).zfill(2), str(ep[0]['episode']).zfill(2), ep[0]['title']))
					ep[0]['tmdb_id'] = ep[1]['tvshow_id']
					ep[0]['Plot'] = episode_title + ' \n ' + ep[0]['Plot']
					ep[0]['Description'] = episode_title + ' \n ' + ep[0]['Description'] 
					listitems1.append(ep[0])

				x = 0
				page = int(self.page)
				listitems = []
				for i in listitems1:
					if x + 1 <= page * 20 and x + 1 > (page - 1) *  20:
						listitems.append(i)
						x = x + 1
					else:
						x = x + 1

				#response['total_pages'] = y 
				total_pages = int(x/20) + (1 if x % 20 > 0 else 0)
				total_results = x
				#xbmc.log(str(listitems)+'===>OPEN_INFO', level=xbmc.LOGINFO)
				info = {
					'listitems': listitems,
					'results_per_page': total_pages,
					'total_results': total_results
					}
				self.mode = 'trakt'
				self.type = 'movie'
				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				return info

			elif self.search_str == 'Trakt Episodes/Movies in progress':
				response = get_trakt_playback('tv')
				listitems1 = []
				#xbmc.log(str(response)+'===>OPEN_INFO', level=xbmc.LOGINFO)
				for i in response:
					#xbmc.log(str(i)+'===>OPEN_INFO', level=xbmc.LOGINFO)
					ep = extended_episode_info(i['show']['ids']['tmdb'], i['episode']['season'], i['episode']['number'])
					#if ep[0]['episode'] == '':
					#	season = extended_season_info(i['show']['ids']['tmdb'], i['episode']['season'])
					#	ep[1]['actors'] = season[1]['actors']
					#	ep[1]['crew'] = season[1]['crew']
					#	#ep[1]['guest_stars'] = season[1]['guest_stars']
					#	ep[0]['season'] = i['episode']['season']
					#	ep[0]['episode'] = i['episode']['number']
					#	ep[0]['Plot'] = season[1]['episodes'][i['episode']['number']-1]['Description']
					#	ep[0]['Description'] = season[1]['episodes'][i['episode']['number']-1]['Description']
					#	ep[0]['Votes'] = season[1]['episodes'][i['episode']['number']-1]['Votes']
					#	ep[0]['Rating'] = season[1]['episodes'][i['episode']['number']-1]['Rating']
					#	ep[0]['id'] = season[1]['episodes'][i['episode']['number']-1]['id']
					#	ep[0]['production_code'] = season[1]['episodes'][i['episode']['number']-1]['production_code']
					#	ep[0]['release_date'] = season[1]['episodes'][i['episode']['number']-1]['release_date']
					#	ep[0]['title'] = season[1]['episodes'][i['episode']['number']-1]['title']
					#	ep[0]['still'] = season[1]['episodes'][i['episode']['number']-1]['still'] 
					#	ep[0]['still_original'] = season[1]['episodes'][i['episode']['number']-1]['still_original'] 
					#	ep[0]['still_small'] = season[1]['episodes'][i['episode']['number']-1]['still_small'] 
					#	ep[0]['thumb'] = season[1]['episodes'][i['episode']['number']-1]['thumb'] 
					#	ep[1]['images'] = {}
					#	ep[1]['images']['still'] = season[1]['episodes'][i['episode']['number']-1]['still'] 
					#	ep[1]['images']['still_original'] = season[1]['episodes'][i['episode']['number']-1]['still_original'] 
					#	ep[1]['images']['still_small'] = season[1]['episodes'][i['episode']['number']-1]['still_small'] 
					#	ep[1]['images']['thumb'] = season[1]['episodes'][i['episode']['number']-1]['thumb'] 

						#xbmc.log(str(season[1])+'===>OPEN_INFO', level=xbmc.LOGINFO)
					#xbmc.log(str(ep)+'===>OPEN_INFO', level=xbmc.LOGINFO)
					ep[0]['tmdb_id'] = ep[1]['tvshow_id']
					ep[0]['PercentPlayed'] = int(i['progress'])
					listitems1.append(ep[0])
					#xbmc.log(str(ep[0])+'===>OPEN_INFO', level=xbmc.LOGINFO)
				response = get_trakt_playback('movie')
				#xbmc.log(str(response)+'===>OPEN_INFO', level=xbmc.LOGINFO)
				for i in response:
					mov = extended_movie_info(i['movie']['ids']['tmdb'])
					mov[0]['PercentPlayed'] = int(i['progress'])
					listitems1.append(mov[0])

				x = 0
				page = int(self.page)
				listitems = []
				for i in listitems1:
					if x + 1 <= page * 20 and x + 1 > (page - 1) *  20:
						listitems.append(i)
						x = x + 1
					else:
						x = x + 1

				#response['total_pages'] = y 
				total_pages = int(x/20) + (1 if x % 20 > 0 else 0)
				total_results = x
				#xbmc.log(str(listitems)+'===>OPEN_INFO', level=xbmc.LOGINFO)
				info = {
					'listitems': listitems,
					'results_per_page': total_pages,
					'total_results': total_results
					}
				self.mode = 'trakt'
				self.type = 'movie'
				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				return info


			elif self.mode == 'trakt':
				#fetch_data_dict_file = write_fetch_data_dict_file()
				movies = self.search_str
				x = 0
				page = int(self.page)
				listitems = None
				responses = {'page': 1, 'results': [],'total_pages': 1, 'total_results': 0}
				if movies == None:
					info = {'listitems': None, 'results_per_page': 0, 'total_results': 0}
					return info

				for i in movies:
					response1 = None
					if (x + 1 <= page * 20 and x + 1 > (page - 1) *  20) or page == 0:
						try: 
							if i['type'] == 'movie':
								self.type = 'movie'
							else: 
								self.type = 'tv'
						except: 
							if "'movie': {'" in str(i) or 'movie' in str(self.filter_label).lower():
								self.type = 'movie'
							elif "'show': {'" in str(i) or not 'movie' in str(self.filter_label).lower():
								self.type = 'tv'
						try: 
							if self.type == 'movie':
								response1 = TheMovieDB.single_movie_info(i['movie']['ids']['tmdb'])
							else:
								response1 = TheMovieDB.single_tvshow_info(i['show']['ids']['tmdb'])
						#except TypeError:
						#	continue
						except KeyError or TypeError:
							try:
								if self.type == 'movie':
									response1 = TheMovieDB.single_movie_info(i['ids']['tmdb'])
								else:
									response1 = TheMovieDB.single_tvshow_info(i['ids']['tmdb'])
							except:
								continue
						if response1:
							responses['results'].append(response1)
						x = x + 1
					else:
						x = x + 1
				total_pages = int(x/20) + (1 if x % 20 > 0 else 0)
				total_results = x
				responses['total_pages'] = total_pages
				responses['total_results'] = total_results
				listitems = TheMovieDB.handle_tmdb_multi_search(responses['results'])
				info = {
					'listitems': listitems,
					'results_per_page': responses['total_pages'],
					'total_results': responses['total_results']
					}
				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				return info
			else:
				#fetch_data_dict_file = write_fetch_data_dict_file()
				if reopen_window == False:
					self.set_filter_url()
					self.set_filter_label()

				url = 'discover/%s?sort_by=%s&%slanguage=%s&page=%i&append_to_response=external_ids&include_adult=%s&' % (self.type, sort_by, self.filter_url, xbmcaddon.Addon().getSetting('LanguageID'), int(self.page), xbmcaddon.Addon().getSetting('include_adults'))
			if force:
				response = TheMovieDB.get_tmdb_data(url=url, cache_days=0)
			else:
				response = TheMovieDB.get_tmdb_data(url=url, cache_days=2)
			if not response:
				info = {'listitems': [], 'results_per_page': 0, 'total_results': 0}
				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				return None
			if 'results' not in response:
				info = {'listitems': [], 'results_per_page': 0, 'total_results': 0}
				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				return {'listitems': [], 'results_per_page': 0, 'total_results': 0}
			if not response['results']:
				Utils.notify('No results found')
			if self.mode == 'search':
				listitems = TheMovieDB.handle_tmdb_multi_search(response['results'])
			elif self.type == 'movie':
				listitems = TheMovieDB.handle_tmdb_movies(results=response['results'], local_first=False, sortkey=None)
			else:
				listitems = TheMovieDB.handle_tmdb_tvshows(results=response['results'], local_first=False, sortkey=None)
			info = {
				'listitems': listitems,
				'results_per_page': response['total_pages'],
				'total_results': response['total_results']
				}
			fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
			fetch_data_dict_file.write(str(fetch_data_dict))
			fetch_data_dict_file.close()
			return info
	return DialogVideoList
