#!/usr/bin/python

from nxapi_module import * 

response = donxapi('cli_show', 'show hostname')
print response['body']['hostname']

