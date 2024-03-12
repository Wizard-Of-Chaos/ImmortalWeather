import discord as dc
from discord.ext import commands
import requests
from submantracker import SubmanTracker, CARDINAL_DIRECTIONS, CARDINAL_IDS
import time
import sys
from subman_utils import *

SUBMAN_TRACKER = SubmanTracker('submen.pkl', 'submen_personal.pkl', 'id_reg.pkl')

class SubmanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.group(pass_context=True)
    async def subman(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid subcommandman.')

    @subman.command(name='global_add')
    async def subman_add(self, ctx, arg):
        if ctx.author.id not in CARDINAL_IDS:
            await ctx.send('Global subman updates only permitted to cardinal directions of the EST-SUN winds.')
            return
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
        SUBMAN_TRACKER.add_subman_global(int(arg))

    @subman.command(name='global_remove')
    async def subman_remove(self, ctx, arg):
        if ctx.author.id not in CARDINAL_IDS:
            await ctx.send('Global subman updates only permitted to cardinal directions of the EST-SUN winds.')
            return
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
        SUBMAN_TRACKER.remove_subman_global(int(arg))

    @subman.command(name='global_tracked')
    async def subman_track(self, ctx):
        submenlist = ''
        for subman in SUBMAN_TRACKER.tracked_list():
            submenlist += str(subman) + '\n'
        embed = dc.Embed(
            color=dc.Color.blue(),
            description = submenlist
        )

        await ctx.send(embed=embed)

    @subman.command(name='clearall')
    async def subman_clear_global(self, ctx):
        if ctx.author.id != 125433170047795200:
            await ctx.send('You are not Wizard of Chaos. You will not pass.')
            return
        SUBMAN_TRACKER.clear_submen_global()
        SUBMAN_TRACKER.add_subman_global(161444478)
        SUBMAN_TRACKER.add_subman_global(106159118)
        await ctx.send('Submen cleared.')

    @subman.group(pass_context=True)
    async def personal(self, ctx):
        if SUBMAN_TRACKER.registered(ctx.author.id) == False:
            await ctx.send('You are not properly registered. Do that with `personal register (your dota id)`.')
            return
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid personal subcommandman.')
    
    @personal.command(name="register")
    async def register(self, ctx, arg):
        if arg.isnumeric() == False:
            await ctx.send('You did not use a number. Try again.')
            return
        if int(ctx.author.id) in CARDINAL_IDS:
            await ctx.send('You are a cardinal direction and are already registered.')
            return
        if int(arg) in CARDINAL_DIRECTIONS:
            await ctx.send('Imposter.')
            return
        registered = SUBMAN_TRACKER.registered_as(int(arg))
        if registered != None and registered != ctx.author.id:
            await ctx.send('That ID is already registered to another user.')
            return
        if SUBMAN_TRACKER.registered(int(arg)) == True:
            await ctx.send('WARNING: You are already registered.')
        
        await ctx.send(f'Registering {arg} to discord id {ctx.author.id}')
        SUBMAN_TRACKER.register(ctx.author.id, int(arg))


    @personal.command(name="add")
    async def personal_add(self, ctx, arg):
        if int(arg) in CARDINAL_DIRECTIONS:
            await ctx.send('The cardinal directions cannot be submen.')
            return
        if arg.isnumeric() == False:
            await ctx.send('Must be an integer value.')
            return
        SUBMAN_TRACKER.add_subman_personal(int(ctx.author.id), int(arg))
        await ctx.send('Added subman to your personal list of submen.')

    @personal.command(name="remove")
    async def personal_remove(self, ctx, arg):
        if int(arg) in CARDINAL_DIRECTIONS:
            await ctx.send('The cardinal directions cannot be submen.')
            return
        if arg.isnumeric() == False:
            await ctx.send('Must be an integer value.')
            return
        SUBMAN_TRACKER.remove_subman_personal(int(ctx.author.id), int(arg))
        await ctx.send('Removed subman from your personal list of submen.')
    
    @personal.command(name="clear")
    async def personal_clear(self, ctx):
        SUBMAN_TRACKER.clear_submen_personal(int(ctx.author.id))
        await ctx.send('Your personal list of submen has been cleared.')
    
    @personal.command(name='tracked')
    async def subman_track(self, ctx):
        submenlist = ''
        for subman in SUBMAN_TRACKER.personal_tracked_list(int(ctx.author.id)):
            submenlist += str(subman) + '\n'
        embed = dc.Embed(
            color=dc.Color.red(),
            description = submenlist
        )

        await ctx.send(embed=embed)
    
    @commands.command(name='myweather')
    async def myweather(self, ctx):
        if SUBMAN_TRACKER.registered(int(ctx.author.id)) == False:
            ctx.send('You are not registered and cannot have personalized weather conditions. Please register with `personal register (your dota id)`.')
            return
        embed = dc.Embed(
            color = dc.Color.red(),
            description = f'Personal weather report for {ctx.author}'
        )
        request_str = wl_request_str(SUBMAN_TRACKER.registered_ids[int(ctx.author.id)])
        embed.add_field(name='**Your wind is:**', value=wl_phrase(wl_ratio_req(request_str)), inline=True)
        if len(SUBMAN_TRACKER.personal_tracked_list(int(ctx.author.id))) > 0:
            most_recent = sys.maxsize
            submen_last_hour = 0
            submen_last_ten_min = 0
            for subman in SUBMAN_TRACKER.personal_tracked_list(int(ctx.author.id)):
                timesince = last_minutes_req(subman)
                if timesince < most_recent:
                    most_recent = timesince
                if timesince < 60:
                    submen_last_hour += 1
                if timesince < 10:
                    submen_last_ten_min += 1
            round(most_recent, 2)
            jubei_factor = bool(last_minutes_req(106159118) < 60)
            submen_percentage = float(submen_last_hour / len(SUBMAN_TRACKER.personal_tracked_list(int(ctx.author.id))))
            confidence = queue_confidence_factor(jubei_factor, submen_percentage, submen_last_ten_min, submen_last_hour)
            embed.add_field(name='**Queue Confidence Factor:**', value=f'{round(confidence*100, 2)}%. Queueing right now would be **{queue_rec(confidence)}.**', inline=False)
            embed.add_field(name='**Personal Subman Report:**', 
                            value=f"""From your personal list, there have been {submen_last_ten_min} in the last ten minutes and {submen_last_hour} in the last hour. 
                            You have {len(SUBMAN_TRACKER.personal_tracked_list(ctx.author.id))} submen tracked in total. 
                            The most recent subman was {round(most_recent, 2)} minutes ago.""", 
                            inline=False)
        else:
            embed.add_field(name='**No Submen Listed:**', value='You do not have any tracked submen.', inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='weather')
    async def weather(self, ctx):
        embed = dc.Embed(
            color=dc.Color.blue(),
            description = f'Weather report for {ctx.author}'
            )
        embed.add_field(name='**Wizard of Chaos:**', value=wl_phrase(wl_ratio_req(WIZ_REQUEST_STR)), inline=True)
        embed.add_field(name='**Snow:**', value=wl_phrase(wl_ratio_req(SNOW_REQUEST_STR)), inline=True)
        embed.add_field(name='**Tint:**', value=wl_phrase(wl_ratio_req(TINT_REQUEST_STR)), inline=True)
        embed.add_field(name='**MxGuire:**', value=wl_phrase(wl_ratio_req(MIKE_REQUEST_STR)), inline=True)

        most_recent = sys.maxsize
        submen_last_hour = 0
        submen_last_ten_min = 0
        for subman in SUBMAN_TRACKER.tracked_list():
            timesince = last_minutes_req(subman)
            if timesince < most_recent:
                most_recent = timesince
            if timesince < 60:
                submen_last_hour += 1
            if timesince < 10:
                submen_last_ten_min += 1

        embed.add_field(name='**Global Subman Report:**', 
                        value=f"""Of {len(SUBMAN_TRACKER.tracked_list())} tracked submen, {submen_last_ten_min} have queued in the last 10 minutes and {submen_last_hour} have queued in the last hour. 
                        There are {len(SUBMAN_TRACKER.tracked_list())} total tracked submen globally from the cardinal directions. 
                        The most recent subman queued {round(most_recent, 2)} minutes ago.""",
                         inline=False)

        jubei_time = last_minutes_req(106159118)
        jubei_report = ''
        if jubei_time < 60:
            jubei_report = f'Jubei has queued in the last hour. Exact time: {round(jubei_time, 2)} minutes ago.'
        else:
            jubei_report = f'Jubei has not queued in the last hour.'
        embed.add_field(name='**Jubei Report:**', value=jubei_report, inline=False)

        if SUBMAN_TRACKER.registered(int(ctx.author.id)) == True and len(SUBMAN_TRACKER.personal_tracked_list(int(ctx.author.id))) > 0:
            most_recent = sys.maxsize
            submen_last_hour = 0
            submen_last_ten_min = 0
            for subman in SUBMAN_TRACKER.personal_tracked_list(int(ctx.author.id)):
                timesince = last_minutes_req(subman)
                if timesince < most_recent:
                    most_recent = timesince
                if timesince < 60:
                    submen_last_hour += 1
                if timesince < 10:
                    submen_last_ten_min += 1
            round(most_recent, 2)
            embed.add_field(name='**Personal Subman Report:**', 
                            value=f"""From your personal list, there have been {submen_last_ten_min} in the last ten minutes and {submen_last_hour} in the last hour. 
                            You have {len(SUBMAN_TRACKER.personal_tracked_list(ctx.author.id))} submen tracked in total. 
                            The most recent subman was {round(most_recent, 2)} minutes ago.""", 
                            inline=False)
            
        await ctx.send(embed=embed)
