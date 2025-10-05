# -*- coding: utf-8 -*-
import sys
import json
from datetime import datetime
from apis.alldebrid_api import AllDebrid
from modules import kodi_utils
from modules.source_utils import supported_video_extensions
from modules.utils import clean_file_name, normalize
# logger = kodi_utils.logger

def ad_cloud(folder_id=None):
	def _builder():
		for count, item in enumerate(cloud_dict, 1):
			try:
				cm = []
				folder_name, folder_id = item['filename'], item['id']
				clean_folder_name = clean_file_name(normalize(folder_name)).upper()
				display = '%02d | [B]FOLDER[/B] | [I]%s [/I]' % (count, clean_folder_name)
				url_params = {'mode': 'alldebrid.browse_ad_cloud', 'id': folder_id, 'folder': json.dumps(item['links'])}
				delete_params = {'mode': 'alldebrid.delete', 'id': folder_id}
				cm.append(('[B]Delete Folder[/B]','RunPlugin(%s)' % kodi_utils.build_url(delete_params)))
				url = kodi_utils.build_url(url_params)
				listitem = kodi_utils.make_listitem()
				listitem.setLabel(display)
				listitem.addContextMenuItems(cm)
				listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon})
				info_tag = listitem.getVideoInfoTag()
				info_tag.setPlot(' ')
				yield (url, listitem, True)
			except: pass
	try:
		cloud = AllDebrid.user_cloud()['magnets']
		cloud_dict = [i for i in cloud if i['statusCode'] == 4]
	except: cloud_dict = []
	icon, fanart = kodi_utils.get_icon('alldebrid'), kodi_utils.get_addon_fanart()
	handle = int(sys.argv[1])
	kodi_utils.add_items(handle, list(_builder()))
	kodi_utils.set_content(handle, 'files')
	kodi_utils.end_directory(handle)
	kodi_utils.set_view_mode('view.premium')

def browse_ad_cloud(folder):
	def _builder():
		for count, item in enumerate(links, 1):
			try:
				cm = []
				url_link = item['link']
				name = clean_file_name(item['filename']).upper()
				size = item['size']
				display_size = float(int(size))/1073741824
				display = '%02d | [B]FILE[/B] | %.2f GB | [I]%s [/I]' % (count, display_size, name)
				url_params = {'mode': 'alldebrid.resolve_ad', 'url': url_link, 'play': 'true'}
				down_file_params = {'mode': 'downloader.runner', 'name': name, 'url': url_link, 'action': 'cloud.alldebrid', 'image': icon}
				url = kodi_utils.build_url(url_params)
				cm.append(('[B]Download File[/B]','RunPlugin(%s)' % kodi_utils.build_url(down_file_params)))
				listitem = kodi_utils.make_listitem()
				listitem.setLabel(display)
				listitem.addContextMenuItems(cm)
				listitem.setArt({'icon': icon, 'poster': icon, 'thumb': icon, 'fanart': fanart, 'banner': icon})
				info_tag = listitem.getVideoInfoTag()
				info_tag.setPlot(' ')
				yield (url, listitem, False)
			except: pass
	try:
		j_folder = json.loads(folder)
		links = [i for i in j_folder if i['filename'].lower().endswith(tuple(supported_video_extensions()))]
	except: links = []
	handle = int(sys.argv[1])
	icon, fanart = kodi_utils.get_icon('alldebrid'), kodi_utils.get_addon_fanart()
	kodi_utils.add_items(handle, list(_builder()))
	kodi_utils.set_content(handle, 'files')
	kodi_utils.end_directory(handle, cacheToDisc=False)
	kodi_utils.set_view_mode('view.premium')

def resolve_ad(params):
	url = params['url']
	resolved_link = AllDebrid.unrestrict_link(url)
	if params.get('play', 'false') != 'true' : return resolved_link
	from modules.player import FenLightPlayer
	FenLightPlayer().run(resolved_link, 'video')

def ad_delete(file_id):
	if not kodi_utils.show_text(): return
	result = AllDebrid.delete_transfer(file_id)
	if not result: return kodi_utils.notification('Error')
	AllDebrid.clear_cache()
	kodi_utils.execute_builtin('Container.Refresh')

def ad_account_info():
	try:
		kodi_utils.show_busy_dialog()
		account_info = AllDebrid.account_info()['user']
		username = account_info['username']
		email = account_info['email']
		status = 'Premium' if account_info['isPremium'] else 'Not Active'
		expires = datetime.fromtimestamp(account_info['premiumUntil'])
		days_remaining = (expires - datetime.today()).days
		body = []
		append = body.append
		append('[B]Username:[/B] %s' % username)
		append('[B]Email:[/B] %s' % email)
		append('[B]Status:[/B] %s' % status)
		append('[B]Expires:[/B] %s' % expires)
		append('[B]Days Remaining:[/B] %s' % days_remaining)
		kodi_utils.hide_busy_dialog()
		return kodi_utils.show_text('ALL DEBRID', '\n\n'.join(body), font_size='large')
	except: kodi_utils.hide_busy_dialog()

def active_days():
	try:
		account_info = AllDebrid.account_info()['user']
		expires = datetime.fromtimestamp(account_info['premiumUntil'])
		days_remaining = (expires - datetime.today()).days
	except: days_remaining = 0
	return days_remaining

