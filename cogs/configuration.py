from database.classes.guild import GuildConfig, GuildInvites
from discord.ext.commands import Cog, command, has_guild_permissions, bot_has_permissions, group, cooldown, BucketType, Context
from discord.ext import tasks
import discord, datetime, random, math, typing, asyncio, logging, io, filetype, requests
from discord.ui.button import button
from database.dao.classesDAO import GuildImagesDAO as dbGI, GuildConfigDAO as dbGC, GuildInvitesDAO as dbGIn
from bot import Bot, class_errors as err, converters as convert
from utils import checks
from components.components_configuration import ButtonGeneric, ButtonEditGeneric, ViewGeneric, ButtonEditRole
from database import classes as c
logging.getLogger('discord')


class Configuration(Cog, name='<:config:881774040698744862> Configuración', description='Personaliza tu servidor.'):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.optionJLB = ['image', 'text', 'idChannel', 'color'] 
        self.emojis = ['🗂️', '📜', '✉️', '🖍️', '📝', '❌']
        self.emojis2 = ['✏️', '🗑️', '↩️']
    
    @command(description="Configuración de la sección de bienvenida.",
             usage="setConfigJoin",
             brief=["setConfigJoin"],
             aliases=["scj"],
             extras=['manage_guild', 'rol_admin', 'send_messages'])
    @checks.rolAdmin(manage_guild=True)
    @bot_has_permissions(embed_links=True)
    @cooldown(1, 5.0, BucketType.member)
    async def setConfigJoin(self, ctx: Context):
        embed = self.bot.tools.embed(self, ctx)
        dataGuild = dbGI.selectGuildImages(ctx.guild.id) 
        buttons = []
        custom_id = 0
        
        for emoji in self.emojis:
            buttons.append(ButtonGeneric(emoji, str(custom_id)))
            custom_id += 1
            
        custom_id = 0
        for emoji in self.emojis2:
            buttons.append(ButtonEditGeneric(emoji, str(custom_id)))
            custom_id += 1
            
        view = ViewGeneric(buttons=buttons, ctx=ctx, bot=self.bot, dataGuild=dataGuild, generic='join', option=self.optionJLB)
        for button in buttons[:6]:
            view.add_item(button)
        embed.description = self.bot.tools.embeds(dataGuild, 'join', ctx, [-1])
        await ctx.reply(embed=embed, view=view, mention_author=False)
        
    @command(description="Configuración de la sección de despedida.",
             usage="setConfigLeave",
             brief=["setConfigLeave"],
             aliases=["scl"],
             extras=['manage_guild', 'rol_admin', 'send_messages'])
    @checks.rolAdmin(manage_guild=True)
    @bot_has_permissions(embed_links=True)
    @cooldown(1, 5.0, BucketType.member)
    async def setConfigLeave(self, ctx: Context):
        embed = self.bot.tools.embed(self, ctx)
        dataGuild = dbGI.selectGuildImages(ctx.guild.id) 
        buttons = []
        custom_id = 0
        
        for emoji in self.emojis:
            buttons.append(ButtonGeneric(emoji, str(custom_id)))
            custom_id += 1
            
        custom_id = 0
        for emoji in self.emojis2:
            buttons.append(ButtonEditGeneric(emoji, str(custom_id)))
            custom_id += 1
            
        view = ViewGeneric(buttons=buttons, ctx=ctx, bot=self.bot, dataGuild=dataGuild, generic='leave', option=self.optionJLB)
        for button in buttons[:6]:
            view.add_item(button)
        embed.description = self.bot.tools.embeds(dataGuild, 'leave', ctx, [-1])
        await ctx.reply(embed=embed, view=view, mention_author=False)

    @command(description="Configuración de la sección de booster.",
             usage="setConfigBoost",
             brief=["setConfigBoost"],
             aliases=["scb"],
             extras=['manage_guild', 'rol_admin', 'send_messages'])
    @checks.rolAdmin(manage_guild=True)
    @bot_has_permissions(embed_links=True)
    @cooldown(1, 5.0, BucketType.member)
    async def setConfigBoost(self, ctx: Context):
        embed = self.bot.tools.embed(self, ctx)
        dataGuild = dbGI.selectGuildImages(ctx.guild.id) 
        buttons = []
        custom_id = 0
        
        for emoji in self.emojis:
            buttons.append(ButtonGeneric(emoji, str(custom_id)))
            custom_id += 1
            
        custom_id = 0
        for emoji in self.emojis2:
            buttons.append(ButtonEditGeneric(emoji, str(custom_id)))
            custom_id += 1
            
        view = ViewGeneric(buttons=buttons, ctx=ctx, bot=self.bot, dataGuild=dataGuild, generic='boost', option=self.optionJLB)
        for button in buttons[:6]:
            view.add_item(button)
        embed.description = self.bot.tools.embeds(dataGuild, 'boost', ctx, [-1])
        await ctx.reply(embed=embed, view=view, mention_author=False)
    
    
    @command(description="Establece el prefix del servidor.",
             usage="setConfigPrefix <prefix>",
             brief=["setConfigPrefix d!"],
             aliases=["scp", 'setprefix'],
             extras=['manage_guild', 'rol_admin', 'send_messages'])
    @bot_has_permissions(embed_links=True)
    @cooldown(1, 5.0, BucketType.member)
    @checks.rolAdmin(manage_guild=True)
    async def setConfigPrefix(self, ctx, prefix = None):
        embed = self.bot.tools.embed(self, ctx)
        guildConfig = dbGC.selectGuildConfig(ctx.guild.id)
        if prefix:
            if len(prefix) < 6:    
                self.bot._prefixes[ctx.guild.id] = prefix
                guildConfig.prefix = prefix
                await dbGC.update([guildConfig.getAll()], ctx)
                embed.description = f'{self.bot.config.emojiCheck} El prefix se ha establecido exitosamente.'
                embed.colour = self.bot.config.checkColor
            else:
                embed.description = f'{self.bot.config.emojiError} El prefix no debe ser mayor a 5 caracteres.'
                embed.colour = self.bot.config.errorColor
        else:
            raise err.BadArgument_('<prefix>')
        await ctx.reply(embed=embed, mention_author=False)
        
    @command(description="Muestra los tags que se pueden utilizar para la configuración de bienvenida, despedida y booster.",
             usage="tagsConfig",
             brief=["tagsConfig"],
             aliases=["tagsConf", 'tc'],
             extras=['send_messages'])
    @bot_has_permissions(embed_links=True)
    async def tagsConfig(self, ctx):
        embed = self.bot.tools.embed(self, ctx)
        embed.description = f'Estas son las variables que puede utilizar para la sección de configuración.\n\n'
        variables = self.bot.config.VARIABLES_CONFIG.keys()
        for variable in variables:
            embed.description += f'`{variable}`: {self.bot.config.VARIABLES_CONFIG.get(variable)}\n'
        embed.description += '\n\nSi deseas mencionar un canal, rol, etc. Simplemente escribes la mención al momento de realizar la configuración.'
        await ctx.reply(embed=embed, mention_author=False)
        
    
    @command(description="Resetea la configuración de una categoría en específico del servidor. Este comando solo esta permitido para el dueño del servidor.",
             usage="resetConfig <all | invites | config >",
             brief=["resetConfig invites"],
             aliases=["reset", 'rc'],
             extras=['owner', 'send_messages'])
    @bot_has_permissions(embed_links=True)
    @checks.isOwnerGuild()
    async def resetConfig(self, ctx: Context, param: convert.verifyParam):
        embed = self.bot.tools.embed(self, ctx)
        embed.description = self.bot.config.charging
        message = await ctx.reply(embed=embed, mention_author=False)
        embed.colour = self.bot.config.checkColor
        if param == 'all':
            dbGC.deleteGuild(ctx.guild.id)
            await dbGC.insertGuild(ctx.guild.id, ctx)
            embed.description = f'{self.bot.config.emojiCheck} Se restableció toda la configuración del servidor.'
        elif param == 'invites':
            guild = GuildInvites(ctx.guild.id)
            await dbGIn.update([guild.getAll()], ctx)
            embed.description = f'{self.bot.config.emojiCheck} Se restableció la configuración de la categoría invitaciones.'
        else:
            guild = GuildConfig(ctx.guild.id)
            await dbGC.update([guild.getAll()], ctx)
            embed.description = f'{self.bot.config.emojiCheck} Se restableció la configuración de la categoría configuración.'
        
        await message.edit(embed=embed)
        
    @command(description="Establece los roles que tendrán una determinada función en tu servidor.\n`Cuando se establece el rol Mute, el bot automáticamente deniega el permiso enviarMensajes para todos los canales y categorías.`",
             usage="setRoles",
             brief=["setRoles"],
             aliases=["sr"],
             extras=['owner', 'send_messages'])
    @bot_has_permissions(embed_links=True)
    @checks.isOwnerGuild()
    async def setRoles(self, ctx: Context):
        
        embed = self.bot.tools.embed(self, ctx)
        dataGuild = dbGC.selectGuildConfig(ctx.guild.id) 
        emojis = ['<a:muted:881910991305187380>', '<:admin:881910502861709385>', '<a:join:881952082612060190>', '❌']
        buttons = []
        option = ['idRoleMute', 'idRoleAdmin', 'idRoleJoin']
        
        for i in range(3):
            buttons.append(ButtonGeneric(emojis[i], option[i]))
        buttons.append(ButtonGeneric(emojis[-1], str(10)))
        custom_id = 0
        for emoji in self.emojis2:
            buttons.append(ButtonEditRole(emoji, str(custom_id)))
            custom_id += 1
    
            
        view = ViewGeneric(buttons=buttons, ctx=ctx, bot=self.bot, dataGuild=dataGuild, option=option)
        for button in buttons[:4]:
            view.add_item(button)
        embed.description = self.bot.tools.embeds(dataGuild, 'mute', ctx, [-2])
        await ctx.reply(embed=embed, view=view, mention_author=False)
        
async def setup(bot):
    await bot.add_cog(Configuration(bot))