#!/usr/bin/env python3
import os
import requests
import time
import re
import urllib.request

from tqdm import tqdm


def download(url: str, fname: str):
	resp = requests.get(url, stream=True)
	total = int(resp.headers.get('content-length', 0))
	# Can also replace 'file' with a io.BytesIO object
	with open(fname, 'wb') as file, tqdm(
		desc=fname,
		total=total,
		unit='iB',
		unit_scale=True,
		unit_divisor=1024,
	) as bar:
		for data in resp.iter_content(chunk_size=1024):
			size = file.write(data)
			bar.update(size)

def getSentenceCase(source: str):
	file_type = source.split('.')[-1]
	source = source.replace('.'+file_type,'')
	output = ""
	isFirstWord = True
	for c in source:
		if isFirstWord and not c.isspace():
			c = c.upper()
			isFirstWord = False
		elif not isFirstWord and c in ".!?":
			isFirstWord = True
		else:
			if c.upper() != c:
				c = c.lower()
		output = output + c
	output = output + '.' + file_type
	output = output.replace(re.search('[S][0-9]*[e][0-9]*', output)[0],re.search('[S][0-9]*[e][0-9]*', output)[0].upper())
	return output

def read_magnet_links(file_path):
	with open(file_path, 'r') as f:
		return f.read().splitlines()

def remove_line_from_file(file_path, line_to_remove):
	with open(file_path, 'r') as f:
		lines = f.readlines()
	
	with open(file_path, 'w') as f:
		for line in lines:
			if line.strip() != line_to_remove.strip():
				f.write(line)

def add_line_to_file(file_path, line_to_add):
	with open(file_path) as fobj:
		text = fobj.read()

	with open(file_path, 'a') as fobj:
		if not text.endswith('\n'):
			fobj.write('\n')
		fobj.write(line_to_add)

def download_file(url, save_path):
	print('DOWNLOAD_START', save_path)
	#response = requests.get(url)
	#with open(save_path, 'wb') as f:
	#	f.write(response.content)
	download(url, save_path)

def add_magnet(api_key, magnet_link):
	headers = {
		'Authorization': f'Bearer {api_key}',
	}

	endpoint = 'https://api.real-debrid.com/rest/1.0/torrents/addMagnet?'
	params = {'magnet': magnet_link}
	response = requests.post(endpoint, headers=headers, data=params)

	if response.status_code == 200 or response.status_code == 201:
		data = response.json()
		return data['id']
	else:
		return None

def delete_torrent(api_key, torr_id):
	headers = {
		'Authorization': f'Bearer {api_key}',
	}

	response = requests.delete('https://api.real-debrid.com/rest/1.0/torrents/delete/' + torr_id, headers=headers)

	if response.status_code == 200 or response.status_code == 201:
		data = response.json()
		return data
	else:
		return None



def unrestrict_link(api_key, link_url):
	headers = {
		'Authorization': f'Bearer {api_key}',
	}
	params = {'link': link_url }
	response = requests.post('https://api.real-debrid.com/rest/1.0/unrestrict/link', headers=headers, data=params)

	if response.status_code == 200 or response.status_code == 201:
		data = response.json()
		return data
	else:
		print(response.json())
		return None

def select_files(api_key, torrent_id):
	headers = {
		'Authorization': f'Bearer {api_key}',
	}

	#params = {'files': 'all'}
	#endpoint = f'https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{torrent_id}'
	#response = requests.get(endpoint, headers=headers, data=params)
	params = {'files': 'all'}
	response = requests.post('https://api.real-debrid.com/rest/1.0/torrents/selectFiles/' + torrent_id, headers=headers, data=params)
	#print(response)
	#print(response.status_code)
	if response.status_code == 200 or response.status_code == 201 or response.status_code == 204:
		data = get_file_info(api_key, torrent_id)
		#print(data)
		#data = response.json()
		return data
		#['files']
	else:
		return None

def select_files_individual(api_key, torrent_id, params):
	headers = {
		'Authorization': f'Bearer {api_key}',
	}
	#params = {'files': ids[files.index(x)]}
	response = requests.post('https://api.real-debrid.com/rest/1.0/torrents/selectFiles/' + torrent_id, headers=headers, data=params)

	if response.status_code == 200 or response.status_code == 201 or response.status_code == 204:
		#data = response.json()
		data = get_file_info(api_key, torrent_id)
		data2 = data
		for i in reversed(data['files']):
			if i['selected'] == 0:
				data2['files'].pop(data['files'].index(i))
		data = data2
		print(data2)
		return data
	else:
		return None

def get_file_info(api_key, file_id):
	headers = {
		'Authorization': f'Bearer {api_key}',
	}

	endpoint = f'https://api.real-debrid.com/rest/1.0/torrents/info/{file_id}'
	response = requests.get(endpoint, headers=headers)

	try:
		data = response.json()
		ids = [element['id'] for element in data['files']]
		files = [element['path'] for element in data['files']]
		files = [x.encode('utf-8') for x in files]
		tot_files = ids[-1]

		#response = requests.delete('https://api.real-debrid.com/rest/1.0/torrents/delete/' + torr_id, headers=header)
		#print(response)

		files, ids = zip(*sorted(zip(files,ids)))
		#print(files)
	except:
		return None

	if response.status_code == 200 or response.status_code == 201:
		data = response.json()
		return data
	else:
		return None

def check_instant_availability(api_key, magnet_link):
	headers = {
		'Authorization': f'Bearer {api_key}',
	}

	endpoint = 'https://api.real-debrid.com/rest/1.0/torrents/checkInstantAvailability'
	payload = {'magnet': magnet_link}
	response = requests.post(endpoint, headers=headers, json=payload)

	if response.status_code == 200:
		data = response.json()
		if 'ready' in data and data['ready']:
			return True
		else:
			return False
	else:
		return False

def process_magnet_links(file_path, api_key, download_folder):
	download_bool = False
	magnet_download = []
	magnet_added = []
	blank_loop_count = 0
	while True:
		if download_bool:
			print('SLEEPING_10_SECONDS!!!')
			time.sleep(10)
		magnet_links = read_magnet_links(file_path)
		print()
		print()
		if not magnet_links:
			print("No new magnet links found. Waiting for new additions...")
			if blank_loop_count > 5:
				print('ALL DOWNLOADS COMPLETE')
				exit()
			# You can add a sleep timer here to avoid excessive API requests
			time.sleep(30)
			blank_loop_count = blank_loop_count + 1
			continue
		
		magnet_link = magnet_links[0]

		if magnet_link.startswith('http'):
			print(f"Downloading RD HTTP link: {magnet_link}")
			#file_name = os.path.basename(magnet_link)
			#save_path = os.path.join(download_folder, file_name)
			#download_file(magnet_link, save_path)
			#print(magnet_link)
			new_link = unrestrict_link(api_key, magnet_link)
			print(new_link)
			#exit()
			if new_link:
				file_name = os.path.basename(new_link['filename'])
				if new_link['filename'][0:1].lower() == new_link['filename'][0:1]:
					file_name = getSentenceCase(os.path.basename(new_link['filename']))
				else:
					file_name = os.path.basename(new_link['filename'])
				save_path = os.path.join(download_folder, file_name)
				download_link = new_link['download']
				download_file(download_link, save_path)
				download_bool = True
				remove_line_from_file(file_path, magnet_link)
				print(f"Download of '{file_name}' complete! Removed link from the file.")
			else:
				download_bool = False
				print(f"HOSTER FAIL '{magnet_link}'.")
				remove_line_from_file(file_path, magnet_link)
		else:
			torrent_id = add_magnet(api_key, magnet_link)
			if torrent_id is None:
				print(f"Link '{magnet_link}' is not a valid magnet link. Removing from the file.")
				remove_line_from_file(file_path, magnet_link)
				continue
			file_info = select_files(api_key, torrent_id)
			file_count = 0
			for x in file_info['files']:
				if '.mp4' in str(x['path']) or '.avi' in str(x['path']) or '.mkv' in str(x['path']):
					file_count = file_count + 1
			data = file_info

			if file_info['status'] != 'downloaded':
				response = delete_torrent(api_key, torrent_id)
				ids = [element['id'] for element in data['files']]
				files = [element['path'] for element in data['files']]
				files = [x.encode('utf-8') for x in files]
				files, ids = zip(*sorted(zip(files,ids)))
				download_count = 0
				for x in files:
					if '.mp4' in str(x) or '.avi' in str(x) or '.mkv' in str(x):
						print('SLEEPING_10_SECONDS!!!')
						time.sleep(10)
						print('')
						print('')

						torrent_id = add_magnet(api_key, magnet_link)
						params = {'files': ids[files.index(x)]}
						file_info2 = select_files_individual(api_key, torrent_id, params)
						if file_info2['status'] == 'downloaded':
							folder = file_info2['original_filename']
							if '.mp4' in str(folder) or '.avi' in str(folder) or '.mkv' in str(folder):
								folder = None
							for file in file_info2['links']:
								new_link = unrestrict_link(api_key, file)
								file_name = os.path.basename(new_link['filename'])
								if new_link['filename'][0:1].lower() == new_link['filename'][0:1]:
									file_name = getSentenceCase(os.path.basename(new_link['filename']))
								else:
									file_name = os.path.basename(new_link['filename'])
								if folder:
									download_folder2 = download_folder + folder + '/'
									folder = None
									if not os.path.exists(download_folder2):
										os.makedirs(download_folder2)
								save_path = os.path.join(download_folder2, file_name)
								download_link = new_link['download']
								if not save_path in str(magnet_download):
									download_file(download_link, save_path)
									magnet_download.append(save_path)
									print(f"Downloaded '{file_name}' successfully!")
								if save_path in str(magnet_download):
									download_count = download_count + 1
						else:
							if file_info2['filename'] in str(magnet_added):
								delete_torrent(api_key, torrent_id)
							else:
								magnet_added.append(file_info2['filename'])
				if download_count == file_count:
					remove_line_from_file(file_path, magnet_link)
					print("All files downloaded. Removed magnet link from the file.")
				else:
					remove_line_from_file(file_path, magnet_link)
					add_line_to_file(file_path, magnet_link)
			if file_info['status'] == 'downloaded':
				print(file_info)
				folder = file_info['original_filename']
				if '.mp4' in str(folder) or '.avi' in str(folder) or '.mkv' in str(folder):
					folder = None
				for file in file_info['links']:
					new_link = unrestrict_link(api_key, file)
					print(new_link)
					if new_link['filename'][0:1].lower() == new_link['filename'][0:1]:
						file_name = getSentenceCase(os.path.basename(new_link['filename']))
					else:
						file_name = os.path.basename(new_link['filename'])
					if folder:
						download_folder2 = download_folder + folder + '/'
						if not os.path.exists(download_folder2):
							os.makedirs(download_folder2)
					save_path = os.path.join(download_folder2, file_name)
					download_link = new_link['download']
					download_bool = True
					download_file(download_link, save_path)
					print(f"Downloaded '{file_name}' successfully!")

				remove_line_from_file(file_path, magnet_link)
				print("All files downloaded. Removed magnet link from the file.")
			else:
				download_bool = False
				print(f"No instant availability for magnet link '{magnet_link}'. Will retry later.")
				# You can add a sleep timer here before checking again
				time.sleep(30)


if __name__ == "__main__":

	with open('/home/osmc/.kodi/userdata/addon_data/script.extendedinfo/settings.xml') as f:
		lines = f.readlines()
		for line in lines:
			if 'RD_api' in str(line):
				api_key = line.split('>')[1].split('</')[0]

	#print(api_key)
	magnet_links_file = '/home/osmc/magnet_list.txt'
	download_folder = '/home/osmc/Movies/'  # Replace with the path to your desired download folder

	process_magnet_links(magnet_links_file, api_key, download_folder)