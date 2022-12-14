import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pymongo
from pymongo import MongoClient
import certifi
import time

mongoClient = pymongo.MongoClient(
    "mongodb+srv://<user>:<password>@groupmagt.cgjzv3a.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=certifi.where())  # 要連結到的 connect string
groupMagt = mongoClient["groupMagt"]  # 指定資料庫
images_table = groupMagt['images']

options = Options()
options.add_argument("--disable-notifications")

driver = webdriver.Chrome('./chromedriver', chrome_options=options)

driver.get("https://www.facebook.com/jkflady/photos")

for i in range(250):
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.SPACE)
    time.sleep(2)

first_div = driver.find_elements(
    By.XPATH, "//div[@class='x9f619 x1r8uery x1iyjqo2 x6ikm8r x10wlt62 x1n2onr6']//div[@class='xqtp20y x1n2onr6 xh8yej3']//div[@class='x1qjc9v5 x1q0q8m5 x1qhh985 xu3j5b3 xcfux6l x26u7qi xm0m39n x13fuv20 x972fbf x1ey2m1c x9f619 x78zum5 xds687c xdt5ytf x1iyjqo2 xs83m0k x1qughib xat24cr x11i5rnm x1mh8g0r xdj266r x2lwn1j xeuugli x18d9i69 x4uap5 xkhd6sd xexx8yu x10l6tqk x17qophe x13vifvy x1ja2u2z']//a[@class='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv x1lliihq x5yr21d x1n2onr6 xh8yej3']//img[@class='xzg4506 xycxndf xua58t2 x4xrfw5 x1lq5wgf xgqcy7u x30kzoy x9jhf4c x9f619 x5yr21d xl1xv1r xh8yej3']")

lst = []

for ele in first_div:
    lst.append(ele.get_attribute('src'))

print('lst len')
print(len(lst))

for i in lst:
    images_table.insert_one({
        'tag': 'jkf',
        'src': i,
    })

print('JKF done')
# time.sleep(360)
