import discord
from discord.ext import commands
import requests
from submantracker import SubmanTracker
import time
import sys

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='--', intents=intents)

API_STR = 'https://api.opendota.com/api/'
DBUFF_STR = 'https://www.dotabuff.com/matches/'
WL_LIMIT_STR = 'wl?limit=10'

WIZ_REQUEST_STR = API_STR + 'players/75688374/' + WL_LIMIT_STR
SNOW_REQUEST_STR = API_STR + 'players/107944284/' + WL_LIMIT_STR
TINT_REQUEST_STR = API_STR + 'players/62681700/' + WL_LIMIT_STR
MIKE_REQUEST_STR = API_STR + 'players/173836647/' + WL_LIMIT_STR

CARDINAL_DIRECTIONS = [75688374, 107944284, 62681700, 173836647]

SUBMAN_TRACKER = SubmanTracker(bot, 'submen.pkl')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('Do the winds blow?'):
        await message.channel.send('It is an ill wind.')
    await bot.process_commands(message)

@bot.group(pass_context=True)
async def subman(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid subcommandman.')

@subman.command(name='add')
async def subman_add(ctx, arg):
    if int(arg) in CARDINAL_DIRECTIONS:
        await ctx.send('The cardinal directions cannot be submen.')
        return
    if arg.isnumeric() == False:
        await ctx.send('Must be an integer value.')
        return
    if int(arg) in SUBMAN_TRACKER.tracked_list():
        await ctx.send('Subman already tracked.')
        return
    await ctx.send('Adding subman ' + arg)
    SUBMAN_TRACKER.add_subman(int(arg))

@subman.command(name='remove')
async def subman_remove(ctx, arg):
    if int(arg) in CARDINAL_DIRECTIONS:
        await ctx.send('The cardinal directions cannot be submen.')
        return
    if arg.isnumeric() == False:
        await ctx.send('Must be an integer value.')
        return
    if int(arg) not in SUBMAN_TRACKER.tracked_list():
        await ctx.send('Subman not tracked.')
        return
    if int(arg) == 161444478:
        await ctx.send('Draskyl must remain a subman.')
        return
    if int(arg) == 106159118:
        await ctx.send('Jubei must remain a subman.')
        return
    await ctx.send('Removing subman ' + arg)
    SUBMAN_TRACKER.remove_subman(int(arg))

@subman.command(name='tracked')
async def subman_track(ctx):
    submenlist = ''
    for subman in SUBMAN_TRACKER.tracked_list():
        submenlist += str(subman) + '\n'
    embed = discord.Embed(
        color=discord.Color.blue(),
        description = submenlist
    )

    await ctx.send(embed=embed)

@subman.command(name='clear')
async def subman_clear(ctx):
    if ctx.author.id != 125433170047795200:
        await ctx.send('You are not Wizard of Chaos. You will not pass.')
        return
    SUBMAN_TRACKER.clear_submen()
    SUBMAN_TRACKER.add_subman(161444478)
    await ctx.send('Submen cleared.')

def _phrase(number):
    if number > 1.0:
        return 'Calm'
    if number >= .8:
        return 'Gusty'
    if number >= .6:
        return 'Turbulent'
    return 'Stormy'

def _ratio(requeststr):
    data = requests.get(requeststr)
    json = data.json()
    ratio = float(float(json['win']) / (float(json['lose']) + float(json['win'])))
    return ratio

def _subman_APIstr(submanid):
    return API_STR + 'players/' + str(submanid) + '/recentMatches'

def _last_minutes(submanid):
    request = requests.get(_subman_APIstr(submanid))
    recent_json = request.json()[0]
    start_time = recent_json['start_time']
    start_time += recent_json['duration']
    elapsed = time.time() - start_time
    return float(elapsed/60)

@bot.command(name='weather')
async def weather(ctx):
    embed = discord.Embed(
        color=discord.Color.blue(),
        description = f'Weather report for {ctx.author}'
        )
    embed.add_field(name='**Wizard of Chaos:**', value=_phrase(_ratio(WIZ_REQUEST_STR)), inline=True)
    embed.add_field(name='**Snow:**', value=_phrase(_ratio(SNOW_REQUEST_STR)), inline=True)
    embed.add_field(name='**Tint:**', value=_phrase(_ratio(TINT_REQUEST_STR)), inline=True)
    embed.add_field(name='**MxGuire:**', value=_phrase(_ratio(MIKE_REQUEST_STR)), inline=True)

    most_recent = sys.maxsize
    submen_last_hour = 0
    submen_last_ten_min = 0
    for subman in SUBMAN_TRACKER.tracked_list():
        timesince = _last_minutes(subman)
        if timesince < most_recent:
            most_recent = timesince
        if timesince < 60:
            submen_last_hour += 1
        if timesince < 10:
            submen_last_ten_min += 1

    submen = 'Of ' + str(len(SUBMAN_TRACKER.tracked_list())) + ' tracked submen, ' + str(submen_last_ten_min) + ' have queued in the last 10 minutes and ' + str(submen_last_hour) + ' have queued in the last hour.'
    submen += ' The most recent subman queued ' + str(round(most_recent, 2)) + ' minutes ago.'
    embed.add_field(name='**Subman Report:**', value=submen, inline=False)

    jubei_time = _last_minutes(106159118)
    jubei_report = ''
    if jubei_time < 60:
        jubei_report = 'Jubei has queued in the last hour. Exact time: ' + str(round(jubei_time, 2)) + ' minutes ago.'
    else:
        jubei_report = 'Jubei has not queued in the last hour.'
    embed.add_field(name='**Jubei Report:**', value=jubei_report, inline=False)

    await ctx.send(embed=embed)

with open('token.txt', 'r') as tok:
    token = tok.readline()
    print(token)
    bot.run(token)