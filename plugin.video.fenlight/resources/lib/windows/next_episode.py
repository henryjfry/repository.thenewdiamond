# -*- coding: utf-8 -*-
import time
from windows.base_window import BaseDialog
from xbmc import executebuiltin
# from modules.kodi_utils import logger

pause_time_before_end, hold_pause_time = 10, 900
episode_flag_base = 'fenlight_flags/episodes/%s.png'
button_actions = {10: 'close', 11: 'play', 12: 'cancel', 13: 'stop'}
episode_status_dict = {
'season_premiere': 'b30385b5',
'mid_season_premiere': 'b385b503',
'series_finale': 'b38503b5',
'season_finale': 'b3b50385',
'mid_season_finale': 'b3b58503',
'':  ''}

class NextEpisode(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, *args)
		self.closed = False
		self.meta = kwargs.get('meta')
		self.selected = kwargs.get('default_action', 'cancel')
		#self.selected = 'play'
		#self._initial_file = self.player.getPlayingFile()
		self.set_properties()


	def onInit(self):
		self._initial_file = self.player.getPlayingFile()
		self.setFocusId(11)

		from threading import Thread
		Thread(target=self.monitor, daemon=True).start()


	def run(self):
		self.doModal()
		self.clearProperties()
		self.clear_modals()
		return self.selected

	def onAction(self, action):
		if action in self.closing_actions:
			self.selected = 'close'
			self.closed = True
			self.close()

	def onClick(self, controlID):
		self.selected = button_actions[controlID]
		self.closed = True
		if self.selected == 'play':
			executebuiltin('PlayerControl(BigSkipForward)')
		elif self.selected == 'stop':
			executebuiltin('PlayerControl(Stop)')
		elif self.selected in ('cancel', 'close'):
			pass  # do nothing
		self.close()


	def set_properties(self):
		episode_type = self.meta.get('episode_type', '')
		self.setProperty('thumb', self.meta.get('ep_thumb', None) or self.meta.get('fanart', ''))
		self.setProperty('clearlogo', self.meta.get('clearlogo', ''))
		self.setProperty('episode_label', '%s[B] | [/B]%02dx%02d[B] | [/B]%s' % (self.meta['title'], self.meta['season'], self.meta['episode'], self.meta['ep_name']))
		self.setProperty('episode_status.highlight', episode_status_dict[episode_type])
		self.setProperty('episode_status.flag', episode_flag_base % episode_type)

	def is_paused(self):
		try:
			import xbmc, json
			result = xbmc.executeJSONRPC(
				'{"jsonrpc":"2.0","method":"Player.GetProperties","params":{"playerid":1,"properties":["speed"]},"id":1}'
			)
			speed = json.loads(result)['result']['speed']
			return int(speed) == 0
		except:
			return False

	def monitor(self):
		start_time = time.time()

		while True:
			try:
				if self.closed:
					break

				if not self.player.isPlayingVideo():
					break

				if self.player.getPlayingFile() != self._initial_file:
					break

				# ✅ pause-safe timeout
				if not self.is_paused():
					try: remaining_time = int(self.player.getTotalTime()) - int(self.player.getTime())
					except: remaining_time = 99
					if remaining_time < 2:
						break
				else:
					start_time = time.time()

				self.sleep(500)

			except:
				break

		self.closed = True
		self.sleep(200)

		try:
			self.close()
		except:
			pass
		return executebuiltin('Dialog.Close(next_episode.xml,true)')

