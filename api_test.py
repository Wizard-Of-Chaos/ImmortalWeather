import requests
import json
import time
from deadlock.deadlock_item_utils import *
from gargoyle_consts import WIZ_ID

api_url = 'http://api.steampowered.com/'

dead_api = "https://api.deadlock-api.com/v1"

def request():
    lock_request = requests.get("https://api.deadlock-api.com/v1/matches/40943044/metadata")
    print(lock_request.status_code)

    lm_detailed = lock_request.json()

    player_details = lm_detailed["match_info"]["players"]
    stats_end = player_details
    for player in lm_detailed["match_info"]["players"]:
        if player["account_id"] != WIZ_ID:
            continue
        player_details = player
        print("Found player in match")
    
    items = player_details["items"]
    images = []
        
    # build_inventory_img(get_inventory_images(items)).save(f"{ITEM_IMG_PATH}inventory.png", "PNG")
    print(lm_detailed["match_info"]["average_badge_team0"])
    print(lm_detailed["match_info"]["average_badge_team1"])
    
    player_team_badge = lm_detailed["match_info"]["average_badge_team0"] if player_details["team"] == 0 else lm_detailed["match_info"]["average_badge_team1"]
    enemy_team_badge = lm_detailed["match_info"]["average_badge_team0"] if player_details["team"] == 1 else lm_detailed["match_info"]["average_badge_team1"]
    print(enemy_team_badge)
    print(player_team_badge)



if __name__ == '__main__':
    print("Requesting")
    request()