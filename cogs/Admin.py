import discord

""" 
Admin : Gestion des admin

>>> Objets

 - admin (liste) : liste des ID des admins

>>> Methodes

 - loadAdmin : Recharge la liste des admin à partir du fichier AdminID
 - getAdmin (liste) : Retourne la liste des admins
 - reloadAdmin : Recharge la liste des admin et envoie un message avec leurs noms

 """

class Admin:

    def __init__(self):
        self.admin = self.loadAdmin()

    def loadAdmin(self):
        admin = open('data\AdminID', 'r')
        loaded =[]
        for ids in admin:
            loaded.append(ids.rstrip())
        admin.close()
        return loaded

    def get_admins(self):
        return self.admin
    
    async def reloadAdmin(self, ctx, bot):
        adminfile = open('data\AdminID', 'r')
        names = ''
        msg= discord.Embed(colour = 0xFFA500)
        self.admin = []
        for ids in adminfile:
            self.admin.append(ids.rstrip())
            user = bot.get_user(int(ids))
            names+=user.name +'\n'
        msg.add_field(name = 'Admin', value=names, inline = True)

        await ctx.send(embed=msg) 
        adminfile.close()