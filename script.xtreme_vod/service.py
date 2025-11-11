import xbmc, xbmcaddon, xbmcgui, xbmcvfs
from threading import Thread
import datetime
import time
import json
import re
import requests
import os
os.environ['first_run'] = str('True')

from resources.lib import library
from resources.lib import Utils
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short
from resources.lib.library import get_trakt_data
from resources.lib.WindowManager import wm
import gc

from pathlib import Path

from resources.lib import TheMovieDB
from urllib.parse import urlencode, quote, quote_plus, unquote, unquote_plus

from resources.lib.Utils import tools_log
from inspect import currentframe, getframeinfo
#tools_log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

import os
import sys
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Subliminal'))

current_directory = str(getframeinfo(currentframe()).filename.replace(os.path.basename(getframeinfo(currentframe()).filename),'').replace('','')[:-1])
#sys.path.append(current_directory)
#sys.path.append(current_directory.replace('a4kscrapers_wrapper',''))

from resources.lib.VideoPlayer import PLAYER
#from a4kscrapers_wrapper import source_tools, babelfish, get_meta

import sys
version_str = sys.version.split()[0]   # '3.9.2'
tools_log(sys.version)
tools_log('PYTHON__VERSION')
version_float = float('.'.join(version_str.split('.')[:2]))
if version_float >= 3.9:
	import importlib_resources_new as importlib_resources
else:
	import importlib_resources_old as importlib_resources
sys.modules["importlib_resources"] = importlib_resources

#import sys
#import glob as real_glob
#
#class GlobWrapper:
#    def __call__(self, *args, **kwargs):
#        return real_glob.glob(*args, **kwargs)  # make glob(...) work
#
#    def __getattr__(self, attr):
#        return getattr(real_glob, attr)  # pass-through attributes

#sys.modules['glob'] = GlobWrapper()
#glob = sys.modules['glob']

import click

import importlib
import guessit
from guessit import api
import functools

import sqlite3

from xtream2m3u_run import generate_m3u
from xtream2m3u_run import generate_xmltv
from xtream2m3u_run import xml_startup_process

def get_guess(release_title, options=None):
	guess = api.guessit(release_title, options)
	return guess

from resources.lib import process

ServiceStop = ''
Utils.hide_busy()


def restart_service_monitor():
	if ServiceStarted == 'True':
		while ServiceStop == '':
			self.xbmc_monitor.waitForAbort(1)
		#wait_for_property('ServiceStop', value='True', set_property=True)  # Stop service
	#wait_for_property('ServiceStop', value=None)  # Wait until Service clears property
	while ServiceStop != '':
		self.xbmc_monitor.waitForAbort(1)
	Thread(target=ServiceMonitor().run).start()

class PlayerMonitor(xbmc.Player):
	
	def __init__(self):
		xbmc.Player.__init__(self)
		self.player = xbmc.Player()
		self.player_meta = {}
		self.trakt_scrobble = xbmcaddon.Addon(library.addon_ID()).getSetting('trakt_scrobble')
		self.trakt_method = {}
		self.reopen_window_bool = xbmcaddon.Addon(library.addon_ID()).getSetting('reopen_window_bool')
		self.window_stack_enable = xbmcaddon.Addon(library.addon_ID()).getSetting('window_stack_enable')
		self.trakt_watched = False
		self.playerid = None
		self.library_refresh = False
		self.play_test = False
		self.playing_file = None
		self.iplayerwww = False
		self.type = None
		self.speed = 1
		self.speed_time = 0
		self.scrobble_time = 0
		self.trakt_error = None

	def getProperty(self, var_name):
		var_value = xbmcgui.Window(10000).getProperty(var_name)
		return str(var_value)

	def clearProperty(self, var_name):
		xbmcgui.Window(10000).clearProperty(var_name)
		return
		
	def SetMovieDetails(self, dbID, resume_position, resume_duration):
		json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(dbID)+', "resume": {"position":'+str(resume_position)+',"total":'+str(resume_duration)+'}},"id":"1"}')
		json_object  = json.loads(json_result)
		#tools_log(str(json_object)+'=movie resume set, '+str(self.player_meta['dbID'])+'=dbID')
		return json_object

	def SetEpisodeDetails(self, dbID, resume_position, resume_duration):
		json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+', "resume": {"position":'+str(resume_position)+',"total":'+str(resume_duration)+'}},"id":"1"}')
		json_object  = json.loads(json_result)
		#tools_log(str(json_object)+'=episode resume set, '+str(dbID)+'=dbID')
		return json_object

	def SetEpisodeDetails2(self, dbID, duration): ##PLAYCOUNT_LASTPLAYED
		json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.GetEpisodeDetails","params":{"episodeid":'+str(dbID)+', "properties": ["playcount"]}}')
		json_object  = json.loads(json_result)
		play_count = int(json_object['result']['episodedetails']['playcount'])+1
		json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+',"playcount": '+str(play_count)+'},"id":"1"}')
		json_object  = json.loads(json_result)
		#tools_log(str(json_object)+'=episode marked watched, playcount = '+str(play_count)+', '+str(self.player_meta['dbID'])+'=dbID')
		json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+', "resume": {"position":0,"total":'+str(duration)+'}},"id":"1"}')
		json_object  = json.loads(json_result)
		#tools_log(str(json_object)+'=episode marked 0 resume, '+str(dbID)+'=dbID')
		dt_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+',"lastplayed": "'+str(dt_string)+'"},"id":"1"}')
		json_object  = json.loads(json_result)
		#tools_log(str(json_object)+'_LASTPLAYED='+str(dt_string)+'=episode marked watched, '+str(dbID)+'=dbID')

	def SetMovieDetails2(self, dbID, duration): ##PLAYCOUNT_LASTPLAYED
		json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.GetMovieDetails","params":{"movieid":'+str(dbID)+', "properties": ["playcount"]}}')
		json_object  = json.loads(json_result)
		play_count = int(json_object['result']['moviedetails']['playcount'])+1
		json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(dbID)+',"playcount": '+str(play_count)+'},"id":"1"}')
		json_object  = json.loads(json_result)
		#tools_log(str(json_object)+'=movie marked watched, '+str(play_count)+', '+str(dbID)+'=dbID')
		json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(dbID)+', "resume": {"position":0,"total":'+str(duration)+'}},"id":"1"}')
		json_object  = json.loads(json_result)
		#tools_log(str(json_object)+'=movie marked 0 resume, '+str(dbID)+'=dbID')
		dt_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(dbID)+',"lastplayed": "'+str(dt_string)+'"},"id":"1"}')
		json_object  = json.loads(json_result)
		#tools_log(str(json_object)+'_LASTPLAYED='+str(dt_string)+'=movie marked watched, '+str(dbID)+'=dbID')

	def setProperty(self, var_name,var_value):
		xbmcgui.Window(10000).setProperty(var_name,str(var_value))
		return

	def update_resume_position_duration(self):
		try: 
			self.player_meta['resume_position'] = self.player.getTime()
			if self.player_meta['resume_position'] > self.player_meta['resume_duration'] or self.player_meta['resume_duration'] == 60:
				json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Duration"]}, "id":1}')
				json_object  = json.loads(json_result)
				timestamp = json_object['result']['VideoPlayer.Duration']
				try: self.player_meta['resume_duration'] = functools.reduce(lambda x, y: x*60+y, [int(i) for i in (timestamp.replace(':',',')).split(',')])
				except: self.player_meta['resume_duration'] = 60
			return True
		except:
			return False

	def update_play_test(self, playing_file):
		self.update_resume_position_duration()
		try: self.play_test = self.player.isPlaying()==1 and playing_file == self.player.getPlayingFile()
		except: self.play_test = False
		return self.play_test


	def get_playerid(self):
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
		return playerid

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

	def movie_populate_dbid(self):
		if self.player_meta['imdb_id'] == None:
			return
		con = sqlite3.connect(self.player_meta['db_path'])
		cur = con.cursor()
		sql_result = cur.execute("SELECT idmovie from movie,uniqueid where uniqueid_id = movie.c09 and uniqueid.value= '"+str(self.player_meta['imdb_id'])+"'").fetchall()

		try:
			self.player_meta['dbID'] = int(sql_result[0][0])
		except:
			self.player_meta['dbID'] = ''

		cur.close()
		if self.player_meta['dbID'] == '':
			self.player_meta['dbID'] = self.movietitle_to_id(self.player_meta['movie_title'])
		return self.player_meta['dbID']

	def episode_populate_dbid(self):
		if self.player_meta['tv_episode'] == None or self.player_meta['tv_season'] == None:
			return
		regex = re.compile('[^0-9a-zA-Z]')
		con = sqlite3.connect(self.player_meta['db_path'])
		cur = con.cursor()
		clean_tv_title = regex.sub(' ', self.player_meta['tv_title'].replace('\'','').replace('&',' ')).replace('  ',' ')
		clean_tv_title = clean_tv_title.replace('  ','%').replace(' ','%')

		#sql_result = cur.execute("""
		#select idEpisode,strTitle,* from episode_view where (strTitle like
		#'{clean_tv_title}' or strTitle = '{tv_title}') and c12 = {self.player_meta['tv_season']} and c13 = {self.player_meta['tv_episode']}
		#""".format(clean_tv_title=clean_tv_title,tv_title=self.player_meta['tv_title'].replace('\'','\'\''),tv_season=self.player_meta['tv_season'],tv_episode=self.player_meta['tv_episode'])
		#).fetchall()
		sql_result = cur.execute("""
		select idEpisode,strTitle,* from episode_view where (strTitle like
		'%s' or strTitle = '%s') and c12 = %s and c13 = %s
		""" % (clean_tv_title,self.player_meta['tv_title'].replace('\'','\'\''),str(self.player_meta['tv_season']),str(self.player_meta['tv_episode']))
		).fetchall()
		cur.close()
		try: sql_year = int(self.player_meta['VideoPlayer.Year'])
		except: sql_year = None
		for i in sql_result:
			if not sql_year or str(sql_year) in str((i[9])):
				try:
					self.player_meta['dbID'] = int(i[0])
				except:
					self.player_meta['dbID'] = None
				break
		return self.player_meta['dbID']

	def trakt_scrobble_details(self):
		trakt_meta = {}
		trakt_meta['trakt_watched']=self.trakt_watched
		trakt_meta['movie_title']=self.player_meta['movie_title']
		trakt_meta['movie_year']=self.player_meta['movie_year']
		trakt_meta['resume_position']=self.player_meta['resume_position']
		trakt_meta['resume_duration']=self.player_meta['resume_duration']
		trakt_meta['tmdb_id']=self.player_meta['tmdb_id']
		trakt_meta['trakt_tmdb_id']=self.player_meta['trakt_tmdb_id']
		trakt_meta['tv_title']=self.player_meta['tv_title']
		trakt_meta['season']=self.player_meta['tv_season']
		trakt_meta['episode']=self.player_meta['tv_episode']
		trakt_meta['user_slug']=self.player_meta['user_slug']
		self.setProperty('trakt_scrobble_details',json.dumps(trakt_meta, sort_keys=True))

	def get_trakt_scrobble_details(self):
		try: trakt_meta = json.loads(self.getProperty('trakt_scrobble_details'))
		except: return {}
		return trakt_meta

	def trakt_scrobble_title(self, movie_title, movie_year, percent, action=None):
		self.trakt_method['function'] = 'trakt_scrobble_title'
		self.trakt_method['movie_title'] = self.player_meta['movie_title']
		self.trakt_method['movie_year'] = self.player_meta['movie_year']
		self.trakt_method['percent'] = None

		response = TheMovieDB.get_tmdb_data('search/movie?query=%s&year=%s&language=en-US&include_adult=%s&' % (self.player_meta['movie_title'],str(self.player_meta['movie_year']), xbmcaddon.Addon().getSetting('include_adults')), 30)
		try: self.player_meta['trakt_tmdb_id'] = response['results'][0]['id']
		except IndexError: return None

		response = get_trakt_data(url='https://api.trakt.tv/search/tmdb/'+str(self.player_meta['trakt_tmdb_id'])+'?type=movie', cache_days=7)
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

		response = None
		count = 0
		while response == None and count < 20:
			count = count + 1
			try:
				response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=self.player_meta['headers'])
				test_var = response.json()
			except: 
				response = None
		#if response.status_code == 429:
		#	tools_log(str(response)+'===>trakt_scrobble_title____OPEN_INFO')
		#	tools_log(str(response.headers)+'===>trakt_scrobble_title____OPEN_INFO')
		x = 0
		try:
			response_status_code = response.status_code
		except:
			return 'ERROR'
		while response.status_code == 429:
			x = x + 1
			if x == 20:
				return 'ERROR'
			try: 
				retry_after = response.headers.json()['Retry-After']
			except: 
				try: retry_after = int(response.headers['Retry-After'])
				except: retry_after = 0
			if retry_after > 0 and retry_after <= 10:
				xbmc.sleep(retry_after * 1000)
				response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=self.player_meta['headers'])
			elif retry_after > 0:
				tools_log(str(response.headers)+'retry_after===>TRAKT_SCROBBLE_TMDB____OPEN_INFO')
		if percent <= 1 or percent >= 84: 
			try: 
				test = response.json()
				if response.status_code <= 299:
					tools_log('TRAKT_SCROBBLE_ACTION_SUCCESS')
				else:
					tools_log(str(response)+'===>TRAKT_SCROBBLE_ACTION_FAIL____OPEN_INFO')
			except: 
				tools_log(str(response)+'===>TRAKT_SCROBBLE_TMDB____OPEN_INFO')
				response = 'ERROR'
			return response

	def trakt_scrobble_tmdb(self, tmdb_id, percent, action=None):
		self.trakt_method['function'] = 'trakt_scrobble_tmdb'
		self.trakt_method['trakt_tmdb_id'] = self.player_meta['trakt_tmdb_id']
		self.trakt_method['percent'] = None

		response = get_trakt_data(url='https://api.trakt.tv/search/tmdb/'+str(self.player_meta['trakt_tmdb_id'])+'?type=movie', cache_days=7)
		trakt = response[0]['movie']['ids']['trakt']
		slug = response[0]['movie']['ids']['slug']
		imdb = response[0]['movie']['ids']['imdb']
		tmdb = response[0]['movie']['ids']['tmdb']
		year = response[0]['movie']['year']
		#try:
		#	title = response[0]['movie']['title']
		#except:
		#	title = str(u''.join(response[0]['movie']['title']).encode('utf-8').strip())


		try: 
			test = str(year)+str(trakt)+'"'+slug+'"'+'"'+imdb+'"'+str(tmdb)+str(percent)
		except:
			response = None
			return response
		
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
		response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=self.player_meta['headers'])
		count = 0
		while response == None and count < 20:
			count = count + 1
			response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=self.player_meta['headers'])
			test_var = response.json()
		#if response.status_code == 429:
		#	tools_log(str(response)+'===>trakt_scrobble_tmdb____OPEN_INFO')
		#	tools_log(str(response.headers)+'===>trakt_scrobble_tmdb____OPEN_INFO')
		x = 0
		try:
			response_status_code = response.status_code
		except:
			return 'ERROR'
		while response.status_code == 429:
			x = x + 1
			if x == 20:
				return 'ERROR'
			try: 
				retry_after = response.headers.json()['Retry-After']
			except: 
				try: retry_after = int(response.headers['Retry-After'])
				except: retry_after = 0
			if retry_after > 0 and retry_after <= 10:
				xbmc.sleep(retry_after * 1000)
				response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=self.player_meta['headers'])
			elif retry_after > 0:
				tools_log(str(response.headers)+'retry_after===>TRAKT_SCROBBLE_TMDB____OPEN_INFO')
		if percent <= 1 or percent >= 84: 
			try: 
				test = response.json()
				if response.status_code <= 299:
					tools_log('TRAKT_SCROBBLE_ACTION_SUCCESS')
				else:
					tools_log(str(response)+'===>TRAKT_SCROBBLE_ACTION_FAIL____OPEN_INFO')
			except: 
				tools_log(str(response)+'===>TRAKT_SCROBBLE_TMDB____OPEN_INFO')
				response = 'ERROR'
		return response

	def trakt_scrobble_tv(self, title, season, episode, percent, action=None):
		self.trakt_method['function'] = 'trakt_scrobble_tv'
		try: 
			self.trakt_method['title'] = self.player_meta['title']
		except:
			tools_log(str('ERROR')+'===>TRAKT_SCROBBLE_TV____OPEN_INFO')
			response = 'ERROR'
			return response
		self.trakt_method['season'] = season
		self.trakt_method['episode'] = episode
		self.trakt_method['percent'] = None

		if 'tmdb_id=' in str(title):
			if self.player_meta['trakt_tmdb_id'] != str(title).replace('tmdb_id=',''):
				self.player_meta['trakt_tmdb_id'] = str(title).replace('tmdb_id=','')
			response = get_trakt_data(url='https://api.trakt.tv/search/tmdb/'+str(self.player_meta['trakt_tmdb_id'])+'?type=show', cache_days=7)
			tvdb = response[0]['show']['ids']['tvdb']
			imdb = response[0]['show']['ids']['imdb']
			trakt = response[0]['show']['ids']['trakt']
			title = response[0]['show']['title']
			year = response[0]['show']['year']
		else:
			response = get_trakt_data(url='https://api.trakt.tv/search/show?query='+str(title), cache_days=7)
			try: 
				trakt = response[0]['show']['ids']['trakt']
			except TypeError: 
				tools_log(str('ERROR')+'===>TRAKT_SCROBBLE_TV____OPEN_INFO')
				response = 'ERROR'
				return response
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
		response = None
		count = 0
		while response == None and count < 20:
			count = count + 1
			response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=self.player_meta['headers'])
		#if response.status_code == 429:
		#	tools_log(str(response)+'===>trakt_scrobble_tv____OPEN_INFO')
		#	tools_log(str(response.headers)+'===>trakt_scrobble_tv____OPEN_INFO')
		x = 0
		try:
			response_status_code = response.status_code
		except:
			return 'ERROR'
		while response.status_code == 429:
			x = x + 1
			if x == 20:
				return 'ERROR'
			try: 
				retry_after = response.headers.json()['Retry-After']
			except: 
				try: retry_after = int(response.headers['Retry-After'])
				except: retry_after = 0
			if retry_after > 0 and retry_after <= 10:
				xbmc.sleep(retry_after * 1000)
				response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=self.player_meta['headers'])
			elif retry_after > 0:
				tools_log(str(response.headers)+'retry_after===>TRAKT_SCROBBLE_TMDB____OPEN_INFO')
		if percent <= 1 or percent >= 84: 
			try: 
				test = response.json()
				if response.status_code <= 299:
					tools_log('TRAKT_SCROBBLE_ACTION_SUCCESS')
				else:
					tools_log(str(response)+'===>TRAKT_SCROBBLE_ACTION_FAIL____OPEN_INFO')
			except: 
				tools_log(str(response)+'===>TRAKT_SCROBBLE_TMDB____OPEN_INFO')
				response = 'ERROR'
		return response

	def trakt_meta_scrobble(self, action):
		try: 
			trakt_meta = self.get_trakt_scrobble_details()
		except: 
			tools_log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
			return
		self.trakt_watched = trakt_meta.get('trakt_watched') 

		response = None
		try: 
			self.player_meta['percentage'] = (trakt_meta.get('resume_position') / trakt_meta.get('resume_duration')) * 100
		except: 
			self.player_meta['percentage'] = 0
		if (self.player_meta['percentage'] > 90 and self.getProperty('script.xtreme_vod.ResolvedUrl') == 'true') or self.player_meta['percentage'] == 0:
			tools_log(str('script.xtreme_vod.ResolvedUrl==TRUE')+'===>OPENINFO')
			if self.trakt_watched  == True:
				return
		if self.trakt_watched:
			return self.trakt_watched
		if self.player_meta['percentage'] > 5 and self.player_meta['percentage'] < 80:
			self.player_meta['percentage'] = self.player_meta['percentage'] -1
		if self.player_meta['percentage'] >= 80:
			action = 'stop'
			self.trakt_watched  = True
		if trakt_meta.get('tmdb_id') == None and self.trakt_scrobble != 'false':
			if trakt_meta.get('episode') != None and trakt_meta.get('movie_title') == None:
				response = self.trakt_scrobble_tv(title=trakt_meta.get('tv_title'), season=trakt_meta.get('season'), episode=trakt_meta.get('episode'), percent=self.player_meta['percentage'],action=action)
			if trakt_meta.get('movie_title') != None:
				response = self.trakt_scrobble_title(movie_title=trakt_meta.get('movie_title'), movie_year=trakt_meta.get('movie_year'), percent=self.player_meta['percentage'], action=action)
		if trakt_meta.get('tmdb_id') != None and self.trakt_scrobble != 'false':
			if trakt_meta.get('episode') != None and trakt_meta.get('movie_title') == None:
				response = self.trakt_scrobble_tv(title='tmdb_id='+str(trakt_meta.get('trakt_tmdb_id')), season=trakt_meta.get('season'), episode=trakt_meta.get('episode'), percent=self.player_meta['percentage'],action=action)
			elif trakt_meta.get('episode') != None and trakt_meta.get('movie_title') != None:
				response = self.trakt_scrobble_title(movie_title=trakt_meta.get('movie_title'), movie_year=trakt_meta.get('movie_year'), percent=self.player_meta['percentage'], action=action)
			else:
				response = self.trakt_scrobble_tmdb(tmdb_id=trakt_meta.get('trakt_tmdb_id'),percent=self.player_meta['percentage'],action=action)
		if response == 'ERROR':
			#xbmc.executebuiltin('RunScript(plugin.video.themoviedb.helper,authorize_trakt)')
			#from resources.lib.trakt_api import refresh_token
			from resources.lib.trakt_api import get_access_token
			#refresh_token()
			get_access_token()
			self.trakt_error = 'ERROR'
		return self.trakt_watched 


	def curr_playback(self):
		json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0","id": "1","method": "Player.GetProperties","params": {"playerid": %s,"properties": ["position","playlistid","speed"]}}' % (self.playerid))
		json_object  = json.loads(json_result)
		try: 
			json_speed = json_object['result']['speed']
		except:
			json_speed = 1
		if json_speed == 1:
			self.player_meta['curr_playback'] = 'PLAY'
			self.player_meta['curr_playback_count'] = 0
		elif json_speed == 0:
			self.player_meta['curr_playback'] = 'PAUSE'
			self.player_meta['curr_playback_count'] = self.player_meta['curr_playback_count'] + 1
		json_object['result']['curr_playback_count'] = self.player_meta['curr_playback_count']
		return json_object

	def scrobble_trakt_speed_resume_test(self):
		self.update_resume_position_duration()
		return_flag = False
		json_speed = 1
		json_object  = self.curr_playback()
		if int(time.time()) >= int(self.speed_time):

			if json_object['result']['curr_playback_count'] <= 10:
				self.trakt_scrobble_details()

			try: self.player_meta['playlist_position2'] = int(json_object['result']['position'])
			except: self.player_meta['playlist_position2'] = 0
			if int(self.player_meta['playlist_position2']) > int(self.player_meta['playlist_position']):
				return False

			try: 
				json_speed = json_object['result']['speed']
			except: 
				if abs(float(old_resume_position - self.player_meta['resume_position'])) < 0.05:
					json_speed = 0
				else:
					json_speed = 1


			if json_speed == 1 and self.speed == 0 and self.trakt_watched != 'true':
				if json_object['result']['curr_playback_count'] <= 10:
					self.trakt_watched = self.trakt_meta_scrobble(action='start')
					xbmc.sleep(1000)
					response = requests.get('https://api.trakt.tv/users/'+str(self.player_meta['user_slug']) + '/watching', headers=self.player_meta['headers'])
					if response.status_code == 204:
						self.trakt_watched = self.trakt_meta_scrobble(action='start')
				
				#tools_log('SPEED_0_PLAY', str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
				return_flag = True
			if int(self.speed) == 1 and json_speed == 0 and self.trakt_watched != 'true':
				if json_object['result']['curr_playback_count'] <= 10:
					self.trakt_watched = self.trakt_meta_scrobble(action='pause')
				#tools_log('SPEED_0_PAUSE', str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
				return_flag = True
			self.speed = json_speed
			self.speed_time = int(time.time()) + 5

		if return_flag:
			return
		if abs( float((self.player_meta['resume_position'] / self.player_meta['resume_duration']) * 100) - float(self.player_meta['percentage']) ) > 0.2 and self.trakt_watched != 'true':
			if json_object['result']['curr_playback_count'] <= 10:
				self.trakt_scrobble_details()
				self.trakt_watched  = self.trakt_meta_scrobble(action='pause')
				#tools_log('PAUSE', str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
				if self.trakt_watched == False:
					self.trakt_watched  = self.trakt_meta_scrobble(action='start')
					xbmc.sleep(1000)
					response = requests.get('https://api.trakt.tv/users/'+str(self.player_meta['user_slug']) + '/watching', headers=self.player_meta['headers'])
					if response.status_code == 204:
						self.trakt_watched = self.trakt_meta_scrobble(action='start')
					#tools_log('PLAY', str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
			self.speed_time = time.time()
			return_flag = True

		if return_flag:
			return
		if int(time.time()) >  int(self.scrobble_time) and self.player_meta['percentage'] < 80 and self.trakt_watched != 'true' and json_speed == 1:
			#json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0","id": "1","method": "Player.GetProperties","params": {"playerid": %s,"properties": ["position","playlistid","speed"]}}' % (self.playerid))
			#json_object  = json.loads(json_result)
			try: 
				json_speed = json_object['result']['speed']
			except: 
				json_speed = 0
			if json_speed == 0:
				self.scrobble_time = int(time.time()) + 10 * 60
				return
			if json_object['result']['curr_playback_count'] <= 10:
				self.trakt_watched  = self.trakt_meta_scrobble(action='pause')
				#tools_log('SCROBBLE_TIME_PAUSE', str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
				if self.trakt_watched == False:
					self.trakt_watched  = self.trakt_meta_scrobble(action='start')
					xbmc.sleep(1000)
					response = requests.get('https://api.trakt.tv/users/'+str(self.player_meta['user_slug']) + '/watching', headers=self.player_meta['headers'])
					if response.status_code == 204:
						self.trakt_watched = self.trakt_meta_scrobble(action='start')
					#tools_log('SCROBBLE_TIME_PLAY', str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
			self.scrobble_time = int(time.time()) + 10 * 60
			return_flag = True
		self.player_meta['percentage'] = (self.player_meta['resume_position'] / self.player_meta['resume_duration']) * 100


	def reopen_window(self):

		window_open = self.getProperty('xtreme_vod_running')
		self.player_meta['script.xtreme_vod_started'] = self.getProperty('script.xtreme_vod_started')
		self.player_meta['Next_EP_ResolvedUrl'] = self.getProperty('script.xtreme_vod.ResolvedUrl')

		if self.window_stack_enable == 'true' and (window_open == 'False' or self.player_meta['script.xtreme_vod_started'] == 'True'):
			xbmc.sleep(100)
			if xbmc.Player().isPlaying()==0:
				if self.getProperty('script.xtreme_vod_started') == 'True':
					xbmc.sleep(1000)
					reopen_window_var = self.getProperty('reopen_window_var')
					self.player_meta['script.xtreme_vod_started'] = False
					self.setProperty('script.xtreme_vod_started',self.player_meta['script.xtreme_vod_started'])
					if reopen_window_var == 'Started':
						self.clearProperty('reopen_window_var')
						reopen_window_var = ''
					return wm.pop_stack()
				else:
					return
		elif self.reopen_window_bool == 'true' and self.getProperty('script.xtreme_vod_started') == 'True' and not xbmc.getCondVisibility('Window.IsActive(10138)'):
			xbmc.sleep(100)
			if not xbmc.getCondVisibility('Window.IsActive(10138)') and xbmc.Player().isPlaying()==0:
				if self.getProperty('script.xtreme_vod_started') == 'True':
					tools_log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
					self.player_meta['script.xtreme_vod_started'] = False
					self.setProperty('script.xtreme_vod_started',self.player_meta['script.xtreme_vod_started'])
					tools_log(str('RunScript(%s,info=reopen_window)' % (addon_ID())))
					xbmc.executebuiltin('RunScript(%s,info=reopen_window)' % (addon_ID()))
					return
				else:
					return

	def onPlayBackEnded(self):
		tools_log(str('onPlayBackEnded'))

		if self.player_meta['script.xtreme_vod_player'] == False:
			tools_log('EXIT__script.xtreme_vod_player')
			return

		try:
			self.trakt_meta_scrobble(action='pause')
		except:
			pass
		if self.player_meta['percentage'] > 85:
			if self.player_meta['global_movie_flag'] == False:
				try:
					response = TheMovieDB.update_trakt_playback(trakt_type='tv',tmdb_id=self.player_meta['tmdb_id'],episode=self.player_meta['tv_episode'],season=self.player_meta['tv_season'])
				except:
					tools_log('EXCEPTION!!', 'TheMovieDB.update_trakt_playback')
					pass
			else:
				try: 
					response = TheMovieDB.update_trakt_playback(trakt_type='movie',tmdb_id=self.player_meta['tmdb_id'])
				except:
					tools_log('EXCEPTION!!', 'TheMovieDB.update_trakt_playback')
					pass

		self.clearProperty('trakt_scrobble_details')

		xbmc.sleep(100)
		gc.collect()
		return self.reopen_window()

	def onPlayBackStopped(self):
		tools_log(str('onPlayBackStopped'))

		if self.player_meta['script.xtreme_vod_player'] == False:
			tools_log('EXIT__script.xtreme_vod_player')
			return

		if self.iplayerwww == False:
			self.trakt_meta_scrobble(action='pause')
		else:
			return
		trakt_meta = self.get_trakt_scrobble_details()
		for i in ['script.xtreme_vod_time', 'xtreme_vod.ResolvedUrl_playlist', 'xtreme_vod.ResolvedUrl','trakt_scrobble_details']:
			self.clearProperty(i)

		if self.player_meta['percentage'] > 85:
			if self.player_meta['global_movie_flag'] == False:
				try:
					response = TheMovieDB.update_trakt_playback(trakt_type='tv',tmdb_id=self.player_meta['tmdb_id'],episode=self.player_meta['tv_episode'],season=self.player_meta['tv_season'])
				except:
					tools_log('EXCEPTION!!', 'TheMovieDB.update_trakt_playback')
					pass
			else:
				try: 
					response = TheMovieDB.update_trakt_playback(trakt_type='movie',tmdb_id=self.player_meta['tmdb_id'])
				except:
					tools_log('EXCEPTION!!', 'TheMovieDB.update_trakt_playback')
					pass

		xbmc.sleep(100)
		gc.collect()

		try: self.player_meta['resume_position'] = trakt_meta.get('resume_position')
		except: self.player_meta['resume_position'] = 0
		try: self.player_meta['resume_duration'] = trakt_meta.get('resume_duration')
		except: self.player_meta['resume_duration'] = 0
		try: self.player_meta['percentage'] = (trakt_meta.get('resume_position') / trakt_meta.get('resume_duration')) * 100
		except: self.player_meta['percentage'] = 0

		self.player_meta['global_movie_flag'] = None
		self.player_meta['dbID'] = None

		try: 
			self.player_meta['dbID'] = int(self.player_meta['dbID'])
			if self.player_meta['dbID'] == 0:
				self.player_meta['dbID'] = None
		except: 
			self.player_meta['dbID'] = None

		try:
			if self.player_meta['global_movie_flag'] == True and self.player_meta['dbID'] != None and self.player_meta['percentage'] < 85 and self.player_meta['percentage'] > 3 and self.player_meta['resume_duration'] > 300:
				self.SetMovieDetails(dbID=self.player_meta['dbID'], resume_position=self.player_meta['resume_position'], resume_duration= self.player_meta['resume_duration'])
			if self.player_meta['global_movie_flag'] == False and self.player_meta['dbID'] != None and self.player_meta['percentage'] < 85 and self.player_meta['percentage'] > 3 and self.player_meta['resume_duration'] > 300:
				self.SetEpisodeDetails(dbID=self.player_meta['dbID'], resume_position=self.player_meta['resume_position'], resume_duration= self.player_meta['resume_duration'])
			if self.player_meta['global_movie_flag'] == True and self.player_meta['dbID'] != None and self.player_meta['resume_duration'] < 300:
				self.SetMovieDetails(dbID=self.player_meta['dbID'], resume_position=str(0), resume_duration= self.player_meta['resume_duration'])
			if self.player_meta['global_movie_flag'] == False and self.player_meta['dbID'] != None and self.player_meta['resume_duration'] < 300 and self.player_meta['resume_duration'] != 60:
				self.SetEpisodeDetails(dbID=self.player_meta['dbID'], resume_position=str(0), resume_duration= self.player_meta['resume_duration'])

		except:
			tools_log(str('EXCEPTION_onPlayBackStopped')+'===>OPENINFO')
			return self.reopen_window()

		return self.reopen_window()


	def onPlayBackStarted(self):
		Utils.hide_busy()
		tools_log(str('onPlayBackStarted'))
		TMDbHelper_PlayerInfoString = xbmcgui.Window(10000).getProperty('TMDbHelper.PlayerInfoString_NEW')
		if TMDbHelper_PlayerInfoString != '':
			xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_PlayerInfoString}'.replace('\'','"'))
		xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString_NEW','')
		
		#wm.reopen_window_var = 'Started'
		self.setProperty('reopen_window_var','Started')

		self.player_meta['script.xtreme_vod_player'] = None
		self.player_meta['script.xtreme_vod_started'] = None
		self.trakt_error = None

		self.player_meta['script.xtreme_vod_time'] = self.getProperty('script.xtreme_vod_time')
		self.player_meta['script.xtreme_vod_player_time'] = self.getProperty('script.xtreme_vod_player_time')

		if self.player_meta['script.xtreme_vod_player_time'] == '':
			self.player_meta['script.xtreme_vod_player_time'] = 0
			if self.player_meta['script.xtreme_vod_time'] != '':
				self.player_meta['script.xtreme_vod_player_time'] = int(self.player_meta['script.xtreme_vod_time'])
		else:
			self.player_meta['script.xtreme_vod_player_time'] = int(self.player_meta['script.xtreme_vod_player_time'])

		json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0","id": "1","method": "Player.GetProperties","params": {"playerid": 1,"properties": ["position","playlistid"]}}')
		json_object  = json.loads(json_result)
		try: self.player_meta['playlist_position'] = int(json_object['result']['position'])
		except: self.player_meta['playlist_position'] = 0

		self.player_meta['Next_EP_ResolvedUrl'] = self.getProperty('script.xtreme_vod.ResolvedUrl')
		if self.player_meta['Next_EP_ResolvedUrl'] == 'suppress_reopen_window':
			self.clearProperty('script.xtreme_vod.ResolvedUrl')
			self.player_meta['script.xtreme_vod_started'] = False
			
		self.clearProperty('script.xtreme_vod.ResolvedUrl_playlist')
		self.clearProperty('trakt_scrobble_details')
		if int(time.time()) < self.player_meta['script.xtreme_vod_player_time'] or self.player_meta['Next_EP_ResolvedUrl'] == 'true':
			self.player_meta['script.xtreme_vod_player'] = True
			self.clearProperty('script.xtreme_vod.ResolvedUrl')
		else:
			self.player_meta['script.xtreme_vod_player'] = False

		if self.player_meta['script.xtreme_vod_time'] == '':
			self.player_meta['script.xtreme_vod_time'] = 0
		else:
			self.player_meta['script.xtreme_vod_time'] = int(self.player_meta['script.xtreme_vod_time'])
		if self.player_meta['script.xtreme_vod_time'] + 120 > int(time.time()):
			self.player_meta['script.xtreme_vod_started'] = True
		elif self.player_meta['script.xtreme_vod_time'] == 0:
			self.player_meta['script.xtreme_vod_started'] = False
		elif self.player_meta['script.xtreme_vod_time'] + 120 < int(time.time()):
			if self.player_meta['playlist_position'] >= 1:
				self.player_meta['script.xtreme_vod_started'] = True
			else:
				self.player_meta['script.xtreme_vod_started'] = False
				self.clearProperty('script.xtreme_vod_time')
			#self.player_meta['script.xtreme_vod_started'] = True
		elif self.player_meta['playlist_position'] == 0:
			self.player_meta['script.xtreme_vod_started'] = False
			self.clearProperty('script.xtreme_vod_time')

		self.setProperty('script.xtreme_vod_started',self.player_meta['script.xtreme_vod_started'])
		#tools_log(str(self.player_meta['script.xtreme_vod_started'])+'script.xtreme_vod_started_onPlayBackStarted===>script.xtreme_vod_started')

		if self.player_meta['script.xtreme_vod_player'] == False:
			tools_log('EXIT__script.xtreme_vod_player')
			return


		if self.player_meta['script.xtreme_vod_started'] == True:
			self.setProperty('script.xtreme_vod_started', 'True')
		else:
			self.clearProperty('script_xtreme_vod_running')

		if self.trakt_scrobble == 'false':
			tools_log(str(' self.trakt_scrobble == "false":'))
			return
		self.player_meta['headers'] = library.trak_auth()

		player = self.player
		self.player_meta['resume_duration'] = None
		self.player_meta['resume_position'] = None
		self.player_meta['dbID'] = None
		self.player_meta['db_path'] = library.db_path()
		self.player_meta['global_movie_flag'] = False
		self.player_meta['tmdb_id'] = None
		self.player_meta['trakt_tmdb_id'] = None
		self.player_meta['movie_title'] = None
		self.player_meta['imdb_id'] = None
		self.player_meta['tv_title'] = None
		self.player_meta['title'] = None
		self.player_meta['VideoPlayer.Year'] = None
		self.player_meta['tv_season'] = None
		self.player_meta['tv_episode'] = None
		self.player_meta['movie_year'] = None
		self.player_meta['timestamp'] = None
		self.player_meta['user_slug'] = trakt_slug = xbmcaddon.Addon().getSetting('trakt_slug')

		self.player_meta['curr_playback'] = 'PLAY'
		self.player_meta['curr_playback_count'] = 0

		count = 0
		while player.isPlaying()==1 and count < 7501:
			try:
				self.player_meta['resume_position'] = player.getTime()
			except:
				self.player_meta['resume_position'] = ''
			if self.player_meta['resume_position'] != '':
				if self.player_meta['resume_position'] > 0:
					break
			else:
				xbmc.sleep(100)
				count = count + 100

		gc.collect()
		if player.isPlaying()==0:
			return
		json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Title", "Player.Filename","Player.Filenameandpath", "VideoPlayer.MovieTitle", "VideoPlayer.TVShowTitle", "VideoPlayer.DBID", "VideoPlayer.DBTYPE", "VideoPlayer.Duration", "VideoPlayer.Season", "VideoPlayer.Episode", "VideoPlayer.DBID", "VideoPlayer.Year", "VideoPlayer.Rating", "VideoPlayer.mpaa", "VideoPlayer.Studio", "VideoPlayer.VideoAspect", "VideoPlayer.Plot", "VideoPlayer.RatingAndVotes", "VideoPlayer.Genre", "VideoPlayer.LastPlayed", "VideoPlayer.IMDBNumber", "ListItem.DBID", "Container.FolderPath", "Container.FolderName", "Container.PluginName", "ListItem.TVShowTitle", "ListItem.FileNameAndPath"]}, "id":1}')
		json_object  = json.loads(json_result)
		self.player_meta['VideoPlayer.Year'] = str(json_object['result']['VideoPlayer.Year'])
		self.player_meta['timestamp']= json_object['result']['VideoPlayer.Duration']
		if 'iplayerwww' in str(json_object['result']['Player.Filenameandpath']):
			self.iplayerwww = True
		else:
			self.iplayerwww = False
		try: self.player_meta['resume_duration'] = functools.reduce(lambda x, y: x*60+y, [int(i) for i in (self.player_meta['timestamp'].replace(':',',')).split(',')])
		except: self.player_meta['resume_duration'] = 60

		if ('trailer' in str(json_result).lower() and self.player_meta['resume_duration'] < 300) or 'plugin.video.youtube' in str(json_result).lower():
			return

		self.player_meta['imdb_id'] = json_object['result']['VideoPlayer.IMDBNumber']
		self.player_meta['dbID'] = json_object['result']['VideoPlayer.DBID']

		tools_log(json_result)

		if 'index.bdmv' != json_object['result']['Player.Filename']:
			PTN_info = get_guess(json_object['result']['Player.Filename'])
		else:
			PTN_info = {}

		self.player_meta['VideoPlayer.Title'] = json_object['result']['VideoPlayer.Title']
		if json_object['result']['VideoPlayer.TVShowTitle'] != '':
			self.player_meta['tv_title'] = json_object['result']['VideoPlayer.TVShowTitle']
			self.player_meta['tv_season'] = int(json_object['result']['VideoPlayer.Season'])
			self.player_meta['tv_episode'] = int(json_object['result']['VideoPlayer.Episode'])
			self.player_meta['VideoPlayer.Year'] = str(json_object['result']['VideoPlayer.Year'])
			self.player_meta['title'] = json_object['result']['VideoPlayer.Title']
			self.type = 'episode'
		elif json_object['result']['VideoPlayer.MovieTitle'] != '':
			self.player_meta['VideoPlayer.Year'] = str(json_object['result']['VideoPlayer.Year'])
			self.player_meta['movie_year'] = str(json_object['result']['VideoPlayer.Year'])
			self.player_meta['movie_title'] = json_object['result']['VideoPlayer.MovieTitle']
			self.player_meta['title'] = json_object['result']['VideoPlayer.MovieTitle']
			self.type = 'movie'
		elif 'tt' in str(self.player_meta['imdb_id']):
			response = TheMovieDB.get_tmdb_data('find/%s?external_source=imdb_id&language=%s&' % (self.player_meta['imdb_id'], xbmcaddon.Addon().getSetting('LanguageID')), 30)
			if response.get('movie_results','') != '':
				self.type = 'movie'
				PTN_info['type'] = 'movie'
				self.player_meta['global_movie_flag'] = True
			elif response.get('tv_results','') != '':
				self.type = 'episode'
				PTN_info['type'] = 'episode'

		elif PTN_info['type'] == 'episode':
			self.player_meta['tv_title'] = PTN_info.get('title','')
			self.player_meta['tv_season'] = PTN_info.get('season','')
			try: self.player_meta['tv_episode'] = PTN_info['episode'][0]
			except: self.player_meta['tv_episode'] = PTN_info.get('episode','')
			self.player_meta['title'] = PTN_info.get('episode_title','')
			self.type = 'episode'
		elif json_object['result']['VideoPlayer.Title'] != '' and json_object['result']['VideoPlayer.Season'] == '':
			self.player_meta['VideoPlayer.Year'] = str(json_object['result']['VideoPlayer.Year'])
			self.player_meta['movie_year'] = str(json_object['result']['VideoPlayer.Year'])
			self.player_meta['movie_title'] = json_object['result']['VideoPlayer.Title']
			self.player_meta['title'] = json_object['result']['VideoPlayer.Title']
			if not 'pvr://' in str(json_object['result']['Player.Filenameandpath']):
				self.type = 'movie'
		elif json_object['result']['VideoPlayer.Title'] != '' and json_object['result']['VideoPlayer.Season'] != '':
			self.player_meta['tv_title'] = json_object['result']['VideoPlayer.Title']
			self.player_meta['tv_season'] = int(json_object['result']['VideoPlayer.Season'])
			self.player_meta['tv_episode'] = int(json_object['result']['VideoPlayer.Episode'])
			self.player_meta['VideoPlayer.Year'] = str(json_object['result']['VideoPlayer.Year'])
			self.player_meta['title'] = json_object['result']['VideoPlayer.Title']
			self.type = 'episode'
		if self.player_meta['title'] == None or self.player_meta['title'] == '':
			self.player_meta['title'] = json_object['result']['VideoPlayer.Title']


		if self.type == None:
			if not 'pvr://' in str(json_object['result']['Player.Filenameandpath']):
				self.type = PTN_info['type']
			else:
				self.iplayerwww = True
			if self.type == 'episode':
				self.player_meta['tv_title'] = PTN_info.get('title','')
				self.player_meta['tv_season'] = PTN_info.get('season','')
				try: self.player_meta['tv_episode'] = PTN_info['episode'][0]
				except: self.player_meta['tv_episode'] = PTN_info.get('episode','')
			if self.type == 'movie':
				self.player_meta['VideoPlayer.Year'] = PTN_info.get('year','')
				self.player_meta['movie_year'] = PTN_info.get('year','')
				self.player_meta['movie_title'] = PTN_info.get('title','')
				self.player_meta['title'] = PTN_info.get('title','')

		if 'tt' in str(self.player_meta['imdb_id']) and self.type == 'movie':
			self.player_meta['tmdb_id'] = TheMovieDB.get_movie_tmdb_id(imdb_id=self.player_meta['imdb_id'])
			self.player_meta['trakt_tmdb_id'] = self.player_meta['tmdb_id']
			self.player_meta['global_movie_flag'] = True
			if json_object['result'].get('VideoPlayer.Year',False):
				self.player_meta['VideoPlayer.Year'] = str(json_object['result']['VideoPlayer.Year'])
				self.player_meta['movie_year'] = str(json_object['result']['VideoPlayer.Year'])
			if json_object['result'].get('VideoPlayer.Title',False):
				self.player_meta['movie_title'] = str(json_object['result']['VideoPlayer.Title'])
				self.player_meta['title'] = str(json_object['result']['VideoPlayer.Title'])


		if 'tt' in str(self.player_meta['imdb_id']) and self.type == 'episode':
			try:
				self.player_meta['tmdb_id'] = TheMovieDB.get_show_tmdb_id(imdb_id=self.player_meta['imdb_id'])
				self.player_meta['trakt_tmdb_id'] = self.player_meta['tmdb_id']
			except:
				self.player_meta['tmdb_id'] = None
				self.player_meta['imdb_id'] = None


		if self.type == 'episode' and (self.player_meta['tmdb_id'] == None or str(self.player_meta['tmdb_id']) == ''):
			regex2 = re.compile('(19|20)[0-9][0-9]')
			clean_tv_title2 = regex2.sub(' ', self.player_meta['tv_title'].replace('\'','').replace('&',' ')).replace('  ',' ')
			response = TheMovieDB.get_tmdb_data('search/tv?query=%s&language=en-US&include_adult=%s&' % (clean_tv_title2, xbmcaddon.Addon().getSetting('include_adults')), 30)
			self.player_meta['tmdb_id'] = response['results'][0]['id']
			self.player_meta['trakt_tmdb_id'] = self.player_meta['tmdb_id']
		elif self.type == 'movie' and (self.player_meta['tmdb_id'] == None or str(self.player_meta['tmdb_id']) == ''):
			response = TheMovieDB.get_tmdb_data('search/movie?query=%s&language=en-US&year=%s&include_adult=%s&' % (self.player_meta['movie_title'], str(self.player_meta['movie_year']), xbmcaddon.Addon().getSetting('include_adults')), 30)
			try: 
				self.player_meta['tmdb_id'] = response['results'][0]['id']
			except: 
				self.player_meta['movie_title'] = PTN_info.get('title','')
				self.player_meta['movie_year'] = PTN_info.get('year','')
				try: 
					response = TheMovieDB.get_tmdb_data('search/movie?query=%s&language=en-US&year=%s&include_adult=%s&' % (self.player_meta['movie_title'], str(self.player_meta['movie_year']), xbmcaddon.Addon().getSetting('include_adults')), 30)
					self.player_meta['tmdb_id'] = response['results'][0]['id']
				except: 
					response = get_trakt_data(url='https://api.trakt.tv/search/%s?query=%s' % ('movie,show', self.player_meta['movie_title']), cache_days=7)
					tools_log(response, 'MOVIE_EXCEPTION_get_trakt_data')
					if len(response) > 0:
						for i in response:
							curr_type = i['type']
							if i[curr_type]['year'] == self.player_meta['movie_year']:
								self.player_meta['imdb_id'] = i[curr_type]['ids']['imdb']
								self.player_meta['tmdb_id'] = i[curr_type]['ids']['tmdb']
								if curr_type == 'show':
									self.type = 'episode'
									self.player_meta['tv_title'] = self.player_meta['movie_title']
					tools_log(self.player_meta)
			self.player_meta['trakt_tmdb_id'] = self.player_meta['tmdb_id']

		if not 'tt' in str(self.player_meta['imdb_id']) and (str(self.player_meta['tmdb_id']) != '' or self.player_meta['tmdb_id'] != None):
			if self.type == 'movie':
				self.player_meta['imdb_id'] = TheMovieDB.get_imdb_id_from_movie_id(self.player_meta['tmdb_id'])
			elif self.type == 'episode':
				response = TheMovieDB.get_tvshow_ids(self.player_meta['tmdb_id'])
				self.player_meta['imdb_id'] = response['imdb_id']

		if self.player_meta['dbID'] == '' and self.type != 'episode':
			self.player_meta['dbID'] = self.movie_populate_dbid()

		if self.player_meta['dbID'] == '' and self.type == 'episode':
			self.player_meta['dbID'] = self.episode_populate_dbid()

		try:self.playing_file = player.getPlayingFile()
		except: return
		self.player_meta['playing_file'] = self.playing_file

		"""
		try: 
			languages = TheMovieDB.get_imdb_language(self.player_meta['imdb_id'])
		except Exception as e:
			if 'port=443' in str(e):
				xbmcgui.Dialog().notification(heading='get_imdb_language ERROR', message='you might want to restart HTTP error', icon=icon_path(),time=1000,sound=True)
				languages = ['English']
			else:
				languages = ['English']
		video_info = player.getVideoInfoTag()
		player_subs_lang_fix = xbmcaddon.Addon(addon_ID()).getSetting('player_subs_lang_fix')
		if player_subs_lang_fix == True or player_subs_lang_fix == 'true':
			audio_languages = [audio for audio in xbmc.Player().getAvailableAudioStreams()]
			subtitle_languages = [subtitle for subtitle in xbmc.Player().getAvailableSubtitleStreams()]

			current_sub_language2 = xbmc.getInfoLabel('VideoPlayer.SubtitlesLanguage')
			current_audio_language = xbmc.getInfoLabel('VideoPlayer.AudioLanguage')

			json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0","id": "1","method": "Player.GetProperties","params": {"playerid": 1,"properties": ["subtitles","audiostreams","subtitleenabled"]}}')
			sub_audio_json  = json.loads(json_result)
			json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0","id": "1","method": "Player.GetProperties","params": {"playerid": 1,"properties": ["currentaudiostream", "currentsubtitle", "currentvideostream"]}}')
			curr_sub_audio_json  = json.loads(json_result)

			lang_toggle = False
			#tools_log('languages',languages, 'audio_languages', audio_languages, 'subtitle_languages', subtitle_languages,   'current_sub_language2',current_sub_language2,'current_audio_language',current_audio_language,'sub_audio_json',sub_audio_json,'curr_sub_audio_json',curr_sub_audio_json)
			if languages[0] == 'English':
				if current_audio_language != 'eng' or not 'eng' in str(curr_sub_audio_json['result']['currentaudiostream']).lower():
					#if self.type == 'movie':
						#tools_log('languages',languages, 'audio_languages', audio_languages, 'subtitle_languages', subtitle_languages,   'current_sub_language2',current_sub_language2,'current_audio_language',current_audio_language,'sub_audio_json',sub_audio_json,'curr_sub_audio_json',curr_sub_audio_json)
					if 'dts' in current_audio_language.lower() and self.type == 'movie':
						tools_log('UNKNOWN_MOVIE_AUDIO_DTS')
					else:
						for i in sub_audio_json['result']['audiostreams']:
							if i['language'] == 'eng' or 'eng' in i['name'].lower() and not 'commentary' in str(i).lower():
								resume_position = player.getTime()
								player.setAudioStream(i['index'])
								player.seekTime(resume_position-5)
								tools_log('ENGLISH_LANG_NON_ENG_AUDIO_FIX')
								lang_toggle = True
								break
						if lang_toggle == False:
							for i in sub_audio_json['result']['audiostreams']:
								if i['language'] in i['name'] and 'Original' in i['name']:
									resume_position = player.getTime()
									player.setAudioStream(i['index'])
									player.seekTime(resume_position-5)
									tools_log('ORIGINAL__NON_ENG_AUDIO_FIX')
									lang_toggle = True
									break
				if current_audio_language == 'eng' and 'commentary' in str(curr_sub_audio_json['result']['currentaudiostream']['name'].lower()):
					for i in sub_audio_json['result']['audiostreams']:
						if 'dts' in i['language'].lower() and self.type == 'movie':
							resume_position = player.getTime()
							player.setAudioStream(i['index'])
							player.seekTime(resume_position-5)
							tools_log('COMMENTARY_UNKNOWN_MOVIE_AUDIO_DTS')
							lang_toggle = True
							break
				
			if languages[0] != 'English':
				if sub_audio_json['result']['subtitleenabled'] == False or sub_audio_json['result']['subtitleenabled'] == 'False':
					for i in reversed(sub_audio_json['result']['subtitles']):
						if i['language'] == 'eng':
							player.setSubtitleStream(i['index'])
							player.showSubtitles(True)
							tools_log('NON_ENGLISH_LANG_ENG_SUBS_FIX')
							break
				if current_audio_language == 'eng':
					for i in sub_audio_json['result']['audiostreams']:
						if babelfish.Language(i['language']).name == languages[0]:
							resume_position = player.getTime()
							player.setAudioStream(i['index'])
							player.seekTime(resume_position-5)
							#tools_log('languages',languages, 'audio_languages', audio_languages, 'subtitle_languages', subtitle_languages,   'current_sub_language2',current_sub_language2,'current_audio_language',current_audio_language,'sub_audio_json',sub_audio_json,'curr_sub_audio_json',curr_sub_audio_json)
							tools_log('NON_ENGLISH_LANG_ENG_DUB_FIX')
							break
			sub_toggle = False

			force_toggle = False
			try:
				for i in sub_audio_json['result']['subtitles']:
					if 'External' in str(i) and i['isforced'] == True:
						force_toggle = True
						break
			except:
				pass


			if lang_toggle == True or force_toggle == True:
				for i in reversed(sub_audio_json['result']['subtitles']):
					if i['language'] == 'eng' and (i['isforced'] == True or i['isforced'] == 'True' or 'forced' in str(i['name']).lower()):
						if sub_audio_json['result']['subtitleenabled'] == False or sub_audio_json['result']['subtitleenabled'] == 'False':
							player.setSubtitleStream(i['index'])
							player.showSubtitles(True)
							tools_log('ENGLISH_LANG_NON_ENG_AUDIO_FORCED_SUBS_FIX')
							sub_toggle = True
							break
			if sub_toggle == False and current_sub_language2 != 'eng':
				for i in reversed(sub_audio_json['result']['subtitles']):
					if i['language'] == 'eng':
						player.setSubtitleStream(i['index'])
						player.showSubtitles(False)
						tools_log('ENGLISH_LANG_NON_ENG_SUBS_FORCED_SUBS_FIX')
						sub_toggle = True
						break
			json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0","id": "1","method": "Player.GetProperties","params": {"playerid": 1,"properties": ["subtitleenabled"]}}')
			subtitleenabled  = json.loads(json_result)
			if languages[0] == 'English' and (subtitleenabled['result']['subtitleenabled'] == 'True' or subtitleenabled['result']['subtitleenabled'] == True):
				forced_external = False
				for i in reversed(sub_audio_json['result']['subtitles']):
					if i['language'] == 'eng' and (i['isforced'] == True or i['isforced'] == 'True' or 'forced' in str(i['name']).lower()) and i['name'] == '(External)':
						forced_external = True
						break
				if forced_external == True:
					for i in reversed(sub_audio_json['result']['subtitles']):
						if i['language'] == 'eng' and (i['isforced'] == True or i['isforced'] == 'True' or 'forced' in str(i['name']).lower()) and i['name'] != '(External)':
							player.setSubtitleStream(i['index'])
							player.showSubtitles(True)
							tools_log('ENGLISH_LANG_FORCED_EXTERNAL_SUBS_FIX')
							sub_toggle = True
							break
		"""

		if self.type == 'episode':
			try: TMDbHelper_PlayerInfoString = eval(xbmcgui.Window(10000).getProperty('TMDbHelper.PlayerInfoString'))
			except: TMDbHelper_PlayerInfoString = {}
			response = TheMovieDB.get_tvshow_ids(self.player_meta['tmdb_id'])
			TMDbHelper_NEW_PlayerInfoString = {'tmdb_type': self.type, 'tmdb_id': str(self.player_meta['tmdb_id']), 'imdb_id': str(self.player_meta['imdb_id']), 'tvdb_id': str(response['tvdb_id']), 'season': self.player_meta['tv_season'], 'episode': self.player_meta['tv_episode']}
			if TMDbHelper_PlayerInfoString != TMDbHelper_NEW_PlayerInfoString:
				tools_log('TMDbHelper_NEW_PlayerInfoString',TMDbHelper_NEW_PlayerInfoString)
				xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))

		if self.type == 'movie':
			self.player_meta['global_movie_flag'] = True
			try: self.player_meta['resume_position'] = player.getTime()
			except: return
			self.player_meta['percentage'] = (self.player_meta['resume_position'] / self.player_meta['resume_duration']) * 100
			if self.player_meta['tmdb_id'] != '':
				try: response = self.trakt_scrobble_tmdb(self.player_meta['tmdb_id'], self.player_meta['percentage'] )
				except: pass
			elif self.player_meta['movie_year'] != '' and self.player_meta['movie_title'] != '':
				try: 
					response = self.trakt_scrobble_title(self.player_meta['movie_title'], self.player_meta['movie_year'], self.player_meta['percentage'] )
				except: 
					pass
			try: 
				self.player_meta['movie_title'] = response['movie']['title']
				self.player_meta['movie_year'] = response['movie']['year']
			except: 
				pass

			self.trakt_scrobble_details()

			tools_log('PLAYBACK STARTED_imdb=%s, %s=dbID, %s=duration, %s=movie_title, %s=title===>___OPEN_INFO' % (self.player_meta['imdb_id'],str(self.player_meta['dbID']),str(self.player_meta['resume_duration']),self.player_meta['movie_title'],self.player_meta['title']))
			url = 'plugin://%s?info=play_vod_player&amp;type=movie&amp;movie_year=%s&amp;movie_title=%s&amp;tmdb=%s' % (addon_ID(), self.player_meta['movie_year'], self.player_meta['movie_title'], self.player_meta['tmdb_id'])
			tools_log(url)
			kodi_send_command = 'kodi-send --action="RunScript(%s,info=play_vod_player,type=movie,movie_year=%s,movie_title=%s,tmdb=%s,test=True)"' % (addon_ID(), self.player_meta['movie_year'], self.player_meta['movie_title'], self.player_meta['tmdb_id'])
			tools_log(kodi_send_command)
			self.setProperty('last_played_tmdb_helper', url)
			xbmcaddon.Addon(addon_ID()).setSetting('last_played_tmdb_helper', url)
			self.speed_time = int(time.time()) + 5

		if self.type == 'episode':
			self.player_meta['global_movie_flag'] = False
			tools_log('PLAYBACK STARTED_tmdb=%s, %s=dbID, %s=duration, %s=tv_show_name, %s=season_num, %s=ep_num, %s=title===>___OPEN_INFO' % (str(self.player_meta['tmdb_id']),str(self.player_meta['dbID']) ,str(self.player_meta['resume_duration']),self.player_meta['tv_title'],str(self.player_meta['tv_season']),str(self.player_meta['tv_episode']),self.player_meta['title']))
			url = 'plugin://%s?info=play_vod_player&amp;type=tv&amp;show_title=%s&amp;show_season=%s&amp;show_episode=%s&amp;tmdb=%s' % (addon_ID(), self.player_meta['tv_title'], self.player_meta['tv_season'], self.player_meta['tv_episode'], self.player_meta['tmdb_id'])
			tools_log(url)
			kodi_send_command = 'kodi-send --action="RunScript(%s,info=play_vod_player,type=tv,show_title=%s,show_season=%s,show_episode=%s,tmdb=%s,test=True)"' % (addon_ID(), self.player_meta['tv_title'], self.player_meta['tv_season'], self.player_meta['tv_episode'], self.player_meta['tmdb_id'])
			tools_log(kodi_send_command)
			self.setProperty('last_played_tmdb_helper', url)
			xbmcaddon.Addon(addon_ID()).setSetting('last_played_tmdb_helper', url)

			try: self.player_meta['resume_position'] = player.getTime()
			except: return
			self.player_meta['percentage'] = (self.player_meta['resume_position'] / self.player_meta['resume_duration']) * 100
			if str(self.player_meta['tmdb_id']) == '' or self.player_meta['tmdb_id'] == None:
				response = self.trakt_scrobble_tv(self.player_meta['tv_title'], self.player_meta['tv_season'], self.player_meta['tv_episode'], self.player_meta['percentage'])
				if not 'Response [404]' in str(response):
					self.player_meta['tmdb_id'] = response.json()['show']['ids']['tmdb']
			else:
				response = self.trakt_scrobble_tv('tmdb_id='+str(self.player_meta['tmdb_id']), self.player_meta['tv_season'], self.player_meta['tv_episode'], self.player_meta['percentage'])
			if 'Response [404]' in str(response) and self.player_meta['tv_season'] == 0:
				self.player_meta['movie_title'] = self.player_meta['VideoPlayer.Title']
				self.player_meta['movie_year'] = self.player_meta['VideoPlayer.Year']
				response = self.trakt_scrobble_title(self.player_meta['movie_title'], self.player_meta['movie_year'], self.player_meta['percentage'])
				
			try: response = response.json()
			except: response = None

			try: self.player_meta['trakt_tmdb_id'] = response['show']['ids']['tmdb']
			except: pass
			try: self.player_meta['tvdb_id'] = response['show']['ids']['tvdb']
			except: pass
			try: self.player_meta['imdb_id'] = response['show']['ids']['imdb']
			except: pass

			self.trakt_scrobble_details()
			self.speed_time = int(time.time()) + 5

		#tools_log(str(self.player_meta['script.xtreme_vod_started'])+'script.xtreme_vod_started===>script.xtreme_vod_started')
		if self.player_meta['script.xtreme_vod_player'] == False:
			tools_log('EXIT__script.xtreme_vod_player')
			return

		count = 0

		try: 
			self.player_meta['dbID'] = int(self.player_meta['dbID'])
			if self.player_meta['dbID'] == 0:
				self.player_meta['dbID'] = None
		except: 
			self.player_meta['dbID'] = None

		if self.type == 'movie':
			self.trakt_watched = False
			if self.iplayerwww:
				self.trakt_watched = True
			self.player_meta['percentage']  = 0
			self.library_refresh = False

			self.playerid = self.get_playerid()

			if self.update_resume_position_duration() == False:
				tools_log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
				return

			self.speed = 1
			self.speed_time = int(time.time()) + 5
			self.scrobble_time = int(time.time()) + 10 * 60
			
			self.trakt_scrobble_details()

		self.update_play_test(self.playing_file)
		if self.play_test == False:
			tools_log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
			return

		tools_log(str(self.player_meta['script.xtreme_vod_player'])+'script.xtreme_vod_player===>OPENINFO')

		#xbmc.sleep(1000 * 15)
		response = TheMovieDB.get_watching_user()
		#tools_log(response)
		if not str(self.player_meta['tmdb_id']) in str(response):
			trakt_meta = self.get_trakt_scrobble_details()
			try: self.player_meta['resume_position'] = player.getTime()
			except: return
			self.player_meta['percentage'] = (self.player_meta['resume_position'] / trakt_meta.get('resume_duration')) * 100
			if self.type == 'movie':
				response = self.trakt_scrobble_title(movie_title=trakt_meta.get('movie_title'), movie_year=trakt_meta.get('movie_year'), percent=self.player_meta['percentage'], action='start')
				#tools_log(response)
			else:
				response = self.trakt_scrobble_tv(title=trakt_meta.get('tv_title'), season=trakt_meta.get('season'), episode=trakt_meta.get('episode'), percent=self.player_meta['percentage'],action='start')
				#tools_log(response)
		self.speed_time = time.time()
		trakt_meta = self.get_trakt_scrobble_details()
		try: self.player_meta['resume_position'] = player.getTime()
		except: return
		self.player_meta['percentage'] = (self.player_meta['resume_position'] / trakt_meta.get('resume_duration',1.00)) * 100

		while self.play_test and self.type == 'movie':
			try: 
				self.update_play_test(self.playing_file)
				old_resume_position = self.player_meta['resume_position']
				xbmc.sleep(250)
				self.player_meta['resume_position'] = player.getTime()
			except: 
				tools_log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
				return

			return_var = self.scrobble_trakt_speed_resume_test()
			if return_var == False:
				tools_log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
				return

			self.player_meta['percentage'] = (self.player_meta['resume_position'] / self.player_meta['resume_duration']) * 100

			if (self.player_meta['percentage'] > 85) and player.isPlayingVideo()==1 and self.player_meta['resume_duration'] > 300 and self.trakt_watched != 'true':
				self.trakt_watched  = self.trakt_meta_scrobble(action='stop')
				xbmc.sleep(250)
				if self.trakt_error:
					self.trakt_watched  = self.trakt_meta_scrobble(action='stop')
				self.trakt_scrobble_details()
				tools_log(str('STARTING...library.trakt_watched_movies_full'))
				library.trakt_refresh_all()
				self.library_refresh = True
				tools_log(str('FINISHED...library.trakt_watched_movies_full'))

			if (self.player_meta['percentage'] > 85) and self.library_refresh == False and player.isPlayingVideo()==1:
				try:
					if int(self.player_meta['dbID']) > 0:
						self.SetMovieDetails2(self.player_meta['dbID'], self.player_meta['resume_duration'])
				except TypeError: 
					return
				if not self.trakt_error:
					try: 
						response = TheMovieDB.update_trakt_playback(trakt_type='movie',tmdb_id=self.player_meta['tmdb_id'])
						#tools_log(str(response), 'TheMovieDB.update_trakt_playback')
					except:
						tools_log('EXCEPTION!!', 'TheMovieDB.update_trakt_playback')
						pass
					tools_log(str('STARTING...library.trakt_watched_movies_full'))
					library.trakt_refresh_all()
					self.library_refresh = True
					tools_log(str('FINISHED...library.trakt_watched_movies_full'))
				self.playing_file = None
				self.trakt_error = None
				return

		if self.type == 'episode':
			self.trakt_watched  = False
			if self.iplayerwww:
				self.trakt_watched = True
			self.player_meta['percentage'] = 0
			self.library_refresh = False
			self.prescrape_test = None

			self.playerid = self.get_playerid()

			if self.player_meta['script.xtreme_vod_player'] == True:
				next_ep_details = PLAYER.get_next_ep_details(season=self.player_meta['tv_season'], episode=self.player_meta['tv_episode'], tmdb=self.player_meta['tmdb_id'])
			else:
				next_ep_details = None
			#tools_log(str(self.player_meta['script.xtreme_vod_player'])+'script.xtreme_vod_player===>OPENINFO')

			prescrape = False
			if next_ep_details == None:
				prescrape = None

			if self.update_resume_position_duration() == False:
				return

			self.speed = 1
			self.speed_time = int(time.time()) + 5
			self.scrobble_time = int(time.time()) + 10 * 60
			self.trakt_scrobble_details()

		self.update_play_test(self.playing_file)
		if self.play_test == False:
			return

		self.player_meta['percentage'] = (self.player_meta['resume_position'] / self.player_meta['resume_duration']) * 100
		while self.play_test and self.type == 'episode':
			try: 
				#play_test = player.isPlaying()==1 and type == 'episode' and self.playing_file == player.getPlayingFile()
				self.update_play_test(self.playing_file)
				old_resume_position = self.player_meta['resume_position']
				xbmc.sleep(250)
				self.player_meta['resume_position'] = player.getTime()
			except: 
				return

			return_var = self.scrobble_trakt_speed_resume_test()
			if return_var == False:
				return

			self.player_meta['percentage'] = (self.player_meta['resume_position'] / self.player_meta['resume_duration']) * 100

			if self.player_meta['percentage'] > 33 and prescrape == False and self.player_meta['script.xtreme_vod_player'] == True:
				#next_ep_play_details = next_ep_play(show_title=next_ep_details['next_ep_show'], show_season=next_ep_details['next_ep_season'], show_episode=next_ep_details['next_ep_episode'], tmdb=next_ep_details['tmdb_id'])
				xbmcgui.Window(10000).clearProperty('script.xtreme_vod_download_link')
				tools_log('next_ep_play!!!',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
				kodi_send_command = 'RunScript(%s,info=play_vod_player,type=tv,show_title=%s,show_season=%s,show_episode=%s,tmdb=%s,prescrape=True)' % (addon_ID(), next_ep_details['next_ep_show'], next_ep_details['next_ep_season'], next_ep_details['next_ep_episode'], next_ep_details['tmdb_id'])
				TMDbHelper_NEW_PlayerInfoString['episode'] = next_ep_details['next_ep_episode']
				xbmcgui.Window(10000).setProperty('TMDbHelper.PlayerInfoString_NEW', f'{TMDbHelper_NEW_PlayerInfoString}'.replace('\'','"'))
				#xbmc.executebuiltin(kodi_send_command)
				PLAYER.prepare_play_VOD_episode(tmdb = next_ep_details['tmdb_id'], series_id=None, search_str = None,episode=next_ep_details['next_ep_episode'], season=next_ep_details['next_ep_season'], window=None)
				prescrape = True

			if self.player_meta['percentage'] > 33 and prescrape == True and self.player_meta['script.xtreme_vod_player'] == True:
				self.prescrape_test = xbmcgui.Window(10000).getProperty('script.xtreme_vod_download_link')
				if 'http' in str(self.prescrape_test):
					tools_log('DOWNLOAD_FOUND!!!',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
					prescrape = self.prescrape_test
					xbmcgui.Window(10000).clearProperty('script.xtreme_vod_download_link')


			#if self.player_meta['percentage'] > 33 and 'http' in str(prescrape) and self.player_meta['script.xtreme_vod_player'] == True:
			#	tools_log('next_ep_play!!!',str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			#	next_ep_play_details = PLAYER.next_ep_play(show_season=next_ep_details['next_ep_season'], show_episode=next_ep_details['next_ep_episode'], tmdb=next_ep_details['tmdb_id'],auto_rd=False,prescrape_test=self.prescrape_test)
			#	try: 
			#		prescrape = 'Done'
			#		if next_ep_play_details.get('ResolvedUrl') == True:
			#			tools_log(str(next_ep_play_details.get('ResolvedUrl'))+'ResolvedUrl_next_ep_play_details===>OPENINFO')
			#	except:
			#		tools_log('NOT_FOUND_PRESCRAPE2===>OPENINFO')


			if player.isPlaying()==1 and self.player_meta['percentage'] > 85 and self.trakt_watched == False:
				self.trakt_watched  = self.trakt_meta_scrobble(action='stop')
				xbmc.sleep(250)
				if self.trakt_error:
					self.trakt_watched  = self.trakt_meta_scrobble(action='stop')
				self.trakt_scrobble_details()
				tools_log(str('STARTING...library.trakt_watched_tv_shows_full'))
				library.trakt_refresh_all()
				self.library_refresh = True
				tools_log(str('FINISHED...library.trakt_watched_tv_shows_full'))

			if player.isPlayingVideo()==1 and self.player_meta['percentage'] > 85 and self.library_refresh == False:

				if self.player_meta['dbID'] != None:
					self.SetEpisodeDetails2(self.player_meta['dbID'], self.player_meta['resume_duration']) ##PLAYCOUNT_LASTPLAYED

				if not self.trakt_error:
					try:
						response = TheMovieDB.update_trakt_playback(trakt_type='tv',tmdb_id=self.player_meta['tmdb_id'],episode=self.player_meta['tv_episode'],season=self.player_meta['tv_season'])
						#tools_log(str(response), 'TheMovieDB.update_trakt_playback')
					except:
						tools_log('EXCEPTION!!', 'TheMovieDB.update_trakt_playback')
						pass

					tools_log(str('STARTING...library.trakt_watched_tv_shows_full'))
					library.trakt_refresh_all()
					self.library_refresh = True
					tools_log(str('FINISHED...library.trakt_watched_tv_shows_full'))

			if self.player_meta['script.xtreme_vod_player'] == False and self.player_meta['percentage'] > 85:
				#tools_log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
				self.playing_file = None
				if self.player_meta['script.xtreme_vod_started'] == True:
					#tools_log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename))+'===>OPENINFO')
					self.setProperty('script.xtreme_vod_time', str(int(time.time())+15))
				return

			if player.isPlaying()==1 and self.player_meta['percentage'] > 90 and 'http' in str(self.prescrape_test) and self.player_meta['script.xtreme_vod_player'] == True:
				try: 
					next_ep_url = self.prescrape_test
				except:
					return
				title = str(next_ep_details.get('next_ep_title'))
				thumb = next_ep_details.get('next_ep_thumb2','')
				if thumb == '':
					thumb = next_ep_details.get('next_ep_thumbnail')
				threads = []
				image_requests = []
				if thumb not in image_requests and thumb:
					image_thread = Utils.GetFileThread(thumb)
					threads += [image_thread]
					image_thread.start()
					image_requests.append(thumb)

				rating = next_ep_details.get('next_ep_rating')
				show = next_ep_details.get('next_ep_show')
				season = next_ep_details.get('next_ep_season')
				episode = next_ep_details.get('next_ep_episode')
				year = next_ep_details.get('next_ep_year')
				kodi_url = 'RunScript(%s,info=display_dialog,next_ep_url=%s,title=%s,thumb=%s,rating=%s,show=%s,season=%s,episode=%s,year=%s)' % (str(addon_ID()), str(next_ep_url), quote_plus(title), str(thumb), str(rating), str(show), str(season), str(episode), str(year))
				while not self.player_meta['resume_position'] > (self.player_meta['resume_duration'] - 35) and self.player_meta['resume_position'] < self.player_meta['resume_duration']:
					xbmc.sleep(250)
					self.update_play_test(self.playing_file)
					if self.play_test == False:
						return
				tools_log(str(kodi_url)+'kodi_url===>OPENINFO')
				xbmc.executebuiltin(kodi_url)
				self.playing_file = None
				self.trakt_error = None
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
		self.next_clean_time = 0
		#library_auto_sync = str(xbmcaddon.Addon(library.addon_ID()).getSetting('library_auto_sync'))
		trakt_kodi_mode = str(xbmcaddon.Addon(library.addon_ID()).getSetting('trakt_kodi_mode'))
		#trakt_calendar_auto_sync = str(xbmcaddon.Addon(library.addon_ID()).getSetting('trakt_calendar_auto_sync')).lower()
		#if library_auto_sync == 'true':
		#	library_auto_sync = True
		#if library_auto_sync == 'false':
		#	library_auto_sync = False
		if  xbmcaddon.Addon(addon_ID()).getSetting('auto_clean_cache_bool') == 'true':
			auto_clean_cache_bool = True
		else:
			auto_clean_cache_bool = False

		try: xml_m3u_sync_hours = int(xbmcaddon.Addon(addon_ID()).getSetting('xml_m3u_sync_hours'))
		except: xml_m3u_sync_hours = 8
		if xbmcaddon.Addon(addon_ID()).getSetting('local_xml_m3u') == 'true':
			local_xml_m3u = True
		else:
			local_xml_m3u = False

		startup_option = xbmcaddon.Addon().getSetting('startup_option')
		startup_url = None
		if startup_option == 'None':
			startup_url = None
		elif startup_option == 'Trakt Watched Movies':
			startup_url = 'RunScript(script.xtreme_vod,info=trakt_watched,trakt_type=movie)'
		elif startup_option == 'Trakt Watched TV':
			startup_url = 'RunScript(script.xtreme_vod,info=trakt_watched,trakt_type=tv)'
		elif startup_option == 'Reopen Last':
			startup_url = 'RunScript(script.xtreme_vod,info=reopen_window)'
		elif startup_option == 'VOD TV':
			startup_url = 'RunScript(script.xtreme_vod,info=alltv2)'
		elif startup_option == 'VOD Movies':
			startup_url = 'RunScript(script.xtreme_vod,info=allmovies2)'

		importlib.reload(Utils)
		
		library.trakt_refresh_all()
		self.xbmc_monitor.waitForAbort(5)  # Wait 10 minutes before doing updates to give boot time
		if self.xbmc_monitor.abortRequested():
			del self.xbmc_monitor
			return
		while not self.xbmc_monitor.abortRequested() and not self.exit and self.poll_time:
			tools_log(str('CronJobMonitor_STARTED_script.xtreme_vod_service_started'))
			self.curr_time = datetime.datetime.now().replace(minute=0,second=0, microsecond=0).timestamp()
			if int(time.time()) > self.next_time:# and library_auto_sync == True:  # Scheduled time has past so lets update
				library_update_period = int(xml_m3u_sync_hours)
				self.next_time = self.curr_time + xml_m3u_sync_hours*60*60
				tools_log(str('process.auto_sync'))

				movies = TheMovieDB.get_vod_data(action= 'get_vod_streams' ,cache_days=0.00001) 
				movies = TheMovieDB.get_vod_data(action= 'get_series' ,cache_days=0.00001) 
				if os.environ['first_run'] == str('True'):
					if startup_url:
						xbmc.executebuiltin(startup_url)
						startup_url = None
					os.environ['first_run'] = str('False')
				else:
					if local_xml_m3u:
						generate_m3u()
						generate_xmltv()
			elif int(time.time()) > self.next_time and trakt_kodi_mode == 'Trakt Only': 
				try: trakt_token = xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('trakt_token')
				except: trakt_token = None
				#if trakt_token:
				#	xbmc.executebuiltin('RunScript(plugin.video.themoviedb.helper,authorize_trakt)')
				#	self.xbmc_monitor.waitForAbort(5)
				self.next_time = self.curr_time + library_update_period*60*60
			if int(time.time()) > self.next_clean_time and auto_clean_cache_bool == True:
				tools_log(str('process.auto_clean_cache(days=30)'))
				process.auto_clean_cache(days=30)
				self.next_clean_time = self.curr_time + 24*60*60
			if startup_url:
				xbmc.executebuiltin(startup_url)
				startup_url = None
			tools_log(str('self.xbmc_monitor.waitForAbort(self.poll_time)'))
			tools_log(str(self.poll_time))
			
			self.xbmc_monitor.waitForAbort(self.poll_time)
		del self.xbmc_monitor


class ServiceMonitor(object):
	def __init__(self):
		tools_log(str('ServiceMonitor_script.xtreme_vod_service_started'))
		Utils.hide_busy()
		self.exit = False
		self.cron_job = CronJobMonitor(0)
		#self.cron_job.setName('Cron Thread')
		self.cron_job.name = 'Cron Thread'
		self.player_monitor = None
		self.my_monitor = None
		self.xbmc_monitor = xbmc.Monitor()

	def _on_listitem(self):
		self.xbmc_monitor.waitForAbort(0.3)

	def _on_scroll(self):
		self.xbmc_monitor.waitForAbort(1)

	def _on_fullscreen(self):
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
		self.xbmc_monitor.waitForAbort(1)

	def _on_exit(self):
		if not self.xbmc_monitor.abortRequested():
			ServiceStarted = ''
			ServiceStop = '' 
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
		tools_log(str('run_script.xtreme_vod_service_started'))
		os.environ['first_run'] = str('True')
		ServiceStarted = 'True'
		window_stack = xbmcvfs.translatePath('special://profile/addon_data/'+addon_ID()+ '/window_stack.db')

		self.player_monitor = PlayerMonitor()
		from resources.lib.trakt_api import get_trakt_auth
		get_trakt_auth(startup=True)

		if xbmcvfs.exists(window_stack):
			os.remove(window_stack)

		auto_plugin_route = xbmcaddon.Addon().getSetting('auto_plugin_route')
		auto_plugin_route_enable = xbmcaddon.Addon().getSetting('auto_plugin_route_enable')
		if auto_plugin_route_enable == 'true':
			if auto_plugin_route[0:7] == 'plugin:':
				xbmc.executebuiltin('RunPlugin(%s)' % auto_plugin_route)
			if auto_plugin_route[0:7] == 'script.':
				xbmc.executebuiltin('RunScript(%s)' % auto_plugin_route)

		self.cron_job.start()
		self.poller()

if __name__ == '__main__':
	xml_startup_process()
	ServiceMonitor().run()
