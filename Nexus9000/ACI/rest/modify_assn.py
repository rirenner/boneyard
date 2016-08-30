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
from optparse import OptionParser

# Gather CLI and interactive input options
optp = OptionParser()
optp.add_option("-i", "--IP", dest="IP",
             help="IP address of APIC to connect to")
optp.add_option("-u", "--USER", dest="USER",
              help="Username")
optp.add_option("-p", "--PASS", dest="PASS",
              help="Password")
opts, args = optp.parse_args()

if opts.IP is None:
     apic = raw_input("APIC IP Address: ")
else:
     apic = opts.IP

if opts.USER is None:
     user = raw_input("Username: ")
else:
     user = opts.USER

if opts.PASS is None:
     password = getpass.getpass("Password: ")
else:
     password = opts.PASS

#import requests.packages.urllib3
#requests.packages.urllib3.disable_warnings()

if len(sys.argv) < 2:
  tofile = ""
else:
  tofile = sys.argv[1]

userJson = {'aaaUser': {'attributes': {'name': user, 'pwd': password } } }

sess = requests.Session()

rsp = sess.post('https://{0}/api/mo/aaaLogin.json'.format(apic), data=json.dumps(userJson, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)

#https://10.96.98.150:8443/api/node/mo/uni/tn-Test/BD-Client_Network/rsctx.json
#{"fvRsCtx":{"attributes":{"tnFvCtxName":"Common_VRF"},"children":[]}}
userJson = {"fvRsCtx": {"attributes": {"tnFvCtxName": "Common_VRF"}, "children":[] } }
rsp = sess.post('https://{0}/api/mo/uni/tn-Test/BD-Client_Network/rsctx.json'.format(apic), data=json.dumps(userJson, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)

#https://10.96.98.150:8443/api/node/mo/uni/tn-Test/BD-Client_Network.json
#{"fvBD":{"attributes":{"dn":"uni/tn-Test/BD-Client_Network","status":"modified"},"children":[{"fvRsBDToOut":{"attributes":{"dn":"uni/tn-Test/BD-Client_Network/rsBDToOut-L3_OUT_Test","status":"deleted"},"children":[]}}]}}
userJson = {"fvBD":{"attributes":{"dn":"uni/tn-Test/BD-Client_Network","status":"modified"},"children":[{"fvRsBDToOut":{"attributes":{"dn":"uni/tn-Test/BD-Client_Network/rsBDToOut-L3_OUT_Test","status":"deleted"},"children":[]}}]}}
rsp = sess.post('https://{0}/api/mo/uni/tn-Test/BD-Client_Network.json'.format(apic), data=json.dumps(userJson, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)


#https://10.96.98.150:8443/api/node/mo/uni/tn-Test/BD-Client_Network.json
#{"fvRsBDToOut":{"attributes":{"tnL3extOutName":"L3_OUT_Common","status":"created"},"children":[]}}
userJson = {"fvRsBDToOut":{"attributes":{"tnL3extOutName":"L3_OUT_Common","status":"created"},"children":[]}}
rsp = sess.post('https://{0}/api/mo/uni/tn-Test/BD-Client_Network.json'.format(apic), data=json.dumps(userJson, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)
