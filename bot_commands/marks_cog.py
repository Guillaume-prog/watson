from discord.ext import commands

from discord.ext.commands import Bot, Context, Cog
from scrappers.marks import MarksClient

from urllib3.exceptions import *

import discord
import util


class MarksCog(Cog):

    def __init__(self, bot: Bot, db, marks_client: MarksClient):
        self.bot = bot
        self.db = db
        self.mc = marks_client

    @commands.group(name='moyenne', aliases=['moy'])
    async def moy(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await self.calc_moy(ctx)

    async def calc_moy(self, ctx: Context):
        print(f"\n{ctx.author} (moy) - Calculating average")

        if ctx.author.dm_channel is None:
            await ctx.author.create_dm()

        can_update = True
        marks = {}

        if self.db.users.count_documents({'id': ctx.author.id}) == 0:
            # Get data from user
            username = await util.get_dm_var(self.bot, ctx, "Nom d'utilisateur ?")
            password = await util.get_dm_var(self.bot, ctx, "Mot de passe ?")
            save = await util.get_dm_var(self.bot, ctx,
                                         "Voulez-vous sauvegarder vos données dans la base de données ? O/N")
            if save.lower() == "o":
                # Create user entry
                self.db.users.insert_one(
                    {'id': ctx.author.id, 'username': username, 'password': password, 'last_updated': "", 'data': ""})
        else:
            user = self.db.users.find_one({'id': ctx.author.id})
            username = user.get('username')
            password = user.get('password')
            # update only happen daily
            can_update = user.get('last_updated') != util.get_date()

            if not can_update:
                marks = user.get('data')

        if can_update:
            message = await ctx.author.dm_channel.send("Attente de disponibilité du service ...")
            self.mc.wait_until_available()

            await message.edit(content="Calcul en cours ...")

            try:
                marks = self.mc.get_marks(username, password)
                self.db.users.update_one({'id': ctx.author.id}, {'$set': {'last_updated': util.get_date(), 'data': marks}})
            except Exception as ex:
                print(ex)
                self.mc.stop()

        if marks != {}:
            embed = discord.Embed(title="Moyenne", description=f'```{self.mc.sort_data(marks)}```', colour=0xff0000)
            await ctx.author.dm_channel.send(embed=embed)
        else:
            await ctx.author.dm_channel.send("Une erreur s'est produite ! Réessayez plus tard.")

        print(f"{ctx.author} (moy) - Done")

    @moy.command(name='suppr')
    async def moy_del(self, ctx: Context):
        self.db.users.delete_one({'id': ctx.author.id})
        await ctx.send("Votre compte a été supprimé de la base de données")
