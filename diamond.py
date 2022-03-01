#!/usr/bin/python3

import os
os.chdir('/home/osmc/repository.thenewdiamond')

import prepare_zips
prepare_zips.prepare_zips()

import prepare_diamond
prepare_diamond.prepare_diamond()

os.system('rm -r /home/osmc/repository.thenewdiamond/__pycache__')
os.system("cd /home/osmc/repository.thenewdiamond && /home/osmc/repository.thenewdiamond/_repo_xml_generator.py")
#import _repo_xml_generator
#_repo_xml_generator.repo()

