import sys
import os
import os.path
import json
import argparse
import urllib2
import urllib
import httplib
import socket

class UHTTPConnection(httplib.HTTPConnection):
    """Subclass of Python library HTTPConnection that uses a unix-domain socket.
    """

    def __init__(self, path):
        httplib.HTTPConnection.__init__(self, 'localhost')
        self.path = path

    def connect(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.path)
        self.sock = sock


def do_delete(url):

    request = urllib2.Request(url)
    request.get_method = lambda: 'DELETE'
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        response = opener.open(request)
    except urllib2.HTTPError as e:
        raise
    return response

def do_get(url):

    request = urllib2.Request(url)
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        raise
    return response

def do_post(url, data):

    request = urllib2.Request(url, data)
    response = None
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        raise
    return response

def do_post_sock(sock, url, data):

    conn = UHTTPConnection(sock)
    # The Cookie and Content-Type headers are a must.
    #headers={'content-type':'application/json'}
    headers = {"Cookie": "nxapi_auth=admin:local", "Content-Type":"application/json"}
    conn.request("POST", url, data, headers)
    response = conn.getresponse()
    return response.read()


def donxapi( type, input):

    if not os.path.exists("/tmp/nginx_local/nginx_1_be_nxapi.sock"):
        print "feature nxapi does not appear to be enabled"
        sys.exit(0)

    url="/ins_local"

    payload={
          "ins_api": {
                "version": "1.0",
                "type": type,
                "chunk": "0",
                "sid": "1",
                "input": input,
                "output_format": "json"
          }
    }

    response = do_post_sock("/tmp/nginx_local/nginx_1_be_nxapi.sock", url, json.dumps(payload))

    response = json.loads(response)
    out = response["ins_api"]["outputs"]["output"]

    code = out['code']
    if int(code) == 200:
        body = out['body']
    elif int(code) == 400:
        body = out['msg'] + ': ' + out['clierror']
    else:
        body = out['msg']

    if len(body) == 0:
        body = ""
   
    return out 

1;
