#!/usr/bin/env python3



##########################################################################################
##########################################################################################
####
####
####    Editor:           Henry Steele, Library Technology Services, Tufts University
####    Name of Program:  publishNotes.py
####    Date created:     2019-07
####    Dependent Programs:
####
####    Author:           Rockefeller ArchiveSpace
####    File:             asReplaceContainers.py
####    Source:           https://github.com/RockefellerArchiveCenter/scripts
####
####    Author:           "ucancallmealicia"
####    File:             create_top_containers.py
####    Source:           https://github.com/ucancallmealicia/archivesspace-collection-control-toolbox/tree/master/top_containers
####
####    Purpose:
####    Given a list of new barcodes and data for desired new top containers, as well
####    as the old top container info, create new top containers, and replace old the top container
####    in the arhival object instance with the new one
####
####    The pur;ose of this script is mostly to call the other two, and to record the purpose for which
####    I've refactored the other two scripts
####
####    Input (from create_top_containers.py):
####    A CSV containing new container, old container, locations, and container profile information, in this order, headerless:
####        - new top container barcode
####        - indicator
####        - New top container profile URI
####        - new location URI" as "location
####        - old top container URI
####        - CUID
####        - AO URI
####        - (from original test CSV. Test to make sure I have everything):  New top container barcode,New top container URI (doesn't exist yet),Old top container barcode,Old top container URI,Indicator,Location barcode,Location URI,CUID,AO URI,New top container profile URI
####
####    Output (from create_top_containers.py):
####        - file in a "Processing folder" containing the new top container URI in the first column,
####          and the old top container URI in the second column.
####        - This is used by the replace script
####
####    Input (from asReplaceContainers.py):
####        - output file from last script
####        - column 1 as new ("keep") top container URIs
####        - column 2 as old ("replace") top container URIs
####    Output (from asReplaceContainers.py):
####        - A log of archival object CUIDs, and the container that was replaced for it, and the new contianer
####          to which it was moved
####    Still to do 2019-07-27:
####        - I will have a list of the CUID from the input CSV, so I know which archival objects
####          I'm dealing with
####        - But I need to parse out the resource number from these lists for the existing scripts I'm using
####        - I also need to determine if these scripts are pulling all archival objects from a resource,
####          because I actually only need the ones listed
##########################################################################################
##########################################################################################
import requests
import json
import getpass
import pprint
import csv


import datetime
import os
import sys

sys.path.append('secrets')
import secrets

# from Tkinter import Tk
# Python 2
from tkFileDialog import askopenfilename

# Python 3

# from tkinter import filedialog

# def login (api_url, username, password):
#     '''This function logs into the ArchivesSpace REST API returning an acccess token'''
#     auth = requests.post(api_url+'/users/'+username+'/login?password='+password).json()
#     session = auth["session"]
#     headers = {'X-ArchivesSpace-Session':session}
#     return headers
#
# if __name__ == '__main__':
#     api_url = input('Please enter the URL for the ArchivesSpace API: ')
#     username = getpass.getuser()
#     check_username = input('Is your username ' + username + '?: ')
#     if check_username.lower() not in ('y', 'yes', 'yep', 'you know it'):
#         username = input('Please enter ArchivesSpace username:  ')
#     password = getpass.getpass(prompt=username + ', please enter your ArchivesSpace Password: ', stream=None)
#     print('Logging in', api_url)
#     headers = login(api_url, username, password)
#     if headers != '':
#         print('Success!')
#     else:
#         print('Ooops! something went wrong')




# Python 2
instanceInputInteger = raw_input("\n\nWhat instance to you want to retrieve records for?\n\n      1) dev-01\n      2) dev-02\n      3) prod\n\nSelect an option: ")

# Python 3
# instanceInputInteger = input("\n\nWhat instance to you want to retrieve records for?\n\n      1) dev-01\n      2) dev-02\n      3) prod\n\nSelect an option: ")



if instanceInputInteger == "1":
	instance = "dev-01"

elif instanceInputInteger == "2":
	instance = "dev-02"

elif instanceInputInteger == "3":
	instance = "prod"

print ("\nInstance: " + str(instance))

if instanceInputInteger != "1" and instanceInputInteger != "2" and instanceInputInteger != "3":
	print ("\nUnknown instance.  Try again.")
	quit()

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

#NOTE - top containers don't actually hold info about linked records, these are related through the top container reference
#in the archival objects themselves. Thus, 2 different things have to happen here. First, the script creates top containers
#which are not linked to anything, and then another operation links those top containers to archival objects. Unfortunately
#this linking operation has to use a different script, because

# Python 2
input_csv = askopenfilename(title = "Select input CSV file")

# Python 3
# input_csv = filedialog.askopenfilename(title = "Select input CSV file")


print("\nInput CSV: " + input_csv + "\n")

csvfile = open(input_csv, 'r+')
txtout = open(oDir + "/Replace and Keep Containers " + datetime.datetime.today().strftime("%Y-%m-%d %H_%M_%S") + ".txt", 'w+')
txtout.write("POST Status, Keep Container URI, Replace Container URI, Archival Object URI\n")
#
csvin = csv.reader(csvfile, delimiter = ',')
next(csvin, None)

"%Y-%m-%d %H:%M:%S"
for row in csvin:
    print("Row: " + str(row) + "\n")

    barcode = row[0]
    indicator = row[1]
    container_profile_uri = row[2]
    locations = row[3]
    start_date = datetime.datetime.today().strftime('%Y-%m-%d')
    repo_num = row[4]
    old_tc_uri = row[5]
    ao_uri = row[6]

    print("Row: Barcode: " + str(barcode) + "; Indicator: " + str(indicator) + "; Container Profile URI: " + container_profile_uri + "; locations: " + locations + "; Start Date: " + start_date + "; Repo Number: " + repo_num + "; Old top container URI: " + old_tc_uri + "; Archival Object URI: " + ao_uri + "\n" )

    if barcode != '':
        create_tc = {'barcode': barcode, 'container_profile': {'ref': container_profile_uri}, 'indicator': indicator,
                     'container_locations': [{'jsonmodel_type': 'container_location', 'status': 'current', 'start_date': start_date,
                                              'ref': locations}],
                     'jsonmodel_type': 'top_container', 'repository': {'ref': repo_num}}
    else:
        create_tc = {'container_profile': {'ref': container_profile_uri}, 'indicator': indicator,
                     'container_locations': [{'jsonmodel_type': 'container_location', 'status': 'current', 'start_date': start_date,
                                              'ref': locations}],
                     'jsonmodel_type': 'top_container', 'repository': {'ref': repo_num}}
    tcdata = json.dumps(create_tc)

    print("\nTC Data: \n" + tcdata + "\n" )
    try:
        tcupdate = requests.post(hostname + '/repositories/2/top_containers', headers=headers, data=tcdata).json()
    except:
        txtout.write("Error" + "," + "No top container created" + "," + old_tc_uri + "," + ao_uri + "\n")
        continue
    print(tcupdate)

    try:
        txtout.write(tcupdate['status'] + "," + tcupdate['uri'] + "," + old_tc_uri + "," + ao_uri + "\n")
    except:
        txtout.write("Error" + "," + "No top container created" + "," + old_tc_uri + "," + ao_uri + "\n")
    # for key, value in tcupdate.items():
    #     if key == 'status':
    #         txtout.write(str(key) + " " + str(value) + ", ")
    #     if key == 'uri':
    #         txtout.write(str(key) + " " + str(value) + ", ")
    #     if key == 'error':
    #         txtout.write(str(key) + " " + str(value) + ", ")
    #     txtout.write(old_tc_uri + ", ")
    #     txtout.write(ao_uri + '\n')
txtout.close()


print('All Done!')
