#!/usr/bin/python
import os
import json
from time import strftime
from slacker import Slacker

#URL Extacted from the hc911.org alerts page
url = "http://hamilton911.discoveregov.com/ajax.php?ts=' + ((new Date()).getTime() / 1000).toFixed()"
slack = Slacker('API_KEY_HERE')
#hacked way of getting only the json string this could be improved but it works
response = os.popen('curl -s \"{}\" | grep \"var activities\"| cut -d= -f2| sed \'s/];/]/\''.format(url)).read()
# load the json string
data = json.loads(response)
# get a single digit hour
hour = strftime("%I").lstrip('0')
#24 hour time needed for am/pm matching of the string from hc911.org
t4hour = strftime("%H")
if its over 11, then its pm else am
if t4hour > 11:
        mn = "pm"
else:
        mn = "am"
# minut minus 5, the time between 'created_str' and current time is around a 5min delta
min = int(strftime("%M")) - 5
# if after the -5 we have a negative number then we need to make this the previous hour
if min < 0:
        min = 60 - abs(min)
        hour = str(int(hour - 1))
# pull the length of the json list
len = len(data)
# length - 1 for adjustment to start at 0
index = len - 1
# match time format from created_str
time = hour + ":" + str(min) + mn
# counter set to 0 for loop through the list
count = 0
while count < index:
        # pull the created_str extract only have time, not the date with the split
        created = data[count]['created_str'].split(" ")[1]
        # do the times match?
        if created == time:
                #pull json elements to post to slack
                addr = data[count]['address']
                agency = data[count]['agency_name']
                status = data[count]['status']
                type = data[count]['type']
                created = data[count]['created_str']
                # post message to slack channel 
                slack.chat.post_message('#random', agency + " - " + addr + " - " + type + " _*STATUS*_ " + status, username="hc911bot", icon_emoji=":police_car:")
        count += 1
