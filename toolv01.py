from bs4 import BeautifulSoup
import re
import pyautogui
import csv
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import sys
import time
from PIL import Image

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
	def __init__(self, name, eyedee, title, width, height, source, ident):
		super(advert, self).__init__()
		self.name = name
		self.eyedee = eyedee
		self.title = title
		self.width = width
		self.height = height
		self.source = source
		self.ident = ident

def handle_images(frame):
	try:
		eyedee = frame.get_attribute("class")	
		print ('class tag found')
	except:
		print ('no class')
		eyedee = "NULL"
	try:
		title = frame.get_attribute("alt")	
		print ('alt tag found')
	except:
		print ('no alt')
		title = "NULL"
	try:
		width = frame.get_attribute("width")
		print ('width:' , width)
	except:
		print ('no width')
		width = "NULL"
	try:
		height = frame.get_attribute("height")
		print ('height:' , height)
	except:
		print ('no height')
		height = "NULL"
	try:
		source = frame.get_attribute("src")	
		print ('source:' , source)
	except:
	 	print ('no source')
	 	source = "NULL"

	name = "exists"
	ad_hai = is_it_an_ad(width, height)

	retclass = advert(name, eyedee, title, width, height, source, ad_hai)
	return retclass

def handle_frames(iframe, iframe_source):
	frame = iframe
	retclassList = []
	try:
		images = driver.find_elements_by_tag_name("img")
		print (len(images), ' images found in iframe')
	except:
		print ('no image')
	for image in images:	
		name = "exists"
		try:
			eyedee = image.get_attribute("id")	
			print ('id: ', eyedee)
		except:
			print ('no id')
			eyedee = "NULL"
		try:
			title = image.get_attribute("title")	
			print ('title: ', title)
		except:
			print ('no title')
			title = "NULL"
		try:
			width = int(image.get_attribute("width"))	
			print ('width:' , width)
		except:
			print ('no width')
			width = "NULL"
		try:
			height = int(image.get_attribute("height"))
			print ('height:' , height)
		except:
			print ('no height')
			height = "NULL"
		try:
			source = image.get_attribute("src")	
			print ('source:' , source)
		except:
		 	print ('no source')
		 	source = "NULL"

		ad_hai = is_it_an_ad(width, height)
		retclassList.append(advert(name, eyedee, title, width, height, source, ad_hai))
		print("xxxxxxxxxxxx inner loop xxxxxxxxxxxxx\n")
	
	reg_ret = use_regex(iframe_source)
	retclassList.append(reg_ret)

	return retclassList


def use_regex(iframe):
	frame = str(iframe)
	pattern =  ';img(.*?)/&gt'
	src_pattern = '(?<=src=")(.*?)(?=")'
	w_pattern = '(?<=width=")(.*?)(?=")'
	h_pattern = '(?<=height=")(.*?)(?=")'
	
	matches = re.findall(pattern,frame)
	print("testing using regex")
	try:
		src = re.search(src_pattern, str(matches))
		width = int(re.search(w_pattern, str(matches)).group(0))
		height = int(re.search(h_pattern, str(matches)).group(0))
		print("src:", src.group(0))
		print("w:", width)
		print("h:", height)
		
		ad_hai = is_it_an_ad(width, height)
		
		ret = advert('regex_ad', 'eyedee', 'title', width, height, src.group(0), ad_hai)
		if ad_hai:
			print("reg ad found")
			# print(matches)
		else:
			print("reg: not ad")
	except:
		print("reg_ad failed")
		ret = advert('F_regex_ad', 'eyedee', 'title', 'width', 'height', 'src', 0)

	return ret

def is_it_an_ad(width, height):
    if (width, height) in BEACON_SIZES:
    	print('web beacon')	
    	return -1
    elif (width, height) not in STANDARD_SIZES:
    	print('Not an ad')
    	return 0
    else:
    	print('we has ad')
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

if __name__ == "__main__":

	chrome_options = Options()
	chrome_options.add_argument("--window-size=1920,1080")


	#site = 'https://www.w3schools.com/python/'
	site = 'https://www.espncricinfo.com'


	driver = webdriver.Chrome('/usr/local/bin/chromedriver' , chrome_options=chrome_options)
	print ("Starting Chrome...")
	driver.get(site)
	time.sleep(5)
	
	scroll_page(driver) # scroll the pafe
	time.sleep(2)
	#innerHTML = driver.execute_script("return document.body.innerHTML") # this runs when the page is fully loaded, we dont need it, just use it to make sure that we save the complete page

	frame_count = 0
	image_count = 0
	ad_count = 0
	tracking_pix = 0
	processed_list_frame = []
	processed_list_img = []
	yes = 0
	emb = 0

	iframes = driver.find_elements_by_tag_name("iframe")
	print("Processing iframes\n")
	for frame in iframes:
		yes = 0
		frame_count +=1
		driver.switch_to.default_content()
		try:
			driver.switch_to.frame(frame)
			print("Frame found")
			yes = 1
		except:
			yes = 0
			print("Not a frame")
		try:
			embed_frames = frame.find_elements_by_tag_name("iframe")
			emb = 1
			print("embed_frames found")
		except:
			print("no embed_frames")
			emb = 0

		if yes == 1 and emb == 1:
			for emb_fram in embed_frames:
				out = handle_frames(emb_fram)
				if out.ident == 1 or out.ident == -1:
					print("adding to list")
					processed_list_frame.append(things)

			iframe_source = driver.page_source
			output_f = "driverFrames" + str(frame_count)+ ".txt"
			iframe_d_f = open(output_f, "w+")
			iframe_d_f.write(iframe_source)
			iframe_d_f.close()
			#print(iframe_source)
			print ('xxxxxxxxxxxx PROCESSING FRAME', frame_count, 'xxxxxxxxxxx')
			#print('current url: ', frame.get_attribute("src")) #returns iframe URL
			out = handle_frames(frame)
			for things in out:
				if things.ident == 1 or things.ident == -1:
					print("adding to list")
					processed_list_frame.append(things)
				print ('xxxxxxxxxxxxxxxxxxxxxxxxx\n')
		elif yes == 1 and emb == 0:
			iframe_source = driver.page_source
			output_f = "driverFrames" + str(frame_count)+ ".txt"
			iframe_d_f = open(output_f, "w+")
			iframe_d_f.write(iframe_source)
			iframe_d_f.close()
			#print(iframe_source)
			print ('xxxxxxxxxxxx PROCESSING FRAME', frame_count, 'xxxxxxxxxxx')
			#print('current url: ', frame.get_attribute("src")) #returns iframe URL
			out = handle_frames(frame, iframe_source)
			for things in out:
				if things.ident == 1 or things.ident == -1:
					print("adding to list")
					processed_list_frame.append(things)
					print ('xxxxxxxxxxxxxxxxxxxxxxxxx')
			print ('xxxxxxxxxxx  FRAME PROCESSED  xxxxxxxxx\n')
			# else:
			# 	print('skipping')


	print('\n')
	time.sleep(1)
	print("Processing images\n")
	
	images = driver.find_elements_by_tag_name('img')
	for image in images:
		image_count +=1
		print ('xxxxxxxxxxxxxxxxxxxxxxxxx')
		out = handle_images(frame)
		try:
			for things in out:
				if things.ident == 1 or things.ident == -1:
					print("adding to list")
					processed_list_frame.append(things)
				print ('xxxxxxxxxxxxxxxxxxxxxxxxx\n')
			else:
				print('skipping')
		except:
				print('skipping')

	print('\n\n')

	print("items processed: ", len(processed_list_frame))
	    
	oldsrc = 'shit'
	#print(len(processed_list_frame))
	for ads in processed_list_frame:
		#output = str(ads.ident) + " " + str(ads.name) + " " + str(ads.eyedee) + " " + str(ads.title) + " " + str(ads.width) + " " + str(ads.height) + " " + str(ads.source)   
		#print("yes")
		if ads.ident == 1 and ads.source != oldsrc: #ad_hai
			oldsrc = ads.source
			ad_count += 1
			print("AD number:", ad_count)
			print("AD src:", ads.source)
			print("AD width:", ads.width)
			print("AD height:", ads.height, "\n")

		elif ads.ident == -1:
			tracking_pix +=1

	# oldsrc = 'shit'
	# print("\n \n")
	# #print(len(processed_list_frame))
	# for ads in processed_list_frame:
	# 	#output = str(ads.ident) + " " + str(ads.name) + " " + str(ads.eyedee) + " " + str(ads.title) + " " + str(ads.width) + " " + str(ads.height) + " " + str(ads.source)   
	# 	#print("yes")
	# 	if ads.ident == 1: #and ads.source != oldsrc: #ad_hai
	# 		#oldsrc = ads.source
	# 		ad_count += 1
	# 		print("AD number:", ad_count)
	# 		print("AD src:", ads.source)
	# 		print("AD width:", ads.width)
	# 		print("AD height:", ads.height, "\n")

	# 	elif ads.ident == -1:
	# 		tracking_pix +=1


	for ads in processed_list_img:
		#output = str(ads.ident) + " " + str(ads.name) + " " + str(ads.eyedee) + " " + str(ads.title) + " " + str(ads.width) + " " + str(ads.height) + " " + str(ads.source)   
		#print(output)
		#print("yesir")	
		if ads.ident == 1: #ad_hai
			ad_count += 1
		elif ads.ident == -1:
			tracking_pix +=1

	
	print("\n\n")
	print("Frames found: ", frame_count)
	#print("Images found:", len(images))
	print("Ads found: ", ad_count)
	print("Tracking pixels found: ", tracking_pix)
	print("\n\n")

	# print("Saving data ...")
	# outfile_loc = directory+"_output.txt"
	# resultFile = open(outfile_loc,'w+')
	# output = "Identity Name ID Title Width Height Source"   
	# resultFile.write(output)
	# for ads in processed_list:
	# 	output = str(ads.ident) + " " + str(ads.name) + " " + str(ads.eyedee) + " " + str(ads.title) + " " + str(ads.width) + " " + str(ads.height) + " " + str(ads.source)   
	# 	#print(output)
	# 	resultFile.write(output)
	# print("Data saved ...")

	# pyautogui.hotkey('ctrl', 's')
	# time.sleep(1)
	# pyautogui.press('tab')
	# time.sleep(1)
	# pyautogui.press('tab')
	# time.sleep(1)
	# pyautogui.press('enter')
	# print("Saving HTML ...")
	# time.sleep(5) 					# time to make sure page downloads
	# print("HTML Saved...")
