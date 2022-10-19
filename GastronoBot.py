import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from cogs.Admin import Admin

load_dotenv()
TOKEN = os.getenv('BOTARIE-TOKEN')
GUILD = os.getenv('BOTARIE-GUILD')


class Bot(commands.Bot):
    """Wrapper for the discord.Client class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin = Admin()
        self.DB = None  # init dans DBManager


bot = Bot(command_prefix='!')


# ------------------------ on ready -------------------------

@bot.event
async def on_ready():
    print('Connexion :')
    print(bot.user.name)
    print(bot.user.id)
    print('---------')


# Chargements Cogs
bot.load_extension('cogs.DBManager')
bot.load_extension('cogs.EnferGastro')


# ---------------------------- OFF ------------------------------
@bot.command(name='off')
async def turnoff(ctx):
    if str(ctx.author.id) in bot.admin.get_admins():
        await ctx.send('Bonne nuit !')
        await bot.logout()
        print('BOT STOPPED')


@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    bot.reload_extension(f"cogs.{extension}")
    embed = discord.Embed(title='Reload', description=f'{extension} successfully reloaded', color=0xff00c8)
    await ctx.send(embed=embed)


bot.run(TOKEN)
