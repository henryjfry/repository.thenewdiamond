# -*- coding: utf-8 -*-

import inspect

from inspect import currentframe, getframeinfo
#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))


from providerModules.a4kScrapers import core

class sources(core.DefaultSources):
	def __init__(self, *args, **kwargs):
		#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		super(sources, self).__init__(__name__, *args, single_query=True, **kwargs)

	def _get_scraper(self, title):
		#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		return super(sources, self)._get_scraper(title)

	def _search_request(self, url, query):
		#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		##query = self._imdb
		##if not self.is_movie_query():
		##	query += ':' + self.scraper.season_x + ':' + self.scraper.episode_x

		request_url = url.base + (url.search % core.quote_plus(query))
		response = self._request.get(request_url)

		#print(response.text)

		if response.status_code != 200:
			return []

		##response = core.normalize(response.text)
		#print(request_url)

		##try:
		##	response = core.json.loads(response.text)
		##except Exception as e:
		##	self._request.exc_msg = 'Failed to parse json: %s' % response.text
		##	return []

		#print(response)
		##return response['torrent_results']
		return response

	"""
	def _soup_filter(self, response):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		return self.genericScraper._parse_rows(response, row_tag='tum')

	def _title_filter(self, el):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		return el['title']

	def _info(self, el, url, torrent):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		torrent['magnet'] = el['download']

		try: torrent['size'] = int((el['size'] / 1024) / 1024)
		except: pass

		torrent['seeds'] = el['seeders']

		return torrent
	"""

	def _soup_filter(self, response):
		#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		#response_list = core.beautifulSoup(response).find_all(class_='gai')
		#print(response.text)
		response_list = response.text.split('class="gai"')

		#return core.beautifulSoup(response).find_all(class_='tum')
		results = []
		for item in response_list:
			result = lambda: None
			test = item
			if 'urn:btih:' in str(test):
				result.hash = test.split('urn:btih:')[1].split('&dn')[0]
				result.title = test.split('href="/torrent')[1].split('">')[1].split('</a>')[0]
				result.size = test.split('align="right">')[1].split('</td>')[0]
				if 'alt="C"' in result.size:
					result.size = test.split('align="right">')[2].split('</td>')[0]
				result.size = core.normalize(result.size)
				result.seeds = test.split('arrowup.gif"')[1].split('/>')[1].split('</span>')[0].replace('&nbsp;','')
				#print('hash', result.hash)
				#print('title', result.title)
				#print('size', result.size)
				#print('seeds', result.seeds)

				results.append(result)

		return results



	"""
	def _title_filter(self, el):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		return core.re.findall(r'<tv:raw_title>(.*?)</tv:raw_title>', str(el))[0]

	def _info(self, el, url, torrent):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		torrent['magnet'] = core.re.findall(r'"(magnet:\?.*?)"', str(el))[0]

		return torrent
	"""

	def movie(self, title, year, imdb=None, **kwargs):
		#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		self._imdb = imdb
		return super(sources, self).movie(title, year, imdb, auto_query=True)

	def episode(self, simple_info, all_info, **kwargs):
		#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		self._imdb = all_info.get('info', {}).get('tvshow.imdb_id', None)
		self._single_query = False
		simple_info['is_airing'] = False
		if self._imdb is None:
			self._imdb = all_info.get('showInfo', {}).get('ids', {}).get('imdb', None)
		return super(sources, self).episode(simple_info, all_info, single_query=False, auto_query=True, query_seasons=True, query_show_packs=True)


"""
class sources(core.DefaultSources):
	def __init__(self, *args, **kwargs):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		super(sources, self).__init__(__name__,
									 *args,
									 request=core.Request(sequental=True, wait=0.4),
									 **kwargs)
		self._imdb = None

	def _search_request(self, url, query, force_token_refresh=False, too_many_requests_max_retries=2, no_results_max_retries=2):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		token = core.database.get(self._get_token, 0 if force_token_refresh else 1, url)

		if token is None:
			return []

		search = url.search
		if self._imdb is not None:
			search = search.replace('search_string=', 'search_imdb=')
			original_query = query
			query = self._imdb

			if not self.is_movie_query():
				if self.scraper.show_title_fallback is not None and self.scraper.show_title_fallback in query:
					search_string = original_query[len(self.scraper.show_title_fallback):]
				else:
					search_string = original_query[len(self.scraper.show_title):]

				if len(search_string.strip()) == 0:
				  return []

				search += '&search_string=%s' % core.quote_plus(search_string.strip())

		search_url = url.base + search % (core.quote_plus(query), token)
		response = self._request.get(search_url)

		if response.status_code != 200:
			core.tools.log('No response from %s' % search_url, 'notice')
			return []

		response = core.json.loads(response.text)

		if 'error_code' in response:
			error_code = response['error_code']

			# unauthenticated/expired
			if error_code == 1 or error_code == 2:
				return self._search_request(url, original_query, force_token_refresh=True)
			# too many requests per second
			elif error_code == 5 and too_many_requests_max_retries > 0:
				core.time.sleep(2)
				core.tools.log('Retrying after too many requests error from %s' % search_url, 'info')
				too_many_requests_max_retries -= 1
				return self._search_request(url, original_query, force_token_refresh, too_many_requests_max_retries, no_results_max_retries)
			# no results found
			elif core.DEV_MODE and error_code == 20 and no_results_max_retries > 0:
				core.time.sleep(25)
				core.tools.log('Retrying after no results from %s' % search_url, 'info')
				no_results_max_retries -= 1
				return self._search_request(url, original_query, force_token_refresh, too_many_requests_max_retries, no_results_max_retries)

			core.tools.log('Error response from %s: %s' % (search_url, core.json.dumps(response)), 'info')
			return []

		else:
			return response['torrent_results']

	def _soup_filter(self, response):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		return response

	def _title_filter(self, el):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		return el['title']

	def _info(self, el, url, torrent):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		torrent['magnet'] = el['download']

		try: torrent['size'] = int((el['size'] / 1024) / 1024)
		except: pass

		torrent['seeds'] = el['seeders']

		return torrent

	def _get_scraper(self, title):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		filter_fn = lambda t, clean_t: self._imdb is not None and self.is_movie_query()
		custom_filter = core.Filter(fn=filter_fn, type='single')
		return super(sources, self)._get_scraper(title, custom_filter=None, use_thread_for_info=False)

	def movie(self, title, year, imdb=None, **kwargs):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		self._imdb = imdb
		return super(sources, self).movie(title, year, imdb, auto_query=False)

	def episode(self, simple_info, all_info, **kwargs):
		print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		self._imdb = all_info.get('info', {}).get('tvshow.imdb_id', None)
		if self._imdb is None:
			self._imdb = all_info.get('showInfo', {}).get('ids', {}).get('imdb', None)
		return super(sources, self).episode(simple_info, all_info, query_show_packs=False)
"""