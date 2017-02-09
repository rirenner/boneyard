#!/usr/bin/env python

#import cli
# print cli.execute('show version')

# o22-3850-10#sho  ip int brief | include Te.*up
# Te1/1/2                unassigned      YES unset  up                    up    
  
# o22-3850-10#sho  ip int brief | include Ethernet.*up     
# GigabitEthernet0/0     172.26.170.243  YES manual up                    up    
  
# GigabitEthernet1/0/1   unassigned      YES unset  up                    up    
  
# o22-3850-10#

#o1 = cli.execute('show ip int brief | include Te.*up');
#o2 = cli.execute('show ip int brief | include Ethernet.*up');

o1 = ""
o2 = "GigabitEthernet0/0/0   unassigned      YES NVRAM  up                    up\n" 
o2+= "GigabitEthernet0/0/0   unassigned      YES NVRAM  up                    up\n"      
o2+= "GigabitEthernet0       172.26.170.253  YES NVRAM  up                    up\n"      
o2+= "GigabitEthernet0       172.26.170.253  YES NVRAM  up                    up\n"

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
   print "i is ", i
