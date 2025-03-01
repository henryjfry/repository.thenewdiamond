# -*- coding: utf-8 -*-
'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re,urllib,os
try:
    import urlparse
except:
    from urllib.parse import urlparse

try:
    from metalibrary.modules import control
except:
	try:
		from modules import control
	except:
		from lib.metalibrary.modules import control

try: from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database

def open_database():
    DATABASE = control.metaDB
    connection = database.connect(DATABASE)
    #connection.text_factory = str
    connection.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
    connection.row_factory = database.Row
    print("DB connection opened to {0}.".format(DATABASE))
    return connection

def metaMovies(imdb=None, tmdb=None):
    try:
    
        if imdb != None: 
            type = 'imdb'
            id = imdb
        elif tmdb != None:
            type = 'tmdb'
            id = tmdb
        
        conn = open_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movies WHERE %s = '%s'" % (type, id))
        row = cursor.fetchone()
        meta = {}
        for id in row.keys(): meta[id] = row[id]
        return meta
        print("[METALIBRARY]", meta)
    except: 
        return

def metaTV(imdb=None, tmdb=None, tvdb=None):
    try:
        if imdb != None: 
            type = 'imdb'
            id = imdb
        elif tmdb != None:
            type = 'tmdb'
            id = tmdb    
        elif tvdb != None:
            type = 'tvdb'
            id = tvdb    
            
        conn = open_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tv WHERE %s = '%s'" % (type, id))
        row = cursor.fetchone()
        meta = {}
        for id in row.keys(): meta[id] = row[id]
        return meta
        print("[METALIBRARY] >>> ", meta)
    except:
        return
        
def playcountMeta(type, meta, action=None):
    DBFile = control.playcountDB
    if not os.path.exists(DBFile): file(DBFile, 'w').close()
    try:
        if type == 'movie':
            
            imdb = meta['imdb']
            tmdb = meta['tmdb']
            if imdb == '0': return
            dbcon = database.connect(DBFile)
            try:
                dbcur = dbcon.cursor()
                dbcur.execute("CREATE TABLE IF NOT EXISTS movies (""imdb TEXT, ""tmdb TEXT, ""playcount TEXT, ""UNIQUE(imdb, tmdb, playcount)"");")
            except:pass
            if action != None:
                print("INSERTING DB", imdb, tmdb, action)
                try:
                    dbcur.execute("DELETE FROM movies WHERE imdb = '%s'" % (imdb))
                    dbcur.execute("INSERT INTO movies Values (?, ?, ?)", (imdb, tmdb, str(action)))
                    dbcon.commit()
                except:
                    label = "[MOVIE][ERROR ADDING]"
                    print(label)
            else:
                dbcur.execute("SELECT * FROM movies WHERE imdb = '%s'" % (imdb))
                match = dbcur.fetchone()
                playcount = str(match[2])
                if match is None: return '6'
                else:return playcount

            
        if type == 'tv':
            
            imdb = meta['imdb']
            tvdb = meta['tvdb']
            if tvdb == '0': return
            dbcon = database.connect(DBFile)
            try:
                dbcur = dbcon.cursor()
                dbcur.execute("CREATE TABLE IF NOT EXISTS tv (""imdb TEXT, ""tvdb TEXT, ""playcount TEXT, ""UNIQUE(imdb, tvdb, playcount)"");")
            except:pass
            
            if action != None:    
                try:
                    label = "[TVSHOW][ADDED]"
                    print(label)
                    dbcur.execute("DELETE FROM tv WHERE tvdb = '%s'" % (tvdb))
                    dbcur.execute("INSERT INTO tv Values (?, ?, ?)", (imdb, tvdb, str(action)))
                    dbcon.commit()
                except:
                    label = "[TVSHOW][ERROR ADDING]"
                    print(label)            
            else:

                dbcur.execute("SELECT * FROM tv WHERE tvdb = '%s'" % (tvdb))
                match = dbcur.fetchone()
                playcount = str(match[2])
                if match is None: return '6'
                else:
                    print("[TVSHOW][IN DATABASE]")
                    return playcount

            
        if type == 'episode':
            imdb = meta['imdb']            
            tvdb = meta['tvdb']
            season = meta['season']
            episode = meta['episode']
            if tvdb == '0': return
            dbcon = database.connect(DBFile)
            try:
                dbcur = dbcon.cursor()
                dbcur.execute("CREATE TABLE IF NOT EXISTS episodes (""imdb TEXT, ""tvdb TEXT,""season TEXT, ""episode TEXT, ""playcount TEXT, ""UNIQUE(imdb, tvdb, season, episode, playcount)"");")
            except:pass
            
            if action != None:    
                try:
                    label = "[EPISODE][ADDED]"
                    print(label)
                    dbcur.execute("DELETE FROM episodes WHERE tvdb = '%s' and season = '%s' and episode = '%s'" % (tvdb, season, episode))
                    dbcur.execute("INSERT INTO episodes Values (?, ?, ?, ?, ?)", (imdb, tvdb, season, episode, str(action)))
                    dbcon.commit()
                except:
                    label = "[EPISODE][ERROR ADDING]"
                    print(label)            
            else:

                dbcur.execute("SELECT * FROM episodes WHERE tvdb = '%s' and season = '%s' and episode = '%s'" % (tvdb, season, episode))
                match = dbcur.fetchone()
                playcount = str(match[4])
                if match is None: return '6'
                else:
                    print("[EPISODE][IN DATABASE]", playcount)
                    return playcount

    except:
        return '6'

        


