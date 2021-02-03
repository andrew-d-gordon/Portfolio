from selenium import webdriver 
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os
import time
import requests
import io
from PIL import Image
import hashlib
from selenium import webdriver  
import datetime

'''Will go and grab specified merchant logos/icons if available,
   Currently stores these images into a folder named imagestest, 
   no masking at the moment (to make look like circles)'''

# Grab Image Source based on specified search and Img.Class tag
def getImageSrcs(search_key:str, css_imgclass:str, driver:webdriver, sleep_between_interactions:float):
  img_srcs = set()

  #send search request to browser
  search_url = "https://www.google.com/search?q={q}&oq={q}&num=1"
  driver.get(search_url.format(q=search_key)) 

  # get desired element (css specified img.class tag), if too long too load/not found, return -1
  try:
    img_tag_object = WebDriverWait(driver, sleep_between_interactions).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, css_imgclass))
    )
  except Exception as e:
    return -1
  finally:
    pass

  img_src = img_tag_object.get_attribute('src')
  return img_src

# Save off images from URL to specified folder
def saveImageFromUrl(src_url:str, folder_path:str, save_name:str):
  try:
      image_content = requests.get(src_url).content

  except Exception as e:
      print(f"ERROR - Could not download {src_url} - {e}")

  try:
      image_file = io.BytesIO(image_content)
      image = Image.open(image_file).convert('RGB')
      file_path = os.path.join(folder_path,save_name+'.png')
      #print("this is file path: ", file_path)
      with open(file_path, 'wb') as f:
          image.save(f, "PNG", quality=85)
      print(f"SUCCESS - saved {src_url} - as {file_path}")
  except Exception as e:
      print(f"ERROR - Could not save {src_url} - {e}")
      return "no_icon"


def startIconScrape(search_key:str, save_name:str): #add driver arg for parallel testing
  # setting up headless chrome driver
  DRIVER_PATH = './chromedriverv86'
  options = Options()  
  options.add_argument("--headless")
  driver = webdriver.Chrome(executable_path=DRIVER_PATH, chrome_options=options)

  #setting search key and html tag to search for
  skey = search_key
  css_imgclass = 'img.DU330c'

  #setting sleep time between browser interactions (e.g. wait for JS to load necessary html divs)
  sleep_time = 0.8

  #init folder to save image off to
  target_path = './scraped_images'
  target_folder = os.path.join(target_path)
  if not os.path.exists(target_folder):
    os.makedirs(target_folder)

  # file name to save img to in target_folder
  file_name = '_'.join(save_name.lower().split(' '))

  #get image source(s)
  result = getImageSrcs(skey, css_imgclass, driver, sleep_time)

  #if result == -1, return fail, else make image, return 0
  if (result==-1):
    return -1

  #save off image(s) to file_name in target_folder
  saveImageFromUrl(result, target_folder, file_name)
  
  #driver.quit()
  return 0


'''
Optional test set, first 3 valid, last invalid:

searchkeytest = ['los pinos santa cruz', 'cafe brasil santa cruz', 'snap taco santa cruz', 'fosters freeze santa cruz']

for sk in searchkeytest:
  res = startIconScrape(sk)
  if res == -1:
    print("Error/img not found on searchkeytest with input:", sk)

'''