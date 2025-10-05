# -*- coding: utf-8 -*-
# created by Venom for Fenomscrapers (updated 6-19-2022)
"""
	Fenomscrapers Project
"""

import re
from urllib.parse import quote_plus, unquote_plus
from cocoscrapers.modules import client
from cocoscrapers.modules import source_utils
from cocoscrapers.modules import log_utils
from time import time
SERVER_ERROR = ('something went wrong', 'Connection timed out', '521: Web server is down', '503 Service Unavailable')


class source:
	priority = 3
	pack_capable = True
	hasMovies = True
	hasEpisodes = True
	def __init__(self):
		self.language = ['en']
		self.base_link = "https://bitcq.com"
		self.search_link = "/search?q=%s&category[]=1"
		self.item_totals = {
			'4K': 0,
			'1080p': 0,
			'720p': 0,
			'SD': 0,
			'CAM': 0 
			}
		self.min_seeders = 0

	def sources(self, data, hostDict):
		sources = []
		if not data: return sources
		sources_append = sources.append
		try:
			startTime = time()
			aliases = data['aliases']
			year = data['year']
			if 'tvshowtitle' in data:
				title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
				episode_title = data['title']
				hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode']))
			else:
				title = data['title'].replace('&', 'and').replace('/', ' ').replace('$', 's')
				episode_title = None
				hdlr = year
			query = '%s %s' % (re.sub(r'[^A-Za-z0-9\s\.-]+', '', title), hdlr)
			url = '%s%s' % (self.base_link, self.search_link % quote_plus(query))
			# log_utils.log('url = %s' % url)
			results = client.request(url, timeout=7)
			if not results or any(value in str(results) for value in SERVER_ERROR): return sources
			rows = client.parseDOM(results, 'tr')
			undesirables = source_utils.get_undesirables()
			check_foreign_audio = source_utils.check_foreign_audio()
		except:
			source_utils.scraper_error('BITCQ')
			return sources

		for row in rows:
			try:
				if 'magnet:' not in row: continue
				columns = re.findall(r'<td.*?>(.+?)</td>', row, re.DOTALL)

				url = unquote_plus(columns[0]).replace('&amp;', '&')
				try: url = re.search(r'(magnet:.+?)&tr=', url, re.I).group(1).replace(' ', '.')
				except: continue
				hash = re.search(r'btih:(.*?)&', url, re.I).group(1)
				name = source_utils.clean_name(url.split('&dn=')[1])

				if not source_utils.check_title(title, aliases, name, hdlr, year): continue
				name_info = source_utils.info_from_name(name, title, year, hdlr, episode_title)
				if source_utils.remove_lang(name_info, check_foreign_audio): continue
				if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

				if not episode_title: # filter for eps returned in movie query (rare but movie and show exists for Run in 2020)
					ep_strings = [r'(?:\.|\-)s\d{2}e\d{2}(?:\.|\-|$)', r'(?:\.|\-)s\d{2}(?:\.|\-|$)', r'(?:\.|\-)season(?:\.|\-)\d{1,2}(?:\.|\-|$)']
					name_lower = name.lower()
					if any(re.search(item, name_lower) for item in ep_strings): continue

				try:
					seeders = int(columns[4].replace(',', ''))
					if self.min_seeders > seeders: continue
				except: seeders = 0

				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					dsize, isize = source_utils._size(columns[3])
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				sources_append({'provider': 'bitcq', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info,
											'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
				self.item_totals[quality]+=1
			except:
				source_utils.scraper_error('BITCQ')
		logged = False
		for quality in self.item_totals:
			if self.item_totals[quality] > 0:
				log_utils.log('#STATS - BITCQ found {0:2.0f} {1}'.format(self.item_totals[quality],quality) )
				logged = True
		if not logged: log_utils.log('#STATS - BITCQ found nothing')
		endTime = time()
		log_utils.log('#STATS - BITCQ took %.2f seconds' % (endTime - startTime))
		return sources

	def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
		self.sources = []
		if not data: return self.sources
		self.sources_append = self.sources.append
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
			queries = [
						self.search_link % quote_plus(query + ' S%s' % self.season_xx),
						self.search_link % quote_plus(query + ' Season %s' % self.season_x)]
			if search_series:
				queries = [
						self.search_link % quote_plus(query + ' Season'),
						self.search_link % quote_plus(query + ' Complete')]
			from cocoscrapers.modules.Thread_pool import run_and_wait
			from functools import partial
			bound_get_sources_packs = partial(self.get_sources_packs)
			links = []
			for url in queries:
				links.append('%s%s' % (self.base_link, url))
			run_and_wait(bound_get_sources_packs, links)
			logged = False
			for quality in self.item_totals:
				if self.item_totals[quality] > 0:
					log_utils.log('#STATS - BITCQ(pack) found {0:2.0f} {1}'.format(self.item_totals[quality],quality) )
					logged = True
			if not logged: log_utils.log('#STATS - BITCQ(pack) found nothing')
			endTime = time()
			log_utils.log('#STATS - BITCQ(pack) took %.2f seconds' % (endTime - startTime))
			return self.sources
		except:
			source_utils.scraper_error('BITCQ')
			return self.sources

	def get_sources_packs(self, link):
		try:
			results = client.request(link, timeout=7)
			if not results or any(value in str(results) for value in SERVER_ERROR): return
			rows = client.parseDOM(results, 'tr')
		except:
			source_utils.scraper_error('BITCQ')
			return
		for row in rows:
			try:
				if 'magnet:' not in row: continue
				columns = re.findall(r'<td.*?>(.+?)</td>', row, re.DOTALL)

				url = unquote_plus(columns[0]).replace('&amp;', '&')
				try: url = re.search(r'(magnet:.+?)&tr=', url, re.I).group(1).replace(' ', '.')
				except: continue
				hash = re.search(r'btih:(.*?)&', url, re.I).group(1)
				name = source_utils.clean_name(url.split('&dn=')[1])

				episode_start, episode_end = 0, 0
				if not self.search_series:
					if not self.bypass_filter:
						valid, episode_start, episode_end = source_utils.filter_season_pack(self.title, self.aliases, self.year, self.season_x, name)
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

				try:
					seeders = int(columns[4].replace(',', ''))
					if self.min_seeders > seeders: continue
				except: seeders = 0

				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					dsize, isize = source_utils._size(columns[3])
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				item = {'provider': 'bitcq', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
							'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize, 'package': package}
				if self.search_series: item.update({'last_season': last_season})
				elif episode_start: item.update({'episode_start': episode_start, 'episode_end': episode_end}) # for partial season packs
				self.sources_append(item)
				self.item_totals[quality]+=1
			except:
				source_utils.scraper_error('BITCQ')