from discord.ext import commands
from discord.ext.commands import Bot, Context

from random import *
from urllib3 import PoolManager
import util


class TeacherCog(commands.Cog):

    def __init__(self, bot: Bot, db):
        self.bot = bot
        self.db = db

    @commands.group(name="prof", aliases=['pr'])
    async def prof(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            print("No subcommand found")

    @prof.command()
    async def list(self, ctx: Context, *args):
        search = ' '.join(args)
        text = ""
        for el in sorted(self.db.teachers.find(), key=lambda item: item.get('name')):
            if el.get('name').split(' ')[0].lower().startswith(search):
                text += f'{el.get("name")} ({el.get("id")}), '
        text = text[:-2] if text != "" else "Aucun prof trouvé"
        await ctx.send(text)

    @prof.command()
    async def get(self, ctx: Context, prof_id: int):
        prof = self.db.teachers.find_one({'id': prof_id})
        text = f'{prof.get("name")}: {prof.get("link")}' if prof is not None else "Aucun prof de ce nom trouvé"
        await ctx.send(text)

    @prof.command()
    async def add_bulk(self, ctx: Context):
        files = ctx.message.attachments
        print(files[0].filename.split('.'))
        if len(files) == 0 or files[0].filename.split('.')[-1] != 'csv':
            await ctx.send("Aucun fichier csv joint")
            return

        http = PoolManager()
        r = http.request('GET', files[0].url)

        for line in r.data.decode('utf-8').split('\n')[4:-1]:
            info = line.split(",")
            name = f'{info[0]} {info[1]}'
            prof_id = randint(1, 99)
            if self.db.teachers.count_documents({'name': name}) == 0 and \
                    self.db.teachers.count_documents({'id': prof_id}) == 0:
                self.db.teachers.insert_one({'id': prof_id, 'name': name, 'link': info[2]})

        await ctx.send('Base de données des profs mise à jour')

    @prof.command()
    async def add(self, ctx: Context, name, surname, link):
        self.db.teachers.insert_one({'name': name + " " + surname, 'link': link})
        await ctx.send("Prof ajouté à la base de données")

    @prof.command()
    async def update(self, ctx: Context, name, surname, link):
        m_name = name + " " + surname
        if self.db.teachers.find_one({'name': m_name}) is None:
            await ctx.send("Aucun prof trouvé")
        else:
            self.db.teachers.update_one({'name': m_name}, {'$set': {'link': link}})
            await ctx.send("Lien du prof mis à jour")

    @prof.command()
    async def delete(self, ctx: Context, name, surname):
        m_name = name + " " + surname
        if self.db.teachers.find_one({'name': m_name}) is None:
            await ctx.send("Aucun prof trouvé")
        else:
            self.db.teachers.delete_one({'name': m_name})
            await ctx.send("Prof supprimé de la base de données")

    @prof.command()
    async def purge(self, ctx: Context):
        m_continue = await util.get_var(self.bot, ctx,
                                        "Etes-vous sur de vouloir supprimer tous les profs de la base de données ? O/N")
        if m_continue.lower() == 'o':
            self.db.teachers.drop()
            await ctx.send("Base de données effacée")
        else:
            await ctx.send("Operation annulée")
