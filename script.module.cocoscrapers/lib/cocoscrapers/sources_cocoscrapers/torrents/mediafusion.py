# created by Venom for Fenomscrapers (updated 3-02-2022) modified by umbrella_dev 10-8-24
"""
	Cocoscrapers Project
"""

from json import dumps as jsdumps
import base64, re, requests
from cocoscrapers.modules import source_utils, cache
from cocoscrapers.modules.control import homeWindow, sleep
from cocoscrapers.modules import log_utils
from cocoscrapers.modules import control
session = requests.Session()
from time import time


class source:
	priority = 2
	pack_capable = True
	hasMovies = True
	hasEpisodes = True
	def __init__(self):
		self.language = ['en']
		if control.setting('mediafusion.usecustomurl') == 'true': 
			self.base_link = control.setting('mediafusion.customurl')
		else:
			self.base_link = 'https://mediafusion.elfhosted.com'
		if self.base_link == '':
			self.base_link = 'https://mediafusion.elfhosted.com'
		self.movieSearch_link = '/stream/movie/%s.json'
		self.tvSearch_link = '/stream/series/%s:%s:%s.json'
		self.item_totals = {
			'4K': 0,
			'1080p': 0,
			'720p': 0,
			'SD': 0,
			'CAM': 0 
			}
		self.min_seeders = 0
# Currently supports BITSEARCH(+), EZTV(+), ThePirateBay(+), TheRARBG(+), YTS(+)

	def _get_files(self, url):
		if control.setting('mediafusion_user_data') == '':
			headers = {
				'encoded_user_data': 'eyJlbmFibGVfY2F0YWxvZ3MiOiBmYWxzZSwgIm1heF9zdHJlYW1zX3Blcl9yZXNvbHV0aW9uIjogOTksICJ0b3JyZW50X3NvcnRpbmdfcHJpb3JpdHkiOiBbXSwgImNlcnRpZmljYXRpb25fZmlsdGVyIjogWyJEaXNhYmxlIl0sICJudWRpdHlfZmlsdGVyIjogWyJEaXNhYmxlIl19'
			}
		else:
			headers = {
				'encoded_user_data': control.setting('mediafusion_user_data')
			}
		if self.get_pack_files: return []
		results = session.get(url, headers=headers, timeout=10)
		files = results.json()['streams']
		return files

	def sources(self, data, hostDict):
		self.get_pack_files = False
		sources = []
		if not data:
			homeWindow.clearProperty('cocoscrapers.mediafusion.performing_single_scrape')
			return sources
		append = sources.append
		self.pack_get = False
		try:
			startTime = time()
			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ')
			aliases = data['aliases']
			episode_title = data['title'] if 'tvshowtitle' in data else None
			year = data['year']
			imdb = data['imdb']
			
			if 'tvshowtitle' in data:
				homeWindow.setProperty('cocoscrapers.mediafusion.performing_single_scrape', 'true')
				season = data['season']
				episode = data['episode']
				hdlr = 'S%02dE%02d' % (int(season), int(episode))
				url = '%s%s' % (self.base_link, self.tvSearch_link % (imdb, season, episode))
				files = cache.get(self._get_files, 10, url)
			else:
				url = '%s%s' % (self.base_link, self.movieSearch_link % (imdb))
				hdlr = year
				files = self._get_files(url)
			#log_utils.log('mediafusion sources url = %s' % url)
			homeWindow.clearProperty('cocoscrapers.mediafusion.performing_single_scrape')
			_INFO = re.compile(r'💾.*')
			undesirables = source_utils.get_undesirables()
			check_foreign_audio = source_utils.check_foreign_audio()
		except:
			homeWindow.clearProperty('cocoscrapers.mediafusion.performing_single_scrape')
			source_utils.scraper_error('MEDIAFUSION')
			return sources
		for file in files:
			try:
				if 'tvshowtitle' in data:
					#hash = file['url'].split('info_hash=')[1]
					#hash = hash.split('&season=')[0]
					hash = file['infoHash']
				else:
					#hash = file['url'].split('info_hash=')[1]
					hash = file['infoHash']
				#log_utils.log('mediafusion hash: %s' % hash)
				file_title = file['description'].split('\n')
				#file_title = file['behaviorHints']['filename']
				file_info = [x for x in file_title if _INFO.match(x)][0]
				name = source_utils.clean_name(file_title[0])

				if not source_utils.check_title(title, aliases, name.replace('.(Archie.Bunker', ''), hdlr, year): continue
				name_info = source_utils.info_from_name(name, title, year, hdlr, episode_title)
				if source_utils.remove_lang(name_info, check_foreign_audio): continue
				if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

				url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name) 

				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					size = re.search(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', file_info).group(0)
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				append({'provider': 'mediafusion', 'source': 'torrent', 'seeders': 0, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
							'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
				self.item_totals[quality] += 1
			except:
				homeWindow.clearProperty('cocoscrapers.mediafusion.performing_single_scrape')
				source_utils.scraper_error('MEDIAFUSION')
		logged = False
		for quality in self.item_totals:
			if self.item_totals[quality] > 0:
				log_utils.log('#STATS - MEDIAFUSION found {0:2.0f} {1}'.format(self.item_totals[quality],quality) )
				logged = True
		endTime = time()
		if not logged: log_utils.log('#STATS - MEDIASEARCH found nothing')
		log_utils.log('#STATS - MEDIAFUSION took %.2f seconds' % (endTime - startTime))
		return sources

	def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
		self.get_pack_files = True
		sources = []
		if not data: return sources
		count, finished_single_scrape = 0, False
		startTime = time()
		sleep(2000)
		while count < 10000 and not finished_single_scrape:
			finished_single_scrape = homeWindow.getProperty('cocoscrapers.mediafusion.performing_single_scrape') != 'true'
			sleep(100)
			count += 100
		if not finished_single_scrape: return sources
		sleep(1000)
		sources_append = sources.append
		try:
			title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ')
			aliases = data['aliases']
			imdb = data['imdb']
			year = data['year']
			season = data['season']
			url = '%s%s' % (self.base_link, self.tvSearch_link % (imdb, season, data['episode']))
			files = cache.get(self._get_files, 10, url)
			_INFO = re.compile(r'💾.*') # _INFO = re.compile(r'👤.*')
			undesirables = source_utils.get_undesirables()
			check_foreign_audio = source_utils.check_foreign_audio()
		except:
			source_utils.scraper_error('MEDIAFUSION')
			return sources
		for file in files:
			#log_utils.log('pack file: %s' % str(file),1)
			try:
				hash = file['infoHash']
				file_title = file['description']
				file_info = [x for x in file_title if _INFO.match(x)][0]

				name = source_utils.clean_name(file_title[0])

				episode_start, episode_end = 0, 0
				if not search_series:
					if not bypass_filter:
						valid, episode_start, episode_end = source_utils.filter_season_pack(title, aliases, year, season, name.replace('.(Archie.Bunker', ''))
						if not valid: continue
					package = 'season'

				elif search_series:
					if not bypass_filter:
						valid, last_season = source_utils.filter_show_pack(title, aliases, imdb, year, season, name.replace('.(Archie.Bunker', ''), total_seasons)
						if not valid: continue
					else: last_season = total_seasons
					package = 'show'

				name_info = source_utils.info_from_name(name, title, year, season=season, pack=package)
				if source_utils.remove_lang(name_info, check_foreign_audio): continue
				if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

				url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)
				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					size = re.search(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', file_info).group(0)
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				item = {'provider': 'mediafusion', 'source': 'torrent', 'seeders': 0, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
							'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize, 'package': package}
				if search_series: item.update({'last_season': last_season})
				elif episode_start: item.update({'episode_start': episode_start, 'episode_end': episode_end}) # for partial season packs
				self.item_totals[quality] += 1
				sources_append(item)
			except:
				source_utils.scraper_error('MEDIAFUSION')
		logged = False
		for quality in self.item_totals:
			if self.item_totals[quality] > 0:
				log_utils.log('#STATS - MEDIAFUSION(pack) found {0:2.0f} {1}'.format(self.item_totals[quality],quality) )
				logged = True
		endTime = time()
		if not logged: log_utils.log('#STATS - MEDIAFUSION(pack) found nothing')
		log_utils.log('#STATS - MEDIAFUSION(pack) took %.2f seconds' % (endTime - startTime))
		return sources

