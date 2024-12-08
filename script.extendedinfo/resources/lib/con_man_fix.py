import os
import tempfile
import xbmcgui

CONNMAN_PATH = "/var/lib/connman"

def parse_network_name(directory):
	"""
	Parses the SSID or network name from a settings file in a Connman directory.
	"""
	settings_file = os.path.join(CONNMAN_PATH, directory, "settings")
	if not os.path.exists(settings_file):
		return None

	try:
		with open(settings_file, "r") as file:
			for line in file:
				if line.startswith("Name="):
					return line.strip().split("=", 1)[1]
	except Exception as e:
		xbmcgui.Dialog().notification("Error", f"Failed to read {settings_file}: {str(e)}", xbmcgui.NOTIFICATION_ERROR, 5000)
	return None

def write_and_run_script(commands, script_name="script.sh"):
	"""
	Writes the given commands to a temporary script and executes it with sudo.
	"""
	try:
		with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".sh") as script_file:
			script_file.write("#!/bin/bash\n")
			script_file.writelines(commands)
			script_path = script_file.name

		os.system(f"chmod +x {script_path}")
		os.system(f"sudo {script_path}")
		xbmcgui.Dialog().notification("Success", f"{script_name} executed", xbmcgui.NOTIFICATION_INFO, 3000)
	except Exception as e:
		xbmcgui.Dialog().notification("Error", str(e), xbmcgui.NOTIFICATION_ERROR, 5000)
	finally:
		if os.path.exists(script_path):
			os.remove(script_path)

def delete_all_connections():
	"""
	Deletes all connection files in /var/lib/connman by generating a script and running it with sudo.
	"""
	if os.path.exists(CONNMAN_PATH):
		commands = []
		for item in os.listdir(CONNMAN_PATH):
			item_path = os.path.join(CONNMAN_PATH, item)
			if os.path.isdir(item_path):
				commands.append(f"rm -rf {item_path}\n")
		if commands:
			write_and_run_script(commands, "delete_all_connections.sh")
		else:
			xbmcgui.Dialog().notification("Connman", "No connections to delete!", xbmcgui.NOTIFICATION_WARNING, 3000)
	else:
		xbmcgui.Dialog().notification("Connman", "Path does not exist!", xbmcgui.NOTIFICATION_WARNING, 3000)

def list_and_select_wifi():
	"""
	Lists Wi-Fi networks (by SSID or name) and allows user to select one for connection.
	"""
	wifi_dirs = [d for d in os.listdir(CONNMAN_PATH) if os.path.isdir(os.path.join(CONNMAN_PATH, d))]
	wifi_list = [(parse_network_name(d) or d, d) for d in wifi_dirs]
	wifi_list = [w for w in wifi_list if w[0]]  # Filter out networks with no name

	if not wifi_list:
		xbmcgui.Dialog().notification("Wi-Fi", "No networks found!", xbmcgui.NOTIFICATION_WARNING, 3000)
		return

	ssid_list = [w[0] for w in wifi_list]
	selected = xbmcgui.Dialog().select("Select Wi-Fi Network", ssid_list)
	if selected == -1:
		return  # User cancelled the selection

	selected_wifi = wifi_list[selected][1]
	xbmcgui.Dialog().notification("Wi-Fi", f"Selected: {ssid_list[selected]}", xbmcgui.NOTIFICATION_INFO, 3000)
	# You can add connection logic here

def mark_favorite_wifi():
	"""
	Allows the user to mark one Wi-Fi as favorite by SSID, setting others to Favorite=false via a script.
	"""
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
	commands = []

	for ssid, wifi_dir in wifi_list:
		settings_file = os.path.join(CONNMAN_PATH, wifi_dir, "settings")
		if os.path.exists(settings_file):
			commands.append(f"sed -i '/^Favorite=/c\\Favorite={'true' if wifi_dir == selected_wifi_dir else 'false'}' {settings_file}\n")
	
	if commands:
		write_and_run_script(commands, "mark_favorite_wifi.sh")
	else:
		xbmcgui.Dialog().notification("Wi-Fi", "No settings files to update!", xbmcgui.NOTIFICATION_WARNING, 3000)
