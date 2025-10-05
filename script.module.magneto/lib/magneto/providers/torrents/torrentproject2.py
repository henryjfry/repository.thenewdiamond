# created by Venom for Fenomscrapers
"""
	Fenomscrapers Project
"""

import re
from urllib.parse import quote_plus, unquote_plus
from magneto.modules import client
from magneto.modules import source_utils
from magneto.modules import workers
_LINKS = re.compile(r'<a\s*href\s*=\s*["\'](.+?torrent.html)["\']', re.I)


class source:
	priority = 6
	pack_capable = True
	hasMovies = True
	hasEpisodes = True
	def __init__(self):
		self.language = ['en']
		self.base_link = "https://torrentproject2.com"
		self.search_link = '/?t=%s&orderby=seeders'
		self.min_seeders = 1

	def sources(self, data, hostDict):
		self.sources = []
		if not data: return self.sources
		self.sources_append = self.sources.append
		try:
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
			self.undesirables = source_utils.get_undesirables()
			self.check_foreign_audio = source_utils.check_foreign_audio()

			query = '%s %s' % (re.sub(r'[^A-Za-z0-9\s\.-]+', '', self.title), self.hdlr)
			url = '%s%s' % (self.base_link, self.search_link % quote_plus(query))
			# log_utils.log('url = %s' % url)

			results = client.request(url, timeout=5)
			if not results: return self.sources
			links = _LINKS.findall(results)
			threads = []
			append = threads.append
			for link in links:
				append(workers.Thread(self.get_sources, link))
			[i.start() for i in threads]
			[i.join() for i in threads]
			return self.sources
		except:
			source_utils.scraper_error('TORRENTPROJECT2')
			return self.sources

	def get_sources(self, link):
		try:
			url = '%s%s' % (self.base_link, link)
			result = client.request(url, timeout=5)
			if not result: return
			hash = re.search(r'<a\s*title\s*=\s*["\']hash:(.+?)\s*torrent', result, re.I).group(1)
			name = re.search(r'<title>(.+?)</title>', result, re.I).group(1)
			name = source_utils.clean_name(unquote_plus(name))

			if not source_utils.check_title(self.title, self.aliases, name, self.hdlr, self.year): return
			name_info = source_utils.info_from_name(name, self.title, self.year, self.hdlr, self.episode_title)
			if source_utils.remove_lang(name_info, self.check_foreign_audio): return
			if self.undesirables and source_utils.remove_undesirables(name_info, self.undesirables): return

			if not self.episode_title: #filter for eps returned in movie query (rare but movie and show exists for Run in 2020)
				ep_strings = [r'[.-]s\d{2}e\d{2}([.-]?)', r'[.-]s\d{2}([.-]?)', r'[.-]season[.-]?\d{1,2}[.-]?']
				name_lower = name.lower()
				if any(re.search(item, name_lower) for item in ep_strings): return

			url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)
			try:
				seeders = int(re.search(r'["\']tseeders["\']>\s*([0-9]+|[0-9]+,[0-9]+)\s*<', result, re.I).group(1).replace(',', ''))
				if self.min_seeders > seeders: return
			except: seeders = 0

			quality, info = source_utils.get_release_quality(name_info, url)
			try:
				size = re.search(r'<div id\s*=\s*["\']torrent-size["\']>(.+?)<', result, re.I).group(1)
				dsize, isize = source_utils._size(size)
				info.insert(0, isize)
			except: dsize = 0
			info = ' | '.join(info)

			self.sources_append({'provider': 'torrentproject2', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info,
											'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
		except:
			source_utils.scraper_error('TORRENTPROJECT2')

	def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
		self.sources = []
		if not data: return self.sources
		self.sources_append = self.sources.append
		self.items = []
		self.items_append = self.items.append
		try:
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
						self.search_link % quote_plus(query + ' Season'),
						self.search_link % quote_plus(query + ' Complete')]
			else:
				queries = [
						self.search_link % quote_plus(query + ' S%s' % self.season_xx),
						self.search_link % quote_plus(query + ' Season %s' % self.season_x)]
			threads = []
			append = threads.append
			for url in queries:
				link = '%s%s' % (self.base_link, url)
				append(workers.Thread(self.get_pack_items, link))
			[i.start() for i in threads]
			[i.join() for i in threads]

			threads2 = []
			append2 = threads2.append
			for i in self.items:
				append2(workers.Thread(self.get_pack_sources, i))
			[i.start() for i in threads2]
			[i.join() for i in threads2]
			return self.sources
		except:
			source_utils.scraper_error('TORRENTPROJECT2')
			return self.sources

	def get_pack_items(self, url):
		try:
			results = client.request(url, timeout=5)
			if not results: return
			links = _LINKS.findall(results)
			for link in links:
				url = '%s%s' % (self.base_link, link)
				self.items_append((url))
			return self.items
		except:
			source_utils.scraper_error('TORRENTPROJECT2')

	def get_pack_sources(self, url):
		try:
			result = client.request(url, timeout=5)
			if not result: return
			hash = re.search(r'<a\s*title\s*=\s*["\']hash:(.+?)\s*torrent', result, re.I).group(1)
			name = re.search(r'<title>(.+?)</title>', result, re.I).group(1)
			name = source_utils.clean_name(unquote_plus(name))

			episode_start, episode_end = 0, 0
			if not self.search_series:
				if not self.bypass_filter:
					valid, episode_start, episode_end = source_utils.filter_season_pack(self.title, self.aliases, self.year, self.season_x, name)
					if not valid: return
				package = 'season'

			elif self.search_series:
				if not self.bypass_filter:
					valid, last_season = source_utils.filter_show_pack(self.title, self.aliases, self.imdb, self.year, self.season_x, name, self.total_seasons)
					if not valid: return
				else: last_season = self.total_seasons
				package = 'show'

			name_info = source_utils.info_from_name(name, self.title, self.year, season=self.season_x, pack=package)
			if source_utils.remove_lang(name_info, self.check_foreign_audio): return
			if self.undesirables and source_utils.remove_undesirables(name_info, self.undesirables): return

			url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)
			try:
				seeders = int(re.search(r'["\']tseeders["\']>\s*([0-9]+|[0-9]+,[0-9]+)\s*<', result, re.I).group(1).replace(',', ''))
				if self.min_seeders > seeders: return
			except: seeders = 0

			quality, info = source_utils.get_release_quality(name_info, url)
			try:
				size = re.search(r'<div id\s*=\s*["\']torrent-size["\']>(.+?)<', result, re.I).group(1)
				dsize, isize = source_utils._size(size)
				info.insert(0, isize)
			except: dsize = 0
			info = ' | '.join(info)

			item = {'provider': 'torrentproject2', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'name_info': name_info, 'quality': quality,
						'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize, 'package': package}
			if self.search_series: item.update({'last_season': last_season})
			elif episode_start: item.update({'episode_start': episode_start, 'episode_end': episode_end}) # for partial season packs
			self.sources_append(item)
		except:
			source_utils.scraper_error('TORRENTPROJECT2')
