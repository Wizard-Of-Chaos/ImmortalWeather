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
    
    @subman.command(name="register")
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
        if SUBMAN_TRACKER.registered(int(ctx.author.id)) == True:
            await ctx.send('WARNING: You are already registered.')
        
        await ctx.send(f'Registering {arg} to discord id {ctx.author.id}')
        SUBMAN_TRACKER.register(ctx.author.id, int(arg))

    @subman.command(name="add")
    async def personal_add(self, ctx:Context, arg):
        print(f'adding subman for author {ctx.author}')
        if SUBMAN_TRACKER.registered(int(ctx.author.id)) == False:
            await ctx.send('You are not registered. Please register first (see `--helpme` for commands).')
            return
        if int(arg) in CARDINAL_DIRECTIONS:
            await ctx.send('The cardinal directions cannot be submen.')
            return
        if arg.isnumeric() == False:
            await ctx.send('Must be an integer value.')
            return
        SUBMAN_TRACKER.add_subman_personal(int(ctx.author.id), int(arg))
        await ctx.send('Added subman to your personal list of submen.')

    @subman.command(name="remove")
    async def personal_remove(self, ctx, arg):
        if SUBMAN_TRACKER.registered(int(ctx.author.id)) == False:
            await ctx.send('You are not registered. Please register first (see `--helpme` for commands).')
            return
        if int(arg) in CARDINAL_DIRECTIONS:
            await ctx.send('The cardinal directions cannot be submen.')
            return
        if arg.isnumeric() == False:
            await ctx.send('Must be an integer value.')
            return
        SUBMAN_TRACKER.remove_subman_personal(int(ctx.author.id), int(arg))
        await ctx.send('Removed subman from your personal list of submen.')
    
    @subman.command(name="clear")
    async def personal_clear(self, ctx):
        if SUBMAN_TRACKER.registered(int(ctx.author.id)) == False:
            await ctx.send('You are not registered. Please register first (see `--helpme` for commands).')
            return
        SUBMAN_TRACKER.clear_submen_personal(int(ctx.author.id))
        await ctx.send('Your personal list of submen has been cleared.')

    @subman.command(name='admin_register')
    async def admin_reg(self, ctx:Context, arg1, arg2):
        if int(ctx.author.id) != 125433170047795200:
            return
        print(f'registering {arg1} to {arg2}')
        SUBMAN_TRACKER.register(int(arg1), int(arg2))
        await ctx.send(f'Registered Discord ID {arg1} to Dota 2 ID {arg2}')
    
    @subman.command(name='whos_registered')
    async def check_regs(self, ctx):
        print(SUBMAN_TRACKER.registered_ids)
        await ctx.send('Printed to console')

    @subman.command(name='tracked')
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
            data = await eval_submen(SUBMAN_TRACKER.personal_tracked_list(int(ctx.author.id)), msg, embed, 1, False)
            data.embed.set_field_at(1, name='**Subman Report**', value = 
                           f"""
                            {data.past_90} submen have queued in the past 90 minutes, with the most recent at {round(data.most_recent, 2)} minutes ago (activity: {round(data.percentage*100,2)}%, {data.invalid_submen}/{data.submen_count} invalid).
                            {data.past_20} submen have queued in the past 20 minutes.
                           """, inline=False)
            data.embed.set_field_at(2, name='**Linear Factor**', value=f'{round(data.lin_factor*100,2)}% | **{queue_rec(data.lin_factor)}**', inline=True)
            data.embed.set_field_at(3, name='**Decay Factor**', value=f'{round(data.decay_factor*100,2)}% | **{queue_rec(data.decay_factor)}**', inline=True)
            msg = await data.msg.edit(embed=embed)

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
        if jubei_time < 90:
            jubei_report = f'Jubei is on the prowl. Exact time: {round(jubei_time, 2)} minutes ago.'
            jubei_bool = True
        else:
            jubei_report = f'Jubei is dormant.'
        
        embed.set_field_at(4, name='**Jubei Status**', value=jubei_report, inline=True)
        msg = await msg.edit(embed=embed)

        data = await eval_submen(SUBMAN_TRACKER.tracked_list(), msg, embed, 5, jubei_bool)
        data.embed.set_field_at(5, name='**Subman Report**', value = 
                           f"""
                            {data.past_90} submen have queued in the past 90 minutes, with the most recent at {round(data.most_recent, 2)} minutes ago (activity: {round(data.percentage*100,2)}%, {data.invalid_submen}/{data.submen_count} invalid).
                            {data.past_20} submen have queued in the past 20 minutes.
                           """, inline=False)
        data.embed.set_field_at(6, name='**Linear Factor**', value=f'{round(data.lin_factor*100,2)}% | **{queue_rec(data.lin_factor)}**', inline=True)
        data.embed.set_field_at(7, name='**Decay Factor**', value=f'{round(data.decay_factor*100,2)}% | **{queue_rec(data.decay_factor)}**', inline=True)

        msg = await data.msg.edit(embed=embed)
