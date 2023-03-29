from discord import permissions
from discord.ext.commands import check, Context, has_permissions
from bot import class_errors as err, Bot
def isOwnerGuild():
    def predicate(ctx: Context):
        if ctx.guild.owner_id == ctx.author.id:
            return True
        else:
            raise err.NotOwnerGuild('Error')
    return check(predicate)

def rolAdmin(**perms):
    def predicate(ctx: Context):
        if not ctx.guild:
            raise err.NoPrivateMessage()
        permissions = ctx.author.guild_permissions
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]
        if ctx.author.get_role(Bot._roles.get(ctx.guild.id).get('idRoleAdmin')) or not missing:
            return True
        raise err.MissingPermissions(['manage_guild', 'rol_admin'])
    return check(predicate)        