# -*- coding: utf-8 -*-
from modules.settings import most_watched_provider
from modules import kodi_utils

MOST_WATCHED_PAGE_SIZE = 20
MOST_WATCHED_ACTIONS = ('movies_most_watched', 'tv_most_watched', 'anime_most_watched', 'trakt_movies_most_watched', 'trakt_tv_most_watched', 'trakt_anime_most_watched')
_ACTION_ALIASES = {
	'trakt_movies_most_watched': 'movies_most_watched',
	'trakt_tv_most_watched': 'tv_most_watched',
	'trakt_anime_most_watched': 'anime_most_watched',
}
_SIMKL_MEDIA = {'movies_most_watched': 'movies', 'tv_most_watched': 'tv', 'anime_most_watched': 'anime'}

def normalize_most_watched_action(action):
	return _ACTION_ALIASES.get(action, action)

def most_watched_category_name(action):
	if most_watched_provider() != 'simkl': return None
	action = normalize_most_watched_action(action)
	labels = {
		'movies_most_watched': 'Most Watched Movies on Simkl',
		'tv_most_watched': 'Most Watched TV on Simkl',
		'anime_most_watched': 'Most Watched Anime on Simkl',
	}
	return labels.get(action)

def simkl_most_watched_has_next(action, page_no):
	from apis.simkl_api import simkl_trending_today_count
	action = normalize_most_watched_action(action)
	media_kind = _SIMKL_MEDIA.get(action)
	if not media_kind: return False
	return page_no * MOST_WATCHED_PAGE_SIZE < simkl_trending_today_count(media_kind)

def _simkl_page(action, page_no):
	from apis.simkl_api import simkl_trending_today_page
	return simkl_trending_today_page(_SIMKL_MEDIA[action], page_no, MOST_WATCHED_PAGE_SIZE)

def _trakt_page(action, page_no):
	if action == 'movies_most_watched':
		from apis.trakt_api import trakt_movies_most_watched
		return trakt_movies_most_watched(page_no) or []
	if action == 'tv_most_watched':
		from apis.trakt_api import trakt_tv_most_watched
		return trakt_tv_most_watched(page_no) or []
	from apis.trakt_api import trakt_anime_most_watched
	return trakt_anime_most_watched(page_no) or []

def _most_watched_page(action, page_no):
	action = normalize_most_watched_action(action)
	if most_watched_provider() == 'simkl':
		data = _simkl_page(action, page_no)
		if data: return data
		kodi_utils.logger('Red Light', 'Most Watched: Simkl empty for %s page %s, falling back to Trakt' % (action, page_no))
	return _trakt_page(action, page_no)

def movies_most_watched(page_no):
	return _most_watched_page('movies_most_watched', page_no)

def tv_most_watched(page_no):
	return _most_watched_page('tv_most_watched', page_no)

def anime_most_watched(page_no):
	return _most_watched_page('anime_most_watched', page_no)

def trakt_movies_most_watched(page_no):
	return movies_most_watched(page_no)

def trakt_tv_most_watched(page_no):
	return tv_most_watched(page_no)

def trakt_anime_most_watched(page_no):
	return anime_most_watched(page_no)
