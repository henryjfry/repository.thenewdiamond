import os, urllib.parse, urllib.request, urllib.error, threading
from PIL import Image, ImageFilter
import xbmc, xbmcvfs
from resources.lib import Utils

def filter_image(input_img, radius=25):
	if not xbmcvfs.exists(os.path.join(Utils.IMAGES_DATA_PATH)):
		xbmcvfs.mkdir(os.path.join(Utils.IMAGES_DATA_PATH))
	input_img = xbmcvfs.translatePath(input_img.encode('utf-8')).replace('image://', '')
	if input_img.endswith('/'):
		input_img = input_img[:-1]
	if len(urllib.parse.unquote_plus(input_img)) < len(input_img):
		input_img = urllib.parse.unquote_plus(input_img)
	cachedthumb = xbmc.getCacheThumbName(input_img)
	filename = '%s-radius_%i.png' % (cachedthumb, radius)
	targetfile = os.path.join(Utils.IMAGES_DATA_PATH, filename)
	xbmc_vid_cache_file = os.path.join('special://profile/Thumbnails/Video', cachedthumb[0], cachedthumb)
	xbmc_cache_file = os.path.join('special://profile/Thumbnails', cachedthumb[0], cachedthumb[:-4] + '.jpg')
	if input_img == '':
		return '', ''
	if not xbmcvfs.exists(targetfile):
		img = None
		for i in range(1, 4):
			try:
				if xbmcvfs.exists(xbmc_cache_file):
					Utils.log('image already in Kodi cache: ' + xbmc_cache_file)
					img = Image.open(xbmcvfs.translatePath(xbmc_cache_file))
					break
				elif xbmcvfs.exists(xbmc_vid_cache_file):
					Utils.log('image already in Kodi video cache: ' + xbmc_vid_cache_file)
					img = Image.open(xbmcvfs.translatePath(xbmc_vid_cache_file))
					break
				else:
					xbmcvfs.copy(str(input_img, 'utf-8', errors='ignore'), targetfile)
					img = Image.open(targetfile)
					break
			except:
				Utils.log('Could not get image for %s (try %i)' % (input_img, i))
				xbmc.sleep(200)
		if not img:
			return '', ''
		try:
			img.thumbnail((200, 200), Image.ANTIALIAS)
			img = img.convert('RGB')
			imgfilter = MyGaussianBlur(radius=radius)
			img = img.filter(imgfilter)
			img.save(targetfile)
		except:
			Utils.log('PIL problem probably....')
			return '', ''
	else:
		Utils.log('blurred img already created: ' + targetfile)
		img = Image.open(targetfile)
	imagecolor = get_colors(img)
	return targetfile, imagecolor

def get_colors(img):
	width, height = img.size
	try:
		pixels = img.load()
	except:
		return 'FFF0F0F0'
	data = []
	for x in range(width//2):
		for y in range(height//2):
			cpixel = pixels[x*2, y*2]
			data.append(cpixel)
	r = 0
	g = 0
	b = 0
	counter = 0
	for x in range(len(data)):
		brightness = data[x][0] + data[x][1] + data[x][2]
		if brightness > 150 and brightness < 720:
			r += data[x][0]
			g += data[x][1]
			b += data[x][2]
			counter += 1
	if counter > 0:
		rAvg = int(r/counter)
		gAvg = int(g/counter)
		bAvg = int(b/counter)
		Avg = (rAvg + gAvg + bAvg) / 3
		minBrightness = 130
		if Avg < minBrightness:
			Diff = minBrightness - Avg
			for color in [rAvg, gAvg, bAvg]:
				if color <= (255 - Diff):
					color += Diff
				else:
					color = 255
		imagecolor = 'FF%s%s%s' % (format(rAvg, '02x'), format(gAvg, '02x'), format(bAvg, '02x'))
	else:
		imagecolor = 'FFF0F0F0'
	Utils.log('Average Color: ' + imagecolor)
	return imagecolor

class FilterImageThread(threading.Thread):

	def __init__(self, image='', radius=25):
		threading.Thread.__init__(self)
		self.filterimage = image
		self.radius = radius

	def run(self):
		try:
			self.image, self.imagecolor = filter_image(self.filterimage, self.radius)
		except:
			self.image = ''
			self.imagecolor = ''
			Utils.log('exception. probably android PIL issue.')

	def raise_exc(self, excobj):
		assert self.isAlive(), "thread must be started"
		for tid, tobj in threading._active.items():
			if tobj is self:
				_async_raise(tid, excobj)
				return


	def terminate(self):
		# must raise the SystemExit type, instead of a SystemExit() instance
		# due to a bug in PyThreadState_SetAsyncExc
		self.raise_exc(SystemExit)

class MyGaussianBlur(ImageFilter.Filter):

	name = 'GaussianBlur'

	def __init__(self, radius=2):
		self.radius = radius

	def filter(self, image):
		return image.gaussian_blur(self.radius)
