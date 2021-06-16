from requests import sessions
from pprint import pprint
import requests
from rocketchat_API.rocketchat import RocketChat

username = ''
password = ''
rocket = RocketChat(username, password, server_url='rocket.chat:port' )
url = 'https://animechan.vercel.app/api/random'
headers = {'user-agent':'My Library (YOUR GITHUB PAGE)'}
response = requests.get(url, headers=headers)
results = response.json()
rocket.chat_post_message("\"%s\" -- %s" % (results['quote'],results['character']), channel='GENERAL', alias='%s' % results['anime'], emoji=':japan:').json()
