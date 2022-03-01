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
from resources.lib.library import basedir_tv_path
from resources.lib.library import basedir_movies_path
from resources.lib.library import trakt_add_tv
from resources.lib.library import trakt_add_movie
from resources.lib.library import next_episode_show
from resources.lib.library import trakt_next_episode_normal
from resources.lib.library import trakt_next_episode_rewatch
from resources.lib.library import trakt_calendar_hide_show

ch = OnClickHandler()

def get_tvshow_window(window_type):

	class DialogTVShowInfo(DialogBaseInfo, window_type):

		def __init__(self, *args, **kwargs):
			super(DialogTVShowInfo, self).__init__(*args, **kwargs)
			self.type = 'TVShow'
			data = TheMovieDB.extended_tvshow_info(tvshow_id=kwargs.get('tmdb_id', False), dbid=self.dbid)
			imdb_recommendations = Utils.imdb_recommendations
			if 'IMDB' in str(imdb_recommendations):
				imdb_id = data[0]['imdb_id']
				if 'tt' not in str(imdb_id):
					imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(kwargs.get('tmdb_id', False)), 'imdb_id')
				imdb_similar = TheMovieDB.get_imdb_recommendations(imdb_id=imdb_id,return_items=True)
			else:
				imdb_similar = None

			if Utils.NETFLIX_VIEW == 'true':
				#super(DialogTVShowInfo, self).__init__(*args, **kwargs)
				#self.type = 'TVShow'
				#data = TheMovieDB.extended_tvshow_info(tvshow_id=kwargs.get('tmdb_id', False), dbid=self.dbid)
				if not data:
					return None
				self.info, self.data = data
				if 'dbid' not in self.info:
					self.info['poster'] = Utils.get_file(self.info.get('poster', ''))


				if imdb_recommendations == 'TMDB Only':
					self.data['similar'] = self.data['similar']
				elif imdb_recommendations == 'IMDB Only' and imdb_similar:
					self.data['similar'] = imdb_similar
				elif imdb_recommendations == 'TMDB then IMDB' and imdb_similar:
					for i in imdb_similar:
						if str(i) not in str(self.data['similar']):
							self.data['similar'].append(i)
				elif imdb_recommendations == 'IMDB then TMDB' and imdb_similar:
					for i in self.data['similar']:
						if str(i) not in str(imdb_similar):
							imdb_similar.append(i)
					self.data['similar'] = imdb_similar
				elif imdb_recommendations == 'IMDB + TMDB Sorted by Popularity' and imdb_similar:
					for i in imdb_similar:
						if str(i) not in str(self.data['similar']):
							self.data['similar'].append(i)
					self.data['similar'] = sorted(self.data['similar'], key=lambda k: k['Popularity'], reverse=True)

				self.listitems = [
					(250, self.data['seasons']),
					(150, self.data['similar']),
					(1000, self.data['actors']),
					(750, self.data['crew']),
					(550, self.data['studios']),
					(1450, self.data['networks']),
					(850, self.data['genres']),
					(1250, self.data['images']),
					(1350, self.data['backdrops'])
					]
			else:
				#super(DialogTVShowInfo, self).__init__(*args, **kwargs)
				#self.type = 'TVShow'
				#data = TheMovieDB.extended_tvshow_info(tvshow_id=kwargs.get('tmdb_id', False), dbid=self.dbid)
				if not data:
					return None
				self.info, self.data = data
				if 'dbid' not in self.info:
					self.info['poster'] = Utils.get_file(self.info.get('poster', ''))
				self.info['ImageFilter'], self.info['ImageColor'] = ImageTools.filter_image(input_img=self.info.get('thumb', ''), radius=25)
				"""
				try:
					filter_thread = ImageTools.FilterImageThread(self.data['backdrops'][0]['thumb'], 25)
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
				if imdb_recommendations == 'TMDB Only':
					self.data['similar'] = self.data['similar']
				elif imdb_recommendations == 'IMDB Only' and imdb_similar:
					self.data['similar'] = imdb_similar
				elif imdb_recommendations == 'TMDB then IMDB' and imdb_similar:
					for i in imdb_similar:
						if str(i) not in str(self.data['similar']):
							self.data['similar'].append(i)
				elif imdb_recommendations == 'IMDB then TMDB' and imdb_similar:
					for i in self.data['similar']:
						if str(i) not in str(imdb_similar):
							imdb_similar.append(i)
					self.data['similar'] = imdb_similar
				elif imdb_recommendations == 'IMDB + TMDB Sorted by Popularity' and imdb_similar:
					for i in imdb_similar:
						if str(i) not in str(self.data['similar']):
							self.data['similar'].append(i)
					self.data['similar'] = sorted(self.data['similar'], key=lambda k: k['Popularity'], reverse=True)

				self.listitems = [
					(250, self.data['seasons']),
					(150, self.data['similar']),
					(1150, self.data['videos']),
					(1000, self.data['actors']),
					(750, self.data['crew']),
					(550, self.data['studios']),
					(1450, self.data['networks']),
					(650, TheMovieDB.merge_with_cert_desc(self.data['certifications'], 'tv')),
					(850, self.data['genres']),
					(1250, self.data['images']),
					(1350, self.data['backdrops'])
					]

		def onInit(self):
			self.get_youtube_vids('%s tv' % self.info['title'])
			super(DialogTVShowInfo, self).onInit()
			Utils.pass_dict_to_skin(data=self.info, prefix='movie.', window_id=self.window_id)
			self.fill_lists()

		def onClick(self, control_id):
			super(DialogTVShowInfo, self).onClick(control_id)
			ch.serve(control_id, self)

		def onAction(self, action):
			super(DialogTVShowInfo, self).onAction(action)
			ch.serve_action(action, self.getFocusId(), self)

		@ch.click(120)
		def browse_tvshow(self):
			url = 'plugin://plugin.video.themoviedb.helper/?info=seasons&amp;tmdb_id='+ str(self.info['id']) +'&amp;tmdb_type=tv'
			self.close()
			xbmc.executebuiltin('ActivateWindow(videos,%s,return)' % url)

		@ch.action('contextmenu', 150)
		def right_click_similar(self):
			item_id = self.listitem.getProperty('id')
			if self.listitem.getProperty('dbid') and self.listitem.getProperty('dbid') != 0:
				dbid = self.listitem.getProperty('dbid')
			else:
				dbid = 0
			if self.listitem.getProperty('TVShowTitle'):
				imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'imdb_id')
				tvdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'tvdb_id')
			else:
				imdb_id = TheMovieDB.get_imdb_id_from_movie_id(item_id)
			if self.listitem.getProperty('TVShowTitle'):
				if self.listitem.getProperty('dbid'):
					listitems = ['Play Kodi Next Episode']
					listitems += ['Play Trakt Next Episode']
					listitems += ['Play first episode']
				else:
					listitems = ['Play Trakt Next Episode']
					listitems += ['Play Trakt Next Episode (Rewatch)']
			else:
				listitems = ['Play']

			if self.listitem.getProperty('dbid'):
				listitems += ['Remove from library']
			else:
				listitems += ['Add to library']
			if self.listitem.getProperty('TVShowTitle'):
				listitems += ['Hide on Trakt Calendar']
				listitems += ['Unhide on Trakt Calendar']
			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			selection_text = listitems[selection]
			if selection == -1:
				return
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
			if selection_text == 'Play first episode' or selection_text == 'Play':
				if self.listitem.getProperty('TVShowTitle'):
					url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % item_id
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
				else:
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					if self.listitem.getProperty('dbid'):
						dbid = self.listitem.getProperty('dbid')
						url = ''
						PLAYER.play_from_button(url, listitem=None, window=self, type='movieid', dbid=dbid)
					else:
						dbid = 0
						url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=movie&amp;tmdb_id=%s' % item_id
						PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
			if selection_text == 'Play Kodi Next Episode':
				url = next_episode_show(tmdb_id_num=item_id,dbid_num=dbid)
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)

			if selection_text == 'Play Trakt Next Episode':
				url = trakt_next_episode_normal(tmdb_id_num=item_id)
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)

			if selection_text == 'Play Trakt Next Episode (Rewatch)':
				url = trakt_next_episode_rewatch(tmdb_id_num=item_id)
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
			
			if selection_text == 'Unhide on Trakt Calendar':
				response_collect = trakt_calendar_hide_show(tmdb_id_num=item_id,unhide=True)
			if selection_text == 'Hide on Trakt Calendar':
				response_collect = trakt_calendar_hide_show(tmdb_id_num=item_id,unhide=False)

		@ch.click(750)
		@ch.click(1000)
		def credit_dialog(self):
			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu(['Show actor TV show appearances','Show Actor Information'])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=['Show actor TV show appearances','Show Actor Information'])
			if selection == 0:
				self.open_credit_dialog(self.listitem.getProperty('credit_id'))
			if selection == 1:
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

		@ch.click(150)
		def open_tvshow_dialog(self):
			if self.listitem.getProperty('media_type') == 'movie':
				wm.open_movie_info(prev_window=self, movie_id=self.listitem.getProperty('id'), dbid=self.listitem.getProperty('dbid'))
			else:
				wm.open_tvshow_info(prev_window=self, tmdb_id=self.listitem.getProperty('id'), dbid=self.listitem.getProperty('dbid'))

		@ch.click(250)
		def open_season_dialog(self):
			wm.open_season_info(prev_window=self, tvshow_id=self.info['id'], season=self.listitem.getProperty('season'), tvshow=self.info['title'])

		@ch.action('contextmenu', 250)
		def season_context_menu(self):
			listitems = ['Play Season']
			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if selection == 0:
				self.close()
				url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % self.info['id']
				xbmc.executebuiltin('RunPlugin(%s)' % url)

		@ch.click(550)
		def open_company_info(self):
			filters = [
				{
					'id': self.listitem.getProperty('id'),
					'type': 'with_companies',
					'typelabel': 'Studios',
					'label': self.listitem.getLabel()#.decode('utf-8')
				}]
			wm.open_video_list(prev_window=self, filters=filters)

		@ch.click(850)
		def open_genre_info(self):
			filters = [
				{
					'id': self.listitem.getProperty('id'),
					'type': 'with_genres',
					'typelabel': 'Genres',
					'label': self.listitem.getLabel()#.decode('utf-8')
				}]
			wm.open_video_list(prev_window=self, filters=filters, media_type='tv')

		@ch.click(1450)
		def open_network_info(self):
			filters = [
				{
					'id': self.listitem.getProperty('id'),
					'type': 'with_networks',
					'typelabel': 'Networks',
					'label': self.listitem.getLabel()#.decode('utf-8')
				}]
			wm.open_video_list(prev_window=self, filters=filters, media_type='tv')

		@ch.click(445)
		def show_manage_dialog(self):
			manage_list = []
			manage_list.append([str(addon_ID_short())+ ' Settings', 'Addon.OpenSettings("'+str(addon_ID())+'")'])
			manage_list.append(["TMDBHelper Context", 'RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type=tv,tmdb_id='+str(self.info['id'])+')'])
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
			xbmc.executebuiltin('RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type=tv,tmdb_id='+str(self.info['id'])+')')
			return

		@ch.click(6002)
		def open_list(self):
			index = xbmcgui.Dialog().select(heading='Choose list', list=['Starred TV shows', 'Rated TV shows'])

		@ch.click(6006)
		def open_rated_items(self):
			wm.open_video_list(prev_window=self, mode='rating', media_type='tv')

		@ch.click(9)
		@ch.action('contextmenu', 9)
		def context_menu(self):
			try:
				if self.info['dbid'] and self.info['dbid'] != 0:
					dbid = self.info['dbid']
				else:
					dbid = 0
			except:
				self.info['dbid'] = 0
				dbid = 0
			item_id = self.info['id']
			try:
				if self.type == 'tv':
					imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'imdb_id')
					tvdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'tvdb_id')
				else:
					imdb_id = TheMovieDB.get_imdb_id_from_movie_id(item_id)
			except:
				imdb_id = None
			if self.info['TVShowTitle']:
				listitems = ['Play first episode']
			else:
				listitems = ['Play']
			if self.info['dbid']:
				listitems += ['Remove from library']
				if self.type == 'tv' or self.info['TVShowTitle']:
					listitems += ['Play Kodi Next Episode']
					listitems += ['Play Trakt Next Episode']
			else:
				listitems += ['Add to library']
				if self.type == 'tv' or self.info['TVShowTitle']:
					listitems += ['Play Trakt Next Episode']
					listitems += ['Play Trakt Next Episode (Rewatch)']
			listitems += ['Search item']
			listitems += ['Trailer']
			if self.info['TVShowTitle']:
				listitems += ['Hide on Trakt Calendar']
				listitems += ['Unhide on Trakt Calendar']
			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			selection_text = listitems[selection]
			if selection == -1:
				return

			xbmcgui.Window(10000).setProperty('tmdbhelper_tvshow.poster', str(self.info['poster']))
			if selection_text == 'Play first episode' or selection_text == 'Play':
				if self.info['TVShowTitle']:
					url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % item_id
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
				else:
					if self.info['dbid']:
						dbid = self.info['dbid']
						url = ''
					else:
						dbid = 0
						url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=movie&amp;tmdb_id=%s' % item_id
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					PLAYER.play_from_button(url, listitem=None, window=self, type='movieid', dbid=dbid)
			if selection_text == 'Remove from library' or selection_text == 'Add to library':
				if self.info['TVShowTitle']:
					TVLibrary = basedir_tv_path()
					if dbid > 0:
						Utils.get_kodi_json(method='VideoLibrary.RemoveTVShow', params='{"tvshowid": %s}' % dbid)
						if os.path.exists(xbmcvfs.translatePath('%s%s/' % (TVLibrary, tvdb_id))):
							shutil.rmtree(xbmcvfs.translatePath('%s%s/' % (TVLibrary, tvdb_id)))
							
							trakt_add_tv(item_id,'Remove')
							Utils.after_add(type='tv')
							Utils.notify(header='[B]%s[/B]' % self.info['TVShowTitle'], message='Removed from library', icon=self.info['poster'], time=1000, sound=False)
							xbmc.sleep(250)
							self.update(force_update=True)
							self.getControl(500).selectItem(self.position)
					else:
						if xbmcgui.Dialog().yesno(str(addon_ID_short()), 'Add [B]%s[/B] to library?' % self.info['TVShowTitle']):
							trakt_add_tv(item_id,'Add')
							Utils.after_add(type='tv')
							Utils.notify(header='[B]%s[/B] added to library' % self.info['TVShowTitle'], message='Exit & re-enter to refresh', icon=self.info['poster'], time=1000, sound=False)
				else:
					if dbid > 0:
						if xbmcgui.Dialog().yesno(str(addon_ID_short()), 'Remove [B]%s[/B] from library?' % self.info['title']):
							Utils.get_kodi_json(method='VideoLibrary.RemoveMovie', params='{"movieid": %s}' % dbid)
							MovieLibrary = basedir_movies_path()
							if os.path.exists(xbmcvfs.translatePath('%s%s/' % (MovieLibrary, item_id))):
								shutil.rmtree(xbmcvfs.translatePath('%s%s/' % (MovieLibrary, item_id)))
								
								trakt_add_movie(item_id,'Remove')
								Utils.after_add(type='movie')
								Utils.notify(header='[B]%s[/B]' % self.info['title'], message='Removed from library', icon=self.info['poster'], time=1000, sound=False)
								xbmc.sleep(250)
								self.update(force_update=True)
								self.getControl(500).selectItem(self.position)
					else:
						if xbmcgui.Dialog().yesno(str(addon_ID_short()), 'Add [B]%s[/B] to library?' % self.info['title']):
							trakt_add_movie(item_id,'Add')
							Utils.after_add(type='movie')
							Utils.notify(header='[B]%s[/B] added to library' % self.info['title'], message='Exit & re-enter to refresh', icon=self.info['poster'], time=1000, sound=False)

			if selection_text == 'Play Kodi Next Episode':
				url = next_episode_show(tmdb_id_num=item_id,dbid_num=dbid)
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)

			if selection_text == 'Play Trakt Next Episode':
				url = trakt_next_episode_normal(tmdb_id_num=item_id)
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)

			if selection_text == 'Play Trakt Next Episode (Rewatch)':
				url = trakt_next_episode_rewatch(tmdb_id_num=item_id)
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)

			if selection_text == 'Search item':
				item_title = self.info['TVShowTitle'] or self.info['Title']
				self.close()
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=search_string,str=%s)' % item_title)

			if selection_text == 'Trailer':
				if self.info['TVShowTitle']:
					url = 'plugin://'+str(addon_ID())+'?info=playtvtrailer&&id=' + str(item_id)
				else:
					url = 'plugin://'+str(addon_ID())+'?info=playtrailer&&id=' + str(item_id)
				PLAYER.play(url, listitem=None, window=self)

			if selection_text == 'Unhide on Trakt Calendar':
				response_collect = trakt_calendar_hide_show(tmdb_id_num=item_id,unhide=True)
				xbmc.log(str(response_collect)+'===>OPEN_INFO', level=xbmc.LOGINFO)
			if selection_text == 'Hide on Trakt Calendar':
				response_collect = trakt_calendar_hide_show(tmdb_id_num=item_id,unhide=False)
				xbmc.log(str(response_collect)+'===>OPEN_INFO', level=xbmc.LOGINFO)


		#@ch.click(9)
		def play_tvshow(self):
			url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % self.info['id']
			xbmc.executebuiltin('RunPlugin(%s)' % url)

		#@ch.action('contextmenu', 9)
		def play_tvshow_choose_player(self):
			url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % self.info['id']
			xbmc.executebuiltin('RunPlugin(%s)' % url)

		@ch.click(20)
		def add_tvshow_to_library(self):
			if xbmcgui.Dialog().yesno(str(addon_ID_short()), 'Add [B]%s[/B] to library?' % self.info['TVShowTitle']):
				trakt_add_tv(self.info['id'],'Add')
				Utils.after_add(type='tv')
				Utils.notify(header='[B]%s[/B] added to library' % self.info['TVShowTitle'], message='Exit & re-enter to refresh', icon=self.info['poster'], time=1000, sound=False)

		@ch.click(21)
		def remove_tvshow_from_library(self):
			if xbmcgui.Dialog().yesno(str(addon_ID_short()), 'Remove [B]%s[/B] from library?' % self.info['TVShowTitle']):
				if os.path.exists(xbmcvfs.translatePath('%s%s/' % (Utils.DIAMONDPLAYER_TV_FOLDER, self.info['tvdb_id']))):
					Utils.get_kodi_json(method='VideoLibrary.RemoveTVShow', params='{"tvshowid": %s}' % int(self.info['dbid']))
					shutil.rmtree(xbmcvfs.translatePath('%s%s/' % (Utils.DIAMONDPLAYER_TV_FOLDER, self.info['tvdb_id'])))
					trakt_add_tv(item_id,'Remove')
					Utils.after_add(type='tv')
					Utils.notify(header='Removed [B]%s[/B] from library' % self.info['TVShowTitle'], message='Exit & re-enter to refresh', icon=self.info['poster'], time=1000, sound=False)

		@ch.click(132)
		def open_text(self):
			wm.open_textviewer(header='Overview', text=self.info['Plot'], color='FFFFFFFF')

		@ch.click(350)
		@ch.click(1150)
		def play_youtube_video(self):
			PLAYER.playtube(self.listitem.getProperty('youtube_id'), listitem=self.listitem, window=self)

		@ch.click(28)
		def play_tv_trailer_button(self):
			TheMovieDB.play_tv_trailer(self.info['id'])

		@ch.click(29)
		def stop_tv_trailer_button(self):
			xbmc.executebuiltin('PlayerControl(Stop)')

	return DialogTVShowInfo