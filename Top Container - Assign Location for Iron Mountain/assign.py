#!/usr/bin/env python3
################################################################################################
################################################################################################
########
########        Title:      assign.py
########        Author:     Henry Steele - Library Technology Services - Tufts University
########        For:
########        Date:       December 2019
########
########        Purpose:
########            - find top containers with iron mountain barcode, indicated by the
########              following prefixes
########                - IM
########                - RF
########                - ARMS
########              and assign them to location "Offsite"
########
########        Input:
########            - MySQL list of barcodes with these
########            - retrieved with this query
########                - mysql -u libadmin -p -h libarcsdb-dev-01.uit.tufts.edu libarchivesspace -e "select id from top_container where barcode like 'IM%' or barcode like 'RF%' or barcode like 'ARMS%'" > /home/hsteel01/top_containers_in_Iron_Mountain.txt
########        Output:
########            - log file of top containers that were successfully changed,
########              any errors, and counts for successes and errors
########

import sys

import requests
import json
import os
import time
import csv
from tkinter.filedialog import askopenfilename
import importlib

sys.path.append(os.path.relpath('scripts/'))
from functions import *
import secrets



# execfile("./scripts/functions.py")
# execfile("./secrets/secrets.py")

print ("\n\n")
print ("#############################################################################")
print ("#############################################################################")
print ("#######")
print ("#######    This program assigns a location of 'Offsite' to any top container")
print ("#######    with an Iron Mountain barcode, based on an input list from ")
print ("#######    MySQL")
print ("#######")
print ("#############################################################################")
print ("#############################################################################")
print("\n\n")
input("Press 'Enter' to continue ...")

instanceInputInteger = input("\n\nWhat instance to you want to make this change on?\n\n      1) dev-01\n      2) dev-02\n      3) prod\n\nSelect an option: ")


if instanceInputInteger == "1":
	instance = "dev-01"

elif instanceInputInteger == "2":
	instance = "dev-02"

elif instanceInputInteger == "3":
	instance = "prod"

url = ""
hostname = ""

if instanceInputInteger == "1":
	hostname =  secrets.dev_host
	url = secrets.dev_host + "/users/" + secrets.dev_username + "/login?password=" + secrets.dev_password
elif instanceInputInteger == "2":
	hostname = "http://as2.library.tufts.edu:8092"
	url = "http://as2.library.tufts.edu:8092/users/admin/login?password=admin"
elif instanceInputInteger == "3":
	hostname = secrets.prod_host
	url = secrets.prod_host + "/users/" + secrets.prod_username + "/login?password=" + secrets.prod_password

filename = askopenfilename(title = "Select input file of TOP CONTAINER IDs")

top_container_list = []
top_container_counter = 0
success_counter = 0
failure_counter = 0

with open(filename, 'r+') as file:
    for line in file:
        top_container_list.append(line)
        top_container_counter += 1

oDir = "./Output"
if not os.path.isdir(oDir) or not os.path.exists(oDir):
	os.makedirs(oDir)


## establish API session
try:
	auth = requests.post(url).json()

except requests.exceptions.RequestException as e:
	print ("\n\nInvalid URL, try again")
	exit()

	##test authentication

if auth.get("session") == None:
	print ("\n\nWrong username or password! Try Again")
	exit()

else:
	print ("\n\nHello " + auth["user"]["name"])

session = auth["session"]

headers = {'X-ArchivesSpace-Session':session}

log_file = open(oDir + "/Change Log.txt", "w+")

initial_tc_file = open(oDir + "/Top Containers - Initial State.json", "w+")

log_file.write("TC ID\tIndicator\tBarcode\tLocation\tSuccess\n")

for tc_id in top_container_list:
    return_list = assign(tc_id, hostname, headers, log_file, initial_tc_file, success_counter, failure_counter, instanceInputInteger)

    success_counter += return_list[0]
    failure_counter += return_list[1]


print("Number of top container IDs in input file:                " + str(top_container_counter) + "\n")
print("Successful location updates:                              " + str(success_counter) + "\n")
print("Unsucessful location updates - CHECK LOG                  " + str(failure_counter) + "\n")

print("\n\n\n")


log_file.close()
initial_tc_file.close()
