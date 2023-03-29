from discord.ext.commands.core import check
from database.classes import guild
from discord.ext.commands import (Cog, command, has_permissions,
                                  bot_has_permissions, has_role,
                                  group, cooldown, BucketType, Context)
from discord.ext import tasks
import discord, datetime, random, math, typing, asyncio, logging, babel, pytz
from discord.ext.commands.errors import BadArgument
from database.dao.classesDAO import GuildConfigDAO as dbGC
from bot import Bot, class_errors as err
from bot.converters import Number, convertTime, Member, TextChannel, DoubleParam, User
from utils import checks

class Moderation(Cog, name='<:moderation:894693485091880990> Moderación', description='Categoría de comandos de moderación.'):
    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        
    @Cog.listener()
    async def on_guild_channel_create(self, channel):
        guildConfig = dbGC.selectGuildConfig(channel.guild.id)      
        if guildConfig.idRoleMute:
            role = discord.utils.get(channel.guild.roles, id=guildConfig.idRoleMute)
            await channel.set_permissions(role, send_messages=False) 
        return 
    
    @command(
        description="Elimina una gran cantidad de mensajes, excepto los mensajes fijados. La cantidad mínima es 1 mensaje.",
        usage="clear <cantidad>",
        brief=["clear 100"],
        aliases=["eliminar", "purge"],
        extras=['manage_messages', 'rol_admin', 'send_messages'])
    @bot_has_permissions(manage_messages=True, embed_links=True)
    @checks.rolAdmin(manage_messages=True)
    async def clear(self, ctx, limit: Number = None):
        embed = self.bot.tools.embed(self, ctx)
        if limit < 0:
            raise err.BadArgument_('<cantidad>')
        else:
            await ctx.message.delete()
            await ctx.channel.purge(limit=limit, check=lambda message: not message.pinned)
            embed.description = f"{self.bot.config.emojiCheck} Se eliminaron {limit} mensajes correctamente."
            embed.color = self.bot.config.checkColor
        await ctx.send(embed=embed, delete_after=3)
        
    @command(
        description="Expulsa a un usuario del servidor.",
        usage="kick <usuario> [razón]",
        brief=["kick @user Nickname inapropiado"],
        aliases=["expulsar"],
        extras=['kick_members', 'rol_admin', 'send_messages'])
    @bot_has_permissions(kick_members=True)
    @checks.rolAdmin(kick_members=True)
    async def kick(self, ctx, member: Member, *, reason="‎No se estableció una razón‏‏‎"):
        embed = self.bot.tools.embed(self, ctx) 
        guild = dbGC.selectGuildConfig(ctx.guild.id)
        embed.color = self.bot.config.errorColor         
        await self.bot.tools.moderation(self, member, ctx, guild, 'Expulsión', reason, embed)
    
    @command(
        description="Veta a un usuario del servidor.",
        usage="ban <usuario> [razón]",
        brief=["ban @user Nickname inapropiado"],
        aliases=['vetar'],
        extras=['ban_members', 'rol_admin', 'send_messages'])
    @bot_has_permissions(ban_members=True)
    @checks.rolAdmin(ban_members=True)
    async def ban(self, ctx, member: User, *, reason="‎No se estableció una razón‏‏‎"):
        embed = self.bot.tools.embed(self, ctx) 
        guild = dbGC.selectGuildConfig(ctx.guild.id)
        embed.color = self.bot.config.errorColor         
        await self.bot.tools.moderation(self, member, ctx, guild, 'Baneado', reason, embed)
    
    @command(
        description="Veta a un usuario del servidor.",
        usage="unban <usuario> [razón]",
        brief=["unban @user Sanción cumplida"],
        aliases=['desban'],
        extras=['ban_members', 'rol_admin', 'send_messages'])
    @bot_has_permissions(ban_members=True)
    @checks.rolAdmin(ban_members=True)
    async def unban(self, ctx, member: User, *, reason="‎No se estableció una razón‏‏‎"):
        embed = self.bot.tools.embed(self, ctx) 
        try:
            f = [("Usuario:", f"{member.mention}", False),
                ("Acción:", "Desbaneado", False ),
                ("Razón:", f"{reason}", False),
                ("Realizado por:", f"{ctx.author.mention}",False)]
            for name, value, inline in f:
                embed.add_field(name=name, value=value, inline=inline)
            await ctx.guild.unban(member, reason=f"{ctx.author} - {reason}")
        except:
            embed.clear_fields()
            embed.description = f"El usuario {member.mention} no se encuentra baneado."
            embed.color = self.bot.config.errorColor
        await ctx.reply(embed=embed, mention_author=False)
        
        
    @command(
        description="Silencia a un usuario del servidor. Si no se establece la duración, el usuario queda silenciado indefinidamente. El formato de la duración es: `1s`, `1m`, `1h`, `1d`, `1y`",
        usage="mute <usuario> [duración] [razón]",
        brief=["mute @user", "mute @user 1d", "mute @user 1d Link inapropiado"],
        aliases=["silenciar"],
        extras=['kick_members', 'rol_admin', 'send_messages', 'manage_roles'])
    @bot_has_permissions(kick_members=True, manage_roles=True)
    @checks.rolAdmin(kick_members=True, manage_roles=True)
    async def mute(self,ctx, member: Member, duration=None, *, reason="No se estableció una razón."):
        
        embed = self.bot.tools.embed(self, ctx)
        guild = dbGC.selectGuildConfig(ctx.guild.id)
        rolAdmin = ctx.guild.get_role(guild.idRoleAdmin if guild.idRoleAdmin else 0)
        role = ctx.guild.get_role(guild.idRoleMute if guild.idRoleMute else 0)
        if not role:
            embed.description = f"Primero debes establecer un rol de muteo. Ejecuta `{ctx.prefix}setRoles` para establecerlo." 

        elif role in member.roles:
            embed.description = f"Este usuario ya se encuentra muteado."
    
        else:
            converter = convertTime(duration if duration else '')
            
            if not converter:
                time = duration
                f = [("Usuario:", f"{member.mention}", False),
                    ("Sanción:", "Muteado", False ),
                    ("Razón:", (f"{reason}" if not duration else f"{duration} "+(" " if reason == "No se estableció una razón." else f"{reason}")), False),
                    ("Realizado por:", f"{ctx.author.mention}",False)]
            else:
                reason = reason
                time = str(converter[0])
                d = converter[2]
                tiempo = converter[1]
                f = [("Usuario:", f"{member.mention}", False),
                ("Sanción:", "Muteado", False ),
                ("Razón:", f"{reason}", False),
                ("Duración: ", f"{d} {tiempo}",False),
                ("Realizado por:", f"{ctx.author.mention}",False)]


            embed.color = self.bot.config.errorColor
            if ctx.guild.me == member:
                    
                embed.description = f"{self.bot.config.emojiError} No puedes silenciarme."
            
            elif ctx.author == member:
                
                embed.description = f"{self.bot.config.emojiError} No puedes silenciarte a ti mismo."
            elif role.position > ctx.guild.me.top_role.position:
                embed.description = f"{self.bot.config.emojiError} Mi rol debe estar por encima del rol {role.mention}."

            elif member.guild_permissions.administrator or (rolAdmin in member.roles):
                embed.description = f"{self.bot.config.emojiError} No puedo silenciar a alguien con permisos de administrador."
                
            else:
                embed.color = self.bot.config.defaultColor
                for name, value, inline in f:
                    embed.add_field(name=name, value=value, inline=inline)
                await member.add_roles(role, reason=reason)
                try:
                    await member.send(embed=embed)
                except:
                    pass
                await ctx.reply(embed=embed, mention_author=False)
                if time.isnumeric():
                    await asyncio.sleep(int(time))
                    await member.remove_roles(role, reason=f"{ctx.author} - Tiempo de mute terminado.")
                return
        await ctx.reply(embed=embed, mention_author=False)
    @command(
        description="Quitar el silencio a un usuario silenciado.",
        usage="unmute <usuario> [razón]",
        brief=["unmute @user", "unmute @user Sanción cumplida"],
        aliases=["desilenciar"],
        extras=['kick_members', 'rol_admin', 'send_messages', 'manage_roles'])
    @bot_has_permissions(kick_members=True, manage_roles=True)
    @checks.rolAdmin(kick_members=True, manage_roles=True)
    async def unmute(self, ctx, member: Member, *, reason="‎No se estableció una razón‏‏‎"):
        embed = self.bot.tools.embed(self, ctx)
        
        guild = dbGC.selectGuildConfig(ctx.guild.id)
        role_member = discord.utils.get(member.roles, id=guild.idRoleMute if guild.idRoleMute else 0)
        role = ctx.guild.get_role(guild.idRoleMute if guild.idRoleMute else 0)
        embed.color = self.bot.config.errorColor
        if not role:
            embed.description = f"{self.bot.config.emojiError} Primero debes establecer un rol de muteo. Ejecuta `{ctx.prefix}setRoles` para establecerlo."
        elif not role_member:
            embed.description = f"El usuario {member.mention} no ha sido silenciado anteriormente."
        else: 
            embed.color = self.bot.config.defaultColor
            f = [("Usuario:", f"{member.mention}", False),
                    ("Acción:", "Desmuteado", False ),
                    ("Razón:", f"{reason}", False),
                    ("Realizado por:", f"{ctx.author.mention}",False)]
                
            for name, value, inline in f:
                embed.add_field(name=name, value=value, inline=inline)
            await member.remove_roles(role, reason=f"{ctx.author} - {reason}")
        
        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot: Bot):
    await bot.add_cog(Moderation(bot))