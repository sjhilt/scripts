#!/usr/bin/python
import requests
import urllib
import datetime
import time
import sys
import os
import json


def post_slack(API,chid,message,username,icon):
    url = "https://slack.com/api/chat.postMessage?token={}&channel={}&text={}&username={}&icon_emoji={}&pretty=1".format(API,chid,message,username,icon)
    u = urllib.urlopen(url)
    response = u.read()
    return response

API  = 'YOURAPIKEYHERE'
url = 'https://icanhazdadjoke.com/slack'
headers = {'user-agent':'My Library (YOUR NAME OR GITHUB HERE)'}
response = requests.get(url, headers=headers)
results = response.json()
post_slack(API,"#general",results['attachments'][0]['text'],"Daily Dad Jokes",":joy:")