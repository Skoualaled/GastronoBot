import discord

""" 
Admin : Gestion des admin lié à une instance de Bot (parce que pourquoi pas)

>>> Objets

 - admin (liste) : liste des ID des admins

>>> Méthodes

 - loadAdmin : Recharge la liste des admin à partir du fichier AdminID
 - getAdmin (liste) : Retourne la liste des admins
 - reloadAdmin : Recharge la liste des admin et envoie un message avec leurs noms

 """


class Admin:

    def __init__(self):
        self.admin = self.load_admin()

    def load_admin(self):
        admin = open('data\AdminID', 'r')
        loaded = []
        for ids in admin:
            loaded.append(ids.rstrip())
        admin.close()
        return loaded

    def get_admins(self):
        return self.admin

    async def reload_admin(self, ctx, _bot):
        adminfile = open('data\AdminID', 'r')
        names = ''
        msg = discord.Embed(colour=0xFFA500)
        self.admin = []
        for ids in adminfile:
            self.admin.append(ids.rstrip())
            user = _bot.get_user(int(ids))
            names += user.name + '\n'
        msg.add_field(name='Admin', value=names, inline=True)

        await ctx.send(embed=msg)
        adminfile.close()
