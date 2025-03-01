"""
import xbmc
import json
from threading import Thread

class Monitor_Thread(Thread):

	def __init__(self):
		Thread.__init__(self)

	def raise_exc(self, excobj):
		assert self.isAlive(), "thread must be started"
		for tid, tobj in threading._active.items():
			if tobj is self:
				_async_raise(tid, excobj)
				return

	def terminate(self):
		# must raise the SystemExit type, instead of a SystemExit() instance
		# due to a bug in PyThreadState_SetAsyncExc
		self.raise_exc(SystemExit)

	class KodiMonitor(xbmc.Monitor):
		xbmc.log(str('SERVICE2')+'===>OPENINFO', level=xbmc.LOGINFO)
		xbmc.log(str('SERVICE2')+'!!===>OPENINFO', level=xbmc.LOGINFO)
		def __init__(self, **kwargs):
			xbmc.Monitor.__init__(self)
			global window
			window = None

		def terminate_mon(self):
			try: Monitor_Thread.terminate()
			except: pass

		def onNotification(self, sender, method, data):
			from resources.lib.WindowManager import wm
			global window
			try: test_window = wm.global_dialog()
			except: pass
			try:
				if not window and test_window:
					window = test_window
					del test_window
					xbmc.log(str(window)+'===>OPENINFO', level=xbmc.LOGINFO)
				elif window != test_window and test_window:
					del window
					window = test_window
					del test_window
					xbmc.log(str(window)+'===>OPENINFO', level=xbmc.LOGINFO)
			except:
				pass
			#xbmc.log(str(sender)+'===>OPENINFO', level=xbmc.LOGINFO)
			if sender == 'POP_STACK':
				command_info = json.loads(data)
				#xbmc.log(str(command_info)+'onNotification===>OPENINFO', level=xbmc.LOGINFO)
				container = command_info['command_params']['container']
				position = command_info['command_params']['position']
				window.doModal()
				self.terminate_mon()
				#del window
				#window = None
				try: del wm
				except: self.terminate_mon()
				try: del monitor
				except: self.terminate_mon()
				try: del Thread
				except: self.terminate_mon()
				return
				#xbmc.log(str(wm.global_dialog())+'===>OPENINFO', level=xbmc.LOGINFO)
				for i in range(600):
					if xbmc.getCondVisibility('Player.HasMedia'):
						xbmc.sleep(250)
						while xbmc.getCondVisibility('Player.HasMedia'):
							xbmc.sleep(250)
							while xbmc.getCondVisibility('Window.IsActive(10138)'):
								xbmc.sleep(250)
						xbmc.sleep(250)
						window.doModal()
						del window
						window = None
						del wm
						del monitor
						del Monitor_Thread
						return
					xbmc.sleep(50)

	#player = xbmc.Player()
	#from resources.lib.WindowManager import wm
	monitor = KodiMonitor()
"""
import xbmc
import json
#import xbmcgui
#import xbmcaddon

#ADDON_ID = 'plugin.audio.delaychanger'
#ADDON = xbmcaddon.Addon(ADDON_ID)

# Define the audio delay settings for different audio codecs
AUDIO_SETTINGS = {
	'eac3': -200,  # milliseconds
	'aac': 0,
	'flac': 0,
	'aac': 0,
	'aac_latm': 0,
	'ac3': -200,
	'aif': 0,
	'aifc': 0,
	'aiff': 0,
	'alac': 0,
	'ape': 0,
	'avc': 0,
	'cdda': 0,
	'dca': -200,
	'dolbydigital': -200,
	'dd': -200,
	'dd+': -200,
	'pt-dtshd': -200,
	'dts': -200,
	'dtshd_hra': -200,
	'dtshd_ma': -200,
	'dtsma': -200,
	'eac3': -200,
	'flac': 0,
	'mp1': 0,
	'mp2': 0,
	'mp3': 0,
	'mp3float': 0,
	'ogg': 0,
	'opus': 0,
	'pcm': -200,
	'pcm_bluray': -200,
	'pcm_s16le': -200,
	'pcm_s24le': -200,
	'truehd': -200,
	'vorbis': 0,
	'wav': -200,
	'wavpack': -200,
	'wma': 0,
	'wmapro': 0,
	'wmav2': 0,
	# Add more audio codecs and their corresponding delay settings as needed
}

def set_audio_delay(audio_delay):
	xbmc.executebuiltin('SetAudioDelay({})'.format(audio_delay))
	#json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Player.SetAudioDelay","id":1,"params":{"playerid":1,"offset":%s}}' % (str(audio_delay/1000)))
	#json_object  = json.loads(json_result)
	#xbmc.log(str(json_object)+'===>PHIL_SUBTITLES!!!!!!', level=xbmc.LOGINFO)

def on_playback_started():
	player = xbmc.Player()
	json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.AudioCodec"]}, "id":1}')
	json_object  = json.loads(json_result)
	audio_codec = json_object['result']['VideoPlayer.AudioCodec']
	xbmc.log(str(audio_codec)+'===>PHIL_SUBTITLES!!!!!!', level=xbmc.LOGINFO)
	xbmc.log(str(json_object)+'===>PHIL_SUBTITLES!!!!!!', level=xbmc.LOGINFO)
	json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Player.GetAudioDelay","id":1}')
	json_object  = json.loads(json_result)
	#'{"jsonrpc":"2.0","method":"Player.SetAudioDelay","id":1,"params":{"playerid":1,"offset":-0.250}}'
	xbmc.log(str(json_object)+'===>PHIL_SUBTITLES!!!!!!', level=xbmc.LOGINFO)
	#audio_codec = player.getAudioCodec()
	if audio_codec == '':
		set_audio_delay(0)
	if audio_codec in AUDIO_SETTINGS:
		audio_delay = AUDIO_SETTINGS[audio_codec]
		xbmc.log(str(audio_delay)+'!!set_audio_delay===SERVICE2===>OPENINFO', level=xbmc.LOGINFO)
		set_audio_delay(audio_delay)

def on_playback_resumed():
	on_playback_started()

def on_playback_changed():
	on_playback_started()

class DelayChanger(xbmc.Player):

	def __init__(self):
		xbmc.Player.__init__(self)

	def onAVStarted(self):
		on_playback_started()

	def onPlayBackStarted(self):
		on_playback_started()

	def onPlayBackResumed(self):
		on_playback_resumed()

	def onAVChange(self):
		on_playback_changed()

	def onPlayBackChanged(self):
		on_playback_changed()

def run_service():
	player = DelayChanger()
	while not xbmc.Monitor().abortRequested():
		xbmc.sleep(100)

xbmc.log(str('SERVICE2')+'!!===>OPENINFO', level=xbmc.LOGINFO)
run_service()
