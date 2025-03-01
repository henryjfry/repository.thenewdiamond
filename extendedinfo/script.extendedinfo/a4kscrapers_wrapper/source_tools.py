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
	import daetutil, babelfish, rebulk, guessit
	from guessit import api
except:
	from a4kscrapers_wrapper import dateutil, babelfish, rebulk, guessit
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
			print(x)
			if str(x).lower() in simple_info['episode_title'].lower():
				part_number_title.append(str(idx)+'+'+str(int(idx)+1))
	part_number_release = []
	for i in multi_dict:
		idx = i
		for x in multi_dict[i]:
			print(x)
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
		show_title_match = check_show_title(simple_info, release_title)

		if show_title_match == False:

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
		result_dict['filter_single_special_episode'] = filter_single_special_episode(simple_info, simple_info['clean_release'])
		filter_fn = get_filter_single_absolute_episode_fn(simple_info)
		result_dict['get_filter_single_absolute_episode_fn'] = filter_fn(simple_info['clean_release'])
		result_dict['filter_check_episode_title_match'] = filter_check_episode_title_match(simple_info, simple_info['clean_release'])

		if not ': True' in str(result_dict):


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
			distance_apart = distance.jaro_similarity(show_title,guess_title)
			if distance_apart < 0.925:
				for i in result_dict:
						if result_dict[i] == True:
							result_dict[i] = False
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

	if re.match(regex_pattern, release_title):
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
		results.append(str('Complete').lower())
		results.append(str('The Complete Series').lower())
		results.append(str('Season '+str(first_season).zfill(1) + '-'+str(last_season).zfill(1)).lower())
		results.append(str('Season '+str(first_season).zfill(2) + '-'+str(last_season).zfill(2)).lower())
		results.append(str('Season '+str(first_season).zfill(1) + ' - '+str(last_season).zfill(1)).lower())
		results.append(str('Season '+str(first_season).zfill(2) + ' - '+str(last_season).zfill(2)).lower())
		results.append(str('Season '+str(first_season).zfill(1) + ' to '+str(last_season).zfill(1)).lower())
		results.append(str('Season '+str(first_season).zfill(2) + ' to '+str(last_season).zfill(2)).lower())
		results.append(str('S'+str(first_season).zfill(1) + '-S'+str(last_season).zfill(1)).lower())
		results.append(str('S'+str(first_season).zfill(2) + '-S'+str(last_season).zfill(2)).lower())
		results.append(str('S'+str(first_season).zfill(1) + ' - S'+str(last_season).zfill(1)).lower())
		results.append(str('S'+str(first_season).zfill(2) + ' - S'+str(last_season).zfill(2)).lower())

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

	def filter_fn(release_title):
		episode_number_match = check_episode_number_match(release_title)
		if episode_number_match:
			return False

		if re.match(regex_pattern, release_title):
			return True

		if os.getenv('A4KSCRAPERS_TEST_TOTAL') != '1':
			tools.log('showpack]: %s' % release_title, 'notice')
		return False

	return filter_fn

#"""
#
#def match_episodes_season_pack_original(meta, sorted_torr_info):
#	now = time.time()
#	url = str(sorted_torr_info[0]) + 'season___' +str(meta['episode_meta']['season']) + 'meta_source__None'
#	folder = 'show_filters'
#	cache_days = 7
#	url = url.encode('utf-8')
#	hashed_url = hashlib.md5(url).hexdigest()
#	cache_path = os.path.join(tools.ADDON_USERDATA_PATH, folder)
#
#	if not os.path.exists(cache_path):
#		os.mkdir(cache_path)
#	cache_seconds = int(cache_days * 86400.0)
#	path = os.path.join(cache_path, '%s.txt' % hashed_url)
#	if os.path.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
#		results = tools.read_all_text(path)
#		results = eval(results)
#		return results
#	else:
#		simple_info_tmdb = []
#		simple_info_tvmaze = []
#		for idx, x in enumerate(meta['tmdb_seasons']['episodes']):
#			simple_info = tools._build_simple_show_info(x)
#			simple_info_tmdb.append(simple_info)
#
#		for idx, x in enumerate(meta['tvmaze_seasons']['episodes']):
#			simple_info = tools._build_simple_show_info(x)
#			simple_info_tvmaze.append(simple_info)
#
#		simple_info1a = simple_info_tmdb[0]
#		simple_info1b = simple_info_tvmaze[0]
#		simple_info2a = simple_info_tmdb[-1]
#		simple_info2b = simple_info_tvmaze[-1]
#		#tools.log(simple_info1a, simple_info2a)
#		#tools.log(simple_info1b, simple_info2b)
#
#		start_index = -1
#		end_index = -1
#		for idx, i in enumerate(sorted_torr_info):
#			pack_path = os.path.basename(i['pack_path'])
#			test1a = run_show_filters(simple_info1a, release_title = pack_path)
#			if ': True' in str(test1a):
#				start_index = idx
#				#test1['start_index'] = int(idx)
#				break
#
#		for idx, i in enumerate(sorted_torr_info):
#			if idx < start_index - 2:
#				continue
#			pack_path = os.path.basename(i['pack_path'])
#			test1a = run_show_filters(simple_info1b, release_title = pack_path)
#			if ': True' in str(test1a):
#				if idx < start_index:
#					start_index = idx
#				#test1['start_index'] = int(idx)
#				break
#
#		for idx, i in enumerate(sorted_torr_info):
#			if idx < start_index:
#				continue
#			pack_path = os.path.basename(i['pack_path'])
#			test1a = run_show_filters(simple_info2a, release_title = pack_path)
#			if ': True' in str(test1a):
#				end_index = idx
#				#test1['start_index'] = int(idx)
#				break
#
#		for idx, i in enumerate(sorted_torr_info):
#			if idx < end_index - 2:
#				continue
#			pack_path = os.path.basename(i['pack_path'])
#			test1a = run_show_filters(simple_info2b, release_title = pack_path)
#			if ': True' in str(test1a):
#				if idx > end_index:
#					end_index = idx
#				#test1['start_index'] = int(idx)
#				break
#
#		if len(simple_info_tvmaze) == (1+(end_index-start_index)):
#			simple_info_list = simple_info_tvmaze
#			meta_source = 'tvmaze_seasons'
#		elif len(simple_info_tmdb) == (1+(end_index-start_index)):
#			simple_info_list = simple_info_tmdb
#			meta_source = 'tmdb_seasons'
#		elif len(simple_info_tmdb) < (1+(end_index-start_index)):
#			simple_info_list = simple_info_tvmaze
#			meta_source = 'tvmaze_seasons'
#		else:
#			simple_info_list = simple_info_tmdb
#			meta_source = 'tmdb_seasons'
#
#		#tools.log(sorted_torr_info)
#		#tools.log(len(simple_info_tmdb), len(simple_info_tvmaze))
#		#tools.log(end_index, start_index)
#		#exit()
#
#		if end_index == -1:
#			end_index = len(sorted_torr_info)-1
#
#		output_list = []
#		output_ep = {}
#		alternate_title = {}
#		missing_list = []
#		pop_ep = 0
#		full_dict = {}
#		full_dict['concat'] = []
#		for iidx, i in enumerate(sorted_torr_info):
#			if iidx < start_index or iidx > end_index:
#				continue
#			for idx, x in enumerate(meta[meta_source]['episodes']):
#				if idx < pop_ep:
#					continue
#				#simple_info = tools._build_simple_show_info(x)
#				simple_info = simple_info_list[idx]
#				pack_path = os.path.basename(i['pack_path'])
#				test = run_show_filters(simple_info, release_title = pack_path)
#				test['alternate_title'].append(simple_info['episode_title'])
#				if ': True' in str(test):
#					output = str('ep='+str(int(idx)+1)+'='+i['pack_path'])
#					if str('ep='+str(int(idx)+1)+'=') in str(output_list):
#						if not i['pack_path'] in str(output_list) and not i['pack_path'] in str(missing_list):
#							missing_list.append(i['pack_path'])
#						continue
#					output_list.append(output)
#					output_ep[int(idx)+1] = i['pack_path']
#					alternate_title[int(idx)+1] = test['alternate_title']
#					pop_ep = idx
#
#		#for i in missing_list:
#		#	if i in str(output_ep):
#		#		continue
#		#	if not i in str(output_ep):
#		#		for jdx, j in enumerate(sorted_torr_info):
#		#			if int(jdx) < int(start_index):
#		#				continue
#		#			if int(jdx) > int(end_index):
#		#				continue
#		#			if j['pack_path'] == i:
#		#				for idx, x in enumerate(meta[meta_source]['episodes']):
#		#					#simple_info = tools._build_simple_show_info(x)
#		#					simple_info = simple_info_list[idx]
#		#					pack_path = os.path.basename(j['pack_path'])
#		#					test = run_show_filters(simple_info, release_title = pack_path)
#
#		result_dict = {}
#		result_dict['episode_numbers'] = []
#		result_dict['pack_paths'] = []
#		result_dict['alternate_title'] = []
#		result_dict['concat'] = []
#		for idx, i in enumerate(meta[meta_source]['episodes']):
#			test = output_ep.get(idx+1)
#			if test:
#				#print(idx+1,test)
#				result_dict['episode_numbers'].append(idx+1)
#				result_dict['pack_paths'].append(test)
#				result_dict['alternate_title'].append(alternate_title[idx+1])
#				result_dict['concat'].append({'meta_source': meta_source, 'tmdb': meta['tmdb'],'season': meta['episode_meta']['season'], 'episode_number': idx+1, 'pack_path': test, 'alternate_title': alternate_title[idx+1]})
#
#		missing_episodes = []
#		for i in range(meta[meta_source]['episodes'][0]['episode'],meta[meta_source]['episodes'][-1]['episode']+1):
#			if not i in result_dict['episode_numbers']:
#				missing_episodes.append(i)
#
#		pop_ep = 0
#		for i in missing_episodes:
#			for jdx, j in enumerate(sorted_torr_info):
#				ep_plus_one = str(int(i)+1)
#				ep_minus_one = str(int(i)-1)
#				simple_info = simple_info_list[int(i)-1]
#				simple_info['episode_number'] = str(i)
#				if int(jdx) < int(start_index):
#					continue
#				elif int(jdx) > int(end_index):
#					continue
#				elif int(jdx) < int(pop_ep):
#					continue
#				pack_path = os.path.basename(j['pack_path'])
#				test1 = run_show_filters(simple_info, release_title = pack_path, fuzzy=True)
#				test1['alternate_title'].append(simple_info['episode_title'])
#
#				if ': True' in str(test1):
#					pop_ep = jdx 
#					result_dict['episode_numbers'].append(simple_info['episode_number'])
#					result_dict['pack_paths'].append(j['pack_path'])
#					result_dict['alternate_title'].append(test1['alternate_title'])
#					result_dict['concat'].append({'meta_source': meta_source, 'tmdb': meta['tmdb'],'season': meta['episode_meta']['season'], 'episode_number': simple_info['episode_number'], 'pack_path': j['pack_path'], 'alternate_title': test1['alternate_title']})
#					break
#				else:
#					test2 = None
#					if len(test1['part_number_title']) > 0:
#						if int(test1['part_number_title'][0]) == 2:
#							simple_info['episode_number'] = ep_minus_one
#							test2 = run_show_filters(simple_info, release_title = pack_path, fuzzy=True)
#							test2['alternate_title'].append(simple_info['episode_title'])
#						elif int(test1['part_number_title'][0]) == 1:
#							simple_info['episode_number'] = ep_plus_one
#							test2 = run_show_filters(simple_info, release_title = pack_path, fuzzy=True)
#							test2['alternate_title'].append(simple_info['episode_title'])
#						if ': True' in str(test2):
#							pop_ep = jdx 
#							result_dict['episode_numbers'].append(str(i))
#							result_dict['pack_paths'].append(j['pack_path'])
#							result_dict['alternate_title'].append(test2['alternate_title'])
#							result_dict['concat'].append({'meta_source': meta_source, 'tmdb': meta['tmdb'],'season': meta['episode_meta']['season'], 'episode_number': str(i), 'pack_path': j['pack_path'], 'alternate_title': test2['alternate_title']})
#							break
#
#					
#				
#				#if not ': True' in str(test) and len(test['part_number_title'])>0 and len(test['part_number_release'])==0:
#				#	simple_info2 = simple_info
#				#	for i in test['part_match_title']:
#				#		simple_info2['episode_title'] = simple_info['episode_title'].replace(i,'')
#				#		simple_info2['clean_release'] = clean_release_title_with_simple_info( j['pack_path'], simple_info2)
#				#		filter_fn = get_filter_single_episode_fn(simple_info2)
#				#		test['get_filter_single_episode_fn'] = filter_fn(simple_info2['clean_release'])
#				#		test['filter_single_special_episode'] = filter_single_special_episode(simple_info2, simple_info2['clean_release'])
#				#		test['filter_check_episode_title_match'] = filter_check_episode_title_match(simple_info, simple_info['clean_release'])
#				#		print('')
#				#		print('')
#				#		print(test)
#				#		print('')
#				#		print('')
#				#		print({'meta_source': meta_source, 'tmdb': meta['tmdb'],'season': meta['episode_meta']['season'], 'episode_number': test['episode_number'], 'pack_path': j['pack_path']})
#		
#		new_result_dict = {}
#		new_result_dict['episode_numbers'] = []
#		new_result_dict['pack_paths'] = []
#		new_result_dict['concat'] = []
#		new_result_dict['alternate_title'] = []
#		missing_list = []
#		for i in range(1, len(result_dict['episode_numbers'])+1):
#			try: idx = result_dict['episode_numbers'].index(str(i))
#			except: 
#				try: idx = result_dict['episode_numbers'].index(i)
#				except: 
#					missing_list.append(i)
#					continue
#			new_result_dict['episode_numbers'].append(str(result_dict['episode_numbers'][idx]))
#			new_result_dict['pack_paths'].append(result_dict['pack_paths'][idx])
#			new_result_dict['alternate_title'].append(result_dict['alternate_title'][idx])
#			new_result_dict['concat'].append(result_dict['concat'][idx])
#
#		#tools.log(sorted_torr_info)
#		tools.log(missing_list)
#		#tools.log(new_result_dict)
#		#result_dict = {}
#		#result_dict['episode_numbers'] = []
#		#result_dict['pack_paths'] = []
#		#result_dict['concat'] = []
#		#result_dict['alternate_title'] = []
#		#update_flag = False
#		#if len(simple_info_tvmaze) > len(simple_info_tmdb):
#		#	for i in meta['tvmaze_seasons']['episodes']:
#		#		tvmaze_ep_name = i['name']
#		#		for jdx, j in enumerate(new_result_dict['alternate_title']):
#		#			for alt in j:
#		#				if alt in str(tvmaze_ep_name):
#		#					#tools.log(i['episode'],tvmaze_ep_name,new_result_dict['concat'][jdx])
#		#					result_dict['episode_numbers'].append(str(i['episode']))
#		#					result_dict['pack_paths'].append(new_result_dict['pack_path'][jdx])
#		#					result_dict['concat'].append(new_result_dict['concat'][jdx])
#		#					result_dict['alternate_title'].append(new_result_dict['alternate_title'][jdx])
#		#					update_flag = True
#		#if update_flag == True:
#		#	new_result_dict = result_dict
#
#		#tools.write_all_text(path, str(result_dict))
#		return new_result_dict
#"""



def unique(list1):
	from functools import reduce
	# Print directly by using * symbol
	ans = reduce(lambda re, x: re+[x] if x not in re else re, list1, [])
	return list(ans)

#def match_episodes_season_pack1(meta, sorted_torr_info):
#	now = time.time()
#	url = str(sorted_torr_info[0]) + 'season___' +str(meta['episode_meta']['season']) + 'meta_source__None'
#	folder = 'show_filters'
#	cache_days = 7
#	url = url.encode('utf-8')
#	hashed_url = hashlib.md5(url).hexdigest()
#	cache_path = os.path.join(tools.ADDON_USERDATA_PATH, folder)
#
#	if not os.path.exists(cache_path):
#		os.mkdir(cache_path)
#	cache_seconds = int(cache_days * 86400.0)
#	path = os.path.join(cache_path, '%s.txt' % hashed_url)
#	if os.path.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
#		results = tools.read_all_text(path)
#		results = eval(results)
#		return results
#	else:
#		#sys.path.append(current_directory)
#		#try:
#		#	import daetutil, babelfish, rebulk, guessit
#		#	from guessit import api
#		#except:
#		#	from a4kscrapers_wrapper import dateutil, babelfish, rebulk, guessit
#		#	from a4kscrapers_wrapper.guessit import api
#
#		last_episode_tmdb = int(meta['tmdb_seasons']['episodes'][-1]['episode'])
#		last_episode_tvmaze = int(meta['tvmaze_seasons']['episodes'][-1]['episode'])
#		season = int(meta['tvmaze_seasons']['episodes'][-1]['season'])
#		
#		folders = unique([item['pack_path'].replace(os.path.basename(item['pack_path']),'') for item in sorted_torr_info])
#		season_path = None
#		for i in folders:
#			#guess = api.guessit(i)
#			guess = get_guess(i)
#			if guess.get('season') == int(season):
#				season_path = i
#				break
#
#		#tools.log(sorted_torr_info)
#		#tools.log(len(simple_info_tmdb), len(simple_info_tvmaze))
#		#tools.log(folders)
#		#exit()
#
#		#for idx, x in enumerate(meta['tvmaze_seasons']['episodes']):
#		#for idx, x in enumerate(meta['tmdb_seasons']['episodes']):
#
#		result_dict = {}
#		result_dict['episode_numbers'] = []
#		result_dict['torr_episode_numbers'] = []
#		result_dict['pack_paths'] = []
#		result_dict['concat'] = []
#		result_dict['alternate_title'] = []
#		#result_dict['concat'].append({'meta_source': meta_source, 'tmdb': meta['tmdb'],'season': meta['episode_meta']['season'], 'episode_number': str(i), 'pack_path': j['pack_path'], 'alternate_title': test2['alternate_title']})
#
#		guessit_list = []
#		start_index = -1
#		end_index = -1
#		options = {'type': 'episode'}
#		for idx, i in enumerate(sorted_torr_info):
#			pack_path = os.path.basename(i['pack_path'])
#			if season_path:
#				if not season_path in str(i['pack_path']):
#					continue
#			#guess = api.guessit(pack_path, options)
#			guess = get_guess(pack_path, options)
#			guessit_list.append([guess, idx, []])
#			guess_season = guess.get('season')
#			guess_episode = []
#			guess_title = guess.get('title')
#			if guess.get('episode') == None:
#				continue
#			if not 'int' in  str(type(guess.get('episode'))):
#				for x in guess.get('episode'):
#					guess_episode.append(x)
#			else:
#				guess_episode.append(guess.get('episode'))
#
#			for x in guess_episode:
#				guessit_list[-1][-1].append(x)
#				if guess_season == season and x == 1:
#					start_index = idx
#				if guess_season == season and x == last_episode_tmdb:
#					if not end_index:
#						end_index = idx
#					elif end_index and idx > end_index:
#						end_index = idx
#				if guess_season == season and x == last_episode_tvmaze:
#					if not end_index:
#						end_index = idx
#					elif end_index and idx > end_index:
#						end_index = idx
#
#		if len(meta['tvmaze_seasons']['episodes']) == (1+(end_index-start_index)):
#			meta_source = 'tvmaze_seasons'
#		elif len(meta['tmdb_seasons']['episodes']) == (1+(end_index-start_index)):
#			meta_source = 'tmdb_seasons'
#		elif len(meta['tmdb_seasons']['episodes']) < (1+(end_index-start_index)):
#			meta_source = 'tvmaze_seasons'
#		else:
#			meta_source = 'tmdb_seasons'
#
#		used_eps = []
#		for xdx, x in enumerate(meta[meta_source]['episodes']):
#			ep_title = x['name'].lower()
#			ep_title = re.sub("[\x00-\x2F\x3A-\x40\x5B-\x60\x7B-\x7F]+", " ", ep_title.lower())
#			if xdx in used_eps:
#				continue
#			for gdx, i in enumerate(guessit_list):
#				idx = i[1]
#				episode_title = i[0].get('episode_title')
#				if episode_title:
#					episode_title = re.sub("[\x00-\x2F\x3A-\x40\x5B-\x60\x7B-\x7F]+", " ", episode_title.lower())
#				else:
#					continue
#				if ep_title == episode_title:
#					for y in i[-1]:
#						used_eps.append(xdx)
#						result_dict['episode_numbers'].append(x['episode'])
#						result_dict['torr_episode_numbers'].append(y)
#						result_dict['pack_paths'].append(sorted_torr_info[idx]['pack_path'])
#						result_dict['alternate_title'].append([ep_title,episode_title])
#						result_dict['concat'].append({'meta_source': meta_source, 'tmdb': meta['tmdb'],'season': meta['episode_meta']['season'], 'episode_number': x['episode'], 'torr_episode_numbers': y, 'pack_path': sorted_torr_info[idx]['pack_path'], 'alternate_title': [ep_title,episode_title]})
#					break
#
#		for xdx, x in enumerate(meta[meta_source]['episodes']):
#			ep_title = x['name'].lower()
#			ep_title = re.sub("[\x00-\x2F\x3A-\x40\x5B-\x60\x7B-\x7F]+", " ", ep_title.lower())
#			if xdx in used_eps:
#				continue
#			for gdx, i in enumerate(guessit_list):
#				idx = i[1]
#				#episode_title = i[0].get('episode_title')
#				#if episode_title:
#				#	episode_title = re.sub("[\x00-\x2F\x3A-\x40\x5B-\x60\x7B-\x7F]+", " ", episode_title.lower())

#				if i[0].get('episode') == None:
#					continue
#				else:
#					break_flag = False
#					for y in i[-1]:
#						if x['episode'] == y and x['season'] == i[0].get('season'):
#							used_eps.append(xdx)
#							result_dict['episode_numbers'].append(x['episode'])
#							result_dict['torr_episode_numbers'].append(y)
#							result_dict['pack_paths'].append(sorted_torr_info[idx]['pack_path'])
#							result_dict['alternate_title'].append([ep_title,episode_title])
#							result_dict['concat'].append({'meta_source': meta_source, 'tmdb': meta['tmdb'],'season': meta['episode_meta']['season'], 'episode_number': x['episode'], 'torr_episode_numbers': y, 'pack_path': sorted_torr_info[idx]['pack_path'], 'alternate_title': [ep_title,episode_title]})
#							break_flag = True
#					if break_flag == True:
#						break
#		for i in result_dict:
#			tools.log(i, result_dict[i])
#		#tools.log(json.dumps(result_dict, indent=2))
#
#		return result_dict

def match_episodes_season_pack(meta, sorted_torr_info):
	now = time.time()
	url = str(sorted_torr_info[0]) + 'season___' +str(meta['episode_meta']['season']) + 'meta_source__None'
	folder = 'show_filters'
	cache_days = 7
	url = url.encode('utf-8')
	hashed_url = hashlib.md5(url).hexdigest()
	cache_path = os.path.join(tools.ADDON_USERDATA_PATH, folder)

	if not os.path.exists(cache_path):
		os.mkdir(cache_path)
	cache_seconds = int(cache_days * 86400.0)
	path = os.path.join(cache_path, '%s.txt' % hashed_url)
	if os.path.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
		results = tools.read_all_text(path)
		results = eval(results)
		return results
	else:
		#sys.path.append(current_directory)
		#try:
		#	import daetutil, babelfish, rebulk, guessit
		#	from guessit import api
		#except:
		#	from a4kscrapers_wrapper import dateutil, babelfish, rebulk, guessit
		#	from a4kscrapers_wrapper.guessit import api

		last_episode_tmdb = int(meta['tmdb_seasons']['episodes'][-1]['episode'])
		last_episode_tvmaze = int(meta['tvmaze_seasons']['episodes'][-1]['episode'])
		season = int(meta['tvmaze_seasons']['episodes'][-1]['season'])
		
		folders = unique([item['pack_path'].replace(os.path.basename(item['pack_path']),'') for item in sorted_torr_info])
		season_path = None
		for i in folders:
			#guess = api.guessit(i)
			guess = get_guess(i)
			if guess.get('season') == int(season):
				season_path = i
				break

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
		for idx, i in enumerate(sorted_torr_info):
			pack_path = os.path.basename(i['pack_path'])
			if season_path:
				if not season_path in str(i['pack_path']):
					continue
			#guess = api.guessit(pack_path, options)
			guess = get_guess(pack_path, options)
			guessit_list.append([guess, idx, []])
			guess_season = guess.get('season')
			guess_episode = []
			guess_title = guess.get('title')
			if guess.get('episode') == None:
				continue
			if not 'int' in  str(type(guess.get('episode'))):
				for x in guess.get('episode'):
					guess_episode.append(x)
			else:
				guess_episode.append(guess.get('episode'))

			for x in guess_episode:
				guessit_list[-1][-1].append(x)
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

		#tools.log(end_index, start_index)
		if len(meta['tvmaze_seasons']['episodes']) == (1+(end_index-start_index)):
			meta_source = 'tvmaze_seasons'
		elif len(meta['tmdb_seasons']['episodes']) == (1+(end_index-start_index)):
			meta_source = 'tmdb_seasons'
		elif len(meta['tmdb_seasons']['episodes']) < (1+(end_index-start_index)):
			meta_source = 'tvmaze_seasons'
		else:
			meta_source = 'tmdb_seasons'

		matched_episodes = {}
		for xdx, x in enumerate(meta[meta_source]['episodes']):
			ep_title = x['name'].lower()
			ep_title = re.sub("[\x00-\x2F\x3A-\x40\x5B-\x60\x7B-\x7F]+", " ", ep_title.lower())
			for gdx, i in enumerate(guessit_list):
				idx = i[1]
				episode_title = i[0].get('episode_title')
				if episode_title:
					episode_title = re.sub("[\x00-\x2F\x3A-\x40\x5B-\x60\x7B-\x7F]+", " ", episode_title.lower())
				else:
					continue
				if ep_title == episode_title or str(ep_title) in str(episode_title) or str(episode_title) in str(ep_title) or distance.jaro_similarity(ep_title, episode_title) > 0.925:
					for y in i[-1]:
						try:
							if not sorted_torr_info[idx]['pack_path'] in matched_episodes[int(x['episode'])]:
								matched_episodes[int(x['episode'])].append(sorted_torr_info[idx]['pack_path'])
						except: 
							matched_episodes[int(x['episode'])] = []
							matched_episodes[int(x['episode'])].append(sorted_torr_info[idx]['pack_path'])

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
					if ep_title == episode_title or str(ep_title) in str(episode_title) or str(episode_title) in str(ep_title) or distance.jaro_similarity(ep_title, episode_title) > 0.925:
						if guess_episode == i and guess_season == int(meta[meta_source]['episodes'][int(i)-1]['season']):
							match = True
						elif part_number_title == part_number_release:
							match = True
					if match == True:
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
				result_dict['episode_numbers'].append(i)
				result_dict['alt_ep_num'].append(guess_episode)
				result_dict['pack_paths'].append(matched_episodes[i][0])
				result_dict['concat'].append({'meta_source': meta_source, 'tmdb': meta['tmdb'],'season': meta['episode_meta']['season'], 'episode_number': i, 'pack_path': pack_path, 'alt_ep_num': guess_episode })


		#for i in result_dict:
		#	tools.log(i, result_dict[i])
		tools.write_all_text(path, str(result_dict))
		return result_dict