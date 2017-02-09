#!/usr/bin/env python

import cli

o1 = cli.execute('show ip int brief | include Te.*up');
o2 = cli.execute('show ip int brief | include Ethernet.*up');

#o1 = ""
#o2 = "GigabitEthernet0/0/0   unassigned      YES NVRAM  up                    up\n" 
#o2+= "GigabitEthernet0/0/0   unassigned      YES NVRAM  up                    up\n"      
#o2+= "GigabitEthernet0       172.26.170.253  YES NVRAM  up                    up\n"      
#o2+= "GigabitEthernet0       172.26.170.253  YES NVRAM  up                    up\n"

intfs = set()

def grab_intf(i):
    global intfs
    if i == "":
        return 
    j = (i.split(' '))[0]
    intfs.add(j) 

for i in o1.split('\n'):
    grab_intf(i)

for i in o2.split('\n'):
    grab_intf(i)

for i in intfs:
   cmd = "test cable-diagnostics tdr interface " + i
   o3 = cli.execute(cmd);
