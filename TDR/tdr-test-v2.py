#!/usr/bin/env python

import cli
import time

o1 = cli.execute('show ip int brief | include Te.*up');
o2 = cli.execute('show ip int brief | include Ethernet.*up');

#o1 = ""
#o2 = "GigabitEthernet0/0/0   unassigned      YES NVRAM  up                    up\n" 
#o2+= "GigabitEthernet0/0/0   unassigned      YES NVRAM  up                    up\n"      
#o2+= "GigabitEthernet0       172.26.170.253  YES NVRAM  up                    up\n"      
#o2+= "GigabitEthernet0       172.26.170.253  YES NVRAM  up                    up\n"

intfs = dict()

def grab_intf(i):
    global intfs
    if i == "":
        return 
    j = (i.split(' '))[0]
    intfs[j] = ""

for i in o1.split('\n'):
    grab_intf(i)

for i in o2.split('\n'):
    grab_intf(i)

for i in intfs:
   cmd = "test cable-diagnostics tdr interface " + i
   o3 = cli.execute(cmd);

done = False
while done == False:
    for i in intfs:
        if intfs[i] != "":
            continue
        cmd = "show cable-diagnostics tdr interface " + i 
        o3 = cli.execute(cmd);
        if "Not Completed" in o3:
            continue
        else :
            intfs[i] = o3

    time.sleep(2)
    # now loop again looking to see if we are all done
    found_one = False
    for i in intfs:
        if intfs[i] == "":
            found_one = True;
    if found_one == False:
        done = True        

# We are done gathering now just print output

for i in intfs:
    print "Interface: ", i
    print intfs[i]
    print "\n\n"
