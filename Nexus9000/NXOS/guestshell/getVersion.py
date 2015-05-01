#!/usr/bin/python

from nxapi_module import * 

response = donxapi('cli_show', 'show version')
print response['body']['kickstart_ver_str']

