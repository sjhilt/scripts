#!/usr/bin/env python
# Author: Stephen J. Hilt
#	pour beer from Talos' Automated Kegorator 
# from DerbyCon 6.0
# There Is No Such Thing As Free Beer 1.0
#
#########################################################
from pycomm.ab_comm.slc import Driver as SlcDriver
import time

# Argument Checking
if (len(sys.argv) != 2): 
	print("USAGE: python ./tinstafb.py <host> <left|right|lock>")
	sys.exit()
	
host=sys.argv[1]
command=sys.argv[2]

c = SlcDriver()
if c.open(host):

  if command == "left":
    # Left tap on
    c.write_tag('B3:0/0', 1)
    # Pour the perfect beer
    time.sleep(5)
    # left tap off
    c.write_tag('B3:0/0', 0)
  elif command == "right":
    # right tap on
    c.write_tag('B3:0/1', 1)
    # Pour the perfect beer
    time.sleep(5)
    # right tap off
    c.write_tag('B3:0/1', 0)
  elif command == "lock"
    #lock the HMI screen so no more beer can be poured until unlocked
    c.write_tag('B3:0/2', 1)
  else:
    # Spencer mode on!
    c.write_tag('B3:0/3', 1)

c.close()
