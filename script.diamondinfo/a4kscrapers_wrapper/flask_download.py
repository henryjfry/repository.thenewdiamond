from flask import Flask, render_template
from threading import Thread
import time
from time import sleep
import json

import sys
from multiprocessing import Process

app = Flask(__name__, template_folder='./')

this = sys.modules[__name__]
this.status = None
this.message = None
this.shutdown = False

from flask import request
def shutdown_server():
	#func = request.environ.get('werkzeug.server.shutdown')
	#if func is None:
	#	raise RuntimeError('Not running with the Werkzeug Server')
	#func()
	this.shutdown = True
	#exit()

@app.get('/shutdown')
def flask_shutdown():
	shutdown_server()
	return 'Server shutting down...'

def task(magnet_list, download_link, download_path):#def download_progressbar():
	global download_path2
	global download_link2
	download_link2 = download_link
	download_path2 = download_path
	if download_link == None:
		status = 'No Donwload'
		message = 'No Donwload'
		return None
	url = download_link
	file_path = download_path
	from urllib.request import urlretrieve, urlcleanup
	from urllib.parse import unquote
	urlcleanup()
	import sys
	global rem_file # global variable to be used in dlProgress
	rem_file = url.split('/')[-1]

	with open(magnet_list, 'r') as fp:
		num_lines = sum(1 for line in fp if line.rstrip())
	log_msg = str('REMAINING_LINES_MAGNET_LIST =   '+str(num_lines))

	start = time.time()
	def dlProgress(count, blockSize, totalSize):
		percent = int(count*blockSize*100/totalSize)
		this.status = percent/1
		done = int(50 * count*blockSize / totalSize)
		suffix = "\r[%s%s] %s  <br>  %s  <br>  %s   Kbps " % ('=' * done, ' ' * (50-done),str(percent)+'%',unquote(rem_file), (1/1000)*count*blockSize//(time.time() - start))
		message = "\r" + rem_file + "...%d%%" % percent 
		message = message + '<br>' + suffix
		this.message = message + '<br>' + log_msg
		#sys.stdout.write("\r" + rem_file + "...%d%%" % percent)
		sys.stdout.write(message.replace('<br>',''))
		sys.stdout.flush()
		if this.shutdown:
			exit()
	urlretrieve(url, file_path, reporthook=dlProgress)
	return file_path


@app.route('/')
def index():
	return render_template('index.html')
	
@app.route('/status', methods=['GET'])
def getStatus():
	statusList = {'status':this.status, 'message': this.message}
	return json.dumps(statusList)

def flask_downloader(magnet_list, download_link, download_path):
	this.shutdown = False
	t1 = Thread(target=task, args=[magnet_list, download_link,download_path])
	t1.start()
	while t1.is_alive():
		sleep(1)
		t1.join()
	del t1

def flask_thread():
	app.run(host='192.168.0.68', debug=False,port=1111, threaded=True)

t2 = Thread(target=flask_thread)
t2.setDaemon(True)
t2.start()

#server = Process(target=flask_thread)
#server.start()

#if __name__ == '__main__':
#	app.run(debug=True,port=8181)