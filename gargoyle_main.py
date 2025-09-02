import discord as dc
from discord.ext import commands
from discord.ext.commands import Context as ctx
from discord import app_commands
from submen.subman_cog import SubmanCog
from deadlock.deadlock_cog import DeadlockCog
import asyncio
import user_reg as urg

#glgglrrrogglglghglhghlh
import gargoyle_consts as gargle

intents = dc.Intents.default()
intents.message_content = True

#change prefix for dev to !-
bot = commands.Bot(command_prefix='!!', intents=intents)

#NOTE FOR LATER TODO
#ADD THIS GUY: 287071378 TO TRACKER

@bot.event
async def on_ready():
    await bot.tree.sync(guild=dc.Object(id=132689675981684736))
    print(f'{bot.user} awaiting orders.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('Do the winds blow?'):
        await message.channel.send('It is an ill wind.')
    await bot.process_commands(message)

@bot.tree.command(name='helpme')
async def global_help(ctx):
    embed = dc.Embed(
        color=dc.Color.blue(),
        description='**Gargoyle Help**'
    )
    embed.add_field(name='weather:', value='Determines the general weather system of Dota 2 pubs. Includes personal submen where possible.', inline=False)

    embed.add_field(name='subman register [dota_id]:', value='Registers your Discord ID to your Dota 2 ID.', inline=False)
    embed.add_field(name='subman add [dota_id]:', value='Adds a subman to your personal list of submen. Must be registered.', inline=False)
    embed.add_field(name='subman remove [dota_id]:', value='Removes a subman from your personal list of submen. Must be registered.', inline=False)
    embed.add_field(name='subman tracked:', value='Lists all of your tracked submen IDs. Must be registered.', inline=False)
    embed.add_field(name='myweather:', value='Generates your individualized weather report. Must be registered.', inline=False)
    embed.add_field(name='myinvalids:', value='Checks validity of your submen accounts, listing the invalid ones.', inline=False)

    embed.add_field(name='subman global_add [dota_id]:', value='Adds subman globally. Only available to cardinal winds.', inline=False)
    embed.add_field(name='subman global_remove [dota_id]:', value='Removes subman globally. Only available to cardinal winds.', inline=False)
    embed.add_field(name='subman global_tracked [dota_id]:', value='Lists all global submen.', inline=False)
    embed.add_field(name='invalids:', value='Checks validity of global submen accounts, listing the invalid ones.', inline=False)
    await ctx.send(embed=embed)

@bot.tree.command(name="unregister")
async def unregister_id(ctx: ctx):
    if ctx.author.id in gargle.CARDINAL_IDS:
        await ctx.send("You are one of the four Cardinal Directions and are here forever.")
        return
    urg.REGISTRY.unregister(ctx.author.id)
    await ctx.send("Unregistered your steam ID.")
 

@bot.tree.command(name="register")
async def register_id(ctx: ctx, steam_id: int):
    if ctx.author.id in gargle.CARDINAL_IDS:
        await ctx.send("You are one of the four Cardinal Directions and are already registered.")
        return
    if steam_id in gargle.CARDINAL_DIRECTIONS:
        await ctx.send("You are not one of the four Cardinal Directions and cannot use this ID.")
        return
    
    if urg.REGISTRY.registered(ctx.author.id):
        ctx.send(f"You are already registered as steam ID {urg.REGISTRY.steam_registered_as(ctx.author.id)}. Unregister with `unregister`.")
        return
    
    urg.REGISTRY.register(ctx.author.id, steam_id)
    await ctx.send(f"User ID {ctx.author.id} registered to steam ID {steam_id}.")

async def main():
    async with bot:
        #change txt for dev to token_alt.txt
        with open('token_alt.txt', 'r') as tok:
            token = tok.readline()
            await bot.add_cog(SubmanCog(bot))
            await bot.add_cog(DeadlockCog(bot))
            await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())