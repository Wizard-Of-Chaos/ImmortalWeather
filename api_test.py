import requests
import json
import time

api_url = 'http://api.steampowered.com/'

def num_matches_str(player_id:int, num_matches:int) -> str:
    return f'{api_url}/IDOTA2Match_570/GetMatchHistory/V001/?key={key}&account_id={player_id}&matches_requested={num_matches}'

def specific_match_str(match_id: int) -> str:
    return f'{api_url}/IDOTA2Match_570/GetMatchDetails/V001/?key={key}&match_id={match_id}'

def get_last_time_minutes(player_id:int) -> float|None:
    begin_request = time.time()
    request1 = requests.get(num_matches_str(player_id, 1))
    if request1.status_code != 200:
        print(f'get_last_time: Request for player {player_id} returned {request1.status_code}')
        return None
    
    if int(request1.json()['result']['status']) != 1:
        print(f'get_last_time: Request for player {player_id} is invalid!')
        return None
    
    match_id = int(request1.json()['result']['matches'][0]['match_id'])
    request2 = requests.get(specific_match_str(match_id))

    if request2.status_code != 200:
        print(f'get_last_time: Request for player {player_id} returned {request1.status_code} for match id {match_id}')
        return None
    
    start_time = request2.json()['result']['start_time']
    start_time += request2.json()['result']['duration']
    elapsed = time.time() - start_time
    elapsed = float(elapsed/60)
    print(f'Time elapsed since last match for player {player_id}: {elapsed} ({time.time() - begin_request} sec response time)')
    return elapsed

def get_recent_wl_ratio(player_id:int) -> float|None:
    begin_request = time.time()
    request1 = requests.get(num_matches_str(player_id, 10))

    if request1.status_code != 200:
        print(f'get_recent_wl: Request for player {player_id} returned {request1.status_code}')
        return None
    
    if int(request1.json()['result']['status']) != 1:
        print(f'get_recent_wl: Request for player {player_id} is invalid!')
        return None
    
    wins = 0
    losses = 0

    for i in range(10):
        specific_req_id = int(request1.json()['result']['matches'][i]['match_id'])
        specific_req = requests.get(specific_match_str(specific_req_id))

        if specific_req.status_code != 200:
            print(f'get_recent_wl: Failed to get match {specific_req_id}, exiting')
            return None
        
        radiant_win = bool(specific_req.json()['result']['radiant_win'])

        for j in range(10):
            id = specific_req.json()['result']['players'][j]['account_id']
            team_number = int(specific_req.json()['result']['players'][j]['team_number'])
            if int(id) == player_id:
                if radiant_win:
                    if team_number == 0:
                        wins += 1
                    else:
                        losses += 1
                else:
                    if team_number == 1:
                        wins += 1
                    else:
                        losses += 1
        
    ratio = float(wins) / 10.0
    print(f'Win ratio for last 10 matches on player {player_id}: {ratio} ({time.time() - begin_request} sec response time)')
    return ratio

get_last_time_minutes(75688374)
get_recent_wl_ratio(75688374)

#with open('recents.json', 'w') as out:
    #out.write(history_json_str)