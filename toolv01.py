from bs4 import BeautifulSoup
import re
import pyautogui
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
from PIL import Image

# handle nested iframes

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


STANDARD_SIZES = set(((250, 250), (300, 1050), (160, 600), (728, 90), 
        (300, 600), (970, 90), (234, 60), (125, 125), (300, 250), 
        (120, 240), (120, 90), (180, 160), (300, 100), (970, 250), 
        (120, 60), (550, 480), (468, 60), (336, 280), (88, 31), 
        (240, 400), (180, 150), (120, 600), (720, 300), (976, 40),
        (180, 900), (970, 90)))



def handle_frames(iframe):
	frame = iframe
	#print("This iframe has " , len(iframe_embed) ," embeded iframes in it")
	try:
		image = driver.find_element_by_tag_name("img")	
		print ('image found')
		name = "exists"
	except:
		print ('no image')
		name = "NULL"
	try:
		eyedee = driver.find_element_by_tag_name("id")	
		print ('id tag found')
	except:
		print ('no id')
		eyedee = "NULL"
	try:
		title = driver.find_element_by_tag_name("title")	
		print ('title tag found')
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

	retclass = advert(name, eyedee, title, width, height, source, ad_hai)
	return retclass

def is_it_an_ad(width, height):
    if (width, height) == (1,1):
    	print('tracking pixel')	
    	return -1
    elif (width, height) not in STANDARD_SIZES:
    	print('Not an ad')
    	return 0
    else:
    	print('we has ad')
    	return 1

if __name__ == "__main__":

	chrome_options = Options()
	chrome_options.add_argument("--window-size=1920,1080")


	site = 'https://www.w3schools.com/python/'
	directory = "w3schools/" #Relative to script location
	if not os.path.exists(directory):
	    os.makedirs(directory)

	driver = webdriver.Chrome('/usr/local/bin/chromedriver' , chrome_options=chrome_options)
	driver.get(site)
	time.sleep(5)
	innerHTML = driver.execute_script("return document.body.innerHTML")


	#soup = BeautifulSoup(driver.page_source, 'html.parser')
	#iframes_s = soup.find_all('iframe')
	iframes = driver.find_elements_by_tag_name("iframe")

	#iframe_s_f = open("soupFrames.txt", "w+")
	iframe_d_f = open("driverFrames.txt", "w+")

	frame_count = 0
	ad_count = 0
	tracking_pix = 0
	processed_list = []
	yes = 0

	for frame in iframes:
		yes = 0	
		frame_count +=1
		driver.switch_to.default_content()
		try:
			driver.switch_to.frame(frame)
			yes = 1
		except:
			yes = 0
			print("Not a frame")
		if yes == 1:
			try:
				element = driver.find_element_by_tag_name('img')
				location = element.location
				print('location: ', location)
			except:
				print('location not found')
			iframe_source = driver.page_source
			iframe_d_f.write(iframe_source)
			iframe_d_f.write("****END****\n\n")
			print ('xxxxxxxxxxxxxxxxxxxxxxxxx')
			#print(iframe_source) #returns iframe source
			print('current url: ', driver.current_url) #returns iframe URL
			out = handle_frames(frame)
			if out.ident == 1:
				#open(directory + str(frame_count) + '.png', 'wb').write(driver.save_screenshot)
				size = element.size
				driver.save_screenshot(directory + str(frame_count) + '.png')
				x = location['x'];
				y = location['y'];
				width = location['x']+size['width'];
				height = location['y']+size['height'];
				print('width: ', width, 'height: ', height)
				im = Image.open(directory + str(frame_count) + '.png')
				im = im.crop((int(x), int(y), int(width), int(height)))
				im.save(directory + str(frame_count) + '.png')
			processed_list.append(out)
			print ('xxxxxxxxxxxxxxxxxxxxxxxxx\n\n')
		else:
			print('skipping')

	print("Frames found: ", frame_count)

	for ads in processed_list:
		if ads.ident == 1: #ad_hai
			ad_count += 1
		elif ads.ident == -1:
			tracking_pix +=1
	
	print("Ads found: ", ad_count)
	print("Tracking pixels found: ", tracking_pix)

	pyautogui.hotkey('ctrl', 's')
	time.sleep(1)
	pyautogui.press('tab')
	time.sleep(1)
	pyautogui.press('tab')
	time.sleep(1)
	pyautogui.press('enter')
	print("Saving HTML ...")
	time.sleep(5) 					# time to make sure page downloads
	print("HTML Saved...")


	# iframes_s = soup.find_all('iframe')
	# print (len(iframes_s), ' iframes\n')
	# for frame in iframes_s:
	# 		# print ('xxxxxxxxxxxxxxxxxxxxxxxxx')
	# 		# print (frame)
	# 	iframe_s_f.write(str(frame))
	# 	iframe_s_f.write("****END****\n\n")
	# 	print ('xxxxxxxxxxxxxxxxxxxxxxxxx')
	# 	try:
	# 		if frame.attrs['height'] != 0:
	# 			print ('xxxxxxxxxxxxxxxxxxxxxxxxx')
	# 			print (frame)
	# 			print ('xxxxxxxxxxxxxxxxxxxxxxxxx')
				
	# 			try:
	# 				name = frame.attrs['name']
	# 				print ('name:' , name)
	# 			except:
	# 				print ('no name')
	# 			try:
	# 				source = frame.attrs['src']
	# 				print ('source:' , source)
	# 			except:
	# 				print ('no source')
	# 			try:
	# 				height = frame.attrs['height']
	# 				print ('height:' , height)
	# 			except:
	# 				print ('no height')
	# 			try:
	# 				width = frame.attrs['width']
	# 				print ('width:' , width)
	# 			except:
	# 				print ('no width')

	# 		else:
	# 			print ('ZERO H')	
	# 	except:
	# 		print ('BAD READ')
	# 	print ('xxxxxxxxxxxxxxxxxxxxxxxxx')
	# 	print ('\n')
		# image = frame.attrs['img']
		# print (image)


	# def get_attrs(iframe):
	# 	try:
	# 		name = frame.attrs['name']
	# 		print ('name:' , name)
	# 	except:
	# 		print ('no name')
	# 	try:
	# 		source = frame.attrs['src']
	# 		print ('source:' , source)
	# 	except:
	# 		print ('no source')
	# 	try:
	# 		height = frame.attrs['height']
	# 		print ('height:' , height)
	# 	except:
	# 		print ('no height')
	# 	try:
	# 		width = frame.attrs['width']
	# 		print ('width:' , width)
	# 	except:
	# 		print ('no width')

	#driver.quit()



	# Make a function that takes ifranes and uses soup to find stiff in it 
	# get the dimension of the ads and then use the existing list ot check if it is an ad ornah
	# use pyautogui to save the ads as jpeg, but how do we tag them tehn?
	# save iframe attricutes in a neat usable manner for further classification
	# find a ocr lobrary to get text from ads and sort them by languagess
	# sift through iframes files 


	# img_tags = soup.find_all('img')

	# urls = [img['src'] for img in img_tags]

	# for url in urls:
	#     filename = re.search(r'/([\w_-]+[.](jpg|gif|png))$', url)

	#     with open(os.path.join(directory, filename.group(1)), 'wb') as f:
	#         if 'http' not in url:
	#             url = '{}{}'.format(site, url)
	#         response = requests.get(url)
	#         f.write(response.content)

	# images = driver.find_elements_by_tag_name('img')
	# for image in images:
	#     print(image.get_attribute('src'))

	# for link in soup.find_all('a', href=True):
	#     print(link['href'])
