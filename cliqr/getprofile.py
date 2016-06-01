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
optp.add_option("-d", "--APPID", dest="APPID",
              help="Application ID")
optp.add_option("-v", "--VERSION", dest="VERSION",
              help="Application Version")
opts, args = optp.parse_args()

if opts.IP is None:
     ccm = raw_input("CliQr CCM Address: ")
else:
     ccm = opts.IP

if opts.APPID is None:
     appid = raw_input("Application ID (Can get from getappinfo.py): ")
else:
     appid = opts.APPID

if opts.VERSION is None:
     vers = raw_input("Application Version (Can get from getappinfo.py): ")
else:
     vers = opts.VERSION

if opts.USER is None:
     user = raw_input("Username: ")
else:
     user = opts.USER

if opts.KEY is None:
     key = getpass.getpass("Key: ")
else:
     key = opts.KEY


runcmd = 'curl -s -k -H "Accept:application/json" -H "Content-Type:application/json" -u ' + user + ':' + key +  ' -X GET https://' + ccm + '/v1/apps/' + appid + "?" + "version=" + vers

f = os.popen(runcmd)
result = f.read()
formed = json.loads(result)
print json.dumps(formed, sort_keys=True, indent=4, separators=(',', ': '))
