import discord as dc
import requests
import time
import sys 

API_STR = 'https://api.opendota.com/api/'
DBUFF_STR = 'https://www.dotabuff.com/matches/'
WL_LIMIT_STR = 'wl?limit=10'

def wl_request_str(id: int) -> str:
    return API_STR + f'players/{id}/' + WL_LIMIT_STR

def recent_request_str(id: int) -> str:
    return API_STR + f'players/{id}' + '/recentMatches'

WIZ_REQUEST_STR = wl_request_str(75688374)
SNOW_REQUEST_STR = wl_request_str(107944284)
TINT_REQUEST_STR = wl_request_str(62681700)
MIKE_REQUEST_STR = wl_request_str(173836647)

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

def wl_ratio_req(requeststr):
    data = requests.get(requeststr)
    if data.status_code != 200:
        return None
    json = data.json()
    ratio = float(float(json['win']) / (float(json['lose']) + float(json['win'])))
    return ratio

def subman_APIstr(submanid):
    return API_STR + 'players/' + str(submanid) + '/recentMatches'

def last_minutes_req(submanid):
    request = requests.get(subman_APIstr(submanid))
    print(request)
    if request.status_code != 200:
        return None
    if len(request.json()) == 0:
        print('invalid request!')
        return None
    recent_json = request.json()[0]
    start_time = recent_json['start_time']
    start_time += recent_json['duration']
    elapsed = time.time() - start_time
    return float(elapsed/60)

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
        timesince = last_minutes_req(subman)
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
