import sys, os
import xbmcgui
from resources.lib import process
from resources.lib.WindowManager import wm
from resources.lib.library import addon_ID_short

os.environ['first_run'] = str('True')

class Main:
	def __init__(self):
		xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'True')
		self._parse_argv()
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

		params = self.params
		search_flag = False
		search_text = None
		pop_index = []
		search_dict_name = None
		for idx, i in enumerate(params):
			if 'search_text' == i or 'str' == i:
				search_flag = True
				search_dict_name = i
			if search_flag == True and ('search_text' == i or 'str' == i):
				search_text = params[i]
			if search_text != None and params[i] == '' and search_flag == True:
				search_text = search_text + ', ' + i
				pop_index.append(i)

		if search_dict_name:
			for i in pop_index:
				params.pop(i)
			params[search_dict_name] = search_text
		if search_dict_name:
			self.params = params


if (__name__ == '__main__'):
	Main()