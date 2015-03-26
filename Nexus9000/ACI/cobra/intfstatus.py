#!/usr/bin/env python
#
# Written by Mike Timm @ cisco System, March 2014
# Revised by Toru Okatsu @ Cisco Systems, June 11th 2014
# Copyright (c) 2014-2015 by cisco Systems, Inc.
# All rights reserved.


# list of packages that should be imported for this code to work
import re
import cobra.mit.access
import cobra.mit.session
import sys
import logging
import getpass
import requests
from optparse import OptionParser

requests.packages.urllib3.disable_warnings()


 
# get an interface name and an index 
# the index is slot_id * 200 + port_id
# assume one slot has no more than 200 ports
def getIfName(intf):
    # phy interface name is like phys-[eth1/98]
    name = None
    idx = None

    match = re.search('\[(eth\d+/\d+)\]', str(intf.dn))
    if match:
        name = match.group(1)
        match = re.search('(\d+)/(\d+)', name)
        if match:
            idx = 200*int(match.group(1)) + int(match.group(2))

    return name, idx 

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


########
# Main #
########

creds = getCredentials()

ls = cobra.mit.session.LoginSession(creds['url'], creds['user'], creds['password'], secure=False, timeout=180) 
md = cobra.mit.access.MoDirectory(ls)

md.login()

# Get the list of pods

pods = md.lookupByClass("fabricPod", parentDn='topology')
for mo in pods:
    print "name = {}".format(mo.rn)

for pod in pods:

    # Get nodes under one pod
    dn = pod.dn
    nodes = md.lookupByClass("fabricNode", parentDn=dn)
    for node in nodes:
        print "Node: {:10s} Name: {:10s} Role: {:10s}".format(node.rn, node.name, node.role)

    for node in nodes:
        # Skip APICs and unsupported switches
        if node.role == 'controller' or node.fabricSt != 'active':
             continue

        print "\nNode Name: " + node.name

        # l1PhysIf has the name of interface and admin status
        # ethpmPhysIf has the operation status
        dn = str(node.dn) + '/sys'
        intfs = md.lookupByClass("l1PhysIf", parentDn=dn) 
        pmifs = md.lookupByClass("ethpmPhysIf", parentDn=dn)

        iftable = {}
        for intf in intfs:
            name, idx = getIfName(intf)
            if name and idx:
                iftable[idx] = [name, intf.adminSt, "Unknown"]
        for intf in pmifs:
            name, idx = getIfName(intf)
            if name and idx:
                list = iftable[idx]
                list[2] = intf.operSt
                iftable[idx] = list

        # print the interface status
        for idx, list in sorted(iftable.items()):
            print list[0], list[1], list[2]

