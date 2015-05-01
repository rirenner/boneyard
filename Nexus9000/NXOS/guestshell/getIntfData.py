#!/usr/bin/python

from nxapi_module import * 

response = donxapi('cli_show', 'show int mgmt0')
intf = ['body']
print response['body']['TABLE_interface']['ROW_interface']

name = intf['interface']
pkts_in = intf['vdc_lvl_in_pkts']
bytes_in = intf['vdc_lvl_in_bytes']
pkts_out = intf['vdc_lvl_out_pkts']
bytes_out = intf['vdc_lvl_out_bytes']

outter = "\n interface:\t" + name + ",\n packets_in:\t" + str(pkts_in)
outter += ",\n bytes_in:\t" + str(bytes_in) + ",\n packets_out:\t"
outter += str(pkts_out) + ",\n bytes_out:\t" + str(bytes_out) + ""

print outter + "\n";
