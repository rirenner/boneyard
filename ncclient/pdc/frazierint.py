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

print "host: ", args.host
print "username: ", args.username

#child = pexpect.spawn('/usr/bin/ssh ' + args.username + '@' + args.host, timeout=300)
child = pexpect.spawn('/usr/bin/ssh cisco@10.95.33.203')
child.expect('.*Password:.*')
child.sendline(args.password)
child.expect('Frazier.*')

#Enter config mode
child.sendline('conf t')
child.expect('.*#')

child.sendline('int g1/0/3')
child.expect('.*#')
child.sendline('shut')
child.expect('.*#')


child.sendline('int g1/0/4')
child.expect('.*#')
child.sendline('shut')
child.expect('.*#')

child.expect('end')
