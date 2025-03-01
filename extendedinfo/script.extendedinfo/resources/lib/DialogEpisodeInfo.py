import xbmc, xbmcgui, threading
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

def get_episode_window(window_type):

	class DialogEpisodeInfo(DialogBaseInfo, window_type):

		def __init__(self, *args, **kwargs):
			if Utils.NETFLIX_VIEW == 'true':
				super(DialogEpisodeInfo, self).__init__(*args, **kwargs)
				self.type = 'Episode'
				self.tvshow_id = kwargs.get('tvshow_id')
				data = TheMovieDB.extended_episode_info(tvshow_id=self.tvshow_id, season=kwargs.get('season'), episode=kwargs.get('episode'))
				if not data:
					return None
				self.info, self.data = data
				self.listitems = [
					(1000, self.data['actors'] + self.data['guest_stars']),
					(750, self.data['crew']),
					(1350, self.data['images'])
					]
			else:
				super(DialogEpisodeInfo, self).__init__(*args, **kwargs)
				self.type = 'Episode'
				self.tvshow_id = kwargs.get('tvshow_id')
				data = TheMovieDB.extended_episode_info(tvshow_id=self.tvshow_id, season=kwargs.get('season'), episode=kwargs.get('episode'))
				if not data:
					return None
				self.info, self.data = data
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
				self.listitems = [
					(1150, self.data['videos']),
					(1000, self.data['actors'] + self.data['guest_stars']),
					(750, self.data['crew']),
					(1350, self.data['images'])
					]

		def onInit(self):
			super(DialogEpisodeInfo, self).onInit()
			try: clearlogo = TheMovieDB.get_fanart_clearlogo(tmdb_id=self.tvshow_id,media_type='tv')
			except: clearlogo = ''
			xbmcgui.Window(self.window_id).setProperty('movie.logo', str(clearlogo))
			xbmcgui.Window(10000).setProperty('movie.logo', str(clearlogo))
			Utils.pass_dict_to_skin(self.info, 'movie.', False, False, self.window_id)
			self.get_youtube_vids('%s tv' % self.info['title'])
			self.fill_lists()

		def onClick(self, control_id):
			super(DialogEpisodeInfo, self).onClick(control_id)
			ch.serve(control_id, self)

		def onAction(self, action):
			super(DialogEpisodeInfo, self).onAction(action)
			ch.serve_action(action, self.getFocusId(), self)

		@ch.click(750)
		@ch.click(1000)
		def open_actor_info(self):
			wm.open_actor_info(prev_window=self, actor_id=self.listitem.getProperty('id'))

		@ch.action('contextmenu', 750)
		@ch.action('contextmenu', 1000)
		def context_menu(self):
			listitems = ['TV Show Info']
			listitems += ['Season Info']
			listitems += ['Search Person']
			selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if selection == 0:
				wm.open_tvshow_info(prev_window=self, tmdb_id=self.tvshow_id, dbid=0)
			if selection == 1:
				wm.open_season_info(prev_window=self, tvshow_id=self.tvshow_id, season=self.info['season'], tvshow='')
			if selection == 2:
				self.close()
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=search_person,person=%s)' % self.listitem.getLabel())

		@ch.click(132)
		def open_text(self):
			wm.open_textviewer(header='Overview', text=self.info['Plot'], color='FFFFFFFF')

		@ch.click(350)
		@ch.click(1150)
		def play_youtube_video(self):
			PLAYER.playtube(self.listitem.getProperty('youtube_id'), listitem=self.listitem, window=self)

		@ch.click(8)
		def play_episode(self):
			if self.dbid and int(self.dbid) > 0:
				dbid = self.dbid
				url = ''
				xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.play_from_button(url, listitem=None, window=self, type='episodeid', dbid=dbid)
			else:
				url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;tmdb_id=%s&amp;type=episode&amp;season=%s&amp;episode=%s' % (self.tvshow_id, self.info['season'], self.info['episode'])
				#xbmc.executebuiltin('RunPlugin(%s)' % url)
				xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)

		@ch.action('contextmenu', 8)
		def play_episode_choose_player(self):
			if self.dbid and int(self.dbid) > 0:
				dbid = self.dbid
				url = ''
				xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.play_from_button(url, listitem=None, window=self, type='episodeid', dbid=dbid)
			else:
				url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;tmdb_id=%s&amp;type=episode&amp;season=%s&amp;episode=%s' % (self.tvshow_id, self.info['season'], self.info['episode'])
				#xbmc.executebuiltin('RunPlugin(%s)' % url)
				xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)

		@ch.click(445)
		def show_manage_dialog(self):
			manage_list = []
			manage_list.append([str(addon_ID_short()) + " Settings", 'Addon.OpenSettings("'+str(addon_ID())+'")'])
			manage_list.append(["TMDBHelper Context", 'RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type=tv,tmdb_id='+str(self.info['season'])+',season='+str(self.tvshow_id)+',episode='+str(self.info['episode'])+')'])
			manage_list.append(["TmdbHelper settings", 'Addon.OpenSettings("plugin.video.themoviedb.helper")'])
			manage_list.append(["YouTube's settings", 'Addon.OpenSettings("plugin.video.youtube")'])
			import xbmcaddon
			settings_user_config = xbmcaddon.Addon(addon_ID()).getSetting('settings_user_config')
			if settings_user_config == 'Settings Selection Menu':
				selection = xbmcgui.Dialog().select(heading='Settings', list=[i[0] for i in manage_list])
			else:
				selection = 1
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
			xbmc.executebuiltin('RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type=tv,tmdb_id='+str(self.info['season'])+',season='+str(self.tvshow_id)+',episode='+str(self.info['episode'])+')')
			return

	return DialogEpisodeInfo