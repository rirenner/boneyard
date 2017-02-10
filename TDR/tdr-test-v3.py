#!/usr/bin/env python
 
# importing the cli module is necessary to run
# config or exec commands on the host.
import cli

# importing the time module works well in 
# this script, as we are pacing some of the execution.
import time
 
o1 = cli.execute('show ip int brief | include Ethernet1/0/.*down');
# Create this thing called o1. Make it be equal to the command above. 
# This is also proper use of the cli.execute API. As you can see, 
# this is CLI, taking advantage of regexp # matching. Essentially, 
# we are running this command to get a list of all the interfaces
# that are UP on the host!
 
# Create this thing called intfs. Make it a Python dictionary.
intfs = dict()

# Create a function to grab the list of interfaces from passed in data. 
def grab_intf(i):
    # use the global intfs variable defined outside of the function.
    global intfs
    # If the passed in data is empty exit the function. 
    if i == "":
        return
    # Take the first column of space separated data 
    j = (i.split(' '))[0]
    # Assign the interface name as a key value in the intfs dictionary.
    intfs[j] = ""
 
for i in o1.split('\n'):
    # Take the o1 data, split it on each line, call the grab_intf 
    # function on each line.
    grab_intf(i)
 
for i in intfs:
   # Run through out interface list.
   cmd = "test cable-diagnostics tdr interface " + i
   # While we run through our interface list, each time we iterate, 
   # create this thing called
   # cmd, and set it equal to the output of the command.
   o2 = cli.execute(cmd);
   # And each time we do, create this thing called o2, and set it 
   # equal to the execution of
   # each command for each interface on the host.
 
done = False
# Create this thing called done and set it to a value of 
# False. Essentially, we're not done!

while done == False:
    # Create a loop condition for when we're not done.   
 
    for i in intfs:
        # Remember our list of interfaces? Run through them again.   
        # If we already have data for an interface, then skip
        if intfs[i] != "":
            continue
        
        # Try to get data for the interface we are working on
        cmd = "show cable-diagnostics tdr interface " + i
        # Once again, create this thing called cmd, and set it equal 
        # to the iterative exec
        # command for all of our interfaces.
        o2 = cli.execute(cmd);
        # And create this thing called o2, and execute each CLI.
        if "Not Completed" in o2:
            # Parse the data we get. We are making sure the TDR test runs, 
            # and also completes.   
            continue
        else :
            # We got valid data, set it into the dictionary value for the
            # specific interface we are working on.
            intfs[i] = o2
 
    time.sleep(2)
    # now loop again looking to see if we are all done
    found_one = False
    for i in intfs:
        if intfs[i] == "":
            found_one = True;
    if found_one == False:
        done = True       
 
# We are done gathering now just print output
target = open('/bootflash/myoutputfile', 'w')
target.truncate()
 
for i in intfs:
    title = "Interfaces: " + i
    print title
    target.write(title)
    print intfs[i]
    target.write(intfs[i])
    print "\n\n"
    target.write("\n\n")
 
target.close()
