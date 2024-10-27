# -*- coding: utf-8 -*-

import random
import re
import inspect
import os
import unicodedata
import string
import sys

import hashlib
try:
	import tools, distance
except:
	from a4kscrapers_wrapper import tools, distance
import time



from requests import Session

from inspect import currentframe, getframeinfo
#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

current_directory = str(getframeinfo(currentframe()).filename.replace(os.path.basename(getframeinfo(currentframe()).filename),'').replace('','')[:-1])
sys.path.append(current_directory)
sys.path.append(current_directory.replace('a4kscrapers_wrapper',''))

try:
	import dateutil, babelfish, rebulk, guessit
	from guessit import api
except:
	from a4kscrapers_wrapper import dateutil, babelfish, rebulk, guessit, pkg_resources
	from a4kscrapers_wrapper.guessit import api

USER_AGENTS = [
	"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36"
]

exclusions = ['soundtrack', 'gesproken', 'sample', 'trailer', 'extras only', 'ost']
release_groups_blacklist = ['lostfilm', 'coldfilm', 'newstudio', 'hamsterstudio', 'jaskier', 'ideafilm', 'lakefilms', 'gears media', 'profix media', 'baibako', 'alexfilm', 'kerob', 'omskbird', 'kb 1080p', 'tvshows', '400p octopus', '720p octopus', '1080p octopus', 'dilnix']
adult_movie_tags = ['porn', 'xxx', 'adult', 'nude', 'ass', 'anal', 'threesome', 'blowjob', 'sex', 'fuck', 'squirt', 'hardcore', 'dick', 'cock', 'cum', 'orgasm', 'pussy']
country_codes = {'afghanistan':'af','albania':'al','algeria':'dz','american samoa':'as','andorra':'ad','angola':'ao','anguilla':'ai','antarctica':'aq','antigua and barbuda':'ag','argentina':'ar','armenia':'am','aruba':'aw','australia':'au','austria':'at','azerbaijan':'az','bahamas':'bs','bahrain':'bh','bangladesh':'bd','barbados':'bb','belarus':'by','belgium':'be','belize':'bz','benin':'bj','bermuda':'bm','bhutan':'bt','bolivia, plurinational state of':'bo','bonaire, sint eustatius and saba':'bq','bosnia and herzegovina':'ba','botswana':'bw','bouvet island':'bv','brazil':'br','british indian ocean territory':'io','brunei darussalam':'bn','bulgaria':'bg','burkina faso':'bf','burundi':'bi','cambodia':'kh','cameroon':'cm','canada':'ca','cape verde':'cv','cayman islands':'ky','central african republic':'cf','chad':'td','chile':'cl','china':'cn','christmas island':'cx','cocos (keeling) islands':'cc','colombia':'co','comoros':'km','congo':'cg','congo, the democratic republic of the':'cd','cook islands':'ck','costa rica':'cr','country name':'code','croatia':'hr','cuba':'cu','curaçao':'cw','cyprus':'cy','czech republic':'cz','côte d\'ivoire':'ci','denmark':'dk','djibouti':'dj','dominica':'dm','dominican republic':'do','ecuador':'ec','egypt':'eg','el salvador':'sv','equatorial guinea':'gq','eritrea':'er','estonia':'ee','ethiopia':'et','falkland islands (malvinas)':'fk','faroe islands':'fo','fiji':'fj','finland':'fi','france':'fr','french guiana':'gf','french polynesia':'pf','french southern territories':'tf','gabon':'ga','gambia':'gm','georgia':'ge','germany':'de','ghana':'gh','gibraltar':'gi','greece':'gr','greenland':'gl','grenada':'gd','guadeloupe':'gp','guam':'gu','guatemala':'gt','guernsey':'gg','guinea':'gn','guinea-bissau':'gw','guyana':'gy','haiti':'ht','heard island and mcdonald islands':'hm','holy see (vatican city state)':'va','honduras':'hn','hong kong':'hk','hungary':'hu','iso 3166-2:gb':'(.uk)','iceland':'is','india':'in','indonesia':'id','iran, islamic republic of':'ir','iraq':'iq','ireland':'ie','isle of man':'im','israel':'il','italy':'it','jamaica':'jm','japan':'jp','jersey':'je','jordan':'jo','kazakhstan':'kz','kenya':'ke','kiribati':'ki','korea, democratic people\'s republic of':'kp','korea, republic of':'kr','kuwait':'kw','kyrgyzstan':'kg','lao people\'s democratic republic':'la','latvia':'lv','lebanon':'lb','lesotho':'ls','liberia':'lr','libya':'ly','liechtenstein':'li','lithuania':'lt','luxembourg':'lu','macao':'mo','macedonia, the former yugoslav republic of':'mk','madagascar':'mg','malawi':'mw','malaysia':'my','maldives':'mv','mali':'ml','malta':'mt','marshall islands':'mh','martinique':'mq','mauritania':'mr','mauritius':'mu','mayotte':'yt','mexico':'mx','micronesia, federated states of':'fm','moldova, republic of':'md','monaco':'mc','mongolia':'mn','montenegro':'me','montserrat':'ms','morocco':'ma','mozambique':'mz','myanmar':'mm','namibia':'na','nauru':'nr','nepal':'np','netherlands':'nl','new caledonia':'nc','new zealand':'nz','nicaragua':'ni','niger':'ne','nigeria':'ng','niue':'nu','norfolk island':'nf','northern mariana islands':'mp','norway':'no','oman':'om','pakistan':'pk','palau':'pw','palestine, state of':'ps','panama':'pa','papua new guinea':'pg','paraguay':'py','peru':'pe','philippines':'ph','pitcairn':'pn','poland':'pl','portugal':'pt','puerto rico':'pr','qatar':'qa','romania':'ro','russian federation':'ru','rwanda':'rw','réunion':'re','saint barthélemy':'bl','saint helena, ascension and tristan da cunha':'sh','saint kitts and nevis':'kn','saint lucia':'lc','saint martin (french part)':'mf','saint pierre and miquelon':'pm','saint vincent and the grenadines':'vc','samoa':'ws','san marino':'sm','sao tome and principe':'st','saudi arabia':'sa','senegal':'sn','serbia':'rs','seychelles':'sc','sierra leone':'sl','singapore':'sg','sint maarten (dutch part)':'sx','slovakia':'sk','slovenia':'si','solomon islands':'sb','somalia':'so','south africa':'za','south georgia and the south sandwich islands':'gs','south sudan':'ss','spain':'es','sri lanka':'lk','sudan':'sd','suriname':'sr','svalbard and jan mayen':'sj','swaziland':'sz','sweden':'se','switzerland':'ch','syrian arab republic':'sy','taiwan, province of china':'tw','tajikistan':'tj','tanzania, united republic of':'tz','thailand':'th','timor-leste':'tl','togo':'tg','tokelau':'tk','tonga':'to','trinidad and tobago':'tt','tunisia':'tn','turkey':'tr','turkmenistan':'tm','turks and caicos islands':'tc','tuvalu':'tv','uganda':'ug','ukraine':'ua','united arab emirates':'ae','united kingdom':'gb','united states':'us','united states minor outlying islands':'um','uruguay':'uy','uzbekistan':'uz','vanuatu':'vu','venezuela, bolivarian republic of':'ve','viet nam':'vn','virgin islands, british':'vg','virgin islands, u.s.':'vi','wallis and futuna':'wf','western sahara':'eh','yemen':'ye','zambia':'zm','zimbabwe':'zw','åland islands':'ax'}

class Filter(object):
	def __init__(self, fn, type):
		self.fn = fn
		self.type = type

def de_string_size(size):
	try:
		if isinstance(size, int):
			return size
		if 'GB' in size or 'GiB' in size:
			size = float(size.replace('GB', ''))
			size = int(size * 1024)
			return size
		if 'MB' in size or 'MiB' in size:
			size = int(size.replace('MB', '').replace(',', '').replace(' ', '').split('.')[0])
			return size
		if 'B' in size:
			size = int(size.replace('B', ''))
			size = int(size / 1024 / 1024)
			return size
	except:
		return 0

def get_quality(release_title):
	release_title = release_title.lower()
	quality = 'SD'
	if ' 4k' in release_title:
		quality = '4K'
	if '2160p' in release_title:
		quality = '4K'
	if '1080p' in release_title:
		quality = '1080p'
	if ' 1080 ' in release_title:
		quality = '1080p'
	if ' 720 ' in release_title:
		quality = '720p'
	if ' hd ' in release_title:
		quality = '720p'
	if '720p' in release_title:
		quality = '720p'
	if 'cam' in release_title:
		quality = 'CAM'

	if quality == '4K' and '264' in release_title:
		quality = '1080p'

	return quality

def strip_non_ascii_and_unprintable(text):
	result = ''.join(char for char in text if char in string.printable)
	return result.encode('ascii', errors='ignore').decode('ascii', errors='ignore')

def strip_accents(s):
	try:
		return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
	except:
		return s

def clean_title(title, broken=None):
	title = title.lower()
	title = strip_accents(title)
	title = strip_non_ascii_and_unprintable(title)

	if broken == 1:
		apostrophe_replacement = ''
	elif broken == 2:
		apostrophe_replacement = ' s'
	else:
		apostrophe_replacement = 's'

	title = title.replace("\\'s", apostrophe_replacement)
	title = title.replace("'s", apostrophe_replacement)
	title = title.replace("&#039;s", apostrophe_replacement)
	title = title.replace(" 039 s", apostrophe_replacement)
	title = title.replace(':',' ')

	title = re.sub(r'\'|\’', '', title)
	title = re.sub(r'\:|\\|\/|\,|\!|\?|\(|\)|\"|\+|\[|\]|\-|\_|\.|\{|\}', ' ', title)
	title = re.sub(r'\s+', ' ', title)
	title = re.sub(r'\&', 'and', title)

	return title.strip()

def clean_tags(title):
	try:
		title = title.lower()

		if title[0] == '[':
			title = title[title.find(']')+1:].strip()
			return clean_tags(title)
		if title[0] == '(':
			title = title[title.find(')')+1:].strip()
			return clean_tags(title)
		if title[0] == '{':
			title = title[title.find('}')+1:].strip()
			return clean_tags(title)

		title = re.sub(r'\(|\)|\[|\]|\{|\}', ' ', title)
		title = re.sub(r'\s+', ' ', title)
	except:
		pass

	return title

def clean_year_range(title, year):
	title = re.sub(r'(?:\(|\[\{)\s*' + re.escape(year) + r'(?:\s|-)\d{' + str(len(year)) + r'}(?:\)|\]\})', ' ', title)
	return re.sub(r'\s+', ' ', title)

def remove_sep(release_title, title):
	def check_for_sep(t, sep, check_count=False):
		if check_count and t.count(sep) > 1:
			return t
		if sep in t and t[t.find(sep)+1:].strip().lower().startswith(title):
			return t[t.find(sep)+1:].strip()
		return t

	release_title = check_for_sep(release_title, '/')
	release_title = check_for_sep(release_title, '-',  True)

	return release_title

def remove_from_title(title, target, clean=True):
	if target == '':
		return title

	title = title.replace(' %s ' % target.lower(), ' ')
	title = title.replace('.%s.' % target.lower(), ' ')
	title = title.replace('+%s+' % target.lower(), ' ')
	title = title.replace('-%s-' % target.lower(), ' ')
	if clean:
		title = clean_title(title) + ' '
	else:
		title = title + ' '

	return re.sub(r'\s+', ' ', title)

def remove_country(title, country, clean=True):
	if isinstance(country, list):
		for c in country:
			title = remove_country(title, c, clean)
		return title

	title = title.lower()
	country = country.lower()
	if country_codes.get(country, None):
		country = country_codes[country]

	if country in ['gb', 'uk']:
		title = remove_from_title(title, 'gb', clean)
		title = remove_from_title(title, 'uk', clean)
	else:
		title = remove_from_title(title, country, clean)

	return title

def clean_title_with_simple_info(title, simple_info):
	title = clean_title(title) + ' '
	country = simple_info.get('country', '')
	title = remove_country(title, country)
	year = simple_info.get('year', '')
	title = remove_from_title(title, year)
	return re.sub(r'\s+', ' ', title)

def encode_text_py2(text):
	if sys.version_info[0] < 3:
		try:
			text = text.encode('utf8')
		except:
			try:
				text = text.encode('ascii')
			except:
				pass
	return text

def decode_text_py2(text):
	if sys.version_info[0] < 3:
		try:
			text = text.decode('utf8')
		except:
			try:
				text = text.decode('ascii')
			except:
				pass
	return text

def clean_release_title_with_simple_info(title, simple_info, remove_complete=True):
	title = title.split('/')[-1]
	title = encode_text_py2(title)

	title = (title.lower()
				  .replace('&ndash;', '-')
				  .replace('–', '-'))

	title = decode_text_py2(title)
	title = strip_non_ascii_and_unprintable(title)

	year = simple_info.get('year', '')
	title = clean_year_range(title, year) + ' '
	title = clean_tags(title) + ' '
	country = simple_info.get('country', '')
	title = remove_country(title, country, False)
	title = remove_sep(title, simple_info['query_title'])
	title = clean_title(title) + ' '

	for group in release_groups_blacklist:
		target = ' %s ' % group
		if target not in (simple_info['query_title'] + ' ') and target in (title + ' '):
			return ''

	if simple_info.get('show_title', None) is None:
		for target in adult_movie_tags:
			if target not in (simple_info['query_title'] + ' ') and target in (title + ' '):
				return ''
	else:
		title = remove_from_title(title, year)

	title = remove_from_title(title, get_quality(title), False)
	if remove_complete:
		title = (title.replace(' tv series ', ' ')
					  .replace(' the completed ', ' ')
					  .replace(' completed ', ' ')
					  .replace(' the complete ', ' ')
					  .replace(' complete ', ' ')
					  .replace(' dvdrip ', ' ')
					  .replace(' bdrip ', ' '))
	else:
		title = (title.replace(' completed ', ' ')
					  .replace(' the completed ', ' ')
					  .replace(' dvdrip ', ' ')
					  .replace(' bdrip ', ' '))

	return re.sub(r'\s+', ' ', title) + ' '

def get_regex_pattern(titles, suffixes_list):
	pattern = r'^(?:'
	for title in titles:
		title = title.strip()
		if len(title) > 0:
			pattern += re.escape(title) + r' |'
	pattern = pattern[:-1] + r')+(?:'
	for suffix in suffixes_list:
		suffix = suffix.strip()
		if len(suffix) > 0:
			pattern += re.escape(suffix) + r' |'
	pattern = pattern[:-1] + r')+'
	regex_pattern = re.compile(pattern)
	return regex_pattern

def check_title_match(title_parts, release_title, simple_info, is_special=False):
	title = clean_title(' '.join(title_parts)) + ' '

	country = simple_info.get('country', '')
	year = simple_info.get('year', '')
	title = remove_country(title, country)
	title = remove_from_title(title, year)

	if simple_info['imdb_id'] is None:
		return release_title.startswith(title + year)
	else:
		return release_title.startswith(title)

def check_episode_number_match(release_title):
	episode_number_match = re.search(r'[+|-|_|.| ]s\d{1,3}[+|-|_|.| ]?e\d{1,3}[+|-|_|.| ]', release_title, re.IGNORECASE)
	if episode_number_match:
		return True

	episode_number_match = re.search(r'[+|-|_|.| ]season[+|-|_|.| ]\d+[+|-|_|.| ]episode[+|-|_|.| ]\d+', release_title, re.IGNORECASE)
	if episode_number_match:
		return True

	return False

def check_episode_title_match(titles, release_title, simple_info):
	if simple_info.get('episode_title', None) is not None:
		episode_title = clean_title(simple_info['episode_title'])

		if len(episode_title.split(' ')) >= 3 and ((episode_title in release_title) or (episode_title.lower() in release_title)):
			for title in titles:
				if episode_title in title:
					return False

			for title in titles:
				if release_title.startswith(title):
					return True
		sum_match = 0
		tot = 0
		for i in episode_title.split(' '):
			if len(i) > 3:
				if str(i + ' ') in release_title or str(' ' + i) in release_title:
					sum_match = sum_match + 1
				tot = tot + 1
			if len(i) > 1:
				if str(i + ' ') in release_title or str(' ' + i) in release_title:
					sum_match = sum_match + 0.5
				tot = tot + 0.5
		if sum_match >= tot - 1 and tot > 2:
			return True
	return False

def filter_movie_title(org_release_title, release_title, movie_title, simple_info):
	if simple_info['imdb_id'] is None and org_release_title is not None and simple_info['year'] not in org_release_title:
		if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
			tools.log('movienoyear]: %s' % release_title, 'notice')
		return False

	if org_release_title is not None and check_episode_number_match(org_release_title):
		if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
			tools.log('movieepisode]: %s' % release_title, 'notice')
		return False

	if any((' %s ' % i) in release_title for i in exclusions):
		if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
			tools.log('movieexcluded]: %s' % release_title, 'notice')
		return False

	title = clean_title(movie_title)

	if 'season' in release_title and 'season' not in title:
		if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
			tools.log('movietvshow]: %s' % release_title, 'notice')
		return False

	if 'trailer' in release_title and 'trailer' not in title:
		if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
			tools.log('movietvshow]: %s' % release_title, 'notice')
		return False

	if 'featurette' in release_title and 'featurette' not in title:
		if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
			tools.log('movietvshow]: %s' % release_title, 'notice')
		return False

	if 'sample' in release_title and 'sample' not in title:
		if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
			tools.log('movietvshow]: %s' % release_title, 'notice')
		return False

	title_broken_1 = clean_title(movie_title, broken=1)
	title_broken_2 = clean_title(movie_title, broken=2)

	if not check_title_match([title], release_title, simple_info) and not check_title_match([title_broken_1], release_title, simple_info) and not check_title_match([title_broken_2], release_title, simple_info):
		if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
			tools.log('movie]: %s' % release_title, 'notice')
		return False

	return True

def multi_parts_check(simple_info, release_title=None):
	ep_number = int(simple_info['episode_number'])
	multi_dict = tools.episodes_parts_lists_multi(ep_number,ep_number+1)
	part_number_title = []
	for i in multi_dict:
		idx = i
		for x in multi_dict[i]:
			#print(x)
			if str(x).lower() in simple_info['episode_title'].lower():
				part_number_title.append(str(idx)+'+'+str(int(idx)+1))
	part_number_release = []
	for i in multi_dict:
		idx = i
		for x in multi_dict[i]:
			#print(x)
			if str(x).lower() in release_title.lower():
				part_number_release.append(str(idx)+'+'+str(int(idx)+1))
	return part_number_title, part_number_release


def parts_check(simple_info, release_title=None):
	parts_roman, parts_numbers, parts_words, parts_numbers2 = tools.episodes_parts_lists()
	episode_title = clean_title(simple_info['episode_title'])
	part_number_title = []
	part_match_title = []
	for idx, i in enumerate(parts_roman):
		if str(parts_roman[idx]).lower() in simple_info['episode_title'].lower():
			part_number_title.append(idx + 1)
			part_match_title.append(parts_roman[idx])
		elif str(parts_numbers[idx]).lower() in simple_info['episode_title'].lower():
			part_number_title.append(idx + 1)
			part_match_title.append(parts_numbers[idx])
		elif str(parts_words[idx]).lower() in simple_info['episode_title'].lower():
			part_number_title.append(idx + 1)
			part_match_title.append(parts_words[idx])
		elif str(parts_numbers2[idx]).lower() in simple_info['episode_title'].lower():
			part_number_title.append(idx + 1)
			part_match_title.append(parts_numbers2[idx])
	part_number_release = []
	part_match_release = []
	for idx, i in enumerate(parts_roman):
		if str(parts_roman[idx]).lower() in release_title.lower():
			part_number_release.append(idx + 1)
			part_match_release.append(parts_roman[idx])
		elif str(parts_numbers[idx]).lower() in release_title.lower():
			part_number_release.append(idx + 1)
			part_match_release.append(parts_numbers[idx])
		elif str(parts_words[idx]).lower() in release_title.lower():
			part_number_release.append(idx + 1)
			part_match_release.append(parts_words[idx])
		elif str(parts_numbers2[idx]).lower() in release_title.lower():
			part_number_release.append(idx + 1)
			part_match_release.append(parts_numbers2[idx])
	return part_number_title, part_number_release, part_match_title, part_match_release

def get_guess(release_title, options=None):
	guess = api.guessit(release_title, options)
	return guess

def run_show_filters(simple_info, pack_title=None, release_title=None, guess=False):


	if pack_title:
		simple_info['query_title'] = pack_title
		simple_info['clean_pack'] = clean_release_title_with_simple_info(pack_title, simple_info, remove_complete=False)
		show_title_match = check_show_title(simple_info, pack_title)
		if show_title_match == False:
			result_dict = {}
			result_dict['pack_title'] = False
			return result_dict
	if release_title:
		simple_info['query_title'] = release_title
		simple_info['clean_release'] = clean_release_title_with_simple_info(release_title, simple_info)
		simple_info2 = simple_info
		simple_info2['clean_release'] = clean_release_title_with_simple_info(release_title, simple_info, remove_complete=False)
		show_title_match = check_show_title(simple_info, release_title)
		show_title_match2 = check_show_title(simple_info2, release_title)

		if show_title_match == False and show_title_match2 == False:

			result_dict = {}
			result_dict['pack_title'] = False
			return result_dict
	
	result_dict = {}
	result_dict['pack_title'] = pack_title
	result_dict['release_title'] = release_title
	result_dict['part_number_title'] = None
	result_dict['part_number_release'] = None
	result_dict['alternate_title'] = []
	if release_title:

		#part_number_title, part_number_release, part_match_title, part_match_release = parts_check(simple_info, simple_info['query_title'])
		#result_dict['part_number_title'] = part_number_title
		#result_dict['part_number_release'] = part_number_release
		#result_dict['part_match_title'] = part_match_title
		#result_dict['part_match_release'] = part_match_release
		#multi_part_number_title, multi_part_number_release = multi_parts_check(simple_info, simple_info['query_title'])
		#result_dict['multi_part_number_title'] = multi_part_number_title
		#result_dict['multi_part_number_release'] = multi_part_number_release

		#if len(part_number_title)>0 and len(part_number_release)==0:
		#	simple_info2 = simple_info
		#	for i in part_match_title:
		#		simple_info2['episode_title'] = simple_info['episode_title'].replace(i,'')

		filter_fn = get_filter_single_episode_fn(simple_info)
		result_dict['get_filter_single_episode_fn'] = filter_fn(simple_info['clean_release'])
		if simple_info['episode_title'][:4].isnumeric():
			if simple_info['episode_title'][:10] in release_title:
				result_dict['get_filter_single_episode_fn'] = True
			elif simple_info['episode_title'][:4] in simple_info['clean_release'] and simple_info['episode_title'][5:7] in simple_info['clean_release'] and simple_info['episode_title'][8:10] in simple_info['clean_release']:
				result_dict['get_filter_single_episode_fn'] = True
		result_dict['filter_single_special_episode'] = filter_single_special_episode(simple_info, simple_info['clean_release'])
		filter_fn = get_filter_single_absolute_episode_fn(simple_info)
		result_dict['get_filter_single_absolute_episode_fn'] = filter_fn(simple_info['clean_release'])
		result_dict['filter_check_episode_title_match'] = filter_check_episode_title_match(simple_info, simple_info['clean_release'])

		#tools.log(result_dict,simple_info)
		#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		if not ': True' in str(result_dict):

			if simple_info['episode_number'] == None or simple_info['episode_number'] == 'None':
				simple_info['episode_number'] = '0'
			guess = get_guess(release_title)
			#guess = api.guessit(release_title)
			guess_season = guess.get('season', -1)
			guess_episode = []
			guess_title = guess.get('title')
			
			if guess.get('episode', None) == None:
				
				return result_dict
			if not 'int' in  str(type(guess.get('episode'))):
				
				for x in guess.get('episode'):
					guess_episode.append(x)
			else:

				guess_episode.append(guess.get('episode'))
			if guess_season == int(simple_info['season_number']):
				for i in guess_episode:
					if i == int(simple_info['episode_number']):
						result_dict['get_filter_single_episode_fn'] = True
		if ': True' in str(result_dict):
			guess = get_guess(release_title)
			guess_title = guess.get('title')
			show_title = simple_info['show_title']
			distance_apart = distance.jaro_similarity(show_title.lower(),guess_title.lower())
			#tools.log(guess, distance_apart)
			if distance_apart < 0.925:
				for i in result_dict:
						if result_dict[i] == True:
							result_dict[i] = False
			guess_episode_title = guess.get('episode_title', '')
			show_episode_title = simple_info['episode_title']
			guess_part = guess.get('part', '')
			guess_season = guess.get('season', -1)
			guess_episode = []
			if guess.get('episode', None) == None:
				return result_dict
			if not 'int' in  str(type(guess.get('episode'))):
				for x in guess.get('episode'):
					guess_episode.append(x)
			else:
				guess_episode.append(guess.get('episode'))
			if guess_episode_title != '':
				distance_apart = distance.jaro_similarity(show_episode_title.lower(),guess_episode_title.lower())
				if distance_apart < 0.925:
					if guess_season == int(simple_info['season_number']):
						for i in guess_episode:
							if i == int(simple_info['episode_number']):
								result_dict['get_filter_single_episode_fn'] = True
								return result_dict
					for i in result_dict:
							if result_dict[i] == True:
								result_dict[i] = False
				if distance_apart > 0.925:
					ep_num_match = False
					if guess_season == int(simple_info['season_number']):
						for i in guess_episode:
							if i == int(simple_info['episode_number']):
								ep_num_match = True
								
						if ep_num_match == False and len(guess_episode) > 0 and guess_part == '':
							for i in result_dict:
									if result_dict[i] == True:
										result_dict[i] = False
							return result_dict
			if guess_part != '':
				if result_dict['filter_check_episode_title_match'] == True or result_dict['filter_single_special_episode'] == True or result_dict['get_filter_single_episode_fn'] == True:
					match = False
					for i in guess_episode:
						if guess_season == int(simple_info['season_number']) and i == int(simple_info['episode_number']):
							match = True
					if match == False:
						result_dict['filter_check_episode_title_match'] = False 
						result_dict['filter_single_special_episode'] = False 
						result_dict['get_filter_single_episode_fn'] = False

		#if len(part_number_title)>0 and len(part_number_release)>0:
		##	print(result_dict)
		#	for idx, i in enumerate(part_number_title):
		#		if part_number_title[idx] != part_number_release[idx]:
		#			for i in result_dict:
		#					if result_dict[i] == True:
		#						result_dict[i] = False
		#	for i in part_match_title:
		#		result_dict['alternate_title'].append(simple_info['episode_title'].replace(i,''))

		#if (len(part_number_title)>0 and len(multi_part_number_release)>0) or len(multi_part_number_release)>0:
		##	print(result_dict)
		#	for idx, i in enumerate(multi_part_number_release):
		#		if str(simple_info['episode_number']) in str(i):
		#			#result_dict['get_filter_single_episode_fn'] = True
		#			show_title_match = check_show_title(simple_info, release_title)
		#			if show_title_match:
		#				result_dict['get_filter_single_episode_fn'] = True


	if pack_title:
		filter_fn = get_filter_season_pack_fn(simple_info)
		result_dict['get_filter_season_pack_fn'] = filter_fn(simple_info['clean_pack'])
		filter_fn = get_filter_show_pack_fn(simple_info)
		result_dict['get_filter_show_pack_fn'] = filter_fn(simple_info['clean_pack'])

	result_dict['episode_number'] = simple_info['episode_number']
	
	#tools.log(result_dict,simple_info)
	return result_dict

def filter_check_episode_title_match(simple_info, release_title):
	show_title, season, episode, alias_list = \
		simple_info['show_title'], \
		simple_info['season_number'], \
		simple_info['episode_number'], \
		simple_info['show_aliases']

	titles = list(alias_list)
	titles.insert(0, show_title)
	clean_titles = []
	for title in titles:
		clean_titles.append(clean_title_with_simple_info(title, simple_info))
	if check_episode_title_match(clean_titles, release_title, simple_info):
		return True
	else:
		return False

def get_filter_single_episode_fn(simple_info):
	show_title, season, episode, alias_list = \
		simple_info['show_title'], \
		simple_info['season_number'], \
		simple_info['episode_number'], \
		simple_info['show_aliases']

	titles = list(alias_list)
	titles.insert(0, show_title)

	
	season_episode_check = 's%se%s' % (season, episode)
	season_episode_fill_check = 's%se%s' % (season, episode.zfill(2))
	season_episode_fill3_check = 's%se%s' % (season, episode.zfill(3))

	season_fill_episode_check = 's%se%s' % (season.zfill(2), episode)
	season_fill3_episode_check = 's%se%s' % (season.zfill(3), episode)

	season_fill_episode_fill_check = 's%se%s' % (season.zfill(2), episode.zfill(2))
	season_fill3_episode_fill_check = 's%se%s' % (season.zfill(3), episode.zfill(2))

	season_fill_episode_fill3_check = 's%se%s' % (season.zfill(2), episode.zfill(3))
	season_fill3_episode_fill3_check = 's%se%s' % (season.zfill(3), episode.zfill(3))


	season_episode_full_check = 'season %s episode %s' % (season, episode)
	season_episode_fill_full_check = 'season %s episode %s' % (season, episode.zfill(2))
	season_episode_fill3_full_check = 'season %s episode %s' % (season, episode.zfill(3))

	season_fill_episode_full_check = 'season %s episode %s' % (season.zfill(2), episode)
	season_fill3_episode_full_check = 'season %s episode %s' % (season.zfill(3), episode)

	season_fill_episode_fill_full_check = 'season %s episode %s' % (season.zfill(2), episode.zfill(2))
	season_fill3_episode_fill_full_check = 'season %s episode %s' % (season.zfill(3), episode.zfill(2))

	season_fill_episode_fill3_full_check = 'season %s episode %s' % (season.zfill(2), episode.zfill(3))
	season_fill3_episode_fill3_full_check = 'season %s episode %s' % (season.zfill(3), episode.zfill(3))

	season_episode_ep_check = 's%sep%s' % (season, episode)
	season_episode_fill_ep_check = 's%sep%s' % (season, episode.zfill(2))
	season_episode_fill3_ep_check = 's%sep%s' % (season, episode.zfill(3))
	
	season_fill_episode_ep_check = 's%sep%s' % (season.zfill(2), episode)
	season_fill3_episode_ep_check = 's%sep%s' % (season.zfill(3), episode)

	season_fill_episode_fill_ep_check = 's%sep%s' % (season.zfill(2), episode.zfill(2))
	season_fill3_episode_fill_ep_check = 's%sep%s' % (season.zfill(3), episode.zfill(2))

	season_fill_episode_fill3_ep_check = 's%sep%s' % (season.zfill(2), episode.zfill(3))
	season_fill3_episode_fill3_ep_check = 's%sep%s' % (season.zfill(3), episode.zfill(3))
	

	season_episode_X_check = '%sx%s' % (season, episode)
	season_episode_fill_X_check = '%sx%s' % (season, episode.zfill(2))
	season_episode_fill3_X_check = '%sx%s' % (season, episode.zfill(3))

	season_fill_episode_X_check = '%sx%s' % (season.zfill(2), episode)
	season_fill3_episode_X_check = '%sx%s' % (season.zfill(3), episode)

	season_fill_episode_fill_X_check = '%sx%s' % (season.zfill(2), episode.zfill(2))
	season_fill3_episode_fill_X_check = '%sx%s' % (season.zfill(3), episode.zfill(2))

	season_fill_episode_fill3_X_check = '%sx%s' % (season.zfill(2), episode.zfill(3))
	season_fill3_episode_fill3_X_check = '%sx%s' % (season.zfill(3), episode.zfill(3))
	
	season_episode_space_dash_check = 's%s - %s' % (season, episode)
	season_episode_fill_space_dash_check = 's%s - %s' % (season, episode.zfill(2))
	season_episode_fill3_space_dash_check = 's%s - %s' % (season, episode.zfill(3))

	season_fill_episode_space_dash_check = 's%s - %s' % (season.zfill(2), episode)
	season_fill3_episode_space_dash_check = 's%s - %s' % (season.zfill(3), episode)

	season_fill_episode_fill_space_dash_check = 's%s - %s' % (season.zfill(2), episode.zfill(2))
	season_fill3_episode_fill_space_dash_check = 's%s - %s' % (season.zfill(3), episode.zfill(2))

	season_fill_episode_fill3_space_dash_check = 's%s - %s' % (season.zfill(2), episode.zfill(3))
	season_fill3_episode_fill3_space_dash_check = 's%s - %s' % (season.zfill(3), episode.zfill(3))

	season_episode_space_dash_e_check = 's%s - e%s' % (season, episode)
	season_episode_fill_space_dash_e_check = 's%s - e%s' % (season, episode.zfill(2))
	season_episode_fill3_space_dash_e_check = 's%s - e%s' % (season, episode.zfill(3))

	season_fill_episode_space_dash_e_check = 's%s - e%s' % (season.zfill(2), episode)
	season_fill3_episode_space_dash_e_check = 's%s - e%s' % (season.zfill(3), episode)

	season_fill_episode_fill_space_dash_e_check = 's%s - e%s' % (season.zfill(2), episode.zfill(2))
	season_fill3_episode_fill_space_dash_e_check = 's%s - e%s' % (season.zfill(3), episode.zfill(2))

	season_fill_episode_fill3_space_dash_e_check = 's%s - e%s' % (season.zfill(2), episode.zfill(3))
	season_fill3_episode_fill3_space_dash_e_check = 's%s - e%s' % (season.zfill(3), episode.zfill(3))
	"""
	season_episode_check = 's%se%s' % (season, episode)
	season_episode_fill_check = 's%se%s' % (season, episode.zfill(2))
	season_fill_episode_fill_check = 's%se%s' % (season.zfill(2), episode.zfill(2))
	season_episode_full_check = 'season %s episode %s' % (season, episode)
	season_episode_fill_full_check = 'season %s episode %s' % (season, episode.zfill(2))
	season_fill_episode_fill_full_check = 'season %s episode %s' % (season.zfill(2), episode.zfill(2))
	"""

	clean_titles = []
	for title in titles:
		clean_titles.append(clean_title_with_simple_info(title, simple_info))

	suffixes = [
		#season_episode_check,season_episode_fill_check,season_fill_episode_fill_check,season_episode_full_check,season_episode_fill_full_check,season_fill_episode_fill_full_check
		season_episode_check, 
		season_episode_fill_check, 
		season_episode_fill3_check, 
		season_fill_episode_check, 
		season_fill3_episode_check, 
		season_fill_episode_fill_check, 
		season_fill3_episode_fill_check, 
		season_fill_episode_fill3_check, 
		season_fill3_episode_fill3_check, 
		season_episode_full_check, 
		season_episode_fill_full_check, 
		season_episode_fill3_full_check, 
		season_fill_episode_full_check, 
		season_fill3_episode_full_check, 
		season_fill_episode_fill_full_check, 
		season_fill3_episode_fill_full_check, 
		season_fill_episode_fill3_full_check, 
		season_fill3_episode_fill3_full_check, 
		season_episode_ep_check, 
		season_episode_fill_ep_check, 
		season_episode_fill3_ep_check, 
		season_fill_episode_ep_check, 
		season_fill3_episode_ep_check, 
		season_fill_episode_fill_ep_check, 
		season_fill3_episode_fill_ep_check, 
		season_fill_episode_fill3_ep_check, 
		season_fill3_episode_fill3_ep_check, 
		season_episode_X_check, 
		season_episode_fill_X_check, 
		season_episode_fill3_X_check, 
		season_fill_episode_X_check, 
		season_fill3_episode_X_check, 
		season_fill_episode_fill_X_check, 
		season_fill3_episode_fill_X_check, 
		season_fill_episode_fill3_X_check, 
		season_fill3_episode_fill3_X_check, 
		season_episode_space_dash_check, 
		season_episode_fill_space_dash_check, 
		season_episode_fill3_space_dash_check, 
		season_fill_episode_space_dash_check, 
		season_fill3_episode_space_dash_check, 
		season_fill_episode_fill_space_dash_check, 
		season_fill3_episode_fill_space_dash_check, 
		season_fill_episode_fill3_space_dash_check, 
		season_fill3_episode_fill3_space_dash_check, 
		season_episode_space_dash_e_check, 
		season_episode_fill_space_dash_e_check, 
		season_episode_fill3_space_dash_e_check, 
		season_fill_episode_space_dash_e_check, 
		season_fill3_episode_space_dash_e_check, 
		season_fill_episode_fill_space_dash_e_check, 
		season_fill3_episode_fill_space_dash_e_check, 
		season_fill_episode_fill3_space_dash_e_check, 
		season_fill3_episode_fill3_space_dash_e_check, 
	]
	"""
	suffixes = [
		season_episode_check,
		season_episode_fill_check,
		season_fill_episode_fill_check,
		season_episode_full_check,
		season_episode_fill_full_check,
		season_fill_episode_fill_full_check
	]
	"""
	regex_pattern = get_regex_pattern(clean_titles, suffixes)
	
	def filter_fn(release_title):
		if re.match(regex_pattern, release_title):
			return True

		if check_episode_title_match(clean_titles, release_title, simple_info):
			return True

		if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
			tools.log('singleepisode]: %s' % release_title, 'notice')
		return False

	return filter_fn

def get_filter_single_absolute_episode_fn(simple_info):
	show_title, season, episode, alias_list = \
		simple_info['show_title'], \
		simple_info['season_number'], \
		simple_info['episode_number'], \
		simple_info['show_aliases']

	titles = list(alias_list)
	titles.insert(0, show_title)
	clean_titles = []
	for title in titles:
		clean_titles.append(clean_title_with_simple_info(title, simple_info))

	episode_title = clean_title(simple_info['episode_title'])

	show_season = season
	show_episode_absolute = simple_info['absolute_number']
	episode_list = []
	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(show_episode_absolute).zfill(1))
	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(show_episode_absolute).zfill(3))
	#episode_list.append('S'+str(show_season).zfill(2)+'E'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(show_episode_absolute).zfill(3))
	#episode_list.append(str(show_season).zfill(1)+'x'+str(show_episode_absolute).zfill(1))
	#episode_list.append(str(show_season).zfill(1)+'x'+str(show_episode_absolute).zfill(2))
	episode_list.append(str(show_season).zfill(1)+'x'+str(show_episode_absolute).zfill(3))
	#episode_list.append(str(show_season).zfill(2)+'x'+str(show_episode_absolute).zfill(2))
	episode_list.append(str(show_season).zfill(2)+'x'+str(show_episode_absolute).zfill(3))

	#episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode_absolute).zfill(1) + '.')
	#episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode_absolute).zfill(2) + '.')
	episode_list.append('S'+str(show_season).zfill(1)+' - '+str(show_episode_absolute).zfill(3) + '.')
	#episode_list.append('S'+str(show_season).zfill(2)+' - '+str(show_episode_absolute).zfill(2) + '.')
	episode_list.append('S'+str(show_season).zfill(2)+' - '+str(show_episode_absolute).zfill(3) + '.')

	#episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode_absolute).zfill(1) + '.')
	#episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode_absolute).zfill(2) + '.')
	episode_list.append('S'+str(show_season).zfill(1)+' - E'+str(show_episode_absolute).zfill(3) + '.')
	#episode_list.append('S'+str(show_season).zfill(2)+' - E'+str(show_episode_absolute).zfill(2) + '.')
	episode_list.append('S'+str(show_season).zfill(2)+' - E'+str(show_episode_absolute).zfill(3) + '.')

	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(1)+'-E'+str(show_episode_absolute).zfill(1))
	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(1)+'-E'+str(int(show_episode_absolute)+1).zfill(1))
	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(2)+'-E'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(3)+'-E'+str(show_episode_absolute).zfill(3))
	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(2)+'-E'+str(int(show_episode_absolute)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(3)+'-E'+str(int(show_episode_absolute)+1).zfill(3))

	#episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(2)+'-E'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(3)+'-E'+str(show_episode_absolute).zfill(3))
	#episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(2)+'-E'+str(int(show_episode_absolute)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(3)+'-E'+str(int(show_episode_absolute)+1).zfill(3))
	#episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(1)+'-E'+str(show_episode_absolute).zfill(1))
	#episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(1)+'-E'+str(int(show_episode_absolute)+1).zfill(1))

	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(1)+'&'+str(show_episode_absolute).zfill(1))
	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(1)+'&'+str(int(show_episode_absolute)+1).zfill(1))
	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(2)+'&'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(3)+'&'+str(show_episode_absolute).zfill(3))
	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(2)+'&'+str(int(show_episode_absolute)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(3)+'&'+str(int(show_episode_absolute)+1).zfill(3))

	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(1)+'&E'+str(show_episode_absolute).zfill(1))
	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(1)+'&E'+str(int(show_episode_absolute)+1).zfill(1))
	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(2)+'&E'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)-1).zfill(3)+'&E'+str(show_episode_absolute).zfill(3))
	#episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(2)+'&E'+str(int(show_episode_absolute)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(1)+'E'+str(int(show_episode_absolute)).zfill(3)+'&E'+str(int(show_episode_absolute)+1).zfill(3))

	#episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(2)+'&'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(3)+'&'+str(show_episode_absolute).zfill(3))
	#episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(2)+'&'+str(int(show_episode_absolute)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(3)+'&'+str(int(show_episode_absolute)+1).zfill(3))
	#episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(1)+'&'+str(show_episode_absolute).zfill(1))
	#episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(1)+'&'+str(int(show_episode_absolute)+1).zfill(1))

	#episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(2)+'&E'+str(show_episode_absolute).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(3)+'&E'+str(show_episode_absolute).zfill(3))
	#episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(2)+'&E'+str(int(show_episode_absolute)+1).zfill(2))
	episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(3)+'&E'+str(int(show_episode_absolute)+1).zfill(3))
	#episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)-1).zfill(1)+'&E'+str(show_episode_absolute).zfill(1))
	#episode_list.append('S'+str(show_season).zfill(2)+'E'+str(int(show_episode_absolute)).zfill(1)+'&E'+str(int(show_episode_absolute)+1).zfill(1))

	episode_list.append('E'+str(show_episode_absolute).zfill(3))
	episode_list.append('E'+str(int(show_episode_absolute)).zfill(3)+'&E'+str(int(show_episode_absolute)+1).zfill(3))
	episode_list.append('E'+str(int(show_episode_absolute)-1).zfill(3)+'&E'+str(int(show_episode_absolute)).zfill(3))
	episode_list.append('E'+str(int(show_episode_absolute)).zfill(3)+'&'+str(int(show_episode_absolute)+1).zfill(3))
	episode_list.append('E'+str(int(show_episode_absolute)-1).zfill(3)+'&'+str(int(show_episode_absolute)).zfill(3))
	episode_list.append('E'+str(int(show_episode_absolute)).zfill(3)+'-'+str(int(show_episode_absolute)+1).zfill(3))
	episode_list.append('E'+str(int(show_episode_absolute)-1).zfill(3)+'-'+str(int(show_episode_absolute)).zfill(3))
	episode_list.append('E'+str(int(show_episode_absolute)).zfill(3)+'-E'+str(int(show_episode_absolute)+1).zfill(3))
	episode_list.append('E'+str(int(show_episode_absolute)-1).zfill(3)+'-E'+str(int(show_episode_absolute)).zfill(3))

	episode_list.append('E'+str(int(show_episode_absolute)).zfill(3)+' E'+str(int(show_episode_absolute)+1).zfill(3))
	episode_list.append('E'+str(int(show_episode_absolute)-1).zfill(3)+' E'+str(int(show_episode_absolute)).zfill(3))
	episode_list.append('E'+str(int(show_episode_absolute)).zfill(3)+' '+str(int(show_episode_absolute)+1).zfill(3))
	episode_list.append('E'+str(int(show_episode_absolute)-1).zfill(3)+' '+str(int(show_episode_absolute)).zfill(3))
	#episode_list.append('E'+str(int(show_episode_absolute)).zfill(3)+' '+str(int(show_episode_absolute)+1).zfill(3))
	#episode_list.append('E'+str(int(show_episode_absolute)-1).zfill(3)+' '+str(int(show_episode_absolute)).zfill(3))
	#episode_list.append('E'+str(int(show_episode_absolute)).zfill(3)+' E'+str(int(show_episode_absolute)+1).zfill(3))
	#episode_list.append('E'+str(int(show_episode_absolute)-1).zfill(3)+' E'+str(int(show_episode_absolute)).zfill(3))

	suffixes = []
	for i in episode_list:
		suffixes.append(str(i).lower())
	regex_pattern = get_regex_pattern(clean_titles, suffixes)

	def filter_fn(release_title):

		if re.match(regex_pattern, release_title):
			return True

		#if check_episode_title_match(clean_titles, release_title, simple_info):
		#	return True

		if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
			tools.log('singleepisode]: %s' % release_title, 'notice')
		return False

	return filter_fn

def check_show_title(simple_info, release_title):
	show_title, season, alias_list = \
		simple_info['show_title'], \
		simple_info['season_number'], \
		simple_info['show_aliases']
	show_title = clean_title(simple_info['show_title'])
	episode_title = clean_title(simple_info['episode_title'])
	release_title = clean_title(release_title)

	titles = list(alias_list)
	titles.insert(0, show_title)

	suffixes = [' ']
	clean_titles = []
	for title in titles:
		clean_titles.append(clean_title_with_simple_info(title, simple_info))
	
		
	pattern = r'^(?:'
	for title in titles:
		title = title.strip()
		if len(title) > 0:
			pattern += re.escape(title) + r' |'
	pattern = pattern[:-1] + r')'
	regex_pattern = re.compile(pattern)
	regex_pattern2 = re.compile(pattern.lower())

	pattern = r'^(?:'
	for title in clean_titles:
		title = title.strip()
		if len(title) > 0:
			pattern += re.escape(title) + r' |'
	pattern = pattern[:-1] + r')'
	regex_pattern3 = re.compile(pattern)
	regex_pattern4 = re.compile(pattern.lower())

	if re.match(regex_pattern, release_title):
		return True
	elif re.match(regex_pattern2, release_title):
		return True
	if re.match(regex_pattern3, release_title):
		return True
	elif re.match(regex_pattern4, release_title):
		return True
	else:
		return False



def filter_single_special_episode(simple_info, release_title):

	show_title, season, alias_list = \
		simple_info['show_title'], \
		simple_info['season_number'], \
		simple_info['show_aliases']
	show_title = clean_title(simple_info['show_title'])
	episode_title = clean_title(simple_info['episode_title'])

	titles = list(alias_list)
	titles.insert(0, show_title)

	suffixes = [' ']
	clean_titles = []
	for title in titles:
		clean_titles.append(clean_title_with_simple_info(title, simple_info))
		
	pattern = r'^(?:'
	for title in titles:
		title = title.strip()
		if len(title) > 0:
			pattern += re.escape(title) + r' |'
	pattern = pattern[:-1] + r')'
	regex_pattern = re.compile(pattern)
	#regex_pattern = get_regex_pattern(clean_titles, suffixes)

	if episode_title in release_title and episode_title not in show_title:
		show_title_match = check_show_title(simple_info, release_title)
		if show_title_match:
			return True

	parts_roman, parts_numbers, parts_words, parts_numbers2 = tools.episodes_parts_lists()
	for idx, i in enumerate(parts_roman):
		if str(parts_roman[idx]).lower() in simple_info['episode_title'].lower() or str(parts_numbers[idx]).lower() in simple_info['episode_title'].lower() or str(parts_numbers2[idx]).lower() in simple_info['episode_title'].lower():
			episode_title = clean_title(simple_info['episode_title'].lower().replace(parts_roman[idx].lower(),'').replace(parts_numbers[idx].lower(),'').replace(parts_numbers2[idx].lower(),''))
	if episode_title in release_title and episode_title not in show_title:
		show_title_match = check_show_title(simple_info, release_title)
		if show_title_match:
			return True

	if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
		tools.log('episodespecial]: %s' % release_title, 'notice')
	return False

def get_filter_season_pack_fn(simple_info):
	show_title, season, alias_list = \
		simple_info['show_title'], \
		simple_info['season_number'], \
		simple_info['show_aliases']

	titles = list(alias_list)
	titles.insert(0, show_title)

	season_fill = season.zfill(2)
	season_check = 's%s' % season
	season_fill_check = 's%s' % season_fill
	season_full_check = 'season %s' % season
	season_full_fill_check = 'season %s' % season_fill

	clean_titles = []
	for title in titles:
		clean_titles.append(clean_title_with_simple_info(title, simple_info))

	suffixes = [season_check, season_fill_check, season_full_check, season_full_fill_check]
	regex_pattern = get_regex_pattern(clean_titles, suffixes)

	def filter_fn(release_title):
		episode_number_match = check_episode_number_match(release_title)
		if episode_number_match:
			return False

		if re.match(regex_pattern, release_title):
			return True

		if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
			tools.log('seasonpack]: %s' % release_title, 'notice')
		return False

	return filter_fn

def get_filter_show_pack_fn(simple_info):
	show_title, season, alias_list, no_seasons, country, year = \
		simple_info['show_title'], \
		simple_info['season_number'], \
		simple_info['show_aliases'], \
		simple_info['no_seasons'], \
		simple_info['country'], \
		simple_info['year']

	titles = list(alias_list)
	titles.insert(0, show_title)
	for idx, title in enumerate(titles):
		titles[idx] = clean_title_with_simple_info(title, simple_info)

	all_season_ranges = []
	all_seasons = '1 '
	season_count = 2
	while season_count <= int(no_seasons):
		all_season_ranges.append(all_seasons + 'and %s' % str(season_count))
		all_seasons += '%s ' % str(season_count)
		all_season_ranges.append(all_seasons)
		season_count += 1

	all_season_ranges = [x for x in all_season_ranges if season in x]
	season_fill = season.zfill(2)

	def get_pack_names(title):
		no_seasons_fill = no_seasons.zfill(2)
		no_seasons_minus_one = str(int(no_seasons) - 1)
		no_seasons_minus_one_fill = no_seasons_minus_one.zfill(2)

		results = [
			'all %s seasons' % no_seasons,
			'all %s seasons' % no_seasons_fill,
			'all %s seasons' % no_seasons_minus_one,
			'all %s seasons' % no_seasons_minus_one_fill,
			'all of serie %s seasons' % no_seasons,
			'all of serie %s seasons' % no_seasons_fill,
			'all of serie %s seasons' % no_seasons_minus_one,
			'all of serie %s seasons' % no_seasons_minus_one_fill,
			'all torrent of serie %s seasons' % no_seasons,
			'all torrent of serie %s seasons' % no_seasons_fill,
			'all torrent of serie %s seasons' % no_seasons_minus_one,
			'all torrent of serie %s seasons' % no_seasons_minus_one_fill,
		]

		for all_seasons in all_season_ranges:
		  results.append('%s' % all_seasons)
		  results.append('season %s' % all_seasons)
		  results.append('seasons %s' % all_seasons)

		if 'series' not in title:
			results.append('series')

		if 'boxset' not in title:
			results.append('boxset')

		if 'collection' not in title:
			results.append('collection')

		first_season = 1
		last_season = no_seasons
		results.append(str(' Complete').lower())
		results.append(str(' The Complete Series').lower())
		results.append(str(' Complete Series').lower())
		results.append(str(' Season '+str(first_season).zfill(1) + '-'+str(last_season).zfill(1)).lower())
		results.append(str(' Season '+str(first_season).zfill(2) + '-'+str(last_season).zfill(2)).lower())
		results.append(str(' Season '+str(first_season).zfill(1) + ' - '+str(last_season).zfill(1)).lower())
		results.append(str(' Season '+str(first_season).zfill(2) + ' - '+str(last_season).zfill(2)).lower())
		results.append(str(' Season '+str(first_season).zfill(1) + ' to '+str(last_season).zfill(1)).lower())
		results.append(str(' Season '+str(first_season).zfill(2) + ' to '+str(last_season).zfill(2)).lower())
		results.append(str(' S'+str(first_season).zfill(1) + '-S'+str(last_season).zfill(1)).lower())
		results.append(str(' S'+str(first_season).zfill(2) + '-S'+str(last_season).zfill(2)).lower())
		results.append(str(' S'+str(first_season).zfill(1) + ' - S'+str(last_season).zfill(1)).lower())
		results.append(str(' S'+str(first_season).zfill(2) + ' - S'+str(last_season).zfill(2)).lower())

		return results

	def get_pack_names_range(last_season):
		last_season_fill = last_season.zfill(2)

		return [
			'%s seasons' % (last_season),
			'%s seasons' % (last_season_fill),

			'season 1 %s' % (last_season),
			'season 01 %s' % (last_season_fill),
			'season1 %s' % (last_season),
			'season01 %s' % (last_season_fill),
			'season 1 to %s' % (last_season),
			'season 01 to %s' % (last_season_fill),
			'season 1 thru %s' % (last_season),
			'season 01 thru %s' % (last_season_fill),

			'seasons 1 %s' % (last_season),
			'seasons 01 %s' % (last_season_fill),
			'seasons1 %s' % (last_season),
			'seasons01 %s' % (last_season_fill),
			'seasons 1 to %s' % (last_season),
			'seasons 01 to %s' % (last_season_fill),
			'seasons 1 thru %s' % (last_season),
			'seasons 01 thru %s' % (last_season_fill),

			'full season 1 %s' % (last_season),
			'full season 01 %s' % (last_season_fill),
			'full season1 %s' % (last_season),
			'full season01 %s' % (last_season_fill),
			'full season 1 to %s' % (last_season),
			'full season 01 to %s' % (last_season_fill),
			'full season 1 thru %s' % (last_season),
			'full season 01 thru %s' % (last_season_fill),

			'full seasons 1 %s' % (last_season),
			'full seasons 01 %s' % (last_season_fill),
			'full seasons1 %s' % (last_season),
			'full seasons01 %s' % (last_season_fill),
			'full seasons 1 to %s' % (last_season),
			'full seasons 01 to %s' % (last_season_fill),
			'full seasons 1 thru %s' % (last_season),
			'full seasons 01 thru %s' % (last_season_fill),

			's1 %s' % (last_season),
			's1 s%s' % (last_season),
			's01 %s' % (last_season_fill),
			's01 s%s' % (last_season_fill),
			's1 to %s' % (last_season),
			's1 to s%s' % (last_season),
			's01 to %s' % (last_season_fill),
			's01 to s%s' % (last_season_fill),
			's1 thru %s' % (last_season),
			's1 thru s%s' % (last_season),
			's01 thru %s' % (last_season_fill),
			's01 thru s%s' % (last_season_fill),
		]

	suffixes = get_pack_names(show_title)
	seasons_count = int(season)
	while seasons_count <= int(no_seasons):
		suffixes += get_pack_names_range(str(seasons_count))
		seasons_count += 1

	regex_pattern = get_regex_pattern(titles, suffixes)
	pattern = r'^(?:'
	for title in titles:
		title = title.strip()
		if len(title) > 0:
			pattern += re.escape(title) + r' |'
	pattern = pattern[:-1] + r')+'
	regex_pattern1 = re.compile(pattern)
	
	pattern = r'.*(?:'
	for suffix in suffixes:
		suffix = suffix.strip()
		if len(suffix) > 0:
			pattern += re.escape(suffix) + r' |'
	pattern = pattern[:-1] + r')+'
	regex_pattern2 = re.compile(pattern)


	def filter_fn(release_title):
		episode_number_match = check_episode_number_match(release_title)

		if episode_number_match:
			return False

		if re.match(regex_pattern, release_title):
			return True

		#tools.log(re.match(regex_pattern1, release_title), re.match(regex_pattern2, release_title))
		#tools.log(pattern)
		#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		if re.match(regex_pattern1, release_title) and re.match(regex_pattern2, release_title):
			return True

		if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
			tools.log('showpack]: %s' % release_title, 'notice')
		return False

	return filter_fn


def unique(list1):
	from functools import reduce
	# Print directly by using * symbol
	ans = reduce(lambda re, x: re+[x] if x not in re else re, list1, [])
	return list(ans)



def match_episodes_season_pack(meta, sorted_torr_info):
	now = time.time()
	url = str(sorted_torr_info[0]) + 'season___' +str(meta['episode_meta']['season']) + 'meta_source__None'
	folder = 'show_filters'
	cache_days = 7
	url = url.encode('utf-8')
	hashed_url = hashlib.md5(url).hexdigest()
	cache_path = os.path.join(tools.ADDON_USERDATA_PATH, folder)

	try: 
		db_result = tools.query_db(connection=tools.db_con,url=url, cache_days=cache_days, folder=folder, headers=None)
	except:
		db_result = None
	if db_result:
		return db_result
	else:
	#if not os.path.exists(cache_path):
	#	os.mkdir(cache_path)
	#cache_seconds = int(cache_days * 86400.0)
	#path = os.path.join(cache_path, '%s.txt' % hashed_url)
	#if os.path.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
	#	results = tools.read_all_text(path)
	#	results = eval(results)
	#	return results
	#else:
		#sys.path.append(current_directory)
		#try:
		#	import daetutil, babelfish, rebulk, guessit
		#	from guessit import api
		#except:
		#	from a4kscrapers_wrapper import dateutil, babelfish, rebulk, guessit
		#	from a4kscrapers_wrapper.guessit import api

		last_episode_tmdb = int(meta['tmdb_seasons']['episodes'][-1]['episode'])
		last_episode_tvmaze = int(meta['tvmaze_seasons']['episodes'][-1]['episode'])

		last_abs_episode_tmdb = int(meta['tmdb_seasons']['episodes'][-1]['absoluteNumber'])
		last_abs_episode_tvmaze = int(meta['tvmaze_seasons']['episodes'][-1]['absoluteNumber'])
		
		season = int(meta['tvmaze_seasons']['episodes'][-1]['season'])
		
		folders = unique([item['pack_path'].replace(os.path.basename(item['pack_path']),'') for item in sorted_torr_info])
		season_path = None
		prev_season_path = None
		for i in folders:
			#guess = api.guessit(i)
			guess = get_guess(i)
			if guess.get('season') == int(season):
				season_path = i
				break
			prev_season_path = i

		prev_season_index = 0
		for idx, i in enumerate(sorted_torr_info):
			if prev_season_path:
				if prev_season_path in i['pack_path']:
					prev_season_index = idx

		#tools.log(sorted_torr_info)
		#exit()


		result_dict = {}
		result_dict['episode_numbers'] = []
		result_dict['pack_paths'] = []
		result_dict['alt_ep_num'] = []
		result_dict['concat'] = []

		guessit_list = []
		start_index = -1
		end_index = -1
		options = {'type': 'episode'}
		prev_episode = 0
		max_episode = 0
		absolute_flag = False
		season_match = False
		
		for idx, i in enumerate(sorted_torr_info):
			pack_path = os.path.basename(i['pack_path'])
			#tools.log(pack_path)
			#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			if season_path:
				#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				if not season_path in str(i['pack_path']):
					season_match = False
					if int(meta['episode_meta']['episode']) == 1 and idx == prev_season_index:
						#tools.log(i['pack_path'])
						curr_episode_tmdb = meta['tmdb_seasons']['episodes'][0]
						curr_episode_tvmaze = meta['tvmaze_seasons']['episodes'][0]
						simple_info = tools._build_simple_show_info(curr_episode_tvmaze)
						test = run_show_filters(simple_info, release_title = i['pack_path'])
						#tools.log(simple_info,test)
						if test.get('get_filter_single_absolute_episode_fn',False) == True or test.get('filter_check_episode_title_match',False) == True or test.get('filter_single_special_episode',False) == True or test.get('get_filter_single_episode_fn',False) == True:
							season_match = True
						else:
							simple_info = tools._build_simple_show_info(curr_episode_tmdb)
							test = run_show_filters(simple_info, release_title = i['pack_path'])
							#tools.log(test)
							if test.get('get_filter_single_absolute_episode_fn',False) == True or test.get('filter_check_episode_title_match',False) == True or test.get('filter_single_special_episode',False) == True or test.get('get_filter_single_episode_fn',False) == True:
								season_match = True
					if season_match == False:
						continue
			if absolute_flag and season_match == False:
				#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				curr_episode_tmdb = meta['tmdb_seasons']['episodes'][0]
				curr_episode_tvmaze = meta['tvmaze_seasons']['episodes'][0]
				simple_info = tools._build_simple_show_info(curr_episode_tvmaze)
	
				
				filter_fn = get_filter_single_absolute_episode_fn(simple_info)
				simple_info['query_title'] = i['pack_path']
				simple_info['clean_release'] = clean_release_title_with_simple_info(i['pack_path'], simple_info)
				test = filter_fn(simple_info['clean_release'])

				simple_info2 = tools._build_simple_show_info(curr_episode_tmdb)
				simple_info2['query_title'] = i['pack_path']
				filter_fn = get_filter_single_absolute_episode_fn(simple_info2)
				simple_info2['clean_release'] = clean_release_title_with_simple_info(i['pack_path'], simple_info2)
				test2 = filter_fn(simple_info2['clean_release'])
				
				if test == True or test2 == True:
					#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
					season_match = True
				if season_match == False:
					#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
					continue
			#guess = api.guessit(pack_path, options)
			guess = get_guess(pack_path, options)
			if guess.get('type') == 'episode' and 'miniseries' in str(meta).lower():
				if guess.get('episode', False) == False and guess.get('part', False) != False:
					guess['episode'] = guess['part'] 
				if guess.get('season', False) == False:
					guess['season'] = 1 
				if guess.get('episode_title', False) == False:
					guess['episode_title'] = simple_info['originaltitle']
					
			#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			#tools.log(pack_path,guess)
			guessit_list.append([guess, idx, []])
			guess_season = guess.get('season')

			if guess_season == None and guess.get('episode') != None and absolute_flag == False:
				absolute_flag = True
				#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				curr_episode_tmdb = meta['tmdb_seasons']['episodes'][0]
				curr_episode_tvmaze = meta['tvmaze_seasons']['episodes'][0]
				simple_info = tools._build_simple_show_info(curr_episode_tvmaze)

				filter_fn = get_filter_single_absolute_episode_fn(simple_info)
				simple_info['query_title'] = i['pack_path']
				simple_info['clean_release'] = clean_release_title_with_simple_info(i['pack_path'], simple_info)
				test = filter_fn(simple_info['clean_release'])

				simple_info2 = tools._build_simple_show_info(curr_episode_tmdb)
				simple_info2['query_title'] = i['pack_path']
				filter_fn = get_filter_single_absolute_episode_fn(simple_info2)
				simple_info2['clean_release'] = clean_release_title_with_simple_info(i['pack_path'], simple_info2)
				test2 = filter_fn(simple_info2['clean_release'])

				if test == True or test2 == True:
					#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
					season_match = True
				if season_match == False:
					#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
					continue

				start_index = idx

			guess_episode = []
			guess_title = guess.get('title')
			if guess.get('episode') == None:

				try:
					curr_episode_tmdb = meta['tmdb_seasons']['episodes'][prev_episode]
					curr_episode_tvmaze = meta['tvmaze_seasons']['episodes'][prev_episode]
				except IndexError:
					continue
				#tools.log(curr_episode_tvmaze,'')
				simple_info = tools._build_simple_show_info(curr_episode_tvmaze)
				test = run_show_filters(simple_info, release_title = i['pack_path'])
				if test.get('get_filter_single_absolute_episode_fn',False) == True or test.get('filter_check_episode_title_match',False) == True or test.get('filter_single_special_episode',False) == True or test.get('get_filter_single_episode_fn',False) == True:
					guess['episode'] = prev_episode
					guess['title'] = curr_episode_tvmaze['tvshowtitle']
					guess['episode_title'] = curr_episode_tvmaze['originaltitle']
					guess['season'] = curr_episode_tvmaze['season_number']
				else:
					simple_info = tools._build_simple_show_info(curr_episode_tmdb)
					test = run_show_filters(simple_info, release_title = i['pack_path'])
					if test.get('get_filter_single_absolute_episode_fn',False) == True or test.get('filter_check_episode_title_match',False) == True or test.get('filter_single_special_episode',False) == True or test.get('get_filter_single_episode_fn',False) == True:
						guess['episode'] = prev_episode
						guess['title'] = curr_episode_tvmaze['tvshowtitle']
						guess['episode_title'] = curr_episode_tvmaze['originaltitle']
						guess['season'] = curr_episode_tvmaze['season_number']
				if guess.get('episode') == None:
					continue
			if not 'int' in  str(type(guess.get('episode'))):
				for x in guess.get('episode'):
					guess_episode.append(x)
			else:
				guess_episode.append(guess.get('episode'))

			#tools.log(guess_episode,'guess_episode')
			max_episode = 0
			for x in guess_episode:
				if x > max_episode:
					max_episode = x
				guessit_list[-1][-1].append(x)
				if absolute_flag:
					
					if x == last_abs_episode_tmdb or x == last_abs_episode_tvmaze:
						end_index = idx
					if x > last_abs_episode_tmdb and x > last_abs_episode_tvmaze:
						season_match = False

				if guess_season == season and x == 1:
					start_index = idx
				if guess_season == season and x == last_episode_tmdb:
					if not end_index:
						end_index = idx
					elif end_index and idx > end_index:
						end_index = idx
				if guess_season == season and x == last_episode_tvmaze:
					if not end_index:
						end_index = idx
					elif end_index and idx > end_index:
						end_index = idx
			prev_episode = x

		if start_index == end_index and start_index == -1:
			if len(guess_episode) == 1:
				start_index = 0
				end_index = 0

		#tools.log(end_index, start_index)
		#tools.log(last_abs_episode_tmdb, last_abs_episode_tvmaze)
		#tools.log(max(guess_episode))
		#tools.log(max_episode,'max_episode')
		if last_episode_tvmaze == -1:
			for i in meta['tvmaze_seasons']['episodes']:
				if i['episode'] > last_episode_tvmaze:
					last_episode_tvmaze = i['episode']
		#tools.log(last_episode_tvmaze,'last_episode_tvmaze')
		if len(meta['tvmaze_seasons']['episodes']) == (1+(end_index-start_index)) or (start_index == end_index and end_index == 0):
			meta_source = 'tvmaze_seasons'
		elif last_episode_tvmaze == (max_episode):
			meta_source = 'tvmaze_seasons'
		elif len(meta['tmdb_seasons']['episodes']) == (1+(end_index-start_index)):
			meta_source = 'tmdb_seasons'
		elif len(meta['tmdb_seasons']['episodes']) < (1+(end_index-start_index)):
			meta_source = 'tvmaze_seasons'
		else:
			meta_source = 'tmdb_seasons'

		if meta_source == 'tmdb_seasons' and last_episode_tmdb != last_episode_tvmaze and last_episode_tvmaze == max(guess_episode):
			meta_source = 'tvmaze_seasons'

		tools.log(meta_source,'meta_source')
		ep_adj_number = 0
		if int(meta[meta_source]['episodes'][-1]['episode']) > max_episode:
			ep_adj_number = max_episode - int(meta[meta_source]['episodes'][-1]['episode'])
		#tools.log(meta[meta_source]['episodes'][-1]['episode'],'max_episode_meta_source')

		matched_episodes = {}
		for xdx, x in enumerate(meta[meta_source]['episodes']):
			ep_title = x['name'].lower()
			ep_title = re.sub("[\x00-\x2F\x3A-\x40\x5B-\x60\x7B-\x7F]+", " ", ep_title.lower())
			#tools.log('meta_source_name                                                    ',x['name'])
			for gdx, i in enumerate(guessit_list):
				idx = i[1]
				episode_title = i[0].get('episode_title')
				#tools.log('pack_episode_title',episode_title)
				if episode_title:
					episode_title = re.sub("[\x00-\x2F\x3A-\x40\x5B-\x60\x7B-\x7F]+", " ", episode_title.lower())
				else:
					continue
				if len(clean_title(i[0].get('episode_title'))) < len(i[0].get('episode_title')):
					jaro_dist_factor = 0.8
				else:
					jaro_dist_factor = 0.90001

				if ep_title == episode_title or str(ep_title) in str(episode_title) or str(episode_title) in str(ep_title) or distance.jaro_similarity(ep_title, episode_title) > float(jaro_dist_factor):
					#tools.log(x,i)
					#tools.log(x['episode'])
					if x['episode'] == -1:
						x['episode'] = i[0].get('episode')
						continue
					for y in i[-1]:
						try:
							if not sorted_torr_info[idx]['pack_path'] in matched_episodes[int(x['episode'])]:
								matched_episodes[int(x['episode'])].append(sorted_torr_info[idx]['pack_path'])
						except: 
							matched_episodes[int(x['episode'])] = []
							matched_episodes[int(x['episode'])].append(sorted_torr_info[idx]['pack_path'])

		#tools.log(matched_episodes,'matched_episodes')
		for idx, i in enumerate(matched_episodes):
			if idx > 0:
				try: 
					if matched_episodes[i] == matched_episodes[i-1]:
						if len(matched_episodes[i]) == 2:
							double_fix = matched_episodes[i]
							matched_episodes[i-1] = [double_fix[0]]
							matched_episodes[i] = [double_fix[1]]
				except:
					continue

		#tools.log(matched_episodes,'matched_episodes')
		for xdx, x in enumerate(meta[meta_source]['episodes']):
			ep_title = x['name'].lower()
			ep_title = re.sub("[\x00-\x2F\x3A-\x40\x5B-\x60\x7B-\x7F]+", " ", ep_title.lower())
			for gdx, i in enumerate(guessit_list):
				idx = i[1]
				if i[0].get('episode') == None:
					continue
				else:
					break_flag = False
					for y in i[-1]:
						if x['episode'] == y and x['season'] == i[0].get('season'):
							try:
								if not sorted_torr_info[idx]['pack_path'] in matched_episodes[int(x['episode'])]:
									matched_episodes[int(x['episode'])].append(sorted_torr_info[idx]['pack_path'])
							except: 
								matched_episodes[int(x['episode'])] = []
								matched_episodes[int(x['episode'])].append(sorted_torr_info[idx]['pack_path'])
							break_flag = True
					if break_flag == True:
						break


		for i in matched_episodes:
			if len(matched_episodes[i]) > 1:
				for x in matched_episodes[i]:
					match = False
					pack_path = x
					for gdx, y in enumerate(guessit_list):
						idx = y[1]
						if pack_path == sorted_torr_info[idx]['pack_path']:
							guess = y[0]
							break
					episode_title = guess.get('episode_title')
					ep_title = meta[meta_source]['episodes'][int(i)-1]['name']
					guess_season = guess.get('season')
					guess_episode = guess.get('episode') 
					simple_info = tools._build_simple_show_info(meta[meta_source]['episodes'][int(i)-1])
					part_number_title, part_number_release, part_match_title, part_match_release = parts_check(simple_info, pack_path)
					#tools.log(simple_info,'simple_info')
					#tools.log(pack_path,'pack_path')
					#tools.log(ep_title,'ep_title')
					if len(clean_title(ep_title)) == 0 and len(clean_title(episode_title)) != 0:
						ep_number_match_only = True
					else:
						ep_number_match_only = False
					#tools.log(part_number_title, part_number_release, part_match_title, part_match_release)
					if episode_title:
						#tools.log(distance.jaro_similarity(ep_title, episode_title))
						#tools.log(ep_title, episode_title)
						try: ep_title_part_test = int(ep_title.split(' ')[-1].replace(')','').replace('(',''))
						except: ep_title_part_test = 0
						#tools.log(ep_title_part_test, 'ep_title_part_test')
						if ep_title_part_test > 0:
							ep_title2 = ep_title.replace(' '+ep_title.split(' ')[-1],'')
						else:
							ep_title2 = None
						#tools.log(ep_title2, 'ep_title2')
						#tools.log(guess_episode, 'guess_episode')
						#tools.log(i, 'i')
						#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
						if ep_title == episode_title or distance.jaro_similarity(ep_title, episode_title) > 0.925 or ep_number_match_only:
							if guess_episode == i and guess_season == int(meta[meta_source]['episodes'][int(i)-1]['season']):
								match = True
							elif ep_adj_number > 0 and guess_episode < i and i - guess_episode <= ep_adj_number and guess_season == int(meta[meta_source]['episodes'][int(i)-1]['season']):
								match = True
							elif part_number_title == part_number_release:
								match = True
						elif len(clean_title(episode_title)) == len(episode_title) and distance.jaro_similarity(ep_title, episode_title) > 0.9:
							#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
							if guess_episode == i and guess_season == int(meta[meta_source]['episodes'][int(i)-1]['season']):
								match = True
							elif ep_adj_number > 0 and guess_episode < i and i - guess_episode <= ep_adj_number and guess_season == int(meta[meta_source]['episodes'][int(i)-1]['season']):
								match = True
							elif part_number_title == part_number_release:
								match = True
						elif len(clean_title(episode_title)) < len(episode_title):
							if ep_title == episode_title or distance.jaro_similarity(ep_title, episode_title) > 0.75:
								if guess_episode == i and guess_season == int(meta[meta_source]['episodes'][int(i)-1]['season']):
									match = True
								elif ep_adj_number > 0 and guess_episode < i and i - guess_episode <= ep_adj_number and guess_season == int(meta[meta_source]['episodes'][int(i)-1]['season']):
									match = True
								elif part_number_title == part_number_release:
									match = True

						if ep_title2 and match == False:
							#tools.log(distance.jaro_similarity(ep_title2, episode_title))
							#tools.log(ep_title2, 'ep_title2')
							#tools.log(guess_episode, i)
							if ep_title2 == episode_title or distance.jaro_similarity(ep_title2, episode_title) > 0.925:
								if (guess_episode == i or max(guess_episode,i)-min(guess_episode,i)==1) and guess_season == int(meta[meta_source]['episodes'][int(i)-1]['season']):
									match = True
								elif part_number_title == part_number_release:
									match = True
							elif len(clean_title(episode_title)) < len(episode_title):
								if ep_title2 == episode_title or distance.jaro_similarity(ep_title2, episode_title) > 0.75:
									if (guess_episode == i or max(guess_episode,i)-min(guess_episode,i)==1) and guess_season == int(meta[meta_source]['episodes'][int(i)-1]['season']):
										match = True

									#elif (guess_episode == i or max(guess_episode,i)-min(guess_episode,i)==1) and guess_season == int(meta[meta_source]['episodes'][int(i)-1]['season']):
									elif ep_adj_number > 0 and guess_episode < i and i - guess_episode <= ep_adj_number and guess_season == int(meta[meta_source]['episodes'][int(i)-1]['season']):
										match = True

									elif part_number_title == part_number_release:
										match = True

						if match == False:
							try:
								if part_number_release[-1] == part_number_title[-1] and str(part_number_title[-1]) in str(part_match_release[-1]):
									if ep_title == episode_title or distance.jaro_similarity(ep_title, episode_title) > 0.8:
										match = True
										#tools.log(simple_info,'simple_info,match = True')
							except:
								#tools.log(simple_info,'simple_info')
								#tools.log(pack_path,'pack_path')
								#tools.log(result_dict,'result_dict')
								#tools.log(part_number_title, part_number_release, part_match_title, part_match_release)
								match = False
					else:
						if guess_episode == i and guess_season == int(meta[meta_source]['episodes'][int(i)-1]['season']):
							match = True
					if match == True and not i in result_dict['episode_numbers']:
						#tools.log(ep_title, episode_title)
						#tools.log(i,'i')
						result_dict['episode_numbers'].append(i)
						result_dict['alt_ep_num'].append(guess_episode)
						result_dict['pack_paths'].append(pack_path)
						result_dict['concat'].append({'meta_source': meta_source, 'tmdb': meta['tmdb'],'season': meta['episode_meta']['season'], 'episode_number': i, 'pack_path': pack_path, 'alt_ep_num': guess_episode })
						break
			else:
				pack_path = matched_episodes[i][0]

				for gdx, y in enumerate(guessit_list):
					idx = y[1]
					if pack_path == sorted_torr_info[idx]['pack_path']:
						guess = y[0]
						break
				guess_season = guess.get('season')
				guess_episode = guess.get('episode') 
				if not i in result_dict['episode_numbers']:
					result_dict['episode_numbers'].append(i)
					result_dict['alt_ep_num'].append(guess_episode)
					result_dict['pack_paths'].append(matched_episodes[i][0])
					result_dict['concat'].append({'meta_source': meta_source, 'tmdb': meta['tmdb'],'season': meta['episode_meta']['season'], 'episode_number': i, 'pack_path': pack_path, 'alt_ep_num': guess_episode })

		result_dict_sorted = {}
		result_dict_sorted['episode_numbers'] = []
		result_dict_sorted['pack_paths'] = []
		result_dict_sorted['alt_ep_num'] = []
		result_dict_sorted['concat'] = []

		#tools.log(result_dict)
		if len(result_dict['episode_numbers']) == 0 or abs(len(meta[meta_source]['episodes']) - len(result_dict['episode_numbers']))>=4:
			return

		for i in range(min(result_dict['episode_numbers']),max(result_dict['episode_numbers'])+1):
			idx = result_dict['episode_numbers'].index(i)
			result_dict_sorted['episode_numbers'].append(result_dict['episode_numbers'][idx])
			result_dict_sorted['pack_paths'].append(result_dict['pack_paths'][idx])
			result_dict_sorted['alt_ep_num'].append(result_dict['alt_ep_num'][idx])
			result_dict_sorted['concat'].append(result_dict['concat'][idx])

		#for i in result_dict:
		#	tools.log(i, result_dict[i])
		#tools.write_all_text(path, str(result_dict_sorted))
		#exit()
		tools.write_db(connection=tools.db_con,url=url, cache_days=cache_days, folder=folder,cache_val=result_dict_sorted)
		
		return result_dict_sorted