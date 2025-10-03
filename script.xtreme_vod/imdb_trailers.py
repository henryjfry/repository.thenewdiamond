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
	import re, requests
	API_URL = "https://graphql.prod.api.imdb.a2z.com/"
	HEADERS = {
		'Referer': 'https://www.imdb.com/',
		'Origin': 'https://www.imdb.com',
		'User-Agent': 'Mozilla/5.0'
	}

	def gqlmin(q):
		return re.sub(' {4}', '', q)

	query_subpage = '''
	query TitleVideoGallerySubPage(
		$const: ID!,
		$first: Int!,
		$filter: VideosQueryFilter,
		$sort: VideoSort
	) {
		title(id: $const) {
			titleText { text }
			plot { plotText { plainText } }
			videoStrip(first: $first, filter: $filter, sort: $sort) {
				...VideoGalleryItems
			}
		}
	}
	'''
	query_pagination = '''
	query TitleVideoGalleryPagination(
		$const: ID!,
		$first: Int!,
		$after: ID!,
		$filter: VideosQueryFilter,
		$sort: VideoSort
	) {
		title(id: $const) {
			videoStrip(first: $first, after: $after, filter: $filter, sort: $sort) {
				...VideoGalleryItems
			}
		}
	}
	'''
	fragment = '''
	fragment VideoGalleryItems on VideoConnection {
		pageInfo {
			endCursor
			hasNextPage
		}
		total
		edges {
			node {
				id
				contentType { id }
				name { value }
				runtime { value }
				thumbnail { url }
				primaryTitle {
					series {
						displayableEpisodeNumber {
							displayableSeason {
								season
							}
						}
						series {
							titleText { text }
						}
					}
				}
			}
		}
	}
	'''

	variables = {
		"const": imdb_id,
		"first": 50,
		"filter": {"maturityLevel": "INCLUDE_MATURE","nameConstraints":{},"titleConstraints":{},"types":["TRAILER"]},
		"sort": {"by": "DATE", "order": "DESC"}
	}

	videos = []
	plot_text = ""
	item_title = ""
	total_videos = None

	# First page
	pdata = {
		'operationName': "TitleVideoGallerySubPage",
		'query': gqlmin(query_subpage + fragment),
		'variables': variables
	}
	r = requests.post(API_URL, headers=HEADERS, json=pdata)
	r.raise_for_status()
	json_data = r.json()

	title_data = json_data.get('data', {}).get('title', {})
	plot_text = title_data.get('plot', {}).get('plotText', {}).get('plainText', "")
	item_title = title_data.get('titleText', {}).get('text', "")

	video_data = title_data.get('videoStrip', {})
	total_videos = video_data.get('total')
	videos.extend([edge.get('node', {}) for edge in video_data.get('edges', [])])

	cursor = video_data.get('pageInfo', {}).get('endCursor')
	has_next = video_data.get('pageInfo', {}).get('hasNextPage', False)

	# Pagination loop
	while has_next and cursor:
		variables["after"] = cursor
		pdata = {
			'operationName': "TitleVideoGalleryPagination",
			'query': gqlmin(query_pagination + fragment),
			'variables': variables
		}
		r = requests.post(API_URL, headers=HEADERS, json=pdata)
		r.raise_for_status()
		video_data = r.json().get('data', {}).get('title', {}).get('videoStrip', {})
		videos.extend([edge.get('node', {}) for edge in video_data.get('edges', [])])
		cursor = video_data.get('pageInfo', {}).get('endCursor')
		has_next = video_data.get('pageInfo', {}).get('hasNextPage', False)
		time.sleep(0.3)

	# Match old output: inject plot, total, and item_title
	for idx, v in enumerate(videos):
		v["plot"] = plot_text
		v["total"] = total_videos
		v["item_title"] = item_title
		videos[idx] = v

	return videos

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
	

def get_video_info(viconst):
	API_URL = "https://graphql.prod.api.imdb.a2z.com/"
	HEADERS = {
		'Referer': 'https://www.imdb.com/',
		'Origin': 'https://www.imdb.com',
		'User-Agent': 'Mozilla/5.0',
		'Content-Type': 'application/json'
	}

	query = '''
	query VideoPlayback(
	  $viconst: ID!
	) {
	  video(id: $viconst) {
		contentType {
		  displayName {
			value
		  }
		}
		videoDimensions {
		  aspectRatio
		}
		...VideoInfo
		...SharedVideoAllPlaybackUrls
	  }
	}

	fragment VideoInfo on Video {
	  name {
		value
		language
	  }
	  description {
		value
		language
	  }
	  primaryTitle {
		genres {
		  genres {
			text
		  }
		}
		...BaseTitleCard
	  }
	}

	fragment BaseTitleCard on Title {
	  id
	  titleText {
		text
	  }
	  titleType {
		id
		text
		canHaveEpisodes
		displayableProperty {
		  value {
			plainText
		  }
		}
	  }
	  originalTitleText {
		text
	  }
	  primaryImage {
		id
		width
		height
		url
		caption {
		  plainText
		}
	  }
	  releaseYear {
		year
		endYear
	  }
	  ratingsSummary {
		aggregateRating
		voteCount
	  }
	  runtime {
		seconds
	  }
	  certificate {
		rating
	  }
	  canRate {
		isRatable
	  }
	  titleGenres {
		genres(limit: 3) {
		  genre {
			text
		  }
		}
	  }
	}

	fragment SharedVideoAllPlaybackUrls on Video {
	  playbackURLs {
		displayName {
		  value
		  language
		}
		videoMimeType
		videoDefinition
		url
	  }
	}
	'''

	variables = {
		"viconst": viconst,
		"userAgent": "Mozilla/5.0",
		"pageType": "VIDEO",
		"subPageType": "VIDEO",
		"viewportSize": {
			"width": 1920,
			"height": 1080
		},
		"autoStartVideo": False
	}

	response = requests.post(API_URL, headers=HEADERS, json={
		"operationName": "VideoPlayback",
		"query": query,
		"variables": variables
	})

	data = response.json()
	for i in data['data']['video']['playbackURLs']:
		if i['videoMimeType'] == 'MP4':
			url = i['url']
			video = i
	return url, video

def extract_imdb_mp4_url(video_id, best_trailer):
	"""
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
	"""
	url, video = get_video_info(video_id)
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

	try:best_trailer, video_url, video = extract_imdb_mp4_url(best_trailer['id'], best_trailer)
	except TypeError: return None
	return play_imdb_video(video_url=video_url, video=video, video_info=best_trailer)
