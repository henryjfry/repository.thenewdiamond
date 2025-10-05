# -*- coding: utf-8 -*-
# created by Venom for Fenomscrapers (updated 7-19-2022)
"""
	Fenomscrapers Project
"""

import re
from urllib.parse import quote_plus, unquote_plus
from cocoscrapers.modules import client
from cocoscrapers.modules import source_utils
from cocoscrapers.modules import workers
from cocoscrapers.modules import log_utils
from time import time

_DATA = re.compile(r'<a\s*href\s*=\s*["\'](/torrent_details/.+?)["\']><span>(.+?)</span>.*?<td\s*class\s*=\s*["\']size-row["\']>(.+?)</td><td\s*class\s*=\s*["\']sn["\']>([0-9]+)</td>', re.I)


class source:
	priority = 7
	pack_capable = False
	hasMovies = True
	hasEpisodes = True
	def __init__(self):
		self.language = ['en']
		self.base_link = "https://isohunt.nz"
		self.search_link = '/torrent/?ihq=%s&fiht=2&age=0&Torrent_sort=seeders&Torrent_page=0'
		self.item_totals = {
			'4K': 0,
			'1080p': 0,
			'720p': 0,
			'SD': 0,
			'CAM': 0 
			}
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
			else:
				self.title = data['title'].replace('&', 'and').replace('/', ' ').replace('$', 's')
				self.episode_title = None
				self.hdlr = self.year
			query = '%s %s' % (re.sub(r'[^A-Za-z0-9\s\.-]+', '', self.title), self.hdlr)
			url = '%s%s' % (self.base_link, self.search_link % quote_plus(query))
			# log_utils.log('url = %s' % url)
			results = client.request(url, timeout=5)
			if not results or '<tbody' not in results: return
			rows = client.parseDOM(results, 'tr', attrs={'data-key': '0'})
			self.undesirables = source_utils.get_undesirables()
			self.check_foreign_audio = source_utils.check_foreign_audio()
			from cocoscrapers.modules.Thread_pool import run_and_wait
			from functools import partial
			bound_get_sources = partial(self.get_sources)
			run_and_wait(bound_get_sources, rows)
			logged = False
			for quality in self.item_totals:
				if self.item_totals[quality] > 0 and not logged:
					logged = True
					log_utils.log('#STATS - ISOHUNT2 found {0:2.0f} {1}'.format(self.item_totals[quality],quality) )
			if not logged: log_utils.log('#STATS - ISOHUNT2 found nothing')
			endTime = time()
			log_utils.log('#STATS - ISOHUNT2 took %.2f seconds' % (endTime - startTime))
			return self.sources
		except:
			source_utils.scraper_error('ISOHUNT2')
			return self.sources

	def get_sources(self, row):
		row = re.sub(r'[\n\t]', '', row)
		data = _DATA.findall(row)
		if not data: return
		for items in data:
			try:
				# item[1] does not contain full info like the &dn= portion of magnet
				link = '%s%s' % (self.base_link, items[0])
				result = client.request(link, timeout=5)
				if not result: continue
				try: url =unquote_plus(re.search(r'(magnet.*?)["\']', result).group(1)).replace('&amp;', '&').split('&tr')[0].replace(' ', '.')
				except: continue
				url = unquote_plus(url) # many links dbl quoted so we must unquote again
				hash = re.search(r'btih:(.*?)&', url, re.I).group(1)
				name = source_utils.clean_name(url.split('&dn=')[1])

				if not source_utils.check_title(self.title, self.aliases, name, self.hdlr, self.year): continue
				name_info = source_utils.info_from_name(name, self.title, self.year, self.hdlr, self.episode_title)
				if source_utils.remove_lang(name_info, self.check_foreign_audio): continue
				if self.undesirables and source_utils.remove_undesirables(name_info, self.undesirables): continue

				if not self.episode_title: #filter for eps returned in movie query (rare but movie and show exists for Run in 2020)
					ep_strings = [r'[.-]s\d{2}e\d{2}([.-]?)', r'[.-]s\d{2}([.-]?)', r'[.-]season[.-]?\d{1,2}[.-]?']
					name_lower = name.lower()
					if any(re.search(item, name_lower) for item in ep_strings): continue

				try:
					seeders = int(items[3].replace(',', ''))
					if self.min_seeders > seeders: continue
				except: seeders = 0

				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					dsize, isize = source_utils._size(items[2])
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				self.sources_append({'provider': 'isohunt2', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info,
													'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
				self.item_totals[quality]+=1
			except:
				source_utils.scraper_error('ISOHUNT2')