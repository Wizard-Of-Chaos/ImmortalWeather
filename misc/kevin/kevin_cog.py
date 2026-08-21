import discord as dc
from discord.ext import commands
from discord import app_commands
import subprocess
from datetime import datetime
from pytz import timezone
import aiohttp

KEVIN_LOCATION:str = "misc/kevin/kevin.jpg"
KEVIN_URL:str = "http://192.168.1.163/kevin"

class KevinCog(commands.Cog):
    def __init__(self, bot):
        print("Initializing lime observation cog...")
        self.bot = bot
        print("Lime observation ready!")

    @app_commands.command(name="kevin", description="Get Kevin's current status.")
    async def kevin(self, interaction: dc.Interaction):
        
        # await interaction.response.send_message("Kevin is under maintenance! Here's the last Kevin pic for now: ", file=dc.File(KEVIN_LOCATION))

        cb: dc.InteractionCallbackResponse = await interaction.response.defer(ephemeral=False, thinking=True)
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                async with session.get(KEVIN_URL) as result:
                    #print(f"Got reply for Kevin on user {interaction.user.name}, HTTP {result.status}")

                    if result.status != 200:
                        await interaction.followup.send(f"HTTP {result.status}. Here's the previous Kevin photo.", file=dc.File(KEVIN_LOCATION))
                        return
                    
                    with open(KEVIN_LOCATION, mode='wb') as kevin:
                        while True:
                            content = await result.content.read()
                            if not content:
                                break
                            kevin.write(content)
                        kevin.close()
                        await interaction.followup.send(file=dc.File(KEVIN_LOCATION))

        except aiohttp.ClientConnectionError:
            await interaction.followup.send("Connection aborted -- the WiFi probably disconnected again. Here's the previous Kevin photo.", file=dc.File(KEVIN_LOCATION))
        except aiohttp.ServerTimeoutError:
            await interaction.followup.send("Request timed out after 1 minute. Here's the previous Kevin photo.", file=dc.File(KEVIN_LOCATION))
        