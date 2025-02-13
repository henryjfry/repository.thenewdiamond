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
#from resources.lib.library import trakt_add_tv
#from resources.lib.library import trakt_add_movie
from resources.lib.library import next_episode_show
from resources.lib.library import trakt_next_episode_normal
from resources.lib.library import trakt_next_episode_rewatch
#from resources.lib.library import trakt_calendar_hide_show

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
			#	imdb_similar = TheMovieDB.get_imdb_recommendations(imdb_id=imdb_id,return_items=True)
			#else:
			#	imdb_similar = None
				imdbs_thread = IMDB_Thread(imdb_id)
				imdbs_thread.start()
				imdbs_thread.join()
				imdb_similar = imdbs_thread.imdb_similar
			else:
				imdb_similar = None

			self.tmdb_id = kwargs.get('tmdb_id', False)

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
					if str(i['title']) not in str(self.data['similar']):
						self.data['similar'].append(i)
			elif imdb_recommendations == 'IMDB then TMDB' and imdb_similar:
				for i in self.data['similar']:
					if str(i['title']) not in str(imdb_similar):
						imdb_similar.append(i)
				self.data['similar'] = imdb_similar
			elif imdb_recommendations == 'IMDB + TMDB Sorted by Popularity' and imdb_similar:
				for i in imdb_similar:
					if str(i['title']) not in str(self.data['similar']):
						self.data['similar'].append(i)
				self.data['similar'] = sorted(self.data['similar'], key=lambda k: (k['Popularity'],k['Votes']), reverse=True)

			movies = TheMovieDB.get_vod_alltv()
			for i in reversed(self.data['similar']):
				match = False
				idx = self.data['similar'].index(i)
				for x in movies:
					if str(i['id']) == x['tmdb']:
						self.data['similar'][idx]['series_id'] = x['series_id']
						match = True
						break
				if match == False:
					self.data['similar'].pop(idx)

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

		@ch.action('play', 250)
		def context_play(self):
			tmdb_id = self.info['id']
			self.info['media_type'] = 'season'
			Utils.context_play(window=self,tmdb_id = self.tmdb_id)

		@ch.action('play', 150)
		@ch.action('play', 9)
		def context_play(self):
			try: 
				tmdb_id = self.listitem.getProperty('id')
			except: 
				tmdb_id = self.info['id']
				self.info['media_type'] = 'tvshow'
			Utils.context_play(window=self,tmdb_id = self.tmdb_id)

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
				listitems = ['Play Trakt Next Episode']
				listitems += ['Play Trakt Next Episode (Rewatch)']
			else:
				listitems = ['Play']

			if xbmcaddon.Addon(addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			selection_text = listitems[selection]
			if selection == -1:
				return

			if selection_text == 'Search item':
				item_title = self.listitem.getProperty('TVShowTitle') or self.listitem.getProperty('Title')
				self.close()
				xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=search_string,str=%s)' % item_title)


			if selection_text == 'Play first episode' or selection_text == 'Play':
				if self.listitem.getProperty('TVShowTitle'):
					#url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % item_id
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					#PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
					PLAYER.prepare_play_VOD_episode(tmdb = item_id, series_id=None, search_str = None,episode=1, season=1, window=self)
				else:
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					PLAYER.prepare_play_VOD_movie(tmdb = item_id, title = None, stream_id=None, search_str = None, window=self)

			if selection_text == 'Play Trakt Next Episode':
				tmdb_id, season, episode = trakt_next_episode_normal(tmdb_id_num=item_id)
				xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.prepare_play_VOD_episode(tmdb = tmdb_id, series_id=None, search_str = None,episode=episode, season=season, window=self)

			if selection_text == 'Play Trakt Next Episode (Rewatch)':
				tmdb_id, season, episode = trakt_next_episode_rewatch(tmdb_id_num=item_id)
				xbmc.executebuiltin('Dialog.Close(all,true)')
				PLAYER.prepare_play_VOD_episode(tmdb = tmdb_id, series_id=None, search_str = None,episode=episode, season=season, window=self)


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
				#url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=%s&amp;episode=1' % (self.info['id'], str(self.listitem.getProperty('season')))
				#xbmc.executebuiltin('RunPlugin(%s)' % url)
				xbmc.executebuiltin('Dialog.Close(all,true)')
				#PLAYER.play_from_button(url, listitem=None, window=self)
				PLAYER.prepare_play_VOD_episode(tmdb = self.info['id'], series_id=None, search_str = None,episode=1, season=self.listitem.getProperty('season'), window=self)

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
			manage_list.append(["Xtreme VOD's settings", 'Addon.OpenSettings("'+str(addon_ID())+'")'])
			#manage_list.append(["TmdbHelper Context", 'RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type=movie,tmdb_id='+str(self.info.get('id', ''))+')'])
			#manage_list.append(["TmdbHelper settings", 'Addon.OpenSettings("plugin.video.themoviedb.helper")'])
			#manage_list.append(["YouTube's settings", 'Addon.OpenSettings("plugin.video.youtube")'])
			import xbmcaddon
			#settings_user_config = xbmcaddon.Addon(addon_ID()).getSetting('settings_user_config')
			#if settings_user_config == 'Settings Selection Menu':
			#	selection = xbmcgui.Dialog().select(heading='Settings', list=[i[0] for i in manage_list])
			#else:
			#	selection = 1
			selection = 0
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
			if self.type == 'tv' or self.info['TVShowTitle']:
					listitems += ['Play Trakt Next Episode']
					listitems += ['Play Trakt Next Episode (Rewatch)']

			listitems += ['Trailer']

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
					#url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % item_id
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					#PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
					PLAYER.prepare_play_VOD_episode(tmdb = item_id, series_id=None, search_str = None,episode=1, season=1, window=self)
				else:
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					#PLAYER.play_from_button(url, listitem=None, window=self, type='movieid', dbid=dbid)
					PLAYER.prepare_play_VOD_movie(tmdb = item_id, title = None, stream_id=None, search_str = None, window=self)


			if selection_text == 'Play Trakt Next Episode':
				tmdb_id, season, episode = trakt_next_episode_normal(tmdb_id_num=item_id)
				#PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
				PLAYER.prepare_play_VOD_episode(tmdb = tmdb_id, series_id=None, search_str = None,episode=episode, season=season, window=self)

			if selection_text == 'Play Trakt Next Episode (Rewatch)':
				tmdb_id, season, episode = trakt_next_episode_rewatch(tmdb_id_num=item_id)
				#PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
				PLAYER.prepare_play_VOD_episode(tmdb = tmdb_id, series_id=None, search_str = None,episode=episode, season=season, window=self)


			if selection_text == 'Trailer':
				if self.info['TVShowTitle']:
					url = 'plugin://'+str(addon_ID())+'?info=playtvtrailer&&id=' + str(item_id)
				else:
					url = 'plugin://'+str(addon_ID())+'?info=playtrailer&&id=' + str(item_id)
				PLAYER.play(url, listitem=None, window=self)

		#@ch.click(9)
		def play_tvshow(self):
			#url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % self.info['id']
			#xbmc.executebuiltin('RunPlugin(%s)' % url)
			PLAYER.prepare_play_VOD_episode(tmdb = self.info['id'], series_id=None, search_str = None,episode=1, season=1, window=self)

		#@ch.action('contextmenu', 9)
		def play_tvshow_choose_player(self):
			#url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % self.info['id']
			#xbmc.executebuiltin('RunPlugin(%s)' % url)
			PLAYER.prepare_play_VOD_episode(tmdb = self.info['id'], series_id=None, search_str = None,episode=1, season=1, window=self)

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

	class IMDB_Thread(threading.Thread):

		def __init__(self, imdb_id=''):
			threading.Thread.__init__(self)
			self.imdb_id = imdb_id
			self.imdb_similar = None

		def run(self):
			if self.imdb_id:
				imdb_similar = TheMovieDB.get_imdb_recommendations(imdb_id=self.imdb_id,return_items=True)
				self.imdb_similar = imdb_similar
			else:
				self.imdb_similar = []

	return DialogTVShowInfo