from resources.lib import Utils

import sys
import os
from inspect import currentframe, getframeinfo

# -----------------------------
# VERY FIRST: patch sys.path
# -----------------------------
# Add Subliminal folder (contains zipp)
subliminal_path = os.path.join(Utils.ADDON_PATH, "Subliminal")
if subliminal_path not in sys.path:
	sys.path.insert(0, subliminal_path)

# Add Subliminal root to sys.path
if subliminal_path not in sys.path:
	sys.path.insert(0, sublimiminal_path)

# Add all subfolders in Subliminal to sys.path
for entry in os.listdir(subliminal_path):
	full_path = os.path.join(subliminal_path, entry)
	if os.path.isdir(full_path) and full_path not in sys.path:
		sys.path.insert(0, full_path)


# Add importlib_resources and fake_useragent paths
sys.path.insert(0, os.path.join(Utils.ADDON_PATH, "importlib_resources_old"))
sys.path.insert(0, os.path.join(Utils.ADDON_PATH, "importlib_resources_new"))

# -----------------------------
# Now import everything else
# -----------------------------


version_str = sys.version.split()[0]   # e.g. '3.9.2'
version_float = float('.'.join(version_str.split('.')[:2]))

if version_float >= 3.9:
	import importlib_resources_new as importlib_resources
	sys.modules["importlib_resources"] = importlib_resources
else:
	import importlib_resources_old as importlib_resources
	sys.modules["importlib_resources"] = importlib_resources

import importlib
importlib.invalidate_caches()

import json
import urllib.parse
import requests


import flask
from flask import Flask, Response, request, jsonify
from requests.exceptions import SSLError
from werkzeug.serving import make_server
import threading
from time import sleep


from time import sleep
#from flask_cors import CORS
import threading

thread_event = threading.Event()


#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)

app = Flask(__name__)





#Utils.tools_log(Utils.xtreme_codes_server_path)
#Utils.tools_log(Utils.xtreme_codes_username)
#Utils.tools_log(Utils.xtreme_codes_password)

from flask import Flask, jsonify, request
import json, os


def start():
	Utils.tools_log('STARTING__SERVER')
	server = make_server("0.0.0.0", 5000, app)
	server_thread = threading.Thread(target=server.serve_forever)
	server_thread.start()
	server_thread.join()

@app.route('/stop', methods=['GET'])
def stop():
	print("exit 1")
	Utils.tools_log('exit SERVER')
	##server.shutdown()
	quit()
	#Utils.tools_log('exit 2')
	#server_thread.join()
	#Utils.tools_log('exit 3')


@app.route('/log-viewer')
def log_viewer():
	import xbmcvfs
	import os
	log_path =  xbmcvfs.translatePath('special://logpath')
	if not 'kodi.log' in log_path:
		log_path = os.path.join(log_path, 'kodi.log')

	if not os.path.isfile(log_path):
		log_content = 'Kodi log file not found.'
	else:
		try:
			with open(log_path, 'r') as f:
				lines = f.readlines()[-500:]
			log_content = ''.join(lines)
		except Exception as e:
			log_content = f'Error reading log file: {str(e)}'

	html = f"""
	<!DOCTYPE html>
	<html lang="en">
	<head>
		<meta charset="UTF-8">
		<title>Kodi Log Viewer</title>
		<meta http-equiv="refresh" content="10">
		<style>
			body {{
				font-family: monospace;
				background-color: #1e1e1e;
				color: #dcdcdc;
				padding: 20px;
			}}
			pre {{
				background-color: #2e2e2e;
				padding: 15px;
				border-radius: 5px;
				overflow-x: auto;
				max-height: 90vh;
			}}
		</style>
	</head>
	<body>
		<h2>Kodi Log - Last 50 Lines (Auto-refresh every 10s)</h2>
		<pre>{log_content}</pre>
	</body>
	</html>
	"""
	return Response(html, mimetype='text/html')



def get_vod_data(action= None,series_ID = None, cache_days=1, folder='VOD'):
	#url = 'https://api.themoviedb.org/3/%sapi_key=%s' % (url, API_key)
	xtreme_codes_password = Utils.xtreme_codes_password
	xtreme_codes_username = Utils.xtreme_codes_username
	xtreme_codes_server_path = Utils.xtreme_codes_server_path

	actions = ['get_series','get_series_categories','get_series_info','get_vod_categories','get_vod_streams','get_live_categories','get_live_streams',]
	url = '%s/player_api.php?username=%s&password=%s&action=%s' % (xtreme_codes_server_path,xtreme_codes_username,xtreme_codes_password,action)
	if series_ID:
		action = 'get_series_info'
		url = '%s/player_api.php?username=%s&password=%s&action=%s&series=%s' % (xtreme_codes_server_path,xtreme_codes_username,xtreme_codes_password,action,str(series_ID)) 
	#xbmc.log(str(url)+'===>PHIL', level=xbmc.LOGINFO)
	return Utils.get_JSON_response(url, cache_days, folder)


def curl_request(url, binary=False, cache_days=7.0):
	"""
	Make a request with custom headers
	binary: If True, return raw bytes instead of text (for images)
	"""
	try:
		headers = {
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Language': 'en-US,en;q=0.5',
			'Connection': 'keep-alive',
		}

		response = requests.get(url, headers=headers)
		response.raise_for_status()
		return response.content if binary else response.text

	except SSLError:
		return {'error': 'SSL Error', 'details': 'Failed to verify SSL certificate'}, 503
	except requests.RequestException as e:
		print(f"RequestException: {e}")
		return {'error': 'Request Exception', 'details': str(e)}, 503

def encode_image_url(url):
	"""Encode the image URL to be used in the proxy endpoint"""
	if not url:
		return ''
	return urllib.parse.quote(url, safe='')


from flask import Flask, jsonify, request
import json, os


def start():
	Utils.tools_log('STARTING__SERVER')
	server = make_server("0.0.0.0", 5000, app)
	server_thread = threading.Thread(target=server.serve_forever)
	server_thread.start()
	server_thread.join()


#@app.route('/xmltv', methods=['GET'])
def generate_xmltv(mode=None):
	Utils.tools_log('def generate_xmltv():')
	# Get parameters from the URL
	url = Utils.xtreme_codes_server_path
	username = Utils.xtreme_codes_username
	password = Utils.xtreme_codes_password

	guide_out = os.path.join(Utils.ADDON_DATA_PATH, 'guide.xml')
	age = Utils.get_file_age(guide_out)
	if age:
		if float(age['hours']) <= float(4.00):
			Utils.tools_log('XML_RETURN')
			if Utils.local_xml_m3u or (Utils.startup_local_xml_m3u and mode == 'startup'):
				return
			with open(guide_out, "r", encoding="utf-8") as f:
				xmltv_response = f.read()
			# Return the M3U playlist as a downloadable file
			return Response(xmltv_response,mimetype='application/xml',headers={"Content-Disposition": "attachment; filename=guide.xml"})

	allowed_groups_file = os.path.join(Utils.ADDON_DATA_PATH, 'allowed_groups.txt')
	allowed_groups = []
	if os.path.isfile(allowed_groups_file):
		allowed_groups_f = open(allowed_groups_file, "r")
		for x in allowed_groups_f:
			allowed_groups.append(x.strip())
	wanted_groups = allowed_groups

	channel_order_file = os.path.join(Utils.ADDON_DATA_PATH, 'channel_order.txt')
	channel_order_lists = []
	channel_order = False
	if os.path.isfile(channel_order_file):
		Utils.tools_log('EXISTS__'+channel_order_file)
		channel_order_f = open(channel_order_file, "r")
		for x in channel_order_f:
			channel_order_lists.append(x.strip())
		channel_order = True
	#priority_names = []

	no_stream_proxy = True
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Language': 'en-US,en;q=0.5',
		'Connection': 'keep-alive',
	}

	livechannel_response = get_vod_data(action='get_live_streams',cache_days=0.5)

	category_response = get_vod_data(action='get_live_categories',cache_days=0.5)

	categoryname = {}
	if category_response == None:
		xmltv_response = None
		return Response(
			xmltv_response,
			mimetype='application/xml',
			headers={"Content-Disposition": "attachment; filename=guide.xml"}
		)
	for i in category_response:
		categoryname[i['category_id']] = i['category_name']

	allowed_channels = []
	for channel in livechannel_response:
		if channel['stream_type'] == 'live':
			#Utils.tools_log(channel)
			category_id = channel["category_id"]
			channel_name = channel["epg_channel_id"]
			group_title = categoryname.get(channel["category_id"], "Uncategorized")
			#Utils.tools_log(category_id)
			#Utils.tools_log(channel_name)
			#Utils.tools_log(group_title)
			for i in wanted_groups:
				if str(i).lower() in group_title.lower():
					if not channel_name in allowed_channels:
						allowed_channels.append(channel_name)
						#Utils.tools_log(channel_name)

	xml_url = '%s/xmltv.php?username=%s&password=%s' % (url.rstrip('/'), username, password)
	response = requests.get(xml_url,headers=headers)
	xmltv_response = response.text

	Utils.tools_log(xml_url)
	print(xml_url, flush=True)

	xmltv_response = xmltv_response.replace('\n','')
	xmltv_response = xmltv_response.replace('/channel>','/channel>\n').replace('/programme>','/programme>\n').replace('<channel','\n<channel').replace('<programme','\n<programme')

	filtered_lines = []
	current_channel = None
	skip_current = False

	allowed_display_name = []
	allowed_channel_id = []

	try:
		for line in xmltv_response.split('\n'):
			skip_current = False
			if '<channel id="' in line:
				channel_id = line.split('channel id="')[1].split('"')[0]
				display_name = line.split('display-name>')[1].split('<')[0]
				exclude = True
				if channel_id in allowed_channels:
					exclude = False
				if display_name in allowed_channels:
					exclude = False
				if len(allowed_channels) == 0:
					exclude = False
				if exclude == False:
					allowed_display_name.append(display_name)
					allowed_channel_id.append(channel_id)

			if '<programme ' in line:
				channel_id = line.split('channel="')[1].split('" >')[0]
				exclude = True
				if channel_id in allowed_channel_id:
					exclude = False

			if '<channel id="' in line or '<programme ' in line:
				if exclude == True:
					skip_current = True

			if skip_current == False and len(line) > 0:
				filtered_lines.append(line)

		xmltv_response = '\n'.join(filtered_lines)
		xmltv_response = xmltv_response.replace('\n','')

	except (json.JSONDecodeError, IndexError, KeyError):
		# If filtering fails, return unfiltered XMLTV
		Utils.tools_log('EXCEPTION_If filtering fails, return unfiltered XMLTV')
		xmltv_response = xmltv_response.replace('\n','')
		pass

	Utils.tools_log('XML_RETURN')
	print('XML_RETURN', flush=True)

	if Utils.local_xml_m3u or (Utils.startup_local_xml_m3u and mode == 'startup'):
		
		Utils.tools_log(guide_out)
		f = open(guide_out, "w")
		f.write(xmltv_response)
		f.close()

	# Return the modified XMLTV data
	return Response(
		xmltv_response,
		mimetype='application/xml',
		headers={"Content-Disposition": "attachment; filename=guide.xml"}
	)

def backgroundTask():
	#while thread_event.is_set():
	#	print('Background task running!')
	#	sleep(5)
	generate_xmltv()
	thread_event.clear()

def startBackgroundTask():
	try:
		thread_event.set()
		
		thread = threading.Thread(target=backgroundTask)
		thread.start()

		return "Background task started!"
	except Exception as error:
		return str(error)

def paste_bin(paste_text):
	import urllib.request
	import urllib.parse

	pastebin_vars = {
		'api_dev_key': '57fe1369d02477a235057557cbeabaa1',
		'api_option': 'paste',
		'api_paste_code': paste_text
	}

	data = urllib.parse.urlencode(pastebin_vars).encode("utf-8")
	req = urllib.request.Request("https://pastebin.com/api/api_post.php", data=data)

	with urllib.request.urlopen(req) as response:
		url = response.read().decode("utf-8")
	print("Pastebin URL:", url)
	return url

def channel_names_groups():
	categoryname = {}
	category_response = get_vod_data(action='get_live_categories',cache_days=0.5)
	for i in category_response:
		categoryname[i['category_id']] = i['category_name']

	livechannel_response = get_vod_data(action='get_live_streams',cache_days=0.5)
	channel_names = []
	groups = []
	for i in livechannel_response:
		curr_channel = {'num': i['num'], 'name': i['name'],'category_id': i['category_id'], 'epg_group': categoryname[i['category_id']]}
		channel_names.append(curr_channel)
		if not categoryname[i['category_id']] in groups:
			groups.append(categoryname[i['category_id']])
	return channel_names, groups

def output_lists_pastebin():
	channel_names, groups = channel_names_groups()
	chanels_list = ''
	epg_groups_list = ''
	for i in channel_names:
		chanels_list = chanels_list + i['name'] +'\n'
	for i in groups:
		epg_groups_list = epg_groups_list + i +'\n'
	pastebin_output = 'CHANNEL_LIST' + '\n\n\n' + chanels_list + '\n\n\n#########\n\n\n' + 'EPG_GROUPS_LIST' + '\n\n\n' + epg_groups_list + '\n\n\n#########'
	url = paste_bin(pastebin_output)
	Utils.tools_log('PASTEBIN FULL CHANNEL AND EPG GROUPS LIST')
	Utils.tools_log(url)
	Utils.tools_log('PASTEBIN FULL CHANNEL AND EPG GROUPS LIST')
	return url


def save_pastebin_to_file(url, file_name):
	import requests
	if not 'raw' in url:
		url = url.replace('https://pastebin.com/','https://pastebin.com/raw/')
	print(url)
	file = requests.get(url).text
	file_out = os.path.join(Utils.ADDON_DATA_PATH, file_name)
	f = open(file_out, "w")
	f.write(file)
	f.close()
	Utils.notify('SAVED', file_out)
	return True

def save_channel_order(paste_bin_url):
	save_pastebin_to_file(url=paste_bin_url, file_name='channel_order.txt')

def save_allowed_groups(paste_bin_url):
	save_pastebin_to_file(url=paste_bin_url, file_name='allowed_groups.txt')



#@app.route('/m3u', methods=['GET'])
def generate_m3u(mode=None):
	if thread_event.is_set() == False and mode == None:
		Utils.tools_log('startBackgroundTask')
		Utils.tools_log('generate_m3u(mode=startup)')
		generate_m3u(mode='startup')
		Utils.tools_log('startBackgroundTask')
		return startBackgroundTask()
	# Get parameters from the URL
	url = Utils.xtreme_codes_server_path
	username = Utils.xtreme_codes_username
	password = Utils.xtreme_codes_password

	m3u_out = os.path.join(Utils.ADDON_DATA_PATH, 'LiveStream.m3u')
	age = Utils.get_file_age(m3u_out)
	if age:
		if float(age['hours']) <= float(4.00):
			Utils.tools_log('M3U_RETURN')
			if Utils.local_xml_m3u or (Utils.startup_local_xml_m3u and mode == 'startup'):
				return
			with open(m3u_out, "r", encoding="utf-8") as f:
				m3u_playlist = f.read()
			# Return the M3U playlist as a downloadable file
			return Response(m3u_playlist, mimetype='audio/x-scpls', headers={"Content-Disposition": "attachment; filename=LiveStream.m3u"})



	allowed_groups_file = os.path.join(Utils.ADDON_DATA_PATH, 'allowed_groups.txt')
	allowed_groups = []
	if os.path.isfile(allowed_groups_file):
		allowed_groups_f = open(allowed_groups_file, "r")
		for x in allowed_groups_f:
			allowed_groups.append(x.strip())
	#wanted_groups = []

	channel_order_file = os.path.join(Utils.ADDON_DATA_PATH, 'channel_order.txt')
	channel_order_lists = []
	channel_order = False
	if os.path.isfile(channel_order_file):
		Utils.tools_log('EXISTS__'+channel_order_file)
		channel_order_f = open(channel_order_file, "r")
		for x in channel_order_f:
			channel_order_lists.append(x.strip())
		channel_order = True
	#priority_names = []
	no_stream_proxy = True

	# Fetch live streams
	livechannel_response = get_vod_data(action='get_live_streams',cache_days=0.5)

	category_response = get_vod_data(action='get_live_categories',cache_days=0.5)
	categoryname = {}
	if category_response == None:
		m3u_playlist = None
		return Response(m3u_playlist, mimetype='audio/x-scpls', headers={"Content-Disposition": "attachment; filename=LiveStream.m3u"})
	for i in category_response:
		categoryname[i['category_id']] = i['category_name']

	# Get the current host URL for the proxy
	#host_url = request.host_url.rstrip('/')

	"""
	priority_names = ['UK: BBC One HD', 'UK: BBC One', 'UK: BBC One Scotland HD', 'UK: BBC One Scotland', 'IE: BBC One Northern Ireland HD', 'UK: BBC Two HD', 'UK: BBC Two', 'IE: BBC Two Northern Ireland HD', 'UK: ITV1 HD', 'UK: ITV1', 'UK: ITV1 +1', 'UK: ITV2 HD', 'UK: ITV2', 'UK: ITV2 +1', 'IE: UTV', 'IE: UTV HD', 'UK: STV HD', 'UK: UTV', 'UK: UTV HD', 'UK: Channel 4 HD', 'UK: Channel 4', 'UK: Channel 4 +1', 'UK: Channel 5 HD', 'UK: Channel5','UK: Channel 5 +1', 'UK: BBC Three', 'UK: BBC Four HD', 'UK: BBC Scotland HD', 'UK: BBC Scotland', 'UK: BBC News HD', 'UK: BBC News', 'UK: BBC Parliament', 'UK: BBC Alba', 'UK: BBC Red Button 01', 'IE:  PremierSports 1', 'IE:  Premier Sports 1 HD', 'IE:  Premier Sports 2', 'IE:  Premier Sports 2 HD', 'UK: ITV3 HD', 'UK: ITV3', 'UK: ITV3 +1', 'UK: ITV4 HD', 'UK: ITV4', 'UK: ITV4 +1', 'UK: ITV Be', 'UK: ITV Be HD', 'UK: More 4 HD', 'UK: More 4', 'UK: More 4 +1', 'UK: E4 HD', 'UK: E4', 'UK: E4 +1', 'UK: E4 Extra', 'UK: 4seven', 'UK: Film4 HD', 'UK: Film4', 'UK: Film4 +1', 'UK: 5 Action', 'UK: 5Select', 'UK: 5Star', 'UK: 5star +1', 'UK: 5USA', 'UK: 5USA +1', 'UK: Gold HD', 'UK: Gold', 'UK: Gold +1', 'IE: Cula 4', 'IE: Cula 4 HD', 'IE: RTE Junior HD', 'IE: RTE News', 'IE: RTE One', 'IE: RTE One +1', 'IE: RTE One HD', 'IE: RTETwo', 'IE: RTE Two +1', 'IE: RTE Two HD', 'IE: TG4', 'IE: TG4 HD', 'IE: Virgin Media 1 HD', 'IE: Virgin Media 2 HD', 'IE: Virgin Media 3 HD', 'IE: Virgin Media 4', 'UK: Comedy Central HD', 'UK: Comedy Central', 'UK: ComedyCentral +1', 'UK: Comedy Central Extra', 'UK: Syfy HD', 'UK: Syfy', 'UK: Dave HD', 'UK: Dave', 'UK: Dave JA VU', 'UK: Alibi HD', 'UK: Alibi', 'UK: Alibi +1', 'UK: Sky Arts HD', 'UK: Sky Atlantic HD', 'UK: Sky CinemaAction HD', 'UK: Sky Cinema Animation HD', 'UK: Sky Cinema Comedy HD', 'UK: Sky Cinema Drama HD', 'UK: Sky Cinema Family HD', 'UK: Sky Cinema Greats HD', 'UK: Sky Cinema Premiere HD', 'UK: Sky Cinema Sci-Fi Horror HD', 'UK: Sky Cinema Select HD', 'UK: Sky Cinema Thriller HD', 'UK: Sky Cinema Hits HD', 'UK: Sky Comedy HD', 'UK: Sky Crime HD', 'UK: Sky Witness HD', 'UK: Sky Showcase HD', 'UK: Sky Documentaries HD', 'UK: Sky History HD', 'UK:Sky Kids HD', 'UK: Sky Nature HD', 'UK: Sky Max HD', 'UK: Sony TV HD', 'UK: Sony Max HD', 'UK: Bloomberg', 'UK: Bloomberg HD', 'UK: Boomerang', 'UK: Boomerang HD', 'UK: CNBC', 'UK: CNBC HD', 'UK: CNN', 'UK: CNN HD', 'UK:Aljazeera News', 'UK: Sky News HD', 'UK: CBS Drama', 'UK: CBS Justice', 'UK: CBS Reality', 'UK: CBS Reality +1', 'UK: Animal Planet HD', 'UK: Animal Planet', 'UK: Animal Planet +1', 'UK: Cartoon Network', 'UK: CartoonNetwork HD', 'UK: Cartoonito', 'UK: CBBC', 'UK: CBBC HD', 'UK: CBeebies', 'UK: CBeebies HD', 'UK: Channel S', 'UK: Clubland TV', 'UK: Colors', 'UK: Colors Cineplex', 'UK: Colors HD', 'UK: Crime & Investigation HD', 'UK:Crime & Investigation', 'UK: Crime & Investigation +1', 'UK: Discovery HD', 'UK: Discovery', 'UK: Discovery +1', 'UK: Discovery History', 'UK: Discovery History +1', 'UK: Sky Arts', 'UK: Sky Atlantic', 'UK: Sky Atlantic +1', 'UK: Sky Cinema Action', 'UK: Sky Cinema Animation', 'UK: Sky Cinema Comedy', 'UK: Sky Cinema Drama', 'UK: Sky Cinema Family', 'UK: Sky Cinema Greats', 'UK: Sky Cinema Hits', 'UK: Sky Cinema Premiere', 'UK: Sky Cinema Sci-Fi Horror', 'UK: Sky Cinema Select', 'UK: Sky Cinema Thriller', 'UK: Sky Comedy', 'UK: Sky Crime', 'UK: Sky Crime +1', 'UK: Sky Documentaries', 'UK: Sky History', 'UK: Sky Kids', 'UK: Sky Max', 'UK: Sky Mix', 'UK: Sky Nature', 'UK: Sky News', 'UK: Sky Replay', 'UK: Sky Showcase', 'UK: Sky Showcase +1', 'UK: Sky Witness', 'UK: Sky Witness +1', 'UK: Sony Action', 'UK: Sony Channel', 'UK: Sony Max', 'UK: Sony Max 2', 'UK: Sony Movies', 'UK: Sony Movies Christmas', 'UK: Sony SAB', 'UK: Sony TV', 'UK: Talking Pictures', 'UK: That\'s TV', 'UK: That\'s TV 2', 'UK: True Crime', 'UK: True Crime +1', 'UK: Yesterday', 'UK: Yesterday +1', 'UK: Yesterday HD', 'UK: Great Action', 'UK: Great Action +1', 'UK: Great Classic', 'UK: Great Classic +1', 'UK: Great Movies', 'UK: Great Movies +1', 'UK: Great TV', 'UK: Great TV +1', 'UK: MTV', 'UK: MTV Base', 'UK: MTV HD', 'UK: MTV Hits', 'UK: MTV Music', 'UK: Nat Geo HD', 'UK: Nat Geo', 'UK: Nat Geo +1', 'UK: Nat Geo Wild HD', 'UK: Nat Geo Wild']
	"""
	priority_names = channel_order_lists
	if channel_order:
		def custom_sort_key(entry):
			name = entry["name"]
			if name in priority_names:
				return (0, priority_names.index(name))  # Keep priority order
			return (1, name)  # Sort the rest alphabetically
		sorted_livechannel_response = sorted(livechannel_response, key=custom_sort_key)
	else:
		sorted_livechannel_response = livechannel_response

	server_url = url.rstrip('/')
	fullurl = f"{server_url}/live/{username}/{password}/"

	# Generate M3U playlist
	unwanted_groups = []
	wanted_groups = allowed_groups
	m3u_playlist = "#EXTM3U\n"
	for channel in sorted_livechannel_response:
		if channel['stream_type'] == 'live':
			group_title = categoryname.get(channel["category_id"], "Uncategorized")
			if not str(group_title) in unwanted_groups:
				wanted_flag = False
				for i in wanted_groups:
					if str(i).lower() in str(group_title).lower():
						wanted_flag = True
				if not wanted_flag:
					unwanted_groups.append(group_title)
				#else:
				#	print(group_title, flush=True)
				#	Utils.tools_log(group_title)
			
			if not any(unwanted_group.lower() in group_title.lower() for unwanted_group in unwanted_groups):
				# Proxy the logo URL
				original_logo = channel.get('stream_icon', '')
				#logo_url = f"{host_url}/image-proxy/{encode_image_url(original_logo)}" if original_logo else ''
				logo_url = original_logo

				stream_url = f'{fullurl}{channel["stream_id"]}.ts'
				#if not no_stream_proxy:
				#	stream_url = f"{host_url}/stream-proxy/{encode_image_url(stream_url)}"

				m3u_playlist += f'#EXTINF:0 tvg-name="{channel["name"]}" group-title="{group_title}" tvg-logo="{logo_url}",{channel["name"]}\n'
				m3u_playlist += f'{stream_url}\n'

	Utils.tools_log('M3U_RETURN')
	if Utils.local_xml_m3u or (Utils.startup_local_xml_m3u and mode == 'startup'):
		
		Utils.tools_log(m3u_out)
		f = open(m3u_out, "w")
		f.write(m3u_playlist)
		f.close()
		return

	# Return the M3U playlist as a downloadable file
	return Response(m3u_playlist, mimetype='audio/x-scpls', headers={"Content-Disposition": "attachment; filename=LiveStream.m3u"})

@app.route('/xml', methods=['GET'])
def serve_xml():
	Utils.tools_log('XML_SERVE')
	print('XML_SERVE', flush=True)

	guide_out = os.path.join(Utils.ADDON_DATA_PATH, 'guide.xml')

	if os.path.isfile(guide_out):
		Utils.tools_log('EXISTS__'+guide_out)
	else:
		Utils.tools_log('NOT_EXISTS__'+guide_out)
		Utils.tools_log('CREATING__'+guide_out)
		generate_xmltv()
	f = open(guide_out, "r")
	xmltv_response = f.read()
	f.close()
	return Response(
			xmltv_response,
			mimetype='application/xml',
			headers={"Content-Disposition": "attachment; filename=guide.xml"}
		)

@app.route('/m3u', methods=['GET'])
def serve_m3u():
	Utils.tools_log('M3U_SERVE')
	print('M3U_SERVE', flush=True)

	m3u_out = os.path.join(Utils.ADDON_DATA_PATH, 'LiveStream.m3u')

	if os.path.isfile(m3u_out):
		Utils.tools_log('EXISTS__'+m3u_out)
	else:
		Utils.tools_log('NOT_EXISTS__'+m3u_out)
		Utils.tools_log('CREATING__'+m3u_out)
		generate_m3u()
	f = open(m3u_out, "r")
	m3u_playlist = f.read()
	f.close()

	return Response(m3u_playlist, mimetype='audio/x-scpls', headers={"Content-Disposition": "attachment; filename=LiveStream.m3u"})

#save_channel_order('https://pastebin.com/ky4LX0M2')
#save_allowed_groups('https://pastebin.com/CRYd6dFM')




def update_iptv_simple_settings():
	import os
	import shutil
	source_file	= os.path.join(Utils.ADDON_PATH,'instance-settings-_xml')
	iptv_data_dir = str(Utils.ADDON_DATA_PATH).replace('script.xtreme_vod','pvr.iptvsimple') 
	if not os.path.exists(iptv_data_dir):
		Utils.tools_log("IPTV Simple addon data folder not found")
		return
	
	# Step 1: Rename any instance-settings-*.xml files
	number = 1
	for fname in os.listdir(iptv_data_dir):
		if fname.startswith("instance-settings-") and fname.endswith(".xml"):
			src = os.path.join(iptv_data_dir, fname)
			dst = os.path.join(iptv_data_dir, "disabled-" + fname)
			number_curr = int(fname.replace('instance-settings-','').replace('.xml',''))
			if number_curr > number:
				number = number_curr
			Utils.tools_log(f"Renaming {src} -> {dst}")
			os.rename(src, dst)

	# Step 2: Copy in the local replacement file
	if os.path.exists(source_file):
		target_file = os.path.join(iptv_data_dir, 'instance-settings-' + str(number+1) + '.xml')
		Utils.tools_log(f"Copying {source_file} -> {target_file}")
		shutil.copyfile(source_file, target_file)
	else:
		Utils.tools_log(f"Source file missing: {source_file}")

def setup_iptv_simple_settings():
	import xbmc
	import xbmcvfs
	Utils.tools_log('disable_IPTV_SIMPLE')
	xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", "params": {"addonid": "pvr.iptvsimple", "enabled": false}, "id": 1}')
	Utils.tools_log('update_iptv_simple_settings')
	update_iptv_simple_settings()
	Utils.tools_log('PVR.Cleardata')
	xbmc.executebuiltin("PVR.Cleardata")
	Utils.tools_log('Sleep_5')
	xbmc.sleep(5* 1000)
	Utils.tools_log('enable_IPTV_SIMPLE')
	xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", "params": {"addonid": "pvr.iptvsimple", "enabled": true}, "id": 1}')


def xml_startup_process():
	import xbmcaddon, xbmc
	from resources.lib.library import addon_ID


	m3u_out = os.path.join(Utils.ADDON_DATA_PATH, 'LiveStream.m3u')
	m3u_out_age = Utils.get_file_age(m3u_out)
	guide_out = os.path.join(Utils.ADDON_DATA_PATH, 'guide.xml')
	guide_out_age = Utils.get_file_age(guide_out)
	if m3u_out_age < 4 and guide_out_age < 4:
		Utils.tools_log('xml_startup_process_RETURN_no_changes')
		return


	if  xbmcaddon.Addon(addon_ID()).getSetting('auto_start_server') == 'true':
		auto_start_server = True
	else:
		auto_start_server = False

	if xbmcaddon.Addon(addon_ID()).getSetting('local_xml_m3u') == 'true':
		local_xml_m3u = True
	else:
		local_xml_m3u = False
	startup_local_xml_m3u = xbmcaddon.Addon(addon_ID()).getSetting('startup_local_xml_m3u')

	pvr_clients = Utils.get_pvr_clients()
	try:
		for i in pvr_clients:
			Utils.tools_log('Disable_IPTV_Clients')
			Utils.addon_disable_reable(addonid = i , enabled=False)
	except:
		pvr_clients = ['pvr.iptvsimple']
	Utils.ResetEPG()

	if auto_start_server and Utils.xtreme_codes_password != '':
		tools_log('STARTING SERVER -  http://localhost:5000/m3u  http://localhost:5000/xml  http://localhost:5000/stop')
		xbmc.executebuiltin('RunScript(script.xtreme_vod,info=xtream2m3u_run)')
	if (startup_local_xml_m3u == True or startup_local_xml_m3u == 'true') and Utils.xtreme_codes_password != '':
		generate_m3u(mode='startup')
		generate_xmltv(mode='startup')

	xbmc.sleep(5*1000)
	for i in pvr_clients:
		Utils.tools_log('Reable_IPTV_Clients')
		Utils.addon_disable_reable(addonid = i , enabled=True)

