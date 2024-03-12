import discord as dc
from discord.ext import commands
from subman_commands import SubmanCog
import asyncio
intents = dc.Intents.default()
intents.message_content = True
#change prefix for dev
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

async def main():
    async with bot:
        #change txt for dev
        with open('token.txt', 'r') as tok:
            token = tok.readline()
            await bot.add_cog(SubmanCog(bot))
            await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())