import json
import os
import random
import string

import aiofiles
import aiohttp
import cv2
import discord
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


def process_img():
    images_tmp = os.listdir('ImagesTMP')
    images_db = os.listdir('Images')
    nb_new = 0
    for img in images_tmp:

        img_test = cv2.imread('ImagesTMP/' + img)
        print('Image test : ' + img)
        old = False
        for imgDB in images_db:
            if imgDB.split('.')[1] != 'gif':
                img_comp = cv2.imread('Images/' + imgDB)
                if img_comp.shape == img_test.shape:
                    diff = cv2.subtract(img_comp, img_test)
                    b, g, r = cv2.split(diff)
                    if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                        print("OLD")
                        old = True
                        break
        if not old:
            os.rename('ImagesTMP/' + img, 'Images/' + img)
            nb_new += 1
        else:
            os.remove('ImagesTMP/' + img)
    return nb_new


def random_name():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(15))


class DBManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.maj_DB()
        self.DB = bot.DB
        self.admin = bot.admin

    # Créé une DB à partir du dossier d'images + json de lien
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

        jsonfile = open('data/DB.json', 'w')
        jsonfile.write(json.dumps(data, indent=4, sort_keys=True))
        # self.bot.DB = json.load(jsonfile)
        jsonfile.close()

        jsontmp = open('data/DB.json')
        self.bot.DB = json.load(jsontmp)
        jsontmp.close()

        print("DB générée")

    # Sur upload d'une image, on la DL dans ImagesTMP
    @commands.Cog.listener()
    async def on_message(self, _message):
        if _message.author == self.bot.user or _message.channel.name != ("gastrotest"):
            return

        if len(_message.attachments) > 0:
            url = _message.attachments[0].url

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        assert resp.headers
                        type_image = url.split('.')[-1]
                        image_name = random_name() + '.' + type_image
                        f = await aiofiles.open('ImagesTMP/' + image_name, mode='wb')
                        await f.write(await resp.read())

    # Recharge le fichier d'admin
    @commands.command(name='reloadAdmin', hidden='True')
    async def reload_admin(self, ctx):
        if str(ctx.author.id) in self.admin.get_admins():
            await self.admin.reload_admin(ctx, self.bot)

    # Recharge DB
    @commands.command(name='reloadDB', hidden='True')
    async def reload_db(self, ctx):
        if str(ctx.author.id) not in self.admin.get_admins():
            return

        self.maj_DB()
        gastro = self.bot.get_cog('EnferGastro')
        if gastro is not None:
            gastro.reload_infos()
        embed = discord.Embed(title='Base rechargée', colour=0x9634D8)
        await ctx.send(embed=embed)

    @commands.command(name='ProcessNew', hidden='True')
    @commands.is_owner()
    async def process_new(self, ctx):
        msg = 'Le chargement de nouvelles images prend du temps. Les commandes seront indisponible jusqu\'à la fin ' \
              'du chargement.'
        await ctx.send(embed=discord.Embed(title='Merci de patienter', description=msg))
        nb = process_img()
        msg = f'{nb} nouvelle(s) image(s).\nRechargement de la base'
        embed = discord.Embed(title='Nouvelles Images', description=msg, colour=0x9634D8)
        await ctx.send(embed=embed)
        await self.reload_db(ctx)


def setup(bot):
    bot.add_cog(DBManager(bot))
