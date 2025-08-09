import sys


from a4kscrapers_wrapper.kodi_stubs import xbmcaddon as xbmcaddon
from a4kscrapers_wrapper.kodi_stubs import xbmcgui as xbmcgui
from a4kscrapers_wrapper.kodi_stubs import xbmcvfs as xbmcvfs
from a4kscrapers_wrapper.kodi_stubs import xbmcplugin as xbmcplugin
from a4kscrapers_wrapper.kodi_stubs import xbmcdrm as xbmcdrm

import sys
import types
import os
import tempfile

# --- xbmc ---
xbmc = types.ModuleType("xbmc")
xbmc.LOGDEBUG = 0
xbmc.LOGINFO = 1
xbmc.LOGWARNING = 2
xbmc.LOGERROR = 3
xbmc.LOGFATAL = 4
xbmc.LOGNONE = 5

xbmc.log = lambda msg, level=xbmc.LOGDEBUG: print(f"[xbmc log - level {level}]: {msg}")
xbmc.getInfoLabel = lambda label: f"Mocked info for {label}"
xbmc.getCondVisibility = lambda cond: True
xbmc.getLanguage = lambda default=False, region=False: "en"
xbmc.getSkinDir = lambda: "default"
xbmc.getLocalizedString = lambda id: f"Localized string {id}"
xbmc.executebuiltin = lambda command, wait=False: print(f"[xbmc.executebuiltin] {command} (wait={wait})")
xbmc.executeJSONRPC = lambda query: f"Mocked JSONRPC response for: {query}"
xbmc.getRegion = lambda key: "US"
xbmc.getUserAgent = lambda: "Kodi/20.0 (Linux; Android 9)"
xbmc.sleep = lambda ms: print(f"[xbmc.sleep] Sleeping for {ms}ms")
xbmc.getProperty = lambda key: f"Mocked property for {key}"
xbmc.setProperty = lambda key, value: print(f"[xbmc.setProperty] {key} = {value}")

class Monitor:
	def waitForAbort(self, timeout=0): return False
	def abortRequested(self): return False
xbmc.Monitor = Monitor



# Inject into sys.modules
sys.modules["xbmc"] = xbmc
sys.modules["xbmcaddon"] = xbmcaddon
sys.modules["xbmcgui"] = xbmcgui
sys.modules["xbmcvfs"] = xbmcvfs
sys.modules["xbmcplugin"] = xbmcplugin
sys.modules["xbmcdrm"] = xbmcdrm
