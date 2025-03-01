#!/usr/bin/python3
import os

def prepare_zips():
	def remove(path):
		""" param <path> could either be relative or absolute. """
		if os.path.isfile(path) or os.path.islink(path):
			os.remove(path)  # remove the file
		elif os.path.isdir(path):
			shutil.rmtree(path)  # remove dir and all contains
		else:
			raise ValueError("file {} is not a file or dir.".format(path))

	main_path = '/home/osmc/repository.thenewdiamond/zips'
	addon_paths = []
	for i in os.listdir(main_path):
		addon_paths.append(i)

	remove_zips = []
	for i in addon_paths:
		path = main_path + '/' + i
		#print(path)
		files = sorted([os.path.join(root,f) for root,_,the_files in os.walk(path) for f in the_files if f.lower().endswith(".zip")], key=os.path.getctime, reverse = True)
		x = 0
		for j in files:
			if x > 0:
				remove_zips.append(j)
			x = x + 1

	for i in remove_zips:
		remove(i)

