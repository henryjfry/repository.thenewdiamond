# -*- coding: utf-8 -*-
# Thanks to kodifitzwell for allowing me to borrow his code
import time
from apis.torbox_api import TorBox, TorBoxAPI
from modules import source_utils
from modules.utils import clean_file_name, normalize
from modules.settings import enabled_debrids_check, filter_by_name
from caches.settings_cache import get_setting
# from modules.kodi_utils import logger

class source:
	def __init__(self):
		self.scrape_provider = 'tb_cloud'
		self.sources = []
		self.extensions = source_utils.supported_video_extensions()
		self._folder_fetch_count = 0
		self._max_folder_fetches = 10

	def results(self, info):
		self.sources = []
		try:
			if not enabled_debrids_check('tb'):
				return self.sources
			self.scrape_results = []
			filter_title = filter_by_name(self.scrape_provider)
			self.media_type, title = info.get('media_type'), info.get('title')
			self.year = int(info.get('year') or 0)
			self.season, self.episode = info.get('season'), info.get('episode')
			self.tmdb_id = info.get('tmdb_id')
			self.title = title
			self.folder_query = source_utils.clean_title(normalize(title))
			self.aliases = source_utils.get_aliases_titles(info.get('aliases', []))
			self.title_queries = self._title_queries()
			self.scrape_deadline = time.time() + min(25, max(10, int(get_setting('redlight.results.timeout', '20'))))
			for media_type in ('torrent', 'usenet', 'webdl'):
				if time.time() >= self.scrape_deadline:
					break
				items = self._cached_mylist_items(media_type)
				if items:
					self._scrape_cloud_list(media_type, items)
			def _process():
				for item in self.scrape_results:
					try:
						if not TorBoxAPI.is_scrapeable_cloud_file(item, self.extensions):
							continue
						file_name = TorBoxAPI._torrent_file_label(item)
						if not file_name:
							continue
						file_name_latin = normalize(file_name) or file_name
						if self.media_type == 'episode':
							if not source_utils.cloud_episode_matches(self.season, self.episode, file_name_latin):
								continue
							if filter_title and not source_utils.check_title(title, file_name_latin, self.aliases, self.year, 'pack', self.episode):
								continue
						elif filter_title and not source_utils.check_title(title, file_name_latin, self.aliases, self.year, self.season, self.episode):
							continue
						display_name = clean_file_name(file_name).replace('html', ' ').replace('+', ' ').replace('-', ' ')
						file_id = TorBoxAPI._torrent_file_id(item)
						if file_id is None:
							continue
						try:
							size_bytes = int(item.get('size') or 0)
						except Exception:
							size_bytes = 0
						size = round(size_bytes / 1073741824, 2) if size_bytes else 0.0
						size_label = '%.2f GB' % size if size_bytes else 'N/A'
						file_dl = '%d,%d' % (int(item['folder_id']), int(file_id))
						video_quality, details = source_utils.get_file_info(name_info=source_utils.release_info_format(file_name_latin))
						source_item = {
							'name': file_name, 'display_name': display_name, 'quality': video_quality, 'size': size,
							'size_label': size_label, 'debrid': self.scrape_provider, 'extraInfo': details,
							'url_dl': file_dl, 'id': file_dl, 'downloads': False, 'direct': True,
							'source': self.scrape_provider, 'scrape_provider': self.scrape_provider,
							'cloud_media_type': item.get('cloud_media_type', 'torrent'),
						}
						yield source_item
					except Exception:
						pass
			self.sources = list(_process())
		except Exception as e:
			from modules.kodi_utils import logger
			logger('torbox scraper Exception', str(e))
		finally:
			source_utils.internal_results(self.scrape_provider, self.sources)
		return self.sources

	def _cached_mylist_items(self, media_type):
		loaders = {
			'torrent': TorBox.user_cloud,
			'usenet': TorBox.user_cloud_usenet,
			'webdl': TorBox.user_cloud_webdl,
		}
		loader = loaders.get(media_type)
		if not loader:
			return []
		try:
			response = loader()
		except Exception:
			return []
		if not response or not isinstance(response, dict) or not response.get('success'):
			return []
		data = response.get('data') or []
		if isinstance(data, dict):
			data = [data]
		return data if isinstance(data, list) else []

	def _title_queries(self):
		queries = set()
		for candidate in [self.title] + list(self.aliases or []):
			if not candidate:
				continue
			for variant in (candidate, source_utils.normalize(candidate), normalize(candidate)):
				if not variant:
					continue
				query = source_utils.clean_title(variant)
				if query:
					queries.add(query)
		return queries

	def _contains_year(self, *texts):
		if not self.year:
			return False
		years = self._year_query_list()
		for text in texts:
			if not text:
				continue
			if any(str(y) in text for y in years):
				return True
		return False

	def _title_match(self, clean_file, folder_name):
		return any(q and (q in clean_file or (folder_name and q in folder_name)) for q in self.title_queries)

	def _prefilter_folder(self, folder_name, raw_folder):
		if not folder_name and not raw_folder:
			return False
		if self.media_type == 'movie':
			if not self.folder_query or self.folder_query not in folder_name:
				return False
			if self.year and not self._contains_year(raw_folder):
				return False
			return True
		if self.folder_query and self.folder_query in folder_name:
			return True
		if source_utils.seas_ep_filter_exact(self.season, self.episode, raw_folder):
			return True
		return self._title_match('', folder_name)

	def _match_cloud_file(self, normalized, folder_name='', raw_file='', raw_folder='', folder_prefiltered=False):
		if self.media_type == 'episode':
			return source_utils.cloud_episode_matches(self.season, self.episode, normalized)
		if folder_prefiltered:
			return True
		clean_file = source_utils.clean_title(normalized)
		return self._title_match(clean_file, folder_name) or self._contains_year(raw_file, raw_folder)

	def _files_for_folder(self, folder_id, media_type, item):
		inline = item.get('files')
		if inline is not None:
			if not inline or not TorBoxAPI.folder_has_playable_videos(inline, self.extensions):
				return []
			return [f for f in TorBoxAPI.filter_browse_cloud_files(inline, self.extensions) if TorBoxAPI.is_scrapeable_cloud_file(f, self.extensions)]
		if self._folder_fetch_count >= self._max_folder_fetches:
			return []
		if time.time() >= self.scrape_deadline - 3:
			return []
		self._folder_fetch_count += 1
		request_timeout = min(8, max(3, int(self.scrape_deadline - time.time()) - 1))
		raw = TorBox.mylist_item_files(
			folder_id, media_type, fresh=False, allow_live_fallback=True, request_timeout=request_timeout,
		) or []
		if not TorBoxAPI.folder_has_playable_videos(raw, self.extensions):
			return []
		return [f for f in TorBoxAPI.filter_browse_cloud_files(raw, self.extensions) if TorBoxAPI.is_scrapeable_cloud_file(f, self.extensions)]

	def _scrape_cloud_list(self, media_type, items):
		try:
			if time.time() >= self.scrape_deadline:
				return
			append = self.scrape_results.append
			for item in items:
				if time.time() >= self.scrape_deadline:
					return
				if not TorBoxAPI._torrent_item_finished(item):
					continue
				folder_id = item.get('id') or item.get('torrent_id')
				if folder_id is None:
					continue
				raw_folder = item.get('name') or ''
				folder_name = source_utils.clean_title(normalize(raw_folder))
				if not self._prefilter_folder(folder_name, raw_folder):
					continue
				files = self._files_for_folder(folder_id, media_type, item)
				if not files:
					continue
				folder_hits = []
				for file in files:
					if time.time() >= self.scrape_deadline:
						return
					label = TorBoxAPI._torrent_file_label(file)
					normalized = normalize(label) or label
					if not self._match_cloud_file(normalized, folder_name, label, raw_folder, True):
						continue
					file_id = TorBoxAPI._torrent_file_id(file)
					if file_id is None:
						continue
					file_entry = dict(file)
					file_entry['id'] = file_id
					file_entry['folder_id'] = folder_id
					file_entry['cloud_media_type'] = media_type
					folder_hits.append(file_entry)
				if not folder_hits:
					continue
				if self.media_type == 'movie':
					folder_hits.sort(key=lambda k: int(k.get('size') or 0), reverse=True)
					append(folder_hits[0])
				else:
					for file_entry in folder_hits:
						append(file_entry)
		except Exception:
			return

	def _year_query_list(self):
		if not self.year:
			return tuple()
		return (str(self.year), str(self.year + 1), str(self.year - 1))
