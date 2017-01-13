#!/usr/bin/python

from  acitoolkit.acitoolkit import *
import time
import getpass

apic_ip = '10.95.33.232'
apic_admin = 'admin'
apic_password = getpass.getpass("Password: ") 

def getAllTenants(session):
    tenants = Tenant.get(session)
    tenant_list = []
    for tenant in tenants:
        tenant_list.append((tenant.name,tenant.name))

    return tenant_list


#main

session = Session('https://' + str(apic_ip), str(apic_admin), str(apic_password))
session.login()
print "session is ", session

ten = getAllTenants(session)
print ten

Tenant.subscribe(session)
AppProfile.subscribe(session)
EPG.subscribe(session)
Endpoint.subscribe(session)

while True:
    if EPG.has_events(session):
        event = EPG.get_event(session)
        print event
    time.sleep(0.1)    


