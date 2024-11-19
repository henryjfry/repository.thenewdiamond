# -*- coding: utf-8 -*-
#from resources.lib.modules.globals import g

subtitles_exts = ['.srt', '.sub']
subtitles_exts_secondary = ['.smi', '.ssa', '.aqt', '.jss', '.ass', '.rt']
subtitles_exts_all = subtitles_exts + subtitles_exts_secondary

try:
	import tools
except:
	from a4kscrapers_wrapper import tools
import os
from inspect import currentframe, getframeinfo
#print(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

def __download(core, filepath, request):
	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	#tools.log(filepath)
	request['stream'] = True

	response = core.request.execute(core, request)
	if response.status_code >= 400:
		raise Exception('Failed to download subtitle (HTTP: %s)' % response.status_code)
	with response as r:
		with open(filepath, 'wb') as f:
			core.shutil.copyfileobj(r.raw, f)
	return filepath

def __extract_gzip(core, archivepath, filename):
	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	if not any(filename.lower().endswith(ext) for ext in subtitles_exts_all):
		# For now, we will use 'srt' to mark unknown file extensions as subtitles.
		filename = filename + ".srt"
	filepath = core.os.path.join(core.utils.temp_dir, filename)

	if core.utils.py2:
		#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		with open(archivepath, 'rb') as f:
			gzip_file = f.read()

		with core.gzip.GzipFile(fileobj=core.utils.StringIO(gzip_file)) as gzip:
			#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			with open(filepath, 'wb') as f:
				f.write(gzip.read())
				f.flush()
	else:
		#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		with core.gzip.open(archivepath, 'rb') as f_in:
			with open(filepath, 'wb') as f_out:
				core.shutil.copyfileobj(f_in, f_out)

	return filepath

def __extract_zip(core, archivepath, filename, episodeid):
	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	sub_exts = subtitles_exts
	sub_exts_secondary = subtitles_exts_secondary

	try:
		using_libvfs = False
		with open(archivepath, 'rb') as f:
			zipfile = core.zipfile.ZipFile(core.BytesIO(f.read()))
		namelist = core.utils.get_zipfile_namelist(zipfile)
	except:
		using_libvfs = True
		archivepath_ = core.utils.quote_plus(archivepath)
		(dirs, files) = core.kodi.xbmcvfs.listdir('archive://%s' % archivepath_)
		namelist = [file.decode(core.utils.default_encoding) if core.utils.py2 else file for file in files]

	#tools.log(namelist)
	#subfile = core.utils.find_file_in_archive(core, namelist, sub_exts, episodeid)
	#if not subfile:
	#	subfile = core.utils.find_file_in_archive(core, namelist, sub_exts_secondary, episodeid)
	subfile = core.utils.find_file_in_archive(core, namelist, sub_exts + sub_exts_secondary, episodeid)
	if subfile:
		# Add the subtitle file extension.
		subfilename_and_ext = subfile.rsplit(".", 1)
		if len(subfilename_and_ext) > 1:
			filename = filename + "." + subfilename_and_ext[-1]

	dest = core.os.path.join(core.utils.temp_dir, filename)
	if not subfile:
		try:
			return __extract_gzip(core, archivepath, filename)
		except:
			try: core.os.remove(dest)
			except: pass
			try: core.os.rename(archivepath, dest)
			except: pass
			return dest

	if not using_libvfs:
		src = core.utils.extract_zipfile_member(zipfile, subfile, core.utils.temp_dir)
		try: core.os.remove(dest)
		except: pass
		try: core.os.rename(src, dest)
		except: pass
	else:
		src = 'archive://' + archivepath_ + '/' + subfile
		core.kodi.xbmcvfs.copy(src, dest)

	return dest

def __insert_lang_code_in_filename(core, filename, lang_code):
	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	#filename_chunks = core.utils.strip_non_ascii_and_unprintable(filename).split('.')
	#filename_chunks.insert(-1, lang_code)
	#return '.'.join(filename_chunks)
	name = core.utils.strip_non_ascii_and_unprintable(filename)
	filename, file_extension = os.path.splitext(name)
	nameparts = name.rsplit(".", 1)
	# Because this can be called via "raw" subtitles where sub ext exists we will ensure it ends with the subtitle ext.
	# Otherwise we will use "filename.lang_code" later the ext will be added on unzip process.
	if len(nameparts) > 1 and ("." + nameparts[1] in subtitles_exts_all):
		file_path = ".".join([nameparts[0], lang_code, nameparts[1]])
	else:
		file_path = "{0}.{1}".format(name, lang_code)
	file_path = file_path.replace(file_extension,'')
	#tools.log(file_extension)
	#tools.log(file_path)
	return file_path

def __postprocess(core, filepath, lang_code):
	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	#tools.log(filepath)
	filename, file_extension = os.path.splitext(filepath)
	if not lang_code in file_extension:
		filepath = filepath.replace(file_extension+file_extension,file_extension)
	#tools.log(filepath)	
	try:
	#if 1==1:
		with open(filepath, 'rb', encoding=core.utils.default_encoding) as f:
			text_bytes = f.read()

		if core.kodi.get_bool_setting('general.use_chardet'):
			encoding = ''
			if core.utils.py3:
				detection = core.utils.chardet.detect(text_bytes)
				#detected_lang_code = core.kodi.xbmc.convertLanguage(detection['language'], core.kodi.xbmc.ISO_639_2)
				detected_lang_code = core.utils.get_lang_id(detection['language'], core.kodi.xbmc.ISO_639_2)
				if detection['confidence'] == 1.0 or detected_lang_code == lang_code:
					encoding = detection['encoding']

			if not encoding:
				encoding = core.utils.code_pages.get(lang_code, core.utils.default_encoding)

			text = text_bytes.decode(encoding)
		else:
			text = text_bytes.decode(core.utils.default_encoding)

		try:
			if all(ch in text for ch in core.utils.cp1251_garbled):
				text = text.encode(core.utils.base_encoding).decode('cp1251')
			elif all(ch in text for ch in core.utils.koi8r_garbled):
				try:
					text = text.encode(core.utils.base_encoding).decode('koi8-r')
				except:
					text = text.encode(core.utils.base_encoding).decode('koi8-u')
		except: pass

		try:
			clean_text = core.utils.cleanup_subtitles(core, text)
			if len(clean_text) > len(text) / 2:
				text = clean_text
		except: pass

		with open(filepath, 'wb') as f:
			f.write(text.encode(core.utils.default_encoding))
	except: pass

def __copy_sub_local(core, subfile):
	tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	# Copy the subfile to local.
	if core.os.getenv('A4KSUBTITLES_TESTRUN') == 'true':
		return
	media_name = core.os.path.splitext(core.os.path.basename(core.kodi.xbmc.getInfoLabel('Player.Filename')))[0]
	sub_name, lang_code, extension = core.os.path.basename(subfile).rsplit(".", 2)
	file_dest, folder_dest = None, None
	if core.kodi.get_kodi_setting("subtitles.storagemode") == 0:
		folder_dest = core.kodi.xbmc.getInfoLabel('Player.Folderpath')
		file_dest = core.os.path.join(folder_dest, ".".join([media_name, lang_code, extension]))
	elif core.kodi.get_kodi_setting("subtitles.storagemode") == 1:
		folder_dest = core.kodi.get_kodi_setting("subtitles.custompath")
		file_dest = core.os.path.join(folder_dest, ".".join([media_name, lang_code, extension]))
	if file_dest and core.kodi.xbmcvfs.exists(folder_dest):
		core.kodi.xbmcvfs.copy(subfile, file_dest)

def download(core, params):
	#core.logger.debug(lambda: core.json.dumps(params, indent=2))
	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

	try: new_VIDEO_META = core.utils.DictAsObject(params.get('VIDEO_META'))
	except: new_VIDEO_META = None
	if new_VIDEO_META:
		tools.VIDEO_META = new_VIDEO_META

	core.shutil.rmtree(core.utils.temp_dir, ignore_errors=True)
	if not os.path.exists(core.utils.temp_dir):
		os.mkdir(core.utils.temp_dir)
	#core.kodi.xbmcvfs.mkdirs(core.utils.temp_dir)

	actions_args = params['action_args']
	#lang_code = core.kodi.xbmc.convertLanguage(actions_args['lang'], core.kodi.xbmc.ISO_639_2)
	#filename = __insert_lang_code_in_filename(core, actions_args['filename'], lang_code)
	lang_code = core.utils.get_lang_id(actions_args['lang'], core.kodi.xbmc.ISO_639_2)
	#tools.log(lang_code)
	filename = __insert_lang_code_in_filename(core, tools.VIDEO_META['subs_filename'], lang_code)
	filename = core.utils.slugify_filename(filename)

	sub_ext = '.' + params['name'].split('.')[-1]
	sub_exts = ['.sub', '.smi', '.ssa', '.aqt', '.jss', '.ass', '.rt', '.txt']
	sub_ext_checked = None
	for i in sub_exts:
		if sub_ext == i:
			sub_ext_checked = i
			break

	filename.replace('.srt.srt','.srt')
	if sub_ext_checked:
		filename = filename.replace('.srt',sub_ext_checked)
	if actions_args.get('gzip', False):
		archivepath = core.os.path.join(core.utils.temp_dir, 'sub.gzip')
	else:
		archivepath = core.os.path.join(core.utils.temp_dir, 'sub.zip')

	service_name = params['service_name']
	service = core.services[service_name]
	request = service.build_download_request(core, service_name, actions_args)
	#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
	#tools.log(request)

	
	if actions_args.get('raw', False):
		#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		filepath = core.os.path.join(core.utils.temp_dir, filename)
		download_filepath = __download(core, filepath, request)
	else:
		#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
		download_filepath = __download(core, archivepath, request)
		
		if actions_args.get('gzip', False) or 'gzip' in download_filepath:
			tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			try: filepath = __extract_gzip(core, archivepath, filename)
			except Exception as e:
				if 'Not a gzipped file' in str(e):
					filepath = core.os.path.join(core.utils.temp_dir, filename + '.srt')
					return filepath
		else:
			#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))
			episodeid = actions_args.get('episodeid', '')
			#tools.log(actions_args)
			filepath = __extract_zip(core, archivepath, filename, episodeid)

	__postprocess(core, filepath, lang_code)

	tools.SUB_FILE = filepath
	if core.api_mode_enabled:
		return filepath

	listitem = core.kodi.xbmcgui.ListItem(label=filepath, offscreen=True)
	core.kodi.xbmcplugin.addDirectoryItem(handle=core.handle, url=filepath, listitem=listitem, isFolder=False)
