import discord as dc
from discord.ext import commands
from discord import app_commands
import requests
import user_reg as urg
import datetime
import random
from deadlock.deadlock_item_utils import *

STEAM_API_KEY = ''
with open('api.txt', 'r') as api:
    STEAM_API_KEY = api.readline()
STEAM_API_URL = 'http://api.steampowered.com'

DEADLOCK_API_URL = "https://api.deadlock-api.com/v1"

HEROES = requests.get("https://assets.deadlock-api.com/v2/heroes?language=english&only_active=true").json()

def hero_name(id: int) -> str:
    for hero in HEROES:
        if hero["id"] == id:
            return hero["name"]

error_default_embed = dc.Embed(
    color=dc.Color.red(),
    description='**Error**'
)
match_default_embed = dc.Embed(
    color=dc.Color.yellow(),
    description='**Last Match**'
)

def get_player_networth_9min(data, playerdata) -> int:
    for stat in playerdata["stats"]:
        if stat["time_stamp_s"] == 900:
            return stat["net_worth"]


def get_player_lane_diff(data, team, lane) -> float:
    soulcount_0 = 0
    soulcount_1 = 0
    print("getting lane diff")
    for player in data["match_info"]["players"]:
        if player["assigned_lane"] == lane:
            if player["team"] == team:
                soulcount_0 += get_player_networth_9min(data, player)
            else:
                soulcount_1 += get_player_networth_9min(data, player)
    
    return round(float(soulcount_0 - soulcount_1) / 1000.0, 1)

class DeadlockCog(commands.Cog):
    def __init__(self, bot):
        print("Initializing Deadlock functionality cog.")
        self.bot = bot

    deadlock = app_commands.Group(
        name="deadlock", 
        description="Deadlock functionality."
    )

    @deadlock.command(
            name="lm", 
            description="Gets the last match of the calling player. Must be registered."
            )
    async def last_match(self, interaction: dc.Interaction) -> None:
        user = interaction.user
        cb: dc.InteractionCallbackResponse = await interaction.response.defer(ephemeral=False, thinking=True)
        int_msg: dc.InteractionMessage = cb.resource

        if not urg.REGISTRY.registered(user.id):
            embed = error_default_embed
            embed.set_field_at(0, name="Reason:", value="You are not registered with the bot. Please use `register steam_id` to register.")
            int_msg.delete()
            await interaction.channel.send(embed=embed)
            return

        steam_id: int = urg.REGISTRY.steam_registered_as(user.id)

        print(f"Performing request for {steam_id} ({user.name})")
        history_request = requests.get(f"{DEADLOCK_API_URL}/players/{steam_id}/match-history")
        print(f"Got history req back: status code {history_request.status_code}")

        if history_request.status_code != 200:
            embed = error_default_embed
            embed.add_field(value=f"Error code {history_request.status_code} on request.")
            await int_msg.delete()
            await interaction.channel.send(embed=embed)
            return
        
        lm = history_request.json()[0]
        print(lm)
        lm_id = lm["match_id"]
        print(lm_id)

        lm_meta = requests.get(f"{DEADLOCK_API_URL}/matches/{lm_id}/metadata")
    
        if lm_meta.status_code != 200:
            embed = error_default_embed
            embed.add_field(value=f"Error code {history_request.status_code} on most recent match request. Has it been parsed?\n -# request string: {DEADLOCK_API_URL}/matches/{lm_id}/metadata")
            await int_msg.delete()
            await interaction.channel.send(embed=embed)
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

        player_victory: bool = lm["match_result"] is lm["player_team"]
        lanediff: float = get_player_lane_diff(lm_detailed, player_details["team"], player_details["assigned_lane"])
        outcome: str = 'You carried this game.'
        if lanediff <= 0 and player_victory:
            outcome = 'You were carried this game.'
        elif lanediff > 0 and not player_victory:
            outcome = "This wasn't your fault."
        elif lanediff <= 0 and not player_victory:
            outcome = 'This was your fault.'

        match_embed = dc.Embed(
            color=dc.Color.yellow(),
            description=f'**{user.nick if user.nick else user.name}** {"achieved **Victory" if lm["match_result"] is lm["player_team"] else "suffered **Defeat"}** as **{hero_name(lm["hero_id"])}** - {datetime.timedelta(seconds=lm["match_duration_s"])}\n-# match id {lm_id}'
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
        match_embed.add_field(name="Economics", value=f'''
            Net Worth: {lm["net_worth"]}
            Last Hits: {lm["last_hits"]}
            Denies: {lm["denies"]}
            Level: {lm["hero_level"]}
        ''', inline=True)

        print("Economy embed completed")

        match_embed.add_field(name="Laning", value=f"""
                              Your lane was **{'won' if lanediff > 0 else 'lost'}** - ** {outcome}**\nLane soul diff at 8 min: {lanediff}k
                              """, inline=False)
        print("Laning embed completed")
        fname = f"inventory-{steam_id}-{lm_id}.png"
        match_embed.set_image(url=f"attachment://{fname}")
        print("Inventory embed completed")

        with io.BytesIO() as image_binary:
            dc_image_file(items).save(image_binary, 'PNG')
            image_binary.seek(0)
            await int_msg.edit(embed=match_embed, content=None, attachments=[dc.File(fp=image_binary, filename=fname)])
            # await interaction.channel.send(embed=match_embed, file=dc.File(fp=image_binary, filename=fname))