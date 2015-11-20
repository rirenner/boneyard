#!/usr/bin/python

#This script will run on a 9k and push data into a slack webhook

import os
import subprocess
from nxapi_module import *

response = donxapi('cli_show', 'show version')
print response['body']['kickstart_ver_str']
version = response['body']['kickstart_ver_str']
chassis = response['body']['chassis_id']

response = donxapi('cli_show', 'show hostname')
hostname = response['body']['hostname']

outj = "\"Hi, I am " + hostname + ", and I am a " + chassis

cmd = "curl --proxy http://proxy.esl.cisco.com:8080 -X POST --data-urlencode 'payload={ \"channel\": \"#chat9k\", \"username\": \"" + hostname + "\", \"text\": " + outj + "\"}' https://hooks.slack.com/services/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"
print "\n\n\n"
print cmd
print "\n\n\n"
os.system(cmd)
