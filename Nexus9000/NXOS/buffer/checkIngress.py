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
# ./checkIngress.py -h
#
# If you do not enter command line options, it will interactively prompt
# for input. Password will be hidden in interactive input.
# Sample run without entering password on CLI:
#
# /checkIngress.py -i 1.1.1.1 -u admin
# Password:
# Switch 
#
# Note this script uses the requests library which can be brought in
# through the python package manager "pip".
#
# This script will check buffer depth queues for an interface.

import requests
import json
import sys
import logging
import getpass
import re
from optparse import OptionParser

# Gather CLI and interactive input options
optp = OptionParser()
optp.add_option("-i", "--IP", dest="IP",
             help="IP address to connect to")
optp.add_option("-u", "--USER", dest="USER",
              help="Username")
optp.add_option("-p", "--PASS", dest="PASS",
              help="Password")
optp.add_option("-x", "--XFC", dest="XFC",
              help="Interface")
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

if opts.XFC is None:
     interface = raw_input("Interface: ")
else:
     interface = opts.XFC

m = re.search(".*\/(\d+)", interface)
if m:
    #print "Found this: ", m.groups()[0]
    eoq = int(m.groups()[0]) - 1
    #print "EOQ: ", eoq
    cmd = "show hardware internal ns buffer info pkt-stats detail | grep 'EOQ " + str(eoq) + " :'" 
    #print "cmd is: ", cmd
else:
    print "Incorrect Interface format found."
    print "Valid input samples: Ethernet1/5  Eth1/5  1/5"
    sys.exit(0)


# Setup JSON for show version
myheaders={'content-type':'application/json'}
payload={
  "ins_api": {
    "version": "1.0",
    "type": "cli_show_ascii",
    "chunk": "0",
    "sid": "1",
    "input": cmd, 
    "output_format": "json"
  }
}

#print "payload is ", payload 

#Send payload to network element, and print response
response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(user,passer)).json()
#print "Response:"
#print response['ins_api']['outputs']['output']['body']
data=response['ins_api']['outputs']['output']['body']
m = re.search("\[.*\]\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", data)
if m:
    print "DROP:\t", m.groups()[0]
    print "NODROP:\t", m.groups()[1]
    print "SPAN:\t", m.groups()[2]
    print "SUP:\t", m.groups()[3]
 
