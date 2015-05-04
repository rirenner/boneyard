#!/usr/bin/python
import httplib, json, sys, time

def post_aaa_auth( mgmt_ip, user_name = "xxx", pwd = "xxx" ):
    payload = { "aaaUser" : { "attributes" : { "name" : user_name, "pwd" : pwd }}}
    headers = {"Content-type": "application/json", "Accept": "text/plain"}

    url = "http://{0}/api/aaaLogin.json".format( mgmt_ip )
    conn = httplib.HTTPConnection( mgmt_ip )
    conn.request( 'POST', url, json.dumps( payload ), headers )

    response = conn.getresponse()
    print response

    if response.status == 200:
        return response.getheader( 'set-cookie' )
    else:
        return None

def config_using_rest( cookie, mgmt_ip, data ):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Cookie': cookie }

    conn = httplib.HTTPConnection( mgmt_ip )

    for i in xrange( len( data )):
        if i == 2:
            time.sleep( 3 )

        url = "http://{0}/api/mo/{1}".format( mgmt_ip, data[i][0] )
        conn.request( 'POST', url, json.dumps( data[i][1] ), headers )

        response = conn.getresponse()

        print url
        print "Response data  :", response.read()
        print

if __name__ == "__main__":

    data = [
      ( 'sys/bgp.json',
                         { "bgpEntity": { "attributes": {}}}),
      ( 'sys/bgp/inst.json',
                         { "bgpInst": { "attributes": { "asn": "200" }}}),
      ( 'sys/bgp/inst/dom-default.json',
                         { "bgpDom": { "attributes": { "name": "default", "rtrId":"10.10.10.12" }}}),
      ( 'sys/bgp/inst/dom-default/peer-[10.10.10.11].json',
                         { "bgpPeer": { "attributes": { "addr": "10.10.10.11", "asn": "100" }}}),
      ( 'sys/bgp/inst/dom-default/peer-[10.10.10.11]/af-ipv4-ucast.json',
                         { "bgpPeerAf": { "attributes": { "type": "ipv4-ucast" }}}),
      ( 'sys/bgp/inst/dom-default/af-ipv4-ucast.json',
                         { "bgpDomAf": { "attributes": { "type": "ipv4-ucast" }}}),
      ( 'sys/bgp/inst/dom-default/af-ipv4-ucast/prefix-[100.100.0.0/16].json',
                         { "bgpAdvPrefix": { "attributes": { "addr": "100.100.0.0/16" }}}),
      ( 'sys/bgp/inst/dom-default/af-ipv4-ucast/prefix-[168.10.10.0/24].json',
                         { "bgpAdvPrefix": { "attributes": { "addr": "168.10.10.0/24" }}}),
      ( 'sys/bgp/inst/dom-default/af-ipv4-ucast/prefix-[192.0.0.0/8].json',
                         { "bgpAdvPrefix": { "attributes": { "addr": "192.0.0.0/8" }}})
    ]

    mgmt_ip = 'xxx.xxx.xxx.xxx'
    cookie = post_aaa_auth( mgmt_ip, 'xxx', 'xxx' )
    if cookie == None:
        print "Unable to authenticate."
        sys.exit(1)
    config_using_rest( cookie, mgmt_ip, data )

