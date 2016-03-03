#!/usr/bin/python
#
#
# Author: Stephen J. Hilt
# Purpose: To read RSS feeds and post to a given slack channel
#
#
import feedparser
from slacker import Slacker
import time
import datetime


t = datetime.datetime.now()
#Setup to pull RSS feed example is ICS-CERT Alerts
rss =feedparser.parse('https://ics-cert.us-cert.gov/alerts/alerts.xml')
#setup slack via Slacker
slack = Slacker('YOUR_API_KEY')
# create current time based off RSS feeds format 
# the minus -4 is for an offset of GMT to East Cost minus an hour since i'm running this 
# as a cron job every how, so this will pull everything from the past hour
date_time = "{}, {} {} {} {}:".format(time.strftime("%a"),time.strftime("%d"),time.strftime("%b"),time.strftime("%Y"),int(time.strftime("%H"))+4)

# set a counter to 0 to loop through all the RSS feed entries
count = 0
while count < len(rss['entries']):
        # pull the entries published date/time
        published = rss['entries'][count]['published']
        # if from the last hour
        if date_time in published:
                # Title, description, and link to be posted
                title = rss['entries'][count]['title']
                desc = rss['entries'][count]['description']
                link = rss['entries'][count]['link']
                # send message to slack
                slack.chat.post_message('#random', "_*{}*_\n{}\n{}\n".format(title,desc,link), username="RSSbot", icon_emoji=":rage:")
        count += 1

