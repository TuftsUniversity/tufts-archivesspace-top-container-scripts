#!/usr/bin/env python3
import sys

import requests
import json
import os
import time
import csv
import re
from tkinter.filedialog import askopenfilename
import importlib

# sys.path.append(os.path.relpath('scripts/'))
# from functions import *
import secrets

import pandas as pd
import numpy as np



# execfile("./scripts/functions.py")
# execfile("./secrets/secrets.py")

print ("\n\n")
print ("#############################################################################")
print ("#############################################################################")
print ("#######")
print ("#######    This program assigns container profiles to a list of top ")
print ("#######    containers you provide in an input file ")
print ("#######    The input file should be an Excel document containing two columns: ")
print ("#######    ")
print ("#######         - barcode")
print ("#######         - container_profile")
print ("#######")
print ("#######    The container profile is the container profile URI")
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


log_file = open(oDir + "/Container Profile Assignment - Change Log.txt", "w+")
initial_top_container_records_file = open(oDir + "/Initial Top Containers.json", "w+")



log_file.write("Status\tTop container ID\tBarcode\tInitial Container Profile\tUpdated Container Profile\n")
df = pd.read_excel(filename, dtype={'barcode': str})
barcode_list = df['barcode'].tolist()

list_2D = df.to_numpy().tolist()


error_count = 0
success_count = 0
x = 0
for barcode, uri in list_2D:

    if x <= 10:
        x += 1
        continue
    if x > 15:
        break
    print('Barcode: ' + barcode + '; URL: ' + uri + '\n')
    try:
        top_container_search_results = requests.get(hostname + '/repositories/2/search?page=1&filter={"query":{"jsonmodel_type":"boolean_query","op":"AND","subqueries":[{"jsonmodel_type":"field_query","field":"primary_type","value":"top_container","literal":true},{"jsonmodel_type":"field_query","field":"barcode_u_sstr","value":"' + str(barcode) + '","literal":true}]}}', headers=headers).json()
    except:
        error_count += 1
        x += 1
        log_file.write('Could not connect to ASpace API at barcode ' + str(barcode) + '\t\t\t\t\n')
        continue

    if "error" in top_container_search_results:
         error_count += 1
         x += 1
         log_file.write('Search for ' + barcode + 'is incorrectly formatted\t\t\t\t\n')
         continue
    else:
        #print("\nGot into else loop\n")
        if top_container_search_results['total_hits'] == 1:
            #print("\nGot one search result\n")
            #print("\n\n" + top_container_search_results['results'][0]['json'] + "\n\n")
            initial_top_container = top_container_search_results['results'][0]['json']

            initial_top_container_records_file.write("\n" + initial_top_container + "\n")

            initial_top_container = json.loads(initial_top_container)
            #print("\n" + initial_top_container['barcode'] + "\n")

            matchObj = re.search(r'\/(\d+)$', initial_top_container['uri'])
            id = matchObj.group(1)

            #print("\n\nID: " + str(id) + "\n\n")
            try:

                full_top_container_record = requests.get(hostname + '/repositories/2/top_containers/  ' + str(id), headers=headers).json()
            #   result_2 =                  requests.get(hostname + '/repositories/2/top_containers/  ' + str(id), headers=headers).json()
                 #print("\ngot real record \n")

                original_profile = ""

                if 'container_profile' in full_top_container_record:
                    original_profile = full_top_container_record['container_profile']['ref']

                updated_profile = {'ref': uri}

                full_top_container_record['container_profile']  = updated_profile
                # print("\ngot barcode\n")
                updated_top_container_string = json.dumps(full_top_container_record)
            except:
                error_count += 1
                x += 1
                log_file.write('Could not retrieve real top container record for ' + barcode + '.\t\t\t\t\n')
                continue


            try:
                #print("\nGot into post try clause\n")
                requests.post( hostname + '/repositories/2/top_containers/  ' + str(id), headers=headers, data=updated_top_container_string).json()
                #requests.post(host_name + "/repositories/2/" + apiType + "/" + str(recordID), headers=head,    data=resource_data).json()
                print('posted\n')
                result_2 = requests.get(hostname + '/repositories/2/top_containers/  ' + str(id), headers=headers).json()

                # updated_posted_barcode = result_2['barcode']
                #print("\n\n" + str(updated_posted_barcode))
                print("get updated file\n")
                log_file.write('Success\t' + str(id) + '\t' + barcode + '\t' + original_profile + '\t' + updated_profile['ref'] + '\n')
                print("write to log")
                # log_file.write("Status\tTop container ID\tBarcode\tInitial Container Profile\tUpdated Container Profile\n")
                #print('\nwrote log file\n')
                success_count += 1
                #log_file.write("Status\tTop container ID\tInitial Barcode\tChanged To Barcode\n")
                #print(json.dumps(result_2))
            except:
                error_count += 1
                x += 1
                log_file.write('Could not post result.\t\t\t\t\n')
                continue
            #print("\n" + id + "\n")

            #print("\n" + str(type(initial_top_container)) + "\n")




        elif top_container_search_results['total_hits'] == 0:
            error_count += 1
            x += 1
            log_file.write('Search for ' + barcode + ' produced no results\t\t\t\t\n')
            continue
        elif top_container_search_results['total_hits'] > 1:
            error_count += 1
            x += 1
            log_file.write('Search for ' + barcode + ' produced no more than one result. Ambiguous.\t\t\t\t\n')
            continue

    x += 1

print("Success Count:                  " + str(success_count))
print("Error Count:                    "  + str(error_count))
log_file.close()
initial_top_container_records_file.close()
#print("\n\n" + str(top_container_search_results) + "\n\n")
