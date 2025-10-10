from resources.lib import Utils
import json
import time
import requests
import xbmc
import xbmcaddon
import xbmcgui


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

def poll_for_token(device_code, interval, progress_dialog,timout=60,message=None):
	start_time = time.time()
	while time.time() - start_time < timout:
		if progress_dialog.iscanceled():
			break
		payload = {
			'code': device_code,
			'client_id': CLIENT_ID,
			'client_secret': CLIENT_SECRET
		}
		response = requests.post(OAUTH_DEVICE_TOKEN_URL, json=payload)

		if response.status_code == 200:
			return response.json()
		elif response.status_code == 400:
			elapsed = time.time() - start_time
			percent = int((elapsed / timout) * 100)
			progress_dialog.update(percent, message)
			time.sleep(interval)
		else:
			break
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
	#Utils.tools_log(response)
	#Utils.tools_log(response.text)
	#Utils.tools_log(response.status_code)
	Utils.tools_log('TRAKT_refresh_token')
	if response.status_code == 200:
		token_data = response.json()
		store_tokens(token_data)
		return token_data['access_token']
	else:
		xbmcgui.Dialog().notification("Trakt Auth", "Token refresh failed - REAUTH!!", xbmcgui.NOTIFICATION_ERROR)
		return None

def login_trakt():
	device_data = get_device_code()
	if not device_data:
		return

	user_code = device_data['user_code']
	verification_url = device_data['verification_url']
	interval = device_data['interval']
	expires_in = device_data['expires_in']
	device_code = device_data['device_code']

	progress = xbmcgui.DialogProgress()
	message = f"Enter code: [B]{user_code}[/B]"
	Utils.tools_log(f"Trakt Authorization Go to: {verification_url}", message)
	Utils.tools_log(user_code)
	
	progress.create(f"Trakt: {verification_url}", message)
	Utils.tools_log('poll_for_token')

	token_data = poll_for_token(device_code, interval, progress,timout=60, message=message)
	progress.close()

	if token_data:
		store_tokens(token_data)
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
		#Utils.tools_log(headers)
	return headers

def get_access_token():
	access_token = ADDON.getSettingString('access_token')
	if access_token == '':
		access_token = False
	expires_at = ADDON.getSettingString('token_expires')
	if expires_at == '':
		expires_at = time.time()-1
	else:
		expires_at = int(expires_at)
	if not access_token or time.time() > expires_at:
		Utils.tools_log('get_trakt_auth__TOKEN_REFRESHED!!')
		return refresh_token()
	return access_token