# -*- coding: utf-8 -*-
import time
import json
import random
from threading import Thread
from caches.external_cache import external_cache
from caches.settings_cache import get_setting
from modules import kodi_utils, source_utils
from modules.debrid import RD_check, PM_check, AD_check, OC_check, ED_check ,TB_check, query_local_cache
from modules.utils import clean_file_name
# logger = kodi_utils.logger

normalize, get_file_info, pack_enable_check = source_utils.normalize, source_utils.get_file_info, source_utils.pack_enable_check
sleep, xbmc_monitor, get_property, set_property = kodi_utils.sleep, kodi_utils.xbmc_monitor, kodi_utils.get_property, kodi_utils.set_property
notification, hide_busy_dialog = kodi_utils.notification, kodi_utils.hide_busy_dialog
int_window_prop = 'fenlight.internal_results.%s'
pack_display = '%s (%s)'
pack_check = ('Season', 'Show')
debrid_runners = {'Real-Debrid': ('Real-Debrid', RD_check), 'Premiumize.me': ('Premiumize.me', PM_check), 'AllDebrid': ('AllDebrid', AD_check),
'Offcloud': ('Offcloud', OC_check), 'EasyDebrid': ('EasyDebrid', ED_check), 'TorBox': ('TorBox', TB_check)}
sd_check = ('SD', 'CAM', 'TELE', 'SYNC')
correct_pack_sizes = ('torrentio', 'knightcrawler', 'comet')

class source:
	def __init__(self, meta, source_dict, active_debrid, debrid_service, debrid_token, internal_scrapers, prescrape_sources, progress_dialog, disabled_ext_ignored=False):
		self.monitor = xbmc_monitor()
		self.scrape_provider = 'external'
		self.progress_dialog = progress_dialog
		self.meta = meta
		self.background = self.meta.get('background', False)
		self.active_debrid = active_debrid
		self.debrid_service, self.debrid_token = debrid_service, debrid_token
		self.source_dict, self.host_dict = source_dict, []
		self.sources, self.all_internal_sources, self.processed_internal_scrapers = [], [], []
		self.processed_internal_scrapers_append = self.processed_internal_scrapers.append
		self.internal_scrapers, self.prescrape_sources = internal_scrapers, prescrape_sources
		self.internal_activated, self.internal_prescraped = len(self.internal_scrapers) > 0, len(self.prescrape_sources) > 0
		self.processed_prescrape, self.threads_completed = False, False
		self.sleep_time = 100
		self.timeout = 60 if disabled_ext_ignored else int(get_setting('fenlight.results.timeout', '20'))
		self.sources_total = self.sources_4k = self.sources_1080p = self.sources_720p = self.sources_sd = 0
		self.final_total = self.final_4k = self.final_1080p = self.final_720p = self.final_sd = 0
		self.count_tuple = (('sources_4k', '4K', self._quality_length), ('sources_1080p', '1080p', self._quality_length), ('sources_720p', '720p', self._quality_length),
							('sources_sd', '', self._quality_length_sd), ('sources_total', '', self.quality_length_final))
		self.count_tuple_final = (('final_4k', '4K', self._quality_length), ('final_1080p', '1080p', self._quality_length), ('final_720p', '720p', self._quality_length),
									('final_sd', '', self._quality_length_sd), ('final_total', '', self.quality_length_final))

	def results(self, info):
		if not self.source_dict: return
		try:
			self.media_type, self.tmdb_id, self.orig_title = info['media_type'], str(info['tmdb_id']), info['title']
			self.season, self.episode, self.total_seasons = info['season'], info['episode'], info['total_seasons']
			self.title, self.year = normalize(info['title']), info['year']
			ep_name, aliases = normalize(info['ep_name']), info['aliases']
			self.single_expiry, self.season_expiry, self.show_expiry = info['expiry_times']
			if self.media_type == 'movie':
				self.season_divider, self.show_divider = 0, 0
				self.data = {'imdb': info['imdb_id'], 'title': self.title, 'aliases': aliases, 'year': self.year,
				'debrid_service': self.debrid_service, 'debrid_token': self.debrid_token}
			else:
				try: self.season_divider = [int(x['episode_count']) for x in self.meta['season_data'] if int(x['season_number']) == int(self.meta['season'])][0]
				except: self.season_divider = 1
				self.show_divider = int(self.meta['total_aired_eps'])
				self.data = {'imdb': info['imdb_id'], 'tvdb': info['tvdb_id'], 'tvshowtitle': self.title, 'aliases': aliases,'year': self.year,
							'title': ep_name, 'season': str(self.season), 'episode': str(self.episode), 'debrid_service': self.debrid_service, 'debrid_token': self.debrid_token}
		except: return []
		return self.get_sources()

	def get_sources(self):
		def _scraperDialog():
			hide_busy_dialog()
			sleep(200)
			start_time = time.time()
			while not self.progress_dialog.iscanceled() and not self.monitor.abortRequested():
				try:
					alive_threads = [x.getName() for x in self.threads if x.is_alive()]
					if self.internal_activated or self.internal_prescraped: alive_threads.extend(self.process_internal_results())
					line1 =  ', '.join(alive_threads).upper()
					percent = (max((time.time() - start_time), 0)/float(self.timeout))*100
					self.progress_dialog.update_scraper(self.sources_sd, self.sources_720p, self.sources_1080p, self.sources_4k, self.sources_total, line1, percent)
					if self.threads_completed:
						len_alive_threads = len(alive_threads)
						if len_alive_threads == 0 or percent >= 100: break
					elif percent >= 100: break
					sleep(self.sleep_time)
				except: pass
			return
		def _background():
			sleep(1500)
			end_time = time.time() + self.timeout
			while time.time() < end_time:
				alive_threads = [x for x in self.threads if x.is_alive()]
				len_alive_threads = len(alive_threads)
				sleep(1000)
				if len_alive_threads <= 5: return
				if len(self.sources) >= 100 * len_alive_threads: return
		self.threads = []
		self.threads_append = self.threads.append
		if self.media_type == 'movie':
			self.source_dict = [i for i in self.source_dict if i[1].hasMovies]
			Thread(target=self.process_movie_threads).start()
		else:
			self.source_dict = [i for i in self.source_dict if i[1].hasEpisodes]
			self.season_packs, self.show_packs = pack_enable_check(self.meta, self.season, self.episode)
			if self.season_packs:
				self.source_dict = [(i[0], i[1], '') for i in self.source_dict]
				pack_capable = [i for i in self.source_dict if i[1].pack_capable]
				if pack_capable:
					self.source_dict.extend([(i[0], i[1], 'Season') for i in pack_capable])
					if self.show_packs: self.source_dict.extend([(i[0], i[1], 'Show') for i in pack_capable])
					random.shuffle(self.source_dict)
			Thread(target=self.process_episode_threads).start()
		if self.background: _background()
		else: _scraperDialog()
		current_results = list(self.sources)
		if current_results: return self.process_results(current_results)
		return []

	def process_movie_threads(self):
		for i in self.source_dict:
			provider, module = i[0], i[1]
			threaded_object = Thread(target=self.get_movie_source, args=(provider, module), name=provider)
			threaded_object.start()
			self.threads_append(threaded_object)
		self.threads_completed = True

	def process_episode_threads(self):
		for i in self.source_dict:
			provider, module = i[0], i[1]
			try: pack_arg = i[2]
			except: pack_arg = ''
			if pack_arg: provider_display = pack_display % (i[0], i[2])
			else: provider_display = provider
			threaded_object = Thread(target=self.get_episode_source, args=(provider, module, pack_arg), name=provider_display)
			threaded_object.start()
			self.threads_append(threaded_object)
		self.threads_completed = True

	def get_movie_source(self, provider, module):
		sources = external_cache.get(provider, self.media_type, self.tmdb_id, self.title, self.year, '', '')
		if sources == None:
			sources = module().sources(self.data, self.host_dict)			
			sources = self.process_sources(provider, sources)
			if not sources: expiry_hours = 1
			else: expiry_hours = self.single_expiry
			external_cache.set(provider, self.media_type, self.tmdb_id, self.title, self.year, '', '', sources, expiry_hours)
		if sources:
			if not self.background: self.process_quality_count(sources)
			self.sources.extend(sources)

	def get_episode_source(self, provider, module, pack):
		if pack in pack_check:
			if pack == 'Show': s_check = ''
			else: s_check = self.season
			e_check = ''
		else: s_check, e_check = self.season, self.episode
		sources = external_cache.get(provider, self.media_type, self.tmdb_id, self.title, self.year, s_check, e_check)
		if sources == None:
			if pack == 'Show':
				expiry_hours = self.show_expiry
				sources = module().sources_packs(self.data, self.host_dict, search_series=True, total_seasons=self.total_seasons)
			elif pack == 'Season':
				expiry_hours = self.season_expiry
				sources = module().sources_packs(self.data, self.host_dict)
			else:
				expiry_hours = self.single_expiry
				sources = module().sources(self.data, self.host_dict)
			sources = self.process_sources(provider, sources)
			if not sources: expiry_hours = 1
			external_cache.set(provider, self.media_type, self.tmdb_id, self.title, self.year, s_check, e_check, sources, expiry_hours)
		if sources:
			if pack == 'Season': sources = [i for i in sources if not 'episode_start' in i or i['episode_start'] <= self.episode <= i['episode_end']]
			elif pack == 'Show': sources = [i for i in sources if i['last_season'] >= self.season]
			if not self.background: self.process_quality_count(sources)
			self.sources.extend(sources)

	def process_results(self, results):
		def _process_duplicates(all_results):
			unique_urls, unique_hashes = set(), set()
			unique_urls_add, unique_hashes_add = unique_urls.add, unique_hashes.add
			for provider in all_results:
				try:
					url = provider['url'].lower()
					if url not in unique_urls:
						unique_urls_add(url)
						if 'hash' in provider:
							if provider['hash'] not in unique_hashes:
								unique_hashes_add(provider['hash'])
								yield provider
						else: yield provider
				except: yield provider
		def _process_cache_check(provider, function):
			cached = function(hash_list, cached_hashes)
			if not self.background: self.process_quality_count_final([i for i in results if i['hash'] in cached])
			final_results.extend([dict(i, **{'cache_provider': provider if i['hash'] in cached else 'Uncached %s' % provider, 'debrid':provider}) for i in results])
		def _debrid_check_dialog():
			self.progress_dialog.reset_is_cancelled()
			start_time, timeout = time.time(), 20
			while not self.progress_dialog.iscanceled() and not self.monitor.abortRequested():
				try:
					remaining_debrids = [x.getName() for x in debrid_check_threads if x.is_alive() is True]
					current_progress = max((time.time() - start_time), 0)
					line1 = ', '.join(remaining_debrids).upper()
					percent = int((current_progress/float(timeout))*100)
					self.progress_dialog.update_scraper(self.final_sd, self.final_720p, self.final_1080p, self.final_4k, self.final_total, line1, percent)
					sleep(self.sleep_time)
					if len(remaining_debrids) == 0: break
					if percent >= 100: break
				except: pass
		try:
			if not self.background and self.all_internal_sources: self.process_quality_count_final(self.all_internal_sources)
			final_results = []
			results = list(_process_duplicates(results))
			hash_list = list(set([i['hash'] for i in results]))
			cached_hashes = query_local_cache(hash_list)
			debrid_check_threads = [Thread(target=_process_cache_check, args=debrid_runners[item], name=item) for item in self.active_debrid]
			[i.start() for i in debrid_check_threads]
			if self.background: [i.join() for i in debrid_check_threads]
			else: _debrid_check_dialog()
			return final_results
		except: return []

	def process_sources(self, provider, sources):
		try:
			for i in sources:
				try:
					i_get = i.get
					size, size_label, divider = 0, None, None
					if 'hash' in i:
						_hash = i_get('hash').lower()
						i['hash'] = str(_hash)
					display_name = clean_file_name(normalize(i['name'].replace('html', ' ').replace('+', ' ').replace('-', ' ')))
					if 'name_info' in i: quality, extraInfo = get_file_info(name_info=i_get('name_info'))
					else: quality, extraInfo = get_file_info(url=i_get('url'))
					try:
						size = i_get('size')
						if 'package' in i and provider not in correct_pack_sizes:
							if i_get('package') == 'season': divider = self.season_divider
							else: divider = self.show_divider
							size = float(size) / divider
						size_label = '%.2f GB' % size
					except: pass
					i.update({'provider': provider, 'display_name': display_name, 'external': True, 'scrape_provider': self.scrape_provider, 'extraInfo': extraInfo,
							'quality': quality, 'size_label': size_label, 'size': round(size, 2)})
				except: pass
		except: pass
		return sources

	def process_quality_count(self, sources):
		for item in self.count_tuple: setattr(self, item[0], getattr(self, item[0]) + item[2](sources, item[1]))
	
	def process_quality_count_final(self, sources):
		for item in self.count_tuple_final: setattr(self, item[0], getattr(self, item[0]) + item[2](sources, item[1]))

	def process_internal_results(self):
		if self.internal_prescraped and not self.processed_prescrape:
			self.all_internal_sources += self.prescrape_sources
			self.process_quality_count(self.prescrape_sources)
			self.processed_prescrape = True
		for i in self.internal_scrapers:
			win_property = get_property(int_window_prop % i)
			if win_property in ('checked', '', None): continue
			try: internal_sources = json.loads(win_property)
			except: continue
			set_property(int_window_prop % i, 'checked')
			self.all_internal_sources += internal_sources
			self.processed_internal_scrapers_append(i)
			self.process_quality_count(internal_sources)
		return [i for i in self.internal_scrapers if not i in self.processed_internal_scrapers]

	def _quality_length(self, items, quality):
		return len([i for i in items if i['quality'] == quality])

	def _quality_length_sd(self, items, dummy):
		return len([i for i in items if i['quality'] in sd_check])

	def quality_length_final(self, items, dummy):
		return len(items)