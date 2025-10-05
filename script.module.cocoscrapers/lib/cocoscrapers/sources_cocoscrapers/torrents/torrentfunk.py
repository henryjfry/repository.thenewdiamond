# -*- coding: utf-8 -*-
# created by Venom for Fenomscrapers (updated 7-19-2022)
"""
	Fenomscrapers Project
"""

import re
from urllib.parse import quote_plus
from cocoscrapers.modules import client
from cocoscrapers.modules import source_utils
from cocoscrapers.modules import workers
from cocoscrapers.modules import log_utils
from time import time


class source:
	priority = 8
	pack_capable = True
	hasMovies = True
	hasEpisodes = True
	def __init__(self):
		self.language = ['en']
		self.base_link = "https://www.torrentfunk.com"
		self.tvsearch_link = '/television/torrents/%s.html?v=on&smi=0&sma=0&i=75&sort=size&o=desc'
		self.msearch_link = '/movie/torrents/%s.html?v=on&smi=0&sma=0&i=75&sort=size&o=desc'
		self.item_totals = {'4K': 0, '1080p': 0, '720p': 0, 'SD': 0, 'CAM': 0}
		self.min_seeders = 0

	def sources(self, data, hostDict):
		self.sources = []
		if not data: return self.sources
		self.sources_append = self.sources.append
		try:
			startTime = time()
			self.aliases = data['aliases']
			self.year = data['year']
			if 'tvshowtitle' in data:
				self.title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
				self.episode_title = data['title']
				self.hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode']))
				search_link = self.tvsearch_link
			else:
				self.title = data['title'].replace('&', 'and').replace('/', ' ').replace('$', 's')
				self.episode_title = None
				self.hdlr = self.year
				search_link = self.msearch_link
			query = '%s %s' % (re.sub(r'[^A-Za-z0-9\s\.-]+', '', self.title), self.hdlr)
			url = '%s%s' % (self.base_link, search_link % quote_plus(query))
			# log_utils.log('url = %s' % url)
			results = client.request(url, timeout=5)
			if not results: return self.sources
			table = client.parseDOM(results, 'table', attrs={'class': 'tmain'})[0]
			links = re.findall(r'<a\s*href\s*=\s*["\'](/torrent/.+?)["\']>(.+?)</a>', table, re.DOTALL | re.I)
			self.undesirables = source_utils.get_undesirables()
			self.check_foreign_audio = source_utils.check_foreign_audio()
			from cocoscrapers.modules.Thread_pool import run_and_wait
			from functools import partial
			bound_get_sources = partial(self.get_sources)
			run_and_wait(bound_get_sources, links)
			logged = False
			for quality in self.item_totals:
				if self.item_totals[quality] > 0:
					log_utils.log('#STATS -TORRENTFUNK found {0:2.0f} {1}'.format(self.item_totals[quality],quality) )
					logged = True
			if not logged: log_utils.log('#STATS - TORRENTFUNK found nothing')
			endTime = time()
			log_utils.log('TORRENTFUNK took %0.1f seconds' % (endTime - startTime))
			return self.sources
		except:
			source_utils.scraper_error('TORRENTFUNK')
			return self.sources

	def get_sources(self, link):
		try:
			try: url = link[0].encode('ascii', errors='ignore').decode('ascii', errors='ignore').replace('&nbsp;', ' ')
			except: url = link[0].replace('&nbsp;', ' ')
			if '/torrent/' not in url: return

			try: name = link[1].encode('ascii', errors='ignore').decode('ascii', errors='ignore').replace('&nbsp;', '.')
			except: name = link[1].replace('&nbsp;', '.')
			if '<span' in name: name = name.split('<span')[0].rstrip(' [')
			name = source_utils.clean_name(name)

			if not source_utils.check_title(self.title, self.aliases, name, self.hdlr, self.year): return
			name_info = source_utils.info_from_name(name, self.title, self.year, self.hdlr, self.episode_title)
			if source_utils.remove_lang(name_info, self.check_foreign_audio): return
			if self.undesirables and source_utils.remove_undesirables(name_info, self.undesirables): return

			if not self.episode_title: #filter for eps returned in movie query (rare but movie and show exists for Run in 2020)
				ep_strings = [r'[.-]s\d{2}e\d{2}([.-]?)', r'[.-]s\d{2}([.-]?)', r'[.-]season[.-]?\d{1,2}[.-]?']
				name_lower = name.lower()
				if any(re.search(item, name_lower) for item in ep_strings): return

			if not url.startswith('http'): link = '%s%s' % (self.base_link, url)
			link = client.request(link, timeout=5)
			if link is None: return
			hash = re.search(r'Infohash.*?>(?!<)(.+?)</', link, re.I).group(1)
			url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)

			try:
				seeders = int(re.search(r'Swarm.+?>([0-9]+|[0-9]+,[0-9]+)</', link, re.I).group(1).replace(',', ''))
				if self.min_seeders > seeders: return
			except: seeders = 0

			quality, info = source_utils.get_release_quality(name_info, url)
			try:
				size = re.search(r'Size:.*?>((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', link).group(1)
				dsize, isize = source_utils._size(size)
				info.insert(0, isize)
			except: dsize = 0
			info = ' | '.join(info)

			self.sources_append({'provider': 'torrentfunk', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info,
												'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
			self.item_totals[quality] += 1
		except:
			source_utils.scraper_error('TORRENTFUNK')

	def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
		self.sources = []
		if not data: return self.sources
		self.sources_append = self.sources.append
		self.items = []
		self.items_append = self.items.append
		try:
			startTime = time()
			self.search_series = search_series
			self.total_seasons = total_seasons
			self.bypass_filter = bypass_filter

			self.title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
			self.aliases = data['aliases']
			self.imdb = data['imdb']
			self.year = data['year']
			self.season_x = data['season']
			self.season_xx = self.season_x.zfill(2)
			self.undesirables = source_utils.get_undesirables()
			self.check_foreign_audio = source_utils.check_foreign_audio()

			query = re.sub(r'[^A-Za-z0-9\s\.-]+', '', self.title)
			if search_series:
				queries = [
						self.tvsearch_link % quote_plus(query + ' Season'),
						self.tvsearch_link % quote_plus(query + ' Complete')]
			else:
				queries = [
						self.tvsearch_link % quote_plus(query + ' S%s' % self.season_xx),
						self.tvsearch_link % quote_plus(query + ' Season %s' % self.season_x)]
			from cocoscrapers.modules.Thread_pool import run_and_wait
			from functools import partial
			bound_get_pack_items = partial(self.get_pack_items)
			links = []
			for url in queries:
				links.append('%s%s' % (self.base_link, url))
			run_and_wait(bound_get_pack_items,links)
			bound_get_pack_sources = partial(self.get_pack_sources)
			run_and_wait(bound_get_pack_sources, self.items)
			logged = False
			for quality in self.item_totals:
				if self.item_totals[quality] > 0:
					log_utils.log('#STATS - TORRENTFUNK(pack) found {0:2.0f} {1}'.format(self.item_totals[quality],quality) )
					logged = True
			if not logged: log_utils.log('#STATS - TORRENTFUNK(pack) found nothing')
			endTime = time()
			log_utils.log('#STATS - TORRENTFUNK(pack) took %.2f seconds' % (endTime - startTime))
			return self.sources
		except:
			source_utils.scraper_error('TORRENTFUNK')
			return self.sources

	def get_pack_items(self, url):
		try:
			# log_utils.log('url = %s' % url)
			results = client.request(url, timeout=7)
			if not results: return
			table = client.parseDOM(results, 'table', attrs={'class': 'tmain'})[0]
			links = re.findall(r'<a\s*href\s*=\s*["\'](/torrent/.+?)["\']>(.+?)</a>', table, re.DOTALL | re.I)
		except:
			source_utils.scraper_error('TORRENTFUNK')
			return
		for link in links:
			try:
				try: url = link[0].encode('ascii', errors='ignore').decode('ascii', errors='ignore').replace('&nbsp;', ' ')
				except: url = link[0].replace('&nbsp;', ' ')
				if '/torrent/' not in url: continue

				try: name = link[1].encode('ascii', errors='ignore').decode('ascii', errors='ignore').replace('&nbsp;', '.')
				except: name = link[1].replace('&nbsp;', '.')
				if '<span' in name: name = name.split('<span')[0].rstrip(' [')
				name = source_utils.clean_name(name)

				self.episode_start, self.episode_end = 0, 0
				if not self.search_series:
					if not self.bypass_filter:
						valid, self.episode_start, self.episode_end = source_utils.filter_season_pack(self.title, self.aliases, self.year, self.season_x, name)
						if not valid: continue
					package = 'season'

				elif self.search_series:
					if not self.bypass_filter:
						valid, last_season = source_utils.filter_show_pack(self.title, self.aliases, self.imdb, self.year, self.season_x, name, self.total_seasons)
						if not valid: continue
					else: last_season = self.total_seasons
					package = 'show'

				name_info = source_utils.info_from_name(name, self.title, self.year, season=self.season_x, pack=package)
				if source_utils.remove_lang(name_info, self.check_foreign_audio): continue
				if self.undesirables and source_utils.remove_undesirables(name_info, self.undesirables): continue

				if not url.startswith('http'): url = '%s%s' % (self.base_link, url)
				if self.search_series: self.items.append((name, name_info, url, package, last_season))
				else: self.items_append((name, name_info, url, package))
			except:
				source_utils.scraper_error('TORRENTFUNK')

	def get_pack_sources(self, items):
		try:
			link = client.request(items[2], timeout=5)
			if link is None: return
			hash = re.search(r'Infohash.*?>(?!<)(.+?)</', link, re.I).group(1)

			url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, items[0])
			try:
				seeders = int(re.search(r'Swarm.+?>([0-9]+|[0-9]+,[0-9]+)</', link, re.I).group(1).replace(',', ''))
				if self.min_seeders > seeders: return
			except: seeders = 0

			quality, info = source_utils.get_release_quality(items[1], url)
			try:
				size = re.search(r'Size:.*?>((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', link).group(1)
				dsize, isize = source_utils._size(size)
				info.insert(0, isize)
			except: dsize = 0
			info = ' | '.join(info)

			item = {'provider': 'torrentfunk', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': items[0], 'name_info': items[1], 'quality': quality,
						'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize, 'package': items[3]}
			if self.search_series: item.update({'last_season': items[4]})
			elif self.episode_start: item.update({'episode_start': self.episode_start, 'episode_end': self.episode_end}) # for partial season packs
			self.sources_append(item)
			self.item_totals[quality] += 1
		except:
			source_utils.scraper_error('TORRENTFUNK')