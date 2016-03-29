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
from toolkit_helper import *

import requests
import sys
import json
import getpass

URL = 'https://10.15.254.33'
LOGIN = 'admin' 
PASSWORD = getpass.getpass('Password:')

# Create a tenant
tenant = Tenant('ACIToolkit')

# Create a Context (vrf)
context = Context('vrfToolkit', tenant)
context.set_allow_all(False)

#Create a bridge domain
bd = BridgeDomain('bdToolkit', tenant)
bd.add_context(context)
gateway = Subnet('gateway',bd)
gateway.set_addr('10.20.10.1/24')
bd.add_subnet(gateway)


# Create an ANP and an EPG
app = AppProfile('ANP', tenant)
epg = EPG('App', app)

sess = Session(URL, LOGIN, PASSWORD, False)
sess.login()


#epgdomain = EPGDomain.get_by_name(sess, 'Linux_VLAN_50')
#epg.add_infradomain(epgdomain)

# Attach the EPG to interfaces using VLAN 55 as the encap
#if1 = Interface('eth','1','105','1','15')
#l2if = L2Interface('eth 1/105/1/15', 'vlan', '55')
#l2if.attach(if1)
#epg.attach(l2if)
epg.add_bd(bd)


# Dump the necessary configuration
#print 'URL:', tenant.get_url()
#print 'JSON:', tenant.get_json()

send_to_apic(tenant, URL, LOGIN, PASSWORD)


# Now lets make the ports untagged:
#mark_port_untagged(tenant, app, epg, '1/105/1/15', URL, LOGIN, PASSWORD)


