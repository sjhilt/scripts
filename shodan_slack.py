import shodan
import sys
import os
from slacker import Slacker
from random import randint

# Configuration
API_KEY = "SHODAN_API_KEY"
slack = Slacker('SLACK_API_KEY')



try:
        # Setup the api
        api = shodan.Shodan(API_KEY):

        # Perform the search
        query = "has_screenshot:true"
        total = api.count('has_screenshot:true')['total']
        page = randint(1, total / 100 + 1)
        results = api.search('has_screenshot:true', page=page)
        num_results = len(results['matches'])
        shodan_result = results['matches'][randint(0,num_results)]['ip_str']
        SHODAN_MESSAGE = "https://www.shodan.io/host/{}".format(shodan_result)
        # Change all the variables you need before running such as BOTNAME and YOUR_EMOJI
        slack.chat.post_message('#random', "Here is a Random host with a screeshot from SHODAN {}".format(SHODAN_MESSAGE), username="BOTNAME", icon_emoji="YOUR_EMOJI")
except Exception as e:
        print 'Error: %s' % e
        sys.exit(1)
