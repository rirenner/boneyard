#!/usr/bin/python
#
# Copyright (C) 2015 Cisco Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This script dumps out top level tenant information from ACI

import requests
import sys
import json

userJson = {'aaaUser': {'attributes': {'name': 'admin', 'pwd': 'Cisco321' } } }

sess = requests.Session()

rsp = sess.post('https://10.15.254.33/api/mo/aaaLogin.json', data=json.dumps(userJson, sort_keys=True, indent=4, separators=(',', ': ')), verify=False)

rsp = sess.get('https://10.15.254.33/api/mo/uni/tn-TenantVM.json', data=json.dumps(userJson, sort_keys=True, indent=4, separators=(',', ':')), verify=False)
formed = json.dumps(json.loads(rsp.content), indent=4, sort_keys=True) 

print formed
