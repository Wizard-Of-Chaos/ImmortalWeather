import discord as dc
from discord.ext import commands
from discord import app_commands
import subprocess
from datetime import datetime
from pytz import timezone
import requests

KEVIN_LOCATION = "misc/kevin/kevin.jpg"
CURL_CMD = ["curl", "--http0.9", "http://192.168.1.163/kevin", "--output", KEVIN_LOCATION ]

class KevinCog(commands.Cog):
    def __init__(self, bot):
        print("Initializing lime observation cog...")
        self.bot = bot

    @app_commands.command(name="kevin", description="Get Kevin's current status.")
    async def kevin(self, interaction: dc.Interaction):
        
        # await interaction.response.send_message("Kevin is under maintenance! Here's the last Kevin pic for now: ", file=dc.File(KEVIN_LOCATION))

        cb: dc.InteractionCallbackResponse = await interaction.response.defer(ephemeral=False, thinking=True)
        result = requests.get("http://192.168.1.163/kevin")
        with open(KEVIN_LOCATION, mode='wb') as kevin:
            kevin.write(result.content)
            kevin.close()
        await interaction.followup.send(file=dc.File(KEVIN_LOCATION))
