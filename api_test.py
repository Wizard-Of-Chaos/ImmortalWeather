import requests
import json

key = '869AE5CCFB534F12A611985021545B8B'
dota_id = 75688374
api_url = 'http://api.steampowered.com/'
history_str = f'{api_url}/IDOTA2Match_570/GetMatchHistory/V001/?key={key}&account_id={dota_id}&matches_requested=10'
test_match = 7634438489
specific_str = f'{api_url}/IDOTA2Match_570/GetMatchDetails/V001/?key={key}&match_id={test_match}'

history_request = requests.get(history_str)
print(history_request)
history_json_str = json.dumps(history_request.json(), indent=4)
history_json = history_request.json()

with open('tst.json', 'w') as out:
    out.write(history_json_str)

match_id = history_json['result']['matches'][0]['match_id']
print(match_id)