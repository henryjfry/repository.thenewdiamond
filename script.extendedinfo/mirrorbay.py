# -*- coding: utf-8 -*-

import inspect

from inspect import currentframe, getframeinfo
#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

"""
        "mirrorbay": {
            "search": "/get-data-for/%s",
            "cat_movie": "207,202,201",
            "cat_episode": "208,205",
            "domains": [
                {
                    "base": "https://mirrorbay.org"
                }
            ]
        },
"""


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

		request_url = url.base + (url.search % core.quote_plus(query))
		response = self._request.get(request_url)

		#print(response.text)

		if response.status_code != 200:
			return []

		##response = core.normalize(response.text)
		print(request_url)

		return response


	def _soup_filter(self, response):
		#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		#response_list = core.beautifulSoup(response).find_all(class_='gai')
		#print(response.text)
		response_list = response.text.split('list-item item-type')

		results = []
		for item in response_list:
			result = lambda: None
			test = item
			if 'urn:btih:' in str(test):
				result.hash = test.split('urn:btih:')[1].replace('&amp;','&').split('&dn')[0]
				result.title = test.split('item-title"')[1].split('">')[1].split('</a>')[0]
				result.size = test.split('item-size">')[1].split('</')[0]
				result.size = core.normalize(result.size)
				result.seeds = 1
				#print('hash', result.hash)
				#print('title', result.title)
				#print('size', result.size)
				#print('seeds', result.seeds)
			results.append(result)

		return results



	def movie(self, title, year, imdb=None, **kwargs):
		##print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		self._imdb = imdb
		return super(sources, self).movie(title, year, imdb, auto_query=True)

	def episode(self, simple_info, all_info, **kwargs):
		##print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		self._imdb = all_info.get('info', {}).get('tvshow.imdb_id', None)
		self._single_query = False
		simple_info['is_airing'] = False
		if self._imdb is None:
			self._imdb = all_info.get('showInfo', {}).get('ids', {}).get('imdb', None)
		return super(sources, self).episode(simple_info, all_info, single_query=False, auto_query=True, query_seasons=True, query_show_packs=True)


