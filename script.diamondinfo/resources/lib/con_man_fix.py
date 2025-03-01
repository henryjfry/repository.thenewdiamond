import os
import tempfile
import xbmcgui
import xbmc
import subprocess


CONNMAN_PATH = "/var/lib/connman"

def parse_network_name(directory):
	"""
	Parses the SSID or network name from a settings file in a Connman directory.
	"""
	settings_file = os.path.join(CONNMAN_PATH, directory, "settings")
	#if not os.path.exists(settings_file):
	#	xbmc.log(str(settings_file)+'===>OPENINFO', level=xbmc.LOGFATAL)
	#	return None

	try:
		#with open(settings_file, "r") as file:
		#	for line in file:
		#		if line.startswith("Name="):
		#			return line.strip().split("=", 1)[1]
		output = subprocess.check_output(['sudo', 'cat', settings_file])
		try: ssid_name = str(output).split('\nName=')[1].split('\n')[0]
		except: ssid_name = str(output).split('\\nName=')[1].split('\\n')[0]
		if 'Favorite' in str(output):
			try: favourite = str(output).split('\=')[1].split('\n')[0]
			except: favourite = str(output).split('\\nFavorite=')[1].split('\\n')[0]
			if favourite == 'true':
				ssid_name = ssid_name + '*'
		#xbmc.log(str(ssid_name)+'===>OPENINFO', level=xbmc.LOGFATAL)
		return ssid_name
	except Exception as e:
		xbmcgui.Dialog().notification("Error", f"Failed to read {settings_file}: {str(e)}", xbmcgui.NOTIFICATION_ERROR, 5000)
	return None

def write_and_run_script(commands, script_name="script.sh"):
	"""
	Writes the given commands to a temporary script and executes it with sudo.
	"""
	#try:
	if 1==1:
		with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".sh") as script_file:
			script_file.write("#!/bin/bash\n")
			script_file.writelines(commands)
			script_path = script_file.name

		os.system(f"chmod +x {script_path}")
		os.system(f"sudo {script_path}")
		xbmc.log(str(commands)+'===>OPENINFO', level=xbmc.LOGFATAL)
		xbmc.log(str('sudo %s' % str(script_path))+'===>OPENINFO', level=xbmc.LOGFATAL)
		xbmcgui.Dialog().notification("Success", f"{script_name} executed", xbmcgui.NOTIFICATION_INFO, 3000)
	#except Exception as e:
	#	xbmcgui.Dialog().notification("Error", str(e), xbmcgui.NOTIFICATION_ERROR, 5000)
	#finally:
		if os.path.exists(script_path):
			os.remove(script_path)
		indexes2 = xbmcgui.Dialog().yesno('REBOOT?', 'REBOOT?', 'No', 'Yes') 
		if indexes2 != False:
			os.system('sudo reboot')

def delete_all_connections():
	"""
	Deletes all connection files in /var/lib/connman by generating a script and running it with sudo.
	"""
	if os.path.exists(CONNMAN_PATH):
		commands = []
		for item in os.listdir(CONNMAN_PATH):
			item_path = os.path.join(CONNMAN_PATH, item)
			if 'ethernet' in str(item_path):
				continue
			if os.path.isdir(item_path):
				commands.append(f"rm -rf {item_path}\n")
		if commands:
			write_and_run_script(commands, "delete_all_connections.sh")
		else:
			xbmcgui.Dialog().notification("Connman", "No connections to delete!", xbmcgui.NOTIFICATION_WARNING, 3000)
	else:
		xbmcgui.Dialog().notification("Connman", "Path does not exist!", xbmcgui.NOTIFICATION_WARNING, 3000)

def wifi_context(selected_wifi,wifi_list):
	actions_list = []
	actions_list.append('Delete Connection')
	actions_list.append('Mark Favourite Wifi (others not)')
	actions_list.append('Mark Favourite Wifi (TRUE)')
	actions_list.append('Mark Favourite Wifi (FALSE)')
	actions_list.append('Delete ALL Connections')
	selected = xbmcgui.Dialog().select("Wi-Fi Network Actions", actions_list)
	
	if selected == -1:
		return

	if actions_list[selected] == 'Delete Connection':
		delete_connection(selected = selected_wifi)
	elif actions_list[selected] == 'Mark Favourite Wifi (others not)':
		mark_favorite_wifi_others_not(wifi_list = wifi_list, selected = selected_wifi)
	elif actions_list[selected] == 'Mark Favourite Wifi (TRUE)':
		mark_favorite_wifi(selected_wifi_dir = selected_wifi, fav_true = True)
	elif actions_list[selected] == 'Mark Favourite Wifi (FALSE)':
		mark_favorite_wifi(selected_wifi_dir = selected_wifi, fav_true = False)
	elif actions_list[selected] == 'Delete ALL Connections':
		delete_all_connections()
	


def list_and_select_wifi():
	"""
	Lists Wi-Fi networks (by SSID or name) and allows user to select one for connection.
	"""
	wifi_dirs = [d for d in os.listdir(CONNMAN_PATH) if os.path.isdir(os.path.join(CONNMAN_PATH, d))]
	wifi_list = [(parse_network_name(d) or d, d) for d in wifi_dirs]
	wifi_list = [w for w in wifi_list if w[0]]  # Filter out networks with no name
	for i in reversed(wifi_list):
		#xbmc.log(str(i)+'===>OPENINFO', level=xbmc.LOGFATAL)
		if i[1][:4] != 'wifi':
			wifi_list.pop(wifi_list.index(i))

	if not wifi_list:
		xbmcgui.Dialog().notification("Wi-Fi", "No networks found!", xbmcgui.NOTIFICATION_WARNING, 3000)
		return

	ssid_list = [w[0] for w in wifi_list]
	selected = xbmcgui.Dialog().select("Select Wi-Fi Network", ssid_list)
	if selected == -1:
		return  # User cancelled the selection

	selected_wifi = wifi_list[selected][1]
	wifi_context(selected_wifi,wifi_list)
	
	#xbmcgui.Dialog().notification("Wi-Fi", f"Selected: {ssid_list[selected]}", xbmcgui.NOTIFICATION_INFO, 3000)

	# You can add connection logic here

def delete_connection(selected = None):
	item_path = os.path.join(CONNMAN_PATH, selected)
	commands = []
	if os.path.isdir(item_path):
		commands.append(f"rm -rf {item_path}\n")
	if commands:
		write_and_run_script(commands, "delete_all_connections.sh")

def mark_favorite_wifi(selected_wifi_dir = None, fav_true = True):
	settings_file = os.path.join(CONNMAN_PATH, selected_wifi_dir, "settings")
	commands = []
	if fav_true:
		commands.append(f"sed -i '/^Favorite=/c\\Favorite={'true'}' {settings_file}\n")
	else:
		commands.append(f"sed -i '/^Favorite=/c\\Favorite={'false'}' {settings_file}\n")
	if commands:
		write_and_run_script(commands, "mark_favorite_wifi.sh")

def mark_favorite_wifi_others_not(wifi_list = None, selected = None):
	"""
	Allows the user to mark one Wi-Fi as favorite by SSID, setting others to Favorite=false via a script.
	"""
	if wifi_list == None:
		wifi_dirs = [d for d in os.listdir(CONNMAN_PATH) if os.path.isdir(os.path.join(CONNMAN_PATH, d))]
		wifi_list = [(parse_network_name(d) or d, d) for d in wifi_dirs]
		wifi_list = [w for w in wifi_list if w[0]]  # Filter out networks with no name

		if not wifi_list:
			xbmcgui.Dialog().notification("Wi-Fi", "No networks found!", xbmcgui.NOTIFICATION_WARNING, 3000)
			return

		ssid_list = [w[0] for w in wifi_list]
		selected = xbmcgui.Dialog().select("Mark Favorite Wi-Fi", ssid_list)
		if selected == -1:
			return  # User cancelled the selection

		selected_wifi_dir = wifi_list[selected][1]
	else:
		selected_wifi_dir = selected
	commands = []

	for ssid, wifi_dir in wifi_list:
		settings_file = os.path.join(CONNMAN_PATH, wifi_dir, "settings")
		commands.append(f"sed -i '/^Favorite=/c\\Favorite={'true' if wifi_dir == selected_wifi_dir else 'false'}' {settings_file}\n")
	
	if commands:
		write_and_run_script(commands, "mark_favorite_wifi.sh")
	else:
		xbmcgui.Dialog().notification("Wi-Fi", "No settings files to update!", xbmcgui.NOTIFICATION_WARNING, 3000)
