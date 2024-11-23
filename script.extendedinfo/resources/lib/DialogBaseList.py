import xbmc, xbmcgui, xbmcaddon, xbmcvfs
from resources.lib import Utils
from resources.lib.WindowManager import wm
from resources.lib.OnClickHandler import OnClickHandler
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short

import os
import sqlite3
from urllib.parse import urlencode, quote_plus, unquote, unquote_plus
from a4kscrapers_wrapper.tools import log

ch = OnClickHandler()

from inspect import currentframe, getframeinfo
#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)

class DialogBaseList(object):

	def __init__(self, *args, **kwargs):
		super(DialogBaseList, self).__init__(*args, **kwargs)
		self.listitem_list = kwargs.get('listitems', None)
		self.search_str = kwargs.get('search_str', '')
		self.filter_label = kwargs.get('filter_label', '')
		self.mode = kwargs.get('mode', 'filter')
		self.filters = kwargs.get('filters', [])
		self.list_id = kwargs.get('list_id', False)
		self.color = kwargs.get('color', 'FFAAAAAA')
		self.media_type = kwargs.get('media_type', 'tv')
		self.page = 1
		self.column = None
		self.last_position = 0
		self.total_pages = 1
		self.total_items = 0
		self.position = 0
		#self.window_stack_len2 = 0
		self.page_token = ''
		self.next_page_token = ''
		self.prev_page_token = ''


	def onInit(self):
		super(DialogBaseList, self).onInit()
		try: self.getControl(500).selectItem(0)
		except: pass
		xbmcgui.Window(10000).setProperty('WindowColor', self.color)
		self.setProperty('WindowColor', self.color)
		if xbmcaddon.Addon().getSetting('alt_browser_layout') == 'true':
			self.setProperty('alt_layout', 'true')

		#log(Utils.db_con)
		self.update_ui()
		xbmc.sleep(100)

		if self.total_items > 0 and self.position == 0 and xbmcgui.Window(10000).getProperty(str(addon_ID_short())+'_running') == 'True':
			self.setFocusId(500)
			self.focus_id = xbmcgui.Window(10000).getProperty('focus_id')
			self.position = xbmcgui.Window(10000).getProperty('position')
			##xbmc.log(str(self.focus_id)+'BASE_LIST_focus_id===>OPENINFO', level=xbmc.LOGINFO)
			##xbmc.log(str(self.position)+'BASE_LIST_position===>OPENINFO', level=xbmc.LOGINFO)
			xbmc.executebuiltin('Control.SetFocus(%s,%s)' % (self.focus_id,self.position))
			#self.setCurrentListPosition(int(self.position))
			self.position == self.last_position
		elif self.total_items == 0:
			self.setFocusId(6000)

	@ch.action('parentdir', '*')
	@ch.action('parentfolder', '*')
	def previous_menu(self):
		try: 
			if self.yt_listitems:
				youtube = True
			else:
				youtube = False
		except:
			youtube = False
		if youtube and Utils.window_stack_enable == 'false':
			self.close()
			try: del self
			except: pass
			return wm.open_video_list(search_str='', mode='reopen_window')
		if Utils.window_stack_enable == 'false':
			self.close()
			xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'False')
			try: del self
			except: pass
			Utils.hide_busy()
			return
		onback = self.getProperty('%i_onback' % self.control_id)
		if wm.window_stack_len > 0:
			onback = None
			#self.window_stack_len2 = self.window_stack_len2 - 1
			xbmcgui.Window(10000).setProperty('diamond_info_started','True')
			self.close()
			try: self.pop_window_stack_table()
			except KeyError: wm.pop_stack()
			return
		if onback:
			xbmc.executebuiltin(onback)
		else:
			self.close()
			log('wm.pop_stack()',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			xbmcgui.Window(10000).clearProperty('diamond_window_number')
			wm.pop_stack()

	@ch.action('previousmenu', '*')
	def exit_script(self):
		Utils.db_con.close()
		self.close()
		Utils.hide_busy()

	@ch.action('left', '*')
	@ch.action('right', '*')
	@ch.action('up', '*')
	@ch.action('down', '*')
	def save_position(self):
		self.focus_id = self.getFocusId()
		self.position = self.getControl(500).getSelectedPosition()
		wm.position = self.position
		wm.focus_id = self.focus_id
		xbmcgui.Window(10000).setProperty('focus_id', str(self.focus_id))
		xbmcgui.Window(10000).setProperty('position', str(self.position))

	def onAction(self, action):
		#xbmcgui.Window(10000).setProperty('focus_id', str(self.focus_id))
		#xbmcgui.Window(10000).setProperty('position', str(self.position))
		self.save_position()
		ch.serve_action(action, self.getFocusId(), self)

	def onFocus(self, control_id):
		self.focus_id = self.getFocusId()
		#wm.focus_id = self.focus_id
		self.save_position()
		old_page = self.page
		if control_id == 600:
			self.go_to_next_page()
		elif control_id == 700:
			self.go_to_prev_page()
		if self.page != old_page:
			#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			if wm.page == self.page:
				return
			self.update()

	def onClick(self, control_id):
		self.save_position()
		#xbmcgui.Window(10000).setProperty('focus_id', str(self.focus_id))
		#xbmcgui.Window(10000).setProperty('position', str(self.position))
		#wm.focus_id = self.focus_id
		#wm.position = self.position
		if 'youtubevideo' in str(self.listitems2):
			function = 'open_youtube_list'
		else:
			function = 'open_video_list'
		self.curr_window = {'function': function, 'params': {'listitems': self.listitems2, 'filters': self.filters, 'mode': self.mode, 'list_id': self.list_id, 'filter_label': self.filter_label, 'media_type': self.media_type, 'search_str': self.search_str, 'page': self.page, 'total_pages': self.total_pages, 'total_items': self.total_items, 'type': self.type, 'filter_url': self.filter_url, 'order': self.order, 'filter': self.filter , 'sort': self.sort, 'sort_label': self.sort_label, 'prev_page_token': self.prev_page_token, 'next_page_token': self.next_page_token, 'page_token': self.page_token}}
		wm.update_windows(curr_window=self.curr_window, prev_window=self.prev_window)
		wm.page_position = None
		ch.serve(control_id, self)

	@ch.click(5018)
	def reset_filters(self):
		if len(self.filters) > 0:
			listitems = ['%s: %s' % (f['typelabel'], f['label']) for f in self.filters]
			listitems.append('Remove all filters')
			index = xbmcgui.Dialog().select(heading='Remove filter', list=listitems)
			if index == -1:
				return None
			elif index == len(listitems) - 1:
				self.filters = []
			else:
				del self.filters[index]
		else:
			self.filters = []
		self.page = 1
		self.mode = 'filter'
		self.update()

	@ch.click(6000)
	def open_search(self):
		result = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
		if result and len(result) > -1:
			self.search(result)
		if self.total_items > 0:
			self.setFocusId(500)
		Utils.hide_busy()

	@ch.click(6001)
	def open_search2(self):
		result = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
		if result and len(result) > -1:
			from resources.lib.WindowManager import wm
			#self.append_window_stack_table('curr_window')
			self.prev_window = self.curr_window 
			#self.curr_window = {'function': 'open_youtube_list', 'params': {'search_str': result, 'filters': self.filters, 'filter_label': self.filter_label, 'media_type': self.media_type}}
			self.curr_window = {'function': 'open_youtube_list', 'params': {'listitems': self.listitems2, 'filters': self.filters, 'mode': self.mode, 'list_id': self.list_id, 'filter_label': self.filter_label, 'media_type': self.media_type, 'search_str': result, 'page': self.page, 'total_pages': self.total_pages, 'total_items': self.total_items, 'type': self.type, 'filter_url': self.filter_url, 'order': self.order, 'filter': self.filter, 'sort': self.sort, 'sort_label': self.sort_label, 'prev_page_token': self.prev_page_token, 'next_page_token': self.next_page_token, 'page_token': self.page_token}}
			if wm.pop_video_list == False:
				wm.update_windows(curr_window=self.curr_window, prev_window=self.prev_window)
			else:
				wm.pop_video_list = False
			wm.open_youtube_list(prev_window=self, search_str=result, curr_window=self.prev_window)
			#xbmc.executebuiltin('RunScript(%s,info=youtube,search_str=%s)' % (addon_ID(), result))
			try: self.close()
			except: pass
			try: del wm
			except: pass
			try: del self
			except: pass
			return

		if self.total_items > 0:
			self.setFocusId(500)
		Utils.hide_busy()

	def search(self, label):
		#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
		if not label:
			return None
		self.search_str = label
		self.mode = 'search'
		self.filters = []
		self.page = 1
		#self.update_content()
		#self.update_ui()
		wm.page = -1
		self.update()

	def set_filter_url(self):
		filter_list = []
		for item in self.filters:
			filter_list.append('%s=%s' % (item['type'], item['id']))
		self.filter_url = '&'.join(filter_list)
		if self.filter_url:
			self.filter_url += '&'

	def set_filter_label(self):
		filter_list = []
		for item in self.filters:
			filter_label = item['label'].replace('|', ' | ').replace(',', ' + ').replace(':', '')
			if 'relatedToVideoId' == item['type']:
				item['typelabel'] = 'Related To '
			if 'channelId' == item['type']:
				item['typelabel'] = 'Channel '
			filter_list.append('[COLOR FFAAAAAA]%s:[/COLOR] %s' % (item['typelabel'], filter_label))
		self.filter_label = '  -  '.join(filter_list)

	def update_content(self, force_update=False):
		#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
		data = self.fetch_data(force=force_update)

		if not data:
			#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			return None

		self.listitems = data.get('listitems', [])
		self.listitems2 = self.listitems
		self.total_pages = data.get('results_per_page', '')
		self.total_items = data.get('total_results', '')
		self.next_page_token = data.get('next_page_token', '')
		self.prev_page_token = data.get('prev_page_token', '')

		if Utils.NETFLIX_VIEW == 'true':
			self.listitems = Utils.create_listitems(self.listitems,preload_images=0, enable_clearlogo=True, info=None)
		else:
			self.listitems = Utils.create_listitems(self.listitems,preload_images=0, enable_clearlogo=False, info=None)

	def update_ui(self):
		#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)

		try: self.position = int(xbmc.getInfoLabel('Container(500).CurrentItem'))-1
		except: self.position = 0
		if self.position > 1 or wm.page_position == -1:
			if wm.page == -1:
				self.position = 0
				wm.page_position = 0
			if self.position > 1 or wm.page_position == -1:
				#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
				return

		if not self.listitems and self.getFocusId() == 500:
			self.setFocusId(6000)
		self.getControl(500).reset()
		if self.listitems:
			self.getControl(500).addItems(self.listitems)
			if wm.page_position:
				self.getControl(500).selectItem(wm.page_position)
				self.position = wm.page_position
				wm.page_position = -1
			else:
				self.getControl(500).selectItem(0)

			"""
			if self.column is not None and self.position == 0:
				if wm.prev_page_flag == True or wm.prev_page_num == self.page:
					if 'info=youtube' in str(wm.curr_window):
						self.getControl(500).selectItem(48+self.column)
						self.column = 48+self.column
					else:
						self.getControl(500).selectItem(16+self.column)
						self.column = 16+self.column
				else:
					self.getControl(500).selectItem(self.column)
				self.position = self.column
			"""
		self.setProperty('TotalPages', str(self.total_pages))
		self.setProperty('TotalItems', str(self.total_items))
		self.setProperty('CurrentPage', str(self.page))
		self.setProperty('Filter_Label', self.filter_label)
		self.setProperty('Sort_Label', self.sort_label)
		if self.page == self.total_pages:
			self.clearProperty('ArrowDown')
		else:
			self.setProperty('ArrowDown', 'True')
		if self.page > 1:
			self.setProperty('ArrowUp', 'True')
		else:
			self.clearProperty('ArrowUp')
		if self.order == 'asc':
			self.setProperty('Order_Label', 'Ascending')
		else:
			self.setProperty('Order_Label', 'Descending')

		if 'youtubevideo' in str(self.listitems2):
			function = 'open_youtube_list'
		else:
			function = 'open_video_list'
		self.curr_window = {'function': function, 'params': {'listitems': self.listitems2, 'filters': self.filters, 'mode': self.mode, 'list_id': self.list_id, 'filter_label': self.filter_label, 'media_type': self.media_type, 'search_str': self.search_str, 'page': self.page, 'total_pages': self.total_pages, 'total_items': self.total_items, 'type': self.type, 'filter_url': self.filter_url, 'order': self.order, 'filter': self.filter, 'sort': self.sort, 'sort_label': self.sort_label, 'total_items': self.total_items, 'total_pages': self.total_pages, 'prev_page_token': self.prev_page_token, 'next_page_token': self.next_page_token, 'page_token': self.page_token}}
		#if wm.pop_video_list == False:
		#	wm.update_windows(curr_window=self.curr_window, prev_window=self.prev_window)
		#else:
		#	wm.pop_video_list = False
		wm.update_windows(curr_window=self.curr_window, prev_window=self.prev_window)
		#xbmc.log(str(self.curr_window['params']['mode'])+'BASE_LIST_update_ui===>OPENINFO', level=xbmc.LOGINFO)
		#xbmc.log(str(self.curr_window['params']['type'])+'BASE_LIST_update_ui===>OPENINFO', level=xbmc.LOGINFO)

	def pop_window_stack_table(self):
		#xbmc.log(str('BASE_LIST')+'pop_window_stack_table_BASE_LIST===>OPENINFO', level=xbmc.LOGINFO)
		xbmc.log('BASE_LIST_pop_window_stack_table\n' +str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), level=xbmc.LOGINFO)
		if xbmc.Player().isPlayingVideo()==1 or xbmc.getCondVisibility('Window.IsActive(12005)'):
			return
		wm.page_position = None
		wm.page = None
		con = self.window_stack_connection()
		cur = con.cursor()

		sql_result = """
		select * from window_stack 
		order by inc_id desc limit 1
		"""
		sql_result = cur.execute(sql_result).fetchall()

		if len(sql_result) == 0:
			return
		window = sql_result[0][1]
		window_number = int(sql_result[0][0])
		window = '{' + unquote_plus(window).replace('function=',"'function': '").replace('&params=',"', 'params': ") + '}'
		window = eval(window)
		self.curr_window = window
		wm.update_windows(curr_window=self.curr_window, prev_window=self.prev_window)
		wm.pop_video_list = True

		sql_result = """
		DELETE FROM window_stack
		WHERE inc_id = '%s';
		""" % int(window_number)
		sql_result = cur.execute(sql_result).fetchall()
		con.commit()

		sql_result = """
		delete from sqlite_sequence where name='window_stack';
		"""
		sql_result = cur.execute(sql_result).fetchall()
		con.commit()
		
		#sql_result = """
		#select * from window_stack 
		#"""
		#sql_result = cur.execute(sql_result).fetchall()
		#self.window_stack_len2 = self.window_stack_len2 - 1
		wm.window_stack_length()

		cur.close()
		con.close()
		#print(window_number, window['function'], window['params'])
		self.focus_id = self.curr_window['params']['focus_id']
		self.position = self.curr_window['params']['position']
		self.total_items = self.curr_window['params']['total_items']
		self.total_pages = self.curr_window['params']['total_pages']
		##self.next_page_token = self.curr_window['params']['next_page_token']
		##self.prev_page_token = self.curr_window['params']['prev_page_token']

		xbmcgui.Window(10000).setProperty('focus_id', str(self.focus_id))
		xbmcgui.Window(10000).setProperty('position', str(self.position))
		xbmcgui.Window(10000).setProperty('pop_stack_focus_id', str(self.focus_id))
		xbmcgui.Window(10000).setProperty('pop_stack_position', str(self.position))

		#xbmc.log(str(self.curr_window['params']['mode'])+'BASE_LIST_pop_window_stack_table===>OPENINFO', level=xbmc.LOGINFO)
		#xbmc.log(str(self.curr_window['params']['type'])+'BASE_LIST_pop_window_stack_table===>OPENINFO', level=xbmc.LOGINFO)
		##xbmc.log(str(self.focus_id)+'focus_id===POP_STACK===>OPENINFO', level=xbmc.LOGINFO)
		##xbmc.log(str(self.position)+'position===POP_STACK===>OPENINFO', level=xbmc.LOGINFO)
		##xbmc.log(str(window)+'BASE_LIST===POP_STACK===>OPENINFO', level=xbmc.LOGINFO)

		if window['function'] == 'open_movie_info':
			wm.open_movie_info(movie_id=window['params']['movie_id'],dbid=window['params']['dbid'],name=window['params']['name'],imdb_id=window['params']['imdb_id'])
		elif window['function'] == 'open_tvshow_info':
			wm.open_tvshow_info(tmdb_id=window['params']['tmdb_id'],dbid=window['params']['dbid'],tvdb_id=window['params']['tvdb_id'],imdb_id=window['params']['imdb_id'],name=window['params']['name'])
		elif window['function'] == 'open_season_info':
			wm.open_season_info(tvshow_id=window['params']['tvshow_id'],season=window['params']['season'],tvshow=window['params']['tvshow'],dbid=window['params']['dbid'])
		elif window['function'] == 'open_episode_info':
			wm.open_episode_info(tvshow_id=window['params']['tvshow_id'], tvdb_id=window['params']['tvdb_id'],season=window['params']['season'],episode=window['params']['episode'],tvshow=window['params']['tvshow'],dbid=window['params']['dbid'])
		elif window['function'] == 'open_actor_info':
			wm.open_actor_info(actor_id=window['params']['actor_id'],name=window['params']['name'])
		elif window['function'] == 'open_video_list':

			self.focus_id = self.curr_window['params']['focus_id']
			self.position = self.curr_window['params']['position']
			if str(self.focus_id) != '500':
				self.focus_id = '500'
				#self.position = '0'
			xbmcgui.Window(10000).setProperty('focus_id', str(self.focus_id))
			xbmcgui.Window(10000).setProperty('position', str(self.position))
			xbmcgui.Window(10000).setProperty('pop_stack_focus_id', str(self.focus_id))
			xbmcgui.Window(10000).setProperty('pop_stack_position', str(self.position))
			wm.page = -1
			wm.open_video_list(listitems=window['params']['listitems'],filters=window['params']['filters'],mode=window['params']['mode'],list_id=window['params']['list_id'],filter_label=window['params']['filter_label'],media_type=window['params']['media_type'],search_str=window['params']['search_str'])
		elif window['function'] == 'open_youtube_list':

			self.focus_id = self.curr_window['params']['focus_id']
			self.position = self.curr_window['params']['position']
			if str(self.focus_id) != '500':
				self.focus_id = '500'
				#self.position = '0'
			xbmcgui.Window(10000).setProperty('focus_id', str(self.focus_id))
			xbmcgui.Window(10000).setProperty('position', str(self.position))
			xbmcgui.Window(10000).setProperty('pop_stack_focus_id', str(self.focus_id))
			xbmcgui.Window(10000).setProperty('pop_stack_position', str(self.position))

			wm.open_youtube_list(search_str=window['params']['search_str'],filters=window['params']['filters'],filter_label=window['params']['filter_label'],media_type=window['params']['media_type'])
		return

	def window_stack_connection(self):
		window_stack = str(xbmcvfs.translatePath("special://profile/addon_data/"+addon_ID()+ '/window_stack.db'))
		if not os.path.exists(window_stack):
			create_window_stack = True
		else:
			create_window_stack = False

		con = sqlite3.connect(window_stack)
		cur = con.cursor()

		if create_window_stack:
			sql_result = cur.execute("""
			CREATE TABLE window_stack (
				inc_id INTEGER PRIMARY KEY AUTOINCREMENT,
				window VARCHAR NOT NULL
			);
			""").fetchall()
			con.commit()

		return con

	def append_window_stack_table(self, mode=None):
		con = self.window_stack_connection()
		cur = con.cursor()
		if mode == 'curr_window':
			self.prev_window = self.curr_window

		self.focus_id = xbmcgui.Window(10000).getProperty('focus_id')
		self.position = xbmcgui.Window(10000).getProperty('position')
		self.prev_window['params']['focus_id'] = self.focus_id
		self.prev_window['params']['position'] = self.position
		window = urlencode(self.prev_window)
		sql_result = """
		INSERT INTO window_stack (window)
		VALUES( '%s');
		""" % (window)
		sql_result = cur.execute(sql_result).fetchall()

		con.commit()
		cur.close()
		con.close()
		#self.window_stack_len2 = self.window_stack_len2 + 1
		wm.window_stack_length()
		#try:
		#	self.last_control = xbmc.getInfoLabel('System.CurrentControlId').decode('utf-8')
		#except:
		#	self.last_control = xbmc.getInfoLabel('System.CurrentControlId')
		#if mode == 'curr_window':
		#	#xbmc.executebuiltin('Dialog.Close(all)')
		#	xbmc.executebuiltin('Dialog.Close(all,true)')

		xbmc.log(str('BASE_LIST')+'append_window_stack_table_BASE_LIST===>OPENINFO', level=xbmc.LOGINFO)
		#xbmc.log(str(mode)+'BASE_mode_append_window_stack_table_BASE_LIST===>OPENINFO', level=xbmc.LOGINFO)
		return


	@Utils.busy_dialog
	def update(self, force_update=False):
		#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
		self.prev_window = self.curr_window
		if self.page == 1 and wm.prev_page_num != self.page:
			self.append_window_stack_table('curr_window')
			#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
		else:
			if wm.page == -1:
				self.append_window_stack_table('curr_window')
				#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			if wm.prev_page_flag == False:
				wm.prev_page_num = 0
				#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			if wm.prev_page_num != 0 and wm.prev_page_flag == True:
				wm.prev_page_flag = False
				#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			if wm.pop_video_list == False:
				wm.update_windows(curr_window=self.curr_window, prev_window=self.prev_window)
				#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
			else:
				wm.pop_video_list = False
				#xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)

		self.update_content(force_update=force_update)
		self.update_ui()
		self.curr_window = {'function': 'open_video_list', 'params': {'listitems': self.listitems2, 'filters': self.filters, 'mode': self.mode, 'list_id': self.list_id, 'filter_label': self.filter_label, 'media_type': self.media_type, 'search_str': self.search_str, 'page': self.page, 'type': self.type, 'filter_url': self.filter_url, 'order': self.order, 'filter': self.filter, 'sort': self.sort, 'sort_label': self.sort_label,'total_items': self.total_items, 'total_pages': self.total_pages, 'prev_page_token': self.prev_page_token, 'next_page_token': self.next_page_token, 'page_token': self.page_token}}


	def get_column(self):
		for i in range(0, 10):
			if xbmc.getCondVisibility('Container(500).Column(%i)' % i):
				self.column = i
				break

	def add_filter(self, key, value, typelabel, label, force_overwrite=False):
		index = -1
		new_filter = {
			'id': value,
			'type': key,
			'typelabel': typelabel,
			'label': label
			}
		if new_filter in self.filters:
			return False
		for i, item in enumerate(self.filters):
			if item['type'] == key:
				index = i
				break
		if not value:
			return False
		if index == -1:
			self.filters.append(new_filter)
			return None
		if force_overwrite:
			self.filters[index]['id'] = quote_plus(str(value))
			self.filters[index]['label'] = str(label)
			return None
		dialog = xbmcgui.Dialog()

		without_genres = [i["label"] for i in self.filters if i["type"] == "without_genres"]
		try: without_genres = without_genres[0].replace(',','+').replace('|',' OR ')
		except: without_genres = ''
		with_genres = [i["label"] for i in self.filters if i["type"] == "with_genres"] 
		try: with_genres = with_genres[0].replace(',','+').replace('|',' OR ')
		except: with_genres = ''
		if key == 'without_genres':
			dialog_label = ' NOT  ' + without_genres
		else:
			dialog_label = ' WITH  ' + with_genres
		dialog_label = dialog_label + ': ' + label + '?'
		#xbmc.log(str(dialog_label)+'indexes===>OPENINFO', level=xbmc.LOGFATAL)

		ret = dialog.yesno(heading='Filter', message='Choose filter behaviour' + dialog_label, nolabel='AND', yeslabel='OR')
		if ret == -1:
			return
		if ret:
			self.filters[index]['id'] = str(self.filters[index]['id']) + '|' + quote_plus(str(value))
			self.filters[index]['label'] = self.filters[index]['label'] + '|' + label
		else:
			self.filters[index]['id'] = str(self.filters[index]['id']) + ',' + quote_plus(str(value))
			self.filters[index]['label'] = self.filters[index]['label'] + ',' + label

