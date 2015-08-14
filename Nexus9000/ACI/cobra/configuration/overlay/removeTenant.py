#!/usr/bin/env python

from createMo import *


def input_key_args(msg='\nPlease Specify the Tenant:'):
    print msg
    return input_raw_input("Tenant Name", required=True)


def remove_tenant(parent_mo, tenant):
    """Remove a tenant"""
    fv_Tenant = Tenant(parent_mo, tenant)
    fv_Tenant.delete()


class RemoveTenant(CreateMo):
    """
    Remove a Tenant
    """
    def __init__(self):
        self.description = 'Remove a Tenant'
        self.tenant_required = True
        super(RemoveTenant, self).__init__()

    def delete_mo(self):
        self.check_if_mo_exist('uni/tn-', self.tenant, Tenant, description='Tenant')
        super(RemoveTenant, self).delete_mo()

    def main_function(self):
        self.mo = self.modir.lookupByDn('uni')
        remove_tenant(self.mo, self.tenant)

if __name__ == '__main__':
    mo = RemoveTenant()
