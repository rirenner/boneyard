#!/usr/bin/env python

import socket

host = ''
port = 50022
backlog = 5
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
while 1:
    client, address = s.accept()
    data = client.recv(size)
    if data:
        if (data == "done"):
	    print "received a done message, exiting"
            client.send("server done, exiting") 
            client.close()
            s.close()
            break
        else :
            print data
            client.send(data)
    client.close()
s.close()
                 
