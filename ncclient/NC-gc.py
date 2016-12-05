#!/usr/bin/env python
import sys
from argparse import ArgumentParser
from ncclient import manager
import xml.dom.minidom
if __name__ == '__main__':

    data = '<rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"> <get-config> <source> <running/> </source> <filter> <native xmlns="http://cisco.com/ns/yang/ned/ios"> <ip> <access-list/> </ip> </native> </filter> </get-config> </rpc>'

    data = '<rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"> <filter> <native xmlns="http://cisco.com/ns/yang/ned/ios"> <ip> <access-list/> </ip> </native> </filter> </rpc>'


    parser = ArgumentParser(description='Select options.')
    # Input parameters
    parser.add_argument('--host', type=str, required=True,
                        help="The device IP or DN")
    parser.add_argument('-u', '--username', type=str, default='cisco',
                        help="Go on, guess!")
    parser.add_argument('-p', '--password', type=str, default='cisco',
                        help="Yep, this one too! ;-)")
    parser.add_argument('--port', type=int, default=830,
                        help="Specify this if you want a non-default port")
    args = parser.parse_args()
    m =  manager.connect(host=args.host,
                         port=args.port,
                         username=args.username,
                         password=args.password,
                         device_params={'name':"csr"})
    # Pretty print the XML reply
    xmlDom = xml.dom.minidom.parseString( str( m.get_config(source=data) ) )
    print xmlDom.toprettyxml( indent = "  " )
