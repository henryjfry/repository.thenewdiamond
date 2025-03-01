import xbmc
from resources.lib import Utils

def run_service():
	#from resources.lib.xtream2m3u_run import app as flask_app
	#from multiprocessing import Process
	#import socket
	#socket.setdefaulttimeout(120) # seconds
	#server = Process(target=flask_app.run(debug=False, host='0.0.0.0'))
	#server.start()
	#Utils.tools_log('STARTING__SERVER')
	#flask_app.run(debug=False, host='0.0.0.0')
	from resources.lib.xtream2m3u_run import start
	start()
	while not xbmc.Monitor().abortRequested():
		xbmc.sleep(100)

xbmc.log(str('SERVICE2')+'!!===>OPENINFO', level=xbmc.LOGINFO)
run_service()