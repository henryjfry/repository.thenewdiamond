#!/usr/bin/python3
import requests
import json
import sys
import base64

import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

f = open(__location__ + '/addon.xml', 'r')
Lines = f.readlines()
for i in Lines:
	if 'id="' in str(i):
		addon_name = i.split('id="')[1].split('"')[0]
	elif 'id ="' in str(i):
		addon_name = i.split('id ="')[1].split('"')[0]

kodi_credentials = b'kodi:kodi' 
kodi_encoded_credentials = base64.b64encode(kodi_credentials) 
kodi_authorization = b'Basic ' + kodi_encoded_credentials 
kodi_header = { 'Content-Type': 'application/json', 'Authorization': kodi_authorization } 
kodi_ip = '127.0.0.1'
kodi_port = '8080'
kodi_url = 'http://' + kodi_ip + ':' + kodi_port + '/jsonrpc'

'''
/usr/share/kodi/system/settings/settings.xml
disc.playback
              <option label="14104">0</option> <!-- show simplified menu -->
              <option label="25003">1</option> <!-- show disc menu -->
              <option label="14103">2</option> <!-- play main movie -->
'''

kodi_params = ('{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"disc.playback"}, "id": 1}')
kodi_response = requests.post(kodi_url, headers=kodi_header, data=kodi_params)
json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
json_object  = json.loads(json_data)
print(json_object['result'])
if json_object['result']['value'] == 2:
	disc_value = 0
	disc_message = 'Toggle=show simplified menu '
if json_object['result']['value'] == 0:
	disc_value = 2
	disc_message = 'Toggle=play main movie '


kodi_params = ('{"jsonrpc":"2.0","method":"Settings.SetSettingValue","params":{"setting":"disc.playback","value":%s}, "id": 1}' % (disc_value))
kodi_response = requests.post(kodi_url, headers=kodi_header, data=kodi_params)
json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
json_object  = json.loads(json_data)
print(json_object['result'])

kodi_params = ('{"jsonrpc":"2.0","method":"GUI.ShowNotification","params":{"title":"disc.playback","message":"%s"}, "id": 1}' % (disc_message))
kodi_response = requests.post(kodi_url, headers=kodi_header, data=kodi_params)
json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
json_object  = json.loads(json_data)
print(json_object['result'])

'''
kodi_params = ('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":8,"params":{"addonid":"%s","enabled":true}}' % (addon_name))
kodi_response = requests.post(kodi_url, headers=kodi_header, data=kodi_params)
json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
json_object  = json.loads(json_data)
print(json_object['result'])

'''