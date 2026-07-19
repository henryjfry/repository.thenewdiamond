# -*- coding: utf-8 -*-
import time
from apis.premiumize_api import Premiumize
from modules import source_utils
from modules.utils import clean_file_name, normalize
from modules.settings import enabled_debrids_check, filter_by_name
from caches.settings_cache import get_setting
# from modules.kodi_utils import logger

class source:
	def __init__(self):
		self.scrape_provider = 'pm_cloud'
		self.sources, self.scrape_results = [], []
		self.extensions = source_utils.supported_video_extensions()
		self._folder_queue = []
		self._folders_scanned = 0
		self._max_folder_scans = 24
		self._listall_reserve_seconds = 8

	def results(self, info):
		try:
			if not enabled_debrids_check('pm'): return source_utils.internal_results(self.scrape_provider, self.sources)
			self.filter_title = filter_by_name(self.scrape_provider)
			self.media_type, title = info.get('media_type'), info.get('title')
			try: self.year = int(info.get('year') or 0)
			except: self.year = 0
			self.season, self.episode = info.get('season'), info.get('episode')
			self.folder_query = source_utils.clean_title(normalize(title))
			self.aliases = source_utils.get_aliases_titles(info.get('aliases', []))
			self.title_queries = self._title_queries()
			self.scrape_deadline = time.time() + min(25, max(10, int(get_setting('redlight.results.timeout', '20'))))
			self._scrape_cloud()
			def _process():
				for item in self.scrape_results:
					try:
						file_name = self._item_label(item)
						if self.media_type == 'episode':
							file_only = normalize(item.get('name') or '')
							if not source_utils.cloud_episode_matches(self.season, self.episode, file_only): continue
							if self.filter_title and not source_utils.check_title(title, file_name, self.aliases, self.year, 'pack', self.episode): continue
						elif self.filter_title and not source_utils.check_title(title, file_name, self.aliases, self.year, self.season, self.episode): continue
						display_name = clean_file_name(normalize(item.get('name') or file_name)).replace('html', ' ').replace('+', ' ').replace('-', ' ')
						file_dl = item['id']
						size = round(float(item.get('size') or 0)/1073741824, 2)
						video_quality, details = source_utils.get_file_info(name_info=source_utils.release_info_format(file_name))
						source_item = {'name': file_name, 'display_name': display_name, 'quality': video_quality, 'size': size, 'size_label': '%.2f GB' % size,
									'debrid': self.scrape_provider, 'extraInfo': details, 'url_dl': file_dl, 'id': file_dl, 'downloads': False, 'direct': True,
									'source': self.scrape_provider, 'scrape_provider': self.scrape_provider}
						yield source_item
					except: pass
			self.sources = list(_process())
		except Exception as e:
			from modules.kodi_utils import logger
			logger('premiumize scraper Exception', str(e))
		source_utils.internal_results(self.scrape_provider, self.sources)
		return self.sources

	def _title_queries(self):
		queries = set()
		if self.folder_query: queries.add(self.folder_query)
		for candidate in list(self.aliases or []):
			if not candidate: continue
			query = source_utils.clean_title(normalize(candidate))
			if query: queries.add(query)
		return queries

	def _item_label(self, item):
		path, name = (item.get('path') or '').strip(), (item.get('name') or '').strip()
		if path and name and not path.rstrip('/').endswith(name):
			return normalize('%s %s' % (path.replace('/', ' '), name))
		return normalize(path or name)

	def _list_folder(self, folder_id):
		"""Folder/list during scrape; bounded timeout so one slow call cannot eat the whole search."""
		if time.time() > self.scrape_deadline - 3:
			return []
		try:
			url = 'folder/list?id=%s' % folder_id if folder_id else 'folder/list'
			try:
				response = Premiumize._get(url, timeout=10)
			except TypeError:
				response = Premiumize._get(url)
			if not isinstance(response, dict) or str(response.get('status', '')).lower() != 'success':
				return []
			return response.get('content') or []
		except: return []

	def _is_video_file(self, item):
		link = (item.get('link') or '').lower()
		if link and link.endswith(tuple(self.extensions)): return True
		name = (item.get('name') or '').lower()
		return name.endswith(tuple(self.extensions))

	def _matches_title(self, label):
		if not self.title_queries: return True
		folder_name = source_utils.clean_title(label)
		return any(q in folder_name for q in self.title_queries)

	def _has_media_hint(self, label):
		if self.media_type == 'movie':
			return bool(self.year and str(self.year) in label)
		return source_utils.seas_ep_filter_exact(self.season, self.episode, label)

	def _should_enter_folder(self, name, path, depth):
		if time.time() > self.scrape_deadline: return False
		label = normalize('%s %s' % (path, name))
		# Root and one level down (e.g. "My Files") — always open so titled folders are reachable.
		if depth < 2: return True
		if self._matches_title(label) or self._has_media_hint(label): return True
		if not self.filter_title and self._has_media_hint(label): return True
		return False

	def _file_passes(self, label, filename=None):
		if self.filter_title and not self._matches_title(label): return False
		if self.media_type == 'movie':
			if self.year and not any(x in label for x in self._year_query_list()): return False
		elif not source_utils.cloud_episode_matches(self.season, self.episode, normalize(filename or label)): return False
		return True

	def _scrape_cloud(self):
		self._folder_queue = [(None, '', 0)]
		self._folders_scanned = 0
		walk_deadline = self.scrape_deadline - self._listall_reserve_seconds
		while self._folder_queue and time.time() < walk_deadline and self._folders_scanned < self._max_folder_scans:
			folder_id, path_prefix, depth = self._folder_queue.pop(0)
			self._scan_folder(folder_id, path_prefix, depth)
		if not self.scrape_results and time.time() < self.scrape_deadline:
			self._scrape_cloud_listall()

	def _scan_folder(self, folder_id, path_prefix, depth):
		self._folders_scanned += 1
		try:
			content = self._list_folder(folder_id)
		except: return
		append_result = self.scrape_results.append
		for item in content:
			if time.time() > self.scrape_deadline: return
			if not isinstance(item, dict): continue
			name = (item.get('name') or '').strip()
			if not name: continue
			child_path = '%s/%s' % (path_prefix, name) if path_prefix else name
			if item.get('type') == 'folder':
				if self._should_enter_folder(name, child_path, depth):
					self._folder_queue.append((item.get('id'), child_path, depth + 1))
				continue
			if not self._is_video_file(item): continue
			file_item = {'id': item.get('id'), 'name': name, 'size': item.get('size') or 0, 'path': child_path}
			label = self._item_label(file_item)
			if not self._file_passes(label, name): continue
			append_result(file_item)

	def _scrape_cloud_listall(self):
		"""Fallback when folder walk finds nothing (flat API)."""
		if time.time() > self.scrape_deadline - 2:
			return
		try:
			try:
				response = Premiumize.user_cloud_all(timeout=12)
			except TypeError:
				response = Premiumize.user_cloud_all()
			if not isinstance(response, dict) or str(response.get('status', '')).lower() != 'success':
				return
			cloud_files = response.get('files') or []
			cloud_files = [i for i in cloud_files if isinstance(i, dict) and self._is_video_file(i)]
		except: return
		append = self.scrape_results.append
		for item in cloud_files:
			if time.time() > self.scrape_deadline: break
			label = self._item_label(item)
			if not self._file_passes(label, item.get('name')): continue
			append(item)

	def _year_query_list(self):
		if not self.year: return ()
		return (str(self.year), str(self.year + 1), str(self.year - 1))
