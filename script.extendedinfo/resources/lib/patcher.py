import os, shutil
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
from resources.lib import Utils
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short



def do_patch(patch_file_path, patch_lines, log_addon_name, start_line, end_line):
	file_path = patch_file_path
	if not xbmcvfs.exists(file_path):
		Utils.tools_log('NO_FILE!!!',file_path)
		return
	Utils.tools_log(file_path,log_addon_name)
	file1 = open(file_path, 'r')
	lines = file1.readlines()
	new_file = ''
	update_flag = False
	line_update = patch_lines
	keep_update = False
	end_line_match = False
	for idx, line in enumerate(lines):
		if '## PATCH' in str(line):
			update_flag = False
			log_message = 'ALREADY_PATCHED_%s_' % (log_addon_name)
			Utils.tools_log(log_message)
			xbmc.sleep(100)
			break

		if start_line in str(line):
			new_file = new_file + line_update
			update_flag = True
			keep_update = True
		elif update_flag == True and keep_update == True:
			if end_line in str(line):
				keep_update = False
				end_line_match = True
		elif keep_update == False:
			new_file = new_file + line
	file1.close()
	if update_flag and end_line_match == True:
		file1 = open(file_path, 'w')
		file1.writelines(new_file)
		file1.close()
		log_message = '%s_PATCH_%s' % (file_path,log_addon_name)
		Utils.tools_log(log_message)
	elif update_flag and end_line_match == False:
		log_message = 'NO_PATCH_%s_PATCH_%s__%s' % (file_path,log_addon_name,'END_LINE_NOT_FOUND')
	xbmc.sleep(100)

def patch_redlight():
	from pathlib import Path
	touch_file = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib') , 'PATCH')
	if os.path.exists(touch_file):
		Utils.tools_log('REDLIGHT_already_patched')
		return 
	log_addon_name = 'REDLIGHT'


	##playlist
	file_path_in = os.path.join(os.path.join(Utils.ADDON_PATH, 'resources', 'lib','patches') , 'playlist.py')
	file_path_out = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','modules') , 'playlist.py')
	shutil.copyfile(file_path_in, file_path_out)
	log_message = '%s_PATCH_%s' % (file_path_out,log_addon_name)
	Utils.tools_log(log_message)

	##redlight.auto.json
	file_path_in = os.path.join(os.path.join(Utils.ADDON_PATH, 'resources', 'lib','patches') , 'redlight.auto.json')
	file_path_out = os.path.join(os.path.join(Utils.ADDON_DATA_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'players') , 'redlight.auto.json')
	shutil.copyfile(file_path_in, file_path_out)
	log_message = '%s_PATCH_%s' % (file_path_out,log_addon_name)
	Utils.tools_log(log_message)

	##redlight.select.json
	file_path_in = os.path.join(os.path.join(Utils.ADDON_PATH, 'resources', 'lib','patches') , 'redlight.select.json')
	file_path_out = os.path.join(os.path.join(Utils.ADDON_DATA_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'players') , 'redlight.select.json')
	shutil.copyfile(file_path_in, file_path_out)
	log_message = '%s_PATCH_%s' % (file_path_out,log_addon_name)
	Utils.tools_log(log_message)

	##next_episode
	file_path_in = os.path.join(os.path.join(Utils.ADDON_PATH, 'resources', 'lib','patches') , 'next_episode.xml')
	file_path_out = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'skins','Default','1080i') , 'next_episode.xml')
	shutil.copyfile(file_path_in, file_path_out)
	log_message = '%s_PATCH_%s' % (file_path_out,log_addon_name)
	Utils.tools_log(log_message)

	##router
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','modules') , 'router.py')
	first_line = "	elif 'playback.' in mode:"
	last_line = '		return player_check(mode, params)'
	line_update = '''	elif 'playback.' in mode:   ## PATCH
#		from modules.kodi_utils import player_check   ## PATCH
#		return player_check(mode, params)   ## PATCH
		if mode == 'playback.media':
			from modules.sources import Sources
			from modules.sources import PROP_SOURCES_BUSY
			import xbmc, xbmcgui
			xbmcgui.Window(10000).clearProperty(PROP_SOURCES_BUSY)
			xbmcgui.Window(10000).clearProperty('fenlight.onPlayBackStarted')
			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
			playlist.clear()
			params['prescrape'] = 'true'
			
			return Sources().playback_prep(params)  ## PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	##episode_tools
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','modules') , 'episode_tools.py')
	with open(file_path, "r", encoding="utf-8") as file:
		content = file.read()

	content = content.replace("watched_info = watched_info_episode(self.meta_get('tmdb_id'))", "watched_info = [] #watched_info = watched_info_episode(self.meta_get('tmdb_id'))")

	with open(file_path, "w", encoding="utf-8") as file:
		file.write(content)


	##subtitles
	##subtitles
	#file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','indexers') , 'subtitles.py')
	#with open(file_path, "r", encoding="utf-8") as file:
	#	content = file.read()

	#content = content.replace("enable_local_subtitles(self, poster=self.poster)", "enable_local_subtitles(self, poster=self.poster, notify=False)")
	#content = content.replace("ku.notification('Downloaded subtitles found', icon=self.poster, settle_ms=150)", "#ku.notification('Downloaded subtitles found', icon=self.poster, settle_ms=150)")
	#content = content.replace("ku.notification('Downloaded subtitles found', icon=poster, settle_ms=150)", "#ku.notification('Downloaded subtitles found', icon=poster, settle_ms=150)")
	#content = content.replace("ku.notification('No subtitles found', icon=poster, settle_ms=150)","#ku.notification('No subtitles found', icon=poster, settle_ms=150)")
	#content = content.replace("ku.notification('No subtitles found', icon=self.poster, settle_ms=150)","#ku.notification('No subtitles found', icon=self.poster, settle_ms=150)")

	#with open(file_path, "w", encoding="utf-8") as file:
	#	file.write(content)


	##rd_cloud
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','scrapers') , 'rd_cloud.py')
	with open(file_path, "r", encoding="utf-8") as file:
		content = file.read()
	content = content.replace("source_utils.cloud_episode_matches(","source_utils.seas_ep_filter(")

	with open(file_path, "w", encoding="utf-8") as file:
		file.write(content)

	##source_utils
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','modules') , 'source_utils.py')
	with open(file_path, "r", encoding="utf-8") as file:
		content = file.read()
	content = content.replace("string3 = r'(s<<S>>e<<E1>>[.-]?e?<<E2>>[.-])'","string3 = r'(s<<S>>e<<E1>>[.-]?e?<<E2>>[.-]?)'")
	content = content.replace("string3 = r'(s<<S>>e<<E1>>[.-]?e?<<E2>>[.-]?)'","string3 = r'(s<<S>>e<<E1>>[.-]?e?<<E2>>(?!80)[.-]?)'")

	with open(file_path, "w", encoding="utf-8") as file:
		file.write(content)


	##sources
	##resolve_internal
	Utils.tools_log('resolve_internal')
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','modules') , 'sources.py')
	first_line = "				elif any(i in scrape_provider for i in ('rd_', 'ad_', 'tb_')):"
	last_line = "					if '_cloud' in scrape_provider: item_id = debrid_function().get_item_details(item_id)['link']"
	line_update = '''				elif any(i in scrape_provider for i in ('rd_', 'ad_', 'tb_')):  ## 1PATCH
					#url = debrid_function().unrestrict_link(item_id)
					url = playlist_module.sources_def_resolve_internal_fix_debrid(debrid_function, scrape_provider, direct_debrid_link, url_dl, item_id)
				else:
					if '_cloud' in scrape_provider: item_id = debrid_function().get_item_details(item_id)['link']  ## 1PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line)

	##sources
	##resolve_sources
	Utils.tools_log('resolve_sources')
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','modules') , 'sources.py')
	first_line = "					url = self.resolve_cached(cache_provider, item['url'], item['hash'], title, season, episode, pack)"
	last_line = "	def resolve_cached(self, debrid_provider, item_url, _hash, title, season, episode, pack):"
	line_update = '''					url = self.resolve_cached(cache_provider, item['url'], item['hash'], title, season, episode, pack)   ## 2PATCH
			else: url = item['url']
		except: pass
		if self._user_cancelled_resolve():
			return None
		import modules.playlist as playlist_module
		url = playlist_module.sources_def_resolve_sources_fix_debrid(self,url, item)
		return url

	def resolve_cached(self, debrid_provider, item_url, _hash, title, season, episode, pack):  ## 2PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line)


	##sources
	##play_file
	Utils.tools_log('play_file')
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','modules') , 'sources.py')
	first_line = "	def play_file(self, results, source={}):"
	last_line = "		playable_results = [i for i in results if 'Uncached' not in i.get('cache_provider', '')]"
	line_update = '''	def play_file(self, results, source={}):   ## 3PATCH
		import modules.playlist as playlist_module
		return playlist_module.playlist_play_file(self, results, source)
		playable_results = [i for i in results if 'Uncached' not in i.get('cache_provider', '')]  ## 3PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line)

	##sources
	##_make_nextep_dialog
	##_make_resume_dialog
	Utils.tools_log('_make_resume_dialog')
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','modules') , 'sources.py')
	first_line = "	def _make_resolve_dialog(self):"
	last_line = "	def _make_still_watching_dialog(self, check_text, heading='Still Watching?', right_align=False):"
	line_update = '''	def _make_resolve_dialog(self):   ## 4PATCH
		self.resolve_dialog_made = True
		if not self.progress_dialog: self._make_progress_dialog()
		self.progress_dialog.enable_resolver()

	def _make_resume_dialog(self, percent):   ## 4PATCH
		import modules.playlist as playlist_module
		return playlist_module.make_resume_choice()
		if not self.progress_dialog: self._make_progress_dialog()
		self.progress_dialog.enable_resume(percent)
		return self.progress_dialog.resume_choice

	def _make_nextep_dialog(self, default_action='cancel'):   ## 4PATCH
		import modules.playlist as playlist_module
		return playlist_module.NEW_nextep_dialog(self, default_action)
		try: action = open_window(('windows.playback_notifications', 'NextEpisode'), 'playback_notifications.xml', meta=self.meta, default_action=default_action)
		except: action = 'cancel'
		return action

	def _make_still_watching_dialog(self, check_text, heading='Still Watching?', right_align=False):  ## 4PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line)


	##sources
	##internal_sources
	Utils.tools_log('internal_sources')
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','modules') , 'sources.py')
	first_line = "				active_sources = [i for i in active_sources if i not in prescrape_ran]"
	last_line = "			active_sources = [i for i in active_sources if not (prescrape and not settings.check_prescrape_sources(i, self.media_type))]"
	line_update = '''				active_sources = [i for i in active_sources if i not in prescrape_ran]  ## 5PATCH
		#if cloud_early:  ## 5PATCH
		#	active_sources = [i for i in active_sources if settings.cloud_scrape_before_external(i)]  ## 5PATCH
		if cloud_early:
			active_sources = [i for i in active_sources if i in self._cloud_scrapers()]
		else:
			active_sources = [i for i in active_sources if not (prescrape and not settings.check_prescrape_sources(i, self.media_type))]  ## 5PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line)


	##sources
	##playback_prep
	Utils.tools_log('playback_prep')
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','modules') , 'sources.py')
	first_line = "		if self.background and self.play_type in ('autoplay_nextep', 'autoscrape_nextep', 'random_continual'):"
	last_line = "	def check_episode_group(self):"
	line_update = '''		#if self.background and self.play_type in ('autoplay_nextep', 'autoscrape_nextep', 'random_continual'):   ## 6PATCH
		#	self._log_nextep_scrape_started()
		#	self._prefetch_nextep_segment_data()
		#if self.background and self.autoplay_nextep and self.nextep_settings and not getattr(self, '_nextep_alert_handled', False):
		#	if not self.still_watching_check():
		#		kodi_utils.notification('Cancel Autoplay', icon=self.meta.get('poster'))
		#		return
		#if getattr(self, '_nextep_stash_results', None):
		#	try:
		#		kodi_utils.logger('Red Light', 'Autoplay next episode play: starting resolve for %s S%02dE%02d' % (
		#			self.meta.get('title', ''), self.season, self.episode))
		#	except:
		#		pass
		#	return self.play_file(self._nextep_stash_results)
		#if self.autoscrape: self.autoscrape_nextep_handler()
		#else: return self.get_sources()
		import modules.playlist as playlist_module   ## 6PATCH
		return playlist_module.sources_def_playback_prep_return(self, self.params)   ## 6PATCH

	def check_episode_group(self):  ## 6PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line)

	##sources
	##playback_prep
	Utils.tools_log('playback_prep2')
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','modules') , 'sources.py')
	first_line = "		self.get_meta()"
	last_line = "		self.sleep_time, self.provider_sort_ranks, self.scraper_settings = 100, settings.provider_sort_ranks(), settings.scraping_settings()"
	line_update = '''		self.get_meta()   ## 7PATCH
		self.determine_scrapers_status()
		#if not self.prescrape and not self._playback_skips_prescrape_override() and settings.prescrape_enabled(self.media_type, self.active_internal_scrapers):
		#	self.prescrape = True
		self.sleep_time, self.provider_sort_ranks, self.scraper_settings = 100, settings.provider_sort_ranks(), settings.scraping_settings()  ## 7PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line)

	##sources
	##playback_prep
	Utils.tools_log('playback_prep3')
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','modules') , 'sources.py')
	first_line = "		self.background = params_get('background', 'false') == 'true'"
	last_line = "		if 'prescrape' in self.params:"
	line_update = '''		self.background = params_get('background', 'false') == 'true'   ## PATCH
		#if not self.background and params_get('nextep_stash_play') != 'true' and self._playback_already_active():
		#	return
		self.play_type = params_get('play_type', '')
		if 'prescrape' in self.params:  ## PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line)

	##player
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','modules') , 'player.py')
	first_line = "	def set_playback_properties(self):"
	last_line = "	def safe_stop(self):"
	line_update = '''	def set_playback_properties(self):  ## PATCH
		try:
			trakt_ids = {'tmdb': self.tmdb_id, 'imdb': self.imdb_id, 'slug': make_trakt_slug(self.title)}
			if self.media_type == 'episode': trakt_ids['tvdb'] = self.tvdb_id
			ku.set_property('script.trakt.ids', json.dumps(trakt_ids))
			if self.playing_filename or getattr(self, 'playing_item', None):
				try:
					from indexers.subtitles import _best_play_filename
					season = self.season if self.media_type == 'episode' else None
					episode = self.episode if self.media_type == 'episode' else None
					best = _best_play_filename(self.playing_filename, getattr(self, 'playing_item', None), season, episode)
					ku.set_property('subs.player_filename', best or self.playing_filename)
				except:
					if self.playing_filename: ku.set_property('subs.player_filename', self.playing_filename)
			elif self.playing_filename:
				ku.set_property('subs.player_filename', self.playing_filename)
		except: pass
		import modules.playlist as playlist_module
		return playlist_module.set_playback_properties_additional(self, trakt_ids)

	def safe_stop(self): ## PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	##service
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib') , 'service.py')
	first_line = "		_start_daemon(lambda: WidgetRefresher().run(self))"
	last_line = "		except Exception as e: kodi_utils.logger('AutoStart', str(e))"
	line_update = '''		_start_daemon(lambda: WidgetRefresher().run(self))  ## PATCH
		import modules.playlist as playlist_module
		self.player_monitor = playlist_module.PlayerMonitor()
		
		try: AutoStart().run(self)
		except Exception as e: kodi_utils.logger('AutoStart', str(e)) ## PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	##rd_cloud
	##_scrape_downloads
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','scrapers') , 'rd_cloud.py')
	first_line = "			for item in my_downloads:"
	last_line = "				elif not source_utils.seas_ep_filter(self.season, self.episode, normalized): continue"
	line_update = '''			for item in my_downloads:  ## 1PATCH
				normalized = normalize(item['filename'])
				folder_name = source_utils.clean_title(normalized)
				#if not self.folder_query in folder_name: continue ## 1PATCH
				if not any(q in folder_name for q in self.folder_queries): continue
				if self.media_type == 'movie':
					if not any(x in normalized for x in year_query_list): continue
				elif not source_utils.seas_ep_filter(self.season, self.episode, normalized): continue  ## 1PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	##rd_cloud
	##_scrape_cloud
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','scrapers') , 'rd_cloud.py')
	first_line = "			for item in my_cloud_files:"
	last_line = "					if self.media_type == 'movie' and not any(x in normalized for x in year_query_list): continue"
	line_update = '''			for item in my_cloud_files:
				normalized = normalize(item['filename'])
				folder_name = source_utils.clean_title(normalized)   ## 2PATCH
				if not folder_name: results_append(item['id'])
				#elif not self.folder_query in folder_name: continue    ## 2PATCH
				elif not any(q in folder_name for q in self.folder_queries): continue
				else:
					if self.media_type == 'movie' and not any(x in normalized for x in year_query_list): continue  ## 2PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	##rd_cloud
	##results
	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.redlight'), 'resources', 'lib','scrapers') , 'rd_cloud.py')
	first_line = "			self.folder_query = source_utils.clean_title(normalize(title))"
	last_line = "			aliases = source_utils.get_aliases_titles(info.get('aliases', []))"
	line_update = '''			self.folder_query = source_utils.clean_title(normalize(title))   ## PATCH
			#self._scrape_downloads()   ## PATCH
			#self._scrape_cloud()   ## PATCH
			#if not self.scrape_results: return source_utils.internal_results(self.scrape_provider, self.sources)    ## PATCH
			aliases = source_utils.get_aliases_titles(info.get('aliases', []))
			import modules.playlist as playlist_module
			self.folder_queries = playlist_module.rd_cloud_def_results_alias_fix(title, aliases)
			self._scrape_downloads()
			self._scrape_cloud()
			if not self.scrape_results: return source_utils.internal_results(self.scrape_provider, self.sources)  ## PATCH
'''
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	Utils.tools_log('DISABLE_REDLIGHT')
	xbmc.executebuiltin('DisableAddon(plugin.video.redlight)')
	Utils.tools_log('EnableAddon(plugin.video.redlight)')
	xbmc.executebuiltin('EnableAddon(plugin.video.redlight)')
	xbmc.sleep(500)
	if xbmc.getCondVisibility('Control.HasFocus(11)'):
		label = 'Yes'
	elif xbmc.getCondVisibility('Control.HasFocus(10)'):
		label = 'No'

	x = 0
	while label != 'Yes' and x < 25:
		xbmc.executebuiltin('Action(right)')
		xbmc.sleep(500)
		if xbmc.getCondVisibility('Control.HasFocus(11)'):
			label = 'Yes'
		elif xbmc.getCondVisibility('Control.HasFocus(10)'):
			label = 'No'

		if label == 'Yes' or x >= 25:
			break
		x = x +1
	xbmc.executebuiltin('Action(select)')
	xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
	xbmc.executebuiltin('Dialog.Close(busydialog)')
	xbmc.executebuiltin('Dialog.Close(ExtendedProgressDialog,True)')
	xbmc.executebuiltin('Dialog.Close(progressdialog,True)')
	Path(touch_file).touch()
	return



def patch_tmdbh():
	from pathlib import Path
	touch_file = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib') , 'PATCH')
	if os.path.exists(touch_file):
		Utils.tools_log('TMDBH_already_patched')
		return 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','player') , 'players.py')
	if not os.path.exists(file_path):
		file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'lib','player') , 'players.py')
	line_update = '''            for idx, i in enumerate(players_list): ## PATCH
                if 'auto_cloud' in str(i).lower() and self.tmdb_type != 'movie': ## PATCH
                    auto_var = idx ## PATCH
                    break ## PATCH
                if 'Auto_Torr_Scrape' in str(i) and self.tmdb_type == 'movie': ## PATCH
                    auto_var = idx ## PATCH
                    break ## PATCH
            #return Dialog().select(header, players, useDetails=detailed) ## PATCH
            #return Dialog().select(header, players, autoclose=30000, preselect=auto_var, useDetails=detailed) ## PATCH
            return Dialog().select(header, players, autoclose=30000, preselect=auto_var, useDetails=detailed) ## PATCH
'''
	first_line = '            for idx, i in enumerate(players_list): '
	last_line = 'return Dialog().select(header, players, useDetails=detailed)'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','player') , 'select.py')
	line_update = '''    def select_player(players_list, header=None, detailed=True, index=False, players=None):
        """ Select from a list of players """
        if 'episode' in str(players[0]['mode']):
            db_type = 'episode'
        else:
            db_type = 'movie'
        for idx, i in enumerate(players): ## PATCH
            if 'auto_cloud' in str(i['name']).lower() and db_type != 'movie': ## PATCH
                auto_var = idx ## PATCH
                break ## PATCH
            if 'Auto_Torr_Scrape' in str(i['name']) and db_type == 'movie': ## PATCH
                auto_var = idx ## PATCH
                break ## PATCH
        x = Dialog().select(header or get_localized(32042), [i.listitem for i in players_list],useDetails=detailed, autoclose=30000, preselect=auto_var)
        return x if index or x == -1 else players_list[x].posx

    def get_player(self, x):
        player = self.players_list[x]
        player['idx'] = x
        return player

    def select(self, header=None, detailed=True):
        """ Select a player from the list """
        x = self.select_player(self.players_generated_list, header=header, detailed=detailed, players=self.players)
        return {} if x == -1 else self.get_player(x)
'''
	first_line = '    def select_player(players_list, header=None, detailed=True, index=False):'
	last_line = '        return {} if x == -1 else self.get_player(x)'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 


	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','player','dialog') , 'standard.py')
	line_update = '''    def select_player(players_list, header=None, detailed=True, index=False, players=None):
        """ Select from a list of players """
        import xbmc
        #xbmc.log(str([i.listitem for i in players_list])+' ===select_player', level=xbmc.LOGINFO)
        players = [i.__dict__ for i in players]
        if 'episode' in str(players[0]['mode']):
            db_type = 'episode'
        else:
            db_type = 'movie'
        for idx, i in enumerate(players): ## PATCH
            if 'Diamond check RD Cloud + Play' in str(i['meta']['name']) and db_type != 'movie': ## PATCH
                auto_var = idx ## PATCH
                header = str(i['item']['name']) + ' - ' + str(i['item']['title']) + ' - ' + str(i['item']['firstaired'])
                break ## PATCH
            if 'Diamond Search + Auto Play Torrent' in str(i['meta']['name']) and db_type == 'movie': ## PATCH
                auto_var = idx ## PATCH
                header = str(i['item']['name']) + ' - ' + str(i['item']['year'])
                break ## PATCH
        x = Dialog().select(header or get_localized(32042), [i.listitem for i in players_list],useDetails=detailed, autoclose=30000, preselect=auto_var)
        return x if index or x == -1 else players_list[x].posx

    def get_player(self, x):
        return self.players_list[x]

    def select(self, header=None, detailed=True):
        """ Select a player from the list """
        x = self.select_player(self.players_generated_list, header=header, detailed=detailed, players=self.players)
        return {} if x == -1 else self.get_player(x)
'''
	first_line = '    def select_player(players_list, header=None, detailed=True, index=False):'
	last_line = '        return {} if x == -1 else self.get_player(x)'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 


	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','script','method') , 'maintenance.py')
	line_update = '''    def vacuum(self, force=False):  ##PATCH
        import time
        if not force and self.is_next_vacuum == False:
            return
        if time.time() < self.next_vacuum:
            return
        self.set_next_vacuum()
        from tmdbhelper.lib.addon.logger import TimerFunc
        from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        with TimerFunc('Vacuuming databases:', inline=True):
            ItemDetailsDatabase().execute_sql("VACUUM")
            FindQueriesDatabase().execute_sql("VACUUM")

    def delete_legacy_folders(self, force=False): ##PATCH
'''
	first_line = '    def vacuum(self, force=False):'
	last_line = '    def delete_legacy_folders(self, force=False):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','api','trakt') , 'authenticator.py')
	line_update = '''    def poller(self): ## PATCH
        import xbmc
        while True:
            xbmc.log(str(self.user_code)+'===>PHIL', level=xbmc.LOGINFO)
            if self.xbmc_monitor.abortRequested(): ## PATCH
'''
	first_line = '    def poller(self):'
	last_line = '            if self.xbmc_monitor.abortRequested():'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','monitor') , 'player.py')
	line_update = '''    def onAVStarted(self):  ## 1PATCH
        import xbmc
        xbmc.sleep(5*1000)
        try: self.get_playingitem()
        except: return

    def onPlayBackStarted(self):
        import xbmc
        xbmc.sleep(5*1000)
        try: self.get_playingitem()
        except: return

    def onAVChange(self):
        import xbmc
        xbmc.sleep(5*1000)
        try: self.get_playingitem()
        except: return

    def onPlayBackEnded(self):  ## 1PATCH
'''
	first_line = '    def onAVStarted(self):'
	last_line = '    def onPlayBackEnded(self):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','monitor') , 'player.py')
	line_update = '''    def get_playingitem(self):  ## PATCH
        # Check that video other than dummy splash video is playing  ## PATCH
        if not self.isPlayingVideo(): ## PATCH
            self.reset_properties()  ## PATCH
            return  ## PATCH
        if self.getPlayingFile() and self.getPlayingFile().endswith('dummy.mp4'):  ## PATCH
            self.reset_properties()  ## PATCH
            return ## PATCH
 ## PATCH
        # Get fresh info tags etc. ## PATCH
'''
	first_line = '    def get_playingitem(self):'
	last_line = '        # Get fresh info tags etc.'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 




	Path(touch_file).touch()
	return




	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','script','method') , 'trakt.py')
	line_update = '''def authenticate_trakt(**kwargs): ## PATCH
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    TraktAPI(force=True)
    invalidate_trakt_sync('all', notification=False)

def authorize_trakt(**kwargs):
    import xbmc
    from tmdbhelper.lib.addon.logger import kodi_log
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from tmdbhelper.lib.api.trakt.token import TraktStoredAccessToken
    trakt_api = TraktAPI(force=False)
    TraktStoredAccessToken(trakt_api).winprop_traktusertoken = ''
    refresh_token = TraktStoredAccessToken(trakt_api).refresh_token
    response = trakt_api.set_authorisation_token(refresh_token)
    if response != {}:
        xbmc.log(str('Trakt authenticated successfully!')+'===>PHIL', level=xbmc.LOGINFO)
    from tmdbhelper.lib.files.futils import json_dumps as data_dumps
    trakt_api.user_token.value = data_dumps(response)
    from tmdbhelper.lib.api.api_keys.tokenhandler import TokenHandler
    USER_TOKEN = TokenHandler('trakt_token', store_as='setting')
    TraktStoredAccessToken(trakt_api).winprop_traktusertoken = USER_TOKEN.value
    TraktStoredAccessToken(trakt_api).confirm_authorization()
    return

def revoke_trakt(**kwargs): ## PATCH
'''
	first_line = 'def authenticate_trakt(**kwargs):'
	last_line = 'def revoke_trakt(**kwargs):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','script') , 'router.py')
	line_update = '''        'authenticate_trakt': ## PATCH
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'authenticate_trakt')(**kwargs),
        'authorize_trakt':
            lambda **kwargs: importmodule('tmdbhelper.lib.script.method.trakt', 'authorize_trakt')(**kwargs),
        'revoke_trakt': ## PATCH
'''
	first_line = "        'authenticate_trakt':"
	last_line = "        'revoke_trakt':" 
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','monitor') , 'player.py')
	line_update = '''    def onAVStarted(self):  ## PATCH
        import xbmc
        xbmc.sleep(5*1000)
        try: self.get_playingitem()
        except: return

    def onPlayBackStarted(self):
        import xbmc
        xbmc.sleep(5*1000)
        try: self.get_playingitem()
        except: return

    def onAVChange(self):
        import xbmc
        xbmc.sleep(5*1000)
        try: self.get_playingitem()
        except: return

    def onPlayBackEnded(self):  ## PATCH
'''
	first_line = '    def onAVStarted(self):'
	last_line = '    def onPlayBackEnded(self):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 


	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','api', 'trakt') , 'api.py')
	line_update = '''    def access_token(self):   ## PATCH
        #if not self.authenticator.access_token:
        #    return
        #if not self.authenticator.trakt_stored_access_token.has_valid_token:
        #    self.refresh_authenticator()
        #return self.authenticator.access_token
        if not self.authenticator.trakt_stored_access_token.has_valid_token:
            self.refresh_authenticator()
        from tmdbhelper.lib.api.api_keys.tokenhandler import TokenHandler
        from tmdbhelper.lib.files.futils import json_loads as data_loads
        USER_TOKEN = TokenHandler('trakt_token', store_as='setting')
        try: access_token = data_loads(USER_TOKEN.value)['access_token']
        except: return None
        if access_token != self.authenticator.access_token:
            #self.authenticator.access_token = access_token
            from tmdbhelper.lib.api.trakt.token import TraktStoredAccessToken
            TraktStoredAccessToken(self).on_success()
            self.refresh_authenticator()
        return access_token

    @cached_property
    def authenticator(self):  ## PATCH
'''
	first_line = '    def access_token(self):'
	last_line = '    def authenticator(self):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	file_path = os.path.join(os.path.join(Utils.ADDON_PATH.replace(addon_ID(),'plugin.video.themoviedb.helper'), 'resources', 'tmdbhelper','lib','api', 'trakt') , 'token.py')
	line_update = '''    def update_stored_authorization(self):  ## PATCH
        test_user_token = self.winprop_traktusertoken
        self.trakt_api.user_token.value = self.winprop_traktusertoken = data_dumps(self.stored_authorization)
        if test_user_token != self.trakt_api.user_token.value and len(test_user_token) > 4:
            self.trakt_api.user_token.value = data_dumps(test_user_token)
            self.stored_authorization = data_dumps(test_user_token)
            self.winprop_traktusertoken = data_dumps(test_user_token)

    @property
    def winprop_traktusertoken(self):  ## PATCH
'''
	first_line = '    def update_stored_authorization(self):'
	last_line = '    def winprop_traktusertoken(self):'
	log_addon_name = 'TMDB_HELPER'
	do_patch(patch_file_path = file_path, patch_lines = line_update, log_addon_name = log_addon_name, start_line = first_line, end_line = last_line) 

	Path(touch_file).touch()
	return