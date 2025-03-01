import sys
import os
import shutil
from inspect import currentframe, getframeinfo
#tools.log(str(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)))

folder = str(os.path.split(str(getframeinfo(currentframe()).filename))[0])
current_directory = folder
sys.path.append(current_directory)
sys.path.append(current_directory.replace('a4kscrapers_wrapper',''))

try:
	import getSources
	import real_debrid
	import tools
	import source_tools
	import get_meta
	from get_meta import get_episode_meta
	from get_meta import get_movie_meta
	from getSources import Sources
except:
	from a4kscrapers_wrapper import getSources
	from a4kscrapers_wrapper import real_debrid
	from a4kscrapers_wrapper import tools
	from a4kscrapers_wrapper import source_tools
	from a4kscrapers_wrapper import get_meta
	from a4kscrapers_wrapper.get_meta import get_episode_meta
	from a4kscrapers_wrapper.get_meta import get_movie_meta
	from a4kscrapers_wrapper.getSources import Sources

import sys

rd_api = real_debrid.RealDebrid()


program_choices = {
	'Search Torrent (episode) 				"main.py -search \'foundation\' -episode 1 -season 2 -interactive False"': 1 ,
	'Search Torrent (movie)				"main.py -search \'batman begins\' -year 2005"': 2,
	'Start downloader service (if not running)		"main.py -downloader -start"': 3,
	'manage downloader list				"main.py -downloader -status"': 4,
	'Setup Providers					"main.py -providers_setup"': 5,
	'enable_disable_providers				"main.py -providers_enable"': 6,
	#'setup_userdata_folder': 7,
	'rd_auth						"main.py -rd_auth"': 8,
	'auto_clean_caches (7 days)				"main.py -auto_clean -days 7"': 9,
	'default settings.xml					"main.py -default_settings"': 10,
	'setup filters/limits/sorting			"main.py -setup_settings"': 11,
	'get current filters/limits/sorting 			"main.py -curr_settings"': 12,
	'Search Torrent (Keyword) 			""': 13,
	'Delete_Dupes 			""': 14,
	'Get Subtitles for File			""': 15
}

program_choices2 = {
	'Search Subtitles (episode) 				" "': 1 ,
	'Search Subtitles (movie)				" "': 2,
}

def downloader_daemon():
	from a4kscrapers_wrapper import daemon
	magnet_list = tools.get_setting('magnet_list')
	download_path = tools.get_setting('download_path')
	with daemon.DaemonContext():
		getSources.run_downloader(magnet_list, download_path)

def copy_and_replace(source_path, destination_path):
	if os.path.exists(destination_path):
		if source_path == destination_path:
			return
		os.remove(destination_path)
	shutil.copy2(source_path, destination_path)

def main():
	#program_choices = tools.program_choices
	try: result = tools.selectFromDict(program_choices, 'CHOOSE')
	except KeyboardInterrupt: 
		print('\nEXIT')
		return

	if result == 1:
		getSources.run_tv_search()

	if result == 2:
		getSources.run_movie_search()
	if result == 13:
		getSources.run_keyword_search()
	if result == 14:
		getSources.rd_delete_dupes()

	if result == 3:
		magnet_list = tools.get_setting('magnet_list')
		download_path = tools.get_setting('download_path')
		getSources.run_downloader(magnet_list, download_path)

	if result == 4:
		magnet_list = tools.get_setting('magnet_list')
		download_path = tools.get_setting('download_path')
		lines = tools.read_all_text(magnet_list).split('\n')
		for line in lines:
			try: new_line = eval(line)
			except: continue
			print('CURR_PACK=%s,          CURR_LINE=%s,        CURR_FILE=%s' % (new_line['download_type'], new_line['file_name'], new_line['release_title']))
		print('Process_Lines')
		print('\n')
		try: 
			append_line = input('Modify Downloads Y?\n')
		except: 
			print('\n')
			append_line = 'N'
		if append_line.lower()[:1] == 'y':
			except_flag = False
			file1 = open(magnet_list, "w")
			file1.write("\n")
			file1.close()
			for line in reversed(lines):
				if except_flag == False:
					try: new_line = eval(line)
					except: continue
					print('CURR_PACK=%s,          CURR_LINE=%s,        CURR_FILE=%s' % (new_line['download_type'], new_line['file_name'], new_line['release_title']))
					try: 
						append_line = input('Delete Line From File:  Y?\n')
						if append_line.lower()[:1] == 'y':
							continue
						else:
							file1 = open(magnet_list, "a") 
							file1.write(str(line))
							file1.write("\n")
							file1.close()
					except:
						except_flag = True
						file1 = open(magnet_list, "a") 
						file1.write(str(line))
						file1.write("\n")
						file1.close()
				else:
					print('EXCEPTION_EXIT\n')
					file1 = open(magnet_list, "a") 
					file1.write(str(line))
					file1.write("\n")
					file1.close()

	if result == 5:
		tools.setup_userdata()
		getSources.setup_providers('https://bit.ly/a4kScrapers')
	if result == 6:
		tools.setup_userdata()
		getSources.enable_disable_providers()
	elif result == 7:
		tools.setup_userdata()
	elif result == 8:
		tools.setup_userdata()
		getSources.rd_auth()
	elif result == 9:
		tools.auto_clean_cache(days=7)
	elif result == 10:
		tools.setup_userdata()
		info = get_meta.blank_meta()
		tools.SourceSorter(info).default_sort_methods()
	elif result == 11:
		info = get_meta.blank_meta()
		tools.SourceSorter(info).set_sort_method_settings()
	elif result == 12:
		info = get_meta.blank_meta()
		tools.SourceSorter(info).get_sort_methods()
	elif result == 15:
		import importlib
		try:
			from importlib import reload as reload_module  # pylint: disable=no-name-in-module
		except ImportError:
			# Invalid version of importlib
			from imp import reload as reload_module
		try: result2 = tools.selectFromDict(program_choices2, 'CHOOSE')
		except KeyboardInterrupt: 
			print('\nEXIT')
			return
		if result2 == 1:
			tv_show_title = input('Enter TV Show Title:  ')

			season_number = input('Enter Season Number:  ')
			episode_number = input('Enter Episode Number:  ')
			meta = get_meta.get_episode_meta(season=season_number, episode=episode_number,tmdb=None, show_name=tv_show_title, year=None, interactive=True)
			info = meta['episode_meta']
			meta = info
			meta['air_date'] = meta['episode_air_date']
			meta['originaltitle'] = meta['title']
			meta['name'] = meta['title']
			print(meta)

		else:
			movie_title = input('Enter Movie Title:  ')
			movie_title = movie_title.replace('.',' ')
			meta = get_meta.get_movie_meta(movie_name=movie_title,year=None, interactive=True)
			info = meta
		
		file_path = input('Enter file path for source file MP4:  ').strip()
		source_dir = os.path.dirname(file_path)
		if file_path[:4] == 'http':
			source_dir = os.path.join(tools.ADDON_USERDATA_PATH, 'temp')
		print(source_dir)
		print(file_path)
		
		try: subs = importlib.import_module("subs")
		except: subs = reload_module(importlib.import_module("subs"))
		subs.META = meta
		meta = subs.set_size_and_hash_url(meta, file_path)
		subs_list = subs.get_subtitles_list(meta, file_path)
		del subs
		#exit()
		if len(subs_list) > 0:
			from subcleaner import clean_file
			from pathlib import Path
			for i in subs_list:
				sub = Path(i)
				clean_file.clean_file(sub)
				dest_file = os.path.join(source_dir, os.path.basename(i))
				copy_and_replace(i, dest_file)
			tools.sub_cleaner_log_clean()
			clean_file.files_handled = []


if __name__ == "__main__":
	print(sys.argv)
	if 'downloader' in str(sys.argv):
		downloader_daemon()
	else:
		main()
