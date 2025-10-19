from resources.lib import Utils
import json
import time
import requests
import xbmc, xbmcvfs
import xbmcaddon
import xbmcgui
import os
import hashlib
import qrcode

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
CLIENT_ID = '0128c95089a7b58477204806a1b62ee130182b48c121c1eb9fe1d37b915fc5cb'
CLIENT_SECRET = '8f2ae1d28337020f0bcd1e60cc036762ecd39f5e49ec35a85a3f5c7d54811ec1'
OAUTH_DEVICE_CODE_URL = 'https://api.trakt.tv/oauth/device/code'
OAUTH_DEVICE_TOKEN_URL = 'https://api.trakt.tv/oauth/device/token'
OAUTH_TOKEN_URL = 'https://api.trakt.tv/oauth/token'
OAUTH_REVOKE_URL = 'https://api.trakt.tv/oauth/revoke'

HEADERS = {
	'Content-Type': 'application/json',
	'trakt-api-version': '2',
	'trakt-api-key': CLIENT_ID
}

import threading

class QRProgressDialog(xbmcgui.WindowXMLDialog):
	def __init__(self, *args, **kwargs):
		super().__init__(*args)
		self.heading = kwargs.get('heading', '')
		self.image = kwargs.get('image', '')
		self.message = kwargs.get('message', '')
		self.device_code = kwargs.get('device_code', '')
		self.interval = kwargs.get('interval', 5)
		self.timeout = kwargs.get('timeout', 120)
		self.percent = 0
		self.is_canceled = False
		self.token_data = None

	def close(self):
		try:
			del self.player
		except:
			pass
		xbmcgui.WindowXMLDialog.close(self)

	def run(self):
		try:
			self.doModal()
		except Exception as e:
			Utils.tools_log(f'doModal error: {e}')
		self.clearProperties()

	def onInit(self):
		try:
			self.getControl(2000).setLabel(self.heading)
			self.getControl(200).setImage(self.image, useCache=False)
			xbmc.executebuiltin('Container.Refresh')
			self.getControl(2001).setText(self.message)
			self.getControl(5000).setPercent(self.percent)
		except Exception as e:
			Utils.tools_log(f'onInit error: {e}')
		# Start polling in background
		threading.Thread(target=self.poll_for_token, daemon=True).start()

	def update(self, message='', percent=0):
		try:
			self.percent = percent
			self.getControl(2001).setText(message)
			self.getControl(5000).setPercent(percent)
		except Exception as e:
			Utils.tools_log(f'update error: {e}')

	def iscanceled(self):
		return self.is_canceled

	def onAction(self, action):
		if action.getId() in (9, 10, 13, 92):  # ESC, Backspace, Stop, Back
			self.is_canceled = True
			self.close()

	def poll_for_token(self):
		start_time = time.time()
		while time.time() - start_time < self.timeout:
			if self.iscanceled():
				break
			payload = {
				'code': self.device_code,
				'client_id': CLIENT_ID,
				'client_secret': CLIENT_SECRET
			}
			response = requests.post(OAUTH_DEVICE_TOKEN_URL, json=payload)
			if response.status_code == 200:
				self.token_data = response.json()
				# Store token data in a property to retrieve later
				#Utils.tools_log(self.token_data)
				xbmcgui.Window(10000).setProperty('trakt.token_data', json.dumps(self.token_data))
				break
			elif response.status_code == 400:
				elapsed = time.time() - start_time
				percent = int((elapsed / self.timeout) * 100)
				self.update(self.message, percent)
				time.sleep(self.interval)
			else:
				break
		self.close()

def remove_old_qr(media_path=Utils.ADDON_DATA_PATH):
	import glob
	pattern = os.path.join(media_path, "trakt_qrcode*.png")
	# Delete matching files
	for file_path in glob.glob(pattern):
		try:
			os.remove(file_path)
			Utils.tools_log(f"Deleted: {file_path}")
		except Exception as e:
			xUtils.tools_log(f"Failed to delete {file_path}: {e}")




def create_qrcode(url, filename, folder=Utils.ADDON_DATA_PATH):
	filepath = os.path.join(folder, str(filename) + '_'+str(int(time.time()))+'.png')
	qr_image = qrcode.make(url)
	qr_image.save(filepath, 'PNG')
	return filepath

def get_device_code():
	payload = {
		'client_id': CLIENT_ID
	}
	response = requests.post(OAUTH_DEVICE_CODE_URL, json=payload, headers=HEADERS)
	if response.status_code == 200:
		return response.json()
	else:
		xbmcgui.Dialog().notification("Trakt Auth", "Failed to get device code", xbmcgui.NOTIFICATION_ERROR)
		return None

def store_tokens(token_data):
	ADDON.setSettingString('access_token', token_data['access_token'])
	ADDON.setSettingString('refresh_token', token_data['refresh_token'])
	ADDON.setSettingString('token_expires', str(int(token_data['created_at']) + token_data['expires_in']))
	token_json = json.dumps(token_data)
	ADDON.setSettingString('trakt_token', token_json)

def refresh_token():
	refresh_token = ADDON.getSettingString('refresh_token')
	if not refresh_token:
		return None
	payload = {
		'refresh_token': refresh_token,
		'client_id': CLIENT_ID,
		'client_secret': CLIENT_SECRET,
		'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
		'grant_type': 'refresh_token'
	}
	response = requests.post(OAUTH_TOKEN_URL, json=payload)
	Utils.tools_log('TRAKT_refresh_token')
	if response.status_code == 200:
		token_data = response.json()
		store_tokens(token_data)
		return token_data['access_token']
	else:
		xbmcgui.Dialog().notification("Trakt Auth", "Token refresh failed - REAUTH!!", xbmcgui.NOTIFICATION_ERROR)
		return None


def login_trakt():
	xbmcgui.Window(10000).clearProperty('trakt.token_data')
	device_data = get_device_code()
	if not device_data:
		return

	user_code = device_data['user_code']
	verification_url = device_data['verification_url']
	interval = device_data['interval']
	expires_in = device_data['expires_in']
	device_code = device_data['device_code']
	remove_old_qr()
	qr_url = f"{verification_url}/{user_code}"
	qr_path = create_qrcode(qr_url, 'trakt_qrcode')

	message = f"Scan QR or go to:\n{verification_url}\nCode: {user_code}"
	xbmcgui.Window(10000).setProperty('trakt.qrcode.image', qr_path)

	progress_dialog = QRProgressDialog(
		'progress.xml',
		Utils.ADDON_PATH,
		heading='Trakt Authorization',
		image=qr_path,
		message=message,
		device_code=device_code,
		interval=interval,
		timeout = min(device_data['expires_in'], 120)
	)
	progress_dialog.run()
	progress_dialog.close()

	xbmcgui.Window(10000).clearProperty('trakt.qrcode.image')

	token_json = xbmcgui.Window(10000).getProperty('trakt.token_data')
	if len(token_json) > 1:
		token_data = json.loads(token_json)
		store_tokens(token_data)
		#Utils.tools_log(token_data)
		xbmcgui.Dialog().notification("Trakt Auth", "Authorization successful", xbmcgui.NOTIFICATION_INFO)
	else:
		xbmcgui.Dialog().notification("Trakt Auth", "Authorization failed or cancelled", xbmcgui.NOTIFICATION_ERROR)


def get_trakt_auth(startup=False):
	access_token = get_access_token()
	trakt_token = ADDON.getSettingString('trakt_token')
	headers = {'trakt-api-version': '2', 'trakt-api-key': CLIENT_ID, 'Content-Type': 'application/json'}
	headers['Authorization'] = 'Bearer {0}'.format(access_token)
	if startup:
		Utils.tools_log('STARTUP_get_trakt_auth')
	return headers

def get_access_token():
	access_token = ADDON.getSettingString('access_token')
	if access_token == '':
		access_token = False
	expires_at = ADDON.getSettingString('token_expires')
	if expires_at == '':
		expires_at = time.time() - 1
	else:
		expires_at = int(expires_at)
	if not access_token or time.time() > expires_at:
		Utils.tools_log('get_trakt_auth__TOKEN_REFRESHED!!')
		return refresh_token()
	return access_token