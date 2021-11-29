import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
# load all environment variable
TOKEN = os.getenv('DISCORD_TOKEN')
# get discord token

intents = discord.Intents.all()
# allow priviledged intent
bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)
bot.remove_command('help')
# remove default help commands
# and add our own
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        bot.load_extension(f'cogs.{file[:-3]}')
        # load all commands from cog folder
# set up bot

bot.run(TOKEN)
# run bot
