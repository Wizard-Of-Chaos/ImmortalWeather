import requests
import json
import time

api_url = 'http://api.steampowered.com/'

dead_api = "https://api.deadlock-api.com/v1"

def request():
    lock_request = requests.get("https://api.deadlock-api.com/v1/matches/40681410/metadata")
    print(lock_request.status_code)
    lm_detailed = lock_request.json()
    player_details = lm_detailed["match_info"]["players"]
    stats_end = player_details
    for player in lm_detailed["match_info"]["players"]:
        if player["account_id"] != 119145593:
            continue
        player_details = player
        print("Found player in match")
    items = player_details["items"]


if __name__ == '__main__':
    print("Requesting")
    request()