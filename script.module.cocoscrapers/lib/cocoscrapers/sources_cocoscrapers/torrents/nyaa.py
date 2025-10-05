# -*- coding: utf-8 -*-
# created by Venom for Fenomscrapers (updated 6-19-2022)
"""
	Fenomscrapers Project
"""

import re
from urllib.parse import quote_plus, unquote_plus
from cocoscrapers.modules import cleantitle
from cocoscrapers.modules import client
from cocoscrapers.modules import source_utils
from cocoscrapers.modules import log_utils
from time import time

class source:
	priority = 5
	pack_capable = False
	hasMovies = True
	hasEpisodes = True
	def __init__(self):
		self.language = ['en']
		self.base_link = "https://nyaa.si"
		self.search_link = '/?f=0&c=0_0&q=%s'
		self.item_totals = {
			'4K': 0,
			'1080p': 0,
			'720p': 0,
			'SD': 0,
			'CAM': 0 
			}
		self.min_seeders = 1

	def sources(self, data, hostDict):
		sources = []
		if not data: return sources
		append = sources.append
		try:
			startTime = time()
			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
			aliases = data['aliases']
			year = data['year']
			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else year
			hdlr2 = 'S%d - %d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else year

			query = '%s %s' % (re.sub(r'[^A-Za-z0-9\s\.-]+', '', title), hdlr)
			query2 = '%s %s' % (re.sub(r'[^A-Za-z0-9\s\.-]+', '', title), hdlr2)
			urls = []
			url = self.search_link % quote_plus(query)
			url = '%s%s' % (self.base_link, url)
			urls.append(url)
			url2 = self.search_link % quote_plus(query2)
			url2 = '%s%s' % (self.base_link, url2)
			urls.append(url2)
			# log_utils.log('urls = %s' % urls)
			undesirables = source_utils.get_undesirables()
			check_foreign_audio = source_utils.check_foreign_audio()
		except:
			source_utils.scraper_error('NYYAA')
			return sources

		for url in urls:
			try:
				results = client.request(url, timeout=5)
				if not results or 'magnet:' not in results: return sources
				results = re.sub(r'[\n\t]', '', results)
				tbody = client.parseDOM(results, 'tbody')
				rows = client.parseDOM(tbody, 'tr')

				for row in rows:
					links = zip(
									re.findall(r'href\s*=\s*["\'](magnet:[^"\']+)["\']', row, re.DOTALL | re.I),
									re.findall(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', row, re.DOTALL),
									[re.findall(r'<td class\s*=\s*["\']text-center["\']>([0-9]+)</td>', row, re.DOTALL)])
					for link in links:
						url = unquote_plus(link[0]).replace('&amp;', '&').split('&tr')[0].replace(' ', '.')
						url = source_utils.strip_non_ascii_and_unprintable(url)
						hash = re.search(r'btih:(.*?)&', url, re.I).group(1)
						name = source_utils.clean_name(url.split('&dn=')[1])

						if hdlr not in name and hdlr2 not in name: continue
						if source_utils.remove_lang(name, check_foreign_audio): continue
						# if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

						if hdlr in name:
							t = name.split(hdlr)[0].replace(year, '').replace('(', '').replace(')', '').replace('&', 'and').replace('.US.', '.').replace('.us.', '.')
						if hdlr2 in name:
							t = name.split(hdlr2)[0].replace(year, '').replace('(', '').replace(')', '').replace('&', 'and').replace('.US.', '.').replace('.us.', '.')
						# if cleantitle.get(t) != cleantitle.get(title): continue # Anime title matching is a bitch!
						try:
							seeders = int(link[2][0])
							if self.min_seeders > seeders: continue
						except: seeders = 0

						quality, info = source_utils.get_release_quality(name, url)
						try:
							size = link[1]
							dsize, isize = source_utils._size(size)
							info.insert(0, isize)
						except: dsize = 0
						info = ' | '.join(info)

						append({'provider': 'nyaa', 'source': 'torrent', 'seeders': seeders, 'hash': hash, 'name': name, 'quality': quality,
										'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
						self.item_totals[quality]+=1
			except:
				source_utils.scraper_error('NYAA')
				return sources
		logged = False
		for quality in self.item_totals:
			if self.item_totals[quality] > 0:
				log_utils.log('#STATS - NYAA found {0:2.0f} {1}'.format(self.item_totals[quality],quality) )
				logged = True
		if not logged: log_utils.log('#STATS - NYAA found nothing')
		endTime = time()
		log_utils.log('#STATS - NYAA took %.2f seconds' % (endTime - startTime))
		return sources