#!/usr/bin/env python

import requests
import json
import sys
import logging
import pandas


import datetime
import os

sys.path.append('secrets')
import secrets

# Python 2
from tkFileDialog import askopenfilename

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

log_file = open(oDir + "/Replace Container Log " + datetime.datetime.today().strftime("%Y-%m-%d %H_%M_%S") + ".txt", 'w+')

# column_names = ['status', 'keep_uri', 'replace_uri', 'ao_uri']
data = pandas.read_csv(input_csv)

data = data.set_axis(['status', 'keep_uri', 'replace_uri', 'ao_uri'], axis='columns', inplace=False)

print("Dataframe: \n" + str(data) + "\n")

replace_containers = data.replace_uri.tolist()
keep_containers = data.keep_uri.tolist()
ao_uris = data.ao_uri.tolist()



x = 0

print("Row count of data frame: " + str(len(data)) + "\n")

while x < len(data):
	keep_uri = data.iloc[x]['keep_uri']
	replace_uri  = data.iloc[x]['replace_uri']
	ao_uri = data.iloc[x]['ao_uri']

	try:
		ao = requests.get(hostname + ao_uri, headers=headers).json()
		for instance in ao['instances']:
			if ('sub_container' in instance):
				if instance['sub_container']['top_container']['ref'] == replace_uri:
					instance['sub_container']['top_container']['ref'] = keep_uri

					post = requests.post(hostname + ao_uri, headers=headers, data=json.dumps(ao))
					if(post.status_code == requests.codes.ok):
						print('Container ' + replace_uri + ' was replaced with container ' + keep_uri + ' in archival object ' + ao_uri + "\n")
						log_file.write('Container ' + replace_uri + ' was replaced with container ' + keep_uri + ' in archival object ' + ao_uri + "\n")
					else:
						print('ERROR replacing ' + replace_uri + ' with' + keep_uri + ' in archival object ' + ao_uri + ".  Follow up or replace manually.  \n")
						log_file.write('ERROR replacing ' + replace_uri + ' with' + keep_uri + ' in archival object ' + ao_uri + ".  Follow up or replace manually.  \n")
				else:
					print("Input file URI " + replace_uri + " doesn't match the top container URI referenced in the archival object record " +  str(instance['sub_container']['top_container']['ref']) + ".\n")
					log_file.write("Input file URI " + replace_uri + " doesn't match the top container URI referenced in the archival object record " +  str(instance['sub_container']['top_container']['ref']) + ".\n")
	except:
		print("Archival object URI in Replace and Keep Containers is invalid: " + str(ao_uri) + "\n")
		log_file.write("Archival object URI in Replace and Keep Containers is invalid: " + str(ao_uri) + "\n")


	x += 1

log_file.close()
