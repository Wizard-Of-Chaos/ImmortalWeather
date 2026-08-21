import discord as dc
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import aiohttp
import glob
import os

KEVIN_LOCATION:str = "misc/kevin/shots/"
KEVIN_URL:str = "http://192.168.1.163/kevin"

class KevinCog(commands.Cog):
    def __init__(self, bot):
        print("Initializing lime observation cog...")
        self.bot = bot
        print("Lime observation ready!")

    async def _most_recent_kevin(self) -> dc.File:
        list_of_files = glob.glob(KEVIN_LOCATION)
        latest = max(list_of_files, key=os.path.getctime)
        return dc.file(latest)

    def _kevin_fname(self):
        return f"{KEVIN_LOCATION}kevin-{datetime.now().strftime("%s")}.jpg"

    @app_commands.command(name="kevin", description="Get Kevin's current status.")
    async def kevin(self, interaction: dc.Interaction):
        
        # await interaction.response.send_message("Kevin is under maintenance! Here's the last Kevin pic for now: ", file=dc.File(self._kevin_fname()))

        cb: dc.InteractionCallbackResponse = await interaction.response.defer(ephemeral=False, thinking=True)
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                async with session.get(KEVIN_URL) as result:
                    #print(f"Got reply for Kevin on user {interaction.user.name}, HTTP {result.status}")

                    if result.status != 200:
                        await interaction.followup.send(f"HTTP {result.status}. Here's the previous Kevin photo.", file=self._most_recent_kevin())
                        return

                    filename: str = self._kevin_fname()

                    with open(filename, mode='wb') as kevin:
                        while True:
                            content = await result.content.read()
                            if not content:
                                break
                            kevin.write(content)
                        kevin.close()
                        await interaction.followup.send(file=dc.File(filename))

                    #cleanup
                    kevinpic_count = len([name for name in os.listdir(KEVIN_LOCATION) if os.path.isfile(os.path.join(KEVIN_LOCATION, name))])
                    print(f"Kevin pic count: {kevinpic_count}")
                    if kevinpic_count > 20:
                        list_of_files = glob.glob(KEVIN_LOCATION)
                        print("Dropping oldest Kevin")
                        oldest = min(list_of_files, key=os.path.getctime)
                        os.remove(oldest)

        except aiohttp.ClientConnectionError:
            await interaction.followup.send("Connection aborted -- the WiFi probably disconnected again. Here's the previous Kevin photo.", file=self._most_recent_kevin())
        except aiohttp.ServerTimeoutError:
            await interaction.followup.send("Request timed out after 1 minute. Here's the previous Kevin photo.", file=self._most_recent_kevin())
        