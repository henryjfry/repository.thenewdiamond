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

from resources.lib.library import trakt_next_episode_normal
from resources.lib.library import trakt_next_episode_rewatch
from resources.lib.library import trakt_watched_tv_shows
from resources.lib.library import trakt_eps_movies_in_progress
from resources.lib.library import trakt_calendar_eps
from resources.lib.library import trakt_watched_movies


from resources.lib.library import trakt_watched_tv_shows_progress
from resources.lib.library import trak_auth
from resources.lib.TheMovieDB import get_trakt_playback
from resources.lib.TheMovieDB import extended_episode_info
#from resources.lib.TheMovieDB import extended_season_info
from resources.lib.TheMovieDB import extended_movie_info
from resources.lib.library import get_trakt_data
from datetime import datetime, timedelta
import math

from inspect import currentframe, getframeinfo
#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
ch = OnClickHandler()
"""
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
"""
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

		"""
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
		"""

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
			#if wm.custom_filter:
			#	self.setup_filter(wm.custom_filter)
			#	wm.custom_filter = None
			#	self.update_content(force_update=kwargs.get('force', False))

			if self.listitem_list:
				#xbmc.log(str(wm.page), level=xbmc.LOGINFO)
				#xbmc.log(str(self.page), level=xbmc.LOGINFO)

				#self.listitems = Utils.create_listitems(self.listitem_list)
				#self.total_items = len(self.listitem_list)
				self.update_content(force_update=kwargs.get('force', False))
			elif self.filters == []:
				self.filters = []
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
			if (self.filter_label == 'Trakt Episodes/Movies in progress' or self.filter_label == 'Trakt Calendar Episodes') and xbmc.getInfoLabel('listitem.DBTYPE') == 'episode':
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
			self.getControl(5006).setVisible(True) ##PAGES
			self.getControl(5008).setVisible(False)
			self.getControl(5009).setVisible(False)
			self.getControl(5010).setVisible(False)
			
			self.getControl(6000).setVisible(True)
			self.getControl(6001).setVisible(False)
			self.getControl(5002).setVisible(False)
			self.getControl(5003).setVisible(False)
			self.getControl(5005).setVisible(False)
			self.getControl(5007).setVisible(False)
			self.getControl(5008).setVisible(False)
			self.getControl(5009).setVisible(False)
			self.getControl(5010).setVisible(False)
			self.getControl(5011).setVisible(False)
			self.getControl(5012).setVisible(False)
			self.getControl(5013).setVisible(False)
			#self.getControl(5014).setVisible(False) ##Categories
			self.getControl(5015).setVisible(True) ##TRAKT
			self.getControl(5016).setVisible(False)
			self.getControl(5017).setVisible(False)
			self.getControl(5018).setVisible(False)
			
			
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
			#Utils.tools_log('context_play')
			#Utils.tools_log(self.listitem.getProperty('full_url'))
			#Utils.tools_log(self.listitem.getProperty('stream_id'))
			#Utils.tools_log(self.listitem.getProperty('id'))
			#Utils.tools_log(self.listitem.getProperty('media_type'))
			if self.listitem.getProperty('media_type') == 'movie' or self.listitem.getProperty('media_type') == '':
				search_str = self.search_str
				stream_id = self.listitem.getProperty('stream_id')
				title = self.listitem.getProperty('Label')
				tmdb = self.listitem.getProperty('id')
				PLAYER.prepare_play_VOD_movie(tmdb = tmdb, title = title, stream_id=stream_id, search_str = search_str, window=self)
				return
			
			try: UnWatchedEpisodes = int(self.listitem.getProperty('UnWatchedEpisodes'))
			except: UnWatchedEpisodes = 0
			if UnWatchedEpisodes > 2:
				tmdb_id, season, episode = trakt_next_episode_normal(tmdb_id_num=self.listitem.getProperty('id'))
				#xbmc.executebuiltin('Dialog.Close(all,true)')
				#PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
				PLAYER.prepare_play_VOD_episode(tmdb = tmdb_id, series_id=None, search_str = None,episode=episode, season=season, window=self)
			else:
				Utils.context_play(window=self,tmdb_id=self.listitem.getProperty('id'))

		@ch.action('info', 500)
		@ch.action('contextmenu', 500)
		def context_menu(self):
			self.position = self.getControl(500).getSelectedPosition()
			wm.position = self.position
			xbmcgui.Window(10000).setProperty('focus_id', str(500))
			xbmcgui.Window(10000).setProperty('position', str(self.position))
			#if str(xbmcaddon.Addon(addon_ID()).getSetting('trakt_kodi_mode')) == 'Trakt Only':
			#	trakt_only = True
			#else:
			#	trakt_only = False
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
				if self.filter_label == 'Trakt Episodes/Movies in progress' or self.filter_label == 'Trakt Calendar Episodes':
					self_type = 'movie'
			if self_type == 'tv':
				imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'imdb_id')
				tvdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'tvdb_id')
			else:
				imdb_id = TheMovieDB.get_imdb_id_from_movie_id(item_id)
			listitems = []

			if self_type == 'tv':
				listitems += ['Play Trakt Next Episode']
				listitems += ['Play Trakt Next Episode (Rewatch)']

				listitems += ['Play first episode']
			else:
				listitems += ['Play']

			#listitems += ['Trailer']
			listitems += ['IMDB Trailers - Best']
			listitems += ['IMDB Trailers - Choose']

			if self.filter_label == 'Trakt Episodes/Movies in progress':
				listitems += ['Trakt remove playback entry']
			if item_id in str(last_played_tmdb_helper):
				listitems += ['Last Played URL']

			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			selection_text = listitems[selection]
			if selection == -1:
				return

			xbmcgui.Window(10000).setProperty('tmdbhelper_tvshow.poster', str(self.listitem.getProperty('poster')))
			if selection_text == 'Last Played URL':
				#xbmc.executebuiltin('Dialog.Close(busydialog)')
				#xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.play_from_button(last_played_tmdb_helper, listitem=None, window=self, dbid=0)
			if selection_text == 'Play first episode':
				PLAYER.prepare_play_VOD_episode(tmdb = self.listitem.getProperty('id'), series_id=self.listitem.getProperty('series_id'), search_str = self.search_str,episode=1, season=1, window=self)
			elif selection_text == 'Play':
				search_str = self.search_str
				stream_id = self.listitem.getProperty('stream_id')
				title = self.listitem.getProperty('Label')
				tmdb = self.listitem.getProperty('id')
				PLAYER.prepare_play_VOD_movie(tmdb = self.listitem.getProperty('id'), title = title, stream_id=stream_id, search_str = search_str, window=self)

			if selection_text == 'Play Trakt Next Episode':
				tmdb_id, season, episode = trakt_next_episode_normal(tmdb_id_num=item_id)
				#xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.prepare_play_VOD_episode(tmdb = self.listitem.getProperty('id'), series_id=self.listitem.getProperty('series_id'), search_str = self.search_str,episode=episode, season=season, window=self)

			if selection_text == 'Play Trakt Next Episode (Rewatch)':
				tmdb_id, season, episode = trakt_next_episode_rewatch(tmdb_id_num=item_id)
				#xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.prepare_play_VOD_episode(tmdb = self.listitem.getProperty('id'), series_id=None, search_str = self.search_str,episode=episode, season=season, window=self)

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
				self.search_str = trakt_eps_movies_in_progress()
				#self.fetch_data()
				self.update()

			if selection_text == 'IMDB Trailers - Choose' or selection_text == 'IMDB Trailers - Best':
				#import imdb_trailers
				if xbmc.getInfoLabel('listitem.DBTYPE') == 'movie':
					imdb_id = TheMovieDB.get_imdb_id_from_movie_id(item_id)
					media_type = 'movie'
				elif xbmc.getInfoLabel('listitem.DBTYPE') in ['tv', 'tvshow', 'season', 'episode']:
					imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'imdb_id')
					media_type = 'tv'
				if selection_text == 'IMDB Trailers - Best':
					url = 'RunScript(%s,info=imdb_trailers_best,imdb_id=%s)' % (str(addon_ID()), str(imdb_id))
					if media_type == 'tv':
						url = url + '&season=1'
				else:
					url = 'RunScript(%s,info=imdb_trailers_choice,imdb_id=%s)' % (str(addon_ID()), str(imdb_id))
				#xbmc.executebuiltin(url)
				#PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
				PLAYER.play_url(url=url, window=self)

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
			if self.mode == 'allmovies2':
				self.type = 'tv'
				self.mode = 'alltvshows2'
				from resources.lib.TheMovieDB import get_vod_alltv
				self.search_str = get_vod_alltv()
				self.filter_label = 'VOD TV'
			elif self.mode == 'alltvshows2':
				self.type = 'movie'
				self.mode = 'allmovies2'
				from resources.lib.TheMovieDB import get_vod_allmovies
				self.search_str = get_vod_allmovies()
				self.filter_label = 'VOD Movies'
			else:
				self.mode = 'filter'
				self.type = 'movie' if self.type == 'tv' else 'tv'
			
			wm.page = -1
			if (self.filter_label == 'Trakt Episodes/Movies in progress' or self.filter_label == 'Trakt Calendar Episodes'):
				self.search_str = ''
			#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			self.update()


		@ch.click(5014)
		def get_category(self):
			self.page = 1
			if self.type == 'tv':
				self.mode = 'alltvshows2'
				movies = TheMovieDB.get_vod_data(action= 'get_series_categories' ,cache_days=1) 
				listitems = []
				for i in movies:
					listitems += [i['category_name']]
				if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
					selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
				else:
					selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
				if selection == -1:
					return
				self.sort_label = movies[selection]['category_id']
				self.filter_label = 'VOD:  ' + movies[selection]['category_name']
			else:
				self.mode = 'allmovies2'
				movies = TheMovieDB.get_vod_data(action= 'get_vod_categories' ,cache_days=1) 
				listitems = []
				for i in movies:
					listitems += [i['category_name']]
				if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
					selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
				else:
					selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
				if selection == -1:
					return
				self.sort_label = movies[selection]['category_id']
				self.filter_label = 'VOD:  ' + movies[selection]['category_name']
			self.fetch_data()
			self.update()
			return



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
					try: tmdb_id = response['results'][0]['id']
					except: tmdb_id = None
					if tmdb_id:
						wm.open_movie_info(prev_window=self, movie_id=tmdb_id, dbid=self.listitem.getProperty('dbid'))
					else:
						Utils.tools_log('PLAY_ITEM!!')
						Utils.tools_log(self.listitem.getProperty('path'))
				else:
					wm.open_movie_info(prev_window=self, movie_id=self.listitem.getProperty('id'), dbid=self.listitem.getProperty('dbid'))


		@ch.click(5006)
		def set_page_number(self):
			page = xbmcgui.Dialog().input(heading='Page Number', type=xbmcgui.INPUT_NUMERIC)#
			try: self.page = int(page)
			except: return
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

			listitems = []
			listitems = ['Trakt Watched Shows']
			listitems += ['Trakt Episodes/Movies in progress']
			listitems += ['Trakt Calendar Episodes']
			listitems += ['Trakt Watched Movies']


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

			elif listitems[selection] == 'Trakt Watched Shows':
				self.search_str = trakt_watched_tv_shows()
				self.type = 'tv'

			elif listitems[selection] == 'Trakt Episodes/Movies in progress':
				self.search_str = trakt_eps_movies_in_progress()
				self.mode = 'trakt'
				self.type = 'movie'
				self.filter_label = 'Trakt Episodes/Movies in progress'
				self.fetch_data()
				self.update()
				Utils.hide_busy()
				return


			elif listitems[selection] == 'Trakt Calendar Episodes':
				self.search_str = trakt_calendar_eps()
				self.mode = 'trakt'
				self.type = 'movie'
				self.filter_label = 'Trakt Calendar Episodes'
				self.fetch_data()
				self.update()
				Utils.hide_busy()
				return

			if not 'trakt' in str(listitems[selection]).lower():
				self.filter_label = 'Results for: Trakt ' + listitems[selection]
			else:
				self.filter_label = 'Results for: ' + listitems[selection]

			self.fetch_data()
			self.update()
			Utils.hide_busy()


		@ch.click(5019)
		def close_all(self):
			xbmc.executebuiltin('Dialog.Close(all,true)')
			wm.window_stack_empty()

		def filter_vod(self, movie_tv_items):
			TV = TheMovieDB.get_vod_alltv()
			movies = TheMovieDB.get_vod_allmovies()
			movie_tv_items2 = movie_tv_items
			for idx, i in enumerate(movie_tv_items2):
				match = False
				try: 
					media_type = i['media_type']
					tmdb_id = i['tmdb_id']
				except: 
					if i.get('show',False) == False:
						media_type = 'movie'
						tmdb_id = i['movie']['ids']['tmdb']
					else:
						media_type = 'tv'
						tmdb_id = i['show']['ids']['tmdb']
				if media_type == 'movie':
					for x in movies:
						if str(tmdb_id) == str(x['tmdb']):
							match = True
							break
				else:
					for x in TV:
						if str(tmdb_id) == str(x['tmdb']):
							match = True
							break
				if match == False:
					movie_tv_items.pop(idx)
			return movie_tv_items

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

				if self.filter_label == 'Trakt Episodes/Movies in progress':
					self.search_str = trakt_eps_movies_in_progress()
					self.search_str = self.filter_vod(self.search_str)
					self.mode = 'trakt'
					self.type = 'movie'
					self.filter_label = 'Trakt Episodes/Movies in progress'
					self.search_str = self.filter_vod(self.search_str)
					listitems1 = self.search_str

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


				if self.filter_label == 'Trakt Episodes/Movies in progress':
					listitems1 = trakt_eps_movies_in_progress()
					listitems1 = self.filter_vod(listitems1)
					info['listitems'] = listitems1
				reopen_window = True

				fetch_data_dict_file = write_fetch_data_dict_file()
				fetch_data_dict = {}
				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				return info

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

			if self.sort_label.isnumeric():
				if self.mode == 'allmovies2':
					self.search_str = TheMovieDB.get_vod_allmovies(self.sort_label)
					self.sort_label = '&' + self.sort_label + '&'
				elif self.mode == 'alltvshows2':
					self.search_str = TheMovieDB.get_vod_alltv(self.sort_label)
					self.sort_label = '&' + self.sort_label + '&'

			#Utils.tools_log(self.mode)
			if self.mode == 'search':
				#fetch_data_dict_file = write_fetch_data_dict_file()
				url = 'search/multi?query=%s&page=%i&include_adult=%s&' % (urllib.parse.quote_plus(self.search_str), self.page, xbmcaddon.Addon().getSetting('include_adults'))
				search_string = self.search_str
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


			elif self.mode == 'allmovies2' or self.mode == 'alltvshows2':
				#fetch_data_dict_file = write_fetch_data_dict_file()
				movies = self.search_str
				x = 0
				page = int(self.page)
				listitems = None
				responses = {'page': 1, 'results': [],'total_pages': 1, 'total_results': 0}
				if movies == None:
					info = {'listitems': None, 'results_per_page': 0, 'total_results': 0}
					return info

				pop_movies = []
				curr_movies = []
				idx = 0
				for i in movies:
					response1 = None
					if (x + 1 <= page * 20 and x + 1 > (page - 1) *  20) or page == 0:
						#Utils.tools_log(i)
						curr_movies.append(i)
						if i['type'] == 'movie':
							self.type = 'movie'
						else: 
							self.type = 'tv'
						if len(i.get('tmdb','0')) > 0:
							if self.type == 'movie':
								if 'tt' in str(i['tmdb']):
									i['tmdb'] = TheMovieDB.get_movie_tmdb_id(imdb_id=i['tmdb'])
								response1 = TheMovieDB.single_movie_info(i['tmdb'])
								response1['original_title'] = i['title']
								response1['title'] = i['title']
								response1['full_url'] = i['full_url']
								response1['stream_id'] = i['stream_id']
								response1['path'] = i['full_url']
							else:
								if 'tt' in str(i['tmdb']):
									i['tmdb'] = TheMovieDB.get_show_tmdb_id(imdb_id=i['tmdb'])
								response1 = TheMovieDB.single_tvshow_info(i['tmdb'])
								response1['series_id'] = i['series_id']
						else:
							pop_movies.append(idx)
							response1 = None
						if response1:
							responses['results'].append(response1)
						x = x + 1
						idx = idx + 1
					else:
						x = x + 1
				missing_movies = []
				movies = curr_movies
				for i in reversed(pop_movies):
					#Utils.tools_log(i)
					idx = i
					i = movies[idx]
					missing_dict = {'Label': i['title'], 'OriginalTitle': i['title'], 'Popularity': None, 'Rating': i['rating'], 'Trailer': None, 'User_Rating': i['rating'], 'Votes': None, 'character': None, 'credit_id': None, 'department': None, 'fanart_original': i['stream_icon'], 'fanart_small': i['stream_icon'], 'id': None, 'job': None, 'mediatype': i['stream_type'], 'stream_id': i['stream_id'], 'full_url': i['full_url'], 'path': i['full_url'],  'plot': None, 'poster': i['stream_icon'], 'poster_original': i['stream_icon'], 'poster_small': i['stream_icon'], 'thumb': i['stream_icon'], 'title': i['title']}
					missing_movies.append(missing_dict)
					movies.pop(idx)
				#Utils.tools_log(missing_movies)
				total_pages = int(x/20) + (1 if x % 20 > 0 else 0)
				total_results = x
				responses['total_pages'] = total_pages
				responses['total_results'] = total_results
				listitems = TheMovieDB.handle_tmdb_multi_search(responses['results'])
				for idx,i in enumerate(listitems):
					#Utils.tools_log(i)
					if self.type == 'movie':
						listitems[idx]['path'] = movies[idx]['full_url']
						listitems[idx]['full_url'] = movies[idx]['full_url']
						listitems[idx]['stream_id'] = movies[idx]['stream_id']
						listitems[idx]['Label'] = movies[idx]['title']
						listitems[idx]['OriginalTitle'] = movies[idx]['title']
						listitems[idx]['title'] = movies[idx]['title']
					else:
						listitems[idx]['series_id'] = movies[idx]['series_id']
				if len(missing_movies) >= 1:
					listitems.extend(missing_movies)
				info = {
					'listitems': listitems,
					'results_per_page': responses['total_pages'],
					'total_results': responses['total_results']
					}
				fetch_data_dict = self.update_fetch_data_dict(info, fetch_data_dict)
				fetch_data_dict_file.write(str(fetch_data_dict))
				fetch_data_dict_file.close()
				return info

			elif self.filter_label == 'Trakt Episodes/Movies in progress' or  self.filter_label == 'Trakt Calendar Episodes':
				self.search_str = self.filter_vod(self.search_str)
				listitems1 = self.search_str

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
				self.search_str = self.filter_vod(self.search_str)
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
				#Utils.tools_log(search_string)
				#if self.type == 'movie':
				if 1==1:
					#movies = TheMovieDB.get_vod_data(action= 'get_vod_streams' ,cache_days=1) 
					movies = TheMovieDB.get_vod_allmovies()
					search_str = []
					tmdb_list = []
					vod_list = []
					vod_tmdb_list = []
					for i in movies:
						#Utils.tools_log(i)
						#try:
						if 1==1:
							if len(str(i.get('tmdb','0'))) > 0:
								if 'tt' in str(i['tmdb']):
									i['tmdb'] = TheMovieDB.get_movie_tmdb_id(imdb_id=i['tmdb'])
								tmdb_list.append(int(i['tmdb']))
							#full_url = '%s%s/%s/%s/%s.%s' % (Utils.xtreme_codes_server_path,i['stream_type'],Utils.xtreme_codes_username,Utils.xtreme_codes_password,str(i['stream_id']),str(i['container_extension']))
							#search_str.append({'type': 'movie','title':i['name'],'tmdb':i['tmdb'], 'full_url': full_url, 'stream_type': i['stream_type'],'stream_icon': i['stream_icon'], 'rating': i['rating'],'category_ids': i['category_ids']})
							search_str.append(i)
							if search_string.lower() in str(i['title']).lower():
								if len(i.get('tmdb','0')) > 0:
									if 'tt' in str(i['tmdb']):
										i['tmdb'] = TheMovieDB.get_movie_tmdb_id(imdb_id=i['tmdb'])
									response1 = TheMovieDB.single_movie_info(i['tmdb'])
									response1['original_title'] = i['title']
									response1['title'] = i['title']
									response1['full_url'] = i['full_url']
									response1['stream_id'] = i['stream_id']
									response1['path'] = i['full_url']
								else:
									response1 = None
								if response1:
									vod_list.append(response1)
									vod_tmdb_list.append(int(i['tmdb']))
						#except:
						#	pass
					pop_list = []
					for idx, i in enumerate(response['results']):
						if i['media_type'] == 'movie': 
							if i['id'] in tmdb_list and not i['id'] in vod_tmdb_list:
								continue
							else:
								pop_list.append(idx)
						else:
							continue

					#Utils.tools_log(response)
					#Utils.tools_log(pop_list)
					for i in reversed(pop_list):
						response['results'].pop(i)
					response['results'].extend(vod_list)

					movies = TheMovieDB.get_vod_alltv()
					search_str = []
					tmdb_list = []
					vod_list = []
					vod_tmdb_list = []
					for i in movies:
						#Utils.tools_log(i)
						#try:
						if 1==1:
							if len(i.get('tmdb','0')) > 0:
								if 'tt' in str(i['tmdb']):
									i['tmdb'] = TheMovieDB.get_show_tmdb_id(imdb_id=i['tmdb'])
								tmdb_list.append(int(i['tmdb']))
							#full_url = '%s%s/%s/%s/%s.%s' % (Utils.xtreme_codes_server_path,i['stream_type'],Utils.xtreme_codes_username,Utils.xtreme_codes_password,str(i['stream_id']),str(i['container_extension']))
							#search_str.append({'type': 'movie','title':i['name'],'tmdb':i['tmdb'], 'full_url': full_url, 'stream_type': i['stream_type'],'stream_icon': i['stream_icon'], 'rating': i['rating'],'category_ids': i['category_ids']})
							search_str.append(i)
							if search_string.lower() in str(i['title']).lower():
								if len(i.get('tmdb','0')) > 0:
									if 'tt' in str(i['tmdb']):
										i['tmdb'] = TheMovieDB.get_show_tmdb_id(imdb_id=i['tmdb'])
									response1 = TheMovieDB.single_tvshow_info(i['tmdb'])
									response1['series_id'] = i['series_id']
								else:
									response1 = None
								if response1:
									vod_list.append(response1)
									vod_tmdb_list.append(int(i['tmdb']))
						#except:
						#	pass
					pop_list = []
					for idx, i in enumerate(response['results']):
						if i['media_type'] != 'movie': 
							if i['id'] in tmdb_list and not i['id'] in vod_tmdb_list:
								continue
							else:
								pop_list.append(idx)
						else:
							continue
					#Utils.tools_log(response)
					#Utils.tools_log(pop_list)
					for i in reversed(pop_list):
						response['results'].pop(i)

					response['results'].extend(vod_list)
					response['results'] = sorted(response['results'], key=lambda k: k['title'], reverse=False)
					#response['results'] = sorted(response['results'], key=lambda k: k['title'].get('sub_key', 0), reverse=False)
					
					response['total_results'] = len(response['results'])
					response['total_pages'] = math.ceil(response['total_results']/20)
				#Utils.tools_log(self.page)
				#Utils.tools_log('self.page')
				response_results = response['results']
				response['results'] = []
				x = 0
				page = int(self.page)
				for i in response_results:
					#Utils.tools_log(i)
					if (x + 1 <= page * 20 and x + 1 > (page - 1) *  20) or page == 0:
						response['results'].append(i)
					x = x + 1
				#Utils.tools_log(response['results'])
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
