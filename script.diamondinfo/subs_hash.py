META = None

import struct, os
#import urllib
__64k = 65536
__longlong_format_char = 'q'
__byte_size = struct.calcsize(__longlong_format_char)

def first_last_64kb(url):
	import requests
	import tempfile
	from urllib3.exceptions import IncompleteRead

	def download_last_64kb(url):
		# Create a temporary file to store the content
		with tempfile.NamedTemporaryFile(delete=False) as temp_file:
			try:
				# Make the request with the Range header to download the last 64 KB
				headers = {'Range': 'bytes=%s' % str(__64k*-1)}
				with requests.get(url, headers=headers, stream=True) as response:
					response.raise_for_status()
					# Write the content to the temporary file
					for chunk in response.iter_content(chunk_size=1024):
						temp_file.write(chunk)
				# Return the path to the temporary file
				return temp_file.name
			except IncompleteRead as e:
				# Handle the incomplete read error
				print(f"IncompleteRead error: {e}")
				if os.path.exists(temp_file.name):
					os.remove(temp_file.name)

	def download_last_64kb_2(url):
		# Create a temporary file to store the content
		with tempfile.NamedTemporaryFile(delete=False) as temp_file:
			try:
				# Make the request with the Range header to download the last 64 KB
				response = requests.head(url, verify=False)
				filesize = int(response.headers['content-length'])
				if filesize < __64k * 2:
					try: filesize = int(str(response.headers['content-range']).split('/')[1])
					except: pass
				headers = {"Range": 'bytes=%s-%s' % (filesize - __64k, filesize)}
				with requests.get(url, headers=headers, stream=True) as response:
					response.raise_for_status()
					# Write the content to the temporary file
					for chunk in response.iter_content(chunk_size=1024):
						temp_file.write(chunk)
				# Return the path to the temporary file
				return temp_file.name
			except IncompleteRead as e:
				# Handle the incomplete read error
				print(f"IncompleteRead error: {e}")
				if os.path.exists(temp_file.name):
					os.remove(temp_file.name)

	def download_first_64kb(url):
		# Create a temporary file to store the content
		with tempfile.NamedTemporaryFile(delete=False) as temp_file:
			try:
				# Make the request with the Range header to download the last 64 KB
				headers = {'Range': 'bytes=0-%s' % str(__64k)}
				with requests.get(url, headers=headers, stream=True) as response:
					response.raise_for_status()
					# Write the content to the temporary file
					for chunk in response.iter_content(chunk_size=1024):
						temp_file.write(chunk)
				# Return the path to the temporary file
				return temp_file.name
			except IncompleteRead as e:
				# Handle the incomplete read error
				print(f"IncompleteRead error: {e}")
				if os.path.exists(temp_file.name):
					os.remove(temp_file.name)
	try: 
		last_64kb = download_last_64kb(url)
	except: 
		last_64kb = download_last_64kb_2(url)
	first_64kb = download_first_64kb(url)
	return first_64kb, last_64kb


def temp_file():
	import tempfile
	file = tempfile.NamedTemporaryFile()
	filename = file.name
	return filename
	
def is_local(_str):
	from urllib.parse import urlparse
	if os.path.exists(_str):
		return True
	elif urlparse(_str).scheme in ['','file']:
		return True
	return False

def hashFile_url(filepath): 
	#https://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
	#filehash = filesize + 64bit sum of the first and last 64k of the file
	name = filepath.strip()
	filepath = filepath.strip()
	if is_local(filepath):
		local_file = True
	else:
		local_file = False

	if local_file == True and filepath[:4] == 'http':
		local_file = False
	if local_file == False:
		f = None
		url = name
		#from urllib import request
		#request.urlcleanup()
		import requests

		response = requests.head(url)#, verify=False)
		filesize = int(response.headers['content-length'])

		if filesize < __64k * 2:
			try: filesize = int(str(response.headers['content-range']).split('/')[1])
			except: pass

		first_64kb = temp_file()
		last_64kb = temp_file()

		headers = {"Range": 'bytes=0-%s' % (str(__64k -1 ))}
		r = requests.get(url, headers=headers)#, verify=False)
		with open(first_64kb, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024): 
				if chunk: # filter out keep-alive new chunks
					f.write(chunk)

		if filesize > 0:
			headers = {"Range": 'bytes=%s-%s' % (filesize - __64k, filesize-1)}
		else:
			f.close()
			os.remove(first_64kb)
			return "SizeError", 0

		try:
			r = requests.get(url, headers=headers)#, verify=False)
			with open(last_64kb, 'wb') as f:
				for chunk in r.iter_content(chunk_size=1024): 
					if chunk: # filter out keep-alive new chunks
						f.write(chunk)
		except:
			f.close()
			if os.path.exists(last_64kb):
				os.remove(last_64kb)
			if os.path.exists(first_64kb):
				os.remove(first_64kb)
			return 'IOError', 0
		f = open(first_64kb, 'rb')

	try:
		longlongformat = '<q'  # little-endian long long
		bytesize = struct.calcsize(longlongformat) 

		if local_file:
			f = open(name, "rb") 
			filesize = os.path.getsize(name) 
		hash = filesize 

		if filesize < __64k * 2: 
			f.close()
			if local_file == False:
				os.remove(last_64kb)
				os.remove(first_64kb)
			return "SizeError", 0

		range_value = __64k / __byte_size
		range_value = round(range_value)

		for x in range(range_value): 
			buffer = f.read(bytesize) 
			(l_value,)= struct.unpack(longlongformat, buffer)  
			hash += l_value 
			hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  

		if local_file:
			f.seek(max(0,filesize-__64k),0) 
		else:
			f.close() 
			f = open(last_64kb, 'rb')
		for x in range(range_value): 
			buffer = f.read(bytesize) 
			(l_value,)= struct.unpack(longlongformat, buffer)  
			hash += l_value 
			hash = hash & 0xFFFFFFFFFFFFFFFF 
		
		f.close() 
		if local_file == False:
			os.remove(last_64kb)
			os.remove(first_64kb)
		returnedhash =  "%016x" % hash 
		return returnedhash, filesize

	except(IOError): 
		if local_file == False:
			os.remove(last_64kb)
			os.remove(first_64kb)
		return 'IOError', 0

import re

def ass_to_srt(ass_filename, srt_filename):
	def ass_time_to_srt_time(ass_time):
		h, m, s = ass_time.split(':')
		s, cs = s.split('.')
		ms = str(int(cs) * 10).zfill(3)  # Convert centiseconds to milliseconds
		return f"{h.zfill(2)}:{m.zfill(2)}:{s.zfill(2)},{ms}"
	with open(ass_filename, 'r', encoding='utf-8') as ass_file:
		lines = ass_file.readlines()
	dialogue_lines = [line for line in lines if line.startswith('Dialogue:')]
	srt_lines = []
	index = 1
	for line in dialogue_lines:
		parts = line.split(',', 9)
		start_time = ass_time_to_srt_time(parts[1].strip())
		end_time = ass_time_to_srt_time(parts[2].strip())
		text = parts[9].strip().replace('\\N', '\n').replace('\\n', '\n')
		text = re.sub(r'{.*?}', '', text)  # Remove ASS style tags
		srt_lines.append(f"{index}")
		srt_lines.append(f"{start_time} --> {end_time}")
		srt_lines.append(text.replace('\h',''))
		srt_lines.append("")
		index += 1
	with open(srt_filename, 'w', encoding='utf-8') as srt_file:
		srt_file.write("\n".join(srt_lines))


