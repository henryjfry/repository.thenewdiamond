# -*- coding: utf-8 -*-
# created by Venom for Fenomscrapers (updated 7-19-2022) ud (updated 05/22/24)
'''
	Fenomscrapers Project
'''

from json import loads as jsloads
import re
from cocoscrapers.modules import client
from cocoscrapers.modules import source_utils, cache
from cocoscrapers.modules import log_utils
from time import time
from cocoscrapers.modules.control import setting as getSetting, homeWindow, sleep

class source:
	priority = 1
	pack_capable = True
	hasMovies = True
	hasEpisodes = True
	def __init__(self):
		self.language = ['en']
		self.base_link = "https://torrentio.strem.fun"
		#self.movieSearch_link = '/providers=yts,eztv,rarbg,1337x,thepiratebay,kickasstorrents,torrentgalaxy|language=english/stream/movie/%s.json' #found this to be broken 12-9-22 umbrelladev
		#self.tvSearch_link = '/providers=yts,eztv,rarbg,1337x,thepiratebay,kickasstorrents,torrentgalaxy|language=english/stream/series/%s:%s:%s.json' #found this to be broken 12-9-22 umbrelladev
		#self.movieSearch_link = '/providers=yts,eztv,rarbg,1337x,thepiratebay,kickasstorrents,torrentgalaxy/stream/movie/%s.json'
		#self.tvSearch_link = '/providers=yts,eztv,rarbg,1337x,thepiratebay,kickasstorrents,torrentgalaxy/stream/series/%s:%s:%s.json'
		self.movieSearch_link = '/stream/movie/%s.json'
		self.item_totals = {'4K': 0, '1080p': 0, '720p': 0, 'SD': 0, 'CAM': 0 }
		self.tvSearch_link = '/stream/series/%s:%s:%s.json'
		self.min_seeders = 0
		self.bypass_filter = getSetting('torrentio.bypass_filter')
# Currently supports YTS(+), EZTV(+), RARBG(+), 1337x(+), ThePirateBay(+), KickassTorrents(+), TorrentGalaxy(+), HorribleSubs(+), NyaaSi(+), NyaaPantsu(+), Rutor(+), Comando(+), ComoEuBaixo(+), Lapumia(+), OndeBaixa(+), Torrent9(+).

	def _get_files(self, url):
		if self.get_pack_files: return []
		results = client.request(url, timeout=10)
		files = jsloads(results)['streams']
		return files

	def sources(self, data, hostDict):
		self.get_pack_files = False
		sources = []
		if not data:
			homeWindow.clearProperty('cocoscrapers.torrentio.performing_single_scrape')
			return sources
		sources_append = sources.append
		try:
			startTime = time()
			aliases = data['aliases']
			year = data['year']
			imdb = data['imdb']
			if 'tvshowtitle' in data:
				homeWindow.setProperty('cocoscrapers.torrentio.performing_single_scrape', 'true')
				title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
				episode_title = data['title']
				season = data['season']
				episode = data['episode']
				hdlr = 'S%02dE%02d' % (int(season), int(episode))
				years = None
				url = '%s%s' % (self.base_link, self.tvSearch_link % (imdb, season, episode))
				files = cache.get(self._get_files, 10, url)
			else:
				title = data['title'].replace('&', 'and').replace('/', ' ').replace('$', 's')
				episode_title = None
				hdlr = year
				years = [str(int(year)-1), str(year), str(int(year)+1)]
				url = '%s%s' % (self.base_link, self.movieSearch_link % imdb)
				files = self._get_files(url)
			homeWindow.clearProperty('cocoscrapers.torrentio.performing_single_scrape')
			_INFO = re.compile(r'👤.*')
			undesirables = source_utils.get_undesirables()
			check_foreign_audio = source_utils.check_foreign_audio()
		except:
			homeWindow.clearProperty('cocoscrapers.torrentio.performing_single_scrape')
			source_utils.scraper_error('TORRENTIO')
			return sources

		for file in files:
			try:
				hash = file['infoHash']
				file_title = file['title'].split('\n')
				file_info = [x for x in file_title if _INFO.match(x)][0]
				name = source_utils.clean_name(file_title[0])
				if self.bypass_filter == 'false':
					if not source_utils.check_title(title, aliases, name.replace('.(Archie.Bunker', ''), hdlr, year, years): continue
				name_info = source_utils.info_from_name(name, title, year, hdlr, episode_title)
				if source_utils.remove_lang(name_info, check_foreign_audio): continue
				if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

				url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name) 
				try:
					seeders = int(re.search(r'(\d+)', file_info).group(1))
					if self.min_seeders > seeders: continue
				except: seeders = 0

				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					size = re.search(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', file_info).group(0)
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				sources_append({'provider': 'torrentio', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info,
											'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
				self.item_totals[quality] += 1
			except:
				homeWindow.clearProperty('cocoscrapers.torrentio.performing_single_scrape')
				source_utils.scraper_error('TORRENTIO')
		logged = False
		for quality in self.item_totals:
			if self.item_totals[quality] > 0:
				log_utils.log('#STATS - TORRENTIO found {0:2.0f} {1}'.format(self.item_totals[quality], quality))
				logged = True
		if not logged: log_utils.log('#STATS - TORRENTIO found nothing')
		endTime = time()
		log_utils.log('#STATS - TORRENTIO took %.2f seconds' % (endTime - startTime))
		return sources

	def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
		self.get_pack_files = True
		sources = []
		if not data: return sources
		count, finished_single_scrape = 0, False
		sleep(2000)
		while count < 10000 and not finished_single_scrape:
			finished_single_scrape = homeWindow.getProperty('cocoscrapers.torrentio.performing_single_scrape') != 'true'
			sleep(100)
			count += 100
		if not finished_single_scrape: return sources
		sources_append = sources.append
		try:
			startTime = time()
			title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
			aliases = data['aliases']
			imdb = data['imdb']
			year = data['year']
			season = data['season']
			url = '%s%s' % (self.base_link, self.tvSearch_link % (imdb, season, data['episode']))
			files = cache.get(self._get_files, 10, url)
			_INFO = re.compile(r'👤.*')
			undesirables = source_utils.get_undesirables()
			check_foreign_audio = source_utils.check_foreign_audio()
		except:
			source_utils.scraper_error('TORRENTIO')
			return sources

		for file in files:
			try:
				hash = file['infoHash']
				file_title = file['title'].split('\n')
				file_info = [x for x in file_title if _INFO.match(x)][0]
				name = source_utils.clean_name(file_title[0])
				if self.bypass_filter == 'true': bypass_filter = True

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
				try:
					seeders = int(re.search(r'(\d+)', file_info).group(1))
					if self.min_seeders > seeders: continue
				except: seeders = 0

				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					size = re.search(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', file_info).group(0)
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				item = {'provider': 'torrentio', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
							'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize, 'package': package}
				if search_series: item.update({'last_season': last_season})
				elif episode_start: item.update({'episode_start': episode_start, 'episode_end': episode_end}) # for partial season packs
				sources_append(item)
				self.item_totals[quality] += 1
			except:
				source_utils.scraper_error('TORRENTIO')
		logged = False
		for quality in self.item_totals:
			if self.item_totals[quality] > 0:
				log_utils.log('#STATS - TORRENTIO(pack) found {0:2.0f} {1}'.format(self.item_totals[quality], quality))
				logged = True
		if not logged: log_utils.log('#STATS - TORRENTIO(pack) found nothing')
		endTime = time()
		log_utils.log('#STATS - TORRENTIO(pack) took %.2f seconds' % (endTime - startTime))
		return sources