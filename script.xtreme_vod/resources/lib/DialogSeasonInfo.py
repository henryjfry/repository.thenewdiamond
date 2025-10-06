import xbmc, xbmcgui, xbmcaddon, threading
from resources.lib import Utils
from resources.lib import ImageTools
from resources.lib import TheMovieDB
from resources.lib.WindowManager import wm
from resources.lib.VideoPlayer import PLAYER
from resources.lib.OnClickHandler import OnClickHandler
from resources.lib.DialogBaseInfo import DialogBaseInfo
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short

ch = OnClickHandler()

def get_season_window(window_type):

	class DialogSeasonInfo(DialogBaseInfo, window_type):

		def __init__(self, *args, **kwargs):
			super(DialogSeasonInfo, self).__init__(*args, **kwargs)
			self.type = 'Season'
			self.tvshow_id = kwargs.get('tvshow_id')
			data = TheMovieDB.extended_season_info(tvshow_id=self.tvshow_id, season_number=kwargs.get('season'))
			if not data:
				return None
			self.info, self.data = data
			if 'dbid' not in self.info:
				self.info['poster'] = Utils.get_file(url=self.info.get('poster', ''))
			#self.info['ImageFilter'], self.info['ImageColor'] = ImageTools.filter_image(input_img=self.info.get('poster', ''), radius=25)
			self.info['ImageFilter'], self.info['ImageColor'] = ImageTools.filter_image(input_img=self.info.get('thumb', ''), radius=25)
			"""
			try:
				filter_thread = ImageTools.FilterImageThread(self.data['images'][0]['thumb'], 25)
				filter_thread.start()
				filter_thread.join()
				self.info['ImageFilter'] = filter_thread.image
				self.info['ImageColor'] = filter_thread.imagecolor
				filter_thread.terminate()
			except:
				#self.info['ImageFilter'] = ''
				#self.info['ImageColor'] = ''
				try: filter_thread.terminate()
				except: pass
			"""

			TV = TheMovieDB.get_vod_alltv()
			season_number = kwargs.get('season')
			for x in TV:
				if x['tmdb'] == self.tvshow_id or str(x['tmdb'])== str(self.tvshow_id):
					series_id = x['series_id']
					break
			vod_series = TheMovieDB.get_vod_data(action= 'get_series_info&series_id=%s' % (str(series_id)) ,cache_days=1)
			tv_item = vod_series['info']
			if vod_series.get('episodes',False) != False:
				episodes = []
				for ic in vod_series['episodes']:
					if type(ic) == type(''):
						if int(season_number) == int(ic):
							Utils.tools_log(ic)
							for jc in vod_series['episodes'][ic]:
								Utils.tools_log(jc)
								try: episodes.append(jc['episode'])
								except: episodes.append(jc['episode_num'])
					elif type(ic) == type([]):
						for jk in ic:
							if int(jk['season']) == int(season_number):
								try: episodes.append(jk['episode'])
								except: episodes.append(jk['episode_num'])

			pop_idx = []
			for idx, i in enumerate(self.data['episodes']):
				if not int(i['episode']) in episodes:
					pop_idx.append(idx)
			for i in reversed(pop_idx):
				self.data['episodes'].pop(i)

			self.listitems = [
				(2000, self.data['episodes']),
				(1150, self.data['videos']),
				(1000, self.data['actors']),
				(750, self.data['crew']),
				(1250, self.data['images'])
				]

		def onInit(self):
			self.get_youtube_vids('%s %s tv' % (self.info['TVShowTitle'], self.info['title']))
			super(DialogSeasonInfo, self).onInit()
			try: clearlogo = TheMovieDB.get_fanart_clearlogo(tmdb_id=self.info['tmdb_id'],media_type='tv')
			except: clearlogo = ''
			xbmcgui.Window(self.window_id).setProperty('movie.logo', str(clearlogo))
			xbmcgui.Window(10000).setProperty('movie.logo', str(clearlogo))
			Utils.pass_dict_to_skin(data=self.info, prefix='movie.', window_id=self.window_id)
			self.fill_lists()

		def onClick(self, control_id):
			super(DialogSeasonInfo, self).onClick(control_id)
			ch.serve(control_id, self)

		def onAction(self, action):
			super(DialogSeasonInfo, self).onAction(action)
			ch.serve_action(action, self.getFocusId(), self)

		@ch.click(120)
		def browse_season(self):
			url = 'plugin://plugin.video.themoviedb.helper/?info=episodes&amp;season='+str(self.info['season'])+'&amp;tmdb_id='+str(self.info['tmdb_id'])+'&amp;tmdb_type=tv'
			self.close()
			xbmc.executebuiltin('ActivateWindow(videos,%s,return)' % url)


		@ch.action('play', 10)
		def context_play(self):
			self.info['media_type'] = 'season'
			Utils.context_play(window=self,tmdb_id = self.tvshow_id)

		@ch.action('play', 2000)
		def context_play(self):
			self.info['media_type'] = 'episode'
			Utils.context_play(window=self,tmdb_id = self.info['tmdb_id'])

		@ch.click(750)
		@ch.click(1000)
		def open_actor_info(self):
			wm.open_actor_info(prev_window=self, actor_id=self.listitem.getProperty('id'))

		@ch.action('contextmenu', 750)
		@ch.action('contextmenu', 1000)
		def actor_context_menu(self):
			listitems = ['Show TV show information', 'Search Person']
			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if selection == 0:
				wm.open_tvshow_info(prev_window=self, tmdb_id=self.tvshow_id, dbid=0)
			if selection == 1:
				self.close()
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=search_person,person=%s)' % self.listitem.getLabel())

		@ch.click(2000)
		def open_episode_info(self):
			wm.open_episode_info(prev_window=self, tvshow=self.info['TVShowTitle'], tvshow_id=self.tvshow_id, season=self.listitem.getProperty('season'), episode=self.listitem.getProperty('episode'))

		@ch.action('contextmenu', 2000)
		def context_menu(self):
			Utils.show_busy()
			if self.listitem.getProperty('dbid') and self.listitem.getProperty('dbid') != 0:
				dbid = self.listitem.getProperty('dbid')
			else:
				dbid = 0
			item_id = self.listitem.getProperty('id')
			episode_id = self.listitem.getProperty('episode')
			imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(self.tvshow_id), 'imdb_id')
			tvdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(self.tvshow_id), 'tvdb_id')
			listitems = ['Play - TMDB Helper']
			listitems += ['TV Show Info']
			#listitems += ['Play - RD Player']
			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			Utils.hide_busy()

			season = self.listitem.getProperty('season')
			if season == '':
				season = 0
			if selection == 0:
				xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.prepare_play_VOD_episode(tmdb = self.tvshow_id, series_id=None, search_str = None,episode=self.listitem.getProperty('episode'), season=season, window=self)
			if selection == 1:
				wm.open_tvshow_info(prev_window=self, tmdb_id=self.tvshow_id, dbid=0)
			if selection == 2:
				PLAYER.prepare_play_VOD_episode(tmdb = self.tvshow_id, series_id=None, search_str = None,episode=self.listitem.getProperty('episode'), season=season, window=self)



		@ch.action('play', 2000)
		@ch.action('playpause', 2000)
		@ch.action('pause', 2000)
		def play_episode(self):
			episode_id = self.listitem.getProperty('episode')
			xbmc.executebuiltin('Dialog.Close(all,true)')
			PLAYER.prepare_play_VOD_episode(tmdb = self.tvshow_id, series_id=None, search_str = None,episode=episode_id, season=self.listitem.getProperty('season'), window=self)

		@ch.click(10)
		def play_season(self):
			xbmc.executebuiltin('Dialog.Close(all,true)')
			PLAYER.prepare_play_VOD_episode(tmdb = self.tvshow_id, series_id=None, search_str = None,episode=1, season=self.info['season'], window=self)

		@ch.action('contextmenu', 10)
		def play_season_choose_player(self):
			url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=%s&amp;episode=1' % (self.tvshow_id, self.info['season'])
			xbmc.executebuiltin('Dialog.Close(all,true)')
			PLAYER.prepare_play_VOD_episode(tmdb = self.tvshow_id, series_id=None, search_str = None,episode=1, season=self.info['season'], window=self)

		@ch.click(445)
		def show_manage_dialog(self):
			manage_list = []
			manage_list.append(["Xtreme VOD's settings", 'Addon.OpenSettings("'+str(addon_ID())+'")'])

			import xbmcaddon
			selection = 0
			if selection > -1:
				for item in manage_list[selection][1].split('||'):
					xbmc.executebuiltin(item)

		@ch.click(446)
		def return_button(self):
			#from resources.lib.process import reopen_window
			self.close()
			#reopen_window()
			return wm.open_video_list(search_str='', mode='reopen_window')

		@ch.click(447)
		def refresh_button(self):
			from resources.lib.library import trakt_refresh_all
			Utils.show_busy()
			trakt_refresh_all()
			Utils.hide_busy()
			return

		@ch.click(448)
		def tmdb_trakt_context(self):
			xbmc.executebuiltin('RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type=tv,tmdb_id='+str(self.info['season'])+',season='+str(self.tvshow_id)+')')
			return

		@ch.click(132)
		def open_text(self):
			wm.open_textviewer(header='Overview', text=self.info['Plot'], color='FFFFFFFF')

		@ch.click(350)
		@ch.click(1150)
		def play_youtube_video(self):
			PLAYER.playtube(self.listitem.getProperty('youtube_id'), listitem=self.listitem, window=self)

	return DialogSeasonInfo