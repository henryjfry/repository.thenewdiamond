import sys, os
import xbmcgui, xbmcplugin
from resources.lib import process
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short

os.environ['first_run'] = str('True')

class Main:
	def __init__(self):
		xbmcgui.Window(10000).setProperty(str(addon_ID_short())+'_running', 'True')
		self._parse_argv()
		if self.infos:
			process.start_info_actions(self.infos, self.params)
		else:
			movies  = {
				'comingsoonmovies': 'Upcoming Movies',
				'popularmovies': 'Popular Movies',
				'allmovies': 'All Movies'
				}
			tvshows = {
				'onairtvshows': 'Currently Airing TV Shows',
				'populartvshows': 'Popular TV Shows',
				'alltvshows': 'All TV Shows'
				}
			library = {
				'libraryallmovies': 'My Movies (Library)',
				'libraryalltvshows': 'My TV Shows (Library)'
				}
			search  = {
				'moviedbbrowser': 'Search...'
				}
			xbmcplugin.setContent(self.handle, 'addons')
			media_path = 'special://home/addons/'+str(addon_ID())+'/resources/skins/Default/media/'
			for key, value in sorted(movies.items()):
				li = xbmcgui.ListItem(value)
				li.setArt({'thumb': media_path + 'tm.png', 'fanart': media_path + 'tm-fanart.jpg'})
				url = 'plugin://'+str(addon_ID())+'?info=%s' % key
				xbmcplugin.addDirectoryItem(self.handle, url, li, False)
			for key, value in sorted(tvshows.items()):
				li = xbmcgui.ListItem(value)
				li.setArt({'thumb': media_path + 'tm.png', 'fanart': media_path + 'tm-fanart.jpg'})
				url = 'plugin://'+str(addon_ID())+'?info=%s' % key
				xbmcplugin.addDirectoryItem(self.handle, url, li, False)
			for key, value in sorted(library.items()):
				li = xbmcgui.ListItem(value)
				li.setArt({'thumb': media_path + 'tm.png', 'fanart': media_path + 'tm-fanart.jpg'})
				url = 'plugin://'+str(addon_ID())+'?info=%s' % key
				xbmcplugin.addDirectoryItem(self.handle, url, li, False)
			for key, value in search.items():
				li = xbmcgui.ListItem(value)
				li.setArt({'thumb': media_path + 'tm.png', 'fanart': media_path + 'tm-fanart.jpg'})
				url = 'plugin://'+str(addon_ID())+'?info=%s' % key
				xbmcplugin.addDirectoryItem(self.handle, url, li, False)
			xbmcplugin.endOfDirectory(self.handle)
		xbmcgui.Window(10000).clearProperty(str(addon_ID_short())+'_running')

	def _parse_argv(self):
		args = sys.argv[2][1:]
		self.handle = int(sys.argv[1])
		self.infos = []
		self.params = {'handle': self.handle}
		if args.startswith('---'):
			delimiter = '&'
			args = args[3:]
		else:
			delimiter = '&&'
		for arg in args.split(delimiter):
			param = arg.replace('"', '').replace("'", " ")
			if param.startswith('info='):
				self.infos.append(param[5:])
			else:
				try:
					self.params[param.split('=')[0].lower()] = '='.join(param.split('=')[1:]).strip()
				except:
					pass

if (__name__ == '__main__'):
	Main()