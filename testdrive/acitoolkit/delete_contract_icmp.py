#!/usr/bin/python

# Copyright (c) 2014 Cisco Systems
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import requests
import sys
import json
import getpass

requests.packages.urllib3.disable_warnings()

URL = 'https://10.15.254.33'
LOGIN = 'admin'
PASSWORD = getpass.getpass('Password:')

#login
userJson = {'aaaUser': {'attributes': {'name': LOGIN, 'pwd': PASSWORD } } }
sess = requests.Session()
rsp = sess.post('{0}/api/mo/aaaLogin.json'.format(URL), data=json.dumps(userJson, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)


#Remove contract icmp_contract from App
JsonApp = {"fvAEPg":{"attributes":{"dn":"uni/tn-ACIToolkit/ap-ANP/epg-App","status":"modified"},"children":[{"fvRsCons":{"attributes":{"dn":"uni/tn-ACIToolkit/ap-ANP/epg-App/rscons-icmp_contract","status":"deleted"},"children":[]}}]}}

rsp = sess.post('{0}/api/node/mo/uni/tn-ACIToolkit/ap-ANP/epg-App.json'.format(URL), data=json.dumps(JsonApp, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)

JsonApp = {"fvAEPg":{"attributes":{"dn":"uni/tn-ACIToolkit/ap-ANP/epg-App","status":"modified"},"children":[{"fvRsProv":{"attributes":{"dn":"uni/tn-ACIToolkit/ap-ANP/epg-App/rsprov-icmp_contract","status":"deleted"},"children":[]}}]}}

rsp = sess.post('{0}/api/node/mo/uni/tn-ACIToolkit/ap-ANP/epg-App.json'.format(URL), data=json.dumps(JsonApp, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)




#Remove contract icmp_contract from Web 
JsonWeb = {"fvAEPg":{"attributes":{"dn":"uni/tn-ACIToolkit/ap-ANP/epg-Web","status":"modified"},"children":[{"fvRsCons":{"attributes":{"dn":"uni/tn-ACIToolkit/ap-ANP/epg-Web/rscons-icmp_contract","status":"deleted"},"children":[]}}]}}

rsp = sess.post('{0}/api/node/mo/uni/tn-ACIToolkit/ap-ANP/epg-Web.json'.format(URL), data=json.dumps(JsonWeb, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)

JsonWeb = {"fvAEPg":{"attributes":{"dn":"uni/tn-ACIToolkit/ap-ANP/epg-Web","status":"modified"},"children":[{"fvRsProv":{"attributes":{"dn":"uni/tn-ACIToolkit/ap-ANP/epg-Web/rsprov-icmp_contract","status":"deleted"},"children":[]}}]}}

rsp = sess.post('{0}/api/node/mo/uni/tn-ACIToolkit/ap-ANP/epg-Web.json'.format(URL), data=json.dumps(JsonWeb, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)

#Now delete corresponding Filter
JsonFilter = {"fvTenant":{"attributes":{"dn":"uni/tn-ACIToolkit","status":"modified"},"children":[{"vzFilter":{"attributes":{"dn":"uni/tn-ACIToolkit/flt-icmp_contractICMP","status":"deleted"},"children":[]}}]}}

rsp = sess.post('{0}/api/node/mo/uni/tn-ACIToolkit.json'.format(URL), data=json.dumps(JsonFilter, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)
if rsp.ok:
    print 'Success'
else:
    print 'Failed'
