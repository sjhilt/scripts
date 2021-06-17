import sys
import os
import requests
import json
import argparse
from rocketchat_API.rocketchat import RocketChat

#Configuration
username = 'username'
password = 'password'
rocket = RocketChat(username, password, server_url='http://rocket.chat:port' )
# Location Change the GPS Cordinates. Example: 38.869256523 -77.0535764524
url = "https://api.weather.gov/points/38.869256523,-77.0535764524/forecast"
# Set the arguments of Morning, Afternoon, or Evening based on the time you are 
# Running the code
parser = argparse.ArgumentParser(description='Morning|Afternoon|Evening')
# arg parse to look for the argument
parser.add_argument("timefield", help="Use Morning|Afternoon|Evening",type=str)
args = parser.parse_args()
argument = args.timefield
#get the json results from the weather URL
data = requests.get(url).json()
# count is 0 
count = 0
# loop through the json looking for results 
while count < len(data['properties']['periods']):
    # Name of the time, morning, afternoon,etc 
    name = data['properties']['periods'][count]['name']
    # set the message, this is the actual forcast
    message = data['properties']['periods'][count]['detailedForecast']
    # set the icon for the message based on what type of weather 
    # These icons are based on rocket chat, if porting to others 
    # icons will need to change, see https://github.com/DC423/Slack-Projects/blob/master/weather_slack.py
    #
    if "Partly sunny" in message:
        icon = ":partly_sunny:"
    elif "Partly cloudy" in message:
        icon = ":white_sun_small_cloud:"
    elif "Mostly sunny" in message:
        icon = ":white_sun_small_cloud:"
    elif "Mostly cloudy" in message:
        icon = ":white_sun_cloud: "
    elif "Mostly clear" in message:
        icon = ":white_sun_cloud:"
    elif "thunderstorms" in message:
        icon = ":cloud_lightning:"
    elif "showers" in message:
        icon = ":cloud_rain:"
    else:
        icon = ":sunny:"
    # Add the thunderstorm cloud to the message as well
    if "thunderstorms" in message:
        message = message + " " + ":cloud_lightning:"
    # Set the argument for the name to send rocket chat message or not
    if argument == "morning":
       timerun = ["Today", "Tonight"]
    elif argument == "afternoon":
       timerun = ["Tonight","This Afternoon"]
    elif argument == "tonight":
       timerun = ["Tonight"]
    else:
       timerun = ""
    if name in timerun:
        # Send Rocket.chat Message. 
        rocket.chat_post_message(message, channel='GENERAL', alias='%s' % name, emoji='%s' % icon).json()
    count = count + 1
sys.exit()
