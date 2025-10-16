import discord as dc
import discord.interactions as interacts
from discord.ext import commands
from discord.ext.commands import Context as ctx
from discord import app_commands
from submen.subman_cog import SubmanCog
from deadlock.deadlock_cog import DeadlockCog
from datetime import datetime, timezone
from misc.dinnertime import DinnerStorage as din
import random
import asyncio
import requests
#urrrrrrrgg... my user...
import user_reg as urg
#glgglrrrogglglghglhghlh
import gargoyle_consts as gargle

prefix: str = "!!"
token_str: str = "token_alt.txt"

_DINNERS = din('misc/storage/dinners.pkl')

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
    print(f"Synchronizing commands for guild id {ctx.guild.id}.")
    bot.tree.copy_global_to(guild=ctx.guild)
    cmd_list = await bot.tree.sync(guild=ctx.guild)
    print(f'{len(cmd_list)} commands were synchronized to guild {ctx.guild.id}.')
    
@bot.tree.command(name="register", description="Register your Steam ID to your Discord ID for use with the bot. Use `/steam_id3` to get yours.")
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
    await interaction.response.send_message(f"User ID {interaction.user.id} registered to steam ID {steam_id}.")

@bot.tree.command(name="unregister", description="Unregister your Steam ID from your Discord ID.")
async def unregister(interaction: dc.Interaction):
    if interaction.user.id in gargle.CARDINAL_IDS:
        await interaction.response.send_message("You are one of the four Cardinal Directions and are here forever.")
        return
    urg.REGISTRY.unregister(interaction.user.id)
    await interaction.response.send_message("Unregistered your steam ID.")

@bot.tree.command(name="steam_id3", description="Get your steam ID for use with `/register`.")
@app_commands.describe(profile_link="Your steam profile link.")
async def steam_id3(interaction: dc.Interaction, profile_link:str):
    req = requests.get(profile_link)
    if req.status_code != 200:
        await interaction.response.send_message(f"Your link returned {req.status_code}. Try again with a real link.")
        return
    steam_id = int(req.text.split("\"steamid\":\"")[1].split("\"")[0])
    mask = (1 << 32) - 1
    print(f"steam ID3 for account link {profile_link}: {steam_id & mask}")
    await interaction.response.send_message(f"Your steam ID3 is `{steam_id & mask}`.")

@bot.tree.command(name="universal_spice", description="In case you forgot.")
async def universal_spice(interaction: dc.Interaction):
    await interaction.response.send_message("The 'Universal Spice' refers to either [Montreal Steak Seasoning](<https://www.mccormick.com/products/mccormick-grill-mates-montreal-steak-seasoning-3-4-oz>!!) OR\n3 tbsp the aforementioned seasoning\n1 tsp garlic powder\n1/2 tsp chili powder\n1/2 tsp oregano\n1/2 tsp thyme")

@bot.tree.command(name="dinner", description="What the hell should I make for dinner?")
async def dinnertime(interaction: dc.Interaction):
    await interaction.response.send_message(random.choice(_DINNERS.dinners))

@bot.tree.command(name="confess", description="Confess your sins to the gargoyle.")
@app_commands.describe(confession="What do you have to say for yourself?")
async def confessional(interaction: dc.Interaction, confession:str):
    salvation_options: list[str] = [
        "You are **forgiven**.",
        "There is no hope. You are **damned**.",
        "You are **forgiven if you apologize**.",
        "I don't **care**. No ruling.",
        "You are **forgiven** if you describe your purpose in sinning.",
        "You are **forgiven** if you ping whoever you wronged with a cat video.",
        "You are **damned** unless you can get Dave to say otherwise.",
        "If you have **dirty dishes** in your room, you are **damned**, otherwise you are **forgiven**.",
        "Huh?",
        "You are **damned** if you have not **eaten a vegetable** today, otherwise you are **forgiven**.",
        "Your salvation would be inconvenient - **purgatory** for this sin.",
        "You are **forgiven** for this and your **next sin.**",
        "You are **damned** for this and your **next sin.**",
        "Morality is subjective. No ruling.",
        "You are **damned** unless your name is Ryan or Will.",
        "You are **forgiven** for three hours, at which point you will be **damned** if you have not completed an MSPaint drawing of your sin.",
        "You are **forgiven** if you make up a guy and submit your guy for judgment by the council.",
        "You **lack the divine spark** and therefore are not capable of damnation or salvation.",
        "You are **forgiven** if you can get ChatGPT to say that you are **damned**."
    ]    
    await interaction.response.send_message(f'For your confession of "{confession}":\n\n{random.choice(salvation_options)}')

@bot.tree.command(name="contribute", description="How does one contribute to Gargoyle?!")
async def contribute(interaction: dc.Interaction):
    embed = dc.Embed(
        color=dc.Color.dark_blue(),
    )
    embed.add_field(
        name="", value=f"""
        Do you have a friend or a relative who would make a valuable contribution to **Gargoyle**?
        Then encourage them to [submit a pull request](<https://github.com/Wizard-Of-Chaos/ImmortalWeather>) here.
        We are **always** looking for new PRs to completely ignore!
        """
    )
    await interaction.response.send_message(embed=embed)

#######################################################################################################

@bot.command(name="add_dinner")
async def add_dinner(ctx: ctx, *, dinner):
    if ctx.author.id != 125433170047795200:
        await ctx.send("Recipes must be vetted by bot author")
        return
    # print(dinner)
    _DINNERS.dinners.append(dinner)
    _DINNERS.save()
    await ctx.send("Added the recipe to possible dinner suggestions.")

@bot.command(name="moron_reg", description="Manually register a moron")
async def moron_reg(ctx: ctx, steam_id: int, disc_id:str):
    if ctx.author.id not in gargle.CARDINAL_IDS:
        await ctx.send("not for you fat boy")
        return
    if urg.REGISTRY.registered(disc_id):
        await ctx.send("already registered")
        return
    print(f"registering {int(disc_id)}, {steam_id}")
    urg.REGISTRY.register(int(disc_id), steam_id)
    await ctx.send(f"Moron {disc_id} registered to steam ID {steam_id}.")

@bot.command(name="moron_unreg", description="Manuallyy unregister a moron")
async def moron_unreg(ctx: ctx, disc_id:str):
    if ctx.author.id not in gargle.CARDINAL_IDS:
        await ctx.send("not for you fat boy")
        return
    urg.REGISTRY.unregister(disc_id)
    await ctx.send(f"Moron {disc_id} unregistered.")

#######################################################################################################

def get_token() -> str:
    with open(token_str, 'r') as tok:
        token = tok.readline()
        return token

if __name__ == "__main__":
    bot.run(get_token())