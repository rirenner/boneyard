#!/usr/bin/python
#
# Copyright (C) 2015 Cisco Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0 
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script can be run with the help option to print command line help:
#
# ./deleteVlan.py -h
#
# If you do not enter command line options, it will interactively prompt
# for input. Password will be hidden in interactive input.
# Sample run without entering password on CLI:
#
# /deleteVlan.py -i 1.1.1.1 -u admin -v 30
# Password:
#
# Note this script uses the requests library which can be brought in
# through the python package manager "pip".

import requests
import json
import sys
import logging
import getpass
from optparse import OptionParser

# Gather CLI and interactive input options
optp = OptionParser()
optp.add_option("-i", "--IP", dest="IP",
             help="IP address to connect to")
optp.add_option("-u", "--USER", dest="USER",
              help="Username")
optp.add_option("-p", "--PASS", dest="PASS",
              help="Password")
optp.add_option("-v", "--vlan", dest="VLAN",
              help="Vlan ID")
opts, args = optp.parse_args()

if opts.IP is None:
     url='http://' + raw_input("IP Address: ") + '/ins'
else:
     url='http://' + opts.IP + '/ins'

if opts.USER is None:
     user = raw_input("Username: ")
else:
     user = opts.USER

if opts.PASS is None:
     passer = getpass.getpass("Password: ")
else:
     passer = opts.PASS

if opts.VLAN is None:
     vlan = raw_input("VLAN Id: ")
else:
     vlan = opts.VLAN


# Setup JSON-RPC for vlan config 
myheaders={'content-type':'application/json-rpc'}
payload=[
  {
    "jsonrpc": "2.0",
    "method": "cli",
    "params": {
      "cmd": "conf t",
      "version": 1
    },
    "id": 1
  },
  {
    "jsonrpc": "2.0",
    "method": "cli",
    "params": {
      "cmd": "no vlan " + vlan,
      "version": 1
    },
    "id": 2
  },
]

response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(user,passer)).json()
