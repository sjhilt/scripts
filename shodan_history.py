#####################################################
# Script to pull the history of an IP address via
# the shodan API. This just dumps out the raw JSON
#  Author: Stephen Hilt
#####################################################
import shodan
import sys

# Make this your API Key from accounts.shodan.io
API_KEY = "YOUR KEY HERE"

# Input validation for one argument (IP address)
if len(sys.argv) == 1:
	print 'Usage: %s <host>' % sys.argv[0]
	sys.exit(1)
try:
  # Pull the first argument for the IP address 
  # to look up the history of
	host = sys.argv[1] 
	# Setup the API to communicate to
	api = shodan.Shodan(API_KEY)
	# pull the information about the host, and the history 
	# this is done by setting the history to True
	result = api.host(host, history=True)
	      # Display raw results, this is where more parsing 
	      # could be done depending on your output needs
        print result
except Exception, e:
	print 'Error: %s' % e
	sys.exit(1)
