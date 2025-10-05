# created by kodifitzwell for Fenomscrapers
"""
	Fenomscrapers Project
"""

#from json import loads as jsloads
import hashlib, requests, queue
#from magneto.modules import client
from magneto.modules import source_utils
from magneto.modules.control import setting as getSetting



class source:
	timeout = 10
	priority = 1
	pack_capable = True
	hasMovies = True
	hasEpisodes = True
	_queue = queue.SimpleQueue()
	def __init__(self):
		self.token = getSetting('prowlarr.token')
		self.language = ['en']
		self.headers = {'user-agent': 'Magneto for Kodi', 'x-api-key': self.token}
		self.base_link = getSetting('prowlarr.url')
		self.movieSearch_link = '/api/v1/search'
		self.tvSearch_link = '/api/v1/search'
		self.min_seeders = 0

	def sources(self, data, hostDict):
		sources = []
		if not data or self.token: return sources
		append = sources.append
		try:
			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ')
			aliases = data['aliases']
			episode_title = data['title'] if 'tvshowtitle' in data else None
			year = data['year']
			imdb = data['imdb']
			if 'tvshowtitle' in data:
				season = data['season']
				episode = data['episode']
				hdlr = 'S%02dE%02d' % (int(season), int(episode))
				url = '%s%s' % (self.base_link, self.tvSearch_link)
				params = {'type': 'search', 'limit': 100, 'categories': 5000, 'query': '%s %s' % (title.lower(), hdlr)}
			else:
				hdlr = year
				url = '%s%s' % (self.base_link, self.movieSearch_link)
				params = {'type': 'search', 'limit': 100, 'categories': 2000, 'query': title.lower()}
			try:
				results = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
				files = results.json()
			except: files = []
			self._queue.put_nowait(files) # if seasons
			self._queue.put_nowait(files) # if shows
		except:
			source_utils.scraper_error('PROWLARR')
			return sources

		for file in files:
			try:
				name = source_utils.clean_name(file['title'])
				if not source_utils.check_title(title, aliases, name.replace('.(Archie.Bunker', ''), hdlr, year): continue
				name_info = source_utils.info_from_name(name, title, year, hdlr, episode_title)

				if file['protocol'] == 'usenet':
					url = file['downloadUrl']
					file['infoHash'] = hashlib.md5(file['fileName'].encode()).hexdigest()
					file['seeders'] = file['age']
				else: url = 'magnet:?xt=urn:btih:%s&dn=%s' % (file['infoHash'], name)

				try:
					seeders = int(file['seeders'])
					if self.min_seeders > seeders: continue
				except: seeders = 0

				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					size = f"{float(file['size']) / 1073741824:.2f} GB"
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				append({'provider': file['indexer'], 'source': file['protocol'], 'seeders': seeders, 'hash': file['infoHash'], 'name': name, 'name_info': name_info,
							'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
			except:
				source_utils.scraper_error('PROWLARR')
		return sources

	def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
		sources = []
		if not data or not self.token: return sources
		sources_append = sources.append
		try:
			title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ')
			aliases = data['aliases']
			imdb = data['imdb']
			year = data['year']
			season = data['season']
			url = '%s%s' % (self.base_link, self.tvSearch_link)
			files = self._queue.get(timeout=self.timeout + 1)
		except:
			source_utils.scraper_error('PROWLARR')
			return sources

		for file in files:
			try:
				name = source_utils.clean_name(file['title'])

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
				if file['protocol'] == 'usenet':
					url = file['downloadUrl']
					file['infoHash'] = hashlib.md5(file['fileName'].encode()).hexdigest()
					file['seeders'] = file['age']
				else: url = 'magnet:?xt=urn:btih:%s&dn=%s' % (file['infoHash'], name)

				try:
					seeders = int(file['seeders'])
					if self.min_seeders > seeders: continue
				except: seeders = 0

				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					size = f"{float(file['size']) / 1073741824:.2f} GB"
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				item = {'provider': file['indexer'], 'source': file['protocol'], 'seeders': seeders, 'hash': file['infoHash'], 'name': name, 'name_info': name_info,
							'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize, 'package': package}
				if search_series: item.update({'last_season': last_season})
				elif episode_start: item.update({'episode_start': episode_start, 'episode_end': episode_end}) # for partial season packs
				sources_append(item)
			except:
				source_utils.scraper_error('PROWLARR')
		return sources
