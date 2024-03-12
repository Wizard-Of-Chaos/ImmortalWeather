import discord as dc
import requests
import time

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

def placeholder_embed(author) -> dc.Embed:
    embed = dc.Embed(
        color=dc.Color.blue(),
        description = f'Weather report for {author}'
        )
    
    embed.insert_field_at(0, name='**Wizard of Chaos:**', value=WAIT_EMOJI, inline=True)
    embed.insert_field_at(1, name='**Snow:**', value=WAIT_EMOJI, inline=True)
    embed.insert_field_at(2, name='**Tint:**', value=WAIT_EMOJI, inline=True)
    embed.insert_field_at(3, name='**MxGuire:**', value=WAIT_EMOJI, inline=True)
    embed.insert_field_at(4, name='**Jubei Report:**', value=WAIT_EMOJI, inline=False)
    embed.insert_field_at(5, name='**Global Subman Report:**', value=WAIT_EMOJI, inline=False)
    embed.insert_field_at(6, name='**Recommendation:**', value=WAIT_EMOJI, inline=False)
    return embed 

def queue_confidence_factor(jubei_active:bool, active_submen_percentage:float, minute_count:int, hour_count:int) -> float:
    confidence = 1.0 #start at 100%
    if jubei_active:
        confidence -= .13 #jubei is 25% off
    confidence = confidence * (1 - active_submen_percentage) #active submen are a flat multiplier
    confidence = confidence - float(minute_count * .04) #each active subman whose game ended in the past 10 minutes is 4% off
    return confidence

def queue_rec(confidence:float) -> str:
    if confidence >= .75:
        return 'safe'
    if confidence >= .6:
        return 'probably harmless'
    if confidence >= .5:
        return 'gambling'
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
    json = data.json()
    ratio = float(float(json['win']) / (float(json['lose']) + float(json['win'])))
    return ratio

def subman_APIstr(submanid):
    return API_STR + 'players/' + str(submanid) + '/recentMatches'

def last_minutes_req(submanid):
    request = requests.get(subman_APIstr(submanid))
    recent_json = request.json()[0]
    start_time = recent_json['start_time']
    start_time += recent_json['duration']
    elapsed = time.time() - start_time
    return float(elapsed/60)