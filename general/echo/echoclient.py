#!/usr/bin/env python

import socket

host = '<ip address>'
port = 50022
size = 1024
while(True):
    test = raw_input('Enter Data to send to server: ')
    if (test == 'q') or (test == 'quit'):
        break
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))
        s.send(test)
        data = s.recv(size)
        print 'Received:', data
        s.close()
print 'done'

