import discord as dc
from discord.ext import commands
from discord.ext.commands import Context
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
    async def subman_personal_track(self, ctx):
        submenlist = ''
        for subman in SUBMAN_TRACKER.personal_tracked_list(int(ctx.author.id)):
            submenlist += str(subman) + '\n'
        embed = dc.Embed(
            color=dc.Color.red(),
            description = submenlist
        )

        await ctx.send(embed=embed)
    
    @commands.command(name='myweather')
    async def myweather(self, ctx: Context):
        if SUBMAN_TRACKER.registered(int(ctx.author.id)) == False:
            ctx.send('You are not registered and cannot have personalized weather conditions. Please register with `personal register (your dota id)`.')
            return
        embed = placeholder_personal_embed(ctx.author)
        msg = await ctx.send(embed=embed)
        request_str = wl_request_str(SUBMAN_TRACKER.registered_ids[int(ctx.author.id)])
        embed.set_field_at(0, name='**Your Wind**', value=wl_phrase(wl_ratio_req(request_str)), inline=False)
        msg = await msg.edit(embed=embed)

        submen_tracked = len(SUBMAN_TRACKER.personal_tracked_list(int(ctx.author.id)))
        if submen_tracked > 0:
            most_recent = sys.maxsize
            submen_last_hour = 0
            submen_last_ten_min = 0
            submen_invalid = 0
            subman_counter = 0
            print(submen_tracked)
            for subman in SUBMAN_TRACKER.personal_tracked_list(int(ctx.author.id)):
                timesince = last_minutes_req(subman)
                if timesince is None:
                    submen_invalid += 1
                else:
                    if timesince < most_recent:
                        most_recent = timesince
                    if timesince < 60:
                        submen_last_hour += 1
                    if timesince < 10:
                        submen_last_ten_min += 1
                subman_counter += 1
                print(subman_counter)
                embed.set_field_at(1, name='**Subman Report**', value=f'Evaluated {subman_counter} submen of {submen_tracked} ({submen_invalid} invalid)', inline=False)
                msg = await msg.edit(embed=embed)
            
            round(most_recent, 2)
            valid_submen = submen_tracked - submen_invalid
            submen_percentage = float(submen_last_hour / valid_submen)
            confidence = queue_confidence_factor(False, submen_percentage, submen_last_ten_min, submen_last_hour)
            embed.set_field_at(1, name='**Subman Report**', 
                           value=f"""
                            {submen_last_hour} submen have queued in the past hour, with the most recent at {round(most_recent, 2)} minutes ago (activity: {round(submen_percentage*100,2)}%, {submen_invalid}/{submen_tracked} invalid).
                            {submen_last_ten_min} submen have queued in the past ten minutes.
                            The queue confidence is {round(confidence*100,2)}%.
                           """, inline=False)
            embed.set_field_at(2, name='**Recommendation**', value=f'It is currently **{queue_rec(confidence)}** to queue.', inline=False)
            msg = await msg.edit(embed=embed)

        else:
            embed.set_field_at(1, name='**No Submen Listed**', value='You do not have any tracked submen.', inline=False)
            msg = await msg.edit(embed=embed)

    @commands.command(name='weather')
    async def weather(self, ctx: Context):
        embed = placeholder_global_embed(ctx.author)
        msg = await ctx.send(embed=embed)

        embed.set_field_at(0, name='**Wizard of Chaos**', value=wl_phrase(wl_ratio_req(WIZ_REQUEST_STR)), inline=True)
        msg = await msg.edit(embed=embed)
        embed.set_field_at(1, name='**Snow**', value=wl_phrase(wl_ratio_req(SNOW_REQUEST_STR)), inline=True)
        msg = await msg.edit(embed=embed)
        embed.set_field_at(2, name='**Tint**', value=wl_phrase(wl_ratio_req(TINT_REQUEST_STR)), inline=True)
        msg = await msg.edit(embed=embed)
        embed.set_field_at(3, name='**MxGuire**', value=wl_phrase(wl_ratio_req(MIKE_REQUEST_STR)), inline=True)
        msg = await msg.edit(embed=embed)

        jubei_time = last_minutes_req(106159118)
        jubei_bool = False
        jubei_report = ''
        if jubei_time < 60:
            jubei_report = f'Jubei is on the prowl. Exact time: {round(jubei_time, 2)} minutes ago.'
            jubei_bool = True
        else:
            jubei_report = f'Jubei is dormant.'
        
        embed.set_field_at(4, name='**Jubei Status**', value=jubei_report, inline=True)
        msg = await msg.edit(embed=embed)

        most_recent = sys.maxsize
        submen_last_hour = 0
        submen_last_ten_min = 0
        submen_invalid = 0
        subman_counter = 0
        for subman in SUBMAN_TRACKER.tracked_list():
            timesince = last_minutes_req(subman)
            if timesince is None:
                submen_invalid += 1
            else:
                if timesince < most_recent:
                    most_recent = timesince
                if timesince < 60:
                    submen_last_hour += 1
                if timesince < 10:
                    submen_last_ten_min += 1
            subman_counter += 1
            embed.set_field_at(5, name='**Global Subman Report**', value=f'Evaluated {subman_counter} submen of {SUBMAN_TRACKER.global_submen_count()} ({submen_invalid} invalid)', inline=False)
            msg = await msg.edit(embed=embed)
        
        percent_submen = submen_last_hour / (SUBMAN_TRACKER.global_submen_count() - submen_invalid)
        confidence = queue_confidence_factor(jubei_bool, percent_submen, submen_last_ten_min, submen_last_hour)

        embed.set_field_at(5, name='**Global Subman Report**', value = 
                           f"""
                            {submen_last_hour} submen have queued in the past hour, with the most recent at {round(most_recent, 2)} minutes ago (activity: {round(percent_submen*100,2)}%, {submen_invalid}/{SUBMAN_TRACKER.global_submen_count()} invalid).
                            {submen_last_ten_min} submen have queued in the past ten minutes.
                            The queue confidence is {round(confidence*100,2)}%.
                           """, inline=False)
        embed.set_field_at(6, name='**Recommendation**', value=f'It is currently **{queue_rec(confidence)}** to queue.', inline=False)
        msg =  await msg.edit(embed=embed)
