import json
import requests
import time
import re


def print_log(log_item1, log_item2=None):
	try:
		import xbmc
		xbmc.log(str(log_item1)+str(log_item2)+'===>OPENINFO', level=xbmc.LOGFATAL)
	except:
		print(str(log_item1)+str(log_item2)+'===>OPENINFO')

def get_imdb_videos(imdb_id):

	def get_first_page(imdb_id, locale="en-GB", page_size=50):
		url = "https://api.graphql.imdb.com/"
		headers = {
			"Content-Type": "application/json",
			"User-Agent": "Mozilla/5.0",
			"Accept": "application/json"
		}
		variables = {
			"const": imdb_id,
			"first": page_size,
			"filter": {
				"maturityLevel": "INCLUDE_MATURE",
				"nameConstraints": {},
				"titleConstraints": {}
			},
			"locale": locale,
			"sort": {
				"by": "DATE",
				"order": "DESC"
			}
		}
		payload = {
			"operationName": "TitleVideoGallerySubPage",
			"variables": variables,
			"extensions": {
				"persistedQuery": {
					"version": 1,
					"sha256Hash": "e65c5b1d7cfedf8728d046ff3a76a323b20702713f5c03c8810dd9b09835d873"
				}
			}
		}
		response = requests.post(url, headers=headers, data=json.dumps(payload))
		x = 0
		if 'PersistedQueryNotFound' in str(response.text):
			while 'PersistedQueryNotFound' in str(response.text):
				response = requests.post(url, headers=headers, data=json.dumps(payload))
				time.sleep(0.3)
				x = x + 1
				if x == 100:
					break
		if "errorType" in str(response.text):
			print_log(response.text,'get_first_page'+str(x))
		data = response.json()
		video_data = data.get("data", {}).get("title", {}).get("videoStrip", {})
		plot = data.get("data", {}).get("title", {}).get("plot", {}).get("plotText", {}).get("plainText", "")
		edges = video_data.get("edges", [])
		videos = [edge.get("node", {}) for edge in edges]
		total = video_data.get("total", {})
		title = data.get("data", {}).get("title", {}).get("titleText", {}).get("text", {})
		print_log(videos)
		for idx, key in enumerate(videos):
			videos[idx]["plot"] = plot
			videos[idx]["total"] = total
			videos[idx]["item_title"] = title
		end_cursor = video_data.get("pageInfo", {}).get("endCursor")
		
		return videos, end_cursor

	def get_next_page(imdb_id, after_cursor):
		url = "https://caching.graphql.imdb.com/"
		headers = {
			"accept": "application/graphql+json, application/json",
			"content-type": "application/json",
			"x-imdb-client-name": "imdb-web-next",
			"x-imdb-user-country": "GB",
			"x-imdb-user-language": "en-GB",
			"user-agent": "Mozilla/5.0"
		}
		payload = {
			"operationName": "TitleVideoGalleryPagination",
			"variables": {
				"after": after_cursor,
				"const": imdb_id,
				"filter": {
					"maturityLevel": "INCLUDE_MATURE",
					"nameConstraints": {},
					"titleConstraints": {}
				},
				"first": 50,
				"locale": "en-GB",
				"sort": {
					"by": "DATE",
					"order": "DESC"
				}
			},
			"extensions": {
				"persistedQuery": {
					"sha256Hash": "e1710d91c7f00600952ca606dd8af0815f7448b173140e01bdbaf79d582b0187",
					"version": 1
				}
			}
		}
		response = requests.post(url, json=payload, headers=headers)
		#print_log(response.text,'get_next_page')

		x = 0
		if 'PersistedQueryNotFound' in str(response.text):
			while 'PersistedQueryNotFound' in str(response.text):
				response = requests.post(url, json=payload, headers=headers)
				time.sleep(0.3)
				x = x + 1
				if x == 100:
					break

		if "errorType" in str(response.text):
			print_log(response.text,'get_next_page'+str(x))

		data = response.json()
		video_data = data.get("data", {}).get("title", {}).get("videoStrip", {})
		edges = video_data.get("edges", [])
		videos = [edge.get("node", {}) for edge in edges]
		end_cursor = video_data.get("pageInfo", {}).get("endCursor")
		has_next_page = video_data.get("pageInfo", {}).get("hasNextPage", False)
		return videos, end_cursor, has_next_page

	def fetch_all_imdb_videos(imdb_id):
		all_videos = []
		videos, cursor = get_first_page(imdb_id)

		all_videos.extend(videos)
		print_log(f"Fetched {len(videos)} videos from first page")
		if len(videos) == 0:
			videos, cursor = get_first_page(imdb_id)
			if len(videos) == 0:
				return None
		plot = videos[0]['plot']
		total = videos[0]['total']
		item_title = videos[0]['item_title']
		while cursor:
			if len(all_videos) == total:
				break
			videos, cursor, has_next = get_next_page(imdb_id, cursor)
			for key in videos:
				videos[key]["plot"] = plot
				videos[key]["item_title"] = item_title
			all_videos.extend(videos)
			print_log(f"Fetched {len(videos)} more videos, total: {len(all_videos)}")
			if not has_next:
				break
			time.sleep(0.5)  # Be polite to the server

		return all_videos

	all_videos = fetch_all_imdb_videos(imdb_id)
	return all_videos

def time_format(seconds: int) -> str:
	if seconds is not None:
		seconds = int(seconds)
		d = seconds // (3600 * 24)
		h = seconds // 3600 % 24
		m = seconds % 3600 // 60
		s = seconds % 3600 % 60
		if d > 0:
			return '{:02d}D {:02d}H {:02d}m {:02d}s'.format(d, h, m, s)
		elif h > 0:
			return '{:02d}H {:02d}m {:02d}s'.format(h, m, s)
		elif m > 0:
			return '{:02d}m {:02d}s'.format(m, s)
		elif s > 0:
			return '{:02d}s'.format(s)
	return '-'

def extract_season_number(title):
	# Match "Season" or "Series" followed by optional spaces, optional punctuation, and digits
	pattern = r"(:?.*(?:Season|Series))(?:\s*\d*)"
	match = re.search(pattern, title, re.IGNORECASE)
	try: extract_season_number = int(match.group(0).replace(match.group(1),'').strip())
	except: extract_season_number = None
	return extract_season_number



def find_best_trailer(trailer_list, season_number=None):
	if len(trailer_list) == 0:
		return None
	best_match = None
	best_score = -1
	fallback_thumbnail = None
	trailer_list = sorted(trailer_list, key=lambda x: x['runtime']['value'], reverse=True)

	match_list = []
	new_trailer_list = []
	season_list = []
	official_flag = False
	theatrical_list = ['theatrical','full','final']
	theatrical_flag = False
	titleText = None


	for trailer in trailer_list:
		if trailer['contentType']['id'] == 'amzn1.imdb.video.contenttype.trailer':
			curr_dict = {}
			if trailer['primaryTitle'].get('series',{}) != {}:
				try: season = int(trailer['primaryTitle']['series']['displayableEpisodeNumber']['displayableSeason']['season'])
				except: season = None
			#print(trailer)
			curr_dict['id'] =  trailer['id']
			curr_dict['vid_url'] =  'https://www.imdb.com/video/%s/?ref_=ttvg_vi_1' % (str(trailer['id']))
			curr_dict['season'] = season
			curr_dict['title'] = trailer['name']['value']
			curr_dict['plot'] = trailer['plot']
			curr_dict['total'] = trailer['total']
			curr_dict['item_title'] = trailer['item_title']
			if season:
				titleText = trailer['primaryTitle']['series']['series']['titleText']['text']
			if not season:
				season = extract_season_number(curr_dict['title'])
				if season:
					curr_dict['season'] = season

			if  any(word in str(curr_dict['title']).lower() for word in theatrical_list):
				curr_dict['theatrical'] = True
				theatrical_flag = True
			else:
				curr_dict['theatrical'] = False

			if 'official' in str(curr_dict['title']).lower():
				curr_dict['official'] = True
				official_flag = True
				if season:
					official_flag = False
					curr_dict['official'] = False
			else:
				curr_dict['official'] = False
			if season and not season in season_list:
				season_list.append(season)
			curr_dict['thumbnail'] = trailer['thumbnail']['url']
			curr_dict['runtime'] = trailer['runtime']['value']
			curr_dict['time'] = time_format(trailer['runtime']['value'])
			curr_dict['titleText'] = titleText
			#print_log(curr_dict['title'])
			new_trailer_list.append(curr_dict)
	
	if season_number and season_number in season_list:
		season_match = True
	elif season_list != []:
		if season_number:
			for i in reversed(sorted(season_list)):
				if i <= season_number:
					break
			season_match = i
		else:
			season_match = False
	else:
		season_match = False
	
	if type(season_match) == type(season_number):
		if season_match > season_number:
			season_match = False

	offical_trailer = None
	season_trailer = None
	if season_match == True and type(season_match) == type(True):
		for trailer in new_trailer_list:
			if trailer['season'] == season_number:
				season_trailer = trailer
				break
	elif season_match == False:
		season_trailer = new_trailer_list[0]
	else:
		for trailer in new_trailer_list:
			if trailer['season'] == season_match:
				season_trailer = trailer
				break

	if theatrical_flag == True:
		for trailer in new_trailer_list:
			if trailer['theatrical']:
				offical_trailer = trailer
				break
	elif official_flag == True:
		for trailer in new_trailer_list:
			if trailer['official'] and not 'teaser' in str(trailer['title']).lower():
				offical_trailer = trailer
				break
		if not offical_trailer:
			for trailer in new_trailer_list:
				if trailer['official']:
					offical_trailer = trailer
					break

	elif titleText:
		for trailer in new_trailer_list:
			if trailer['title'] == titleText:
				offical_trailer = trailer
				break

	if offical_trailer and official_flag:
		if season_match == False or season_trailer == None:
			season_trailer = offical_trailer
	elif official_flag == False and offical_trailer:
		if season_match == False:
			season_trailer = offical_trailer
	#print(new_trailer_list)
	#print(titleText)
	return season_trailer

def extract_imdb_mp4_url(video_id, best_trailer):
	url = f"https://www.imdb.com/video/{video_id}?ref_=ttvg_vi_26"
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

	response = requests.get(url, headers=headers)
	if response.status_code != 200:
		raise Exception(f"Failed to fetch page: {response.status_code}")

	html = response.text
	PlaybackURL = ('[' + html.split('"playbackURLs":[')[1].split('}]')[0] + '}]')
	url = None
	for i in eval(PlaybackURL):
		if i['videoMimeType'] == 'MP4':
			return best_trailer, i['url'], i
		else:
			if not url:
				url = i['url']
				video = i
		#print(i['videoDefinition'])
		#print(i['videoMimeType'])
	return best_trailer, url, video

def play_imdb_video(video_url, video, video_info):
	import xbmcplugin
	import xbmcgui
	import xbmc
	try:
		from infotagger.listitem import ListItemInfoTag
	except:
		pass
	imdb_video = video_info
	if not 'trailer' in str(imdb_video['title']).lower():
		imdb_video['title'] = 'Trailer - ' + imdb_video['title'] 
	if not str(imdb_video['item_title']).lower() in str(imdb_video['title']).lower():
		imdb_video['title'] = imdb_video['title'] + ' - ' + imdb_video['item_title']

	xbmcplugin.setContent(0, 'movies')

	try:
		li = xbmcgui.ListItem(imdb_video['title'], iconImage=imdb_video['thumbnail'])
	except:
		li = xbmcgui.ListItem(imdb_video['title'], imdb_video['thumbnail'])

	li.setProperty('fanart_image', imdb_video['thumbnail'])
	li.setProperty('startoffset', str(0))
	li.setProperty('DBID', str(0))
	li.setProperty('MovieTitle', imdb_video['title'])

	li.setProperty('Duration', str(imdb_video['runtime']))

	li.setProperty('IsPlayable', 'true')
	li.setProperty('IsFolder', 'false')
	li.setPath(video_url)

	infolabels = {'year': None, 'premiered': None, 'aired': None, 'mpaa': None, 'genre': None, 'imdbnumber': None, 'duration': None, 'dateadded': None, 'rating': None, 'votes': None, 'tagline': None, 'mediatype': 'movie', 'title': imdb_video['title'], 'originaltitle': imdb_video['title'], 'sorttitle': imdb_video['title'], 'plot': imdb_video['plot'], 'plotoutline': imdb_video['plot'], 'studio': None, 'country': None, 'director': None, 'writer': None, 'status': None, 'trailer': video_url}

	#info_tag = ListItemInfoTag(li, 'video')

	#infolabels['imdbnumber'] = imdb
	try: infolabels['duration'] = int(imdb_video['runtime'])
	except: infolabels['duration'] = 0
	infolabels['mediatype'] = 'movie'
	infolabels['title'] = imdb_video['title']
	infolabels['originaltitle'] = imdb_video['title']
	infolabels['sorttitle'] = imdb_video['title']
	infolabels['playcount'] = 0
	li.setProperty('FileNameAndPath', str(video_url))
	infolabels['path'] = video_url
	infolabels['plot'] = imdb_video['plot']

	try:
		info_tag = ListItemInfoTag(li, 'video')
		info_tag.set_info(infolabels)
	except:
		li.setInfo(type='Video', infoLabels = infolabels)

	li.setArt({ 'poster': imdb_video['thumbnail'], 'fanart': imdb_video['thumbnail'], 'banner': None, 'clearlogo': None, 'landscape': imdb_video['thumbnail'], 'thumb': imdb_video['thumbnail']})

	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

	playlist.clear()
	xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
	playlist.add(video_url, li)
	#xbmcplugin.addDirectoryItem(handle=0, url=video_url , listitem=li, isFolder=False)
	xbmcplugin.setResolvedUrl(0, True, li)
	xbmcplugin.endOfDirectory(0)
	#xbmc.Player().play(item=video_url, listitem=li)
	xbmc.Player().play(playlist)


def play_imdb_trailer(imdb_id=None, select=False, season=None):
	all_videos = get_imdb_videos(imdb_id=imdb_id)
	if select == False:
		best_trailer = find_best_trailer(all_videos, season_number=season)
	else:
		listitems = []
		#print_log(all_videos)
		all_videos_new = []
		all_videos = sorted(all_videos, key=lambda x: x['runtime']['value'], reverse=True)
		for idx, i in enumerate(all_videos):
			if i['contentType']['id'] == 'amzn1.imdb.video.contenttype.trailer':
				all_videos_new.append(i)
				listitems += [{'label': i['name']['value'] + ' ' + time_format(i['runtime']['value']), 'poster': i['thumbnail']['url'],'label2': i['name']['value']}]
		from resources.lib.WindowManager import wm
		listitem, selection = wm.open_selectdialog_autoclose(listitems=listitems, autoclose=30, autoselect=0)
		if selection == -1:
			return None, meta
		if selection >= 0:
			idx = selection
		else:
			idx = 0
		best_trailer = find_best_trailer([all_videos_new[idx]], season_number=None)

	best_trailer, video_url, video = extract_imdb_mp4_url(best_trailer['id'], best_trailer)
	return play_imdb_video(video_url=video_url, video=video, video_info=best_trailer)
