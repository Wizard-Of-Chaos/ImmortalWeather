import discord as dc
from discord.ext import commands
from discord.ext.commands import Context as ctx
import asyncio
from discord import app_commands
import requests
import user_reg as urg
import datetime
from PIL import Image 

STEAM_API_KEY = ''
with open('api.txt', 'r') as api:
    STEAM_API_KEY = api.readline()
STEAM_API_URL = 'http://api.steampowered.com'

DEADLOCK_API_URL = "https://api.deadlock-api.com/v1"

print("Loading up default Deadlock requests...")
HEROES = requests.get("https://assets.deadlock-api.com/v2/heroes?language=english&only_active=true").json()
ITEMS = requests.get("https://assets.deadlock-api.com/v2/items/by-type/upgrade").json()

def hero_name(id: int) -> str:
    for hero in HEROES:
        if hero["id"] == id:
            return hero["name"]

def get_item(id: int):
    for item in ITEMS:
        if item["id"] == id:
            return item

def is_upgrade(id: int) -> bool:
    for item in ITEMS:
        if item["id"] == id:
            return True
    return False

error_default_embed = dc.Embed(
    color=dc.Color.red(),
    description='**Error**'
)
match_default_embed = dc.Embed(
    color=dc.Color.yellow(),
    description='**Last Match**'
)

class DeadlockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.hybrid_group(name="deadlock", pass_context=True)
    async def deadlock(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Does not meet all 4 conditions for deadlock.')

    @deadlock.command(
            name="lm", 
            description="Gets the last match of the calling player"
            )
    async def last_match(self, ctx: ctx):
        if not urg.REGISTRY.registered(ctx.author.id):
            embed = error_default_embed
            embed.set_field_at(0, name="Reason:", value="You are not registered with the bot. Please use `register steam_id` to register.")
        msg: dc.Message = await ctx.send("Getting match data...")

        steam_id: int = urg.REGISTRY.steam_registered_as(ctx.author.id)

        print(f"Performing request for {steam_id} ({ctx.author})")
        history_request = requests.get(f"{DEADLOCK_API_URL}/players/{steam_id}/match-history")
        print(f"Got history req back: status code {history_request.status_code}")

        if history_request.status_code != 200:
            embed = error_default_embed
            embed.add_field(value=f"Error code {history_request.status_code} on request")
            await ctx.send(embed=error_default_embed)
            return
        
        lm = history_request.json()[0]
        print(lm)
        lm_id = lm["match_id"]
        print(lm_id)

        lm_meta = requests.get(f"{DEADLOCK_API_URL}/matches/{lm_id}/metadata")
    
        if lm_meta.status_code != 200:
            embed = error_default_embed
            embed.add_field(value=f"Error code {history_request.status_code} on most recent match request. Has it been parsed?\n-# request string: {DEADLOCK_API_URL}/matches/{lm_id}/metadata")
            await msg.delete()
            await ctx.send(embed=error_default_embed)
            return

        lm_detailed = lm_meta.json()

        player_details = lm_detailed["match_info"]["players"]
        stats_end = player_details
        for player in lm_detailed["match_info"]["players"]:
            if player["account_id"] != steam_id:
                continue
            player_details = player
            print("Found player in match")
            for stat in player_details["stats"]:
                if stat["time_stamp_s"] == lm["match_duration_s"]:
                    stats_end = stat

        items = player_details["items"]

        match_embed = dc.Embed(
            color=dc.Color.yellow(),
            description=f'**{ctx.author.nick}** achieved **{"Victory" if lm["match_result"] is lm["player_team"] else "Defeat"}** as **{hero_name(lm["hero_id"])}** - {datetime.timedelta(seconds=lm["match_duration_s"])}'
        )
        print("Match embed completed")
        match_embed.add_field(name="Damage", value=f'''
            K/D/A: {lm["player_kills"]}/{lm["player_deaths"]}/{lm["player_assists"]}
            Damage: {stats_end["player_damage"]}
            Healing: {stats_end["player_healing"]}
            Damage Taken: {stats_end["player_damage_taken"]}
            Accuracy: {round((stats_end["shots_hit"] / (stats_end["shots_missed"] + stats_end["shots_hit"])) * 100, 1)}%
        ''')
        print("Damage embed completed")
        match_embed.add_field(name="Net Worth", value=f'''
            Net Worth: {lm["net_worth"]}
            Last Hits: {lm["last_hits"]}
            Denies: {lm["denies"]}
            Level: {lm["hero_level"]}
        ''', inline=True)
        print("Economy embed completed")
        # match_embed.add_field(name="Inventory", value=f"test" inline=True)
        # match_embed.add_field(name="", value=f'-# (View Match)[https://deadlocktracker.gg/matches/{lm_id}], all of these sites suck')
        itemstr: str = ""
        for item in items:
            if item["sold_time_s"] != 0:
                continue
            if is_upgrade(item["item_id"]):
                itemstr = itemstr + f'{get_item(item["item_id"])["name"]}\n'
        match_embed.add_field(name="Inventory", value=itemstr, inline=False)
        match_embed.add_field(name="", value=f"-# match id {lm_id}")
        print("Inventory embed completed")
        await msg.delete()
        await ctx.send(embed=match_embed)