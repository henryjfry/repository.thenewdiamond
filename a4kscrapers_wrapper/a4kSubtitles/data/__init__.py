# -*- coding: utf-8 -*-

import importlib
try:
	from a4kSubtitles.lib import utils, kodi
	prefix = 'a4kSubtitles'
except:
	from a4kscrapers_wrapper.a4kSubtitles.lib import utils, kodi
	prefix = 'a4kscrapers_wrapper.a4kSubtitles'

kodi.xbmcvfs.mkdirs(utils.data_dir)
__all = utils.get_all_relative_entries(__file__, ext='')

data = {}
for service_name in __all:
    data[service_name] = importlib.import_module('%s.data.%s' % (prefix, service_name))
