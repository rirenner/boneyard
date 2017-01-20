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


child = pexpect.spawn('ssh -o "StrictHostKeyChecking no" ' + args.username + '@' + args.host)
child.expect('.*Password:')
child.sendline(args.password)
child.expect('Frazier.*')
child.sendline('conf t')
child.expect('.*#')

# set acl
child.sendline('ip access-list extended ' + acl)
child.expect('.*#')
child.sendline('no permit tcp any host ' + myip + ' eq www')
child.expect('.*#')
child.sendline('no permit tcp host ' + myip + ' eq www any')
child.expect('.*#')
child.sendline('no deny ip any host ' + myip)
child.expect('.*#')
#child.sendline('no deny ip host ' + myip + ' any')
#child.expect('.*#')
child.sendline('exit')
child.expect('.*#')
