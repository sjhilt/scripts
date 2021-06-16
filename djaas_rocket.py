from requests import sessions
from pprint import pprint
import requests
from rocketchat_API.rocketchat import RocketChat

rocket = RocketChat('username', 'password', server_url='rocket.chat:port' )
url = 'https://icanhazdadjoke.com/slack'
headers = {'user-agent':'My Library (Link to your github here)'}
response = requests.get(url, headers=headers)
results = response.json()
rocket.chat_post_message(results['attachments'][0]['text'], channel='GENERAL', alias='DAD JOKES!', emoji=':joy:').json()
