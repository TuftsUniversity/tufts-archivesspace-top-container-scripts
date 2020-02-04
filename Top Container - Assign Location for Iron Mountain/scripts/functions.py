#!/usr/bin/env python3
import sys

import requests
import json
import os
import time
import csv
import datetime
from tkinter.filedialog import askopenfilename
sys.path.append('scripts/')
from functions import *
sys.path.append('secrets/')
import secrets


def assign(tc_id, host, h, log_file, tc_file, success, failure, instance):


    endpoint = host + "/repositories/2/top_containers/" + str(tc_id)
    try:
        print(endpoint + "\n")

        tc = requests.get(endpoint, headers=h)
        tc.encoding = 'utf-8'

        # tc_string  = tc_string.decode('utf-8')
        tc_file.write(tc.text + "\n")


        tc = tc.text

        tc = json.loads(tc)
        print("Before change:\n" + json.dumps(tc) + "\n" )
        print("\n")
        print(type(tc))
        print("\n\n\n")

        location = ""

        if instance == "1":
            location = "3494"

        elif instance == "3":
            location = "3495"
        else:
            location = "Error"
        start_date = datetime.datetime.today().strftime('%Y-%m-%d')
        tc['container_locations'] = [{'jsonmodel_type': 'container_location', 'status': 'current', 'start_date': start_date,
                                 'ref': '/locations/' + location}]




        tc_data = json.dumps(tc)

        print("After change:\n" + json.dumps(tc) + "\n" )


        try:
            post_success = requests.post(endpoint, headers=h, data=tc_data)

            print(str(post_success.text) + "\n")
            post_success_string = post_success.text

            if post_success_string.startswith("{\"error\""):
                failure += 1
                log_file.write(str(tc_id) + "\t\t\t\tFailure\n")
                print(str(tc_id) + "\t\t\t\tFailure\n")

            else:
                log_file.write(str(tc_id) + "\t" + tc['indicator']  + "\t" + tc['barcode'] + "\t" + str(tc['container_locations']) + "\t" + 'Success' + "\n")
                print(str(tc_id) + "\t" + tc['indicator']  + "\t" + tc['barcode'] + "\t" + str(tc['container_locations']) + "\t" + 'Success' + "\n")
                success += 1

        except:
            failure += 1
            log_file.write(str(tc_id) + "\t\t\t\tFailure\n")
            print(str(tc_id) + "\t\t\t\tFailure\n")

    except:
        failure += 1
        log_file.write(str(tc_id) + "\t\t\t\tFailure\n")
        print(str(tc_id) + "\t\t\t\tFailure\n")

    return([success, failure])
