import asyncio
import random
from datetime import datetime, timedelta
import discord
from discord.ext import commands

"""
----------------------------------------------------------
EnferGastro 

Classe qui gère les marathons

>>> Objets
 - auth 		(bool)		: booléen pour authorisation du marathon
 - NbImg		(int)		: Nombre d'image du marathon
 - data 		(liste)		: Contenu du json DB
 - duree 		(float/int)	: durée en heure du marathon
 - delai 		(float)		: délai entre les images du marathon (dépend de la durée)
 - admin 		(Admin)		: Instance d'Admin --> Voir Admin.py pour plus d'info
 - Machine 		(Marathon)	: instance de marathon
 - LastSend 	(int)		: Numéro de la dernière image envoyé (dans data)
>>> Méthodes
 - get_delai 	(float)		: retourne le délai
 - get_nbimg 	(int)		: retourne le nombre d'image de DB
 - get_auth		(bool)		: retourne l'état de l'authorisation du marathon
 - set_LastSend (int)		: défini la clé de la dernière image envoyée
 - is_admin 	(bool)		: vérifie si l'auteur d'un message est admin du bot
 - GestroMessage			: Envoi d'une image formaté selon les données dans data
 - LastImgInfo 				: Envoi les information de la dernière image posté
 - Duree 					: Information sur la durée du marathon
 - getInfo 					: envoi information sur la classe
 - oskour 					: poste une image aléatoire
 - switch 					: change le statut d'authorisation du marathon
 - Marathon 				: Lance le marathon de l'enfer gastronomique

> Si marathon en cours

 - tempsMR 					: temps restant
 - tempsME 					: temps écoulé
 - avanceM 					: nombre images restante
"""


class EnferGastro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auth = False

        self.data = bot.DB

        self.NbImg = len(self.data)
        self.duree = 10
        self.delai = 10 * 3600 / len(self.data)
        self.admin = bot.admin
        self.Machine = None
        self.LastSend = None

    # Getters qui servent après
    def get_delai(self):
        return round(self.delai, 2)

    def get_nbimg(self):
        return self.NbImg

    def get_auth(self):
        return self.auth

    # change l'id de LastSend
    def set_lastsend(self, ident):
        self.LastSend = ident

    # Custom check pour certaines fonctions
    # Vérifie que l'auteur du message dans ctx est dans la liste des admins d'Admin
    async def is_admin(self, ctx):
        return str(ctx.author.id) in self.admin.get_admins()

    # Envoi message formatter selon type (image / lien) de DB.json
    # Item (liste) : Objet du json
    # id   (int)   : clé de l'objet json
    async def gastro_message(self, ctx, _item, _ident):
        self.set_lastsend(_ident)
        if _item['type'] == 'image':
            image_to_send = discord.File('Images\\' + _item['url'])
            await ctx.send(file=image_to_send)
        elif _item['type'] == 'lien':
            await ctx.send(_item['url'])
        else:
            print('GastroMessage : Erreur de type pour la donnee ', _item)

    # Info de la dernière image postée
    @commands.command(
        name='LFI',
        brief='Information sur la dernière image posté (par moi)'
    )
    async def last_img_info(self, ctx):
        if self.LastSend is None:
            await ctx.send('Aucune Image en mémoire ...')
        else:
            item = self.data[self.LastSend]
            await ctx.send('``` \nType : ' + item['type']
                           + '\nNom/URL : < ' + item['url'] + ' > \n ```')

    # Renvoi durée du marathon actuelle, ou défini une nouvelle durée si time est mis à 0
    # time (int) :
    # 	- None -> Renvoie les infos liées à la durée
    #   - Sinon défini la durée en seconde
    #   - Si le délai trop court ou si time n'est pas un entier, on envoie un message d'alerte (5 seconde en dur)
    @commands.command(
        name='duree',
        brief='Renvoi ou défini duree marathon'
    )
    async def duree(self, ctx, _time=None):
        if _time is None:
            if self.duree > 1:
                await ctx.send('Durée prévu du marathon : ' + str(self.duree) + ' Heures')
            else:
                await ctx.send('Durée prévu du marathon : ' + str(self.duree) + ' Heure')
            await ctx.send('Délai entre chaque monstruosité : ' + str(self.get_delai()) + ' secondes')
            return
        else:
            try:
                temps = float(_time)
            except ValueError:
                await ctx.send('Il faut rentrer un nombre pour que ça marche ...')
                return
        if (temps* 3600 / self.NbImg) < 5:
            await ctx.send(
                'Bien essayé mais non. Je limite le délai entre chaque image à 5sec\nLa durée minimum que '
                'j\'authorise est de {0} heures (calculé en onction du nombre d\'images)\nLe temps à mettre en '
                'paramètre est en heures.'.format(
                    str(round((self.NbImg * 5) / 3600, 2))))
            return

        elif await self.is_admin(ctx):
            self.duree = temps
            self.delai = temps * 3600 / self.NbImg
            if self.duree > 1:
                await ctx.send('Durée du marathon initialisé à ' + str(self.duree) + ' Heures')
            else:
                await ctx.send('Durée du marathon initialisé à ' + str(self.duree) + ' Heure')
            await ctx.send('Délai entre chaque monstruosité : ' + str(self.get_delai()) + ' secondes')
            return

    # Infos générales :
    # Authorisation du lancement du marathon, nombre d'images et délai
    @commands.command(
        name='get_info',
        brief='Infos marathon'
    )
    async def get_info(self, ctx):
        await ctx.send('``` \nAuth : ' + str(self.get_auth())
                       + '\nNb Img : ' + str(self.get_nbimg())
                       + '\nDélai : ' + str(self.get_delai()) + '\n ```')

    # envoi objet random depuis DB
    @commands.command(name='oskour',
                      description='Vision d\'horreur aléatoire',
                      brief='( ͡° ͜ʖ ͡°)')
    async def oskour(self, ctx):
        rng = random.randint(0, self.NbImg)
        item = self.data[rng]
        await self.gastro_message(ctx, item, rng)

    # switch l'authorisation du marathon via Booléen
    @commands.command(name='switch', description='Authorisation marathon', brief='Authorisation Marathon')
    async def switch(self, ctx):
        if await self.is_admin(ctx):
            self.auth = not self.auth
            await ctx.send('Statut Authorisation : ' + str(self.auth))

    # Marathon des enfers
    @commands.command(
        name='marathon',
        description='Lancement du Marathon',
        brief='Enclenchez le mécanisme de la terreur !')
    async def marathon(self, ctx):
        # check admin
        if not self.auth or not await self.is_admin(ctx):
            await ctx.send("Non.")
        else:
            rng = random.sample(range(0, self.NbImg), self.NbImg)  # liste randomisée des id des images
            lkp = 0  # lookup dans la liste
            self.Machine = Marathon(self.NbImg, self.duree)  # Init Machine
            while self.auth and lkp <= self.NbImg - 1:  # auth pour permettre arrêt prématuré
                item = self.data[rng[lkp]]
                await self.gastro_message(ctx, item, rng[lkp])
                lkp += 1
                self.Machine.avance()
                await asyncio.sleep(self.delai)  # attend x secondes

            await ctx.send('Petit Jesus a été vaincu ! Il reviendra peut-être dans un futur proche ...')
            del self.Machine

        # Commandes pour stats du marathon

    @commands.command(
        name='tempsMR',
        brief='Temps restant du marathon (si en cours)'
    )
    async def tempsMR(self, ctx):
        if self.Machine is not None:
            await ctx.send(self.Machine.temps_restant())

    @commands.command(
        name='tempsME',
        brief='Temps écoulé du marathon (si en cours)'
    )
    async def tempsME(self, ctx):
        if self.Machine is not None:
            await ctx.send(self.Machine.temps_ecoule())

    @commands.command(
        name='imgM',
        brief='Nombre d\'image restante du marathon (si en cours)'
    )
    async def avanceM(self, ctx):
        if self.Machine is not None:
            await ctx.send(self.Machine.img_restant())

    @commands.command(
        name='DEBUG',
        brief='fonction modulable pour test',
        hidden='True'
    )
    async def debug(self, ctx):
        if not await self.is_admin(ctx):
            await ctx.send("Bien essayé petit margoulin...")
        else:
            await ctx.send('Ceci est un test')


def setup(bot):
    bot.add_cog(EnferGastro(bot))


""" 
Marathon

Instance de marathon

>>> Objet
 - Img :   Nombre d'image restante
 - duree : durée du marathon
 - start : datetime de départ

>>> Methodes
 - avance : Diminue le nombre d'image restante de 1
 - TempsRestant : retourne le temps restant
 - ImgRestant : Renvoi le nombre d'image restante
 - TempsEcoule: Retourne le temps restant du marathon

 """


class Marathon:

    def __init__(self, liste, _duree):
        self.Img = liste
        self.duree = _duree
        self.start = datetime.now()

    # fait avancer le marathon d'une image
    def avance(self):
        self.Img -= 1

    def temps_restant(self):
        return timedelta(hours=self.duree) - (datetime.now() - self.start)

    def img_restant(self):
        return self.Img

    def temps_ecoule(self):
        now = datetime.now()
        return now - self.start
