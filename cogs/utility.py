from discord.ext.commands import (Cog, command, has_permissions,
                                  bot_has_permissions, has_role,
                                  group, cooldown, BucketType, Context)
import discord, datetime, random, math, typing, asyncio, logging, babel
from database.dao.classesDAO import GuildConfigDAO as dbGC
from bot import Bot, class_errors as err
from bot.converters import Emoji, Number, convertTime, Member, TextChannel, DoubleParam, User
from utils import checks
from components.components_utility import ViewGeneric
from babel.dates import format_datetime

class Utility(Cog, name='🌀 Utilidades', description='Categoría de comandos de utilidades'):
    def __init__(self, bot):
        self.bot: Bot = bot
        
    @command(
        description="Muestra el avatar suyo o de un usuario. También puedes colocar el ID del usuario del que quieres ver el avatar.",
        usage="avatar [usuario]",
        brief=["avatar @user"],
        aliases=["foto"],
        extras=['send_messages'])
    @bot_has_permissions(embed_links=True)
    async def avatar(self, ctx, member: User = None):
        embed = self.bot.tools.embed(self, ctx)
        if not member:
            member = ctx.author
        view = ViewGeneric('Avatar URL', url=member.display_avatar.url) 
        embed.set_image(url=member.display_avatar.url).set_author(name=f'{member}', icon_url=member.display_avatar.url)
        await ctx.reply(embed=embed, mention_author=False, view=view)
    
    
    @command(
        description="Obtén la latencia de envíos de mensajes de Daniel's Bot",
        usage="ping",
        brief=["ping"],
        aliases=["latencia"],
        extras=['send_messages'])
    @bot_has_permissions(embed_links=True)
    async def ping(self, ctx):
        start = datetime.datetime.utcnow()
        embed = self.bot.tools.embed(self, ctx)
        message = await ctx.reply('Pong', mention_author=False)
        end = datetime.datetime.utcnow()
        await message.edit(f'🏓 Pong!\n📨 Envio de mensajes: `{(end-start).total_seconds()*1000:.0f} ms`.\nAPI: `{round(self.bot.latency*1000)} ms`.')    
        
    
    @command(
        description="Muestra el banner del servidor o de otro servidor.",
        usage="banner",
        brief=["banner"],
        aliases=["cartel"],
        extras=['send_messages'])
    @bot_has_permissions(embed_links=True)
    async def banner(self, ctx):
        embed = self.bot.tools.embed(self, ctx)
        
        banner = ctx.guild.banner 
        view = None
        if banner:
            embed.set_author(name=f'{ctx.guild}', url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)
            embed.set_image(url=banner.url)
            view = ViewGeneric('Banner URL', url=banner.url)
        else:
            embed.colour = self.bot.config.errorColor
            embed.description = f'{self.bot.config.emojiError} El servidor no tiene un banner.'
        
        await ctx.reply(embed=embed, mention_author=False, view=view)
    
    @command(
        description="Obtén la imagen más grande del emoji proporcionado.",
        usage="emoji <emoji>",
        brief=["emoji :hola:", 'emoji hola'],
        aliases=["jumbo", 'emote'],
        extras=['send_messages'])
    @bot_has_permissions(embed_links=True)
    async def emoji(self, ctx, emoji: Emoji):
        embed = self.bot.tools.embed(self, ctx)
        timestamp = emoji.created_at.timestamp() 
        fields = [
            ['**Nombre:**', f'`{emoji.name}`', False],
            ['**ID:**', f'`{emoji.id}`', False],
            ['**Identifier:**', f'`{emoji.name}:{emoji.id}`', False],
            ['**Creado:**', f'<t:{int(timestamp)}>', False]
            ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_author(name=emoji.name, icon_url=emoji.url)
        embed.set_image(url=emoji.url)
        view = view = ViewGeneric('Emoji URL', url=emoji.url)
        await ctx.reply(embed=embed, mention_author=False, view=view)
        
     
    @command(
        description="Muestra información detallada suya o de algún usuario.",
        usage="userinfo [usuario]",
        brief=["userinfo @! TheDanielrity", 'userinfo'],
        aliases=['user'],
        extras=['send_messages'])
    @bot_has_permissions(embed_links=True)
    async def userinfo(self, ctx, member: Member = None):
        if not member:
          member = ctx.author
        roles = [role.mention for role in member.roles]
        joined = int(member.joined_at.timestamp())
        created = int(member.created_at.timestamp())
        
        embed = discord.Embed(colour=self.bot.config.defaultColor, description=f"{member.mention}")
        embed.set_author(name=f'{member}', icon_url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Apodo", value=("Ninguno" if member.nick is None else member.nick))
        embed.add_field(name="Avatar", value=f"[Link]({member.display_avatar.url})", inline=False)
        embed.add_field(
            name="Fecha de ingreso", value=f'<t:{joined}> (<t:{joined}:R>)' if member.joined_at else "Desconocido", inline=False
        )
        embed.add_field(name="Cuenta creada", value=f'<t:{created}> (<t:{created}:R>)', inline=False)
        
        embed.add_field(name="Roles", value=(f"{len(roles)} roles" if len(", ".join(roles)) > 1000 else ", ".join(roles[1:])) if len(roles) != 1 else "Ninguno")
        
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.reply(embed=embed, mention_author=False)
        
        
            
    
async def setup(bot):
   await bot.add_cog(Utility(bot))