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
#
# This script dumps out top level tenant information from ACI

import requests
import sys
import json
import logging
import getpass
import time 
import calendar 
from optparse import OptionParser

# Gather CLI and interactive input options
optp = OptionParser()
optp.add_option("-i", "--IP", dest="IP",
             help="IP address of APCI to connect to")
optp.add_option("-u", "--USER", dest="USER",
              help="Username")
optp.add_option("-p", "--PASS", dest="PASS",
              help="Password")
optp.add_option("-r", "--HOST", dest="HOST",
              help="SCP Host")
optp.add_option("-d", "--DIR", dest="DIR",
              help="SCP Directory")
optp.add_option("-s", "--SUSER", dest="SUSER",
              help="SCP Username")
optp.add_option("-t", "--SPASS", dest="SPASS",
              help="SCP Password")
opts, args = optp.parse_args()

if opts.IP is None:
     apic = raw_input("APIC IP Address: ")
else:
     apic = opts.IP

if opts.USER is None:
     user = raw_input("APIC Username: ")
else:
     user = opts.USER

if opts.PASS is None:
     password = getpass.getpass("APCI Password: ")
else:
     password = opts.PASS

if opts.HOST is None:
     host = raw_input("SCP Host Address: ")
else:
     host = opts.HOST

if opts.DIR is None:
     dir = raw_input("SCP Directory: ")
else:
     dir = opts.DIR

if opts.SUSER is None:
     suser = raw_input("SCP Username: ")
else:
     suser = opts.SUSER

if opts.SPASS is None:
     spass = raw_input("SCP Password: ")
else:
     spass = opts.SPASS

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

jtime = calendar.timegm(time.gmtime())
jtime = 0

userJson = {'aaaUser': {'attributes': {'name': user, 'pwd': password } } }

sess = requests.Session()

rsp = sess.post('https://{0}/api/mo/aaaLogin.json'.format(apic), data=json.dumps(userJson, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)

userJson = {"fileRemotePath": { "attributes": { "dn": 'uni/fabric/path-autoconf{0}'.format(jtime), "remotePort": "22", "name":'autoconf{0}'.format(jtime), "host": host, "protocol": "scp", "remotePath": dir, "userName": suser, "userPasswd": spass, "rn": 'path-autoconf{0}'.format(jtime)}, "children": [{ "fileRsARemoteHostToEpg": {"attributes": { "tDn": "uni/tn-mgmt/mgmtp-default/oob-default"}, "children":[]}}]}}
rsp = sess.post('https://{0}/api/node/mo/uni/fabric/path-autoconf{1}.json'.format(apic, jtime), data=json.dumps(userJson, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)
print rsp.content

userJson = {"configExportP": { "attributes": { "dn": 'uni/fabric/configexp-autoconf{0}'.format(jtime), "name": 'autoconf{0}'.format(jtime), "adminSt": "triggered", "rn": 'configexp-autoconf{0}'.format(jtime)}, "children": [{ "configRsExportDestination": {"attributes": {"tnFileRemotePathName": 'autoconf{0}'.format(jtime)}, "children":[]}}]}}
rsp = sess.post('https://{0}/api/node/mo/uni/fabric/configexp-autoconf{1}.json'.format(apic, jtime), data=json.dumps(userJson, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)
print rsp.content
