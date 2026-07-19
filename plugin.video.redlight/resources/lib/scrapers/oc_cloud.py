# -*- coding: utf-8 -*-
# Thanks to kodifitzwell for allowing me to borrow his code
from threading import Thread
from apis.offcloud_api import Offcloud
from modules import source_utils
from modules.utils import clean_file_name, normalize
from modules.settings import enabled_debrids_check, filter_by_name
# from modules.kodi_utils import logger

class source:
	def __init__(self):
		self.scrape_provider = 'oc_cloud'
		self.sources = []
		self.extensions = source_utils.supported_video_extensions()

	def results(self, info):
		try:
			if not enabled_debrids_check('oc'): return source_utils.internal_results(self.scrape_provider, self.sources)
			self.folder_results, self.scrape_results = [], []
			filter_title = filter_by_name(self.scrape_provider)
			self.media_type, title = info.get('media_type'), info.get('title')
			self.year, self.season, self.episode = int(info.get('year') or 0), info.get('season'), info.get('episode')
			self.title = title
			self.folder_query = source_utils.clean_title(normalize(title))
			self.year_query_list = tuple(map(str, range(self.year - 1, self.year + 2)))
			self.aliases = source_utils.get_aliases_titles(info.get('aliases', []))
			self.title_queries = self._title_queries()
			self._scrape_cloud()
			if not self.scrape_results: return source_utils.internal_results(self.scrape_provider, self.sources)
			def _process():
				for item in self.scrape_results:
					try:
						file_name = item['filename']
						if self.media_type == 'episode':
							if not source_utils.cloud_episode_matches(self.season, self.episode, file_name): continue
							if filter_title and not source_utils.check_title(title, file_name, self.aliases, self.year, 'pack', self.episode): continue
						elif filter_title and not source_utils.check_title(title, file_name, self.aliases, self.year, self.season, self.episode): continue
						display_name = clean_file_name(file_name).replace('html', ' ').replace('+', ' ').replace('-', ' ')
						file_dl, size = Offcloud.requote_uri(item['url']), 0
						video_quality, details = source_utils.get_file_info(name_info=source_utils.release_info_format(file_name))
						source_item = {'name': file_name, 'display_name': display_name, 'quality': video_quality, 'size': size, 'size_label': '%.2f GB' % size,
									'extraInfo': details, 'url_dl': file_dl, 'id': file_dl, 'downloads': False, 'direct': True, 'source': self.scrape_provider,
									'debrid': self.scrape_provider, 'scrape_provider': self.scrape_provider, 'direct_debrid_link': True}
						yield source_item
					except Exception:
						pass
			self.sources = list(_process())
		except Exception as e:
			from modules.kodi_utils import logger
			logger('offcloud scraper Exception', e)
		source_utils.internal_results(self.scrape_provider, self.sources)
		return self.sources

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

	def _title_match(self, clean_file, folder_name):
		return any(q and (q in clean_file or (folder_name and q in folder_name)) for q in self.title_queries)

	def _contains_year(self, *texts):
		if not self.year:
			return False
		for text in texts:
			if not text:
				continue
			if any(str(y) in text for y in self.year_query_list):
				return True
		return False

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

	def _cloud_file_matches(self, normalized, folder_name='', folder_prefiltered=False):
		if self.media_type == 'movie':
			filename = source_utils.clean_title(normalized)
			return any(x in filename for x in self.year_query_list) and self.folder_query in filename
		if not source_utils.cloud_episode_matches(self.season, self.episode, normalized):
			return False
		if folder_prefiltered:
			return True
		clean_file = source_utils.clean_title(normalized)
		return self._title_match(clean_file, folder_name)

	def _is_cloud_archive(self, item):
		if item.get('isDirectory'):
			return True
		file_name = (item.get('fileName') or '').lower()
		return not file_name.endswith(tuple(self.extensions))

	def _scrape_cloud(self):
		try:
			try:
				my_cloud_files = Offcloud.user_cloud_check()
			except Exception:
				return
			if not my_cloud_files: return
			results_append = self.folder_results.append
			seen_ids = set()
			for item in my_cloud_files:
				if str(item.get('status', '')).lower() != 'downloaded': continue
				request_id = item.get('requestId')
				if self._is_cloud_archive(item):
					raw_folder = item.get('fileName') or ''
					folder_name = source_utils.clean_title(normalize(raw_folder))
					if not self._prefilter_folder(folder_name, raw_folder):
						continue
					if request_id and request_id not in seen_ids:
						seen_ids.add(request_id)
						results_append((request_id, folder_name, raw_folder))
				else:
					file_name = item.get('fileName', '')
					normalized = normalize(file_name)
					if not self._cloud_file_matches(normalized): continue
					link = Offcloud.item_play_link(item)
					if link: self.scrape_results.append({'filename': normalized, 'url': link})
			if not self.folder_results: return
			threads = [Thread(target=self._scrape_folders, args=(i,)) for i in self.folder_results]
			[i.start() for i in threads]
			[i.join() for i in threads]
		except Exception:
			return

	def _scrape_folders(self, folder_info):
		try:
			folder_id, folder_name, _raw_folder = folder_info
			results_append = self.scrape_results.append
			torrent_files = Offcloud.torrent_info(folder_id)
			if not isinstance(torrent_files, list): return
			for item in torrent_files:
				try:
					if not isinstance(item, str) or not item.lower().endswith(tuple(self.extensions)): continue
					normalized = normalize(item.split('/')[-1])
					if not self._cloud_file_matches(normalized, folder_name, folder_prefiltered=True): continue
					results_append({'filename': normalized, 'url': item})
				except Exception:
					continue
		except Exception:
			return
