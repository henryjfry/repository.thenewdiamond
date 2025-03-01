#!/usr/bin/env python3
import os
import shutil
import time

source_file = "/home/osmc/EXTENDEDINFO_settings.xml"
destination_file = "/home/osmc/.kodi/userdata/addon_data/script.extendedinfo/settings.xml"

def copy_if_not_exist(source, destination):
	if not os.path.exists(destination):
		if not os.path.exists(source_file):
			return
		else:
			shutil.copy2(source, destination)
			#print("File copied successfully.")


if __name__ == "__main__":
	x = 0 
	while x < 120:
		copy_if_not_exist(source_file, destination_file)
		time.sleep(2)
		x = x + 2
