import discord as dc
import requests
import time
import sys 

DBUFF_STR = 'https://www.dotabuff.com/players/'

STEAM_API_KEY = ''
with open('api.txt', 'r') as api:
    STEAM_API_KEY = api.readline()
print(STEAM_API_KEY)
STEAM_API_URL = 'http://api.steampowered.com/'

def num_matches_str(player_id:int, num_matches:int) -> str:
    return f'{STEAM_API_URL}/IDOTA2Match_570/GetMatchHistory/V001/?key={STEAM_API_KEY}&account_id={player_id}&matches_requested={num_matches}'

def specific_match_str(match_id: int) -> str:
    return f'{STEAM_API_URL}/IDOTA2Match_570/GetMatchDetails/V001/?key={STEAM_API_KEY}&match_id={match_id}'

WIZ_ID  = 75688374
SNOW_ID = 107944284
TINT_ID = 62681700
MIKE_ID = 173836647

WAIT_EMOJI = '<a:clockwerk:635269145151143956>'

def placeholder_global_embed(author) -> dc.Embed:
    embed = dc.Embed(
        color=dc.Color.blue(),
        description = f'*Immortal Draft weather report*'
        )
    
    embed.insert_field_at(0, name='**Wizard of Chaos**', value=WAIT_EMOJI, inline=True)
    embed.insert_field_at(1, name='**Snow**', value=WAIT_EMOJI, inline=True)
    embed.insert_field_at(2, name='**Tint**', value=WAIT_EMOJI, inline=True)
    embed.insert_field_at(3, name='**MxGuire**', value=WAIT_EMOJI, inline=True)
    embed.insert_field_at(4, name='**Jubei Status**', value=WAIT_EMOJI, inline=True)
    embed.insert_field_at(5, name='**Subman Report**', value=WAIT_EMOJI, inline=False)
    embed.insert_field_at(6, name='**Linear Factor**', value=WAIT_EMOJI, inline=True)
    embed.insert_field_at(7, name='**Decay Factor**', value=WAIT_EMOJI, inline=True)
    return embed 

def placeholder_personal_embed(author) -> dc.Embed:
    embed = dc.Embed(
        color=dc.Color.red(),
        description = f'*Weather report for {author}*'
        )
    embed.insert_field_at(0, name='**Your Wind**', value=WAIT_EMOJI, inline=False)
    embed.insert_field_at(1, name='**Subman Report**', value=WAIT_EMOJI, inline=False)
    embed.insert_field_at(2, name='**Linear Factor**', value=WAIT_EMOJI, inline=True)
    embed.insert_field_at(3, name='**Decay Factor**', value=WAIT_EMOJI, inline=True)
    return embed

def linear_queue_factor(jubei_active:bool, active_submen_percentage:float, minute_count:int) -> float:
    confidence = 1.0 #start at 100%
    if jubei_active:
        confidence -= .13 #jubei is 13% off
    confidence = confidence * (1 - active_submen_percentage) #active submen are a flat multiplier
    confidence = confidence - float(minute_count * .05) #each active subman whose game ended in the past 20 minutes is 4% off
    return confidence

def decay_queue_factor(submen_minute_list:list[int]) -> float:
    confidence = 1.0
    if len(submen_minute_list) == 0:
        return confidence
    for subman in submen_minute_list:
        base_factor = .2
        decay_rate = 5
        factor = base_factor * (.5**(subman/decay_rate))
        print(f'{factor} for subman with time {subman}')
        confidence -= factor
    return confidence

def queue_rec(confidence:float) -> str:
    if confidence >= .75:
        return 'safe'
    if confidence >= .6:
        return 'probably harmless'
    if confidence >= .5:
        return 'a gamble'
    if confidence >= .35:
        return 'unsafe'
    return 'extremely hazardous'

def wl_phrase(number):
    if number > .53:
        return 'Calm'
    if number >= .45:
        return 'Gusty'
    if number >= .35:
        return 'Turbulent'
    return 'Stormy'

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


class SubmenData(object):
    def __init__(self, jubei:bool, past_90:int, past_20:int, submen_count:int, invalid_submen:int, active_submen:int, past_20_list:list[int], recent:int, msg:dc.Message, embed:dc.Embed):
        self.jubei = jubei
        self.past_90 = past_90
        self.past_20 = past_20
        self.past_20_list = past_20_list
        self.submen_count = submen_count
        self.active_submen = active_submen
        self.invalid_submen = invalid_submen
        self.msg = msg
        self.embed = embed
        self.most_recent = recent
        self.percentage = float(active_submen / (submen_count - invalid_submen))
        self.lin_factor = linear_queue_factor(jubei, self.percentage, past_20)
        self.decay_factor = decay_queue_factor(past_20_list)

async def eval_submen(submen_list:list[int], msg:dc.Message, embed:dc.Embed, report_index:int, jubei:bool) -> SubmenData:
    submen_last_ninety_min = 0
    submen_last_twenty_min = 0
    submen_invalid = 0
    subman_counter = 0
    submen_time_list = []
    updated_embed = embed
    updated_msg = msg
    most_recent = sys.maxsize
    for subman in submen_list:
        timesince = get_last_time_minutes(subman)
        if timesince is None:
            submen_invalid += 1
        else:
            if timesince < most_recent:
                most_recent = timesince
            if timesince < 90:
                submen_last_ninety_min += 1
            if timesince < 20:
                submen_last_twenty_min += 1
                submen_time_list.append(timesince)
        subman_counter += 1
        if(subman_counter % 5) == 0:
            updated_embed.set_field_at(report_index, name='**Subman Report**', value=f'Evaluated {subman_counter} submen of {len(submen_list)} ({submen_invalid} invalid)', inline=False)
            updated_msg = await updated_msg.edit(embed=updated_embed)
    
    return SubmenData(jubei, submen_last_ninety_min, submen_last_twenty_min, subman_counter, submen_invalid, submen_last_ninety_min, submen_time_list, most_recent, updated_msg, updated_embed)
