import abc

import xbmc

from resources.lib.gui.windows.base_window import BaseWindow
from resources.lib.modules.globals import g

 
import json

class SmartPlayWindow(BaseWindow):
	"""
	Dialog to provide quick skipping to next playlist item if available.
	"""

	def __init__(self, xml_file, xml_location, item_information=None):
		try:
			super().__init__(xml_file, xml_location, item_information=item_information)
			self.player = xbmc.Player()
			self.playing_file = self.getPlayingFile()
			self.duration = self.getTotalTime() - self.getTime()
			self.closed = False
		except Exception:
			g.log_stacktrace()

	def __del__(self):
		self.player = None
		del self.player

	# region player methods
	def getTotalTime(self):
		"""
		Fetches total time of current playing item
		:return: Total time in seconds
		:rtype: float
		"""
		return self.player.getTotalTime() if self.isPlaying() else 0

	def getTime(self):
		"""
		Get curent position of playing item
		:return: Current position in seconds
		:rtype: float
		"""
		return self.player.getTime() if self.isPlaying() else 0

	def isPlaying(self):
		"""
		Checks if an item is currently playing
		:return: True if player is currently playing something
		:rtype: bool
		"""
		return self.player.isPlaying()

	def getPlayingFile(self):
		"""
		Returns path to playing item
		:return: path to playing item
		:rtype: str
		"""
		return self.player.getPlayingFile()

	def seekTime(self, seekTime):
		"""
		Seeks player to provided point in time
		:param seekTime: Time to seek to in fractional seconds
		:type seekTime: float
		:return:
		"""
		self.player.seekTime(seekTime)

	def pause(self):
		"""
		Pauses currently playing item
		:return:
		"""
		self.player.pause()

	# endregion

	def onInit(self):
		"""
		Runs when window is displayed
		:return:
		"""
		self.background_tasks()
		super().onInit()

	def calculate_percent(self):
		"""
		Calculates percent of playing item is watched
		:return: Percentage played
		:rtype: int
		"""
		return ((int(self.getTotalTime()) - int(self.getTime())) / float(self.duration)) * 100

	def background_tasks(self):
		"""
		Runs background watcher tasks
		:return:
		"""
		try:
			try:
				progress_bar = self.getControlProgress(3014)
			except RuntimeError:
				progress_bar = None

			while (
				int(self.getTotalTime()) - int(self.getTime()) > 2
				and not self.closed
				and self.playing_file == self.getPlayingFile()
				and not g.abort_requested()
			):
				xbmc.sleep(500)
				if progress_bar is not None:
					progress_bar.setPercent(self.calculate_percent())

			self.smart_play_action()
		except Exception:
			g.log_stacktrace()

		self.close()

	@abc.abstractmethod
	def smart_play_action(self):
		"""
		Perform the default smartplay action at window timeout
		:return:
		"""

	def close(self):
		"""
		Call to close window
		:return:
		"""
		self.closed = True
		super().close()

	def handle_action(self, action, control_id=None):
		if action == 7:
			if control_id == 3001:
				if_playback_paused()
				xbmc.executebuiltin('PlayerControl(BigSkipForward)')
				self.close()
			if control_id == 3002:
				self.close()
			if control_id == 3003:
				xbmc.PlayList(xbmc.PLAYLIST_VIDEO).clear()
				self.close()

def if_playback_paused():
	try:
		#start_time = xbmc.Player().getTime()
		json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0","id": "1","method": "Player.GetProperties","params": {"playerid": 1,"properties": ["speed"]}}')
		json_object  = json.loads(json_result)
		speed = json_object['result']['speed']
		if int(speed) == 0:
			xbmc.executebuiltin('PlayerControl(Play)')
			return
		else:
			return
	except:
		return