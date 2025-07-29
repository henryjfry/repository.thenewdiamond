import json
import os
import urllib.parse

from inspect import currentframe, getframeinfo

import sys
folder = str(os.path.split(str(getframeinfo(currentframe()).filename))[0])
current_directory = os.path.dirname(os.path.dirname(folder))
sys.path.append(current_directory)

from resources.lib import Utils
#Utils.tools_log(current_directory)

current_directory2 = os.path.join(current_directory,'Subliminal')
sys.path.append(current_directory2)
#Utils.tools_log(current_directory2)

import requests
from fake_useragent import UserAgent
from flask import Flask, Response, request
from requests.exceptions import SSLError



from time import sleep
from flask import Flask
#from flask_cors import CORS
import threading

from werkzeug.serving import make_server

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
	server = make_server("localhost", 5000, app)
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
		ua = UserAgent()
		headers = {
			'User-Agent': ua.chrome,
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

@app.route('/image-proxy/<path:image_url>')
def proxy_image(image_url):
	"""Proxy endpoint for images to avoid CORS issues"""
	try:
		# Decode the URL
		original_url = urllib.parse.unquote(image_url)
		#Utils.tools_log(f"Image proxy request for: {original_url}")

		# Make request with stream=True and timeout
		response = requests.get(original_url, stream=True, timeout=10)
		response.raise_for_status()

		# Get content type from response
		content_type = response.headers.get('Content-Type', '')
		#Utils.tools_log(f"Image response headers: {dict(response.headers)}")

		if not content_type.startswith('image/'):
			logger.error(f"Invalid content type for image: {content_type}")
			return Response('Invalid image type', status=415)

		def generate():
			try:
				bytes_sent = 0
				for chunk in response.iter_content(chunk_size=8192):
					if chunk:
						bytes_sent += len(chunk)
						yield chunk
				#Utils.tools_log(f"Image completed, sent {bytes_sent} bytes")
			except Exception as e:
				logger.error(f"Image streaming error in generator: {str(e)}")
				raise

		headers = {
			'Cache-Control': 'public, max-age=31536000',
			'Access-Control-Allow-Origin': '*',
		}

		# Only add Content-Length if we have it and it's not chunked transfer
		if ('Content-Length' in response.headers and
			'Transfer-Encoding' not in response.headers):
			headers['Content-Length'] = response.headers['Content-Length']
		else:
			headers['Transfer-Encoding'] = 'chunked'

		#Utils.tools_log(f"Sending image response with headers: {headers}")

		return Response(
			generate(),
			mimetype=content_type,
			headers=headers
		)
	except requests.Timeout:
		logger.error(f"Timeout fetching image: {original_url}")
		return Response('Image fetch timeout', status=504)
	except requests.HTTPError as e:
		logger.error(f"HTTP error fetching image: {str(e)}")
		return Response(f'Failed to fetch image: {str(e)}', status=e.response.status_code)
	except Exception as e:
		logger.error(f"Image proxy error: {str(e)}")
		return Response('Failed to process image', status=500)

@app.route('/stream-proxy/<path:stream_url>')
def proxy_stream(stream_url):
	"""Proxy endpoint for streams"""
	try:
		# Decode the URL
		original_url = urllib.parse.unquote(stream_url)
		#Utils.tools_log(f"Stream proxy request for: {original_url}")

		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
		}

		# Add timeout to prevent hanging
		response = requests.get(original_url, stream=True, headers=headers, timeout=10)
		response.raise_for_status()

		#Utils.tools_log(f"Stream response headers: {dict(response.headers)}")

		# Get content type from response
		content_type = response.headers.get('Content-Type')
		if not content_type:
			# Try to determine content type from URL
			if original_url.endswith('.ts'):
				content_type = 'video/MP2T'
			elif original_url.endswith('.m3u8'):
				content_type = 'application/vnd.apple.mpegurl'
			else:
				content_type = 'application/octet-stream'

		#Utils.tools_log(f"Using content type: {content_type}")

		def generate():
			try:
				bytes_sent = 0
				for chunk in response.iter_content(chunk_size=64*1024):
					if chunk:
						bytes_sent += len(chunk)
						yield chunk
				#Utils.tools_log(f"Stream completed, sent {bytes_sent} bytes")
			except Exception as e:
				logger.error(f"Streaming error in generator: {str(e)}")
				raise

		response_headers = {
			'Access-Control-Allow-Origin': '*',
			'Content-Type': content_type,
			'Accept-Ranges': 'bytes',
			'Cache-Control': 'no-cache',
			'Connection': 'keep-alive'
		}

		# Only add Content-Length if we have it and it's not chunked transfer
		if ('Content-Length' in response.headers and
			'Transfer-Encoding' not in response.headers):
			response_headers['Content-Length'] = response.headers['Content-Length']
		else:
			response_headers['Transfer-Encoding'] = 'chunked'

		#Utils.tools_log(f"Sending response with headers: {response_headers}")

		return Response(
			generate(),
			headers=response_headers,
			direct_passthrough=True
		)
	except requests.Timeout:
		logger.error(f"Timeout fetching stream: {original_url}")
		return Response('Stream timeout', status=504)
	except requests.HTTPError as e:
		logger.error(f"HTTP error fetching stream: {str(e)}")
		return Response(f'Failed to fetch stream: {str(e)}', status=e.response.status_code)
	except Exception as e:
		logger.error(f"Stream proxy error: {str(e)}")
		return Response('Failed to process stream', status=500)


#@app.route('/xmltv', methods=['GET'])
def generate_xmltv(mode=None):
	Utils.tools_log('def generate_xmltv():')
	# Get parameters from the URL
	url = Utils.xtreme_codes_server_path
	username = Utils.xtreme_codes_username
	password = Utils.xtreme_codes_password

	xtreme_wanted_groups = Utils.xtreme_wanted_groups
	wanted_groups = []
	for i in xtreme_wanted_groups.split(','):
		wanted_groups.append(i)

	no_stream_proxy = True
	ua = UserAgent()
	headers = {
		'User-Agent': ua.chrome,
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Language': 'en-US,en;q=0.5',
		'Connection': 'keep-alive',
	}

	#if not url or not username or not password:
	#	return json.dumps({
	#		'error': 'Missing Parameters',
	#		'details': 'Required parameters: url, username, and password'
	#	}), 400, {'Content-Type': 'application/json'}

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

	#base_url = url.rstrip('/')  # Remove trailing slash if present
	#base_url = url  # Remove trailing slash if present
	#xmltv_response = curl_request(f'{base_url}/xmltv.php?username={username}&password={password}')
	xml_url = '%s/xmltv.php?username=%s&password=%s' % (url.rstrip('/'), username, password)
	response = requests.get(xml_url,headers=headers)
	xmltv_response = response.text
	#Utils.tools_log(f'{base_url}/xmltv.php?username={username}&password={password}')
	#print(f'{base_url}/xmltv.php?username={username}&password={password}', flush=True)
	Utils.tools_log(xml_url)
	print(xml_url, flush=True)

	# Get the current host URL for the proxy
	#host_url = request.host_url.rstrip('/')

	#if isinstance(xmltv_response, tuple):  # Check if it's an error response
	#	return json.dumps(xmltv_response[0]), xmltv_response[1], {'Content-Type': 'application/json'}

	## Replace image URLs in the XMLTV content
	#if not isinstance(xmltv_response, tuple):
	#	import re

	#	def replace_icon_url(match):
	#		original_url = match.group(1)
	#		proxied_url = f"{host_url}/image-proxy/{encode_image_url(original_url)}"
	#		return f'<icon src="{proxied_url}"'

	#	# Replace icon URLs in the XML
	#	xmltv_response = re.sub(
	#		r'<icon src="([^"]+)"',
	#		replace_icon_url,
	#		xmltv_response
	#	)
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
		if Utils.output_folder != None and Utils.output_folder != '':
			guide_out = os.path.join(Utils.output_folder, 'guide.xml')
		else:
			guide_out = os.path.join(Utils.ADDON_DATA_PATH, 'guide.xml')
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
	xtreme_wanted_groups = Utils.xtreme_wanted_groups
	wanted_groups = []
	for i in xtreme_wanted_groups.split(','):
		wanted_groups.append(i)
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
	priority_names = []
	if Utils.channel_order:
		if not os.path.isfile(Utils.channel_order):
			Utils.tools_log('NOT_EXISTS__'+Utils.channel_order)
			Utils.tools_log('CREATING_REMOTE__'+Utils.channel_order)
			get_remote_channel_list()
		if os.path.isfile(Utils.channel_order):
			Utils.tools_log('EXISTS__'+Utils.channel_order)
			channel_order_f = open(Utils.channel_order, "r")
			for x in channel_order_f:
				priority_names.append(x.strip())

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
		if Utils.output_folder != None and Utils.output_folder != '':
			m3u_out = os.path.join(Utils.output_folder, 'LiveStream.m3u')
		else:
			m3u_out = os.path.join(Utils.ADDON_DATA_PATH, 'LiveStream.m3u')
		Utils.tools_log(m3u_out)
		f = open(m3u_out, "w")
		f.write(m3u_playlist)
		f.close()

	# Return the M3U playlist as a downloadable file
	return Response(m3u_playlist, mimetype='audio/x-scpls', headers={"Content-Disposition": "attachment; filename=LiveStream.m3u"})

def get_remote_channel_list():
	if os.path.isfile(Utils.channel_order):
		Utils.tools_log('EXISTS__'+Utils.channel_order)
		return
	if Utils.channel_order_remote:
		if Utils.channel_order:
			url = Utils.channel_order_remote
			response = requests.get(url)
			if str(response) == '<Response [200]>':
				channel_order_text = eval(response.text)
				channel_order_f = open(Utils.channel_order, "w")
				channel_order_f.write(channel_order_text)
				f.close()
	Utils.tools_log(Utils.channel_order)
	print(Utils.channel_order, flush=True)
	return

@app.route('/xml', methods=['GET'])
def serve_xml():
	Utils.tools_log('XML_SERVE')
	print('XML_SERVE', flush=True)

	if Utils.output_folder != None and Utils.output_folder != '':
		guide_out = os.path.join(Utils.output_folder, 'guide.xml')
	else:
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

	if Utils.output_folder != None and Utils.output_folder != '':
		m3u_out = os.path.join(Utils.output_folder, 'LiveStream.m3u')
	else:
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

#if __name__ == '__main__':
#	#app.run(debug=True, host='0.0.0.0')