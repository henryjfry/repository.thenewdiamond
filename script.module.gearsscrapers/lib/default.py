"""
	Fenomscrapers Module
"""

from sys import argv
from urllib.parse import parse_qsl
from gearsscrapers import providers
from gearsscrapers.modules import control

params = dict(parse_qsl(argv[2].replace('?', '')))
action = params.get('action')
name = params.get('name')

if action is None:
	control.openSettings('0.0', 'script.module.gearsscrapers')

if action == "gearsscrapersSettings":
	control.openSettings('0.0', 'script.module.gearsscrapers')

elif action == 'ShowChangelog':
	from gearsscrapers.modules import changelog
	changelog.get()

elif action == 'ShowHelp':
	from gearsscrapers.modules import help
	help.get(name)

elif action == "Defaults":
	from gearsscrapers import sources
	try:
		provider_defaults = control.getProviderDefaults()
		sourceList = []
		sourceList = sources(ret_all=True)
		for name, source in sourceList:
			source_setting = 'provider.' + name
			default_setting = provider_defaults.get(source_setting) or 'false'
			control.setSetting(source_setting, default_setting)
		control.notification(message='Success')
	except: control.notification(message='Error')

elif action == "toggleAll":
	sourceList = []
	sourceList = providers.all_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])

elif action == "toggleAllHosters":
	sourceList = []
	sourceList = providers.hoster_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])

elif action == "toggleAllTorrent":
	sourceList = []
	sourceList = providers.torrent_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])

elif action == "toggleAllPackTorrent":
	from gearsscrapers import sources
	sourceList = []
	sourceList = sources(ret_all=True)
	for name, source in sourceList:
		setting = 'true' if source.pack_capable else 'false'
		source_setting = 'provider.' + name
		control.setSetting(source_setting, setting)

elif action == 'cleanSettings':
	control.clean_settings()

elif action == 'undesirablesSelect':
	from gearsscrapers.modules.undesirables import undesirablesSelect
	undesirablesSelect()

elif action == 'undesirablesInput':
	from gearsscrapers.modules.undesirables import undesirablesInput
	undesirablesInput()

elif action == 'undesirablesUserRemove':
	from gearsscrapers.modules.undesirables import undesirablesUserRemove
	undesirablesUserRemove()

elif action == 'undesirablesUserRemoveAll':
	from gearsscrapers.modules.undesirables import undesirablesUserRemoveAll
	undesirablesUserRemoveAll()

elif action == 'tools_clearLogFile':
	from gearsscrapers.modules import log_utils
	cleared = log_utils.clear_logFile()
	if cleared == 'canceled': pass
	elif cleared: control.notification(message='gearsscrapers Log File Successfully Cleared')
	else: control.notification(message='Error clearing gearsscrapers Log File, see kodi.log for more info')

elif action == 'tools_viewLogFile':
	from gearsscrapers.modules import log_utils
	log_utils.view_LogFile(name)

elif action == 'tools_uploadLogFile':
	from gearsscrapers.modules import log_utils
	log_utils.upload_LogFile()

elif action == 'healthCheck':
	from gearsscrapers.modules.health import gearsscrapers
	gearsscrapers()