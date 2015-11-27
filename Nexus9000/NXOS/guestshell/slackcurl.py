#!/usr/bin/python

import os
import subprocess
from nxapi_module import *

response = donxapi('cli_show', 'show version')
print response['body']['kickstart_ver_str']
version = response['body']['kickstart_ver_str']
chassis = response['body']['chassis_id']
updays = response['body']['kern_uptm_days']
uphrs = response['body']['kern_uptm_hrs']
upmins = response['body']['kern_uptm_mins']

response = donxapi('cli_show', 'show hostname')
hostname = response['body']['hostname']

#outj = "\"Hi, I am " + hostname + ", and I am a " + chassis
outj = "\"Hi, I am " + hostname + ", a " + chassis + ". I have been up for " + str(updays) + " days, " + str(uphrs) + " hours, and " + str(upmins) + " minutes."

cmd = "curl --proxy http://proxy.esl.cisco.com:8080 -X POST --data-urlencode 'payload={ \"channel\": \"#chat9k\", \"username\": \"" + hostname + "\", \"text\": " + outj + "\"}' https://hooks.slack.com/services/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"
print "\n\n\n"
print cmd
print "\n\n\n"
os.system(cmd)
