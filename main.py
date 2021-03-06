import os
import atexit

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from pymongo import MongoClient

from bot_commands.timetable_cog import TimetableCog
from bot_commands.teacher_cog import TeacherCog
from bot_commands.marks_cog import MarksCog

from scrappers.timetable import TimetableClient
from scrappers.marks import MarksClient

DRIVER_PATH = "/usr/bin/chromedriver"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = '$'

bot = commands.Bot(command_prefix=PREFIX)
bot.remove_command('help')

client = MongoClient("mongodb://localhost/watson_db")
db = client.watson_db

# Get help text
with open("help.txt", 'r') as f:
    help_text = f.read()
help_embed = discord.Embed(title="A propos", description=help_text, colour=0xff0000)


@bot.event
async def on_ready():
    # await bot.change_presence(activity=discord.Game(name='Sauvetage de semestre'))
    print(f'{bot.user} is online')


@bot.command(name='help')
async def help_custom(ctx: commands.Context):
    await ctx.send(embed=help_embed)


mc = MarksClient(DRIVER_PATH)
tc = TimetableClient(DRIVER_PATH)

bot.add_cog(MarksCog(bot, db, mc))
bot.add_cog(TimetableCog(bot, db, tc))
bot.add_cog(TeacherCog(bot, db))


def shutdown():
    client.close()
    print("\nGoodbye !")


atexit.register(shutdown)
bot.run(TOKEN)

