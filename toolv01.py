import re
import os
import sys
import csv
import time
import shutil
import tempfile
import requests
import filetype
import argparse
from selenium import webdriver
from urllib.parse import urlparse
from file_read_backwards import FileReadBackwards
from selenium.webdriver.chrome.options import Options
import tbselenium.common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import launch_tbb_tor_with_stem

# handle nested iframes
SCROLL_PAUSE_TIME = 1
SCROLL_AMOUNT = 4

STANDARD_SIZES = set(((250, 250), (147,147), (300, 1050), (160, 600), (728, 90), 
        (300, 600), (970, 90), (234, 60), (125, 125), (300, 250), 
        (120, 240), (120, 90), (180, 160), (300, 100), (970, 250), 
        (120, 60), (550, 480), (468, 60), (336, 280), (88, 31), 
        (240, 400), (180, 150), (120, 600), (720, 300), (976, 40),
        (180, 900), (970, 90) , (292 ,143), (127, 82) , (615,40))) # stadard ad sizes

BEACON_SIZES = set(((1, 1)))

def inter(s):
    return s.format(**sys._getframe(1).f_locals) #string interpolation

class advert:
	"""docstring for advert"""
	def __init__(self, name, eyedee, title, width, height, source, ident, fn):
		super(advert, self).__init__()
		self.name = name
		self.eyedee = eyedee
		self.title = title
		self.width = width
		self.height = height
		self.source = source
		self.ident = ident
		self.fn = fn

def handle_images(frame, fn):
	try:
		eyedee = frame.get_attribute("class")	
		#print ('class tag found')
	except:
		#print ('no class')
		eyedee = "NULL"
	try:
		title = frame.get_attribute("alt")	
		#print ('alt tag found')
	except:
		#print ('no alt')
		title = "NULL"
	try:
		width = frame.get_attribute("width")
		#print ('width:' , width)
	except:
		#print ('no width')
		width = "NULL"
	try:
		#height = frame.get_attribute("height")
		print ('height:' , height)
	except:
		#print ('no height')
		height = "NULL"
	try:
		source = frame.get_attribute("src")	
		#print ('source:' , source)
	except:
	 	#print ('no source')
	 	source = "NULL"

	name = "exists"
	ad_hai = is_it_an_ad(width, height)

	retclass = advert(name, eyedee, title, width, height, source, ad_hai, fn)
	return retclass

def handle_frames(iframe, iframe_source, fn):
	frame = iframe
	retclassList = []
	try:
		images = driver.find_elements_by_tag_name("img")
		#print (len(images), ' images found in iframe')
	except:
		pass
		#print ('no image')
	for image in images:	
		name = driver.execute_script('return document.location.href');
		try:
			eyedee = image.get_attribute("id")	
			#print ('id: ', eyedee)
		except:
			eyedee = "NULL"
			#print ('no id')
		try:
			title = image.get_attribute("title")	
			#print ('title: ', title)
		except:
			title = "NULL"
			#print ('no title')
		try:
			width = int(image.get_attribute("width"))	
			#print ('width:' , width)
		except:
			width = "NULL"
			#print ('no width')
		try:
			height = int(image.get_attribute("height"))
			#print ('height:' , height)
		except:
			height = "NULL"
			#print ('no height')
		try:
			source = image.get_attribute("src")	
			#print ('source:' , source)
		except:
		 	source = "NULL"
		 	#print ('no source')

		ad_hai = is_it_an_ad(width, height)
		retclassList.append(advert(name, eyedee, title, width, height, source, ad_hai, fn))
		#print("xxxxxxxxxxxx inner loop xxxxxxxxxxxxx\n")
	
	reg_ret = use_regex(iframe_source, fn)
	retclassList.append(reg_ret)

	return retclassList

def use_regex(iframe, fn):
	frame = str(iframe)
	pattern =  ';img(.*?)/&gt'
	src_pattern = '(?<=src=")(.*?)(?=")'
	w_pattern = '(?<=width=")(.*?)(?=")'
	h_pattern = '(?<=height=")(.*?)(?=")'
	
	matches = re.findall(pattern,frame)
	#print("Testing using regex")
	try:
		src = re.search(src_pattern, str(matches))
		width = int(re.search(w_pattern, str(matches)).group(0))
		height = int(re.search(h_pattern, str(matches)).group(0))
		#print("src:", src.group(0))
		#print("w:", width)
		#print("h:", height)
		
		ad_hai = is_it_an_ad(width, height)
		
		ret = advert('regex_ad', 'NULL', 'NULL', width, height, src.group(0), ad_hai, fn)
		# if ad_hai:
		# 	print("reg ad found")
		# else:
		# 	print("reg: not ad")
	except:
		#print("reg_ad failed")
		ret = advert('F_regex_ad', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 0, fn)

	return ret

def is_it_an_ad(width, height):
    if width == 1 and height == 1:
    	#print('web beacon')	
    	return -1
    elif (width, height) not in STANDARD_SIZES:
    	#print('Not an ad')
    	return 0
    else:
    	#print('We have an ad')
    	return 1

def scroll_page(driver):
	# Scroll down to bottom
	print("Scrolling down the page...")
	page_height = driver.execute_script("return document.documentElement.scrollHeight") # get page height
	scroll_num = int(page_height/540)
	Y = 540

	for i in range(scroll_num):
		script = inter("window.scrollTo(0, {Y})")
		driver.execute_script(script)
		time.sleep(SCROLL_PAUSE_TIME)
		Y += 540

	time.sleep(1)
	page_height = driver.execute_script("return document.documentElement.scrollHeight") # get page height again
	scroll_num = int((page_height - Y)/540)
	for i in range(scroll_num):
		script = inter("window.scrollTo(0, {Y})")
		driver.execute_script(script)
		time.sleep(SCROLL_PAUSE_TIME)
		Y += 540

def set_exit_relay(code):
	torrc_file_path = "/home/kasai/.local/share/torbrowser/tbb/x86_64/tor-browser_en-US/Browser/TorBrowser/Data/Tor/torrc" 
	torrc_org = "/home/kasai/.local/share/torbrowser/tbb/x86_64/tor-browser_en-US/Browser/TorBrowser/Data/Tor/torrc_org" 
	
	if not os.path.exists(torrc_file_path):
			return -1

	if not os.path.exists(torrc_org): # create initial copy
		read_file = open(torrc_file_path, "r")
		copy = read_file.read()
		read_file.close()
		write_file = open(torrc_org, 'a')
		write_file.write(copy)
		write_file.close()

	read_file = open(torrc_org, "r")
	copy = read_file.read()
	read_file.close()

	os.remove(torrc_file_path)
	
	wtf = "ExitNodes {" + code + "} StrictNodes 1"
	file = open(torrc_file_path, "a")
	file.write(copy)
	file.write(wtf)
	file.close()
	return 1

if __name__ == "__main__":

	this_dir = os.getcwd() # can use later

	parser = argparse.ArgumentParser()
	parser.add_argument("browser_select", type = int, help="Please choose 1 for Chrome or 2 for Tor")
	args = parser.parse_args()

	selection = int(args.browser_select)
	cc = "es"
	#site = 'https://check.torproject.org'

	#site = 'https://sourceforge.net/projects/peazip/'
	#site = "https://stackoverflow.com/questions/23028664/python-beautifulsoup-iframe-document-html-extract"
	#site = 'https://www.dawn.com'
	#site = 'https://www.w3schools.com/python/'
	site  = 'https://www.speedtest.net'
	
	#site = 'https://www.youtube.com'
	#site = 'https://www.geeksforgeeks.org/rename-multiple-files-using-python/'
	#site = 'https://symptoms.webmd.com/default.htm#/info'
	#site = 'https://www.accuweather.com'
	#site = 'https://www.espncricinfo.com'
	
	domain_parsed = urlparse(site)
	
	if selection == 1:
		print("Domain is: ", domain_parsed.hostname)
		domain = domain_parsed.hostname +"_chrome"
		if not os.path.exists(domain):
			os.makedirs(domain)

		chrome_options = Options()
		chrome_options.add_argument("--window-size=1920,1080")
		driver = webdriver.Chrome('/usr/local/bin/chromedriver' , chrome_options=chrome_options)
		print ("Starting Chrome...")

	elif selection == 2:
		print("Domain is: ", domain_parsed.hostname)
		domain = domain_parsed.hostname +"_tor_"+cc
		if not os.path.exists(domain):
			os.makedirs(domain)

		tbpath = '/home/kasai/.local/share/torbrowser/tbb/x86_64/tor-browser_en-US'
		torrc_file_path = "/home/kasai/.local/share/torbrowser/tbb/x86_64/tor-browser_en-US/Browser/TorBrowser/Data/Tor/torrc" 
		
		print ("Setting up Tor...")
		#cus_config = {'ControlPort': str(cm.STEM_CONTROL_PORT), 'SOCKSPort': str(cm.STEM_SOCKS_PORT), 'DataDirectory': tempfile.mkdtemp(), 'ExitNodes': '{es}', 'StrictNodes' : '1'}
		#tor_process = launch_tbb_tor_with_stem(tbb_path=tbpath)
		driver = TorBrowserDriver(tbpath, tor_cfg=1)
		print ("Starting Tor...")

	elif selection == 3:
		cc = input("Enter country code to set: ")
		done = set_exit_relay(cc)
		print("Restarting Tor service...")
		os.system("sudo service tor restart")
		print(done)
		# time.sleep(5)
		# tbpath = '/home/kasai/.local/share/torbrowser/tbb/x86_64/tor-browser_en-US'
		# driver = TorBrowserDriver(tbpath)
		# print ("Starting Tor...")
		# driver.get('https://check.torproject.org')
		exit()	
	
	else:
		sys.stderr.write("Please choose 1 for Chrome or 2 for Tor")

	os.chdir('/home/kasai/Documents/adscape/code/newScape/adtool') #settool dir

	frames_folder = domain+"/Frames"
	if not os.path.exists(frames_folder):
		os.makedirs(frames_folder)	

	ads_folder = domain+"/Ads"
	if not os.path.exists(ads_folder):
		os.makedirs(ads_folder)


	start_time = time.time()
	driver.get(site)
	end_time = time.time()
	time.sleep(2)
	plt = round(end_time-start_time, 3)
	
	scroll_page(driver) # scroll the page
	time.sleep(3)

	frame_count = 0
	image_count = 0
	ad_count = 0
	tracking_pix = 0
	processed_list_frame = []
	processed_list_img = []
	emb = 0

	iframes = driver.find_elements_by_tag_name("iframe")
	print("Processing iframes...")
	
	for frame in iframes:
		frame_count += 1
		driver.switch_to.default_content()
		try:
			driver.switch_to.frame(frame)
			#print("Frame found")
		except:
			#print("Not a frame")
			continue
		#stale frames
		try:
			embed_frames = frame.find_elements_by_tag_name("iframe")
			emb = 1
			#print("Embed frames found")
		except:
		 	#print("No embed frames")
		 	emb = 0

		if emb == 1:
			iframe_source = driver.page_source
			for emb_fram in embed_frames:
				out = handle_frames(frame, iframe_source, frame_count)
				if out.ident == 1 or out.ident == -1:
					#print("adding to list")
					processed_list_frame.append(things)

			output_f = frames_folder + "/driverFrames" + str(frame_count)+ ".txt"
			iframe_d_f = open(output_f, "w+")
			iframe_d_f.write(iframe_source)
			iframe_d_f.close()
			
			#print ('xxxxxxxxxxxx PROCESSING FRAME', frame_count, 'xxxxxxxxxxx')
			out = handle_frames(frame, iframe_source, frame_count)
			for things in out:
				if things.ident == 1 or things.ident == -1:
					#print("adding to list")
					processed_list_frame.append(things)
				#print ('xxxxxxxxxxxxxxxxxxxxxxxxx\n')
		
		elif emb == 0:
			iframe_source = driver.page_source
			output_f = frames_folder + "/driverFrames" + str(frame_count)+ ".txt"
			iframe_d_f = open(output_f, "w+")
			iframe_d_f.write(iframe_source)
			iframe_d_f.close()
			#print ('xxxxxxxxxxxx PROCESSING FRAME', frame_count, 'xxxxxxxxxxx')
			out = handle_frames(frame, iframe_source, frame_count)
			for things in out:
				if things.ident == 1 or things.ident == -1:
					#print("adding to list")
					processed_list_frame.append(things)
					#print ('xxxxxxxxxxxxxxxxxxxxxxxxx')
			#print ('xxxxxxxxxxx  FRAME PROCESSED  xxxxxxxxx\n')

	#print('\n')
	time.sleep(1)
	print("Processing images...\n")
	
	images = driver.find_elements_by_tag_name('img')
	for image in images:
		image_count +=1
		#print ('xxxxxxxxxxxxxxxxxxxxxxxxx')
		out = handle_images(image, image_count)
		try:
			for things in out:
				if things.ident == 1 or things.ident == -1:
					#print("adding to list")
					processed_list_frame.append(things)
				#print ('xxxxxxxxxxxxxxxxxxxxxxxxx\n')
		except:
			#print('skipping')
			pass

	print("items processed: ", len(processed_list_frame))
	    
	oldsrc = 'placeholder'
	for ads in processed_list_frame:
		if ads.ident == 1 and ads.source != oldsrc: #ad_hai
			oldsrc = ads.source
			ad_count += 1
			print("AD number:", ad_count)
			print("AD src:", ads.source)
			print("AD width:", ads.width)
			print("AD height:", ads.height, "\n")
			filename = ads_folder+"/"+str(ad_count)+"_AD_.png"
			r = requests.get(ads.source, stream=True)
			if r.status_code == 200:
				with open(filename, 'wb') as f:
					r.raw.decode_content = True
					shutil.copyfileobj(r.raw, f)
				kind = filetype.guess(filename)
				if kind.extension != "png":
					newname = filename[:-3]+ str(kind.extension)
					os.rename(filename, newname)
		elif ads.ident == -1:
			tracking_pix += 1

	for ads in processed_list_img:
		if ads.ident == 1: #ad_hai
			ad_count += 1
		elif ads.ident == -1:
			tracking_pix += 1

	print("\n\n")
	print("Page load time: ", plt,"s")
	print("Frames found: ", frame_count)
	print("Images found:", len(images))
	print("Ads found: ", ad_count)
	print("1x1 pixels found: ", tracking_pix)
	print("\n\n")

	actual = input("How many ads did you see on screen?\n")
	fp = input("How many false postives?\n")
	try:
		accuracy = round((float(ad_count)/float(actual))*100, 2)
	except:
		accuracy = 100 #round by zero
	print('Accuracy: ', accuracy,'%')
	
	# tor_process.kill()
	# driver.quit()

	csv_file_loc = domain+"/all.csv"
	with open(csv_file_loc, mode='w') as out_file:
		out_writer = csv.writer(out_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
		out_writer.writerow(['Frame Number','Name', 'Ad?', 'ID', 'Title', 'Width', 'Height', 'Source'])
		for ads in processed_list_frame:
			out_writer.writerow([ads.fn, ads.name, ads.ident, ads.eyedee, ads.title, ads.width, ads.height, ads.source])
		out_writer.writerow([''])
		out_writer.writerow(['Frame Number','Name', 'Ad?', 'ID', 'Title', 'Width', 'Height', 'Source'])
		for ads in processed_list_img:
			out_writer.writerow([ads.fn, ads.name, ads.ident, ads.eyedee, ads.title, ads.width, ads.height, ads.source])
		out_writer.writerow([''])
		out_writer.writerow(['PLT','Frame count', 'Image count', 'Ads found', 'Actual Ads', '1x1 found', 'False positives', 'Accuracy'])
		out_writer.writerow([plt, frame_count, len(images), ad_count, actual, tracking_pix , fp, accuracy])	
	out_file.close()

	
