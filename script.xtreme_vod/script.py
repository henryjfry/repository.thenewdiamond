import sys, os
import xbmcgui
from resources.lib import process
from resources.lib.WindowManager import wm
from resources.lib.library import addon_ID_short
from resources.lib import Utils
os.environ['first_run'] = str('True')

class Main:
	def __init__(self):
		xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'True')
		self._parse_argv()
		if len(self.infos) == 0:
				self.infos.append('allmovies2')
		if self.infos:
			process.start_info_actions(self.infos, self.params)
		else:
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			wm.open_video_list()
			xbmcgui.Window(10000).clearProperty('infodialogs.active')
		xbmcgui.Window(10000).clearProperty(str(addon_ID_short())+'_running')

	def _parse_argv(self):
		self.infos = []
		self.params = {'handle': None}
		for arg in sys.argv:
			param = arg.replace('"', '').replace("'", ' ')
			if param.startswith('info='):
				self.infos.append(param[5:])
			else:
				try:
					self.params[param.split('=')[0].lower()] = '='.join(param.split('=')[1:]).strip()
				except:
					pass

if (__name__ == '__main__'):
	Main()