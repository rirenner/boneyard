#!/usr/bin/python

from nxapi_module import * 
import json

response = donxapi('cli_show', 'show int mgmt0')
print json.dumps(response['body'], indent=4, sort_keys=True)

