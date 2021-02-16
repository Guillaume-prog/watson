import time
from discord.ext.commands import Context, Bot


def get_date():
    return time.strftime('%d-%m-%Y', time.localtime())


async def get_var(bot: Bot, ctx: Context, text):
    await ctx.send(text)
    res = await bot.wait_for('message',
                             check=lambda msg: msg.author == ctx.author and msg.channel == ctx.author.dm_channel)
    return res.content


async def get_dm_var(bot: Bot, ctx: Context, text):
    await ctx.author.dm_channel.send(text)
    res = await bot.wait_for('message',
                             check=lambda msg: msg.author == ctx.author and msg.channel == ctx.author.dm_channel)
    return res.content
