#!/usr/bin/env python
#
# Copyright (C) 2014-2015 Cisco Systems Inc.
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
# This is to get Domains, VLAN pools, AEPs, Port and Switch profiles
# and to show summary of those information
#
# Written by Toru Okatsu @ Cisco Systems, August 13th 2014
#

import argparse
import re
import cobra.mit.access
import cobra.mit.session
import sys
import logging
import getpass
import requests
from optparse import OptionParser

requests.packages.urllib3.disable_warnings()

# This is the abstract class to store ACI mo
class AbsBaseObj:
    def __init__(self, mo):
        self.mo = mo
        self.tDn = None

    @property
    def name(self):
        return self.mo.name

    def get_mo(self):
        return self.mo


class AbsRangeObj(AbsBaseObj):
    def __init__(self, mo):
        AbsBaseObj.__init__(self, mo) 
        self.list = []
        self.tDn = None

    @property
    def list(self):
        return self.list

    @property
    def tDn(self):
        return self.tDn

    @tDn.setter
    def tDn(self, tDn):
        self.tDn = tDn


# This class is to store the vlan pool information
class VlanPool(AbsRangeObj):
    def add_range(self, mo):
        first_id = getattr(mo, 'from')
        first_id = first_id.strip("vlan-")
        last_id = mo.to
        last_id = last_id.strip("vlan-")
        if first_id == last_id:
            range = first_id
        else:
            range = first_id + "-" + last_id
        self.list.append(range)


# This class is to store the node profile information
class Node(AbsRangeObj):
    def add_range(self, mo):
        first_id = mo.from_
        last_id = mo.to_
        if first_id == last_id:
            range = first_id
        else:
            range = first_id + "-" + last_id
        self.list.append(range)

# This class is to store the interface profile information
class IfProf(AbsRangeObj):
    def add_range(self, mo):
        first_id = mo.fromCard + "/" + mo.fromPort
        last_id = mo.toCard + "/" + mo.toPort
        if first_id == last_id:
            range = first_id
        else:
            range = first_id + "-" + last_id
        self.list.append(range)


# Get Tenant and EPG information from infraRtDomAtt.tDn
def dn_to_epg(dn):
    m = re.search('/tn-(.+)/ap-.+/epg-(.+)', str(dn))
    if m:
        return m.group(1) + ':' + m.group(2)
    else:
        return None

def getCredentials():
    creds ={}
    # Gather CLI and interactive input options
    optp = OptionParser()
    optp.add_option("-i", "--IP", dest="IP",
             help="IP address to connect to")
    optp.add_option("-u", "--USER", dest="USER",
              help="Username")
    optp.add_option("-p", "--PASS", dest="PASS",
              help="Password")
    opts, args = optp.parse_args()

    if opts.IP is None:
         creds['url']='https://' + raw_input("IP Address: ")
    else:
         creds['url']='https://' + opts.IP

    if opts.USER is None:
         creds['user'] = raw_input("Username: ")
    else:
         creds['user'] = opts.USER

    if opts.PASS is None:
         creds['password'] = getpass.getpass("Password: ")
    else:
         creds['password'] = opts.PASS

    return creds



# Main function 

creds = getCredentials()

# Login to the APIC and create the directory object

ls = cobra.mit.session.LoginSession(creds['url'], creds['user'], 
                                    creds['password'],
                                    secure=False, timeout=180) 
md = cobra.mit.access.MoDirectory(ls)
md.login()

# Get Node Profiles
q = cobra.mit.request.ClassQuery('uni/' + 'infraNodeP')
q.subtree = 'full'
mos = md.query(q)

nodes = {}
for mo in mos:
    node = Node(mo)
    for leaf in  mo.leaves:
        for node_blk in leaf.nodeblk:
            node.add_range(node_blk) 
    nodes[mo.dn] = node

# Get Interface Profiles
q = cobra.mit.request.ClassQuery('uni/' + 'infraAccPortP')
q.subtree = 'full'
q.subtreeClassFilter = ['infraRtAccPortP', 'infraHPortS', 'infraPortBlk']
mos = md.query(q)

if_profs = {}
for mo in mos:
    for rtaccportps in mo.rtaccPortP:
        tDn = rtaccportps.tDn
        for hport in  mo.hports:
            if_prof = IfProf(mo)
            if_prof.tDn = tDn
            for portblk in hport.portblk:
                if_prof.add_range(portblk)
            if_profs[hport.dn] = if_prof

# Get Interface Policy Groups
q = cobra.mit.request.ClassQuery('uni/' + 'infraAccPortGrp')
q.subtree = 'children'
q.subtreeClassFilter = 'infraRtAccBaseGrp'
mos = md.query(q)

if_pol_groups = {}
for mo in mos:
    if_pol_groups[mo.dn] = mo

# Get AEP information
q = cobra.mit.request.ClassQuery('uni/' + 'infraAttEntityP')
q.subtree = 'children'
q.subtreeClassFilter = 'infraRtAttEntP'
mos = md.query(q)

aeps = {}
for mo in mos:
    aeps[mo.dn] = mo

# Get vlan pools
q = cobra.mit.request.ClassQuery('uni/' + 'fvnsVlanInstP')
q.subtree = 'children'
q.subtreeClassFilter = 'fvnsEncapBlk'
mos = md.query(q)

vlan_pools = {}
for mo in mos:
    vlan_pool =  VlanPool(mo)
    for child in mo.children:
        vlan_pool.add_range(child)
    vlan_pools[mo.dn] = vlan_pool

# Get Domain information
# l3extDomP, physDomP, l2extDomP, vmmDomP
class_list = ('l3extDomP', 'physDomP', 'l2extDomP', 'vmmDomP') 
for cl in class_list:
    q = cobra.mit.request.ClassQuery('uni/' + cl)
    q.subtreeClassFilter = ['infraRsVlanNs', 'infraRtDomP','infraRtDomAtt']
    q.subtree = 'full'
    domains = md.query(q)

    for domain in domains:
        print "DOMAIN: {:20s}  TYPE: {:10s}".format(domain.name, cl)

        for child in domain.rtfvDomAtt:
            tDn = child.tDn
            print "    EPG:      {:30s}".format(dn_to_epg(tDn))

        for child in domain.rsvlanNs:
            tDn = child.tDn
            if vlan_pools.has_key(tDn):
                vlan_info = ""
                for vlan in vlan_pools[tDn].list:
                    vlan_info = vlan_info + " " + vlan
                print "    VLAN:     {:20s} {:s}".format(
                        vlan_pools[tDn].name, vlan_info)

        for child in domain.rtdomP:
            tDn = child.tDn
            if aeps.has_key(tDn):
                print "    AEP:      {:20s}".format(aeps[tDn].name)
                for child2 in aeps[tDn].rtattEntP:
                    tDn2 = child2.tDn
                    if if_pol_groups.has_key(tDn2):
                        print "    IF_POL_G: {:20s}".format(
                                if_pol_groups[tDn2].name)
                        for child3 in if_pol_groups[tDn2].rtaccBaseGrp:
                            tDn3 = child3.tDn
                            if if_profs.has_key(tDn3):
                                tDn4 = if_profs[tDn3].tDn
                                if nodes.has_key(tDn4):
                                    node_info = " "
                                    for node in nodes[tDn4].list:
                                        node_info = node_info + " " + node
                                    print "      NODE:     {:20s} {:s}".format(
                                            nodes[tDn4].name, node_info)
                                port_info = ""
                                for port in if_profs[tDn3].list:
                                    port_info = port_info + " " + port
                                print "      IF_PROF:  {:20s} {:s}".format(
                                        if_profs[tDn3].name, port_info)
        print
