#!/usr/bin/python

from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.model.fv import Tenant
from cobra.mit.request import ConfigRequest

apicUrl = 'https://10.15.254.33'
loginSession = LoginSession(apicUrl, 'admin', 'Cisco321')
moDir = MoDirectory(loginSession)
moDir.login()

uniMo = moDir.lookupByDn('uni')
fvTenantMo = Tenant(uniMo, 'CobraTenant')


cfgRequest = ConfigRequest()
cfgRequest.addMo(fvTenantMo)
moDir.commit(cfgRequest)

