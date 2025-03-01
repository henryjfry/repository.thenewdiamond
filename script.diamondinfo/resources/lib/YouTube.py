from resources.lib import Utils
from resources.lib.library import addon_ID
from resources.lib.library import main_file_path
import xbmcaddon, xbmc
import os
from pathlib import Path
import html
from random import choice

#API_key = 'AIzaSyA-7-vxSFjNqfcOyCG33rwzRB0UZW30Pic'
try: API_key = xbmcaddon.Addon('plugin.video.youtube').getSetting('youtube.api.key')
except: API_key = ''
#https://github.com/umbrellaplug/umbrellaplug.github.io/blob/77057a7cf63ab8a628246c986197d3ff88cf0fbf/nexus/plugin.video.youtube/resources/lib/youtube_plugin/__init__.py#L11
if len(API_key) != 39:
	#xbmcaddon.Addon('plugin.video.youtube').setSetting('youtube.api.key','ODYxNTU2NzA4NDU0LWQ2ZGxtM2xoMDVpZGQ4bnBlazE4azZiZThiYTNvYzY4')
	#xbmcaddon.Addon('plugin.video.youtube').setSetting('youtube.api.id','QUl6YVN5QzZmdlpTSkhBN1Z6NWo4akNpS1J0N3RVSU9xakUyTjNn')
	#xbmcaddon.Addon('plugin.video.youtube').setSetting('youtube.api.secret','U2JvVmhvRzlzMHJOYWZpeENTR0dLWEFU')
	#API_key = xbmcaddon.Addon('plugin.video.youtube').getSetting('youtube.api.key')
	#API_key = choice(['AIzaSyA0LiS7G-KlrlfmREcCAXjyGqa_h_zfrSE', 'AIzaSyBOXZVC-xzrdXSAmau5UM3rG7rc8eFIuFw'])
	#API_key = 'AIzaSyA0LiS7G-KlrlfmREcCAXjyGqa_h_zfrSE'
	API_key = 'AIzaSyDCJJcBtvDsTH5f-7xJWeV10ZnoRZB_E50'


xbmc.log(str(API_key)+'===>OPENINFO', level=xbmc.LOGINFO)

def patch_youtube():
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.youtube'), 'resources','lib','youtube_plugin', 'youtube', 'client') , 'youtube.py')
	xbmc.log(str(file_path)+'===>OPENINFO', level=xbmc.LOGINFO)
	if os.path.exists(file_path) == False:
		return

	import json
	file1 = open(file_path, 'r')
	lines = file1.readlines()
	new_file = ''
	update_flag = False
	line_original = '_ = requests.get(url, params=params, headers=headers, verify=self._verify, allow_redirects=True)'
	line_update = '''            try: _ = requests.get(url, params=params, headers=headers, verify=self._verify, allow_redirects=True)  ## PATCH
            except: pass  ## PATCH
'''
	for idx, line in enumerate(lines):
		if '## PATCH' in str(line):
			update_flag = False
			xbmc.log('ALREADY_PATCHED_YOUTUBE_===>OPENINFO', level=xbmc.LOGINFO)
			break
		try: test_var = lines[idx+1]
		except: test_var = ''
		if line_original in str(line):
			new_file = new_file + line_update
			update_flag = True
		else:
			new_file = new_file + line
	file1.close()
	if update_flag:
		file1 = open(file_path, 'w')
		file1.writelines(new_file)
		file1.close()
		xbmc.log(str(file_path)+'_PATCH_YOUTUBE===>OPENINFO', level=xbmc.LOGINFO)

		addon_name = 'plugin.video.youtube'

		kodi_params = ('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":8,"params":{"addonid":"%s","enabled":false}}' % (addon_name))
		json_result = xbmc.executeJSONRPC(kodi_params)
		json_object  = json.loads(json_result)
		xbmc.log(str(json_object)+'_PATCH_YOUTUBE===>OPENINFO', level=xbmc.LOGINFO)
		
		kodi_params = ('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":8,"params":{"addonid":"%s","enabled":true}}' % (addon_name))
		json_result = xbmc.executeJSONRPC(kodi_params)
		json_object  = json.loads(json_result)
		xbmc.log(str(json_object)+'_PATCH_YOUTUBE===>OPENINFO', level=xbmc.LOGINFO)






def handle_youtube_videos(results, extended=False):
	videos = []
	youtube_thumb = Path(str(main_file_path()) + 'resources/skins/Default/media/common/youtube.png')
	for item in results:
		thumb = ''
		try: 
			snippet = item['snippet']
		except: 
			continue
			#item['snippet'] = {}
			#item['snippet']['description'] = ''
			#item['snippet']['title'] = item['id']['videoId']
			#item['snippet']['channelTitle'] = ''
			#item['snippet']['channelId'] = ''
			#item['snippet']['publishedAt'] = ''
		try: 
			if 'thumbnails' in item['snippet']:
				thumb = item['snippet']['thumbnails']['high']['url']
		except: 
				thumb = youtube_thumb
		if thumb == '':
			thumb = youtube_thumb
		try:
			video_id = item['id']['videoId']
		except:
			video_id = item['snippet']['resourceId']['videoId']
		video = {
			'thumb': thumb,
			'youtube_id': video_id,
			'Play': 'plugin://'+str(addon_ID())+'?info=youtubevideo&&id=' + video_id,
			'path': 'plugin://'+str(addon_ID())+'?info=youtubevideo&&id=' + video_id,
			'Description': item['snippet']['description'],
			'title': html.unescape(item['snippet']['title']),
			'channel_title': item['snippet']['channelTitle'],
			'channel_id': item['snippet']['channelId'],
			'Date': item['snippet']['publishedAt'].replace('T', ' ').replace('.000Z', '')[:-3]
			}
		videos.append(video)
	if not extended:
		return videos
	video_ids = [item['youtube_id'] for item in videos]
	API_key2 = API_key
	url = 'https://www.googleapis.com/youtube/v3/videos?id=%s&part=contentDetails%%2Cstatistics&key=%s' % (','.join(video_ids), API_key2)
	ext_results = Utils.get_JSON_response(url=url, cache_days=0.5, folder='YouTube')
	if 'quota' in str(ext_results):
		xbmc.log(str(ext_results)+'_QUOTA_YOUTUBE===>OPENINFO', level=xbmc.LOGINFO)
	if 'API_KEY_INVALID' in str(ext_results):
		xbmc.log(str(ext_results)+'_API_KEY_INVALID_YOUTUBE===>OPENINFO', level=xbmc.LOGINFO)
		#API_key2 = choice(['AIzaSyA0LiS7G-KlrlfmREcCAXjyGqa_h_zfrSE', 'AIzaSyBOXZVC-xzrdXSAmau5UM3rG7rc8eFIuFw'])
		#url = 'https://www.googleapis.com/youtube/v3/videos?id=%s&part=contentDetails%%2Cstatistics&key=%s' % (','.join(video_ids), API_key2)
		#ext_results = Utils.get_JSON_response(url=url, cache_days=0.5, folder='YouTube')
	if not ext_results:
		return videos
	for i, item in enumerate(videos):
		try: test_var = ext_results['items']
		except: continue
		for ext_item in ext_results['items']:
			if not item['youtube_id'] == ext_item['id']:
				continue
			item['duration'] = ext_item['contentDetails']['duration'][2:].lower()
			item['dimension'] = ext_item['contentDetails']['dimension']
			item['definition'] = ext_item['contentDetails']['definition']
			item['caption'] = ext_item['contentDetails']['caption']
			try: ext_item['statistics']['viewCount'] = int(ext_item['statistics']['viewCount'])
			except: ext_item['statistics']['viewCount'] = 0
			if 'statistics' in ext_item:
				if 'viewCount' in ext_item['statistics']:
					item['viewcount'] = Utils.millify(ext_item['statistics']['viewCount'])
				else:
					item['viewcount'] = 'unknown'
				if 'viewCount' in ext_item['statistics']:
					item['likes'] = ext_item['statistics'].get('likeCount')
				else:
					item['likes'] = 'unknown'
				if 'dislikeCount' in ext_item['statistics']:
					item['dislikes'] = ext_item['statistics'].get('dislikeCount')
				else:
					item['dislikes'] = 'unknown'
			else:
				item['viewcount'] = 'unknown'
				item['likes'] = 'unknown'
				item['dislikes'] = 'unknown'
			if item['likes'] and item['likes'] != 'unknown' and item['dislikes'] and item['dislikes'] != 'unknown':
				vote_count = float(int(item['likes']) + int(item['dislikes']))
				if vote_count > 0:
					item['rating'] = format(float(item['likes']) / vote_count * 10, '.2f')
			break
		else:
			item['duration'] = ''
	return videos

def search_youtube(search_str='', hd='', limit=None, extended=True, page='', filter_str=''):
	if page:
		page = '&pageToken=' + page
	if hd and not hd == 'false':
		hd = '&hd=true'
	else:
		hd = ''
	search_str = '&q=' + Utils.url_quote(search_str.replace('"', ''))
	API_key2 = API_key
	url = 'https://www.googleapis.com/youtube/v3/search?part=id%%2Csnippet&type=video%s%s&order=relevance&%skey=%s%s&maxResults=%i' % (page, search_str, filter_str, API_key2, hd, int(limit))
	#xbmc.log(str(url)+'YOUTUBE.PY===>OPENINFO', level=xbmc.LOGINFO)
	results = Utils.get_JSON_response(url=url, cache_days=0.5, folder='YouTube')
	if 'quota' in str(results).lower():
		xbmc.log(str(results)+'_QUOTA_YOUTUBE===>OPENINFO', level=xbmc.LOGINFO)
	if 'API_KEY_INVALID' in str(results):
		xbmc.log(str(results)+'_API_KEY_INVALID_YOUTUBE===>OPENINFO', level=xbmc.LOGINFO)
	#if 'API_KEY_INVALID' in str(results):
	#	API_key2 = choice(['AIzaSyA0LiS7G-KlrlfmREcCAXjyGqa_h_zfrSE', 'AIzaSyBOXZVC-xzrdXSAmau5UM3rG7rc8eFIuFw'])
	#	url = 'https://www.googleapis.com/youtube/v3/search?part=id%%2Csnippet&type=video%s%s&order=relevance&%skey=%s%s&maxResults=%i' % (page, search_str, filter_str, API_key2, hd, int(limit))
	#	results = Utils.get_JSON_response(url=url, cache_days=0.5, folder='YouTube')
		
	videos = handle_youtube_videos(results['items'], extended=extended)
	if videos:
		info = {
			'listitems': videos,
			'results_per_page': results['pageInfo']['resultsPerPage'],
			'total_results': results['pageInfo']['totalResults'],
			'next_page_token': results.get('nextPageToken', ''),
			'prev_page_token': results.get('prevPageToken', '')
			}
		return info
	else:
		return {}