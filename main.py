import os
from discord import Embed
from discord.ext import commands
from dotenv import load_dotenv

from pymongo import MongoClient

from marks import *


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('DISCORD_PREFIX')

bot = commands.Bot(command_prefix=PREFIX)
bot.remove_command('help')

client = MongoClient("mongodb://localhost/watson_db")
db = client.watson_db

# Get help text
with open("help.txt", 'r') as f:
    help_text = f.read()
help_embed = Embed(title="A propos", description=help_text, colour=0xff0000)


@bot.event
async def on_ready():
    print(f'{bot.user} is online')


@bot.command(name='help')
async def help(ctx: commands.Context):
    await ctx.send(embed=help_embed)


@bot.command(name='moy_suppr')
async def moy_del(ctx: commands.Context):
    db.users.delete_one({'id': ctx.author.id})
    await ctx.send("Votre compte a été supprimé de la base de données")


@bot.command(name='moy')
async def moy(ctx: commands.Context):
    if ctx.author.dm_channel is None:
        await ctx.author.create_dm()

    can_update = True

    if db.users.count_documents({'id': ctx.author.id}) == 0:
        # Get data from user
        username = await get_var(ctx, "Nom d'utilisateur ?")
        password = await get_var(ctx, "Mot de passe ?")
        save = await get_var(ctx, "Voulez-vous sauvegarder vos données dans la base de données ? O/N")
        if save.lower() == "o":
            # Create user entry
            db.users.insert_one({'id': ctx.author.id, 'username': username, 'password': password, 'last_updated': "", 'data': ""})
    else:
        user = db.users.find({'id': ctx.author.id})[0]
        username = user.get('username')
        password = user.get('password')
        # update only happen daily
        can_update = user.get('last_updated') != get_date()

    if can_update:
        await ctx.author.dm_channel.send("Calcul en cours ...")
        text = get_average_text(username, password)
        db.users.update_one({'id': ctx.author.id}, {'$set': {'last_updated': get_date(), 'data': text}})
    else:
        text = user.get('data')

    embed = Embed(title="Moyenne", description=f'```{text}```', colour=0xff0000)
    await ctx.author.dm_channel.send(embed=embed)


def get_average_text(username, password):
    b = get_browser()
    connect(b, username, password)
    marks = get_marks(b)
    b.quit()
    return sort_data(marks)


def get_date():
    time.strftime('%d-%m-%Y', time.localtime())


async def get_var(ctx, text):
    await ctx.author.dm_channel.send(text)
    res = await bot.wait_for('message',
                             check=lambda msg: msg.author == ctx.author and msg.channel == ctx.author.dm_channel)
    return res.content

bot.run(TOKEN)




