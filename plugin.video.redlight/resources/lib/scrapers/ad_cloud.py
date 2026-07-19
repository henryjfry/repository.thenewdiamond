# -*- coding: utf-8 -*-
from threading import Thread
from apis.alldebrid_api import AllDebridAPI
from modules import source_utils
from modules.utils import clean_file_name, normalize
from modules.settings import enabled_debrids_check, filter_by_name
# from modules.kodi_utils import logger

class source:
	def __init__(self):
		self.scrape_provider = 'ad_cloud'
		self.sources = []
		self.AllDebrid = AllDebridAPI()
		self.extensions = source_utils.supported_video_extensions()

	def results(self, info):
		try:
			if not enabled_debrids_check('ad'): return source_utils.internal_results(self.scrape_provider, self.sources)
			self.folder_results, self.scrape_results = [], []
			self.filter_title = filter_by_name(self.scrape_provider)
			self.media_type, title = info.get('media_type'), info.get('title')
			self.year, self.season, self.episode = int(info.get('year')), info.get('season'), info.get('episode')
			self.tmdb_id = info.get('tmdb_id')
			self.title = title
			self.folder_query = source_utils.clean_title(normalize(title))
			self.aliases = source_utils.get_aliases_titles(info.get('aliases', []))
			self._scrape_history()
			self._scrape_links()
			self._scrape_cloud()
			if not self.scrape_results: return source_utils.internal_results(self.scrape_provider, self.sources)
			def _process():
				for item in self.scrape_results:
					try:
						file_name = normalize(item['n'])
						if self.filter_title and not source_utils.check_title(title, file_name, self.aliases, self.year, self.season, self.episode): continue
						display_name = clean_file_name(file_name).replace('html', ' ').replace('+', ' ').replace('-', ' ')
						direct_debrid_link = item.get('direct_debrid_link', False)
						file_dl, size = item['l'], round(float(int(item['s']))/1073741824, 2)
						video_quality, details = source_utils.get_file_info(name_info=source_utils.release_info_format(file_name))
						source_item = {'name': file_name, 'display_name': display_name, 'quality': video_quality, 'size': size, 'size_label': '%.2f GB' % size,
									'extraInfo': details, 'url_dl': file_dl, 'id': file_dl, 'downloads': False, 'direct': True, 'source': self.scrape_provider,
									'debrid': self.scrape_provider, 'scrape_provider': self.scrape_provider, 'direct_debrid_link': direct_debrid_link}
						yield source_item
					except: pass
			self.sources = list(_process())
		except Exception as e:
			from modules.kodi_utils import logger
			logger('alldebrid scraper Exception', str(e))
		source_utils.internal_results(self.scrape_provider, self.sources)
		return self.sources

	def _dedupe_key(self, name):
		return name.replace('/', '').lower()

	def _already_scraped(self, name):
		key = self._dedupe_key(name)
		return key in {self._dedupe_key(d['n']) for d in self.scrape_results}

	def _append_scrape_result(self, item):
		if not item.get('l') or self._already_scraped(item.get('n', '')): return
		self.scrape_results.append(item)

	def _folder_matches(self, folder_name):
		if not folder_name: return True
		if not self.filter_title: return True
		return source_utils.check_title(self.title, folder_name, self.aliases, self.year, self.season, self.episode)

	def _file_matches(self, filename):
		if self.media_type == 'movie':
			if not any(x in normalize(filename) for x in self._year_query_list()): return False
		elif self.media_type == 'episode' and not source_utils.seas_ep_filter(self.season, self.episode, filename):
			return False
		if not self.filter_title: return True
		return source_utils.check_title(self.title, filename, self.aliases, self.year, self.season, self.episode)

	def _scrape_history(self):
		try:
			history = self.AllDebrid.history()
			my_history = history.get('links', []) or []
			my_history = [i for i in my_history if not i.get('error')]
			my_history = [i for i in my_history if i['filename'].lower().endswith(tuple(self.extensions))]
			for item in my_history:
				filename = item['filename']
				if not self._file_matches(filename): continue
				self._append_scrape_result({
					'l': item.get('link_dl') or item.get('link'),
					's': item['size'],
					'n': filename,
					'direct_debrid_link': bool(item.get('link_dl')),
				})
		except: pass

	def _scrape_links(self):
		try:
			links = self.AllDebrid.user_links()
			my_links = links.get('links', []) or []
			my_links = [i for i in my_links if i['filename'].lower().endswith(tuple(self.extensions))]
			for item in my_links:
				filename = item['filename']
				if not self._file_matches(filename): continue
				self._append_scrape_result({'l': item['link'], 's': item['size'], 'n': filename})
		except: pass

	def _scrape_cloud(self):
		try:
			try:
				my_cloud_files = self.AllDebrid.user_cloud()['magnets']
				my_cloud_files = [i for i in my_cloud_files if i['statusCode'] == 4]
			except: return self.sources
			threads = []
			append = threads.append
			for item in my_cloud_files:
				folder_name = item.get('filename') or ''
				if not self._folder_matches(folder_name): continue
				if self.media_type == 'movie' and self.filter_title:
					normalized = normalize(folder_name)
					if normalized and not any(x in normalized for x in self._year_query_list()): continue
				folder_id = item.get('id')
				if folder_id: self.folder_results.append(folder_id)
			if not self.folder_results: return self.sources
			for folder_id in self.folder_results:
				append(Thread(target=self._scrape_folders, args=(folder_id,)))
			[i.start() for i in threads]
			[i.join() for i in threads]
		except: pass

	def _scrape_folders(self, folder_id):
		try:
			if isinstance(folder_id, dict):
				folder_id = folder_id.get('id')
			if not folder_id: return
			links = self.AllDebrid.cloud_file_links(folder_id)
			links = [i for i in links if i.get('n', '').lower().endswith(tuple(self.extensions)) and i.get('l')]
			for item in links:
				if self.media_type == 'episode' and not source_utils.seas_ep_filter(self.season, self.episode, item['n']): continue
				if self.filter_title and not source_utils.check_title(self.title, item['n'], self.aliases, self.year, self.season, self.episode): continue
				self._append_scrape_result(item)
		except: return

	def _year_query_list(self):
		return (str(self.year), str(self.year+1), str(self.year-1))
