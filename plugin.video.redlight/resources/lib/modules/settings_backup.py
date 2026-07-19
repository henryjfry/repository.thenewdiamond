# -*- coding: utf-8 -*-
import json
import os
import shutil
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
from caches.base_cache import database_locations, locations, make_database
from modules import kodi_utils, settings
from modules.import_export_utils import offer_save_export_directory, pick_export_folder, settings_privacy_warning, settings_import_reminders

SETTINGS_BACKUP_FORMAT = 1
SETTINGS_BACKUP_MASK = '.zip'
BACKUP_DATABASES = ('settings_db', 'navigator_db', 'personal_lists_db', 'discover_db', 'episode_groups_db')


def export_settings(params):
	inventory = _local_inventory()
	if not inventory['databases'] and not inventory['images']:
		return kodi_utils.ok_dialog(heading='Export settings', text='Nothing to export on this device.')
	folder = pick_export_folder(heading='Choose export folder')
	if not folder:
		return
	filename = 'redlight-settings-%s.zip' % datetime.now().strftime('%Y%m%d-%H%M%S')
	path = os.path.join(folder, filename)
	preview = _export_preview_text(filename, inventory)
	if not kodi_utils.confirm_dialog(heading='Export settings', text=preview, ok_label='Export', cancel_label='Cancel', default_control=10, scroll=True):
		return
	try:
		kodi_utils.make_directory(folder)
		_write_settings_zip(path, inventory)
	except Exception as e:
		return kodi_utils.ok_dialog(heading='Export failed', text=str(e))
	summary = 'Settings exported to %s' % filename
	kodi_utils.ok_dialog(heading='Export complete', text=summary, scroll=True)
	kodi_utils.notification(summary, 6500)
	offer_save_export_directory(folder)


def import_settings(params):
	path = _pick_import_zip(settings.import_export_directory_setting())
	if not path:
		return
	try:
		with ZipFile(path, 'r') as archive:
			manifest = _read_manifest(archive)
			inventory = _zip_inventory(archive, manifest)
	except Exception as e:
		return kodi_utils.ok_dialog(heading='Import failed', text='Could not read that file.[CR][CR]%s' % e)
	if not inventory['databases']:
		return kodi_utils.ok_dialog(heading='Import settings', text='That zip does not contain Red Light settings.')
	confirm = _import_confirm_text(path, manifest, inventory)
	if not kodi_utils.confirm_dialog(heading='Import settings', text=confirm, ok_label='Import', cancel_label='Cancel', default_control=10, scroll=True):
		return
	try:
		summary = _apply_settings_import(path, inventory)
	except Exception as e:
		return kodi_utils.ok_dialog(heading='Import failed', text=str(e))
	kodi_utils.ok_dialog(heading='Import complete', text=summary, scroll=True)
	kodi_utils.notification('Settings imported', 6500)
	kodi_utils.kodi_refresh()


def _addon_version():
	try:
		return kodi_utils.addon_info('version') or ''
	except:
		return ''


def _pick_import_zip(default_dir):
	path = kodi_utils.browse_file(SETTINGS_BACKUP_MASK, default_dir, heading='Choose settings backup', force_defaultt=True)
	if not path:
		return None
	tpath = kodi_utils.translate_path(path)
	if not os.path.isfile(tpath):
		return None
	if not tpath.lower().endswith('.zip'):
		kodi_utils.ok_dialog(heading='Import settings', text='Please choose a Red Light settings backup (.zip).')
		return None
	return tpath


def _local_inventory():
	profile = kodi_utils.translate_path(kodi_utils.addon_profile())
	databases = []
	for db_key in BACKUP_DATABASES:
		src = database_locations(db_key)
		if os.path.isfile(src):
			databases.append({'key': db_key, 'filename': locations()[db_key], 'size': os.path.getsize(src)})
	images_path = os.path.join(profile, 'images')
	image_files = 0
	if os.path.isdir(images_path):
		for _root, _dirs, files in os.walk(images_path):
			image_files += len(files)
	return {
		'databases': databases,
		'images': image_files,
		'accounts': _detect_accounts(),
	}


def _detect_accounts():
	return {
		'trakt': settings.trakt_user_active(),
		'simkl': settings.simkl_user_active(),
		'mdblist': settings.mdblist_user_active(),
	}


def _build_manifest(inventory):
	return {
		'format': SETTINGS_BACKUP_FORMAT,
		'type': 'redlight_settings',
		'addon_version': _addon_version(),
		'exported': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
		'databases': [i['filename'] for i in inventory['databases']],
		'image_files': inventory['images'],
		'accounts': inventory['accounts'],
	}


def _write_settings_zip(dest_path, inventory):
	profile = kodi_utils.translate_path(kodi_utils.addon_profile())
	manifest = _build_manifest(inventory)
	with ZipFile(dest_path, 'w', ZIP_DEFLATED) as archive:
		archive.writestr('manifest.json', json.dumps(manifest, indent=2, ensure_ascii=False))
		for item in inventory['databases']:
			src = database_locations(item['key'])
			archive.write(src, 'databases/%s' % item['filename'])
		images_path = os.path.join(profile, 'images')
		if inventory['images'] and os.path.isdir(images_path):
			for root, _dirs, files in os.walk(images_path):
				for filename in files:
					full = os.path.join(root, filename)
					rel = os.path.relpath(full, profile).replace('\\', '/')
					archive.write(full, rel)


def _read_manifest(archive):
	try:
		data = archive.read('manifest.json').decode('utf-8')
		manifest = json.loads(data)
	except Exception as e:
		raise ValueError('Invalid or missing manifest.json (%s)' % e)
	if manifest.get('type') != 'redlight_settings':
		raise ValueError('This zip is not a Red Light settings backup.')
	if int(manifest.get('format', 0)) != SETTINGS_BACKUP_FORMAT:
		raise ValueError('Unsupported backup format (%s).' % manifest.get('format'))
	return manifest


def _zip_inventory(archive, manifest):
	db_names = set(manifest.get('databases') or [])
	databases = []
	for name in archive.namelist():
		if not name.startswith('databases/') or name.endswith('/'):
			continue
		filename = name.split('/', 1)[1]
		if filename in db_names or not db_names:
			info = archive.getinfo(name)
			databases.append({'filename': filename, 'arcname': name, 'size': info.file_size})
	image_files = sum(1 for name in archive.namelist() if name.startswith('images/') and not name.endswith('/'))
	return {'databases': databases, 'images': image_files, 'accounts': manifest.get('accounts') or {}}


def _export_preview_text(filename, inventory):
	lines = [
		'[B]%s[/B]' % filename,
		'Settings, menus, lists, and preferences from this device.',
	]
	if inventory['images']:
		lines.append('%s custom list image(s).' % inventory['images'])
	lines.extend(['', settings_privacy_warning()])
	return '[CR]'.join(lines)


def _import_confirm_text(path, manifest, inventory):
	lines = [
		'[B]%s[/B]' % os.path.basename(path),
		'From Red Light %s (%s)' % (manifest.get('addon_version') or 'unknown', (manifest.get('exported') or 'unknown')[:10]),
		'',
		'This replaces your current Red Light settings, menus, and lists.',
		'Favorites and watch history are not changed.',
	]
	if inventory['images']:
		lines.append('%s custom list image(s) will be restored.' % inventory['images'])
	lines.extend(['', settings_import_reminders(inventory.get('accounts')), '', settings_privacy_warning()])
	return '[CR]'.join(lines)


def _apply_settings_import(zip_path, inventory):
	profile = kodi_utils.translate_path(kodi_utils.addon_profile())
	temp_dir = os.path.join(kodi_utils.translate_path('special://temp'), 'redlight_settings_import')
	if os.path.isdir(temp_dir):
		shutil.rmtree(temp_dir, ignore_errors=True)
	os.makedirs(temp_dir)
	try:
		with ZipFile(zip_path, 'r') as archive:
			archive.extractall(temp_dir)
		copied_dbs = []
		imported_db_keys = []
		for item in inventory['databases']:
			src = os.path.join(temp_dir, item['arcname'].replace('/', os.sep))
			if not os.path.isfile(src):
				continue
			db_key = _db_key_for_filename(item['filename'])
			if not db_key:
				continue
			dest = database_locations(db_key)
			kodi_utils.make_directory(os.path.dirname(dest))
			if os.path.isfile(dest):
				kodi_utils.delete_file(dest)
			shutil.copy2(src, dest)
			make_database(db_key)
			copied_dbs.append(item['filename'])
			imported_db_keys.append(db_key)
		copied_images = _import_images(os.path.join(temp_dir, 'images'), os.path.join(profile, 'images'))
		_reload_settings(imported_db_keys)
		from caches.base_cache import check_databases_integrity
		check_databases_integrity(silent=True)
	finally:
		shutil.rmtree(temp_dir, ignore_errors=True)
	parts = []
	if copied_dbs:
		parts.append('%s database(s) restored' % len(copied_dbs))
	if copied_images:
		parts.append('%s image(s) restored' % copied_images)
	reminders = settings_import_reminders(inventory.get('accounts'))
	if parts:
		return 'Import complete — %s.[CR][CR]%s' % ('; '.join(parts), reminders)
	return 'Import complete.[CR][CR]%s' % reminders


def _db_key_for_filename(filename):
	for db_key in BACKUP_DATABASES:
		if locations()[db_key] == filename:
			return db_key
	return None


def _import_images(src_root, dest_root):
	if not os.path.isdir(src_root):
		return 0
	count = 0
	for root, _dirs, files in os.walk(src_root):
		for filename in files:
			src = os.path.join(root, filename)
			rel = os.path.relpath(src, src_root)
			dest = os.path.join(dest_root, rel)
			kodi_utils.make_directory(os.path.dirname(dest))
			shutil.copy2(src, dest)
			count += 1
	return count


def _reload_settings(imported_db_keys=()):
	try:
		from caches.settings_cache import reload_after_settings_restore
		reload_after_settings_restore(imported_db_keys)
	except Exception as e:
		kodi_utils.logger('settings_import', str(e))
