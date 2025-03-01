import xbmc, xbmcaddon, xbmcgui, xbmcvfs
from threading import Thread
import datetime
import time
import json
import re
import requests
from resources.lib import library
from resources.lib import Utils
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib.library import get_trakt_data
from resources.lib.WindowManager import wm
import gc
import os
from pathlib import Path

from resources.lib import TheMovieDB
from urllib.parse import urlencode, quote, quote_plus, unquote, unquote_plus

#from resources import PTN
from a4kscrapers_wrapper import source_tools
from source_tools import get_guess
import functools

import sqlite3

from resources.lib.library import trakt_calendar_list
from resources.lib import process
#from diamond_rd_player import next_ep_play
#from diamond_rd_player import get_next_ep_details

from a4kwrapper_player import next_ep_play
from a4kwrapper_player import get_next_ep_details

#global percentage
ServiceStop = ''
#xbmc.executebuiltin('RunScript('+str(addon_ID())+',info=service2)')
Utils.hide_busy()

from inspect import currentframe, getframeinfo

def restart_service_monitor():
    if ServiceStarted == 'True':
        while ServiceStop == '':
            self.xbmc_monitor.waitForAbort(1)
        #wait_for_property('ServiceStop', value='True', set_property=True)  # Stop service
    #wait_for_property('ServiceStop', value=None)  # Wait until Service clears property
    while ServiceStop != '':
        self.xbmc_monitor.waitForAbort(1)
    Thread(target=ServiceMonitor().run).start()

class MyMonitor(xbmc.Monitor):

    def onNotification(self, sender, method, data):

        if sender == addon_ID_short():
            command_info = json.loads(data)
            xbmc.log(str(command_info)+'onNotification===>OPEN_INFO', level=xbmc.LOGINFO)
            container = command_info['command_params']['container']
            position = command_info['command_params']['position']
            xbmc.sleep(550)
            xbmc.executebuiltin('SetFocus('+str(container)+','+str(position)+')')
            #x = 0
            #while container != xbmc.getInfoLabel('System.CurrentControlId') and x < 5000:
            #    x = x + 50
            #    if container == xbmc.getInfoLabel('System.CurrentControlId'):
            #        xbmc.sleep(150)
            #        xbmc.executebuiltin('SetFocus('+str(container)+','+str(position)+')')
            #    xbmc.sleep(50)

class PlayerMonitor(xbmc.Player):
    
    def __init__(self):
        xbmc.Player.__init__(self)
        self.player = xbmc.Player()
        #self.playerstring = None
        #self.property_prefix = 'Player'
        #self.reset_properties()

    def movietitle_to_id(self, title):
        query = {
            "jsonrpc": "2.0",
            "method": "VideoLibrary.GetMovies",
            "params": {
                "properties": ["title"]
            },
            "id": "libMovies"
        }
        try:
            jsonrpccommand=json.dumps(query, encoding='utf-8')    
            rpc_result = xbmc.executeJSONRPC(jsonrpccommand)
            json_result = json.loads(rpc_result)
            if 'result' in json_result and 'movies' in json_result['result']:
                json_result = json_result['result']['movies']
                for movie in json_result:
                    # Switch to ascii/lowercase and remove special chars and spaces
                    # to make sure best possible compare is possible
                    titledb = movie['title'].encode('ascii', 'ignore')
                    titledb = re.sub(r'[?|$|!|:|#|\.|\,|\'| ]', r'', titledb).lower().replace('-', '')
                    if '(' in titledb:
                        titledb = titledb.split('(')[0]
                    titlegiven = title.encode('ascii','ignore')
                    titlegiven = re.sub(r'[?|$|!|:|#|\.|\,|\'| ]', r'', titlegiven).lower().replace('-', '')
                    if '(' in titlegiven:
                        titlegiven = titlegiven.split('(')[0]
                    if titledb == titlegiven:
                        return movie['movieid']
            return '-1'
        except Exception:
            return '-1' 

    def trakt_scrobble_details(self, trakt_watched=None, movie_title=None, movie_year=None, resume_position=None, resume_duration=None, tmdb_id=None, tv_title=None, season=None, episode=None):
        trakt_meta = {}
        trakt_meta['trakt_watched']=trakt_watched
        trakt_meta['movie_title']=movie_title
        trakt_meta['movie_year']=movie_year
        trakt_meta['resume_position']=resume_position
        trakt_meta['resume_duration']=resume_duration
        trakt_meta['tmdb_id']=tmdb_id
        trakt_meta['tv_title']=tv_title
        trakt_meta['season']=season
        trakt_meta['episode']=episode
        xbmcgui.Window(10000).setProperty('trakt_scrobble_details',json.dumps(trakt_meta, sort_keys=True))

    def get_trakt_scrobble_details(self):
        try: trakt_meta = json.loads(xbmcgui.Window(10000).getProperty('trakt_scrobble_details'))
        except: return {}
        return trakt_meta

    def trakt_scrobble_title(self, movie_title, movie_year, percent, action=None):
        global trakt_method
        trakt_method = {}
        trakt_method['function'] = 'trakt_scrobble_title'
        trakt_method['movie_title'] = movie_title
        trakt_method['movie_year'] = movie_year
        trakt_method['percent'] = None

        #headers = library.trak_auth()
        response = TheMovieDB.get_tmdb_data('search/movie?query=%s&year=%s&language=en-US&include_adult=%s&' % (movie_title,str(movie_year), xbmcaddon.Addon().getSetting('include_adults')), 30)
        #url = 'https://api.themoviedb.org/3/search/movie?api_key='+str(tmdb_api)+'&query=' +str(movie_title) + '&language=en-US&include_image_language=en,null&year=' +str(movie_year)
        #response = requests.get(url).json()
        tmdb_id = response['results'][0]['id']

        #response = requests.get('https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=movie', headers=headers).json()
        response = get_trakt_data(url='https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=movie', cache_days=7)
        trakt = response[0]['movie']['ids']['trakt']
        slug = response[0]['movie']['ids']['slug']
        imdb = response[0]['movie']['ids']['imdb']
        tmdb = response[0]['movie']['ids']['tmdb']
        year = response[0]['movie']['year']
        try:
            title = response[0]['movie']['title']
        except:
            title = str(u''.join(response[0]['movie']['title']).encode('utf-8').strip())

        values = """
          {
            "movie": {
              "title": """+'"'+title+'"'+ """,
              "year": """+str(year)+""",
              "ids": {
                "trakt": """+str(trakt)+""",
                "slug": """+'"'+slug+'"'+ """,
                "imdb": """+'"'+imdb+'"'+ """,
                "tmdb": """+str(tmdb)+"""
              }
            },
            "progress": """+str(percent)+""",
            "app_version": "1.0",
            "app_date": "2014-09-22"
          }
        """
        if not action:
            action = 'start'
            if percent > 80:
                action = 'stop'

        #response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=headers)
        response = None
        count = 0
        while response == None and count < 20:
            count = count + 1
            try:
                response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=headers)
                test_var = response.json()
            except: 
                response = None
    #    xbmc.log(str(response.json())+'===>TRAKT_SCROBBLE_TITLE____OPEN_INFO', level=xbmc.LOGFATAL)
        if percent == 1 or percent >= 84: 
            xbmc.log(str(response.json())+'===>TRAKT_SCROBBLE_TITLE____OPEN_INFO', level=xbmc.LOGFATAL)
        try:
            return response.json()
        except:
            return response

    def trakt_scrobble_tmdb(self, tmdb_id, percent, action=None):
        global trakt_method
        trakt_method = {}
        trakt_method['function'] = 'trakt_scrobble_tmdb'
        trakt_method['tmdb_id'] = tmdb_id
        trakt_method['percent'] = None
        #headers = library.trak_auth()

        #response = requests.get('https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=movie', headers=headers).json()
        response = get_trakt_data(url='https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=movie', cache_days=7)
        trakt = response[0]['movie']['ids']['trakt']
        slug = response[0]['movie']['ids']['slug']
        imdb = response[0]['movie']['ids']['imdb']
        tmdb = response[0]['movie']['ids']['tmdb']
        year = response[0]['movie']['year']
        #try:
        #    title = response[0]['movie']['title']
        #except:
        #    title = str(u''.join(response[0]['movie']['title']).encode('utf-8').strip())


        values = """
          {
            "movie": {
              "year": """+str(year)+""",
              "ids": {
                "trakt": """+str(trakt)+""",
                "slug": """+'"'+slug+'"'+ """,
                "imdb": """+'"'+imdb+'"'+ """,
                "tmdb": """+str(tmdb)+"""
              }
            },
            "progress": """+str(percent)+""",
            "app_version": "1.0",
            "app_date": "2014-09-22"
          }
        """

        '''
        try:
            values = """
              {
                "movie": {
                  "title": """+'"'+title+'"'+ """,
                  "year": """+str(year)+""",
                  "ids": {
                    "trakt": """+str(trakt)+""",
                    "slug": """+'"'+slug+'"'+ """,
                    "imdb": """+'"'+imdb+'"'+ """,
                    "tmdb": """+str(tmdb)+"""
                  }
                },
                "progress": """+str(percent)+""",
                "app_version": "1.0",
                "app_date": "2014-09-22"
              }
            """
        except:
            values = """
              {
                "movie": {
                  "year": """+str(year)+""",
                  "ids": {
                    "trakt": """+str(trakt)+""",
                    "slug": """+'"'+slug+'"'+ """,
                    "imdb": """+'"'+imdb+'"'+ """,
                    "tmdb": """+str(tmdb)+"""
                  }
                },
                "progress": """+str(percent)+""",
                "app_version": "1.0",
                "app_date": "2014-09-22"
              }
            """
        '''

        if not action:
            action = 'start'
            if percent > 80:
                action = 'stop'
        response = None
        #xbmc.log(str('https://api.trakt.tv/scrobble/' + str(action))+'===>TRAKT_SCROBBLE_TMDB____OPEN_INFO', level=xbmc.LOGFATAL)
        #xbmc.log(str(values)+'===>TRAKT_SCROBBLE_TMDB____OPEN_INFO', level=xbmc.LOGFATAL)
        #xbmc.log(str(headers)+'===>TRAKT_SCROBBLE_TMDB____OPEN_INFO', level=xbmc.LOGFATAL)
        response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=headers)
        #xbmc.log(str(response)+'===>TRAKT_SCROBBLE_TMDB____OPEN_INFO', level=xbmc.LOGFATAL)
        count = 0
        while response == None and count < 20:
            count = count + 1
            try:
                response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=headers)
                test_var = response.json()
            except: 
                response = None
    #    xbmc.log(str(response.json())+'===>TRAKT_SCROBBLE_TMDB____OPEN_INFO', level=xbmc.LOGFATAL)
        if percent == 1 or percent >= 84: 
            try:    xbmc.log(str(response.json())+'===>TRAKT_SCROBBLE_TMDB____OPEN_INFO', level=xbmc.LOGFATAL)
            except: pass
        try:
            return response.json()
        except:
            return response

    def trakt_scrobble_tv(self, title, season, episode, percent, action=None):
        #headers = library.trak_auth()
        global trakt_method
        trakt_method = {}
        trakt_method['function'] = 'trakt_scrobble_tv'
        trakt_method['title'] = title
        trakt_method['season'] = season
        trakt_method['episode'] = episode
        trakt_method['percent'] = None

        if 'tmdb_id=' in str(title):
            tmdb_id = str(title).replace('tmdb_id=','')
            #response = requests.get('https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show', headers=headers).json()
            response = get_trakt_data(url='https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show', cache_days=7)
            tvdb = response[0]['show']['ids']['tvdb']
            imdb = response[0]['show']['ids']['imdb']
            trakt = response[0]['show']['ids']['trakt']
            title = response[0]['show']['title']
            year = response[0]['show']['year']
        else:
            #response = requests.get('https://api.trakt.tv/search/show?query='+str(title), headers=headers).json()
            response = get_trakt_data(url='https://api.trakt.tv/search/show?query='+str(title), cache_days=7)
            #print(response[0])
            trakt = response[0]['show']['ids']['trakt']
            tvdb = response[0]['show']['ids']['tvdb']
            year = response[0]['show']['year']
            try:
                title = response[0]['show']['title']
            except:
                title = str(u''.join(response[0]['show']['title']).encode('utf-8').strip())

        values = """
          {
            "show": {
              "title": """+'"'+title+'"'+ """,
              "year": """+str(year)+""",
              "ids": {
                "trakt": """+str(trakt)+""",
                "tvdb": """+str(tvdb)+"""
              }
            },
            "episode": {
              "season": """+str(season)+""",
              "number": """+str(episode)+"""
            },
            "progress": """+str(percent)+""",
            "app_version": "1.0",
            "app_date": "2014-09-22"
          }
        """
        if not action:
            action = 'start'
            if percent > 80:
                action = 'stop'
        #response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=headers)
        response = None
        count = 0
        while response == None and count < 20:
            count = count + 1
            try:
                response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=headers)
                test_var = response.json()
            except: 
                response = None
        if percent == 1 or percent >= 84: 
            try: xbmc.log(str(response.json())+'===>TRAKT_SCROBBLE_TV____OPEN_INFO', level=xbmc.LOGFATAL)
            except: pass
        try:
            return response.json()
        except:
            return response

    def trakt_meta_scrobble(self, action):
        trakt_scrobble = str(xbmcaddon.Addon(library.addon_ID()).getSetting('trakt_scrobble'))
        #trakt_meta = self.get_trakt_scrobble_details()
        try: 
            trakt_meta = self.get_trakt_scrobble_details()
        except: 
            xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
            return
        trakt_watched = trakt_meta.get('trakt_watched') 
        #if trakt_meta.get('resume_position') ==None:
        #    return
        #xbmcgui.Window(10000).clearProperty('trakt_scrobble_details')
        #xbmc.log(str(trakt_meta)+'trakt_scrobble_details===>___OPEN_INFO', level=xbmc.LOGINFO)
        response = None
        try: 
            percentage = (trakt_meta.get('resume_position') / trakt_meta.get('resume_duration')) * 100
        except: 
            percentage = 0
            xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
        if (percentage > 90 and xbmcgui.Window(10000).getProperty('Next_EP.ResolvedUrl') == 'true') or percentage == 0:
            xbmc.log(str('Next_EP.ResolvedUrl==TRUE')+'===>OPENINFO', level=xbmc.LOGINFO)
            if trakt_watched == 'true':
                return
            else:
                xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
        if percentage > 5 and percentage < 80:
            percentage = percentage -1
        if percentage >= 80:
            action = 'stop'
            trakt_watched = 'true'
        if trakt_meta.get('tmdb_id') == None and trakt_scrobble != 'false':
            if trakt_meta.get('episode') != None:
                response = self.trakt_scrobble_tv(title=trakt_meta.get('tv_title'), season=trakt_meta.get('season'), episode=trakt_meta.get('episode'), percent=percentage,action=action)
            if trakt_meta.get('movie_title') != None:
                response = self.trakt_scrobble_title(movie_title=trakt_meta.get('movie_title'), movie_year=trakt_meta.get('movie_year'), percent=percentage, action=action)
        if trakt_meta.get('tmdb_id') != None and trakt_scrobble != 'false':
            if trakt_meta.get('episode') != None:
                response = self.trakt_scrobble_tv(title='tmdb_id='+str(trakt_meta.get('tmdb_id')), season=trakt_meta.get('season'), episode=trakt_meta.get('episode'), percent=percentage,action=action)
            else:
                response = self.trakt_scrobble_tmdb(tmdb_id=trakt_meta.get('tmdb_id'),percent=percentage,action=action)
        return trakt_watched
        #xbmc.log(str(response)+'trakt_scrobble===>OPENINFO', level=xbmc.LOGINFO)

    def reopen_window(self):
        trakt_scrobble = str(xbmcaddon.Addon(library.addon_ID()).getSetting('trakt_scrobble'))
        reopen_window_bool = str(xbmcaddon.Addon(library.addon_ID()).getSetting('reopen_window_bool'))
        window_stack_enable = str(xbmcaddon.Addon(library.addon_ID()).getSetting('window_stack_enable'))
        window_open = xbmcgui.Window(10000).getProperty(str(addon_ID_short())+'_running')
        diamond_info_started = xbmcgui.Window(10000).getProperty('diamond_info_started')
        Next_EP_ResolvedUrl = xbmcgui.Window(10000).getProperty('Next_EP.ResolvedUrl')
        #xbmc.log(str(Next_EP_ResolvedUrl)+'=Next_EP_ResolvedUrl===>PENINFO', level=xbmc.LOGINFO)
        xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
        if window_stack_enable == 'true' and (window_open == 'False' or diamond_info_started == 'True'):
            xbmc.sleep(100)
            if xbmc.Player().isPlaying()==0:
                if xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True':
                    #return wm.open_video_list(search_str='', mode='reopen_window')
                    #xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
                    xbmc.sleep(1000)
                    wm.pop_stack()
                    diamond_info_started = False
                    xbmcgui.Window(10000).setProperty('diamond_info_started',str(diamond_info_started))
                    return
                else:
                    return
        elif reopen_window_bool == 'true' and xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True' and not xbmc.getCondVisibility('Window.IsActive(10138)'):
            xbmc.sleep(100)
            if not xbmc.getCondVisibility('Window.IsActive(10138)') and xbmc.Player().isPlaying()==0:
                if xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True':
                    diamond_info_started = False
                    xbmcgui.Window(10000).setProperty('diamond_info_started',str(diamond_info_started))
                    #xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
                    xbmc.executebuiltin('RunScript(%s,info=reopen_window)' % (addon_ID()))
                    return
                else:
                    return

    def onPlayBackEnded(self):
        xbmc.log(str('onPlayBackEnded')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(xbmcgui.Window(10000).getProperty('trakt_scrobble_details'))+'trakt_scrobble_details===>___OPEN_INFO', level=xbmc.LOGINFO)
        reopen_window_bool = str(xbmcaddon.Addon(library.addon_ID()).getSetting('reopen_window_bool'))
        try:
            self.trakt_meta_scrobble(action='pause')
        except:
            pass

        xbmcgui.Window(10000).clearProperty('trakt_scrobble_details')
        var_test = addon_ID_short()+'_running'
        if xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True':
            xbmcgui.Window(10000).setProperty(var_test, 'True')
        else:
            xbmcgui.Window(10000).clearProperty(var_test)

        xbmc.sleep(100)
        gc.collect()
        xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
        self.reopen_window()
        return
        """
        if reopen_window_bool == 'true' and xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True' and not xbmc.getCondVisibility('Window.IsActive(10138)'):
            #from resources.lib.process import reopen_window
            #reopen_window()
            #from resources.lib.WindowManager import wm
            xbmc.sleep(100)
            if not xbmc.getCondVisibility('Window.IsActive(10138)') and xbmc.Player().isPlaying()==0:
                if xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True':
                    diamond_info_started = False
                    xbmcgui.Window(10000).setProperty('diamond_info_started',str(diamond_info_started))
                    xbmc.executebuiltin('RunScript(%s,info=reopen_window)' % (library.addon_ID()))
                    return
                    #return wm.open_video_list(search_str='', mode='reopen_window')
                else:
                    return
        #self.set_watched()
        #self.reset_properties()
        #return wm.pop_stack()
        """

    def onPlayBackStopped(self):
        xbmc.log(str('onPlayBackStopped')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        trakt_scrobble = str(xbmcaddon.Addon(library.addon_ID()).getSetting('trakt_scrobble'))
        reopen_window_bool = str(xbmcaddon.Addon(library.addon_ID()).getSetting('reopen_window_bool'))
        window_stack_enable = str(xbmcaddon.Addon(library.addon_ID()).getSetting('window_stack_enable'))

        self.trakt_meta_scrobble(action='pause')
        trakt_meta = self.get_trakt_scrobble_details()
        xbmcgui.Window(10000).clearProperty('diamond_player_time')
        xbmcgui.Window(10000).clearProperty('Next_EP.ResolvedUrl_playlist')
        xbmcgui.Window(10000).clearProperty('Next_EP.ResolvedUrl')
        xbmcgui.Window(10000).clearProperty('trakt_scrobble_details')
        #var_test = addon_ID_short()+'_running'
        #if xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True':
        #    xbmcgui.Window(10000).setProperty(var_test, 'True')
        #else:
        #    xbmcgui.Window(10000).clearProperty(var_test)

        xbmc.sleep(100)
        gc.collect()
        #self.reopen_window()
        """
        if trakt_scrobble == 'false':
            if reopen_window_bool == 'true' and xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True' and not xbmc.getCondVisibility('Window.IsActive(10138)'):
                #from resources.lib.process import reopen_window
                #reopen_window()
                #from resources.lib.WindowManager import wm
                xbmc.sleep(100)
                if not xbmc.getCondVisibility('Window.IsActive(10138)') and xbmc.Player().isPlaying()==0:
                    if xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True':
                        diamond_info_started = False
                        xbmcgui.Window(10000).setProperty('diamond_info_started',str(diamond_info_started))
                        #return wm.open_video_list(search_str='', mode='reopen_window')
                        xbmc.executebuiltin('RunScript(%s,info=reopen_window)' % (library.addon_ID()))
                        return
                    else:
                        return
            return
        """

        xbmc.log(str('onPlayBackStopped1')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        try: resume_position = trakt_meta.get('resume_position')
        except: resume_position = 0
        try: resume_duration = trakt_meta.get('resume_duration')
        except: resume_duration = 0
        try: percentage = (trakt_meta.get('resume_position') / trakt_meta.get('resume_duration')) * 100
        except: percentage = 0

        global global_movie_flag
        #global resume_position
        #global resume_duration
        global dbID

        #try: percentage = (resume_position / resume_duration) * 100
        #except: percentage = 100

        try: 
            dbID = int(dbID)
            if dbID == 0:
                dbID = None
        except: 
            dbID = None

        try:
            if global_movie_flag == 'true' and dbID != None and percentage < 85 and percentage > 3 and resume_duration > 300:
                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(dbID)+', "resume": {"position":'+str(resume_position)+',"total":'+str(resume_duration)+'}},"id":"1"}')
                json_object  = json.loads(json_result)
                xbmc.log(str(json_object)+'=movie resume set, '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
            if global_movie_flag == 'false' and dbID != None and percentage < 85 and percentage > 3 and resume_duration > 300:
                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+', "resume": {"position":'+str(resume_position)+',"total":'+str(resume_duration)+'}},"id":"1"}')
                json_object  = json.loads(json_result)
                xbmc.log(str(json_object)+'=episode resume set, '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
            if global_movie_flag == 'true' and dbID != None and resume_duration < 300:
                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(dbID)+', "resume": {"position":'+str(0)+',"total":'+str(resume_duration)+'}},"id":"1"}')
                json_object  = json.loads(json_result)
                xbmc.log(str(json_object)+'=movie resume set, '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
            if global_movie_flag == 'false' and dbID != None and resume_duration < 300 and resume_duration != 60:
                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+', "resume": {"position":'+str(0)+',"total":'+str(resume_duration)+'}},"id":"1"}')
                json_object  = json.loads(json_result)
                xbmc.log(str(json_object)+'=episode resume set, '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
        except:
            xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
            self.reopen_window()
            """
            if reopen_window_bool == 'true' and xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True' and not xbmc.getCondVisibility('Window.IsActive(10138)'):
                #from resources.lib.process import reopen_window
                #reopen_window()
                #from resources.lib.WindowManager import wm
                xbmc.sleep(100)
                if not xbmc.getCondVisibility('Window.IsActive(10138)') and xbmc.Player().isPlaying()==0:
                    if xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True':
                        diamond_info_started = False
                        xbmcgui.Window(10000).setProperty('diamond_info_started',str(diamond_info_started))
                        xbmc.executebuiltin('RunScript(%s,info=reopen_window)' % (addon_ID()))
                        #return wm.open_video_list(search_str='', mode='reopen_window')
                    else:
                        return
            """
            return

        xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
        self.reopen_window()
        return
        """
        window_open = xbmcgui.Window(10000).getProperty(str(addon_ID_short())+'_running')
        if reopen_window_bool == 'true' and xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True' and not xbmc.getCondVisibility('Window.IsActive(10138)'):
            #from resources.lib.process import reopen_window
            #reopen_window()
            #from resources.lib.WindowManager import wm
            xbmc.sleep(100)
            if not xbmc.getCondVisibility('Window.IsActive(10138)') and xbmc.Player().isPlaying()==0:
                if xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True':
                    diamond_info_started = False
                    xbmcgui.Window(10000).setProperty('diamond_info_started',str(diamond_info_started))
                    xbmc.executebuiltin('RunScript(%s,info=reopen_window)' % (addon_ID()))
                    #return wm.open_video_list(search_str='', mode='reopen_window')
                else:
                    return
        if window_stack_enable == 'true' and window_open == 'False':
            xbmc.sleep(100)
            if xbmc.Player().isPlaying()==0:
                if xbmcgui.Window(10000).getProperty('diamond_info_started') == 'True':
                    diamond_info_started = False
                    xbmcgui.Window(10000).setProperty('diamond_info_started',str(diamond_info_started))
                    return wm.open_video_list(search_str='', mode='reopen_window')
                else:
                    return
        """

    def onPlayBackStarted(self):
        Utils.hide_busy()
        xbmc.log(str('onPlayBackStarted1')+'===>___OPEN_INFO', level=xbmc.LOGINFO)

        global diamond_info_started
        #playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        #playlist_size = playlist.size()
        diamond_info_time = xbmcgui.Window(10000).getProperty('diamond_info_time')
        diamond_player_time = xbmcgui.Window(10000).getProperty('diamond_player_time')
        if diamond_player_time == '':
            diamond_player_time = 0
        else:
            diamond_player_time = int(diamond_player_time)

        json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0","id": "1","method": "Player.GetProperties","params": {"playerid": 1,"properties": ["position","playlistid"]}}')
        json_object  = json.loads(json_result)
        try: playlist_position = int(json_object['result']['position'])
        except: playlist_position = 0

        Next_EP_ResolvedUrl = xbmcgui.Window(10000).getProperty('Next_EP.ResolvedUrl')
        xbmcgui.Window(10000).clearProperty('Next_EP.ResolvedUrl_playlist')
        xbmcgui.Window(10000).clearProperty('trakt_scrobble_details')
        if int(time.time()) < diamond_player_time or Next_EP_ResolvedUrl == 'true':
            diamond_player = True
            xbmcgui.Window(10000).clearProperty('Next_EP.ResolvedUrl')
        else:
            diamond_player = False

        if diamond_info_time == '':
            diamond_info_time = 0
        else:
            diamond_info_time = int(diamond_info_time)
        if diamond_info_time + 120 > int(time.time()):
            diamond_info_started = True
        elif diamond_info_time == 0:
            diamond_info_started = False
        elif diamond_info_time + 120 < int(time.time()):
            if playlist_position >= 1:
                diamond_info_started = True
            else:
                diamond_info_started = False
                xbmcgui.Window(10000).clearProperty('diamond_info_time')
            #diamond_info_started = True
        elif playlist_position == 0:
            diamond_info_started = False
            xbmcgui.Window(10000).clearProperty('diamond_info_time')

        xbmcgui.Window(10000).setProperty('diamond_info_started',str(diamond_info_started))
        xbmc.log(str(diamond_info_started)+'diamond_info_started===>diamond_info_started', level=xbmc.LOGINFO)
        xbmc.log(str('onPlayBackStarted')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        trakt_scrobble = str(xbmcaddon.Addon(library.addon_ID()).getSetting('trakt_scrobble'))

        var_test = addon_ID_short()+'_running'
        if diamond_info_started == True:
            xbmcgui.Window(10000).setProperty(var_test, 'True')
            #xbmc.executebuiltin('Dialog.Close(all,true)')
        else:
            xbmcgui.Window(10000).clearProperty(var_test)

        if trakt_scrobble == 'false':
            return
        global headers
        headers = library.trak_auth()

        player = self.player
        #global resume_position
        resume_position = None
        #global resume_duration
        resume_duration = None
        global dbID
        dbID = None
        global db_path
        db_path = library.db_path()
        global global_movie_flag
        global_movie_flag = 'false'

        count = 0
        while player.isPlaying()==1 and count < 7501:
            try:
                resume_position = player.getTime()
            except:
                resume_position = ''
            if resume_position != '':
                if resume_position > 0:
                    break
            else:
                xbmc.sleep(100)
                count = count + 100

        xbmcgui.Window(10000).setProperty('plugin.video.seren.runtime.tempSilent', 'False')
        try: seren_version = xbmcaddon.Addon('plugin.video.seren').getAddonInfo("version")
        except: seren_version = ''
        xbmcgui.Window(10000).setProperty('plugin.video.seren.%s.runtime.tempSilent' % (str(seren_version)), 'False')
        gc.collect()
        if player.isPlaying()==0:
            return
        json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Title", "Player.Filename","Player.Filenameandpath", "VideoPlayer.MovieTitle", "VideoPlayer.TVShowTitle", "VideoPlayer.DBID", "VideoPlayer.DBTYPE", "VideoPlayer.Duration", "VideoPlayer.Season", "VideoPlayer.Episode", "VideoPlayer.DBID", "VideoPlayer.Year", "VideoPlayer.Rating", "VideoPlayer.mpaa", "VideoPlayer.Studio", "VideoPlayer.VideoAspect", "VideoPlayer.Plot", "VideoPlayer.RatingAndVotes", "VideoPlayer.Genre", "VideoPlayer.LastPlayed", "VideoPlayer.IMDBNumber", "ListItem.DBID", "Container.FolderPath", "Container.FolderName", "Container.PluginName", "ListItem.TVShowTitle", "ListItem.FileNameAndPath"]}, "id":1}')
        json_object  = json.loads(json_result)
        timestamp = json_object['result']['VideoPlayer.Duration']
        try: duration = functools.reduce(lambda x, y: x*60+y, [int(i) for i in (timestamp.replace(':',',')).split(',')])
        except: duration = 60

        if ('trailer' in str(json_result).lower() and duration < 300) or 'plugin.video.youtube' in str(json_result).lower():
            return

        #PTN_info = PTN.parse(json_object['result']['Player.Filename'])
        PTN_info = get_guess(json_object['result']['Player.Filename'])
        try: PTN_season = PTN_info['season']
        except: PTN_season = ''
        try: PTN_episode = PTN_info['episode']
        except: PTN_episode = ''
        PTN_movie = ''
        PTN_show = ''
        PTN_year = ''
        try: VideoPlayer_Season = int(json_object['result']['VideoPlayer.Season'])
        except: VideoPlayer_Season = 0
        try: VideoPlayer_Episode = int(json_object['result']['VideoPlayer.Episode'])
        except: VideoPlayer_Episode = 0
        if PTN_season != '' and PTN_episode != '':
            PTN_show = PTN_info['title']
        elif VideoPlayer_Season > 0 and VideoPlayer_Episode > 0:
            PTN_show = json_object['result']['VideoPlayer.TVShowTitle']
            PTN_episode = VideoPlayer_Episode
            PTN_season = VideoPlayer_Season
            tv_title = PTN_show
            tv_season = PTN_season
            tv_episode = PTN_episode
            type = 'episode'
        elif json_object['result']['VideoPlayer.TVShowTitle'] != '' or json_object['result']['VideoPlayer.TVShowTitle'] != None:
            PTN_show = json_object['result']['VideoPlayer.TVShowTitle']
            type = 'episode'
        else:
            PTN_movie = PTN_info['title']
            try: PTN_year = PTN_info['year']
            except: PTN_year = ''
        type = ''
        if json_object['result']['VideoPlayer.TVShowTitle'] == '' and PTN_show != '':
            json_object['result']['VideoPlayer.TVShowTitle'] = PTN_show
            tv_title = PTN_show
            json_object['result']['VideoPlayer.Season'] = PTN_season
            tv_season = PTN_season
            json_object['result']['VideoPlayer.Episode'] = PTN_info['episode']
            tv_episode = PTN_info['episode']
            type = 'episode'
        if json_object['result']['VideoPlayer.MovieTitle'] == '' and PTN_movie != '':
            json_object['result']['VideoPlayer.MovieTitle'] = PTN_movie
            json_object['result']['VideoPlayer.Year'] = PTN_year
            year = PTN_year
            json_object['result']['VideoPlayer.Title'] = PTN_movie
            movie_title = PTN_movie
            type = 'movie'

        year = ''
        tmdb_id = ''
        tvdb_id = ''
        imdb_id = ''
        title = ''
        if type == '':
            type = 'movie'
        if json_object['result']['VideoPlayer.TVShowTitle'] != '':
            tv_title = json_object['result']['VideoPlayer.TVShowTitle']
            tv_season = json_object['result']['VideoPlayer.Season']
            tv_episode = json_object['result']['VideoPlayer.Episode']
            year = str(json_object['result']['VideoPlayer.Year'])
            query=json_object['result']['VideoPlayer.TVShowTitle']
            type = 'episode'
        imdb_id = json_object['result']['VideoPlayer.IMDBNumber']

        if json_object['result']['VideoPlayer.MovieTitle'] != '':
            title = json_object['result']['VideoPlayer.MovieTitle']
            movie_title = title
            year = json_object['result']['VideoPlayer.Year'] 
            type = 'movie'
        elif json_object['result']['VideoPlayer.Title'] != '' and title == '':
            original_title = json_object['result']['VideoPlayer.Title']
            movie_title = json_object['result']['VideoPlayer.Title']
            json_object['result']['VideoPlayer.MovieTitle'] = movie_title
            year = json_object['result']['VideoPlayer.Year']

        if 'tt' in str(imdb_id) and type == 'movie':
            tmdb_id = TheMovieDB.get_movie_tmdb_id(imdb_id=imdb_id)
        elif type == 'episode':
            regex2 = re.compile('(19|20)[0-9][0-9]')
            clean_tv_title2 = regex2.sub(' ', tv_title.replace('\'','').replace('&',' ')).replace('  ',' ')
            #tmdb_id = TheMovieDB.search_media(media_name=clean_tv_title2, media_type='tv')
            response = TheMovieDB.get_tmdb_data('search/tv?query=%s&language=en-US&include_adult=%s&' % (clean_tv_title2, xbmcaddon.Addon().getSetting('include_adults')), 30)
            tmdb_id = response['results'][0]['id']
            #if str(tmdb_id) == '' or str(tmdb_id) == None or tmdb_id == None:
            #    tmdb_api = library.tmdb_api_key()
            #    url = 'https://api.themoviedb.org/3/search/tv?api_key='+str(tmdb_api)+'&language=en-US&page=1&query='+str(clean_tv_title2)+'&include_adult=false'
            #    response = requests.get(url).json()
            #    tmdb_id = response['results'][0]['id']
        else:
            response = TheMovieDB.get_tmdb_data('search/movie?query=%s&language=en-US&year=%s&include_adult=%s&' % (movie_title, str(year), xbmcaddon.Addon().getSetting('include_adults')), 30)
            tmdb_id = response['results'][0]['id']
            #tmdb_id = TheMovieDB.search_media(media_name=movie_title, year=year, media_type='movie')
            #if str(tmdb_id) == '' or str(tmdb_id) == None or tmdb_id == None:
            #    tmdb_api = library.tmdb_api_key()
            #    url = 'https://api.themoviedb.org/3/search/movie?api_key='+str(tmdb_api)+'&query=' +str(movie_title) + '&language=en-US&include_image_language=en,null&year=' +str(year)
            #    response = requests.get(url).json()
            #    tmdb_id = response['results'][0]['id']
        if not (str(tmdb_id) == '' or str(tmdb_id) == None or tmdb_id == None) and type == 'movie':
            imdb_id = TheMovieDB.get_imdb_id_from_movie_id(tmdb_id)
            if not 'tt' in str(json_object['result']['VideoPlayer.IMDBNumber']):
                json_object['result']['VideoPlayer.IMDBNumber'] = imdb_id
        if not (str(tmdb_id) == '' or str(tmdb_id) == None or tmdb_id == None) and type != 'movie':
            response = TheMovieDB.get_tvshow_ids(tmdb_id)
            imdb_id = response['imdb_id']
            json_object['result']['VideoPlayer.IMDBNumber'] = imdb_id

        #TheMovieDB.get_show_tmdb_id(tvdb_id=None, db=None, imdb_id=None)
        dbID = json_object['result']['VideoPlayer.DBID']
        regex = re.compile('[^0-9a-zA-Z]')

        if dbID == '' and type != 'episode':
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            sql_result = cur.execute("SELECT idmovie from movie,uniqueid where uniqueid_id = movie.c09 and uniqueid.value= '"+str(imdb_id)+"'").fetchall()
            try:
                dbID = int(sql_result[0][0])
                json_object['result']['ListItem.DBID'] = dbID
            except:
                dbID = ''
            cur.close()
            if dbID == '':
                movie_id = self.movietitle_to_id(movie_title)
            if movie_id != -1:
                dbID = movie_id
            if int(dbID) > -1:
                json_object['result']['VideoPlayer.DBTYPE'] = 'movie'
                json_object['result']['VideoPlayer.DBID'] = dbID
            #if imdb_id != '' and type != 'episode':
            #    response = trakt_movie_imdb(imdb_id)
            #    #xbmc.log(str(response)+'Rresponse===>___OPEN_INFO', level=xbmc.LOGFATAL)
            #    tmdb_id = str(response[0]['movie']['ids']['tmdb'])
            #    try: self.trakt_scrobble_tmdb(tmdb_id, 1)
            #    except: pass
        if dbID == '' and type == 'episode':
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            clean_tv_title = regex.sub(' ', tv_title.replace('\'','').replace('&',' ')).replace('  ',' ')
            clean_tv_title = clean_tv_title.replace('  ','%').replace(' ','%')
            #sql_result = cur.execute("""
            #select idEpisode,strTitle,* from episode_view where strTitle like
            #'{clean_tv_title}' or strTitle = '{tv_title}' and c12 = {tv_season} and c13 = {tv_episode}
            #""".format(clean_tv_title=clean_tv_title,tv_title=tv_title,tv_season=tv_season,tv_episode=tv_episode)
            #).fetchall()
            sql_result = cur.execute("""
            select idEpisode,strTitle,* from episode_view where (strTitle like
            '{clean_tv_title}' or strTitle = '{tv_title}') and c12 = {tv_season} and c13 = {tv_episode}
            """.format(clean_tv_title=clean_tv_title,tv_title=tv_title.replace('\'','\'\''),tv_season=tv_season,tv_episode=tv_episode)
            ).fetchall()
            cur.close()
            try: sql_year = int(json_object['result']['VideoPlayer.Year'])
            except: sql_year = None
            for i in sql_result:
                if not sql_year or str(sql_year) in str((i[9])):
                    try:
                        dbID = int(i[0])
                        json_object['result']['ListItem.DBID'] = dbID
                        json_object['result']['VideoPlayer.DBTYPE'] = 'episode'
                        json_object['result']['VideoPlayer.DBID'] = dbID
                        json_object['result']['ListItem.TVShowTitle'] = str(i[1])
                    except:
                        dbID = ''
                    break
        #xbmc.log(str(duration)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(tmdb_id)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(imdb_id)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(PTN_season)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(PTN_episode)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(PTN_movie)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(PTN_show)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(PTN_year)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(dbID)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        xbmc.log(str(json_object)+'json_object===>___OPEN_INFO', level=xbmc.LOGINFO)

        playing_file = player.getPlayingFile()
        if type != 'episode':
            movie_id = dbID
            global_movie_flag = 'true'

            if tmdb_id != '':
                try: response = self.trakt_scrobble_tmdb(tmdb_id, 1)
                except: pass
            elif year != '' and movie_title != '':
                try: 
                    response = self.trakt_scrobble_title(movie_title, year, 1)
                except: 
                    pass
            try: trakt_watched = self.trakt_scrobble_details(trakt_watched='false', movie_title=None, movie_year=None, resume_position=resume_position, resume_duration=duration, tmdb_id=tmdb_id, tv_title=None, season=None, episode=None)
            except: trakt_watched = self.trakt_scrobble_details(trakt_watched='false', movie_title=movie_title, movie_year=year, resume_position=resume_position, resume_duration=duration, tmdb_id=None, tv_title=None, season=None, episode=None)
            try: 
                movie_title = response['movie']['title']
                year = response['movie']['year']
            except: 
                movie_title = movie_title
                year = year
            xbmc.log('PLAYBACK STARTED_tvdb='+str(imdb_id)+ '  ,'+str(dbID)+'=dbID, '+str(duration)+'=duration, '+str(movie_title)+'=movie_title, '+str(title)+'___OPEN_INFO', level=xbmc.LOGFATAL)
            url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=movie&amp;tmdb_id=%s' % (str(tmdb_id))
            xbmc.log(url, level=xbmc.LOGFATAL)
            #kodi_send_command = 'kodi-send --action="RunScript(%s,info=diamond_rd_player,type=movie,movie_year=%s,movie_title=%s,tmdb=%s,test=True)"' % (addon_ID(), year, movie_title, tmdb_id)
            kodi_send_command = 'kodi-send --action="RunScript(%s,info=a4kwrapper_player,type=movie,movie_year=%s,movie_title=%s,tmdb=%s,test=True)"' % (addon_ID(), year, movie_title, tmdb_id)
            xbmc.log(kodi_send_command, level=xbmc.LOGFATAL)
            xbmcgui.Window(10000).setProperty('last_played_tmdb_helper', url)
            xbmcaddon.Addon(addon_ID()).setSetting('last_played_tmdb_helper', url)

        if type == 'episode':
            global_movie_flag = 'false'
            xbmc.log('PLAYBACK STARTED_tvdb='+str(tmdb_id)+ '  ,'+str(dbID)+'=dbID, '+str(duration)+'=duration, '+str(tv_title)+'=tv_show_name, '+str(tv_season)+'=season_num, '+str(tv_episode)+'=ep_num, '+str(title)+'___OPEN_INFO', level=xbmc.LOGFATAL)
            url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=%s&amp;episode=%s' % (str(tmdb_id), str(tv_season), str(tv_episode))
            xbmc.log(url, level=xbmc.LOGFATAL)
            kodi_send_command = 'kodi-send --action="RunScript(%s,info=a4kwrapper_player,type=tv,show_title=%s,show_season=%s,show_episode=%s,tmdb=%s,test=True)"' % (addon_ID(), tv_title, tv_season, tv_episode, tmdb_id)
            xbmc.log(kodi_send_command, level=xbmc.LOGFATAL)
            xbmcgui.Window(10000).setProperty('last_played_tmdb_helper', url)
            xbmcaddon.Addon(addon_ID()).setSetting('last_played_tmdb_helper', url)
            try:
                response = self.trakt_scrobble_tv('tmdb_id='+str(tmdb_id), tv_season, tv_episode, 1)
            except: 
                try:
                    response = self.trakt_scrobble_tv(tv_title, tv_season, tv_episode, 1)
                except:
                    pass
            try: trakt_watched = self.trakt_scrobble_details(trakt_watched='false', movie_title=None, movie_year=None, resume_position=resume_position, resume_duration=duration, tmdb_id=tmdb_id, tv_title=None, season=tv_season, episode=tv_episode)
            except: trakt_watched = self.trakt_scrobble_details(trakt_watched='false', movie_title=None, movie_year=None, resume_position=resume_position, resume_duration=duration, tmdb_id=None, tv_title=tv_title, season=tv_season, episode=tv_episode)
            try: tmdb_id = response['show']['ids']['tmdb']
            except: pass
            try: tvdb_id = response['show']['ids']['tvdb']
            except: pass
            try: imdb_id = response['show']['ids']['imdb']
            except: pass

        xbmc.log(str(diamond_info_started)+'diamond_info_started===>diamond_info_started', level=xbmc.LOGINFO)
        count = 0

        if type != 'episode':
            trakt_watched = 'false'
            percentage = 0
            library_refresh = False
            try: movie_id = int(movie_id)
            except: movie_id = 0

            try:
                json_object = {}
                json_object['result'] = []
                jx = 0
                while json_object['result'] == [] and jx < 10:
                    json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":%s,"method":"Player.GetActivePlayers","params":{}}' % (jx))
                    json_object  = json.loads(json_result)
                    jx = jx + 1
                playerid = json_object['result']['playerid']
            except:
                playerid = 1

            #json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"Player.GetActivePlayers","params":{}}')
            #try:
            #    json_object  = json.loads(json_result)
            #    playerid = json_object['result']['playerid']
            #except:
            #    playerid = 0

            try: resume_position = player.getTime()
            except: return
            if resume_position > duration:
                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Duration"]}, "id":1}')
                json_object  = json.loads(json_result)
                timestamp = json_object['result']['VideoPlayer.Duration']
                try: duration = functools.reduce(lambda x, y: x*60+y, [int(i) for i in (timestamp.replace(':',',')).split(',')])
                except: duration = 60
            resume_duration = duration

            speed = 1
            speed_time = int(time.time()) + 5
            scrobble_time = int(time.time()) + 10 * 60
            try: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=None, movie_year=None, resume_position=resume_position, resume_duration=resume_duration, tmdb_id=tmdb_id, tv_title=None, season=None, episode=None)
            except: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=movie_title, movie_year=year, resume_position=resume_position, resume_duration=resume_duration, tmdb_id=None, tv_title=None, season=None, episode=None)

        try: play_test = player.isPlaying()==1 and type != 'episode' and playing_file == player.getPlayingFile()
        except: return

        while play_test:
            try: 
                play_test = player.isPlaying()==1 and type != 'episode' and playing_file == player.getPlayingFile()
                old_resume_position = resume_position
                xbmc.sleep(250)
                resume_position = player.getTime()
            except: 
                return
            if int(time.time()) >= int(speed_time):
                json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0","id": "1","method": "Player.GetProperties","params": {"playerid": %s,"properties": ["position","playlistid","speed"]}}' % (playerid))
                json_object  = json.loads(json_result)

                try: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=None, movie_year=None, resume_position=resume_position, resume_duration=resume_duration, tmdb_id=tmdb_id, tv_title=None, season=None, episode=None)
                except: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=movie_title, movie_year=year, resume_position=resume_position, resume_duration=resume_duration, tmdb_id=None, tv_title=None, season=None, episode=None)

                try: playlist_position2 = int(json_object['result']['position'])
                except: playlist_position2 = 0
                if int(playlist_position2) > int(playlist_position):
                    return

                try: 
                    json_speed = json_object['result']['speed']
                except: 
                    if abs(float(old_resume_position - resume_position)) < 0.05:
                        json_speed = 0
                    else:
                        json_speed = 1

                if json_speed == 1 and speed == 0 and trakt_watched != 'true':
                    trakt_watched = self.trakt_meta_scrobble(action='start')
                if int(speed) == 1 and json_speed == 0 and trakt_watched != 'true':
                    trakt_watched = self.trakt_meta_scrobble(action='pause')
                speed = json_speed
                speed_time = int(time.time()) + 5

            if abs( float((resume_position / duration) * 100) - float(percentage) ) > 0.2 and trakt_watched != 'true':
                try: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=None, movie_year=None, resume_position=resume_position, resume_duration=resume_duration, tmdb_id=tmdb_id, tv_title=None, season=None, episode=None)
                except: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=movie_title, movie_year=year, resume_position=resume_position, resume_duration=resume_duration, tmdb_id=None, tv_title=None, season=None, episode=None)
                trakt_watched = self.trakt_meta_scrobble(action='pause')
                if trakt_watched != 'true':
                    trakt_watched = self.trakt_meta_scrobble(action='start')
                speed_time = time.time()
            if int(time.time()) >  int(scrobble_time) and percentage < 80 and trakt_watched != 'true':
                trakt_watched = self.trakt_meta_scrobble(action='pause')
                if trakt_watched != 'true':
                    trakt_watched = self.trakt_meta_scrobble(action='start')
                scrobble_time = int(time.time()) + 10 * 60
            percentage = (resume_position / duration) * 100

            if (percentage > 85) and player.isPlayingVideo()==1 and duration > 300 and trakt_watched != 'true':
                trakt_watched = self.trakt_meta_scrobble(action='stop')
                try: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=None, movie_year=None, resume_position=0, resume_duration=0, tmdb_id=tmdb_id, tv_title=None, season=None, episode=None)
                except: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=movie_title, movie_year=year, resume_position=0, resume_duration=0, tmdb_id=None, tv_title=None, season=None, episode=None)

            if (percentage > 85) and library_refresh == False and player.isPlayingVideo()==1:
                if int(movie_id) > 0:
                    json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.GetMovieDetails","params":{"movieid":'+str(movie_id)+', "properties": ["playcount"]}}')
                    json_object  = json.loads(json_result)
                    play_count = int(json_object['result']['moviedetails']['playcount'])+1
                    json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(movie_id)+',"playcount": '+str(play_count)+'},"id":"1"}')
                    json_object  = json.loads(json_result)
                    xbmc.log(str(json_object)+'=movie marked watched, '+str(play_count)+', '+str(movie_id)+'=dbID', level=xbmc.LOGFATAL)
                    json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(movie_id)+', "resume": {"position":0,"total":'+str(duration)+'}},"id":"1"}')
                    json_object  = json.loads(json_result)
                    xbmc.log(str(json_object)+'=movie marked 0 resume, '+str(movie_id)+'=dbID', level=xbmc.LOGFATAL)
                    dt_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(movie_id)+',"lastplayed": "'+str(dt_string)+'"},"id":"1"}')
                    json_object  = json.loads(json_result)
                    xbmc.log(str(json_object)+'_LASTPLAYED='+str(dt_string)+'=movie marked watched, '+str(movie_id)+'=dbID', level=xbmc.LOGFATAL)
                xbmc.log(str('STARTING...library.trakt_watched_movies_full')+'===>OPEN_INFO', level=xbmc.LOGINFO)
                library.trakt_refresh_all()
                library_refresh = True
                xbmc.log(str('FINISHED...library.trakt_watched_movies_full')+'===>OPEN_INFO', level=xbmc.LOGINFO)
                playing_file = None
                return

        if type == 'episode':
            trakt_watched = 'false'
            percentage = 0
            library_refresh = False
            try: movie_id = int(movie_id)
            except: movie_id = 0


            try:
                json_object = {}
                json_object['result'] = []
                jx = 0
                while json_object['result'] == [] and jx < 10:
                    json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":%s,"method":"Player.GetActivePlayers","params":{}}' % (jx))
                    json_object  = json.loads(json_result)
                    jx = jx + 1
                playerid = json_object['result']['playerid']
            except:
                playerid = 1

            #json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"Player.GetActivePlayers","params":{}}')
            #try:
            #    json_object  = json.loads(json_result)
            #    playerid = json_object['result']['playerid']
            #except:
            #    playerid = 1

            if diamond_player == True:
                #next_ep_details = get_next_ep_details(show_title=tv_title, show_curr_season=tv_season, show_curr_episode=tv_episode, tmdb=tmdb_id)
                next_ep_details = get_next_ep_details(show_title=tv_title, season_num=tv_season, ep_num=tv_episode, tmdb=tmdb_id)
            else:
                next_ep_details = None
            xbmc.log(str(diamond_player)+'diamond_player===>OPENINFO', level=xbmc.LOGINFO)
            prescrape = False
            if next_ep_details ==None:
                prescrape = True

            try: resume_position = player.getTime()
            except: return
            if resume_position > duration:
                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Duration"]}, "id":1}')
                json_object  = json.loads(json_result)
                timestamp = json_object['result']['VideoPlayer.Duration']
                try: duration = functools.reduce(lambda x, y: x*60+y, [int(i) for i in (timestamp.replace(':',',')).split(',')])
                except: duration = 60
            resume_duration = duration

            speed = 1
            speed_time = int(time.time()) + 5
            scrobble_time = int(time.time()) + 10 * 60
            try: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=None, movie_year=None, resume_position=resume_position, resume_duration=resume_duration, tmdb_id=tmdb_id, tv_title=None, season=tv_season, episode=tv_episode)
            except: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=None, movie_year=None, resume_position=resume_position, resume_duration=resume_duration, tmdb_id=None, tv_title=tv_title, season=tv_season, episode=tv_episode)

        try: play_test = player.isPlaying()==1 and type == 'episode' and playing_file == player.getPlayingFile()
        except: return

        prescrape_time = 0
        while play_test:
            try: 
                play_test = player.isPlaying()==1 and type == 'episode' and playing_file == player.getPlayingFile()
                old_resume_position = resume_position
                xbmc.sleep(250)
                resume_position = player.getTime()
            except: 
                return
            if int(time.time()) >= int(speed_time):
                json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0","id": "1","method": "Player.GetProperties","params": {"playerid": %s,"properties": ["position","playlistid","speed"]}}' % (playerid))
                json_object  = json.loads(json_result)

                try: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=None, movie_year=None, resume_position=resume_position, resume_duration=resume_duration, tmdb_id=tmdb_id, tv_title=None, season=tv_season, episode=tv_episode)
                except: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=None, movie_year=None, resume_position=resume_position, resume_duration=resume_duration, tmdb_id=None, tv_title=tv_title, season=tv_season, episode=tv_episode)

                try: playlist_position2 = int(json_object['result']['position'])
                except: playlist_position2 = 0
                if int(playlist_position2) > int(playlist_position):
                    return

                json_result_test = xbmc.executeJSONRPC('{"jsonrpc": "2.0","method": "Playlist.GetItems","params": {"properties": ["title", "file"],"playlistid": 1},"id": "1"}')
                json_object_test  = json.loads(json_result_test)
                try: playlist_total = int(json_object_test['result']['limits']['total'])
                except: playlist_total = 0
                if int(playlist_total) > 1 and int(playlist_position2)+1 != int(playlist_total):
                    xbmcgui.Window(10000).setProperty('Next_EP.ResolvedUrl_playlist','true')

                #if json_object['result']['speed'] == 1 and speed == 0 and trakt_watched != 'true':
                #    trakt_watched = self.trakt_meta_scrobble(action='start')
                #if int(speed) == 1 and json_object['result']['speed'] == 0 and trakt_watched != 'true':
                #    trakt_watched = self.trakt_meta_scrobble(action='pause')
                #speed = json_object['result']['speed']
                #speed_time = int(time.time()) + 5

                try: 
                    json_speed = json_object['result']['speed']
                except: 
                    if abs(float(old_resume_position - resume_position)) < 0.05:
                        json_speed = 0
                    else:
                        json_speed = 1

                if json_speed == 1 and speed == 0 and trakt_watched != 'true':
                    trakt_watched = self.trakt_meta_scrobble(action='start')
                if int(speed) == 1 and json_speed == 0 and trakt_watched != 'true':
                    trakt_watched = self.trakt_meta_scrobble(action='pause')
                speed = json_speed
                speed_time = int(time.time()) + 5


            if abs( float((resume_position / duration) * 100) - float(percentage) ) > 0.3 and trakt_watched != 'true':
                xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
                try: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=None, movie_year=None, resume_position=resume_position, resume_duration=resume_duration, tmdb_id=tmdb_id, tv_title=None, season=tv_season, episode=tv_episode)
                except: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=None, movie_year=None, resume_position=resume_position, resume_duration=resume_duration, tmdb_id=None, tv_title=tv_title, season=tv_season, episode=tv_episode)
                trakt_watched = self.trakt_meta_scrobble(action='pause')
                if trakt_watched != 'true':
                    xbmc.sleep(250)
                    trakt_watched = self.trakt_meta_scrobble(action='start')
                speed_time = time.time()
            if int(time.time()) >  int(scrobble_time) and percentage < 80 and trakt_watched != 'true':
                xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
                trakt_watched = self.trakt_meta_scrobble(action='pause')
                if trakt_watched != 'true':
                    xbmc.sleep(250)
                    trakt_watched = self.trakt_meta_scrobble(action='start')
                scrobble_time = int(time.time()) + 10 * 60
            percentage = (resume_position / duration) * 100

            if percentage > 33 and prescrape == False and prescrape_time == 0 and diamond_player == True:
                #kodi-send --action="RunScript(script.extendedinfo,info=diamond_rd_player,type=tv,show_title=Star Trek: Enterprise,show_season=4,show_episode=20,tmdb=314)"
                next_ep_play_details = next_ep_play(show_title=next_ep_details['next_ep_show'], show_season=next_ep_details['next_ep_season'], show_episode=next_ep_details['next_ep_episode'], tmdb=next_ep_details['tmdb_id'])
                #xbmc.log(str(next_ep_play_details)+'next_ep_play_details===>OPENINFO', level=xbmc.LOGINFO)
                try: 
                    prescrape = True
                    if next_ep_play_details.get('ResolvedUrl') == True:
                        xbmc.log(str(next_ep_play_details.get('ResolvedUrl'))+'ResolvedUrl_next_ep_play_details===>OPENINFO', level=xbmc.LOGINFO)
                except:
                    xbmc.log('NOT_FOUND_PRESCRAPE1===>OPENINFO', level=xbmc.LOGINFO)
                    prescrape = False
                    prescrape_time = time.time() + 120

            if percentage > 66 and prescrape_time > 0 and time.time() > prescrape_time and prescrape == False and diamond_player == True:
                rd_seren_prescrape = xbmcaddon.Addon(addon_ID()).getSetting('rd_seren_prescrape')
                xbmc.log(str(prescrape_time)+'===>prescrape_time', level=xbmc.LOGINFO)
                #xbmcgui.Window(10000).setProperty('plugin.video.seren.runtime.tempSilent', 'False')
                try: seren_version = xbmcaddon.Addon('plugin.video.seren').getAddonInfo("version")
                except: seren_version = ''
                if seren_version != '' and rd_seren_prescrape == 'true':
                    if xbmcgui.Window(10000).getProperty('plugin.video.seren.%s.runtime.tempSilent' % (str(seren_version))) == 'True' and xbmcgui.Window(10000).getProperty('plugin.video.seren.runtime.tempSilent')  == 'True':
                        prescrape_time = time.time() + 120
                    else:
                        xbmcgui.Window(10000).setProperty('plugin.video.seren.%s.runtime.tempSilent' % (str(seren_version)), 'False')
                        xbmcgui.Window(10000).setProperty('plugin.video.seren.runtime.tempSilent', 'False')
                        next_ep_play_details = next_ep_play(show_title=next_ep_details['next_ep_show'], show_season=next_ep_details['next_ep_season'], show_episode=next_ep_details['next_ep_episode'], tmdb=next_ep_details['tmdb_id'])
                        try: 
                            prescrape = True
                            if next_ep_play_details.get('ResolvedUrl') == True:
                                xbmc.log(str(next_ep_play_details.get('ResolvedUrl'))+'ResolvedUrl_next_ep_play_details===>OPENINFO', level=xbmc.LOGINFO)
                        except:
                            xbmc.log('NOT_FOUND_PRESCRAPE2===>OPENINFO', level=xbmc.LOGINFO)
                            prescrape = False
                            prescrape_time = -1
                else:
                    xbmcgui.Window(10000).setProperty('plugin.video.seren.%s.runtime.tempSilent' % (str(seren_version)), 'False')
                    xbmcgui.Window(10000).setProperty('plugin.video.seren.runtime.tempSilent', 'False')
                    prescrape_time = -1

            if player.isPlaying()==1 and percentage > 85 and trakt_watched != 'true':
            #if (percentage > 85) and player.isPlayingVideo()==1 and duration > 300 and trakt_watched != 'true':
                xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
                trakt_watched = self.trakt_meta_scrobble(action='stop')
                try: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=None, movie_year=None, resume_position=0, resume_duration=0, tmdb_id=tmdb_id, tv_title=None, season=tv_season, episode=tv_episode)
                except: self.trakt_scrobble_details(trakt_watched=trakt_watched, movie_title=None, movie_year=None, resume_position=0, resume_duration=0, tmdb_id=None, tv_title=tv_title, season=tv_season, episode=tv_episode)

            if player.isPlayingVideo()==1 and percentage > 85 and library_refresh == False:
                try: 
                    dbID = int(dbID)
                    if dbID == 0:
                        dbID = None
                except: 
                    dbID = None
                if dbID != None:
                    json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.GetEpisodeDetails","params":{"episodeid":'+str(dbID)+', "properties": ["playcount"]}}')
                    json_object  = json.loads(json_result)
                    play_count = int(json_object['result']['episodedetails']['playcount'])+1
                    json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+',"playcount": '+str(play_count)+'},"id":"1"}')
                    json_object  = json.loads(json_result)
                    xbmc.log(str(json_object)+'=episode marked watched, playcount = '+str(play_count)+', '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
                    json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+', "resume": {"position":0,"total":'+str(duration)+'}},"id":"1"}')
                    json_object  = json.loads(json_result)
                    xbmc.log(str(json_object)+'=episode marked 0 resume, '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
                    dt_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+',"lastplayed": "'+str(dt_string)+'"},"id":"1"}')
                    json_object  = json.loads(json_result)
                    xbmc.log(str(json_object)+'_LASTPLAYED='+str(dt_string)+'=episode marked watched, '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
                xbmc.log(str('STARTING...library.trakt_watched_tv_shows_full')+'===>OPEN_INFO', level=xbmc.LOGINFO)
                library.trakt_refresh_all()
                library_refresh = True
                xbmc.log(str('FINISHED...library.trakt_watched_tv_shows_full')+'===>OPEN_INFO', level=xbmc.LOGINFO)

            if diamond_player == False and percentage > 85:
                xbmc.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO', level=xbmc.LOGINFO)
                playing_file = None
                if diamond_info_started == True:
                    xbmcgui.Window(10000).setProperty('diamond_info_time', str(int(time.time())+15))
                return

            if player.isPlaying()==1 and percentage > 90 and resume_position > (duration - 35) and resume_position < duration and prescrape == True and diamond_player == True:
                try: 
                    next_ep_url = next_ep_play_details.get('PTN_download')
                except:
                    return
                title = str(next_ep_play_details.get('episode_name'))
                thumb = next_ep_details.get('next_ep_thumb2','')
                if thumb == '':
                    thumb = next_ep_play_details.get('next_ep_thumbnail')
                rating = next_ep_details.get('next_ep_rating')
                if rating == '' or rating == 0:
                    rating = next_ep_play_details.get('rating')
                show = next_ep_play_details.get('show_title')
                season = next_ep_play_details.get('PTN_season')
                episode = next_ep_play_details.get('PTN_episode')
                year = next_ep_play_details.get('year')
                kodi_url = 'RunScript(%s,info=display_dialog,next_ep_url=%s,title=%s,thumb=%s,rating=%s,show=%s,season=%s,episode=%s,year=%s)' % (str(addon_ID()), str(next_ep_url), quote_plus(title), str(thumb), str(rating), str(show), str(season), str(episode), str(year))
                xbmc.log(str(kodi_url)+'kodi_url===>OPENINFO', level=xbmc.LOGINFO)
                xbmc.executebuiltin(kodi_url)
                playing_file = None
                return
 
class CronJobMonitor(Thread):
    def __init__(self, update_hour=0):
        Thread.__init__(self)
        ServiceStarted = 'False'
        ServiceStop = ''
        self.exit = False
        self.poll_time = 1800  # Poll every 30 mins since we don't need to get exact time for update
        self.update_hour = update_hour
        self.xbmc_monitor = xbmc.Monitor()

    def run(self):
        self.next_time = 0
        library_auto_sync = str(xbmcaddon.Addon(library.addon_ID()).getSetting('library_auto_sync'))
        trakt_kodi_mode = str(xbmcaddon.Addon(library.addon_ID()).getSetting('trakt_kodi_mode'))
        trakt_calendar_auto_sync = str(xbmcaddon.Addon(library.addon_ID()).getSetting('trakt_calendar_auto_sync')).lower()
        if library_auto_sync == 'true':
            library_auto_sync = True
        if library_auto_sync == 'false':
            library_auto_sync = False
        Utils.hide_busy()
        library.trakt_refresh_all()
        self.xbmc_monitor.waitForAbort(5)  # Wait 10 minutes before doing updates to give boot time
        if self.xbmc_monitor.abortRequested():
            del self.xbmc_monitor
            return
        while not self.xbmc_monitor.abortRequested() and not self.exit and self.poll_time:
            xbmc.log(str('CronJobMonitor_STARTED_diamond_info_service_started')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
            self.curr_time = datetime.datetime.now().replace(minute=0,second=0, microsecond=0).timestamp()
            if int(time.time()) > self.next_time and library_auto_sync == True:  # Scheduled time has past so lets update
                library_update_period = int(xbmcaddon.Addon(library.addon_ID()).getSetting('library_sync_hours'))
                self.next_time = self.curr_time + library_update_period*60*60

                process.auto_library()
            elif int(time.time()) > self.next_time and trakt_kodi_mode == 'Trakt Only': 
                try: trakt_token = xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('trakt_token')
                except: trakt_token = None
                if trakt_token:
                    if trakt_calendar_auto_sync == 'true' or trakt_calendar_auto_sync == True:
                        trakt_calendar_list()
                library_update_period = int(xbmcaddon.Addon(library.addon_ID()).getSetting('library_sync_hours'))
                self.next_time = self.curr_time + library_update_period*60*60

            self.xbmc_monitor.waitForAbort(self.poll_time)

        del self.xbmc_monitor


class ServiceMonitor(object):
    def __init__(self):
        xbmc.log(str('ServiceMonitor_diamond_info_service_started')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        Utils.hide_busy()
        self.exit = False
        self.cron_job = CronJobMonitor(0)
        self.cron_job.setName('Cron Thread')
        self.player_monitor = None
        self.my_monitor = None
        self.xbmc_monitor = xbmc.Monitor()

    def _on_listitem(self):
        #self.listitem_monitor.get_listitem()
        self.xbmc_monitor.waitForAbort(0.3)

    def _on_scroll(self):
        #self.listitem_monitor.clear_on_scroll()
        self.xbmc_monitor.waitForAbort(1)

    def _on_fullscreen(self):
        #if self.player_monitor.isPlayingVideo():
        #    self.player_monitor.current_time = self.player_monitor.getTime()
        self.xbmc_monitor.waitForAbort(1)

    def _on_idle(self):
        self.xbmc_monitor.waitForAbort(30)

    def _on_modal(self):
        self.xbmc_monitor.waitForAbort(2)

    def _on_clear(self):
        """
        IF we've got properties to clear lets clear them and then jump back in the loop
        Otherwise we should sit for a second so we aren't constantly polling
        """
        #if self.listitem_monitor.properties or self.listitem_monitor.index_properties:
        #    return self.listitem_monitor.clear_properties()
        #self.listitem_monitor.blur_fallback()
        self.xbmc_monitor.waitForAbort(1)

    def _on_exit(self):
        if not self.xbmc_monitor.abortRequested():
            #self.listitem_monitor.clear_properties()
            ServiceStarted = ''
            ServiceStop = '' 
        #del self.player_monitor
        #del self.listitem_monitor
        del self.xbmc_monitor

    def poller(self):
        while not self.xbmc_monitor.abortRequested() and not self.exit:
            if ServiceStop == 'True' :
                self.cron_job.exit = True
                self.exit = True

            # If we're in fullscreen video then we should update the playermonitor time
            elif xbmc.getCondVisibility("Window.IsVisible(fullscreenvideo)"):
                self._on_fullscreen()

            # Sit idle in a holding pattern if the skin doesn't need the service monitor yet
            elif xbmc.getCondVisibility(
                    "System.ScreenSaverActive | "
                    "[!Skin.HasSetting(TMDbHelper.Service) + "
                    "!Skin.HasSetting(TMDbHelper.EnableBlur) + "
                    "!Skin.HasSetting(TMDbHelper.EnableDesaturate) + "
                    "!Skin.HasSetting(TMDbHelper.EnableColors)]"):
                self._on_idle()

            # skip when modal / busy dialogs are opened (e.g. context / select / busy etc.)
            elif xbmc.getCondVisibility(
                    "Window.IsActive(DialogSelect.xml) | "
                    "Window.IsActive(progressdialog) | "
                    "Window.IsActive(contextmenu) | "
                    "Window.IsActive(busydialog) | "
                    "Window.IsActive(shutdownmenu)"):
                self._on_modal()

            # skip when container scrolling
            elif xbmc.getCondVisibility(
                    "Container.OnScrollNext | "
                    "Container.OnScrollPrevious | "
                    "Container.Scrolling"):
                self._on_scroll()

            # media window is opened or widgetcontainer set - start listitem monitoring!
            elif xbmc.getCondVisibility(
                    "Window.IsMedia | "
                    "Window.IsVisible(MyPVRChannels.xml) | "
                    "Window.IsVisible(MyPVRGuide.xml) | "
                    "Window.IsVisible(DialogPVRInfo.xml) | "
                    "Window.IsVisible(movieinformation)"):
                self._on_listitem()

            # Otherwise just sit here and wait
            else:
                self._on_clear()

        # Some clean-up once service exits
        self._on_exit()

    def run(self):
        xbmc.log(str('run_diamond_info_service_started')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        ServiceStarted = 'True'
        window_stack = xbmcvfs.translatePath('special://profile/addon_data/'+addon_ID()+ '/window_stack.db')
        if xbmcvfs.exists(window_stack):
            os.remove(window_stack)

        auto_plugin_route = xbmcaddon.Addon().getSetting('auto_plugin_route')
        auto_plugin_route_enable = xbmcaddon.Addon().getSetting('auto_plugin_route_enable')
        if auto_plugin_route_enable == 'true':
            if auto_plugin_route[0:7] == 'plugin:':
                xbmc.executebuiltin('RunPlugin(%s)' % auto_plugin_route)
            if auto_plugin_route[0:7] == 'script.':
                xbmc.executebuiltin('RunScript(%s)' % auto_plugin_route)
        library.auto_setup_xml_filenames()
        if  xbmcaddon.Addon(addon_ID()).getSetting('auto_clean_cache_bool') == 'true':
            process.auto_clean_cache(days=30)
        self.cron_job.start()
        self.player_monitor = PlayerMonitor()
        self.my_monitor = MyMonitor()
        self.poller()

if __name__ == '__main__':
    ServiceMonitor().run()
