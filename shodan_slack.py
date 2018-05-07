#!/usr/bin/python
import shodan
import sys
import os
import urllib
from slacker import Slacker
from random import randint
from PIL import Image



# Configuration
API_KEY = "SHODAN_API_KEY"
slack = Slacker('SLACK_API_KEY')
#
# to perform the shodan output, returns the shodan result (IP) as well as a formated string
def shodanMessage():
        # Perform the search
        total = api.count('has_screenshot:true')['total']
        page = randint(1, total / 100 + 1)
        results = api.search('has_screenshot:true', page=page)
        num_results = len(results['matches'])
        num = randint(0,num_results)
        shodan_result = results['matches'][num]['ip_str']
        image = results['matches'][num]['opts']['screenshot']['data']
        shodan_result = results['matches'][randint(0,num_results)]['ip_str']
        url = "https://www.shodan.io/host/{}/image".format(shodan_result)
        return url, image, shodan_result

#
# Checks to see if the image is black, or tuns out if its majority one color
# the value None appears when the image has more than just gray tones in it. 
def isBlack():
        # Loop until we find an image thats not all black
        while True:
                SHODAN_MESSAGE, image, shodan_result = shodanMessage()
                f = open ('00000001.jpg', 'wb')
                # write image to file, for color analysis
                f.write(image.decode('base64'))
                f.close()
                # open the local image for analysis
                img = Image.open("00000001.jpg")
                # get the colors in a list
                clrs = img.getcolors()
                if "None" in str(clrs):
                        return SHODAN_MESSAGE

#
# Send the slack messsage
def slackSend(SHODAN_MESSAGE):
        slack.chat.post_message('#random', "Here is a Random host with a screenshot from SHODAN {}".format(SHODAN_MESSAGE), username="BOTNAME", icon_emoji=":smile:")

try:
        # Setup the api
        api = shodan.Shodan(API_KEY)
        # send the non single tone image to slack channel
        slackSend(isBlack())
        # remve the image we downloaded 
        os.remove('00000001.jpg')

except Exception as e:
        print 'Error: %s' % e
        sys.exit(1)
