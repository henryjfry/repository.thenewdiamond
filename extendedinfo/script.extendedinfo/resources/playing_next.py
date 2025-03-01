import xbmc
import xbmcaddon
import xbmcgui
import functools
import json
#import re
from resources.base_window import BaseWindow
from inspect import currentframe, getframeinfo

class PlayingNext(BaseWindow):

	def __init__(self, xml_file, xml_location, actionArgs=None):
		try:
			self.player = xbmc.Player()
			self.closed = False
			self.actioned = None

			try:
				super(PlayingNext, self).__init__('playing_next.xml', xbmcaddon.Addon().getAddonInfo('path'), actionArgs=actionArgs)
			except:
				super(PlayingNext, self).__init__('playing_next.xml', xbmcaddon.Addon().getAddonInfo('path').decode('utf-8'), actionArgs=actionArgs)
			self.remaining_time = int(self.player.getTotalTime()) - int(self.player.getTime())
			self.percent_decrease = (0.5 / self.remaining_time) * 100
			self.playing_file = self.player.getPlayingFile()
			try: 
				self.duration = int(self.player.getVideoInfoTag().getDuration())
			except:
				self.duration = int(self.player.getTotalTime())
				#json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Title", "Player.Filenameandpath", "VideoPlayer.MovieTitle", "VideoPlayer.TVShowTitle", "VideoPlayer.DBID", "VideoPlayer.Duration", "VideoPlayer.Season", "VideoPlayer.Episode", "VideoPlayer.DBID"]}, "id":1}')
				#json_object  = json.loads(json_result)
				#timestamp = json_object['result']['VideoPlayer.Duration']
				#self.duration = functools.reduce(lambda x, y: x*60+y, [int(i) for i in (timestamp.replace(':',',')).split(',')])


		except:
			import traceback
			traceback.print_exc()

	def onInit(self):
		self.background_tasks()

	def calculate_percent(self):
		#xbmc.log(str(((int(self.player.getTotalTime()) - int(self.player.getTime())) / int(self.remaining_time)) * 100)+' ===PLAYING_NEXT', level=xbmc.LOGFATAL)
		return ((int(self.player.getTotalTime()) - int(self.player.getTime())) / int(self.remaining_time)) * 100

	def background_tasks(self):
		try:
			try:
				progress_bar = self.getControl(3014)
			except:
				progress_bar = None

			percent = 100
			while 35 > (int(self.player.getTotalTime()) - int(self.player.getTime())) > 2 and not self.closed:
				remaining_time = int(self.player.getTotalTime()) - int(self.player.getTime())
				xbmcgui.Window(10000).setProperty('Next_EP.RemainingTime', str(remaining_time))
				xbmc.sleep(500)
				if progress_bar is not None:
					percent = float(percent) - self.percent_decrease
					progress_bar.setPercent(self.calculate_percent())
				try:
					test_var = int(self.player.getTime())
				except:
					break
				if self.playing_file != self.player.getPlayingFile() or remaining_time < 3:
					break

		except:
			#import traceback
			#traceback.print_exc()
			#pass
			if self.closed != True:
				self.close()
				return
			if self.closed == True:	
				return
		if self.closed != True:
			self.close()
			return
		if self.closed == True:	
			return

	def doModal(self):
		try:
			super(PlayingNext, self).doModal()
		except:
			import traceback
			traceback.print_exc()



	def close(self):
		self.closed = True
		super(PlayingNext, self).close()
		try:
			while self.actioned != True and xbmc.Player().isPlayingVideo()==1 and (int(self.player.getTotalTime()) - int(self.player.getTime())) > 2:
				try:
					#resume_position = xbmc.Player().getTime()
					remaining_time = int(self.player.getTotalTime()) - int(self.player.getTime())
				except:
					break
				if self.playing_file != self.player.getPlayingFile() or remaining_time < 3:
					break
			xbmc.log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)+'===>OPENINFO', level=xbmc.LOGFATAL)
			if self.actioned == True :
				if_playback_paused()
				xbmc.executebuiltin('PlayerControl(BigSkipForward)')
				return
			return
		except:
			if self.actioned == True:
				if_playback_paused()
				xbmc.executebuiltin('PlayerControl(BigSkipForward)')
				return
		return

	def onClick(self, control_id):
		self.handle_action(7, control_id)

	def handle_action(self, action, control_id=None):
		if control_id is None:
			control_id = self.getFocusId()

		if control_id == 3001:
			self.actioned = True
			self.close()
			if_playback_paused()
			xbmc.executebuiltin('PlayerControl(BigSkipForward)')
			return
		if control_id == 3002:
			self.closed = True
			#self.close()
			super(PlayingNext, self).close()
			return

	def onAction(self, action):

		action = action.getId()

		if action == 92 or action == 10:
			# BACKSPACE / ESCAPE
			self.close()

		if action == 7:
			self.handle_action(action)
			return


def if_playback_paused():
	try:
		#start_time = xbmc.Player().getTime()
		json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0","id": "1","method": "Player.GetProperties","params": {"playerid": 1,"properties": ["speed"]}}')
		json_object  = json.loads(json_result)
		speed = json_object['result']['speed']
		xbmc.log(str(speed)+'playback_speed===>OPENINFO', level=xbmc.LOGINFO)
		#xbmc.sleep(10)
		#if xbmc.Player().getTime() == start_time:
		if int(speed) == 0:
			xbmc.executebuiltin('PlayerControl(Play)')
			return
		else:
			return
	except:
		return