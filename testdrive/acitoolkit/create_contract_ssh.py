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
from acitoolkit.acitoolkit import *
import getpass
import requests

#requests.packages.urllib3.disable_warnings()

URL = 'https://10.15.254.33'
LOGIN = 'admin'
PASSWORD = getpass.getpass('Password:')

def send_to_apic(tenant):
    # Login to APIC and push the config
    session = Session(URL, LOGIN, PASSWORD, False)
    session.login()
    resp = session.push_to_apic(tenant.get_url(), data=tenant.get_json())
    if resp.ok:
        print 'Success'
    else:
        print 'Failed'


tenant = Tenant('ACIToolkit')


app = AppProfile('ANP', tenant)
epgWeb = EPG('Web', app)
epgApp = EPG('App', app)

contract = Contract('ssh_contract', tenant)
entry2 = FilterEntry('SSH',
                     applyToFrag='no',
                     arpOpc='unspecified',
                     dFromPort='1',
                     dToPort='65535',
                     etherT='ip',
                     prot='tcp',
                     sFromPort='22',
                     sToPort='22',
                     tcpRules='unspecified',
                     parent=contract)

epgWeb.provide(contract)
epgWeb.consume(contract)
epgApp.consume(contract)
epgApp.provide(contract)

# Dump the necessary configuration
#print 'URL:', tenant.get_url()
#print 'JSON:', tenant.get_json()

send_to_apic(tenant)
