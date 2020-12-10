import asyncio
import json
import os
import random
import string
from datetime import datetime, timedelta

import aiofiles
import aiohttp
import discord
from discord.ext import commands
"""
----------------------------------------------------------
EnferGastro 
>>> Objets
 - auth 		(bool)		: booléen pour authorisation du marathon
 - NbImg		(int)		: Nombre d'image du marathon
 - data 		(liste)		: Contenu du json DB
 - duree 		(float/int)	: duree en heure du marathon
 - delai 		(float)		: delai entre les images du marathon (dépend de la durée)
 - admin 		(Admin)		: Instance d'Admin --> Voir Admin.py pour plus d'info
 - Machine 		(Marathon)	: instance de marathon
 - LastSend 	(int)		: Numréro de la dernière image envoyé (dans data)
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
		self.bot=bot
		self.auth=False 
		
		self.data = bot.DB
		
		self.NbImg = len(self.data)
		self.duree =10
		self.delai = 10*3600 / len(self.data)
		self.admin = bot.admin
		self.Machine = None
		self.LastSend = None



	# Getter qui servent après
	def get_delai(self):
		return round(self.delai,2)

	def get_nbimg(self):
		return self.NbImg

	def get_auth(self):
		return self.auth

	# change l'id de LastSend
	def set_LastSend(self, id):
		self.LastSend = id


	# Custom check pour certaines fonction
	# Vérifie que l'auteur du message dans ctx est dans la liste des admins de Admin
	async def is_admin(self, ctx):
		return str(ctx.author.id) in self.admin.get_admins()

	
	# Envoi message formatter selon type (image / lien) de DB.json
	# Item (liste) : Objet du json
	# id   (int)   : clé de l'bjet json
	async def GastroMessage(self, ctx, Item, id):
		self.set_LastSend(id)
		if Item['type'] == 'image':
			ImageToSend= discord.File('Images\\'+Item['url'])
			await ctx.send(file=ImageToSend)
		elif Item['type']=='lien':
			await ctx.send(Item['url'])
		else:
			print('GastroMessage : Erreur de type pour la donnee ', Item)

    # Info de la dernière image posté
	@commands.command(
		name='LFI',
		brief='Information sur la dernière image posté (par moi)'
	)
	async def LastImgInfo(self, ctx):
		if self.LastSend == None:
			await ctx.send('Aucune Image en mémroire ...')
		else:
			Item = self.data[self.LastSend]
			await ctx.send('``` \nType : '+ Item['type']
			+ '\nURL : < ' + Item['url']+ '> \n ```')

	# Renvoi durée actuelle ou la défini, ou défini une nouvelle durée si time est mis à 0
	# time (int) :
	# 	- None -> Renvoie les info lié à la durée
	#   - Sinon défini la durée en seconde
	#   - Si le délai trop court ou si time n'est pas un entier  on renvoi un message d'alerte (5 seconde en dur)
	@commands.command(
		name='Duree',
		brief='Renvoi ou défini duree marathon'
	)
	async def Duree(self, ctx, time=None):
		if time==None:
			if self.duree > 1 :
				await ctx.send('Duree prévu du marathon : ' + str(self.duree) + ' Heure')
			else: 
				await ctx.send('Duree prévu du marathon : ' + str(self.duree) + ' Heures')
			await ctx.send('Délai entre chaque monstruosité : ' + str(self.get_delai()) + ' secondes')
		elif (time * 3600 / self.NbImg) < 5 or type(time) is str:
			await ctx.send('Bien essayé mais non. Je limite le délai entre chaque image à 5sec\nLa durée minimum que j\'authorise est de ' + str(round((self.NbImg * 5) / 3600),2)+ ' heures (environ)')
		elif await self.is_admin(ctx):
			self.duree = time
			self.delai = time * 3600 / self.NbImg
			if self.duree > 1 :
				await ctx.send('Duree du marathon initialisé à ' + str(self.duree) + ' Heures')
			else:
				await ctx.send('Duree du marathon initialisé à ' + str(self.duree) + ' Heure')
			await ctx.send('Délai entre chaque monstruosité : ' + str(self.get_delai()) + ' secondes')

	# Infos générales :
	# Authorisation, nombre d'image et délai
	@commands.command(
		name='getInfo',
		brief='Infos marathon'
	)
	async def getInfo(self, ctx):
		await ctx.send('``` \nAuth : ' + str(self.get_auth()) 
		+'\nNb Img : '+ str(self.get_nbimg())
		+ '\nDelai : ' + str(self.get_delai())+ '\n ```')
	

	#envoi objet random depuis DB 
	@commands.command(name='oskour',
                description='Vision d\'horreur aléatoire',
                brief='( ͡° ͜ʖ ͡°)')
	async def oskour(self, ctx):
		# channel = self.bot.get_channel(585160113132666904)
		rng = random.randint(0, self.NbImg)
		Item = self.data[rng]
		await self.GastroMessage(ctx, Item, rng)
		
		
	# switch l'authorisation du marathon
	@commands.command(name='switch',descritpion='Authorisation marathon', brief='Athorisation Marathon')
	async def switch(self, ctx):
		if await self.is_admin(ctx):
			self.auth = not self.auth 
			await ctx.send('Statut Authorisation : ' + str(self.auth))
	
	# Marathon des enfer
	@commands.command(
	name='Marathon', 
	description='Lancement Marathon', 
	brief='Enclenchez le mécanisme de la terreur !')
	async def Marathon(self, ctx):
		# chack admin
		if not self.auth or not await self.is_admin(ctx):
			await ctx.send("Non.")
		else:
			rng=random.sample(range(0, self.NbImg), self.NbImg) # liste randomisé des id des images
			lkp=0 # lookup dans la liste
			self.Machine = Marathon(self.NbImg, self.duree) # Init Machine
			while self.auth and lkp <= self.NbImg -1: # auth pour permettre arrêt prématuré
				item = self.data[rng[lkp]]
				await self.GastroMessage(ctx, item, rng[lkp])
				lkp+=1
				self.Machine.avance()
				await asyncio.sleep(self.delai) # attend x secondes
		
			await ctx.send('Petit Jesus a été vaincu ! Il reviendra peut-être dans un futur proche ...')
			del self.Machine 

	@commands.command(
		name ='tempsMR',
		brief='Temps restant du marathon (si en cours)'
	)
	async def tempsMR(self, ctx):
		if self.Machine != None:
			await ctx.send(self.Machine.TempsRestant())

	@commands.command(
		name='tempsME',
		brief='Temps écoulé du marathon (si en cours)'
	)
	async def tempsME(self, ctx):
		if self.Machine != None:
			await ctx.send(self.Machine.TempsEcoule())

	@commands.command(
		name='imgM',
		brief='Nombre d\'image restante du marathon (si en cours)'
	)
	async def avanceM(self, ctx):
		if self.Machine != None:
			await ctx.send(self.Machine.ImgRestant())
	


def setup(bot):
	bot.add_cog(EnferGastro(bot))


""" 
Marathon
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

	def __init__(self, liste, duree):
		self.Img = liste
		self.duree = duree
		self.start = datetime.now()

	# fait avancé le marathon d'une image
	def avance(self):
		self.Img-=1
	
	def TempsRestant(self):
		return timedelta(hours=self.duree) - (datetime.now() - self.start)

	def ImgRestant(self):
		return self.Img

	def TempsEcoule(self):
		now = datetime.now()
		return now - self.start
	

