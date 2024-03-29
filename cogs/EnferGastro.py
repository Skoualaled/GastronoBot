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
 - auth 		(bool)		: booléen pour autorisation du marathon
 - NbImg		(int)		: Nombre d'image du marathon
 - data 		(liste)		: Contenu du json DB
 - duree 		(float/int)	: durée en heure du marathon
 - delai 		(float)		: délai entre les images du marathon (dépend de la durée)
 - admin 		(Admin)		: instance d'Admin --> cf Admin.py
 - Machine 		(Marathon)	: instance de marathon
 - LastSend 	(int)		: Numéro de la dernière image envoyé (dans data)
>>> Méthodes
 - reload_infos             : met à jour les objets
 - is_admin 	(bool)		: vérifie si l'auteur d'un message est admin du bot
 - gastro_message			: envoi d'une image formaté selon les données dans data
 - last_img_info 			: envoi les information de la dernière image posté
 - duree 					: information sur la durée du marathon
 - info_marathon			: envoi information sur la classe
 - oskour 					: poste une image aléatoire
 - switch 					: change le statut d'autorisation du marathon
 - marathon 				: lance le marathon de l'enfer gastronomique
 - debug                    : modification manuelle pour tester des trucs (check owner)

"""


class EnferGastro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autorisation = False

        self.data = bot.DB

        self.NbImg = len(self.data)
        self.duree = 10
        self.delai = 10 * 3600 / len(self.data)
        self.admin = bot.admin
        self.Machine = None
        self.LastSend = None

    def reload_infos(self):
        self.data = self.bot.DB
        self.NbImg = len(self.data)
        self.delai = 10 * 3600 / len(self.data)

    # Custom check pour certaines fonctions
    # Vérifie que l'auteur du message dans ctx est dans la liste des admins d'Admin
    async def is_admin(self, ctx):
        return str(ctx.author.id) in self.admin.get_admins()

    # Envoi message formatter selon type (image / lien) de DB.json
    # Item (liste) : Objet du json
    # id   (int)   : clé de l'objet json
    async def gastro_message(self, ctx, _item, _ident):
        self.LastSend = _ident
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
            msg = 'Type : {0} \nNom/URL : <{1}> \n'.format(item['type'], item['url'])
            embed = discord.Embed(title='Info dernière image', description=msg, color=0xFFFFFF)
            await ctx.send(embed=embed)

    # Renvoi durée du marathon actuelle, ou défini une nouvelle durée si time est mis à 0
    # time (int) :
    # 	- None -> Renvoie les infos liées à la durée
    #   - Sinon défini la durée en seconde
    #   - Si le délai trop court ou si time n'est pas un entier, on envoie un message d'alerte (5 seconde en dur)
    @commands.command(
        name='duree',
        brief='Renvoi ou défini duree marathon (en heures)'
    )
    async def duree(self, ctx, _time=None):
        if _time is None:
            if self.duree > 1:
                await ctx.send(f'Durée prévu du marathon : {self.duree} heures')
            else:
                await ctx.send(f'Durée prévu du marathon : {self.duree} heure')
            await ctx.send(f'Délai entre chaque monstruosité : {round(self.delai, 2)} secondes')
            return
        else:
            try:
                temps = float(_time)
            except ValueError:
                await ctx.send('Il faut rentrer un nombre pour que ça marche ...')
                return
        if (temps * 3600 / self.NbImg) < 5:
            await ctx.send(
                'Bien essayé mais non. Je limite le délai entre chaque image à 5sec (faut pas déconner)\nLa durée '
                'minimum que j\'autorise est de {0} heures (calculé en fonction du nombre d\'images)\nLe temps à '
                'mettre en paramètre est en heures.'.format(
                    str(round((self.NbImg * 5) / 3600, 2))))
            return

        elif await self.is_admin(ctx):
            self.duree = temps
            self.delai = temps * 3600 / self.NbImg
            if self.duree > 1:
                await ctx.send(f'Durée du marathon initialisé à {self.duree} heures')
            else:
                await ctx.send(f'Durée du marathon initialisé à {self.duree} heure')
            await ctx.send(f'Délai entre chaque monstruosité : {round(self.delai, 2)} secondes')
            return

    # envoi objet random depuis DB
    @commands.command(name='oskour',
                      description='Vision d\'horreur aléatoire',
                      brief='( ͡° ͜ʖ ͡°)')
    async def oskour(self, ctx):
        rng = random.randint(0, self.NbImg)
        item = self.data[rng]
        await self.gastro_message(ctx, item, rng)

    # switch l'autorisation du marathon via Booléen
    @commands.command(name='switch', description='Autorisation marathon', brief='Autorisation Marathon')
    async def switch(self, ctx):
        if await self.is_admin(ctx):
            self.autorisation = not self.autorisation
            await ctx.send('Statut Autorisation : ' + str(self.autorisation))
        else:
            await ctx.send('Non.')

    # Marathon des enfers
    @commands.command(
        name='marathon',
        description='Lancement du Marathon',
        brief='Enclenchez le mécanisme de la terreur !')
    async def marathon(self, ctx):
        # check admin
        if not self.autorisation or not await self.is_admin(ctx):
            await ctx.send("Non.")
        else:
            rng = random.sample(range(0, self.NbImg), self.NbImg)  # liste randomisée des id des images
            lkp = 0  # lookup dans la liste
            self.Machine = Marathon(self.NbImg, self.duree)  # Init Machine
            while self.autorisation and lkp <= self.NbImg - 1:  # auth pour permettre arrêt prématuré
                item = self.data[rng[lkp]]
                await self.gastro_message(ctx, item, rng[lkp])
                lkp += 1
                self.Machine.avance()
                await asyncio.sleep(self.delai)  # attend x secondes

            await ctx.send('Petit Jesus a été vaincu ! Il reviendra peut-être dans un futur proche ...')
            del self.Machine

        # Commandes pour stats du marathon

    # Infos générales :
    @commands.command(name='infos', brief='Infos sur le marathon')
    async def info_marathon(self, ctx):
        if self.Machine is None:
            msg = f'Marathon autorisé ? {self.autorisation} \nNombre de vision : {self.NbImg} \n' \
                  f'Temps de répis : {round(self.delai,2)} sec'
            embed = discord.Embed(title='Infos', description=msg, color=0x992d22)
            await ctx.send(embed=embed)
        else:
            tr = self.Machine.temps_restant()
            te = self.Machine.temps_ecoule()
            ir = self.Machine.img_restant()

            msg = f'Temps passé : {tr}\nTemps restant : {te}\nVision d\'horreur posté : {ir}\nTemps de répis : ' \
                  f'{self.delai} \nEnsemble des vision : {self.NbImg} '
            embed = discord.Embed(title='Infos Marathon', description=msg, color=0x1f8b4c)
            await ctx.send(embed=embed)

    @commands.command(
        name='DEBUG',
        brief='fonction modulable pour test',
        hidden='True'
    )
    @commands.is_owner()
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

    def __init__(self, _liste, _duree):
        self.Img = _liste
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
