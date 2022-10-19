import json
import os
import random
import string

import aiofiles
import aiohttp
from discord.ext import commands

""" 
DBManager : Gestion de la base de donnée

>>> Objets :

    DB (liste de listes) : liste imbriqué avec les infos des images (le json) lié à l'instance du bot
    admin : instance d'Admin

>>> Méthodes :

- cog_check : vérification auto de l'admin
- reloadAdmin : recharge de la liste des admins
- reloadDB : Recharge la liste des images
- MajDB : Recharge la liste des images
- on_message : automatique sur message -> si image on la DL dans ImageTMP
- randomName : Génère un nom aléatoire

 """


class DBManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.maj_DB()
        self.DB = bot.DB
        self.admin = bot.admin

    async def cog_check(self, ctx):
        return str(ctx.author.id) in self.admin.get_admins()

    # Recharge le fichier d'admin
    @commands.command()
    async def reload_admin(self, ctx):

        await self.admin.reload_admin(ctx, self.bot)

    # Recharge DB
    @commands.command()
    async def reload_DB(self, ctx):
        self.maj_DB()
        await ctx.send("DB rechargé")

    # Créé une DB à partir du dossier d'images + json de lien
    # @commands.command(name='MajDB')
    def maj_DB(self):
        jsonfile = open('data/Liens.json')
        data = json.load(jsonfile)
        jsonfile.close()

        for item in data:
            item['type'] = 'lien'

        images = os.listdir('Images')
        for Img in images:
            item = {'url': Img, 'type': 'image'}
            data.append(item)

        jsonfile = open('data\\DB.json', 'w')
        jsonfile.write(json.dumps(data, indent=4, sort_keys=True))
        # self.bot.DB = json.load(jsonfile)
        jsonfile.close()

        jsontmp = open('data\\DB.json')
        self.bot.DB = json.load(jsontmp)
        jsontmp.close()

        print("DB générée")

    # Sur upload d'une image, on la DL dans ImagesTMP
    @commands.Cog.listener()
    async def on_message(self, _message):
        if _message.author == self.bot.user:
            return

        if len(_message.attachments) > 0:
            url = _message.attachments[0].url

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        assert resp.headers
                        type_image = url.split('.')[-1]
                        image_name = self.random_name() + '.' + type_image
                        f = await aiofiles.open('ImagesTMP\\' + image_name, mode='wb')
                        await f.write(await resp.read())

    # Nom aléatoire 
    @staticmethod
    def random_name():
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(15))


def setup(bot):
    bot.add_cog(DBManager(bot))
