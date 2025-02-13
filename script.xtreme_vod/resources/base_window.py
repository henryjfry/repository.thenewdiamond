__metaclass__ = type


import os

#from resources.lib.common import tools
#from resources.lib.modules.skin_manager import SkinManager

import xbmc
import xbmcgui
import re

class BaseWindow(xbmcgui.WindowXMLDialog):

	def __init__(self, xml_file, location, actionArgs=None):

		self.next_url = re.findall(r'([^\[\]]*)', actionArgs)[1]
		self.title = re.findall(r'([^\[\]]*)', actionArgs)[4]
		self.thumb = re.findall(r'([^\[\]]*)', actionArgs)[7]
		self.rating = re.findall(r'([^\[\]]*)', actionArgs)[10]
		self.show = re.findall(r'([^\[\]]*)', actionArgs)[13]
		self.season = re.findall(r'([^\[\]]*)', actionArgs)[16]
		self.episode = re.findall(r'([^\[\]]*)', actionArgs)[19]
		self.year = re.findall(r'([^\[\]]*)', actionArgs)[22]

		try:
			super(BaseWindow, self).__init__(xml_file, location)
		except:
			xbmcgui.WindowXMLDialog().__init__()

		if xbmc.getCondVisibility('Window.IsActive(busydialog)'):
				xbmc.executebuiltin('Dialog.Close(busydialog)')
		if xbmc.getCondVisibility('Window.IsActive(busydialognocancel)'):
				xbmc.executebuiltin('Dialog.Close(busydialognocancel)')

		self.canceled = False

		self.setProperty('texture.white', '/home/osmc/.kodi/addons/service.next_playlist/resources/images/white.png')
		self.setProperty('seren.logo', '/home/osmc/.kodi/addons/service.next_playlist/resources/images/trans-gold-fox-final.png')
		self.setProperty('seren.fanart', '/home/osmc/.kodi/addons/service.next_playlist/resources/images/fanart-fox-gold-final.png')
		self.setProperty('settings.color', 'deepskyblue')
		self.setProperty('test_pattern', '/home/osmc/.kodi/addons/service.next_playlist/resources/images/test_pattern.png')
		self.setProperty('skin.dir', '/home/osmc/.kodi/addons/service.next_playlist')


#		import xbmc
#		import xbmcgui
#		self.window = xbmcgui.getCurrentWindowId()
#		xbmc.log(str(xml_file)+' ===BASE_WINDOW', level=xbmc.LOGNOTICE)
#		xbmc.log(str(SkinManager().confirm_skin_path(xml_file))+' ===BASE_WINDOW', level=xbmc.LOGNOTICE)
#		xbmc.log(str(self.window)+' ===BASE_WINDOW', level=xbmc.LOGNOTICE)
#		xbmc.log(str(xbmcgui.Window(self.window).getProperty('skin.dir'))+' ===BASE_WINDOW', level=xbmc.LOGNOTICE)

		if actionArgs is None:
			return

		self.setProperty('item.info.title', self.title)
		self.setProperty('item.art.thumb', self.thumb)
		self.setProperty('item.art.landscape', self.thumb)
		self.setProperty('item.art.fanart', self.thumb)
		self.setProperty('item.info.tvshowtitle', self.show)
		self.setProperty('item.info.year', self.year)
		self.setProperty('item.info.rating', self.rating)

		"""
		self.item_information = tools.get_item_information(actionArgs)

		for id, value in self.item_information['ids'].items():
			self.setProperty('item.ids.%s_id' % id, str(value))

		for i in self.item_information['art'].keys():
			self.setProperty('item.art.%s' % i, str(self.item_information['art'][i]))

		self.item_information['info'] = tools.clean_air_dates(self.item_information['info'])

		year, month, day = self.item_information['info'].get('aired', '0000-00-00').split('-')

		self.setProperty('item.info.aired.year', year)
		self.setProperty('item.info.aired.month', month)
		self.setProperty('item.info.aired.day', day)

		try:
			if 'aired' in self.item_information['info']:
				aired_date = self.item_information['info']['aired']
				aired_date = tools.datetime_workaround(aired_date)
				aired_date = aired_date.strftime(tools.get_region('dateshort'))
				self.item_information['info']['aired'] = aired_date
				
			if 'premiered' in self.item_information['info']:
				premiered = self.item_information['info']['premiered']
				premiered = tools.datetime_workaround(premiered)
				premiered = premiered.strftime(tools.get_region('dateshort'))
				self.item_information['info']['premiered'] = premiered
		except:
			pass

		for i in self.item_information['info'].keys():
			value = self.item_information['info'][i]
			if i == 'aired' or i == 'premiered':
				try:
					value = value[:10]
				except:
					value = 'TBA'
			if i == 'duration':
				try:
					hours = int(value) % 60
					self.setProperty('item.info.%s.minutes' % i, str(int(value) - (hours*60)))
					self.setProperty('item.info.%s.hours' % i, str(hours))
				except:
					pass
			try:
				self.setProperty('item.info.%s' % i, str(value))
			except UnicodeEncodeError:
				self.setProperty('item.info.%s' % i, value)
		"""
