# -*- coding: utf-8 -*-
import os
import sys
import ssl
import json
from threading import Thread
from urllib.request import Request, urlopen
from urllib.parse import parse_qsl, urlparse, unquote
from modules import kodi_utils
from modules.sources import Sources, PROP_RESOLVE_CANCEL
from modules.settings import download_directory, store_resolved_to_cloud
from modules.debrid import normalize_debrid_provider
from modules.source_utils import clean_title
from modules.utils import clean_file_name, safe_string, remove_accents, normalize
# logger = kodi_utils.logger

NO_DOWNLOAD_URL_MSG = 'No URL found for Download. Pick another Source'

def runner(params):
	action = params.get('action')
	if action == 'image':
		for item in ('thumb_url', 'image_url'):
			image_params = params
			image_params['url'] = params.pop(item)
			image_params['media_type'] = item
			Downloader(image_params).run()
	elif action == 'meta.pack':
		from modules.source_utils import find_season_in_release_title
		from modules.debrid import ExternalPackSource, downloader_provider_slug
		source, meta = json.loads(params['source']), json.loads(params['meta'])
		pack_source = ExternalPackSource(source, meta)
		pack_result = pack_source.browse_packs(download=True)
		if not pack_result:
			return
		pack_choices, pack_api = pack_result
		provider = downloader_provider_slug(getattr(pack_source, 'debrid', '') or source.get('cache_provider', ''))
		pack_items = [dict(params, **{'pack_files': item, 'provider': provider}) for item in pack_choices]
		icon = {'real-debrid': 'realdebrid', 'premiumize.me': 'premiumize', 'alldebrid': 'alldebrid', 'offcloud': 'offcloud', 'torbox': 'torbox'}.get(provider, 'box_office')
		chosen_list = select_pack_item(pack_items, kodi_utils.get_icon(icon))
		if not chosen_list: return
		show_package = source.get('package') == 'show'
		image = meta.get('poster') or kodi_utils.get_icon('box_office')
		default_name = '%s (%s)' % (clean_file_name(get_title(meta)), get_year(meta))
		default_foldername = kodi_utils.kodi_dialog().input('Title', defaultt=default_name)
		threads = []
		threads_append = threads.append
		for item in chosen_list:
			if show_package:
				season = find_season_in_release_title(item['pack_files']['filename'])
				if season:
					meta['season'] = season
					item['meta'] = json.dumps(meta)
					item['default_foldername'] = default_foldername
			threads_append(Thread(target=Downloader(item).run))
		kodi_utils.notification('Multi File Pack Download Started...', 3500, image)
		for thread in threads:
			thread.start()
		if provider == 'torbox' and pack_choices and not store_resolved_to_cloud('TorBox', True):
			torrent_id = pack_choices[0].get('torrent_id')
			if torrent_id:
				def _cleanup():
					for thread in threads:
						thread.join()
					try: pack_api.delete_torrent(torrent_id)
					except: pass
				Thread(target=_cleanup, daemon=True).start()
	else: Downloader(params).run()

def download_threads_manager(multi_downloads, image, pack_cleanup=None):
	kodi_utils.notification('Multi File Pack Download Started...', 3500, image)
	started_downloads = []
	started_downloads_append = started_downloads.append
	for item in multi_downloads:
		while len([x for x in multi_downloads if x[0].is_alive()]) >= 2:
			kodi_utils.sleep(2000)
			continue
		item[0].start()
		started_downloads_append(item)
		remaining_downloads = [x[1] for x in multi_downloads if not x in started_downloads]
		kodi_utils.set_property('redlight.active_queued_downloads', json.dumps(remaining_downloads))
	kodi_utils.clear_property('redlight.active_queued_downloads')
	if pack_cleanup:
		torrent_id, debrid_function = pack_cleanup
		if not store_resolved_to_cloud('TorBox', True):
			try: debrid_function().delete_torrent(torrent_id)
			except: pass

def select_pack_item(pack_choices, icon):
	list_items = [{'line1': '%.2f GB | %s' % (float(item['pack_files']['size'])/1073741824, clean_file_name(item['pack_files']['filename']).upper()), 'icon': icon} \
				for item in pack_choices]
	heading = 'Choose Files to Download - %s' % clean_file_name(json.loads(pack_choices[0].get('source')).get('name'))
	kwargs = {'items': json.dumps(list_items), 'heading': heading, 'enumerate': 'true', 'multi_choice': 'true'}
	return kodi_utils.select_dialog(pack_choices, **kwargs)

def get_title(meta):
	title = meta.get('custom_title', None) or meta.get('english_title') or meta.get('title')	
	return title

def get_year(meta):
	return meta.get('custom_year', None) or meta.get('year')

def get_season(meta):
		season = meta.get('custom_season', None) or meta.get('season')
		return int(season) if season else None

def _sanitize_path_name(name):
	if not name:
		return ''
	for char in r'\/:*?"<>|':
		name = name.replace(char, '')
	return name.strip('. ')

def _video_extension(name):
	if not name:
		return ''
	ext = os.path.splitext(name)[1].lstrip('.').lower()
	if ext in kodi_utils.video_extensions():
		return ext
	return ''

def _release_name_from_source(source_json):
	try:
		source = json.loads(source_json) if isinstance(source_json, str) else (source_json or {})
		for key in ('name', 'display_name'):
			val = (source.get(key) or '').strip()
			if val: return val
	except: pass
	return ''

class Downloader:
	def __init__(self, params):
		self.params = params
		self.params_get = self.params.get

	def run(self):
		kodi_utils.show_busy_dialog()
		self.download_prep()
		self.get_url_and_headers()
		if self.url in (None, 'None', ''): return self.return_notification(_notification=NO_DOWNLOAD_URL_MSG)
		self.get_filename()
		self.get_extension()
		if not self.download_check():
			if self.media_type == 'thumb_url': return
			return self.return_notification(_ok_dialog='Failed')
		if not self.confirm_download(): return self.return_notification(_notification='Cancelled')
		self.get_download_folder()
		if not self.get_destination_folder(): return self.return_notification(_notification='Cancelled')
		self.download_runner()

	def _is_torbox_download(self, url=None):
		if 'torbox' in (self.action or ''):
			return True
		if self.provider in ('torbox', 'TorBox', 'Torbox', 'tb_cloud'):
			return True
		try:
			source = json.loads(self.source) if self.source else {}
			if normalize_debrid_provider(source.get('debrid') or source.get('cache_provider', '')) == 'TorBox':
				return True
		except:
			pass
		check_url = (url or self.url or '').lower()
		return 'tb-cdn' in check_url or 'torbox.app' in check_url

	def download_prep(self):
		if 'meta' in self.params:
			self.meta = json.loads(self.params_get('meta'))
			self.meta_get = self.meta.get
			self.media_type = self.meta_get('media_type')
			self.title = clean_file_name(get_title(self.meta))
			self.year = get_year(self.meta)
			self.season = get_season(self.meta)
			self.image = self.meta_get('poster') or kodi_utils.get_icon('box_office')
			self.name = self.params_get('name')
		else:
			self.meta, self.year, self.season = None, None, None
			self.media_type = self.params_get('media_type')
			self.name = self.params_get('name')
			self.title = clean_file_name(self.name or '')
			self.image = self.params_get('image')
		self.provider = self.params_get('provider')
		self.action = self.params_get('action')
		self.source = self.params_get('source')
		if self.action == 'meta.single' and self.source:
			release = _release_name_from_source(self.source)
			if release: self.name = release
		self.final_name = None

	def download_runner(self):
		self.final_destination = os.path.join(self.final_destination, self.final_name + self.extension)
		self.add_active_download()
		self.start_download()

	def get_active_downloads(self):
		return json.loads(kodi_utils.get_property('redlight.active_downloads') or '[]')

	def add_active_download(self):
		if self.action == 'image': return
		active_downloads = self.get_active_downloads()
		active_downloads.append(self.final_name)
		kodi_utils.set_property('redlight.active_downloads', json.dumps(active_downloads))

	def remove_active_download(self):
		if self.action == 'image': return
		active_downloads = self.get_active_downloads()
		try: active_downloads.remove(self.final_name)
		except: pass
		if active_downloads: kodi_utils.set_property('redlight.active_downloads', json.dumps(active_downloads))
		else: self.clear_active_downloads()

	def clear_active_downloads(self):
		kodi_utils.clear_property('redlight.active_downloads')

	def set_percent_property(self, percent):
		kodi_utils.set_property('redlight.%s' % self.final_name, str(percent))

	def check_status(self):
		status = kodi_utils.get_property('redlight.download_status.%s' % self.final_name)
		if status in ('unpaused', 'cancelled'): kodi_utils.clear_property('redlight.download_status.%s' % self.final_name)
		return status

	def get_url_and_headers(self):
		url = self.params_get('url')
		if url in (None, 'None', ''):
			if self.action == 'meta.single':
				try:
					source = json.loads(self.source)
					if source.get('scrape_provider', '') == 'easynews': source['url_dl'] = source['down_url']
					kodi_utils.clear_property(PROP_RESOLVE_CANCEL)
					url = Sources().resolve_sources(source, meta=self.meta)
					if url and self._is_torbox_download(url):
						from apis.torbox_api import TorBoxAPI
						url = TorBoxAPI().add_headers_to_url(url)
				except: pass
			elif self.action == 'meta.pack':
				debrid_function = None
				if self.provider in ('real-debrid', 'Real-Debrid'):
					from apis.real_debrid_api import RealDebridAPI as debrid_function
				elif self.provider in ('premiumize.me', 'Premiumize.me'):
					from apis.premiumize_api import PremiumizeAPI as debrid_function
				elif self.provider in ('alldebrid', 'AllDebrid'):
					from apis.alldebrid_api import AllDebridAPI as debrid_function
				elif self.provider in ('torbox', 'TorBox', 'Torbox'):
					from apis.torbox_api import TorBoxAPI as debrid_function
				elif self.provider in ('offcloud', 'Offcloud'):
					from apis.offcloud_api import OffcloudAPI as debrid_function
				link = self.params_get('pack_files', {}).get('link')
				if not link:
					url = None
				elif debrid_function and self.provider in ('real-debrid', 'Real-Debrid'):
					url = debrid_function().unrestrict_link(link)
				elif debrid_function and self.provider in ('premiumize.me', 'Premiumize.me'):
					url = debrid_function().add_headers_to_url(link)
				elif debrid_function and self.provider in ('alldebrid', 'AllDebrid'):
					url = debrid_function().unrestrict_link(link)
				elif debrid_function and self.provider in ('torbox', 'TorBox', 'Torbox'):
					api = debrid_function()
					url = api.unrestrict_link(link)
					if url:
						url = api.add_headers_to_url(url)
					else:
						return self.return_notification(_notification='TorBox: Download link not ready. Wait until the torrent is finished in TorBox, then try Download Pack again.')
				elif self.provider in ('offcloud', 'Offcloud'):
					# display_magnet_pack / cache_download already returns direct Offcloud CDN URLs
					url = link
				else:
					url = None
		else:
			if self.action.startswith('cloud'):
				if '_direct' in self.action:
					url = self.params_get('url')
				elif 'realdebrid' in self.action:
					from indexers.real_debrid import resolve_rd
					url = resolve_rd(self.params)
				elif 'alldebrid' in self.action:
					from indexers.alldebrid import resolve_ad
					url = resolve_ad(self.params)
				elif 'premiumize' in self.action:
					from apis.premiumize_api import PremiumizeAPI
					url = PremiumizeAPI().add_headers_to_url(url)
				elif 'torbox' in self.action:
					from apis.torbox_api import TorBoxAPI
					api = TorBoxAPI()
					file_id = self.params_get('url')
					media_type = self.params_get('media_type') or 'torrent'
					if media_type == 'torrent':
						url = api.unrestrict_link(file_id)
					elif media_type == 'webdl':
						url = api.unrestrict_webdl(file_id)
					else:
						url = api.unrestrict_usenet(file_id)
					if not url:
						return self.return_notification(_notification='TorBox: Unable to resolve download link')
					url = api.add_headers_to_url(url)
				elif 'easynews' in self.action:
					from indexers.easynews import resolve_easynews
					url = resolve_easynews(self.params)
		try: headers = dict(parse_qsl(url.rsplit('|', 1)[1]))
		except: headers = dict('')
		try: url = url.split('|')[0]
		except: pass
		self.url = url
		self.headers = headers

	def get_download_folder(self):
		self.down_folder = download_directory(self.media_type)
		if self.media_type == 'thumb_url': self.down_folder = os.path.join(self.down_folder, '.thumbs')
		for level in ['../../../..', '../../..', '../..', '..']:
			try: kodi_utils.make_directory(os.path.abspath(os.path.join(self.down_folder, level)))
			except: pass

	def get_destination_folder(self):
		if self.action == 'image':
			self.final_destination = self.down_folder
		elif self.action in ('meta.single', 'meta.pack'):
			default_name = '%s (%s)' % (self.title, self.year)
			if self.action == 'meta.single': folder_rootname = kodi_utils.kodi_dialog().input('Title', defaultt=default_name)
			else: folder_rootname = self.params_get('default_foldername', default_name)
			if not folder_rootname: return False
			if self.media_type == 'episode':
				inter = os.path.join(self.down_folder, folder_rootname)
				kodi_utils.make_directory(inter)
				self.final_destination = os.path.join(inter, 'Season %02d' %  int(self.season))
			else: self.final_destination = os.path.join(self.down_folder, folder_rootname)
		else: self.final_destination = self.down_folder
		kodi_utils.make_directory(self.final_destination)
		return True

	def get_filename(self):
		if self.final_name: final_name = self.final_name
		elif self.action == 'meta.pack':
			name = self.params_get('pack_files')['filename']
			final_name = os.path.splitext(urlparse(name).path)[0].split('/')[-1]
		elif self.action == 'image':
			final_name = self.title
		else:
			name_url = unquote(self.url)
			file_name = clean_title(name_url.split('/')[-1])
			if self.action == 'meta.single':
				release = _release_name_from_source(self.source)
				if release:
					base = os.path.splitext(release)[0] or release
					final_name = _sanitize_path_name(base) or _sanitize_path_name(release)
				elif clean_title(self.title).lower() in file_name.lower():
					final_name = os.path.splitext(urlparse(name_url).path)[0].split('/')[-1]
				else:
					name_ref = (self.name or self.title or '').strip()
					if name_ref:
						base = os.path.splitext(name_ref)[0] or name_ref
						final_name = _sanitize_path_name(base) or _sanitize_path_name(name_ref)
					else:
						final_name = os.path.splitext(urlparse(name_url).path)[0].split('/')[-1]
			elif clean_title(self.title).lower() in file_name.lower():
				final_name = os.path.splitext(urlparse(name_url).path)[0].split('/')[-1]
			else:
				name_ref = (self.name or self.title or '').strip()
				if name_ref:
					base = os.path.splitext(name_ref)[0] or name_ref
					final_name = _sanitize_path_name(base) or _sanitize_path_name(name_ref)
				else:
					final_name = os.path.splitext(urlparse(name_url).path)[0].split('/')[-1]
			if not final_name:
				final_name = os.path.splitext(urlparse(name_url).path)[0].split('/')[-1] or 'download'
		self.final_name = safe_string(remove_accents(final_name))

	def get_extension(self):
		if self.action == 'archive':
			ext = 'zip'
		elif self.action == 'image':
			ext = os.path.splitext(urlparse(self.url).path)[1][1:]
			if not ext in kodi_utils.image_extensions(): ext = 'jpg'
		else:
			ext = _video_extension(self.name or self.title or '')
			if not ext:
				ext = os.path.splitext(urlparse(self.url).path)[1][1:]
			if not ext in kodi_utils.video_extensions(): ext = 'mp4'
		ext = '.%s' % ext
		self.extension = ext

	def download_check(self):
		self.content_unknown = False
		self.resp = self.get_response()
		if not self.resp: return False
		try: self.content = int(self.resp.headers.get('Content-Length') or 0)
		except: self.content = 0
		try: self.resumable = 'bytes' in self.resp.headers.get('Accept-Ranges', '').lower()
		except: self.resumable = False
		self.size = 1024 * 1024
		if self.content < 1:
			self.content_unknown = True
			self.mb = 0
			kodi_utils.hide_busy_dialog()
			return True
		self.mb = self.content / (1024 * 1024)
		if self.content < self.size: self.size = self.content
		kodi_utils.hide_busy_dialog()
		return True

	def start_download(self):
		if self.action == 'meta.pack':
			kodi_utils.notification('Pack download started: %s' % self.final_name.replace('.', ' ').replace('_', ' '), 3000, self.image)
		monitor_progress = self.action != 'image'
		total, errors, count, resume, sleep_time  = 0, 0, 0, 0, 0
		f = kodi_utils.open_file(self.final_destination, 'w')
		chunk  = None
		chunks = []
		while True:
			downloaded = total
			for c in chunks: downloaded += len(c)
			if self.content_unknown:
				percent = min(99, downloaded // (50 * 1024 * 1024)) if downloaded else 0
			else:
				percent = min(round(float(downloaded) * 100 / self.content), 100)
			if monitor_progress:
				status = self.check_status()
				if status == 'paused':
					while status == 'paused':
						status = self.check_status()
						kodi_utils.sleep(1000)
				if status == 'cancelled': return self.finish_download(status)
				if percent % 5 == 0: self.set_percent_property(percent)
			chunk = None
			error = False
			try:        
				chunk  = self.resp.read(self.size)
				if not chunk:
					if not self.content_unknown and percent < 99:
						error = True
					else:
						while len(chunks) > 0:
							c = chunks.pop(0)
							f.write(c)
							del c
						f.close()
						return self.finish_download('success')
			except Exception as e:
				error = True
				sleep_time = 10
				errno = 0
				if hasattr(e, 'errno'):
					errno = e.errno
				if errno == 10035: # 'A non-blocking socket operation could not be completed immediately'
					pass
				if errno == 10054: #'An existing connection was forcibly closed by the remote host'
					errors = 10 #force resume
					sleep_time = 30
				if errno == 11001: # 'getaddrinfo failed'
					errors = 10 #force resume
					sleep_time = 30
			if chunk:
				errors = 0
				chunks.append(chunk)
				if len(chunks) > 5:
					c = chunks.pop(0)
					f.write(c)
					total += len(c)
					del c
			if error:
				errors += 1
				count  += 1
				kodi_utils.sleep(sleep_time*1000)
			if (self.resumable and errors > 0) or errors >= 10:
				if (not self.resumable and resume >= 50) or resume >= 500:
					return self.finish_download('failed')
				resume += 1
				errors  = 0
				if self.resumable:
					chunks  = []
					self.resp = self.get_response(total)
				else: pass

	def get_response(self, size=0):
		try:
			headers = dict(self.headers or {})
			if self._is_torbox_download():
				headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
				headers.setdefault('Referer', 'https://torbox.app/')
			if size > 0:
				size = int(size)
				headers['Range'] = 'bytes=%d-' % size
			req = Request(self.url, headers=headers)
			timeout = 60 if self._is_torbox_download() else 30
			resp = urlopen(req, context=ssl.create_default_context(), timeout=timeout)
			return resp
		except: return None

	def finish_download(self, status):
		if self.action == 'image':
			if self.media_type == 'image_url': return kodi_utils.notification(status.upper(), 2500, self.final_destination)
			else: return
		if not kodi_utils.get_visibility('Window.IsActive(fullscreenvideo)'):
			kodi_utils.notification('[B]%s[/B] %s' % (status.upper(), self.final_name.replace('.', ' ').replace('_', ' ')), 2500, self.image)
		self.remove_active_download()

	def confirm_download(self):
		if self.action in ('image', 'meta.pack'):
			return True
		if getattr(self, 'content_unknown', False):
			text = 'File size could not be determined from the server.[CR]Continue with download?'
		else:
			text = 'Complete file is [B]%dMB[/B][CR]Continue with download?' % self.mb
		return kodi_utils.confirm_dialog(heading=self.final_name, text=text)

	def return_notification(self, _notification=None, _ok_dialog=None):
		kodi_utils.hide_busy_dialog()
		if _notification: kodi_utils.notification(_notification, 2500)
		elif _ok_dialog: kodi_utils.ok_dialog(text=_ok_dialog)
		else: return

def viewer(params):
	def _process():
		for info in results:
			try:
				path = info[0]
				url = os.path.join(folder_path, path)
				listitem = kodi_utils.make_listitem()
				listitem.setLabel(clean_file_name(normalize(path)))
				listitem.setArt({'fanart': fanart})
				info_tag = listitem.getVideoInfoTag(True)
				info_tag.setPlot(' ')
				yield (url, listitem, info[1])
			except: pass
	handle = int(sys.argv[1])
	fanart = kodi_utils.get_addon_fanart()
	folder_path = download_directory(params['folder_type'])
	dirs, files = kodi_utils.list_dirs(folder_path)
	results = [(i, True) for i in dirs] + [(i, False) for i in files]
	item_list = list(_process())
	kodi_utils.add_items(handle, item_list)
	kodi_utils.set_sort_method(handle, 'files')
	kodi_utils.set_content(handle, kodi_utils.MENU_FOLDER_CONTENT)
	kodi_utils.set_category(handle, params.get('name'))
	kodi_utils.end_directory(handle)
	kodi_utils.set_view_mode('view.main', kodi_utils.MENU_FOLDER_CONTENT, False)

def manager(foo=None):
	from windows.base_window import open_window
	kwargs = {}
	return open_window(('windows.downloads_manager', 'DownloadsManager'), 'downloads_manager.xml', **kwargs)
