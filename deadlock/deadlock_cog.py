import discord as dc
from discord.ext import commands
from discord import app_commands
import requests
import user_reg as urg
import datetime
import random
from deadlock.deadlock_item_utils import *
#I consider it an act of restraint on my part to not name the digestion func "Colon"
from deadlock.match_digestion import *

STEAM_API_KEY = ''
with open('api.txt', 'r') as api:
    STEAM_API_KEY = api.readline()
STEAM_API_URL = 'http://api.steampowered.com'

DEADLOCK_API_URL = "https://api.deadlock-api.com/v1"

class DeadlockCog(commands.Cog):
    def __init__(self, bot):
        print("Initializing Deadlock functionality cog...")
        self.bot = bot

    deadlock = app_commands.Group(
        name="deadlock", 
        description="Deadlock functionality."
    )

    #Spits out a digest from the most recent game attached to the steam ID
    #TODO - make it agnostic and capable of just grabbing a random match ID
    async def get_digest(self, steam_id: int, user: str, int_msg: dc.InteractionMessage) -> Digest_lm | None:
        print(f"Performing request for {steam_id} ({user})")
        history_request = requests.get(f"{DEADLOCK_API_URL}/players/{steam_id}/match-history")

        if history_request.status_code != 200:
            await int_msg.edit(content=f"Request failed. Status code: {history_request.status_code}")
            return None
        
        lm = history_request.json()[0]
        lm_meta = requests.get(f"{DEADLOCK_API_URL}/matches/{lm["match_id"]}/metadata")
    
        if lm_meta.status_code != 200:
            await int_msg.edit(content=f"Request failed. Status code: {history_request.status_code}")
            return None
        
        digest: Digest_lm = Digest_lm(steam_id, lm_meta.json())
        return digest
    
    def lane_outcome_str(self, digest: Digest_lm) -> str:
        outcome: str = 'You carried this game.'
        if digest.lane_diff <= 0 and digest.victory:
            outcome = 'You were carried this game.'
        elif digest.lane_diff > 0 and not digest.victory:
            outcome = "This wasn't your fault."
        elif digest.lane_diff <= 0 and not digest.victory:
            outcome = 'This was your fault.'
        return outcome

    @deadlock.command(
            name="lm", 
            description="Gets the last match of the calling player. Must be registered."
            )
    async def last_match(self, interaction: dc.Interaction) -> None:
        user = interaction.user
        cb: dc.InteractionCallbackResponse = await interaction.response.defer(ephemeral=False, thinking=True)
        int_msg: dc.InteractionMessage = cb.resource

        if not urg.REGISTRY.registered(user.id):
            await int_msg.edit(content="You're not registered. Register with `/register")
            return
        steam_id: int = urg.REGISTRY.steam_registered_as(user.id)

        digest = await self.get_digest(steam_id, user.name, int_msg)
        if digest == None:
            print("Digest failure")
            return None

        outcome: str = self.lane_outcome_str(digest)
        
        rank_flavor: str = f"Your **{get_rank_str(digest.player_team_badge)}** team "

        if digest.victory:
            if digest.player_team_badge == digest.enemy_team_badge:
                rank_flavor += "outplayed and outwitted "
            elif digest.player_team_badge > digest.enemy_team_badge:
                rank_flavor += "brutally crushed "
            elif digest.player_team_badge < digest.enemy_team_badge:
                rank_flavor += "skillfully defeated "
        else:
            if digest.player_team_badge == digest.enemy_team_badge:
                rank_flavor += "was barely defeated by "
            elif digest.player_team_badge > digest.enemy_team_badge:
                rank_flavor += "hilariously lost to "
            elif digest.player_team_badge < digest.enemy_team_badge:
                rank_flavor += "expectedly lost to "

        rank_flavor += f"the **{get_rank_str(digest.enemy_team_badge)}** enemy team."

        match_embed = dc.Embed(
            color=dc.Color.yellow(),
            description=f'**{user.nick if user.nick else user.name}** {"achieved **Victory" if digest.victory else "suffered **Defeat"}** as **{hero_name(digest.player_hero)}** - {datetime.timedelta(seconds=digest.duration)}\n-# match id {digest.lm_id}'
        )
        match_embed.add_field(name="Combat", value=f'''
            K/D/A: {digest.kills}/{digest.deaths}/{digest.assists}
            Damage: {digest.player_end_stats["player_damage"]}
            Objective Damage: {digest.player_end_stats["boss_damage"]}
            Healing: {digest.player_end_stats["player_healing"]}
            Damage Taken: {digest.player_end_stats["player_damage_taken"]}
            Accuracy: {round((digest.player_end_stats["shots_hit"] / (digest.player_end_stats["shots_missed"] + digest.player_end_stats["shots_hit"])) * 100, 1)}%
        ''')

        match_embed.add_field(name="Economics", value=f'''
            Net Worth: {digest.player_nw}
            Last Hits: {digest.player_lh}
            Denies: {digest.player_denies}
            Level: {digest.player_lvl}
        ''', inline=True)
        match_embed.add_field(name="Match Details", value=f"""
            Your lane was **{'won' if digest.lane_diff > 0 else 'lost'}** - ** {outcome}**
            Lane soul diff at **9** min: **{digest.lane_diff}k**
            {rank_flavor}
        """, inline=False)
        
        fname = f"inventory-{steam_id}-{digest.lm_id}.png"
        match_embed.set_image(url=f"attachment://{fname}")

        with io.BytesIO() as image_binary:
            dc_image_file(digest.player_items).save(image_binary, 'PNG')
            image_binary.seek(0)
            await int_msg.edit(embed=match_embed, content=None, attachments=[dc.File(fp=image_binary, filename=fname)])

    @deadlock.command(
        name="blame",
        description="Find out EXACTLY who screwed up your last match."
    )
    async def copium(self, interaction: dc.Interaction):
        user = interaction.user
        cb: dc.InteractionCallbackResponse = await interaction.response.defer(ephemeral=False, thinking=True)
        int_msg: dc.InteractionMessage = cb.resource

        if not urg.REGISTRY.registered(user.id):
            await int_msg.edit(content="You're not registered. Register with `/register")
            return
        steam_id: int = urg.REGISTRY.steam_registered_as(user.id)

        digest: Digest_lm = await self.get_digest(steam_id, user.name, int_msg)
        if digest == None:
            print("Digest failure")
            return
        
        embed =  dc.Embed(
            color=dc.Color.red(),
            description='**Last Match**'
        )
        embed.add_field(name="Player Hero", value=f"{hero_name(digest.player_hero)}")
        embed.add_field(name="Match Details", value=f"""
            Your lane was **{'won' if digest.lane_diff > 0 else 'lost'}** - ** {self.lane_outcome_str(digest)}**
            Lane soul diff at **9** min: **{digest.lane_diff}k**
        """)
        embed.add_field(name="Setup", value=f"""
            At 9 minutes, you had **{round(float(digest.player_nw_9)/1000, 1)}k** and your allied **{hero_name(digest.lane_partner_hero)}** had **{round(float(digest.lane_partner_nw_9)/1000, 1)}k.**
            The enemy **{hero_name(digest.lane_opp_0_hero)}** had **{round(float(digest.lane_opp_0_nw_9)/1000, 1)}k** and the enemy **{hero_name(digest.lane_opp_1_hero)}** had **{round(float(digest.lane_opp_1_nw_9)/1000, 1)}k.**
            """,
        inline=False)

        nws = [(digest.player_hero, digest.player_nw_9), 
               (digest.lane_partner_hero, digest.lane_partner_nw_9),
               (digest.lane_opp_0_hero, digest.lane_opp_0_nw_9),
               (digest.lane_opp_1_hero, digest.lane_opp_1_nw_9),
            ]
        loser = min(nws, key= lambda t: t[1])

        embed.add_field(name="Deadweight", value=f"In this lane, the **{hero_name(loser[0])}** was complete deadweight.", inline=False)

        await int_msg.edit(embed=embed, content=None)

    @deadlock.command(
        name="courage",
        description="Are you fearless enough to take this build suggestion?"
    )
    async def courage(self, interaction: dc.Interaction) -> None:
        user = interaction.user
        cb: dc.InteractionCallbackResponse = await interaction.response.defer(ephemeral=False, thinking=True)
        int_msg: dc.InteractionMessage = cb.resource

        embed = dc.Embed(
            color=dc.Color.blue(),
            description=f'**{hero_name(random.choice(HEROES)["id"])}**'
        )
        fname = f"bot-author-not-liable.png"
        embed.set_image(url=f"attachment://{fname}")

        with io.BytesIO() as image_binary:
            randomized_inv_image().save(image_binary, 'PNG')
            image_binary.seek(0)
            await int_msg.edit(embed=embed, content=None, attachments=[dc.File(fp=image_binary, filename=fname)])

    @deadlock.command(
        name="herostats",
        description="Get your personal stats on a given hero."
    )
    @app_commands.describe(hero="Hero in question to pull up stats on.")
    async def hero_stats(self, interaction: dc.Interaction, hero: str) -> None:
        user = interaction.user
        cb: dc.InteractionCallbackResponse = await interaction.response.defer(ephemeral=False, thinking=True)
        int_msg: dc.InteractionMessage = cb.resource

        if not urg.REGISTRY.registered(user.id):
            await int_msg.edit(content="You're not registered. Register with `/register")
            return
        steam_id: int = urg.REGISTRY.steam_registered_as(user.id)

        hero_id = get_hero_id(hero)
        if hero_id == None:
            await int_msg.edit(content="That's not a real hero.")
            return

        hero_req = requests.get(f"{DEADLOCK_API_URL}/players/hero-stats?account_ids={steam_id}")
        if hero_req.status_code != 200:
            await int_msg.edit(content=f"Request failed. Status code: {hero_req.status_code}")
            return None
        
        data = hero_req.json()

        hero_stat = None
        for hero in data:
            if hero["hero_id"] == hero_id:
                hero_stat = hero
        
        matches = hero_stat["matches_played"]

        embed = dc.Embed(
            color=dc.Color.gold(),
            description=f'**{user.nick if user.nick else user.name}** as **{hero_name(hero_id)}**'
        )
        embed.add_field(name="Overall", value=f"""
            {hero_stat["wins"]} in {matches} matches (**{round((float(hero_stat["wins"]) / float(matches)) * 100, 2) }% winrate**)
        """, inline=False)

        embed.add_field(name="Combat", value=f"""
            Average kills: **{round(float(hero_stat["kills"]) / float(matches), 1)}**
            Average deaths: **{round(float(hero_stat["deaths"]) / float(matches), 1)}**
            Average assists: **{round(float(hero_stat["assists"]) / float(matches), 1)}**
            Damage per minute: **{round(hero_stat["damage_per_min"], 1)}**
            Objective damage per minute: **{round(hero_stat["obj_damage_per_min"], 1)}**
            Damage taken per minute: **{round(hero_stat["damage_taken_per_min"], 1)}**
            Accuracy: **{round(float(hero_stat["accuracy"]) * 100, 1)}%**
            Headshot rate: **{round(float(hero_stat["crit_shot_rate"]) * 100, 1)}%**
        """)

        embed.add_field(name="Economics", value=f"""
            Average level: **{round(float(hero_stat["ending_level"]), 1)}**
            Net worth per minute: **{round(hero_stat["networth_per_min"], 1)}**
            Creeps per minute: **{round(hero_stat["creeps_per_min"], 1)}**
            Damage per soul: **{round(hero_stat["damage_per_soul"], 3)}**
            Objective damage per soul: **{round(hero_stat["obj_damage_per_soul"], 3)}**
        """)

        await int_msg.edit(embed=embed)
    @deadlock.command(
        name="meta-roulette",
        description="Gets a build for the given hero in an Eternus game."
    )
    @app_commands.describe(hero="Hero in question to pull up stats on.")
    async def hero_stats(self, interaction: dc.Interaction, hero: str) -> None:
        user = interaction.user
        cb: dc.InteractionCallbackResponse = await interaction.response.defer(ephemeral=False, thinking=True)
        int_msg: dc.InteractionMessage = cb.resource

        hero_id = get_hero_id(hero)
        if hero_id == None:
            await int_msg.edit(content="That's not a real hero.")
            return

        eternus_req = requests.get(f"{DEADLOCK_API_URL}/matches/metadata?include_objectives=true&include_mid_boss=true&include_player_info=true&include_player_items=true&include_player_stats=true&include_player_death_details=true&min_average_badge=110&order_by=match_id&order_direction=desc&limit=200")
        if eternus_req.status_code != 200:
            await int_msg.edit(content=f"Request failed. Status code: {eternus_req.status_code}")
            return None

        #player_id: int = None
        #match_data = None
        matches = []

        # print(match_data)
        for match in eternus_req.json():
            for player in match["players"]:
                if player["hero_id"] == hero_id:
                    #print("found a match!")
                    json_dat = json.loads("{}")
                    json_dat["match_info"] = match
                    matches.append((player["account_id"], json_dat))

                    #match_data["match_info"] = match
                    #player_id = player["account_id"]
                    #match_id = match["match_id"]
                    #break
            #if player_id != None:
                #break

        if len(matches) == 0:
            await int_msg.edit(content=f"Unable to find an appropriate Eternus game for {hero_name(hero_id)}.")
            return None
        # print(match_data)

        which = random.choice(matches)

        digest = Digest_lm(which[0], which[1])

        match_embed = dc.Embed(
            color=dc.Color.green(),
            description=f'Some random Eternus freak just pulled this shit as **{hero_name(hero_id)}** (they **{'won' if digest.victory else 'lost'}** in {datetime.timedelta(seconds=digest.duration)})\n-# match id {digest.lm_id}'
        )

        match_embed.add_field(name="Combat", value=f'''
            K/D/A: {digest.kills}/{digest.deaths}/{digest.assists}
            Damage: {digest.player_end_stats["player_damage"]}
            Objective Damage: {digest.player_end_stats["boss_damage"]}
            Healing: {digest.player_end_stats["player_healing"]}
            Damage Taken: {digest.player_end_stats["player_damage_taken"]}
            Accuracy: {round((digest.player_end_stats["shots_hit"] / (digest.player_end_stats["shots_missed"] + digest.player_end_stats["shots_hit"])) * 100, 1)}%
        ''')

        match_embed.add_field(name="Economics", value=f'''
            Net Worth: {digest.player_nw}
            Last Hits: {digest.player_lh}
            Denies: {digest.player_denies}
            Level: {digest.player_lvl}
        ''', inline=True)
        match_embed.add_field(name="Match Details", value=f"""
            Their lane was **{'won' if digest.lane_diff > 0 else 'lost'}**.
            Lane soul diff at **9** min: **{digest.lane_diff}k**
        """, inline=False)

        fname = f"inventory-{which[0]}-{digest.lm_id}.png"
        match_embed.set_image(url=f"attachment://{fname}")

        with io.BytesIO() as image_binary:
            dc_image_file(digest.player_items).save(image_binary, 'PNG')
            image_binary.seek(0)
            await int_msg.edit(embed=match_embed, content=None, attachments=[dc.File(fp=image_binary, filename=fname)])
