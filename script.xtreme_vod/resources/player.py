import xbmc
import xbmcaddon
import xbmcgui
import sys

#PlayerDialogs().display_dialog()

class PlayerDialogs(xbmc.Player):

	def __init__(self):
		super(PlayerDialogs, self).__init__()
		player = xbmc.Player


	def display_dialog(self, next_url, title, thumb, rating, show, season, episode, year):

		if xbmc.Player().isPlayingVideo()==0:
			xbmc.executebuiltin('Dialog.Close(busydialog)')
			xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
			return

		self.next_url = next_url
		self.title = title
		self.thumb = thumb
		self.rating = rating
		self.show = show
		self.season = season
		self.episode = episode
		self.year = year
		self.player = xbmc.Player()
		self.actioned = False
		self.duration = None

		target = self._show_playing_next
		target()


	def _show_playing_next(self):

#	   xbmc.log(str(self.next_url)+'NEXT_URL___PLAYER1===>service.next_playlist1', level=xbmc.LOGFATAL)

		from resources.playing_next import PlayingNext
		actionArgs = '[' + str(self.next_url) + ']' + '[' + str(self.title) + ']' + '[' + str(self.thumb) + ']' + '[' + str(self.rating) + ']' + '[' + str(self.show) + ']' + '[' + str(self.season) + ']' + '[' + str(self.episode) + ']' + '[' + str(self.year) + ']'
		xbmc.log(str(actionArgs)+' actionArgs===SEREN_PLAYER', level=xbmc.LOGFATAL)
		try:
			PlayingNext('playing_next.xml', xbmcaddon.Addon().getAddonInfo('path'),  actionArgs=actionArgs).doModal()
		except:
			PlayingNext('playing_next.xml', xbmcaddon.Addon().getAddonInfo('path').decode('utf-8'),  actionArgs=actionArgs).doModal()



#	   next_url = 1
#		PlayingNext('playing_next.xml', xbmcaddon.Addon().getAddonInfo('path').decode('utf-8'), actionArgs=next_url).doModal()


		"""
		xbmc.sleep(10000)


		while xbmc.Player().isPlayingVideo()==0:
				xbmc.log(str(xbmc.Player().isPlayingVideo())+'PLAYER2===>service.next_playlist1', level=xbmc.LOGFATAL)
				xbmc.sleep(500)

		xbmc.log(str(xbmc.Player().isPlayingVideo())+'PLAYER3===>service.next_playlist1', level=xbmc.LOGFATAL)
		"""
