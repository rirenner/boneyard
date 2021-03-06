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

allowedip = os.environ.get('allowedip')
if allowedip == None:
    print "allowed env is empty"
    sys.exit()

if vlan == '104':
    if acl != 'pdc':
        print "Error: acl must be pdc when vlan is 104"
        sys.exit(1)

print "vlan:", vlan, " acl:", acl, " myip:", myip, " allowedip:", allowedip


child = pexpect.spawn('ssh -o "StrictHostKeyChecking no" ' + args.username + '@' + args.host)
child.expect('.*Password:')
child.sendline(args.password)
child.expect('Frazier.*')

#get acl
child.sendline('show run | section ip access-list extended pdc')
data = ""
returned = child.readline(size=-1)
while 'permit ip any any' not in returned:
    data += returned
    returned = child.readline(size=-1)
lister = data.split('\r\n');
lister.pop()
lister.pop(0)
lister.pop(0)

#Enter config mode
child.sendline('conf t')
child.expect('.*#')

# set vlan
child.sendline('vlan ' + vlan)
child.expect('.*#')
child.sendline('exit')
child.expect('.*#')

# set access-map
child.sendline('vlan access-map ' + acl + ' 10')
child.expect('.*#')
child.sendline('match ip address ' + acl)
child.expect('.*#')
child.sendline('action forward')
child.expect('.*#')
child.sendline('exit')
child.expect('.*#')

# set vlan filter
child.sendline('vlan filter ' + acl + ' vlan-list ' + vlan)
child.expect('.*#')

# set acl
child.sendline('no ip access-list extended ' + acl)
child.expect('.*#')
child.sendline('ip access-list extended ' + acl)
child.expect('.*#')
child.sendline('permit tcp host ' + allowedip + ' host ' + myip + ' eq www')
child.expect('.*#')
child.sendline('permit tcp host ' + myip + ' eq www host ' + allowedip)
child.expect('.*#')
child.sendline('deny ip any host ' + myip)
child.expect('.*#')
child.sendline('deny ip host ' + myip + ' any')
child.expect('.*#')
for line in lister:
    print "sending in ", line
    child.sendline(line)
    child.expect('.*#')

child.sendline('permit ip any any')
child.expect('.*#')
child.sendline('exit')
child.expect('.*#')
