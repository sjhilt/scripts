#!/usr/bin/python
import requests
import shodan
import sys
import os
import time
from slacker import Slacker
from random import randint
from PIL import Image
import urllib

# Configuration
API_KEY = "SHODAN_API_KEY"
API = "SLACK_API_KEY"
slack = Slacker(API)

# Fixed to allow for the new method that allows only the first 10 pages
# Pulls a random image from shodan, 
def shodanMessage():
        # Perform the search
        page = randint(1, 10)  # Only the first 10 pages can be accessed in a random pattern
        # Check
        results = api.search('has_screenshot:true -port:3388,3389', page=page)
        num_results = len(results['matches'])
        num = randint(0,num_results)
        shodan_result = results['matches'][num]['ip_str']
        image = results['matches'][num]['opts']['screenshot']['data']
        shodan_result = results['matches'][randint(0,num_results)]['ip_str']
        url = "https://beta.shodan.io/host/{}/image".format(shodan_result)
        return url, image, shodan_result
#Tests to see if the image is mostly black 
def isBlack():
        while True:
                SHODAN_MESSAGE, image, shodan_result = shodanMessage()
                f = open ('00000001.jpg', 'wb')
                f.write(image.decode('base64'))
                f.close()
                img = Image.open("00000001.jpg")
                nblack=0
                #Returns a tuple of the RGB data for each pixel 
                pixels = img.getdata()
                # for each pixel that is in the image. 
                for pixel in pixels:
                    # Sum up the 3 tuples 
                    sum_pixel = sum(pixel)
                    # Devide the number by 3, for the average of the three tuples 
                    avg_pixel = sum_pixel / 3
                    # If the average is "dark", which is an random picked value by me. 
                    # In this case while playing with RGB values I deteremind that if the average
                    # was 50 then the pixel is "dark" 
                    if avg_pixel < 50: 
                        nblack +=1
                # how many pixels 
                n = len(pixels)
                # if the image is more than 90% "dark" 
                if (nblack / float(n)) > 0.9: 
                    # print value that its mostly dark and the link just incase for testing 
                    print "Mostly Black? %s" % SHODAN_MESSAGE
                    # sleep for 5 seconds so we don't time out on the Shodan API
                    time.sleep(5)
                # if the value is < 90% dark lets go ahead and print it anyway. 
                else:
                    return SHODAN_MESSAGE
#Send a message to slack with a link to the image
def slackSend(SHODAN_MESSAGE):
        slack.chat.post_message('#random', u'Enjoy a random host with an image from SHODAN\u2122 {}'.format(SHODAN_MESSAGE), username="BOT_NAME_HERE", icon_emoji=":fail_rail:")

#MAIN 
#Try statement incase there is an error 
try:
        # Setup the api
        api = shodan.Shodan(API_KEY)
        # Check to see if iamge is black
        slackSend(isBlack())
        # Remove the image we created during the above processes to be clean
        os.remove('00000001.jpg')
# Print Error message if there was an error and exit with an error. 
except Exception as e:
        print 'Error: %s' % e
        sys.exit(1)

