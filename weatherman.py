import discord as dc
from discord.ext import commands
from subman_commands import SubmanCog
import asyncio

intents = dc.Intents.default()
intents.message_content = True

#change prefix for dev to !-
bot = commands.Bot(command_prefix='--', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} awaiting orders.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('Do the winds blow?'):
        await message.channel.send('It is an ill wind.')
    await bot.process_commands(message)

@bot.command(name='helpme')
async def global_help(ctx):
    embed = dc.Embed(
        color=dc.Color.blue(),
        description='**Broken Winds Help**'
    )
    embed.add_field(name='weather:', value='Determines the general weather system of Dota 2 pubs. Includes personal submen where possible.', inline=False)

    embed.add_field(name='subman register [dota_id]:', value='Registers your Discord ID to your Dota 2 ID.', inline=False)
    embed.add_field(name='subman add [dota_id]:', value='Adds a subman to your personal list of submen. Must be registered.', inline=False)
    embed.add_field(name='subman remove [dota_id]:', value='Removes a subman from your personal list of submen. Must be registered.', inline=False)
    embed.add_field(name='subman tracked:', value='Lists all of your tracked submen IDs. Must be registered.', inline=False)
    embed.add_field(name='myweather:', value='Generates your individualized weather report. Must be registered.', inline=False)

    embed.add_field(name='subman global_add [dota_id]:', value='Adds subman globally. Only available to cardinal winds.', inline=False)
    embed.add_field(name='subman global_remove [dota_id]:', value='Removes subman globally. Only available to cardinal winds.', inline=False)
    embed.add_field(name='subman global_tracked [dota_id]:', value='Lists all global submen.', inline=False)

    await ctx.send(embed=embed)

async def main():
    async with bot:
        #change txt for dev to token_alt.txt
        with open('token.txt', 'r') as tok:
            token = tok.readline()
            await bot.add_cog(SubmanCog(bot))
            await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())