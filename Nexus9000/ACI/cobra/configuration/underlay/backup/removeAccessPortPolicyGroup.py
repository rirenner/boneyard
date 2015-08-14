from cobra.model.infra import AccPortGrp, RsHIfPol, RsCdpIfPol, RsLldpIfPol, RsStpIfPol, RsMonIfInfraPol, RsAttEntP, ConnNodeS, HConnPortS, ConnNodeBlk, RsConnPortS, ConnPortBlk

from createMo import *

DEFAULT_POLICY = None

CHOICES = []


def input_key_args(msg='\nPlease Specify Port Policy Group:'):
    print msg
    return input_raw_input("Port Policy Group Name", required=True)


def input_interface():
    return input_raw_input('Interface (eg: 1/14, 1/13-15, 101/13-15)', required=True)


def input_connectivity_filter(msg='Please specify the Connectivity Filters:'):
    print msg
    args = {}
    args['switch_id'] = input_raw_input('Switch IDs', required=True)
    args['interfaces'] = read_add_mos_args(add_mos('Add an Interface', input_interface))
    return args


def input_optional_args():
    args = {}
    args['link_level'] = input_raw_input("Link Level Policy", default=DEFAULT_POLICY)
    args['cdp'] = input_raw_input("CDP Policy", default=DEFAULT_POLICY)
    args['lldp'] = input_raw_input("LLDP Policy", default=DEFAULT_POLICY)
    args['stp_interface'] = input_raw_input("STP Interface Policy", default=DEFAULT_POLICY)
    args['monitoring'] = input_raw_input("Monitoring Policy", default=DEFAULT_POLICY)
    args['entity_profile'] = input_raw_input("Attached Entity Profile", default=DEFAULT_POLICY)
    if args['entity_profile'] != '' and args['entity_profile'] is not None:
        args['connectivity_filters'] = read_add_mos_args(add_mos('Add a Connectivity Filter', input_connectivity_filter))
    return args


def remove_access_port_port_policy_group(infra_funcprof, group_name, **args):
    """Remove an Access Port Policy Group. The interface policy group. This enables you to specify the interface policies you want to use. """
    args = args['optional_args'] if 'optional_args' in args.keys() else args

    infra_accportgrp = AccPortGrp(infra_funcprof, group_name)
    infra_accportgrp.delete()


class CreateAccessPortPortPolicyGroup(CreateMo):

    def __init__(self):
        self.description = 'Create an Access Port Policy Group. The interface policy group. This enables you to specify the interface policies you want to use. '
        self.group = None
        super(CreateAccessPortPortPolicyGroup, self).__init__()

    def set_cli_mode(self):
        super(CreateAccessPortPortPolicyGroup, self).set_cli_mode()
        self.parser_cli.add_argument('group', help='Group Name.')
        self.parser_cli.add_argument('-L', '--link_level', default= DEFAULT_POLICY, help='The physical interface policy name. A relation to the host interface policy.')
        self.parser_cli.add_argument('-c', '--cdp', default= DEFAULT_POLICY, help='The CDP policy name. A relation to the CDP Interface Policy.')
        self.parser_cli.add_argument('-l', '--lldp', default= DEFAULT_POLICY, help='The LLDP policy name. A relation to the LLDP policy parameters for the interface.')
        self.parser_cli.add_argument('-s', '--stp_interface', default= DEFAULT_POLICY, help='The STP policy name. A relation to the spanning-tree protocol (STP) policy.')
        self.parser_cli.add_argument('-m', '--monitoring', default= DEFAULT_POLICY, help='The monitoring policy name. A relation to the monitoring policy model.')
        self.parser_cli.add_argument('-e', '--entity_profile', default= DEFAULT_POLICY, help='The Entity Profile name. A relation to the attached entity profile.')
        self.parser_cli.add_argument('-I', '--switch_id', default= DEFAULT_POLICY, help='Switch ID.')
        self.parser_cli.add_argument('-i', '--interfaces', default= DEFAULT_POLICY, help='Interfaces.')

    def read_key_args(self):
        self.group = self.args.pop('group')

    def wizard_mode_input_args(self):
        self.args['group'] = input_key_args()
        if not self.delete:
            self.args['optional_args'] = input_optional_args()

    def delete_mo(self):
        self.check_if_mo_exist('uni/infra/funcprof/accportgrp-', self.group, AccPortGrp, description='Access Port Policy Group')
        super(CreateAccessPortPortPolicyGroup, self).delete_mo()

    def main_function(self):
        self.look_up_mo('uni/infra/funcprof/', '')
        remove_access_port_port_policy_group(self.mo, self.group, optional_args=self.optional_args)


if __name__ == '__main__':
    mo = CreateAccessPortPortPolicyGroup()


