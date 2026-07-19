# -*- coding: utf-8 -*-
import os
from modules import kodi_utils, settings


def pick_export_folder(heading='Choose export folder'):
	folder = kodi_utils.browse_directory(
		settings.import_export_directory_setting(),
		heading=heading,
		use_defaultt=True,
		confirm_unchanged=True,
		force_defaultt=True,
	)
	if not folder:
		return None
	return kodi_utils.translate_path(folder)


def offer_save_export_directory(folder):
	if not folder:
		return
	current = settings.import_export_directory_setting()
	if _same_folder(folder, current):
		return
	display = folder if len(folder) <= 120 else '%s...' % folder[:117]
	if not kodi_utils.confirm_dialog(
		heading='Default backup folder',
		text='Use this folder for future backups?[CR][CR][B]%s[/B]' % display,
		ok_label='Yes',
		cancel_label='No',
		default_control=11,
	):
		return
	from caches.settings_cache import set_setting
	set_setting('import_export_directory', folder)
	settings.ensure_import_export_directory()
	kodi_utils.notification('Default backup folder updated', 3500)


def _same_folder(a, b):
	if not a or not b:
		return False
	try:
		return os.path.normpath(kodi_utils.translate_path(a)) == os.path.normpath(kodi_utils.translate_path(b))
	except:
		return a == b


def meta_account_names(accounts):
	if not accounts:
		return ''
	names = []
	if accounts.get('trakt'): names.append('Trakt')
	if accounts.get('simkl'): names.append('Simkl')
	if accounts.get('mdblist'): names.append('MDBList')
	return ', '.join(names)


def settings_privacy_warning():
	return '[COLOR yellow]This file can contain API keys and account logins. Keep it private.[/COLOR]'


def settings_import_reminders(accounts=None):
	lines = [
		'After import, check:',
		'• Folder paths if you changed device or operating system',
		'• Your scraper package is installed',
	]
	meta = meta_account_names(accounts)
	if meta:
		lines.append('• Meta Accounts (%s) — re-authorise if sync fails' % meta)
	return '[CR]'.join(lines)
