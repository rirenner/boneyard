#!/usr/bin/python

import os
import json
import getpass
from optparse import OptionParser
import requests
import sys

requests.packages.urllib3.disable_warnings()

# Gather CLI and interactive input options
optp = OptionParser()
optp.add_option("-i", "--IP", dest="IP",
             help="IP address of CCM to connect to")
optp.add_option("-u", "--USER", dest="USER",
              help="Username")
optp.add_option("-k", "--KEY", dest="KEY",
              help="API Key")
opts, args = optp.parse_args()

if opts.IP is None:
     ccm = raw_input("CliQr CCM Address: ")
else:
     ccm = opts.IP

if opts.USER is None:
     user = raw_input("Username: ")
else:
     user = opts.USER

if opts.KEY is None:
     key = getpass.getpass("Key: ")
else:
     key = opts.KEY


runcmd = 'curl -s -k -H "Accept:application/json" -H "Content-Type:application/json" -u ' + user + ':' + key +  ' -X GET https://' + ccm + '/v1/jobs/'

f = os.popen(runcmd)
result = f.read()
formed = json.loads(result)

for i in formed['jobs']:
    g = i['deploymentInfo']
    if type(g).__name__=='dict':
        print i['name'] + " : " + g['deploymentStatus']
    else:
        print i['name']
