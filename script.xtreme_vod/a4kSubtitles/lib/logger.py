# -*- coding: utf-8 -*-
import os
from .kodi import xbmc, addon_id, get_kodi_setting

__get_debug_logenabled_err = False
def __get_debug_logenabled():
	global __get_debug_logenabled_err
	if __get_debug_logenabled_err:
		return False

	try:
		#return get_kodi_setting("debug.showloginfo", log_error=False)
		return False
	except:
		__get_debug_logenabled_err = True

	return False

try:
	notice_type = xbmc.LOGNOTICE
except:
	notice_type = xbmc.LOGINFO

def __log(message, level):
	if level == notice_type and not __get_debug_logenabled():
		return

	is_lazy_msg = callable(message)
	if is_lazy_msg:
		message = message()

	try:
		if os.environ['sub_logs'] != 'False':
			xbmc.log('{0}: {1}'.format(addon_id, message), level)
	except:
		xbmc.log('{0}: {1}'.format(addon_id, message), level)

try:
	notice_type = xbmc.LOGNOTICE
except:
	notice_type = xbmc.LOGINFO

def notice(message):
	__log(message, notice_type)

def error(message):
	__log(message, xbmc.LOGERROR)

def debug(message):
	__log(message, notice_type)
