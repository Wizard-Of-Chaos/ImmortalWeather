import discord as dc
import discord.interactions as interacts
from discord.ext import commands
from discord.ext.commands import Context as ctx
from discord import app_commands
from submen.subman_cog import SubmanCog
from deadlock.deadlock_cog import DeadlockCog
from datetime import datetime, timezone

import asyncio
#urrrrrrrgg... my user...
import user_reg as urg
#glgglrrrogglglghglhghlh
import gargoyle_consts as gargle

prefix: str = "!!"
token_str: str = "token_alt.txt"

class Bot(commands.Bot):
    uptime: datetime = datetime.now(timezone.utc)
    user: dc.ClientUser

    def __init__(self, *, intents: dc.Intents):
        super().__init__(command_prefix=prefix, intents=intents)
        # self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=dc.Object(id=132689675981684736))
        await self.tree.sync(guild=dc.Object(id=132689675981684736))

intents = dc.Intents.default()
intents.message_content = True
bot = Bot(intents=intents)

@bot.event
async def on_ready():
    await bot.add_cog(DeadlockCog(bot))
    await bot.setup_hook()
    print(f'{bot.user} ready.')

@bot.command(name="sync")
async def sync(ctx: ctx):
    print("Synchronizing commands")
    bot.tree.copy_global_to(guild=ctx.guild)
    cmd_list = await bot.tree.sync(guild=ctx.guild)
    print(len(cmd_list))

@bot.tree.command()
async def slahser(interaction: dc.Interaction):
    """Slahser's way."""
    await interaction.response.send_message("BUY A BUNCH OF FUCKING SALVES AND USE THEM IN CHRONO")

@bot.tree.command(name="register", description="Register your Steam ID to your Discord ID for use with the bot.")
@app_commands.describe(steam_id="Your steam ID (ID3).")
async def register(interaction: dc.Interaction, steam_id: int):
    if interaction.user.id in gargle.CARDINAL_IDS:
        await interaction.response.send_message("You are one of the four Cardinal Directions and are already registered.")
        return
    if steam_id in gargle.CARDINAL_DIRECTIONS:
        await interaction.response.send_message("You are not one of the four Cardinal Directions and cannot use this ID.")
        return
    
    if urg.REGISTRY.registered(interaction.user.id):
        interaction.response.send_message(f"You are already registered as steam ID {urg.REGISTRY.steam_registered_as(interaction.user.id)}. Unregister with `unregister`.")
        return
    urg.REGISTRY.register(interaction.user.id, steam_id)
    await interaction.response.send_message(f"User ID {ctx.author.id} registered to steam ID {steam_id}.")

@bot.tree.command(name="unregister", description="Unregister your Steam ID from your Discord ID.")
async def unregister(interaction: dc.Interaction):
    if interaction.user.id in gargle.CARDINAL_IDS:
        await interaction.response.send_message("You are one of the four Cardinal Directions and are here forever.")
        return
    urg.REGISTRY.unregister(ctx.author.id)
    await interaction.response.send_message("Unregistered your steam ID.")

#######################################################################################################

def get_token() -> str:
    with open(token_str, 'r') as tok:
        token = tok.readline()
        return token

if __name__ == "__main__":
    bot.run(get_token())