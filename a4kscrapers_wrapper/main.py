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
	'check downloader status				"main.py -downloader -status"': 4,
	'Setup Providers					"main.py -providers_setup"': 5,
	'enable_disable_providers				"main.py -providers_enable"': 6,
	#'setup_userdata_folder': 7,
	'rd_auth						"main.py -rd_auth"': 8,
	'auto_clean_caches (7 days)				"main.py -auto_clean -days 7"': 9,
	'default settings.xml					"main.py -default_settings"': 10,
	'setup filters/limits/sorting			"main.py -setup_settings"': 11,
	'get current filters/limits/sorting 			"main.py -curr_settings"': 12
}

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

	if result == 3:
		magnet_list = tools.get_setting('magnet_list')
		download_path = tools.get_setting('download_path')
		getSources.run_downloader(magnet_list, download_path)

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


if __name__ == "__main__":
	print(sys.argv)
	main()