#!/usr/bin/env python3

##  for this to work, you need to pip install lxml, bs4  (Beautful Soup), and html5lib(check this in python3 > help("modules"))
##


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains

import chardet
import csv
import sys
import time


import secrets

import time

import pandas as pd

sys.path.append('scripts/')
from functions_report import *

driver = webdriver.Chrome("c:/Users/hsteel01.TUFTS/chromedriver.exe")

driver.get(secrets.prod_frontend_url)

element = login(driver, secrets.prod_username, secrets.prod_password)

time.sleep(2)
table = navigate_to_tc(driver)

table = table.encode()

print("Encoding:" + str(chardet.detect(table)['encoding']) + "\n" )

table = table.decode('latin1')

# print("\n\n\n" + str(table) + "\n\n\n")
data = pd.read_html(table)

data = data[0]
# print(data)

data.to_excel("Top Container Report from ArchivesSpace Interface.xlsx", index=False)
