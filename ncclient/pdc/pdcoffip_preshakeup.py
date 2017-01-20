#!/usr/bin/python

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import pexpect
import sys
import os
from argparse import ArgumentParser

parser = ArgumentParser(description='Select options.')
# Input parameters
parser.add_argument('--host', type=str, default='10.95.33.203',
                    help="The device IP or DN")
parser.add_argument('-u', '--username', type=str, default='cisco',
                    help="Go on, guess!")
parser.add_argument('-p', '--password', type=str, default='cisco',
                    help="Yep, this one too! ;-)")
args = parser.parse_args()


vlan = os.environ.get('vlan')
if vlan == None:
    print "vlan env is empty"
    sys.exit()

acl = os.environ.get('acl')
if acl == None:
    print "acl env is empty"
    sys.exit()

myip = os.environ.get('CliqrTier_LoadBalancer_PUBLIC_IP')
if myip == None:
    print "myip env is empty"
    sys.exit()

print "vlan:", vlan, " acl:", acl, " myip:", myip

child = pexpect.spawn('ssh -o "StrictHostKeyChecking no" cisco@10.15.254.159')
child.expect('.*Password:')
child.sendline('cisco')
child.expect('Frazier.*')
child.sendline('conf t')
child.expect('.*#')

# remove vlan
child.sendline('no vlan ' + vlan)
child.expect('.*#')

# remove access-map
child.sendline('no vlan access-map ' + acl + ' 10')
child.expect('.*#')

# remove vlan filter
child.sendline('no vlan filter ' + acl + ' vlan-list ' + vlan)
child.expect('.*#')

# remove acl
child.sendline('no ip access-list extended ' + acl)
child.expect('.*#')
