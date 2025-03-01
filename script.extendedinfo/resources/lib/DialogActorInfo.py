import xbmc, xbmcgui, xbmcaddon, threading
from resources.lib import Utils
from resources.lib import ImageTools
from resources.lib import TheMovieDB
from resources.lib.WindowManager import wm
from resources.lib.VideoPlayer import PLAYER
from resources.lib.OnClickHandler import OnClickHandler
from resources.lib.DialogBaseInfo import DialogBaseInfo
from resources.lib.library import addon_ID

ch = OnClickHandler()

def get_actor_window(window_type):

	class DialogActorInfo(DialogBaseInfo, window_type):

		def __init__(self, *args, **kwargs):
			super(DialogActorInfo, self).__init__(*args, **kwargs)
			self.id = kwargs.get('id', False)
			self.type = 'Actor'
			data = TheMovieDB.extended_actor_info(actor_id=self.id)
			if not data:
				return None
			self.info, self.data = data
			self.info['ImageFilter'], self.info['ImageColor'] = ImageTools.filter_image(input_img=self.info.get('thumb', ''), radius=25)
			#self.info['ImageFilter'], self.info['ImageColor'] = ImageTools.filter_image(input_img=self.data['images'][0]['thumb'], radius=25)
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
				(150, self.data['movie_roles']),
				(250, self.data['tvshow_roles']),
				(450, self.data['images']),
				(550, Utils.merge_dict_lists(self.data['movie_crew_roles'])),
				(650, Utils.merge_dict_lists(self.data['tvshow_crew_roles'])),
				(750, self.data['tagged_images'])
				]

		def onInit(self):
			self.get_youtube_vids(self.info['name'])
			super(DialogActorInfo, self).onInit()
			Utils.pass_dict_to_skin(data=self.info, prefix='actor.', window_id=self.window_id)
			self.fill_lists()

		def onClick(self, control_id):
			super(DialogActorInfo, self).onClick(control_id)
			ch.serve(control_id, self)

		def onAction(self, action):
			super(DialogActorInfo, self).onAction(action)
			ch.serve_action(action, self.getFocusId(), self)

		@ch.click(150)
		@ch.click(550)
		def open_movie_info(self):
			wm.open_movie_info(prev_window=self, movie_id=self.listitem.getProperty('id'), dbid=self.listitem.getProperty('dbid'))

		@ch.click(250)
		@ch.click(650)
		def open_tvshow_dialog(self):
			#selection = xbmcgui.Dialog().select(heading='Choose option', list=['Show TV show information', 'Show actor TV show appearances'])
			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu(['Show TV show information', 'Show actor TV show appearances'])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=['Show TV show information', 'Show actor TV show appearances'])
			if selection == 0:
				wm.open_tvshow_info(prev_window=self, tmdb_id=self.listitem.getProperty('id'), dbid=self.listitem.getProperty('dbid'))
			if selection == 1:
				self.open_credit_dialog(credit_id=self.listitem.getProperty('credit_id'))

		@ch.action('contextmenu', 150)
		@ch.action('contextmenu', 250)
		def context_menu(self):
			Utils.show_busy()
			if self.listitem.getProperty('dbid') and self.listitem.getProperty('dbid') != 0:
				dbid = self.listitem.getProperty('dbid')
			else:
				dbid = 0
			item_id = self.listitem.getProperty('id')
			if self.type == 'tv':
				imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'imdb_id')
				tvdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'tvdb_id')
			else:
				imdb_id = TheMovieDB.get_imdb_id_from_movie_id(item_id)

			if self.listitem.getProperty('TVShowTitle'):
				listitems = ['Play - TMDB Helper ']
			else:
				listitems = ['Play - TMDB Helper']

			listitems += ['Search item']
			#selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			Utils.hide_busy()
			if selection == 0:
				if self.type == 'tv':
					url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;tmdb_id=%s&amp;type=episode&amp;season=%s&amp;episode=%s' % (item_id, self.listitem.getProperty('season'), self.listitem.getProperty('episode'))
				else:
					url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;tmdb_id=%s&amp;type=movie' % (item_id)
				xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.play_from_button(url, listitem=None, window=self)

			if selection == 1:
				import urllib
				item_title = self.listitem.getProperty('TVShowTitle') or self.listitem.getProperty('Title')
				#item_title = urllib.parse.quote_plus(item_title)
				self.close()
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=search_string,str=%s)' % item_title)

		@ch.click(450)
		@ch.click(750)
		def open_image(self):
			listitems = next((v for (i, v) in self.listitems if i == self.control_id), None)
			index = self.control.getSelectedPosition()
			pos = wm.open_slideshow(listitems=listitems, index=index)
			self.control.selectItem(pos)

		@ch.click(350)
		def play_youtube_video(self):
			PLAYER.playtube(youtube_id=self.listitem.getProperty('youtube_id'), listitem=self.listitem, window=self)

		@ch.click(132)
		def show_plot(self):
			wm.open_textviewer(header='Overview', text=self.info['biography'], color=self.info['ImageColor'])
	return DialogActorInfo