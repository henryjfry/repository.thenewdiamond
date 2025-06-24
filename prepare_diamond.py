#!/usr/bin/python3
import os
import shutil
from pathlib import Path
import fileinput

def remove(path):
	""" param <path> could either be relative or absolute. """
	if os.path.isfile(path) or os.path.islink(path):
		os.remove(path)  # remove the file
	elif os.path.isdir(path):
		shutil.rmtree(path)  # remove dir and all contains
	else:
		raise ValueError("file {} is not a file or dir.".format(path))

def search_replace(old_addonID, addon_ID, update_files):
	for fi in update_files:
		filename = Path(fi)
		print(str(old_addonID)+'= REPLACE OLD ADDONID - '+ fi + ', ' + str(addon_ID) + ' = NEW ADDONID -- DIAMONDINFO_MOD')
		with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
			for line in file:
				if 'settings.xml' in fi:
					if not '(Diamond)' in str(line):
						print(line.replace(old_addonID, str(addon_ID)), end='')
				else:
					print(line.replace(old_addonID, str(addon_ID)), end='')

def prepare_xtreme():
	xtreme_dest = '/home/osmc/repository.thenewdiamond/script.xtreme_vod/'
	if os.path.exists(xtreme_dest):
		remove(xtreme_dest)
	xtreme_source = '/home/osmc/.kodi/addons/script.xtreme_vod/'
	remove_pycache = []
	for i in os.walk(xtreme_source):
		for j in i[1]:
			if j == '__pycache__':
				pycache_path = i[0] + '/' + j
				remove_pycache.append(pycache_path)
	for i in remove_pycache:
		print('remove', i)
		remove(i)
		
	repo_source = '/home/osmc/repository.thenewdiamond/'
	shutil.copytree(xtreme_source, xtreme_dest)
	os.remove(xtreme_dest + 'addon.xml') 

	# Using readlines()
	file1 = open(xtreme_source + 'addon.xml', 'r')
	Lines = file1.readlines()

	output_lines = ''
	for line in Lines:
		if '<addon id="' in str(line):
			print("%.2f" % (round(float(line.split('version="')[1].split('" provider')[0])+0.01,2)))
			new_line = line.replace(line.split('version="')[1].split('" provider')[0], "%.2f" % round(float(line.split('version="')[1].split('" provider')[0])+0.01,2))
		else:
			new_line = line
		output_lines = output_lines + str(new_line)

	outF = open(xtreme_dest + 'addon.xml', "w")
	outF.write(output_lines)
	outF.close()
	shutil.copyfile(xtreme_dest + 'addon.xml', xtreme_source + 'addon.xml')

def prepare_diamond():
	diamond_dest = '/home/osmc/repository.thenewdiamond/script.diamondinfo/'
	extended_dest = '/home/osmc/repository.thenewdiamond/script.extendedinfo/'
	if os.path.exists(diamond_dest):
		remove(diamond_dest)
	if os.path.exists(extended_dest):
		remove(extended_dest)

	diamond_source = '/home/osmc/.kodi/addons/script.extendedinfo/'

	remove_pycache = []
	for i in os.walk(diamond_source):
		for j in i[1]:
			if j == '__pycache__':
				pycache_path = i[0] + '/' + j
				remove_pycache.append(pycache_path)

	for i in remove_pycache:
		print('remove', i)
		remove(i)
		
	repo_source = '/home/osmc/repository.thenewdiamond/'

	remove_pycache = []
	for i in os.walk(diamond_source):
		for j in i[1]:
			if j == '__pycache__':
				pycache_path = i[0] + '/' + j
				remove_pycache.append(pycache_path)

	for i in remove_pycache:
		print('remove', i)
		remove(i)

	shutil.copytree(diamond_source, diamond_dest)



	os.remove(diamond_dest + 'addon.xml') 

	# Using readlines()
	file1 = open(diamond_dest + 'addon.xml.DIAMONDINFO', 'r')
	Lines = file1.readlines()
	"""
	output_lines = ''
	for line in Lines:
		if '<addon id="' in str(line):
			x = 0
			for i in line.split('"'):
				if x == 0:
					new_line = i
				if x > 0:
					if line.split('"')[x-1] == ' version=':
						version_number = round(float(i) + 0.01,2)
						print('addon.xml.EXTENDEDINFO', version_number)
						new_line += str(version_number)
					else:
						new_line += i
				new_line += '"'
				x = x + 1
			output_lines += new_line
		else:
			output_lines += line
	"""
	output_lines = ''
	for line in Lines:
		if '<addon id="' in str(line):
			print("%.2f" % (round(float(line.split('version="')[1].split('" provider')[0])+0.01,2)))
			new_line = line.replace(line.split('version="')[1].split('" provider')[0], "%.2f" % round(float(line.split('version="')[1].split('" provider')[0])+0.01,2))
		else:
			new_line = line
		output_lines = output_lines + str(new_line)

	outF = open(diamond_dest + 'addon.xml', "w")
	outF.write(output_lines)
	outF.close()

	shutil.copyfile(diamond_dest + 'addon.xml', diamond_source + 'addon.xml.DIAMONDINFO')


	shutil.copytree(diamond_source, extended_dest)

	os.remove(extended_dest + 'addon.xml') 

	# Using readlines()
	file1 = open(extended_dest + 'addon.xml.EXTENDEDINFO', 'r')
	Lines = file1.readlines()
	"""
	output_lines = ''
	for line in Lines:
		if '<addon id="' in str(line):
			x = 0
			for i in line.split('"'):
				if x == 0:
					new_line = i
				if x > 0:
					if line.split('"')[x-1] == ' version=':
						version_number = round(float(i) + 0.01,2)
						print('addon.xml.EXTENDEDINFO', version_number)
						new_line += str(version_number)
					else:
						new_line += i
				new_line += '"'
				x = x + 1
			output_lines += new_line
		else:
			output_lines += line
	"""
	output_lines = ''
	for line in Lines:
		if '<addon id="' in str(line):
			print("%.2f" % (round(float(line.split('version="')[1].split('" provider')[0])+0.01,2)))
			new_line = line.replace(line.split('version="')[1].split('" provider')[0], "%.2f" % round(float(line.split('version="')[1].split('" provider')[0])+0.01,2))
		else:
			new_line = line
		output_lines = output_lines + str(new_line)

	outF = open(extended_dest + 'addon.xml', "w")
	outF.write(output_lines)
	outF.close()

	shutil.copyfile(extended_dest + 'addon.xml', diamond_source + 'addon.xml.EXTENDEDINFO')

	os.remove(diamond_dest + 'addon.xml.DIAMONDINFO') 
	os.remove(diamond_dest + 'addon.xml.EXTENDEDINFO') 

	os.remove(extended_dest + 'addon.xml.DIAMONDINFO') 
	os.remove(extended_dest + 'addon.xml.EXTENDEDINFO') 

	update_files = []
	update_files.append(extended_dest + 'resources/settings.xml')
	update_files.append(extended_dest + 'README.md')
	update_files.append(extended_dest + 'readme.txt')
	update_files.append(extended_dest + 'direct.diamond_player.json')
	update_files.append(extended_dest + 'direct.diamond_player_torr_scrape.json')
	update_files.append(extended_dest + 'direct.diamond_player_bluray.json')
	update_files.append(extended_dest + 'direct.diamond_player_bluray2.json')
	old_addonID = 'script.diamondinfo'
	addon_ID = 'script.extendedinfo'
	search_replace(old_addonID, addon_ID, update_files)
	for i in update_files:
		os.remove(i + '.bak')
	
	update_files = []
	update_files.append(diamond_dest + 'resources/settings.xml')
	update_files.append(diamond_dest + 'README.md')
	update_files.append(diamond_dest + 'readme.txt')
	update_files.append(diamond_dest + 'direct.diamond_player.json')
	update_files.append(diamond_dest + 'direct.diamond_player_torr_scrape.json')
	update_files.append(diamond_dest + 'direct.diamond_player_bluray.json')
	update_files.append(diamond_dest + 'direct.diamond_player_bluray2.json')
	addon_ID = 'script.diamondinfo'
	old_addonID = 'script.extendedinfo'
	search_replace(old_addonID, addon_ID, update_files)
	for i in update_files:
		os.remove(i + '.bak')