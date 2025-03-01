# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import importlib
import os
import sys

try:
	from thread_pool import ThreadPool
	import tools
except:
	from a4kscrapers_wrapper.thread_pool import ThreadPool
	from a4kscrapers_wrapper import tools
#from resources.lib.modules.globals import g

from inspect import currentframe, getframeinfo
#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

class SubtitleService:
	"""
	Connects to available subtitle services and retrieves available subtitles for media
	"""

	def __init__(self):
		self.task_queue = ThreadPool()
		#self.subtitle_languages = g.get_kodi_subtitle_languages()
		#self.preferred_language = g.get_kodi_preferred_subtitle_language()
		#self.base_request = {
		#	"languages": ",".join(self.subtitle_languages),
		#	"preferredlanguage": self.preferred_language,
		#}
		self.base_request = {'action': 'search', 'languages': 'English', 'preferredlanguage': 'forced_only'}
		tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)), self.base_request)
		self.sources = [A4kSubtitlesAdapter()]

	def get_subtitle(self):
		"""
		Fetch subtitle source
		:return: Url to subtitle
		:rtype: str
		"""
		#self.base_request['VIDEO_META'] = tools.VIDEO_META
		if self.sources is None:
			return None
		[
			self.task_queue.put(r.search, self.base_request)
			for r in self.sources
			if r.enabled
		]
		results = self.task_queue.wait_completion()
		#results[0]['VIDEO_META'] = tools.VIDEO_META
		if results is None:
			return None
		try:
			return self.sources[0].download(results[0])
		except IndexError:
			tools.log("No subtitles available from A4kSubtitles", "error")
			return None

class A4kSubtitlesAdapter:
	"""
	Ease of use adapter for A4kSubtitles
	"""

	def __init__(self):
		try: 
			from a4kSubtitles import api
		except:
			from a4kscrapers_wrapper.a4kSubtitles import api
		#path = tools.translate_path(
		#	os.path.join(g.ADDONS_PATH, "/plugin.video.seren_downloader/resources/lib/modules")
		#)
		#try:
		#	sys.path.append(path)
		#	self.service = importlib.import_module("a4kSubtitles.api").A4kSubtitlesApi(
		#		{"kodi": tools.is_stub()}
		#	)
		#	self.enabled = True
		#except ImportError:
		#	self.enabled = False
		self.service = api.A4kSubtitlesApi(
			{"kodi": False}
		)
		self.enabled = True

	def search(self, request, **extra):
		"""
		Search for a subtitle
		:param request: Dictionary containing currently available subtitles and the preferred language
		:type request: dict
		:param extra: Kwargs to provide video meta and settings to A4kSubtitles
		:type extra: dict
		:return: Available subtitle matches
		:rtype: list
		"""

		video_meta = extra.pop("video_meta", None)
		settings = extra.pop("settings", None)
		#video_meta = tools.VIDEO_META
		return self.service.search(request, video_meta=video_meta, settings=settings)

	def download(self, request, **extra):
		"""
		Downloads requested subtitle
		:param request: Selected subtitle from search results
		:type request: dict
		:param extra: Kwargs, set settings to settings to request to use
		:type extra: dict
		:return: Path to subtitle
		:rtype: str
		"""
		#tools.log(request)
		try:
			settings = extra.pop("settings", None)
			return self.service.download(request, settings)
		except (OSError, IOError):
			tools.log("Unable to download subtitle, file already exists", "error")
		except Exception as e:
			tools.log("Unknown error acquiring subtitle: {}".format(e), "error")
			#g.log_stacktrace()
