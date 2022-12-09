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
    "mongodb+srv://andy:acdwsx321@groupmagt.cgjzv3a.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=certifi.where())  # 要連結到的 connect string
groupMagt = mongoClient["groupMagt"]  # 指定資料庫
images_table = groupMagt['images']

options = Options()
options.add_argument("--disable-notifications")

driver = webdriver.Chrome('./chromedriver', chrome_options=options)

driver.get("https://www.jkforum.net/forum-1112-1.html")

lst = []

for page in range(1, 23):
    driver.get(f"https://www.jkforum.net/forum-1112-{page}.html")
    try:
        for i in range(40):
            time.sleep(2)
            driver.find_elements(
                By.XPATH, "//ul[@id='waterfall']//div[@class='c cl']//a")[i].click()
            img = driver.find_elements(By.XPATH, "//ignore_js_op//img")
            for j in img:
                lst.append(j.get_attribute('src'))
            print(len(lst))
            driver.back()
    except:
        pass


print('lst len')
print(len(lst))

for i in lst:
    images_table.insert_one({
        'tag': 'jkf_girls',
        'src': i,
    })

print('JKF done')
