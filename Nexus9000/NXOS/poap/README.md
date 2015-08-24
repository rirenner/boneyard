Power on Auto Provisioning Demo scripts.


demo_poap.py.cablemap

This script checks CDP information for neighbors and compares output
to a static "cablemap" file.  If there is a mismatch in cabling a
warning is output in the poap.log. files.

demo_poap.py.image_check

This script will check if the loaded image is set to the "desired_version"
set within the script.  If there is a match it schedules configuration
and reloads.  If not, it checks to see if there is an image in bootflash
which matches the desired version.  If there is it schedules a reload of
the bootflash image.   If no image is found in bootflash, it will copy
the image into bootflash and schedule a reload.

dhcpd.conf

This is a dhcpd configuration file, it can be used as a model to see
how http downloads can be done with poap.  It defaults to sending
demo_poap.py.


