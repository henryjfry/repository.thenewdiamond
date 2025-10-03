import os
import glob
import sys
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Subliminal'))
import tools 

cache_directory = tools.ADDON_USERDATA_PATH
def get_subs_file(cache_directory=None, video_path = None, same_folder=True, meta_info=None):
	import subliminal
	from babelfish import Language
	from subliminal import download_best_subtitles, region, save_subtitles, scan_videos, Video, list_subtitles, compute_score, download_subtitles
	from subliminal import refiners
	import requests

	import logging
	logging.disable(logging.CRITICAL)
	
	if cache_directory == None:
		tools.log('NO CACHE DIRECTORY PROVIDED')
		return None, None
	if cache_directory == None:
		tools.log('NO CACHE DIRECTORY PROVIDED')
		return None, None

	temp_directory = os.path.join(cache_directory,'temp')
	if not os.path.exists(cache_directory):
		os.mkdir(temp_directory)
	if not os.path.exists(temp_directory):
		os.mkdir(temp_directory)
	else:
		try: files = glob.glob(os.path.join(temp_directory,'*'))
		except AttributeError: files = glob(os.path.join(temp_directory,'*'))
		for f in files:
			os.remove(f)
	cache_file = os.path.join(cache_directory,'cachefile.dbm')

	opensubtitles_org_username = tools.get_setting('opensubtitles_org_username')
	opensubtitles_org_password = tools.get_setting('opensubtitles_org_password')
	opensubtitles_com_username = tools.get_setting('opensubtitles_com_username')
	opensubtitles_com_password = tools.get_setting('opensubtitles_com_password')
	opensubtitlescom_credentials = {'username': opensubtitles_com_username, 'password': opensubtitles_com_password}
	opensubtitles_credentials = {'username': opensubtitles_org_username, 'password': opensubtitles_org_password}

	tmdb_apikey = tools.get_setting('tmdb_api')
	# configure the cache
	region.configure('dogpile.cache.dbm', arguments={'filename': cache_file},replace_existing_backend=True)

	#import subs_hash

	file_path = video_path

	from urllib.parse import unquote

	dir_source = None
	if not os.path.isfile(file_path):
		#use a temp folder where file isnt a file, eg a url
		#same_folder = False
		#MBFACTOR = float(1 << 20)
		response = requests.head(file_path, allow_redirects=True)
		size = response.headers.get('content-length', 0)
		#file_path = unquote(file_path)
		size = int(size)
		filesize = size
		##'hashes': {'opensubtitles': 'e45d225d49846408', 'opensubtitlescom': 'e45d225d49846408'}
		#http_file = True
		##returnedhash, filesize = subs_hash.hashFile_url(file_path)
		##tools.log(returnedhash, filesize)
		##hashes = {'opensubtitles': returnedhash, 'opensubtitlescom': returnedhash}
		hashes = {'opensubtitles': 'e45d225d49846408', 'opensubtitlescom': 'e45d225d49846408'}
	else:
		dir_source =  os.path.dirname(file_path)
		size = os.stat(file_path).st_size
		#http_file = False
		#returnedhash, filesize = subs_hash.hashFile_url(file_path)
		#tools.log(returnedhash, filesize)
		#hashes = {'opensubtitles': returnedhash, 'opensubtitlescom': returnedhash}
		filesize = size
		hashes = {'opensubtitles': 'e45d225d49846408', 'opensubtitlescom': 'e45d225d49846408'}

	subs_out = os.path.basename(file_path)
	subs_out_FORCED = os.path.splitext(subs_out)[0] + str('.ENG.FOREIGN.PARTS.srt')
	subs_out_ENG = os.path.splitext(subs_out)[0] + str('.ENG.srt')
	subs_out_HEARING = os.path.splitext(subs_out)[0] + str('.ENG.srt')

	if same_folder == True:
		out_directory = dir_source
	else:
		out_directory = temp_directory

	#video = Video.fromname(file_path)
	#if not http_file:
	#	video = refiners.hash.refine(video, providers=['opensubtitles','addic7ed','napiprojekt','opensubtitlescom','podnapisi','tvsubtitles'],languages={Language('eng')})

	#tools.log(meta_info)
	if meta_info['mediatype'] == 'movie':
		from subliminal.video import Movie
		video = Movie(name=meta_info['title'],title=meta_info['title'], year=meta_info['year'])
	else:
		from subliminal.video import Episode
		video = Episode(name=meta_info['title'], series=meta_info['show_title'], season=meta_info['season'], episodes=[meta_info['episode']])
	video = refiners.tmdb.refine(video, apikey=tmdb_apikey)


	video.__dict__['size'] = filesize
	video.__dict__['hashes'] = hashes

	"""
	{'name': '/folder/folder/file_path.mp4', 'source': 'Blu-ray', 'release_group': 'RARBG', 'streaming_service': None, 'resolution': '720p', 'video_codec': 'H.264', 'audio_codec': 'AAC', 'frame_rate': None, 'duration': None, 'hashes': {}, 'size': None, 'subtitles': set(), 'title': 'Movie Title', 'year': 2021, 'country': None, 'imdb_id': None, 'tmdb_id': None, 'alternative_titles': []}
	"""
	tools.log(video.__dict__)
	
	#video.__dict__['episodes'] = [6]

	#if meta_info['mediatype'] == 'movie':
	#	subtitles = list_subtitles([video], languages={Language('eng')}, providers=['opensubtitles','addic7ed','opensubtitlescom'],	provider_configs={'opensubtitlescom': opensubtitlescom_credentials, 'opensubtitles': opensubtitles_credentials})
	#	if len(subtitles[video]) < 50:
	#		subtitles2 = list_subtitles([video], languages={Language('eng')}, providers=['napiprojekt','podnapisi','tvsubtitles'])
	#		subtitles.extend(subtitles2)
	#else:
	#	subtitles = list_subtitles([video], languages={Language('eng')}, providers=['opensubtitles','addic7ed','napiprojekt','opensubtitlescom','podnapisi','tvsubtitles'],	provider_configs={'opensubtitlescom': opensubtitlescom_credentials, 'opensubtitles': opensubtitles_credentials})
	all_subtitles = None
	for provider in ['addic7ed','opensubtitles','podnapisi','tvsubtitles','gestdown','subtitulamos','napiprojekt']:
		try: mediatype = meta['episode_meta']['mediatype']
		except: mediatype = 'movie'
		#if provider == 'opensubtitlescom' and mediatype == 'movie' and len(all_subtitles[video]) >= 80:
		#	continue
		subtitles = list_subtitles([video], languages={Language('eng')}, providers=[provider],	provider_configs={'opensubtitlescom': opensubtitlescom_credentials, 'opensubtitles': opensubtitles_credentials})
		tools.log(provider + '___' + str(len(subtitles[video])))
		if all_subtitles:
			try: all_subtitles[video].extend(subtitles[video])
			except: continue
		else:
			all_subtitles = subtitles
		try:
			if len(all_subtitles[video]) >= 200:
				break
		except: 
			pass
	subtitles = all_subtitles

	tools.log(len(subtitles[video]))
	tools.log('len(subtitles[video])')
	high_score_forced = 0
	high_score_HEARING = 0
	high_score = 0
	curr_subs_forced = None
	curr_subs_HEARING = None
	curr_subs = None

	if len(subtitles[video]) > 50:
		#from subliminal.utils import compute_score  # or your own version

		# Pre-sort by computed score or any criteria
		filtered = [s for s in subtitles[video] if not s.hearing_impaired]

		# Only take the top 100 best-matching subtitles
		limited_subtitles = filtered[:99]
		subtitles = limited_subtitles
	else:
		limited_subtitles = subtitles[video]

	tools.log(limited_subtitles)
	for i in limited_subtitles:
		try:
			if i.__dict__['matched_by'] == 'imdbid':
				imdbid = True
			else:
				imdbid = False
		except:
			imdbid = False

		if 'parts' in str(i.__dict__).lower() or 'foreign' in str(i.__dict__).lower() or 'Forced' in str(i.__dict__):
			#tools.log()
			#tools.log(i)
			curr_score_forced = compute_score(i, video)
			if imdbid:
				curr_score_forced = curr_score_forced + 200
			if curr_score_forced > high_score_forced:
				if high_score_forced == 0 and curr_score_forced < 500:
					matches = i.get_matches(video)
					if 'episode' in str(matches) and 'season' in str(matches) and not 'series' in str(matches):
						continue
				high_score_forced = curr_score_forced
				curr_subs_forced = i
				curr_subs_forced_dict = i.__dict__
				try:
					if curr_subs_forced_dict.get('filename','') == '':
						curr_subs_forced_dict['filename'] = curr_subs_forced_dict['file_name']
				except:
					#tools.log(i.__dict__)
					curr_subs_forced_dict['filename'] = subs_out_FORCED
					#tools.log('except')
					#tools.log(curr_subs_forced_dict)
			#tools.log(i.__dict__)
			#tools.log(video.__dict__)
			#tools.log(i.get_matches(video))
			#sorted(i.get_matches(video))
			#tools.log()
		if not ('parts' in str(i.__dict__).lower() or 'foreign' in str(i.__dict__).lower() or 'Forced' in str(i.__dict__)) and not 'HEARING' in str(i.__dict__):
			curr_score = compute_score(i, video)
			if imdbid:
				curr_score = curr_score + 200
			if curr_score > high_score:
				high_score = curr_score
				curr_subs = i
				curr_subs_dict = i.__dict__
				try:
					if curr_subs_dict.get('filename','') == '':
						curr_subs_dict['filename'] = curr_subs_dict['file_name']
				except:
					#tools.log(i.__dict__)
					curr_subs_dict['filename'] = subs_out_ENG
					#tools.log('except')
					#tools.log(curr_subs_dict)
		elif not ('parts' in str(i.__dict__).lower() or 'foreign' in str(i.__dict__).lower()  or 'Forced' in str(i.__dict__)) and 'HEARING' in str(i.__dict__):
			curr_score_HEARING = compute_score(i, video)
			if imdbid:
				curr_score_HEARING = curr_score_HEARING + 200
			if curr_score_HEARING > high_score_HEARING:
				high_score_HEARING = curr_score_HEARING
				curr_subs_HEARING = i
				curr_subs_HEARING_dict = i.__dict__
				try:
					if curr_subs_HEARING_dict.get('filename','') == '':
						curr_subs_HEARING_dict['filename'] = curr_subs_HEARING_dict['file_name']
				except:
					#tools.log(i.__dict__)
					curr_subs_dict['filename'] = subs_out_HEARING
					#tools.log('except')
					#tools.log(curr_subs_dict)
	if curr_subs_forced:
		tools.log(curr_subs_forced_dict)
		try:
			if curr_subs_forced_dict.get('page_link',None):
				tools.log(os.path.join(curr_subs_forced_dict['page_link'], curr_subs_forced_dict['filename']))
			else:
				tools.log(curr_subs_forced_dict['filename'])
		except:
			tools.log('except')
			#tools.log(curr_subs_forced_dict)
		download_subtitles([curr_subs_forced])
		try: file_type =  os.path.splitext(curr_subs_forced_dict['filename'])[1]
		except: file_type = '.srt'
		subs_out_FORCED = subs_out_FORCED.replace('.srt',file_type)
		subs_out_FORCED = os.path.join(out_directory, subs_out_FORCED)
		with open(subs_out_FORCED, 'w') as f:
			f.write(curr_subs_forced.text)
		if file_type == '.ass':
			subs_hash.ass_to_srt(subs_out_FORCED, subs_out_FORCED.replace(file_type,'.srt'))
			subs_out_FORCED = subs_out_FORCED.replace(file_type,'.srt')
	else:
		subs_out_FORCED = None

	if curr_subs:
		tools.log(curr_subs_dict)
		try:
			if curr_subs_dict.get('page_link',None):
				tools.log(os.path.join(curr_subs_dict['page_link'], curr_subs_dict['filename']))
			else:
				tools.log(curr_subs_dict['filename'])
		except:
			tools.log('except')
			#tools.log(curr_subs_dict)
		try: file_type =  os.path.splitext(curr_subs_dict['filename'])[1]
		except: file_type = '.srt'
		download_subtitles([curr_subs])
		subs_out_ENG = subs_out_ENG.replace('.srt',file_type)
		subs_out_ENG = os.path.join(out_directory, subs_out_ENG)
		with open(subs_out_ENG, 'w') as f:
			f.write(curr_subs.text)

		if file_type == '.ass':
			subs_hash.ass_to_srt(subs_out_ENG, subs_out_ENG.replace(file_type,'.srt'))
			subs_out_ENG = subs_out_ENG.replace(file_type,'.srt')
	else:
		subs_out_ENG = None

	if subs_out_ENG == None and curr_subs_HEARING:
		tools.log(curr_subs_HEARING_dict)
		try:
			if curr_subs_HEARING_dict.get('page_link',None):
				tools.log(os.path.join(curr_subs_HEARING_dict['page_link'], curr_subs_HEARING_dict['filename']))
			else:
				tools.log(curr_subs_HEARING_dict['filename'])
		except:
			tools.log('except')
			#tools.log(curr_subs_HEARING_dict)
		download_subtitles([curr_subs_HEARING])
		try: file_type =  os.path.splitext(curr_subs_HEARING_dict['filename'])[1]
		except: file_type = '.srt'
		subs_out_HEARING = subs_out_HEARING.replace('.srt',file_type)
		subs_out_HEARING = os.path.join(out_directory, subs_out_HEARING)
		with open(subs_out_HEARING, 'w') as f:
			f.write(curr_subs_HEARING.text)
		if file_type == '.ass':
			subs_hash.ass_to_srt(subs_out_HEARING, subs_out_HEARING.replace(file_type,'.srt'))
			subs_out_HEARING = subs_out_HEARING.replace(file_type,'.srt')
		subs_out_ENG = subs_out_HEARING
	else:
		subs_out_HEARING = None
		


	return subs_out_ENG, subs_out_FORCED
	"""
	#save_subtitles(video, curr_subs,directory='/home/osmc/.kodi/userdata/addon_data/script.xtreme_vod/temp')

	subtitles = download_best_subtitles([video], languages={Language('eng')}, providers=['opensubtitlescom'],	provider_configs={'opensubtitlescom': opensubtitlescom_credentials, 'opensubtitles': opensubtitles_credentials} , hearing_impaired=False)
	tools.log(subtitles[video])
	save_subtitles(video, subtitles[video],directory='/home/osmc/.kodi/userdata/addon_data/script.xtreme_vod/temp')
	"""
#file_path = "/home/osmc/Movies/Star Trek Deep Space Nine (1993)/Star Trek Deep Space Nine - Season 01/Star Trek Deep Space Nine - S01E01 - Emissary (1).mkv"
#subs_out_ENG, subs_out_FORCED = get_subs_file(cache_directory=tools.ADDON_USERDATA_PATH, video_path = file_path, same_folder=True)