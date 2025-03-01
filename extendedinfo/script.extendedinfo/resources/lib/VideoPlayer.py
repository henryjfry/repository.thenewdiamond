import xbmc, xbmcgui
from resources.lib import Utils
import gc
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
import json
from resources.lib.WindowManager import wm

class VideoPlayer(xbmc.Player):

	def wait_for_video_end(self):
		while xbmc.Player().isPlaying()==1:
			xbmc.sleep(250)
			#while xbmc.getCondVisibility('Window.IsActive(10138)') or xbmcgui.Window(10000).getProperty('Next_EP.ResolvedUrl') == 'true' or xbmcgui.Window(10000).getProperty('Next_EP.ResolvedUrl_playlist') == 'true':
			#	xbmc.sleep(250)
		xbmc.sleep(250)
		#self.stopped = False

	def container_position(self, container=None, position=None):
		params = {'sender': addon_ID_short(),
						  'message': 'SetFocus',
						  'data': {'command': 'SetFocus',
									   'command_params': {'container': container, 'position': position}
									   },
						  }

		command = json.dumps({'jsonrpc': '2.0',
									  'method': 'JSONRPC.NotifyAll',
									  'params': params,
									  'id': 1,
									  })
		result = xbmc.executeJSONRPC(command)
		return result

	def play(self, url, listitem, window=False):
		import time
		xbmcgui.Window(10000).setProperty('diamond_info_time', str(int(time.time())+120))
		container = xbmc.getInfoLabel('System.CurrentControlId')
		position = int(xbmc.getInfoLabel('Container('+str(container)+').CurrentItem'))-1
		#window.close()
		#super(VideoPlayer, self).play(item=url, listitem=listitem, windowed=False, startpos=-1)
		xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'False')
		xbmcgui.Window(10000).setProperty('diamond_info_started', 'True')
		wm.add_to_stack(window, 'curr_window')
		window.close()
		xbmc.executebuiltin('Dialog.Close(all,true)')
		##Utils.get_kodi_json(method='Player.Open', params='{"item": %s}' % item)
		#xbmc.executebuiltin('RunPlugin(%s)' % url)
		xbmc.executebuiltin('RunScript(%s,info=play_test_pop_stack)' % addon_ID())
		super(VideoPlayer, self).play(item=url, listitem=listitem, windowed=False, startpos=-1)
		xbmc.log(str('play')+'_________________________play===>OPENINFO', level=xbmc.LOGINFO)
		return

		for i in range(600):
			if xbmc.getCondVisibility('VideoPlayer.IsFullscreen'):
				if window and window.window_type == 'dialog':
					wm.add_to_stack(window, 'curr_window')
					#window.close()
					if Utils.window_stack_enable == 'true':
						window = None
						del window
					self.wait_for_video_end()
					if Utils.window_stack_enable == 'false':
						self.container_position(container=container,position=position)
						window.doModal()
						window = None
						del window
						return
					self.container_position(container=container,position=position)
					return wm.pop_stack()
			xbmc.sleep(50)

	def play_from_button(self, url=None, listitem=None, window=False, type='', dbid=0):
		#from resources.lib.WindowManager import wm
		import time
		xbmcgui.Window(10000).setProperty('diamond_info_time', str(int(time.time())+120))
		if dbid != 0:
			item = '{"%s": %s}' % (type, dbid)
		else:
			item = '{"file": "%s"}' % url
		if Utils.window_stack_enable == 'false':
			super(VideoPlayer, self).play(item=url, listitem=listitem, windowed=False, startpos=-1)
			window.close()
			gc.collect()
			#xbmc.executebuiltin('RunPlugin(%s)' % url)
			del window
			#xbmc.executebuiltin('Dialog.Close(all,true)')
			#try: self.close()
			#except: pass
			return
		xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'False')
		xbmcgui.Window(10000).setProperty('diamond_info_started', 'True')
		wm.add_to_stack(window, 'curr_window')
		window.close()
		xbmc.executebuiltin('Dialog.Close(all,true)')
		#Utils.get_kodi_json(method='Player.Open', params='{"item": %s}' % item)
		xbmc.executebuiltin('RunScript(%s,info=play_test_pop_stack)' % addon_ID())
		xbmc.executebuiltin('RunPlugin(%s)' % url)
		xbmc.log(str('play_from_button')+'_________________________play_from_button===>OPENINFO', level=xbmc.LOGINFO)
		return

		for i in range(800):
			#xbmc.log(str('self.wait_for_video_end()')+str(i)+'before===>OPENINFO', level=xbmc.LOGINFO)
			#if xbmc.getCondVisibility('VideoPlayer.IsFullscreen'):
			if xbmc.Player().isPlaying()==1:
				if window and window.window_type == 'dialog':
					wm.add_to_stack(window, 'curr_window')
					window = None
					del window
					if xbmcgui.Window(10000).getProperty('bluray') == 'true':
						xbmc.sleep(500)
					xbmc.log(str('wait_for_video_end')+'append_window_stack_table===>OPENINFO', level=xbmc.LOGINFO)
					self.wait_for_video_end()
					xbmc.log(str('wait_for_video_end')+'append_window_stack_table===>OPENINFO', level=xbmc.LOGINFO)
					return wm.pop_stack()
			if xbmcgui.Window(10000).getProperty('bluray') == 'true':
				xbmc.sleep(350)
				i = i - 20
			xbmc.sleep(150)

	def playtube(self, youtube_id=False, listitem=None, window=False):
		xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'False')
		url = 'plugin://plugin.video.youtube/play/?video_id=%s' % str(youtube_id)
		self.play(url=url, listitem=listitem, window=window)

PLAYER = VideoPlayer()