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
import os
import sys
import xbmc
import xbmcgui
import xbmcvfs
from xbmcaddon import Addon

### get addon info
__addon__           = Addon("script.artwork.downloader")
__addonname__       = __addon__.getAddonInfo( "name" )
__addonprofile__    = xbmcvfs.translatePath( __addon__.getAddonInfo('profile') )

class Viewer:
    # constants
    WINDOW = 10147
    CONTROL_LABEL = 1
    CONTROL_TEXTBOX = 5

    def __init__(self, *args, **kwargs):
        # activate the text viewer window
        xbmc.executebuiltin("ActivateWindow(%d)" % (self.WINDOW,))
        # get window
        self.window = xbmcgui.Window(self.WINDOW)
        # give window time to initialize
        xbmc.sleep(100)
        # set controls
        self.setControls()

    def setControls(self):
        #get header, text
        heading, text = self.getText()
        # set heading
        self.window.getControl(self.CONTROL_LABEL).setLabel("%s - %s" % (heading, __addonname__,))
        # set text
        self.window.getControl(self.CONTROL_TEXTBOX).setText(text)

    def getText(self):
        try:
            if sys.argv[ 1 ] == "downloadreport":
                return "Download report", self.readFile(os.path.join(__addonprofile__, "downloadreport.txt"))
        except Exception as e:
            xbmc.log(__addonname__ + ': ' + str(e), xbmc.LOGERROR)
        return "", ""

    def readFile(self, filename):
        return open(filename).read()

class WebBrowser:
    """ Display url using the default browser. """

    def __init__(self, *args, **kwargs):
        try:
            url = sys.argv[2]
            # notify user
            notification(__addonname__, url)
            xbmc.sleep(100)
            # launch url
            self.launchUrl(url)
        except Exception as e:
            xbmc.log(__addonname__ + ': ' + str(e), xbmc.LOGERROR)

    def launchUrl(self, url):
        import webbrowser
        webbrowser.open(url)

def Main():
    try:
        if sys.argv[ 1 ] == "webbrowser":
            WebBrowser()
        else:
            Viewer()
    except Exception as e:
        xbmc.log(__addonname__ + ': ' + str(e), xbmc.LOGERROR)

if (__name__ == "__main__"):
    Main()
