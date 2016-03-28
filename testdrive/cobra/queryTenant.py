#!/usr/bin/python

from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.model.fv import Tenant
from cobra.mit.request import DnQuery

apicUrl = 'https://10.15.254.33'
loginSession = LoginSession(apicUrl, 'admin', 'Cisco321')
moDir = MoDirectory(loginSession)
moDir.login()

tenant1Mo = moDir.lookupByClass("fvTenant", propFilter='and(eq(fvTenant.name, "CobraTenant"))')

print(tenant1Mo)
