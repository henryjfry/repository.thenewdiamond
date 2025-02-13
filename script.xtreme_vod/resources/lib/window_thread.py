from threading import Thread
import threading
class window_thread(threading.Thread):

	def __init__(self, window):
		threading.Thread.__init__(self, daemon=True)
		self.window = window
		del window

	def run(self):
		self.window2 = self.window
		del self.window
		return self.window2