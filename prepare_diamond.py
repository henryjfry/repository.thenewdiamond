#!/usr/bin/python3
import os
import shutil

def remove(path):
	""" param <path> could either be relative or absolute. """
	if os.path.isfile(path) or os.path.islink(path):
		os.remove(path)  # remove the file
	elif os.path.isdir(path):
		shutil.rmtree(path)  # remove dir and all contains
	else:
		raise ValueError("file {} is not a file or dir.".format(path))

def prepare_diamond():
	diamond_dest = '/home/osmc/repository.thenewdiamond/script.diamondinfo/'
	extended_dest = '/home/osmc/repository.thenewdiamond/script.extendedinfo/'
	if os.path.exists(diamond_dest):
		remove(diamond_dest)
	if os.path.exists(extended_dest):
		remove(extended_dest)

	diamond_source = '/home/osmc/.kodi/addons/script.diamondinfo/'

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
						print('addon.xml.DIAMONDINFO', version_number)
						new_line += str(version_number)
					else:
						new_line += i
				new_line += '"'
				x = x + 1
			output_lines += new_line
		else:
			output_lines += line

	outF = open(diamond_dest + 'addon.xml', "w")
	outF.write(output_lines)
	outF.close()

	shutil.copyfile(diamond_dest + 'addon.xml', diamond_source + 'addon.xml.DIAMONDINFO')


	shutil.copytree(diamond_source, extended_dest)

	os.remove(extended_dest + 'addon.xml') 

	# Using readlines()
	file1 = open(extended_dest + 'addon.xml.EXTENDEDINFO', 'r')
	Lines = file1.readlines()
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

	outF = open(extended_dest + 'addon.xml', "w")
	outF.write(output_lines)
	outF.close()

	shutil.copyfile(extended_dest + 'addon.xml', diamond_source + 'addon.xml.EXTENDEDINFO')

	os.remove(diamond_dest + 'addon.xml.DIAMONDINFO') 
	os.remove(diamond_dest + 'addon.xml.EXTENDEDINFO') 

	os.remove(extended_dest + 'addon.xml.DIAMONDINFO') 
	os.remove(extended_dest + 'addon.xml.EXTENDEDINFO') 


