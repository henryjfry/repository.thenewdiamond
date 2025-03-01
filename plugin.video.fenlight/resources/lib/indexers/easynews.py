# -*- coding: utf-8 -*-
import sys
from datetime import datetime
from urllib.parse import unquote, urlencode, quote
from modules.utils import jsondate_to_datetime
from apis.easynews_api import import_easynews
from indexers.images import Images
from modules import kodi_utils
from modules.utils import clean_file_name
# logger = kodi_utils.logger

build_url = kodi_utils.build_url
show_busy_dialog, hide_busy_dialog, show_text, set_view_mode = kodi_utils.show_busy_dialog, kodi_utils.hide_busy_dialog, kodi_utils.show_text, kodi_utils.set_view_mode
default_easynews_icon, get_addon_fanart, sleep = kodi_utils.get_icon('easynews'), kodi_utils.get_addon_fanart, kodi_utils.sleep
add_items, set_content, end_directory = kodi_utils.add_items, kodi_utils.set_content, kodi_utils.end_directory
make_listitem, ok_dialog = kodi_utils.make_listitem, kodi_utils.ok_dialog
fanart = get_addon_fanart()
EasyNews = import_easynews()

def search_easynews_image(key_id=None):
	return Images().run({'mode': 'easynews_image_results', 'key_id': unquote(key_id), 'page_no': 1})

def search_easynews(params):
	handle = int(sys.argv[1])
	key_id = params.get('key_id') or params.get('query')
	search_name = clean_file_name(unquote(key_id))
	try:
		files = EasyNews.search(search_name)
		easynews_file_browser(files, handle)
	except: pass
	set_content(handle, 'files')
	end_directory(handle, cacheToDisc=False)
	set_view_mode('view.premium')

def easynews_file_browser(files, handle):
	def _builder():
		for count, item in enumerate(files, 1):
			try:
				cm = []
				item_get = item.get
				width = item_get('width', 0)
				if width > 1920: display_res = '4K'
				elif 1280 < width <= 1920: display_res = '1080P'
				elif 720 < width <= 1280: display_res = '720P'
				else: display_res = 'SD'
				name = clean_file_name(item_get('name')).upper()
				url_dl = item_get('url_dl')
				down_url = item_get('down_url', url_dl)
				size = str(round(float(int(item_get('rawSize')))/1048576000, 1))
				length = item_get('runtime', '0')
				display = '%02d | [B]%s[/B] | [B]%sGB | %sMINS | [/B][I]%s [/I]' % (count, display_res, size, length, name)
				url_params = {'mode': 'easynews.resolve_easynews', 'action': 'cloud.easynews_direct', 'name': name, 'url': down_url,
								'url_dl': url_dl, 'image': default_easynews_icon, 'play': 'true'}
				url = build_url(url_params)
				down_file_params = {'mode': 'downloader.runner', 'name': name, 'url': down_url, 'action': 'cloud.easynews_direct', 'image': default_easynews_icon}
				cm.append(('[B]Download File[/B]', 'RunPlugin(%s)' % build_url(down_file_params)))
				listitem = make_listitem()
				listitem.setLabel(display)
				listitem.addContextMenuItems(cm)
				thumbnail = item_get('thumbnail', default_easynews_icon)
				listitem.setArt({'icon': thumbnail, 'poster': thumbnail, 'thumb': thumbnail, 'fanart': fanart, 'banner': default_easynews_icon})
				info_tag = listitem.getVideoInfoTag()
				info_tag.setPlot(' ')
				yield (url, listitem, False)
			except: pass
	add_items(handle, list(_builder()))

def resolve_easynews(params):
	resolved_link = EasyNews.resolve_easynews(params['url_dl'])
	if params.get('play', 'false') != 'true': return resolved_link
	from modules.player import FenLightPlayer
	FenLightPlayer().run(resolved_link, 'video')

def account_info(params):
	try:
		show_busy_dialog()
		account_info, usage_info = EasyNews.account()
		if not account_info or not usage_info: return ok_dialog(text='Error')
		body = []
		append = body.append
		expires = jsondate_to_datetime(account_info[2], '%Y-%m-%d')
		days_remaining = (expires - datetime.today()).days
		append('[B]Account:[/B] %s' % account_info[1])
		append('[B]Username:[/B] %s' % account_info[0])
		append('[B]Status:[/B] %s' % account_info[3])
		append('[B]Expires:[/B] %s' % expires)
		append('[B]Days Remaining:[/B] %s' % days_remaining)
		append('[B]Current Subscription:[/B] %s' % usage_info[2])
		append('[B]Data Used:[/B] %s' % usage_info[0].replace('Gigs', 'GB'))
		append('[B]Data Remaining:[/B] %s' % usage_info[1].replace('Gigs', 'GB'))
		hide_busy_dialog()
		return show_text('EASYNEWS', '\n\n'.join(body), font_size='large')
	except: hide_busy_dialog()

def active_days():
	try:
		account_info = EasyNews.account_info()
		expires = jsondate_to_datetime(account_info[2], '%Y-%m-%d')
		days_remaining = (expires - datetime.today()).days
	except: days_remaining = 0
	return days_remaining
