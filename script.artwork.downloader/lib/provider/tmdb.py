#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2011-2014 Martijn Kaijser
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

#import modules
import xbmc
import xbmcaddon
import sys

### import libraries
from lib.language import *
from lib.script_exceptions import NoFanartError
from lib.utils import *
from operator import itemgetter

### get addon info
__localize__    = ( sys.modules[ "__main__" ].__localize__ )
__addon__ = xbmcaddon.Addon()
api_key_tmdb = __addon__.getSetting("api_key_themoviedb")       #Added by @burekas

API_KEY = api_key_tmdb
API_CFG = 'http://api.themoviedb.org/3/configuration?api_key=%s'
API_URL = 'http://api.themoviedb.org/3/%s/%s/images?api_key=%s'  ####### @burekas

class TMDBProvider(): 

    def __init__(self):
        self.name = 'TMDB'	

    def get_image_list(self, media_type, media_id):  ####### @burekas
        log('TMDB API get images:')		
        image_list = []
        api_cfg = get_data(API_CFG%(API_KEY), 'json')
        if api_cfg == "Empty" or not api_cfg:
            return image_list
        BASE_IMAGEURL = api_cfg['images'].get('base_url')
        if media_type == 'tvshow': ####### @burekas
            media_type = 'tv'      ####### @burekas
        data = get_data(API_URL%(media_type,media_id, API_KEY), 'json') ####### @burekas
        if data == "Empty" or not data:
            return image_list
        else:
            # Get fanart
            try:
                for item in data['backdrops']:
                    if int(item.get('vote_count')) >= 1:
                        rating = float( "%.1f" % float( item.get('vote_average'))) #output string with one decimal
                        votes = item.get('vote_count','n/a')
                    else:
                        rating = 'n/a'
                        votes = 'n/a'
                    image_list.append({'url': BASE_IMAGEURL + 'original' + item['file_path'],
                                       'preview': BASE_IMAGEURL + 'w300' + item['file_path'],
                                       #'id': 'TMDB_' + item.get('file_path').lstrip('/').replace('.jpg', ''),         ####### @burekas
                                       'id': '[TMDB] ' + item.get('file_path')[item.get('file_path').rfind('/')+1:],   ####### @burekas
                                       'art_type': ['fanart','extrafanart'],
                                       'height': item.get('height'),
                                       'width': item.get('width'),
                                       'language': item.get('iso_639_1','n/a'),
                                       'rating': rating,
                                       'votes': votes,
                                       # Create Gui string to display
                                       'generalinfo': ('%s: %s  |  %s: %s  |  %s: %s  |  %s: %sx%s  |  ' 
                                                       %( __localize__(32141), get_language(item.get('iso_639_1','n/a')).capitalize(),
                                                          __localize__(32142), rating,
                                                          __localize__(32143), votes,
                                                          __localize__(32145), item.get('width'), item.get('height')))})
            except Exception as e:
                log( 'Problem report: %s' %str( e ), xbmc.LOGNOTICE )
            # Get thumbs
            try:
                for item in data['backdrops']:
                    if int(item.get('vote_count')) >= 1:
                        rating = float( "%.1f" % float( item.get('vote_average'))) #output string with one decimal
                        votes = item.get('vote_count','n/a')
                    else:
                        rating = 'n/a'
                        votes = 'n/a'
                    # Fill list
                    image_list.append({'url': BASE_IMAGEURL + 'w780' + item['file_path'],
                                       'preview': BASE_IMAGEURL + 'w300' + item['file_path'],
                                       #'id': 'TMDB_' + item.get('file_path').lstrip('/').replace('.jpg', ''),         ####### @burekas
                                       'id': '[TMDB] ' + item.get('file_path')[item.get('file_path').rfind('/')+1:],   ####### @burekas
                                       'art_type': ['extrathumbs'],
                                       'height': item.get('height'),
                                       'width': item.get('width'),
                                       'language': item.get('iso_639_1','n/a'),
                                       'rating': rating,
                                       'votes': votes,
                                       # Create Gui string to display
                                       'generalinfo': ('%s: %s  |  %s: %s  |  %s: %s  |  %s: %sx%s  |  ' 
                                                       %( __localize__(32141), get_language(item.get('iso_639_1','n/a')).capitalize(),
                                                          __localize__(32142), rating,
                                                          __localize__(32143), votes,
                                                          __localize__(32145), item.get('width'), item.get('height')))})
            except Exception as e:
                log( 'Problem report: %s' %str( e ), xbmc.LOGNOTICE )
            # Get posters
            try:
                for item in data['posters']:
                    if int(item.get('vote_count')) >= 1:
                        rating = float( "%.1f" % float( item.get('vote_average'))) #output string with one decimal
                        votes = item.get('vote_count','n/a')
                    else:
                        rating = 'n/a'
                        votes = 'n/a'
                    # Fill list
                    image_list.append({'url': BASE_IMAGEURL + 'original' + item['file_path'],
                                       'preview': BASE_IMAGEURL + 'w185' + item['file_path'],
                                       #'id': 'TMDB_' + item.get('file_path').lstrip('/').replace('.jpg', ''),         ####### @burekas
                                       'id': '[TMDB] ' + item.get('file_path')[item.get('file_path').rfind('/')+1:],   ####### @burekas
                                       'art_type': ['poster'],
                                       'height': item.get('height'),
                                       'width': item.get('width'),
                                       'language': item.get('iso_639_1','n/a'),
                                       'rating': rating,
                                       'votes': votes,
                                       # Create Gui string to display
                                       'generalinfo': ('%s: %s  |  %s: %s  |  %s: %s  |  %s: %sx%s  |  ' 
                                                       %( __localize__(32141), get_language(item.get('iso_639_1','n/a')).capitalize(),
                                                          __localize__(32142), rating,
                                                          __localize__(32143), votes,
                                                          __localize__(32145), item.get('width'), item.get('height')))})
            except Exception as e:
                log( 'Problem report: %s' %str( e ), xbmc.LOGNOTICE )
            if image_list == []:
                raise NoFanartError(media_id)
            else:
                # Sort the list before return. Last sort method is primary
                #image_list = sorted(image_list, key=itemgetter('rating'), reverse=True)
                image_list = sorted(image_list, key=lambda x : str(x['rating']), reverse=True)
                #image_list = sorted(image_list, key=itemgetter('language'))
                image_list = sorted(image_list, key=lambda x: x['language'] or "" )
                return image_list


def _search_movie(medianame,year=''):
    #medianame = normalize_string(medianame)
    log('TMDB API search criteria: Title[''%s''] | Year[''%s'']' % (medianame,year) )
    illegal_char = ' -<>:"/\|?*%'
    for char in illegal_char:
        medianame = medianame.replace( char , '+' ).replace( '++', '+' ).replace( '+++', '+' )

    #search_url = "https://api.tmdb.org/3/search/movie?api_key=%s&query=%s&year=%s"%(API_KEY,urllib.parse.quote(medianame),year)
    search_url = "https://api.themoviedb.org/3/search/movie?api_key=%s&query=%s&year=%s"%(API_KEY,urllib.parse.quote(medianame),year)
    tmdb_id = ''
    log('TMDB API search Movie:   %s ' % search_url)
    try:
        data = get_data(search_url, 'json')
        if data == "Empty":
            tmdb_id = ''
        else:
            for item in data['results']:
                if item['id']:
                    tmdb_id = item['id']
                    break
    except Exception as e:
        log( str( e ), xbmc.LOGERROR )
    if tmdb_id == '':
        log('TMDB API search found no ID for the movie: %s' %medianame )
    else:
        log('TMDB API search found ID: %s for the movie: %s' %(tmdb_id,item['title']))
    return tmdb_id


def _search_tv(medianame,year=''):   ####### @burekas
    #medianame = normalize_string(medianame)
    log('TMDB API search criteria: Title[''%s''] | Year[''%s'']' % (medianame,year) )
    illegal_char = ' -<>:"/\|?*%'
    for char in illegal_char:
        medianame = medianame.replace( char , '+' ).replace( '++', '+' ).replace( '+++', '+' )

    #search_url = 'http://api.tmdb.org/3/search/tv?query=%s&api_key=%s' %( medianame, API_KEY )
    search_url = 'http://api.themoviedb.org/3/search/tv?query=%s&api_key=%s' %( medianame, API_KEY )
    tmdb_id = ''
    log('TMDB API search TV:   %s ' % search_url)
    try:
        data = get_data(search_url, 'json')
        if data == "Empty":
            tmdb_id = ''
        else:
            if year:
                year = int(year)
                for item in data['results']:
                    aired_year = int(item['first_air_date'].split('-')[0].strip())
                    if aired_year == year:			
                        if item['id']:
                            tmdb_id = item['id']
                            break
    except Exception as e:
        log( str( e ), xbmc.LOGERROR )
    
    if tmdb_id == '':
        log('TMDB API search found no ID for TV Show: %s' %medianame)
    else:
        log('TMDB API search found ID: %s for TV Show: %s' % (tmdb_id, item['name']))
    return tmdb_id