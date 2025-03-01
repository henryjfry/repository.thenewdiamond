# -*- coding: utf-8 -*-
#from __future__ import absolute_import, division, unicode_literals

import time

#from database.cache import use_cache

import os
try:
	from thread_pool import ThreadPool
	import tools
except:
	from a4kscrapers_wrapper import tools
	from a4kscrapers_wrapper.thread_pool import ThreadPool
	
import requests	

try:
	from functools import cached_property  # Supported from py3.8
except ImportError:
	try: from resources.lib.third_party.cached_property import cached_property
	except: from cached_property import cached_property

from inspect import currentframe, getframeinfo
#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

RD_AUTH_KEY = "rd.auth"
RD_STATUS_KEY = "rd.premiumstatus"
RD_REFRESH_KEY = "rd.refresh"
RD_EXPIRY_KEY = "rd.expiry"
RD_SECRET_KEY = "rd.secret"
RD_CLIENT_ID_KEY = "rd.client_id"
RD_USERNAME_KEY = "rd.username"
RD_AUTH_CLIENT_ID = "X245A4XAIBGVM"

class RealDebrid:

	def __init__(self):
		self.oauth_url = "https://api.real-debrid.com/oauth/v2/"
		self.device_code_url = "device/code?{}"
		self.device_credentials_url = "device/credentials?{}"
		self.token_url = "token"
		self.device_code = ""
		self.oauth_timeout = 0
		self.oauth_time_step = 0
		self.base_url = "https://api.real-debrid.com/rest/1.0/"
		self.cache_check_results = {}
		self._load_settings()
		self.UNRESTRICT_FILE = None
		self.UNRESTRICT_FILE_ID = None
		self.UNRESTRICT_FILE_SIZE = None
		self.original_tot_bytes = None
		self.original_start_time = None
		self.remaining_tot_bytes = None
		self.num_lines = None

	@cached_property
	def session(self):
		import requests
		from requests.adapters import HTTPAdapter
		from urllib3 import Retry
		session = requests.Session()
		retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
		session.mount("https://", HTTPAdapter(max_retries=retries, pool_maxsize=100))
		return session

	def _auth_loop(self):
		url = "client_id={}&code={}".format(RD_AUTH_CLIENT_ID, self.device_code)
		url = self.oauth_url + self.device_credentials_url.format(url)
		response = self.session.get(url).json()
		if "error" not in response and response.get("client_secret"):
			try:
				tools.set_setting(RD_CLIENT_ID_KEY, response["client_id"])
				tools.set_setting(RD_SECRET_KEY, response["client_secret"])
				self.client_secret = response["client_secret"]
				self.client_id = response["client_id"]
				return True
			except Exception:
				#xbmcgui.Dialog().ok(g.ADDON_NAME, g.get_language_string(30065))
				tools.log("Authentication with Real-Debrid has failed, please try again")
				raise
		return False

	def auth_kodi(self):
		import xbmcgui, xbmc
		#url = "client_id={}&new_credentials=yes".format(self.client_id)
		#url = self.oauth_url + self.device_code_url.format(url)
		#url = "client_id={}&code={}".format(RD_AUTH_CLIENT_ID, self.device_code)
		#tools.log(url)
		#url = self.oauth_url + self.device_credentials_url.format(url)
		#tools.log(url)
		self.client_id = tools.get_setting("rd.client_id")
		if str(self.client_id).strip() == '' or str(self.client_id).strip() == None or self.client_id == None:
			self.client_id = RD_AUTH_CLIENT_ID
		url = "client_id={}&new_credentials=yes".format(self.client_id)
		url = self.oauth_url + self.device_code_url.format(url)
		#tools.log(RD_AUTH_CLIENT_ID)
		#tools.log(self.client_id)
		#tools.log(url)
		response = self.session.get(url).json()
		#tools.log(response)
		#tools.copy2clip(response["user_code"])
		success = False
		try:
			line1=str("Open this link in a browser: {}").format(str("https://real-debrid.com/device"))
			line2=str("Enter the code: {}").format(str(response["user_code"]))
			line3=str("This code has NOT! been copied to your clipboard")
			progress_dialog = xbmcgui.DialogProgress()
			progress_dialog.create(
				tools.ADDON_NAME + ": " + str('Real-Debrid Auth'),
				line1+'\n'+line2+'\n'+line3,
			)
			self.oauth_timeout = int(response["expires_in"])
			token_ttl = int(response["expires_in"])
			self.oauth_time_step = int(response["interval"])
			self.device_code = response["device_code"]
			progress_dialog.update(100)
			while (
				not success
				and not token_ttl <= 0
				and not progress_dialog.iscanceled()
			):
				xbmc.sleep(1000)
				if token_ttl % self.oauth_time_step == 0:
					success = self._auth_loop()
				progress_percent = int(float((token_ttl * 100) / self.oauth_timeout))
				progress_dialog.update(progress_percent)
				token_ttl -= 1
			progress_dialog.close()
		finally:
			del progress_dialog

		if success:
			self.token_request()

			user_information = self.get_url("user")
			if user_information["type"] != "premium":
				xbmcgui.Dialog().ok(Utils.ADDON_NAME, "You appear to have authorized a non-premium account and will not be able to play items using this account")

	def auth(self):
		self.client_id = tools.get_setting("rd.client_id")
		if self.client_id == '':
			self.client_id = RD_AUTH_CLIENT_ID
		url = "client_id={}&new_credentials=yes".format(self.client_id)
		url = self.oauth_url + self.device_code_url.format(url)
		response = self.session.get(url).json()
		tools.copy2clip(response["user_code"])
		success = False
		
		try:
			line1=str("Open this link in a browser: {}").format(str("https://real-debrid.com/device"))
			line2=str("Enter the code: {}").format(str(response["user_code"]))
			line3=str("This code has been copied to your clipboard")
			tools.log(line1)
			tools.log(line2)
			tools.log(line3)
			tools.log('RD_AUTH_RUNNING_FOR_90s')
			start_time = time.time()
			self.oauth_timeout = int(response["expires_in"])
			token_ttl = int(response["expires_in"])
			self.oauth_time_step = int(response["interval"])
			self.device_code = response["device_code"]
			#while (
			#	not success
			#	and not token_ttl <= 0
			#	and not time.time() > start_time + 90
			#):
			for i in tools.progressbar(range(100), "AUTH: ", 40):
				time.sleep(1) # any code you need
				if token_ttl % self.oauth_time_step == 0:
					success = self._auth_loop()
				progress_percent = int(float((token_ttl * 100) / self.oauth_timeout))
				#progress_dialog.update(progress_percent)
				#tools.log('progress_percent=', progress_percent)
				token_ttl -= 1
				if not success and not token_ttl <= 0 and not time.time() > start_time + 90:
					continue
				else:
					break
			tools.log('success??')
		finally:
			tools.log('finally_success')

		if success:
			self.token_request()

			user_information = self.get_url("user")
			if user_information["type"] != "premium":
				#xbmcgui.Dialog().ok(g.ADDON_NAME, g.get_language_string(30194))
				tools.log("You appear to have authorized a non-premium account and will not be able to play items using this account")
			else:
				tools.log('RD_AUTH_SUCCESS')

	def token_request(self):
		if not self.client_secret:
			return

		url = self.oauth_url + self.token_url
		response = self.session.post(
			url,
			data={
				"client_id": self.client_id,
				"client_secret": self.client_secret,
				"code": self.device_code,
				"grant_type": "http://oauth.net/grant_type/device/1.0",
			},
		).json()
		self._save_settings(response)
		self._save_user_status()
		#xbmcgui.Dialog().ok(g.ADDON_NAME, "Real Debrid " + g.get_language_string(30020))
		tools.log("Authentication is completed")

	def _save_settings(self, response):
		self.token = response["access_token"]
		self.refresh = response["refresh_token"]
		self.expiry = time.time() + int(response["expires_in"])

		#tools.log(RD_AUTH_KEY, self.token)
		#tools.log(RD_REFRESH_KEY, self.refresh)
		#tools.log(RD_EXPIRY_KEY, self.expiry)
		tools.set_setting(RD_AUTH_KEY, self.token)
		tools.set_setting(RD_REFRESH_KEY, self.refresh)
		tools.set_setting(RD_EXPIRY_KEY, self.expiry)

	def _save_user_status(self):
		username = self.get_url("user").get("username")
		status = self.get_account_status().title()
		tools.set_setting(RD_USERNAME_KEY, username)
		tools.set_setting(RD_STATUS_KEY, status)

	def _load_settings(self):
		#self.client_id = g.get_setting("rd.client_id", RD_AUTH_CLIENT_ID)
		self.client_id = tools.get_setting("rd.client_id")
		self.token = tools.get_setting(RD_AUTH_KEY)
		self.refresh = tools.get_setting(RD_REFRESH_KEY)
		try: self.expiry = tools.get_setting(RD_EXPIRY_KEY,'float')
		except: self.expiry = time.time() - 1
		self.client_secret = tools.get_setting(RD_SECRET_KEY)

	@staticmethod
	def _handle_error(response):
		tools.log("Real Debrid API return a {} response".format(response.status_code))
		tools.log(response.text)
		tools.log(response.request.url)

	def _is_response_ok(self, response):
		if not response:
			tools.log("Real Debrid API return a {} response".format('ERROR'))
			return False
		if 200 <= response.status_code < 400:
			return True
		if response.status_code > 400:
			self._handle_error(response)
			return False

	def try_refresh_token(self, force=False):
		if not self.refresh:
			return
		if not force and self.expiry > float(time.time()):
			return

		try:
			with tools.GlobalLock(self.__class__.__name__, True, self.token):
				url = self.oauth_url + "token"
				response = self.session.post(
					url,
					data={
						"grant_type": "http://oauth.net/grant_type/device/1.0",
						"code": self.refresh,
						"client_secret": self.client_secret,
						"client_id": self.client_id,
					},
				)
				retry_count = 0
				while response and ('502 Bad Gateway' in str(response) or '502 Bad Gateway' in str(response.text)):
					time.sleep(2)
					response = self.session.post(url,data={"grant_type": "http://oauth.net/grant_type/device/1.0","code": self.refresh,"client_secret": self.client_secret,"client_id": self.client_id,},)
					retry_count = retry_count + 1
					if retry_count > 5:
						tools.log("Failed to refresh RD token, please manually re-auth")
						self._handle_error(response)
						return False
				if response and ('502 Bad Gateway' in str(response) or '502 Bad Gateway' in str(response.text)):
					tools.log("Failed to refresh RD token, please manually re-auth")
					return False
				if not self._is_response_ok(response):
					response = response.json()
					tools.log(
						 "Failed to refresh RD token, please manually re-auth"
					)
					tools.log("RD Refresh error: {}".format(response["error"]))
					tools.log(
						"Invalid response from Real Debrid - {}".format(response), "error"
					)
					return False
				response = response.json()
				self._save_settings(response)
				tools.log("Real Debrid Token Refreshed")
				return True
		except tools.RanOnceAlready:
			self._load_settings()
			return

	def _get_headers(self):
		headers = {
			"Content-Type": "application/json",
		}
		if self.token:
			headers["Authorization"] = "Bearer {}".format(self.token)
		return headers

	def post_url(self, url, post_data, fail_check=False):
		original_url = url
		url = self.base_url + url
		if not self.token:
			return None

		response = self.session.post(url, data=post_data, headers=self._get_headers(), timeout=5)
		if 'infringing_file' in str(response.text) or '{files} is missing' in str(response.text) or 'too_manny_requests' in str(response.text) or 'unknown_ressource' in str(response.text):
			tools.log('infringing_file__{files} is missing_unknown_ressource')
			return None
		if not self._is_response_ok(response) and not fail_check:
			#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			self.try_refresh_token(True)
			response = self.post_url(original_url, post_data, fail_check=True)
		try:
			return response.json()
		except (ValueError, AttributeError):
			return response

	def get_url(self, url, post_data=None, fail_check=False):
		if post_data:
			import requests
		original_url = url
		url = self.base_url + url
		if not self.token:
			tools.log("No Real Debrid Token Found")
			return None

		if post_data:
			response = requests.get(url, params=post_data, headers=self._get_headers(), timeout=5)
		else:
			response = self.session.get(url, headers=self._get_headers(), timeout=5)

		if 'infringing_file' in str(response.text) or '{files} is missing' in str(response.text) or 'too_manny_requests' in str(response.text) or 'unknown_ressource' in str(response.text):
			tools.log('infringing_file__{files} is missing_unknown_ressource')
			return None
		if not self._is_response_ok(response) and 'Max retries exceeded with url' in str(response.text):
			return response

		if not self._is_response_ok(response) and not fail_check:
			#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			self.try_refresh_token(True)
			response = self.get_url(original_url, post_data=post_data, fail_check=True)
		try:
			return response.json()
		except (ValueError, AttributeError):
			return response

	def delete_url(self, url, fail_check=False):
		original_url = url
		url = self.base_url + url
		if not self.token:
			tools.log("No Real Debrid Token Found")
			return None

		response = self.session.delete(url, headers=self._get_headers(), timeout=5)
		if 'infringing_file' in str(response.text) or '{files} is missing' in str(response.text) or 'too_manny_requests' in str(response.text) or 'unknown_ressource' in str(response.text):
			tools.log('infringing_file__{files} is missing_unknown_ressource')
			return None
		if not self._is_response_ok(response) and not fail_check:
			#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			self.try_refresh_token(True)
			response = self.delete_url(original_url, fail_check=True)
		try:
			return response.json()
		except (ValueError, AttributeError):
			return response

	def check_hash(self, hash_list):
		if isinstance(hash_list, list):
			#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			hash_list = [hash_list[x : x + 100] for x in range(0, len(hash_list), 100)]
			thread = ThreadPool()
			for section in hash_list:
				thread.put(self._check_hash_thread, sorted(section))
			thread.wait_completion()
			return self.cache_check_results
		else:
			tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			#hash_string = "/" + hash_list
			#return self.get_url("torrents/instantAvailability" + hash_string)
			magnet = 'magnet:?xt=urn:btih:' + hash_list
			response = self.add_magnet(magnet)
			try: torr_id = response['id']
			except: return {}
			RD_STATUS = None
			try: response = self.torrent_select_all(torr_id)
			except TypeError: RD_STATUS = 'error'
			if not RD_STATUS:
				response = self.torrent_info(torr_id)
			try: RD_STATUS = response['status']
			except: RD_STATUS = 'error'
			if RD_STATUS == 'downloaded':
				hash_dict = {hash_list: {'rd':[]}}
				for x in response['files']:
					if x['selected'] == 1:
						hash_dict[hash_list]['rd'].append({x['id']:{'filename':x['path'],'filesize':x['bytes']}})
				response = self.delete_torrent(torr_id)
				#tools.log(hash_dict)
				#self.cache_check_results.update(hash_dict)
				#return self.cache_check_results
				return hash_dict
			else:
				hash_dict = {hash_list: {'d':[]}}
				response = self.delete_torrent(torr_id)
				hash_dict[hash_list]['d'].append({1:{'filename':'','filesize':99}})
				return hash_dict

	def _check_hash_thread(self, hashes):
		hash_string = "/" + "/".join(hashes)
		#tools.log(str(hash_string))
		#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		for i in hashes:
			magnet = 'magnet:?xt=urn:btih:' + i
			response = self.add_magnet(magnet)
			#tools.log(response)
			try: torr_id = response['id']
			except: continue
			#response = self.torrent_select_all(torr_id)
			##tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			##tools.log(response)
			#response = self.torrent_info(torr_id)
			RD_STATUS = None
			try: response = self.torrent_select_all(torr_id)
			except TypeError: RD_STATUS = 'error'
			if not RD_STATUS:
				response = self.torrent_info(torr_id)
			#tools.log(response)
			try: RD_STATUS = response['status']
			except: RD_STATUS = 'error'
			if RD_STATUS == 'downloaded':
				hash_dict = {i: {'rd':[]}}
				for x in response['files']:
					if x['selected'] == 1:
						hash_dict[i]['rd'].append({x['id']:{'filename':x['path'],'filesize':x['bytes']}})
				response = self.delete_torrent(torr_id)
				#tools.log(hash_dict)
				self.cache_check_results.update(hash_dict)
			else:
				hash_dict = {i: {'d':[]}}
				response = self.delete_torrent(torr_id)
				hash_dict[i]['d'].append({1:{'filename':'','filesize':99}})
				self.cache_check_results.update(hash_dict)
		#response = self.get_url("torrents/instantAvailability" + hash_string)
		#self.cache_check_results.update(response)

	def add_magnet(self, magnet):
		post_data = {"magnet": magnet}
		url = "torrents/addMagnet"
		response = self.post_url(url, post_data)
		return response

	def list_downloads_page(self, page):
		post_data = {'page': page}
		url = "downloads"
		response = self.get_url(url, post_data=post_data)
		return response

	def list_torrents_page(self, page):
		post_data = {'page': page}
		url = "torrents"
		response = self.get_url(url, post_data=post_data)
		return response

	def list_downloads(self):
		url = "downloads"
		response = self.get_url(url)
		return response

	def list_torrents(self):
		url = "torrents"
		response = self.get_url(url)
		return response

	def torrent_info(self, id):
		url = "torrents/info/{}".format(id)
		response = self.get_url(url)
		#tools.log(response)
		return response

	def torrent_info_files(self, torr_info):
		files = []
		for i in torr_info['files']:
			if i['selected'] == 1:
				files.append(i)

		files_links = []
		release_name = torr_info['filename']
		full_pack_bytes = int(torr_info['bytes'])
		full_pack_original_bytes = int(torr_info['original_bytes'])
		fraction_of_pack = 0
		curr_diff_from_prev = 0
		for idx,i in enumerate(files):
			old_fraction_of_pack = fraction_of_pack
			fraction_of_pack = float(int(i['bytes'])/full_pack_original_bytes)*100
			if old_fraction_of_pack > 0:
				curr_diff_from_prev = float((old_fraction_of_pack - fraction_of_pack)/old_fraction_of_pack)*100
			file_path = os.path.join(tools.DOWNLOAD_FOLDER,release_name + i['path'])
			download_dir = os.path.join(tools.DOWNLOAD_FOLDER,release_name)
			try: unrestrict_link = torr_info['links'][idx]
			except: unrestrict_link = ''
			files_links.append({'unrestrict_link': unrestrict_link, 'pack_file_id': i['id'], 'pack_path': i['path'], 'pack_bytes': i['bytes'], 'download_path': file_path, 'download_dir': download_dir, 'full_pack_bytes': full_pack_bytes, 'full_pack_original_bytes': full_pack_original_bytes, 'fraction_of_pack': fraction_of_pack, 'curr_diff_from_prev': curr_diff_from_prev})
		torr_info['files_links'] = files_links
		torr_info['pack_length'] = len(torr_info['links'])
		fracs = []
		for i in torr_info['files_links']:
			fracs.append(i['fraction_of_pack'])
		for idx, i in enumerate(fracs):
			pc_of_max_frac = abs(100*((i-max(fracs))/max(fracs)))
			torr_info['files_links'][idx]['pc_of_max_frac'] = pc_of_max_frac
			if pc_of_max_frac > 45:
				torr_info['files_links'][idx]['double_ep'] = True
			else:
				torr_info['files_links'][idx]['double_ep'] = False
		return torr_info


	def torrent_select_all(self, torrent_id):
		torr_info = self.torrent_info(torrent_id)
		#tools.log(torr_info)
		file_string = ''
		for i in torr_info['files']:
			res = [ele for ele in self.common_video_extensions() if(ele in os.path.splitext(i['path'])[1])]
			if res and ('Sample' in i['path'] or 'sample.' in i['path']) == False:
				if file_string == '':
					file_string = file_string + str(i['id'])
				else:
					file_string = file_string + ',' + str(i['id'])

		file_id='all'
		#response = self.torrent_select(torrent_id,file_id)
		response = self.torrent_select(torrent_id,file_string)
		return response

	def torrent_select(self, torrent_id, file_id):
		url = "torrents/selectFiles/{}".format(torrent_id)
		post_data = {"files": file_id}
		return self.post_url(url, post_data)

	def delete_download(self, id):
		url = "downloads/delete/{}".format(id)
		self.delete_url(url)

	def headers_filesize(self,headers):
		filesize = int(headers['content-length'])
		if filesize < 65536 * 2:
			try: filesize = int(str(response.headers['content-range']).split('/')[1])
			except: filesize = 0
		self.UNRESTRICT_FILE_SIZE = filesize
		return filesize

	def test_download_link(self,download_link,rar_test=True):
		if not download_link:
			return None
		try: 
			headers=requests.head(download_link).headers
			filesize = self.headers_filesize(headers)
		except AttributeError:
			self.UNRESTRICT_FILE_ID = download_link.split('/')[4]
			self.delete_download(self.UNRESTRICT_FILE_ID)
			return None
		if download_link[-4:] == '.rar' and rar_test:
			self.UNRESTRICT_FILE_ID = download_link.split('/')[4]
			self.delete_download(self.UNRESTRICT_FILE_ID)
			return None
		self.UNRESTRICT_FILE_ID = download_link.split('/')[4]
		if not str('attachment') in headers.get('Content-Disposition',''):
			self.delete_download(self.UNRESTRICT_FILE_ID)
			return None
		else:
			return download_link

	def resolve_hoster(self, link):
		import requests
		url = "unrestrict/link"
		post_data = {"link": link}
		response = self.post_url(url, post_data)
		try:
			self.UNRESTRICT_FILE = response["download"]
			self.UNRESTRICT_FILE_ID = response["id"]
			try: 
				headers=requests.head(self.UNRESTRICT_FILE).headers
				filesize = self.headers_filesize(headers)
			except AttributeError:
				self.delete_download(self.UNRESTRICT_FILE_ID)
				return None
			if not str('attachment') in headers.get('Content-Disposition',''):
				self.delete_download(self.UNRESTRICT_FILE_ID)
				return None
			return response["download"]
		except KeyError:
			return None

	def delete_torrent(self, id):
		url = "torrents/delete/{}".format(id)
		self.delete_url(url)

	def common_video_extensions(self):
		getSupportedMedia = '.m4v|.3g2|.3gp|.nsv|.tp|.ts|.ty|.strm|.pls|.rm|.rmvb|.mpd|.m3u|.m3u8|.ifo|.mov|.qt|.divx|.xvid|.bivx|.vob|.nrg|.img|.iso|.udf|.pva|.wmv|.asf|.asx|.ogm|.m2v|.avi|.bin|.dat|.mpg|.mpeg|.mp4|.mkv|.mk3d|.avc|.vp3|.svq3|.nuv|.viv|.dv|.fli|.flv|.001|.wpl|.xspf|.zip|.vdr|.dvr-ms|.xsp|.mts|.m2t|.m2ts|.evo|.ogv|.sdp|.avs|.rec|.url|.pxml|.vc1|.h264|.rcv|.rss|.mpls|.mpl|.webm|.bdmv|.bdm|.wtv|.trp|.f4v|.ssif|.pvr|.disc|'
		getSupportedMedia = '.m4v|.3g2|.3gp|.nsv|.tp|.ts|.ty|.strm|.pls|.rm|.rmvb|.mpd|.m3u|.m3u8|.ifo|.mov|.qt|.divx|.xvid|.bivx|.vob|.pva|.wmv|.asf|.asx|.ogm|.m2v|.avi|.bin|.dat|.mpg|.mpeg|.mp4|.mkv|.mk3d|.avc|.vp3|.svq3|.nuv|.viv|.dv|.fli|.flv|.001|.wpl|.xspf|.zip|.vdr|.dvr-ms|.xsp|.mts|.m2t|.m2ts|.evo|.ogv|.sdp|.avs|.rec|.url|.pxml|.vc1|.h264|.rcv|.rss|.mpls|.mpl|.webm|.bdmv|.bdm|.wtv|.trp|.f4v|.ssif|.pvr|.disc|'
		return [
			i
			for i in getSupportedMedia.split("|")
			if i not in ["", ".zip", ".rar"]
		]

	def is_file_ext_valid(self, file_name):
		"""
		Checks if the video file type is supported by Kodi
		:param file_name: name/path of file
		:return: True if video file is expected to be supported else False
		"""
		if "." + file_name.split(".")[-1] not in self.common_video_extensions():
			return False
		return True

	def is_streamable_storage_type(self, storage_variant):
		"""
		Confirms that all files within the storage variant are video files
		This ensure the pack from RD is instantly streamable and does not require a download
		:param storage_variant:
		:return: BOOL
		"""
		return (
			False
			if len(
				[
					i
					for i in storage_variant.values()
					if not self.is_file_ext_valid(i["filename"])
				]
			)
			> 0
			else True
		)


	@staticmethod
	def is_service_enabled():
		return (
			tools.get_setting("realdebrid.enabled",'bool')
			and tools.get_setting(RD_AUTH_KEY) is not None
		)

	def get_account_status(self):
		status = None
		status_response = self.get_url("user")
		if isinstance(status_response, dict):
			status = status_response.get("type")
		return status if status else "unknown"
