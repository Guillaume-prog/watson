from discord.ext import commands
from discord.ext.commands import Bot, Context

from .scrappers.timetable import TimetableClient
from datetime import datetime

import json


class TimetableCog(commands.Cog):

    def __init__(self, bot: Bot, db, timetable_client: TimetableClient):
        self.bot = bot
        self.db = db
        self.tc = timetable_client

        self.tt = {}

    @commands.group(name="timetable", aliases=['tt'])
    async def get_table(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            self.tt = self.tc.get_timetable("https://edt.univ-nantes.fr/iut_nantes/g39705.html")
            with open("x.json", "w") as f:
                json.dump(self.tt, f, indent=4)
            await ctx.send("Got timetable")

    @commands.command(name="classes")
    async def get_next_class(self, ctx: Context):
        day = self.tt[datetime.today().weekday()]
        # print(day)
        text = "Cours de la journée:\n"
        for el in day:
            room = el.get('salle')
            if room == "":
                link = self.db.teachers.find_one({'name': el.get('prof')})
                room = link.get('link') if link is not None else "Aucune salle trouvée"
            text += f'> **{el.get("type")}** {el.get("nom")} ({el.get("horaires")}) : {el.get("prof")}\n> **Salle** : {room}\n\n'
        await ctx.send(text)
