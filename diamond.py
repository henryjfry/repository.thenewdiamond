#!/usr/bin/python3


import os
os.chdir('/home/osmc/repository.thenewdiamond')

if os.path.exists('/home/osmc/.kodi/addons/script.extendedinfo/subcleaner/settings/logs/subcleaner.log'):
	os.remove('/home/osmc/.kodi/addons/script.extendedinfo/subcleaner/settings/logs/subcleaner.log') 

import prepare_zips
prepare_zips.prepare_zips()

import prepare_diamond
prepare_diamond.prepare_diamond()

import prepare_diamond
prepare_diamond.prepare_xtreme()

os.system('rm -r /home/osmc/repository.thenewdiamond/__pycache__')
os.system("cd /home/osmc/repository.thenewdiamond && /home/osmc/repository.thenewdiamond/_repo_xml_generator.py")
#import _repo_xml_generator
#_repo_xml_generator.repo()

