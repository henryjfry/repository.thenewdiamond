import os, shutil, threading
import xbmc, xbmcgui, xbmcvfs, xbmcaddon
from resources.lib import Utils
from resources.lib import ImageTools
from resources.lib import TheMovieDB
from resources.lib.WindowManager import wm
from resources.lib.VideoPlayer import PLAYER
from resources.lib.OnClickHandler import OnClickHandler
from resources.lib.DialogBaseInfo import DialogBaseInfo
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib.library import trakt_add_movie

ch = OnClickHandler()

def get_movie_window(window_type):

	class DialogVideoInfo(DialogBaseInfo, window_type):

		def __init__(self, *args, **kwargs):
			super(DialogVideoInfo, self).__init__(*args, **kwargs)
			self.type = 'Movie'
			#imdb_id = TheMovieDB.get_imdb_id_from_movie_id(kwargs.get('id'))
			#xbmc.log(str(imdb_id)+'===>OPENINFO', level=xbmc.LOGINFO)
			#xbmc.log(str(kwargs.get('id'))+'===>OPENINFO', level=xbmc.LOGINFO)
			data = TheMovieDB.extended_movie_info(movie_id=kwargs.get('id'), dbid=self.dbid)
			imdb_recommendations = Utils.imdb_recommendations

			if 'IMDB' in str(imdb_recommendations):
				imdb_id = data[0]['imdb_id']
				#xbmc.log(str(data[0]['imdb_id'])+'===>OPENINFO', level=xbmc.LOGINFO)
				#if 'tt' not in str(imdb_id):
				#	imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(kwargs.get('id')), 'imdb_id')
				#xbmc.log(str(imdb_id)+'===>OPENINFO', level=xbmc.LOGINFO)
				imdb_similar = TheMovieDB.get_imdb_recommendations(imdb_id=imdb_id,return_items=True)
			else:
				imdb_similar = None
			if Utils.NETFLIX_VIEW == 'true':
				#super(DialogVideoInfo, self).__init__(*args, **kwargs)
				#self.type = 'Movie'
				#data = TheMovieDB.extended_movie_info(movie_id=kwargs.get('id'), dbid=self.dbid)
				if not data:
					return None
				self.info, self.data = data
				sets_thread = SetItemsThread(self.info['SetId'])
				sets_thread.start()
				if 'dbid' not in self.info:
					self.info['poster'] = Utils.get_file(self.info.get('poster', ''))
				sets_thread.join()
				self.setinfo = sets_thread.setinfo

				if imdb_recommendations == 'TMDB Only':
					self.data['similar'] = self.data['similar']
					self.data['similar'] = [i for i in self.data['similar'] if i['id'] not in sets_thread.id_list]
				elif imdb_recommendations == 'IMDB Only' and imdb_similar:
					self.data['similar'] = imdb_similar
					self.data['similar'] = [i for i in self.data['similar'] if i['id'] not in sets_thread.id_list]
				elif imdb_recommendations == 'TMDB then IMDB' and imdb_similar:
					for i in imdb_similar:
						if str(i['title']) not in str(self.data['similar']):
							self.data['similar'].append(i)
					self.data['similar'] = [i for i in self.data['similar'] if i['id'] not in sets_thread.id_list]
				elif imdb_recommendations == 'IMDB then TMDB' and imdb_similar:
					for i in self.data['similar']:
						if str(i['title']) not in str(imdb_similar):
							imdb_similar.append(i)
					self.data['similar'] = imdb_similar
					self.data['similar'] = [i for i in self.data['similar'] if i['id'] not in sets_thread.id_list]
				elif imdb_recommendations == 'IMDB + TMDB Sorted by Popularity' and imdb_similar:
					for i in imdb_similar:
						if str(i['title']) not in str(self.data['similar']):
							self.data['similar'].append(i)
					self.data['similar'] = [i for i in self.data['similar'] if i['id'] not in sets_thread.id_list]
					self.data['similar'] = sorted(self.data['similar'], key=lambda k: (k['Popularity'],k['Votes']), reverse=True)

				#if imdb_similar:
				#	for i in imdb_similar:
				#		if str(i) not in str(self.data['similar']):
				#			self.data['similar'].append(i)
				#self.data['similar'] = [i for i in self.data['similar'] if i['id'] not in sets_thread.id_list]
				#self.data['similar'] = sorted(self.data['similar'], key=lambda k: k['Popularity'], reverse=True)

				self.listitems = [
					(250, sets_thread.listitems),
					(1000, self.data['actors']),
					(750, Utils.merge_dict_lists(self.data['crew'])),
					(150, self.data['similar']),
					(550, self.data['studios']),
					(850, self.data['genres']),
					(1050, self.data['reviews']),
					(1250, self.data['images']),
					(1350, self.data['backdrops'])
					]
			else:
				#super(DialogVideoInfo, self).__init__(*args, **kwargs)
				#self.type = 'Movie'
				#data = TheMovieDB.extended_movie_info(movie_id=kwargs.get('id'), dbid=self.dbid)
				if not data:
					return None

				self.info, self.data = data
				sets_thread = SetItemsThread(self.info['SetId'])
				filter_thread = ImageTools.FilterImageThread(self.info.get('thumb', ''), 25)
				for thread in [sets_thread, filter_thread]:
					thread.start()
				if 'dbid' not in self.info:
					self.info['poster'] = Utils.get_file(self.info.get('poster', ''))
				sets_thread.join()
				self.setinfo = sets_thread.setinfo

				filter_thread.join()
				self.info['ImageFilter'] = filter_thread.image
				self.info['ImageColor'] = filter_thread.imagecolor
				filter_thread.terminate()

				#if imdb_similar:
				#	for i in imdb_similar:
				#		if str(i) not in str(self.data['similar']):
				#			self.data['similar'].append(i)
				#self.data['similar'] = [i for i in self.data['similar'] if i['id'] not in sets_thread.id_list]
				#self.data['similar'] = sorted(self.data['similar'], key=lambda k: k['Popularity'], reverse=True)

				if imdb_recommendations == 'TMDB Only':
					self.data['similar'] = self.data['similar']
					self.data['similar'] = [i for i in self.data['similar'] if i['id'] not in sets_thread.id_list]
				elif imdb_recommendations == 'IMDB Only' and imdb_similar:
					self.data['similar'] = imdb_similar
					self.data['similar'] = [i for i in self.data['similar'] if i['id'] not in sets_thread.id_list]
				elif imdb_recommendations == 'TMDB then IMDB' and imdb_similar:
					for i in imdb_similar:
						if str(i['title']) not in str(self.data['similar']):
							self.data['similar'].append(i)
					self.data['similar'] = [i for i in self.data['similar'] if i['id'] not in sets_thread.id_list]
				elif imdb_recommendations == 'IMDB then TMDB' and imdb_similar:
					for i in self.data['similar']:
						if str(i['title']) not in str(imdb_similar):
							imdb_similar.append(i)
					self.data['similar'] = imdb_similar
					self.data['similar'] = [i for i in self.data['similar'] if i['id'] not in sets_thread.id_list]
				elif imdb_recommendations == 'IMDB + TMDB Sorted by Popularity' and imdb_similar:
					for i in imdb_similar:
						if str(i['title']) not in str(self.data['similar']):
							self.data['similar'].append(i)
					self.data['similar'] = [i for i in self.data['similar'] if i['id'] not in sets_thread.id_list]
					self.data['similar'] = sorted(self.data['similar'], key=lambda k: (k['Popularity'],k['Votes']), reverse=True)

				self.listitems = [
					(250, sets_thread.listitems),
					(150, self.data['similar']),
					(1150, self.data['videos']),
					(1000, self.data['actors']),
					(750, Utils.merge_dict_lists(self.data['crew'])),
					(550, self.data['studios']),
					(650, TheMovieDB.merge_with_cert_desc(self.data['releases'], 'movie')),
					(850, self.data['genres']),
					(1050, self.data['reviews']),
					(1250, self.data['images']),
					(1350, self.data['backdrops'])
					]

		def onInit(self):
			super(DialogVideoInfo, self).onInit()
			Utils.pass_dict_to_skin(data=self.info, prefix='movie.', window_id=self.window_id)
			Utils.pass_dict_to_skin(data=self.setinfo, prefix='movie.set.', window_id=self.window_id)
			self.get_youtube_vids('%s %s, movie' % (self.info['Label'], self.info['year']))
			self.fill_lists()

		def onClick(self, control_id):
			super(DialogVideoInfo, self).onClick(control_id)
			ch.serve(control_id, self)

		def onAction(self, action):
			super(DialogVideoInfo, self).onAction(action)
			ch.serve_action(action, self.getFocusId(), self)

		@ch.click(1000)
		@ch.click(750)
		def open_actor_info(self):
			wm.open_actor_info(prev_window=self, actor_id=self.listitem.getProperty('id'))

		@ch.action('contextmenu', 750)
		@ch.action('contextmenu', 1000)
		def actor_context_menu(self):
			listitems = ['Search Person']
			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if selection == 0:
				self.close()
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=search_person,person=%s)' % self.listitem.getLabel())
			
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

			if xbmcaddon.Addon(addon_ID()).getSetting('RD_bluray_player') == 'true' or xbmcaddon.Addon(addon_ID()).getSetting('RD_bluray_player2')  == 'true':
				listitems += ['Eject/Load DVD']

			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			Utils.hide_busy()
			selection_text = listitems[selection]
			if selection == -1:
				selection_text = ''
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
				self.close()
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=search_string,str=%s)' % item_title)

			if selection_text == 'Eject/Load DVD':
				xbmc.executebuiltin('RunScript(%s,info=eject_load_dvd)' % (addon_ID()))


		@ch.click(150)
		@ch.click(250)
		def open_movie_info(self):
			if self.listitem.getProperty('media_type') == 'movie':
				wm.open_movie_info(prev_window=self, movie_id=self.listitem.getProperty('id'), dbid=self.listitem.getProperty('dbid'))
			else:
				wm.open_tvshow_info(prev_window=self, tmdb_id=self.listitem.getProperty('id'), dbid=self.listitem.getProperty('dbid'))

		@ch.click(550)
		def open_company_list(self):
			filters = [
				{
					'id': self.listitem.getProperty('id'),
					'type': 'with_companies',
					'typelabel': 'Studios',
					'label': self.listitem.getLabel()
				}]
			wm.open_video_list(prev_window=self, filters=filters)

		@ch.click(1050)
		def show_review(self):
			author = self.listitem.getProperty('author')
			text = '[B]%s[/B][CR]%s' % (author, Utils.clean_text(self.listitem.getProperty('content')))
			wm.open_textviewer(header='Plot', text=text, color='FFFFFFFF')

		@ch.click(850)
		def open_genre_list(self):
			filters = [
				{
					'id': self.listitem.getProperty('id'),
					'type': 'with_genres',
					'typelabel': 'Genres',
					'label': self.listitem.getLabel()
				}]
			wm.open_video_list(prev_window=self, filters=filters)

		@ch.click(650)
		def open_cert_list(self):
			filters = [
				{
					'id': self.listitem.getProperty('iso_3166_1'),
					'type': 'certification_country',
					'typelabel': 'Certification country',
					'label': self.listitem.getProperty('iso_3166_1')
				},
				{
					'id': self.listitem.getProperty('certification'),
					'type': 'certification',
					'typelabel': 'Certification',
					'label': self.listitem.getProperty('certification')
				},
				{
					'id': self.listitem.getProperty('year'),
					'type': 'year',
					'typelabel': 'Year',
					'label': self.listitem.getProperty('year')
				}]
			wm.open_video_list(prev_window=self, filters=filters)

		@ch.click(120)
		def search_in_meta_by_title(self):
			url =  'plugin://plugin.video.themoviedb.helper/?info=details&amp;type=movie&amp;query=%s' % self.info.get('title', '')
			self.close()
			xbmc.executebuiltin('ActivateWindow(videos,%s,return)' % url)

		@ch.click(132)
		def show_plot(self):
			wm.open_textviewer(header='Plot', text=self.info['Plot'], color='FFFFFFFF')

		@ch.click(8)
		def play_movie(self):
			if self.dbid and int(self.dbid) > 0:
				dbid = self.dbid
				url = ''
				PLAYER.play_from_button(url, listitem=None, window=self, type='movieid', dbid=dbid)
			else:
				url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=movie&amp;tmdb_id=%s' % self.info.get('id', '')
				#PLAYER.play_from_button(url, listitem=None, window=self)
				Utils.hide_busy()
				PLAYER.play_from_button(url, listitem=None, window=self, type='movieid', dbid=0)

		@ch.action('contextmenu', 8)
		def play_movie_choose_player(self):
			if self.dbid and int(self.dbid) > 0:
				dbid = self.dbid
				url = ''
				PLAYER.play_from_button(url, listitem=None, window=self, type='movieid', dbid=dbid)
			else:
				url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=movie&amp;tmdb_id=%s' % self.info.get('id', '')
				PLAYER.play_from_button(url, listitem=None, window=self, type='movieid', dbid=dbid)

		@ch.click(445)
		def show_manage_dialog(self):
			manage_list = []
			manage_list.append(["Diamond Info's settings", 'Addon.OpenSettings("'+str(addon_ID())+'")'])
			manage_list.append(["TmdbHelper Context", 'RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type=movie,tmdb_id='+str(self.info.get('id', ''))+')'])
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
			xbmc.executebuiltin('RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type=movie,tmdb_id='+str(self.info.get('id', ''))+')')
			return

		@ch.click(18)
		def add_movie_to_library(self):
			if xbmcgui.Dialog().yesno(str(addon_ID_short()), 'Add [B]%s[/B] to library?' % self.info['title']):
				trakt_add_movie(self.info['id'],'Add')
				Utils.after_add(type='movie')
				Utils.notify(header='[B]%s[/B] added to library' % self.info['title'], message='Exit & re-enter to refresh', icon=self.info['poster'], time=1000, sound=False)

		@ch.click(19)
		def remove_movie_from_library(self):
			if xbmcgui.Dialog().yesno(str(addon_ID_short()), 'Remove [B]%s[/B] from library?' % self.info['title']):
				if os.path.exists(xbmcvfs.translatePath('%s%s/' % (Utils.DIAMONDPLAYER_MOVIE_FOLDER, self.info['id']))):
					Utils.get_kodi_json(method='VideoLibrary.RemoveMovie', params='{"movieid": %d}' % int(self.info['dbid']))
					shutil.rmtree(xbmcvfs.translatePath('%s%s/' % (Utils.DIAMONDPLAYER_MOVIE_FOLDER, self.info['id'])))
					trakt_add_movie(self.info['id'],'Remove')
					Utils.after_add(type='movie')
					Utils.notify(header='Removed [B]%s[/B] from library' % self.info.get('title', ''), message='Exit & re-enter to refresh', icon=self.info['poster'], time=1000, sound=False)

		@ch.click(350)
		@ch.click(1150)
		def play_youtube_video(self):
			PLAYER.playtube(self.listitem.getProperty('youtube_id'), listitem=self.listitem, window=self)

		@ch.click(28)
		def play_movie_trailer_button(self):
			TheMovieDB.play_movie_trailer(self.info['id'])

		@ch.click(29)
		def stop_movie_trailer_button(self):
			xbmc.executebuiltin('PlayerControl(Stop)')

	class SetItemsThread(threading.Thread):

		def __init__(self, set_id=''):
			threading.Thread.__init__(self)
			self.set_id = set_id

		def run(self):
			if self.set_id:
				self.listitems, self.setinfo = TheMovieDB.get_set_movies(self.set_id)
				self.id_list = [item['id'] for item in self.listitems]
			else:
				self.id_list = []
				self.listitems = []
				self.setinfo = {}

	return DialogVideoInfo
