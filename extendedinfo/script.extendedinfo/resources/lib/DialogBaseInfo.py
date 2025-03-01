import xbmc, xbmcgui
from resources.lib import Utils
from resources.lib import YouTube
from resources.lib import TheMovieDB
from resources.lib.WindowManager import wm
from resources.lib.OnClickHandler import OnClickHandler
from resources.lib.library import addon_ID_short

ch = OnClickHandler()

class DialogBaseInfo(object):

	ACTION_PREVIOUS_MENU = [92, 9]
	ACTION_EXIT_SCRIPT = [13, 10]

	def __init__(self, *args, **kwargs):
		super(DialogBaseInfo, self).__init__(*args, **kwargs)
		self.dbid = kwargs.get('dbid')
		self.bouncing = False
		self.data = None
		self.yt_listitems = []
		self.total_items = 0
		self.position = 0
		self.info = {}

	def onInit(self, *args, **kwargs):
		super(DialogBaseInfo, self).onInit()
		xbmcgui.Window(10000).setProperty('ImageColor', self.info.get('ImageColor', ''))
		self.window = xbmcgui.Window(self.window_id)
		self.window.setProperty('type', self.type)
		xbmcgui.Window(10000).setProperty('diamondinfo_fanart', self.info.get('fanart', ''))
		if Utils.trakt_kodi_mode == 'Trakt Only':
			xbmcgui.Window(self.window_id).setProperty('trakt_only', 'true')
		else:
			xbmcgui.Window(self.window_id).clearProperty('trakt_only')
		try: clearlogo = TheMovieDB.get_fanart_clearlogo(tmdb_id=self.info['tmdb_id'],media_type=self.info['media_type'])
		except: clearlogo = ''
		xbmcgui.Window(self.window_id).setProperty('movie.logo', str(clearlogo))
		#xbmcgui.Window(10000).setProperty('movie.tmdbid', str(self.info['tmdb_id']))
		xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_fanart', self.info.get('fanart', ''))
		xbmc.sleep(500)


	@ch.action('left', '*')
	@ch.action('right', '*')
	@ch.action('up', '*')
	@ch.action('down', '*')
	def save_position(self):
		self.focus_id = self.getFocusId()
		try: self.position = self.getControl(self.focus_id).getSelectedPosition()
		except: self.position = xbmc.getInfoLabel("Container.Position")
		xbmcgui.Window(10000).setProperty('focus_id', str(self.focus_id))
		try:
			int_test = int(self.position)
			xbmcgui.Window(10000).setProperty('position', str(self.position))
		except:
			self.position = 'No Position'
			xbmcgui.Window(10000).setProperty('position', str('No Position'))
		wm.position = self.position
		wm.focus_id = self.focus_id

	def onAction(self, action):
		#xbmcgui.Window(10000).setProperty('focus_id', str(self.focus_id))
		#xbmcgui.Window(10000).setProperty('position', str(self.position))
		self.save_position()
		ch.serve_action(action, self.getFocusId(), self)

	def onClick(self, control_id):
		#xbmcgui.Window(10000).setProperty('focus_id', str(self.focus_id))
		#xbmcgui.Window(10000).setProperty('position', str(self.position))
		self.save_position()
		ch.serve(control_id, self)

	def onFocus(self, control_id):
		self.focus_id = self.getFocusId()
		self.save_position()
		if control_id == 20000:
			if not self.bouncing:
				self.bounce('up')
			self.setFocusId(self.last_focus)
			self.last_focus = control_id
		elif control_id == 20001:
			if not self.bouncing:
				self.bounce('down')
			self.setFocusId(self.last_focus)
			self.last_focus = control_id
		else:
			self.last_focus = control_id

	@Utils.run_async
	def bounce(self, identifier):
		self.bouncing = True
		self.window.setProperty('Bounce.' + identifier, 'true')
		xbmc.sleep(100)
		self.window.clearProperty('Bounce.' + identifier)
		self.bouncing = False

	def fill_lists(self):
		for container_id, listitems in self.listitems:
			#try:
			if 1==1:
				self.getControl(container_id).reset()
				#xbmc.log(str('fill_lists')+'===>OPENINFO', level=xbmc.LOGINFO)
				self.getControl(container_id).addItems(Utils.create_listitems(listitems,preload_images=0, enable_clearlogo=False, info=self.info))
			#except:
			#	Utils.log('Notice: No container with id %i available' % container_id)
		xbmc.sleep(100)
		self.focus_id = xbmcgui.Window(10000).getProperty('focus_id')
		self.position = xbmcgui.Window(10000).getProperty('position')
		pop_stack_focus_id = xbmcgui.Window(10000).getProperty('pop_stack_focus_id')
		pop_stack_position = xbmcgui.Window(10000).getProperty('pop_stack_position')
		##xbmc.log(str(self.focus_id)+'focus_id_fill_lists===>OPENINFO', level=xbmc.LOGINFO)
		##xbmc.log(str(self.position)+'position_fill_lists===>OPENINFO', level=xbmc.LOGINFO)
		##xbmc.log(str(pop_stack_focus_id)+'pop_stack_focus_id_fill_lists===>OPENINFO', level=xbmc.LOGINFO)
		##xbmc.log(str(pop_stack_position)+'pop_stack_position_fill_lists===>OPENINFO', level=xbmc.LOGINFO)
		if pop_stack_focus_id != 500:
			self.focus_id = pop_stack_focus_id
			self.position = pop_stack_position
		try: focus_id_int = int(self.focus_id)
		except: focus_id_int = 0
		if str(self.focus_id) != '':
			xbmc.sleep(100)
			#xbmc.log(str(self.focus_id)+'focus_id_fill_lists===>OPENINFO', level=xbmc.LOGINFO)
			#xbmc.log(str(self.position)+'position_fill_lists===>OPENINFO', level=xbmc.LOGINFO)
			try: self.focus_id = int(self.focus_id)
			except: self.focus_id = 500
			if self.focus_id != 500:
				self.setFocusId(int(self.focus_id))
				if str(self.position) != 'No position':
					xbmc.executebuiltin('Control.SetFocus(%s,%s)' % (self.focus_id,self.position))

	@ch.click(1250)
	@ch.click(1350)
	def open_image(self):
		listitems = next((v for (i, v) in self.listitems if i == self.control_id), None)
		index = self.control.getSelectedPosition()
		pos = wm.open_slideshow(listitems=listitems, index=index)
		self.control.selectItem(pos)

	@ch.action('contextmenu', 1250)
	def thumbnail_options(self):
		if not self.info.get('dbid'):
			return None
		selection = xbmcgui.Dialog().select(heading='Artwork', list=['Use as thumbnail'])
		if selection == 0:
			path = self.listitem.getProperty('original')
			media_type = self.window.getProperty('type')
			params = '"art": {"poster": "%s"}' % path
			Utils.get_kodi_json(method='VideoLibrary.Set%sDetails' % media_type, params='{ %s, "%sid":%s }' % (params, media_type.lower(), self.info['dbid']))

	@ch.action('contextmenu', 1350)
	def fanart_options(self):
		if not self.info.get('dbid'):
			return None
		selection = xbmcgui.Dialog().select(heading='Fanart', list=['Use as fanart'])
		if selection == 0:
			path = self.listitem.getProperty('original')
			media_type = self.window.getProperty('type')
			params = '"art": {"fanart": "%s"}' % path
			Utils.get_kodi_json(method='VideoLibrary.Set%sDetails' % media_type, params='{ %s, "%sid":%s }' % (params, media_type.lower(), self.info['dbid']))

	@ch.action('parentdir', '*')
	@ch.action('parentfolder', '*')
	#@ch.action('back', '*')
	def previous_menu(self):
		import sys
		if 'script=false' in str(sys.argv).lower() or 'diamondinfo' in str(sys.argv) or 'extendedinfo' in str(sys.argv) or 'extendedactorinfo' in str(sys.argv) or 'extendedtvinfo' in str(sys.argv) or 'seasoninfo' in str(sys.argv) or 'extendedepisodeinfo' in str(sys.argv):
			window_stack_enable2 = False
			if 'script=true' in str(sys.argv).lower() or 'reopen_window' in str(sys.argv).lower() :
				window_stack_enable2 = True
		else:
			window_stack_enable2 = True

		if Utils.window_stack_enable == 'false' and window_stack_enable2:
			#window_id = xbmcgui.getCurrentWindowDialogId()
			#window = xbmcgui.Window(self.window_id)
			#xbmc.log(str(window_id)+'window_id===>OPEN_INFO', level=xbmc.LOGINFO)
			#xbmc.log(str(window)+'window===>OPEN_INFO', level=xbmc.LOGINFO)
			self.close()
			try: del self
			except: pass
			return wm.open_video_list(search_str='', mode='reopen_window')

		onback = self.window.getProperty('%i_onback' % self.control_id)
		if onback:
			xbmc.executebuiltin(onback)
		else:
			#self.close()
			self.close()
			wm.pop_stack()

	@ch.action('previousmenu', '*')
	def exit_script(self):
		self.close()
		try: del self
		except: pass

	@Utils.run_async
	def get_youtube_vids(self, search_str):
		try:
			youtube_list = self.getControl(350)
		except:
			return None
		try:
			result = YouTube.search_youtube(search_str, limit=10)
		except:
			return None
		if not self.yt_listitems:
			self.yt_listitems = result.get('listitems', [])
			if 'videos' in self.data:
				vid_ids = [item['key'] for item in self.data['videos']]
				self.yt_listitems = [i for i in self.yt_listitems if i['youtube_id'] not in vid_ids]
		youtube_list.reset()
		youtube_list.addItems(Utils.create_listitems(self.yt_listitems))

	def open_credit_dialog(self, credit_id):
		info = TheMovieDB.get_credit_info(credit_id)
		listitems = []
		if 'seasons' in info['media']:
			listitems += TheMovieDB.handle_tmdb_seasons(info['media']['seasons'])
		if 'episodes' in info['media']:
			listitems += TheMovieDB.handle_tmdb_episodes(info['media']['episodes'])
		if not listitems:
			listitems += [{'label': 'No information available'}]
		listitem, index = wm.open_selectdialog(listitems=listitems)
		if listitem['media_type'] == 'episode':
			wm.open_episode_info(prev_window=self, season=listitems[index]['season'], episode=listitems[index]['episode'], tvshow_id=info['media']['id'])
		elif listitem['media_type'] == 'season':
			wm.open_season_info(prev_window=self, season=listitems[index]['season'], tvshow_id=info['media']['id'])