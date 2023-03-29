from utils.tools import rolPerms
from discord.ui import Select, Button, Item, View, button
from discord.ext.commands import (Cog, command, Context)
import discord, typing, datetime, asyncio, config, logging, requests, re, filetype, io, string
from database.classes.guild import GuildImages
from database.dao.classesDAO import GuildImagesDAO as dbGI, GuildConfigDAO as dbGC

# Command setConfigJoinLeave
class ViewGeneric(View):
    def __init__(self, **kwargs):
        self.buttons = kwargs.get('buttons')
        self.bot = kwargs.get('bot')
        self.ctx = kwargs.get('ctx')
        self.generic = kwargs.get('generic')
        if self.generic == 'join':
            self.textEmbed = 'bienvenida'     
        elif self.generic == 'leave':
            self.textEmbed = 'despedida'
        elif self.generic == 'boost':
            self.textEmbed = 'booster'
        else: self.textEmbed = 'roles'
        self.custom_id_ = kwargs.get('custom_id_')
        self.dataGuild = kwargs.get('dataGuild')
        self.view2 = kwargs.get('view2')
        self.option = kwargs.get('option') if kwargs.get('option') else []
        super().__init__()
    
class ButtonEditGeneric(Button):
    def __init__(self, emoji, custom_id, **kwargs):
        super().__init__(emoji=emoji, custom_id=custom_id)
        
    
    async def callback(self, interaction: discord.Interaction):
        view2 = self.view.view2
        custom_id_, custom_id = int(self.custom_id), self.view.custom_id_ 
        verify = False       
        ctx = view2.ctx
        dataGuild = view2.dataGuild
        embed = interaction.message.embeds[0] if interaction.message.embeds else view2.bot.tools.embed(view2, ctx)
        
        if interaction.user == ctx.author:
            if custom_id_ == 0:
                verify = True
                embed.description = view2.bot.tools.embeds(dataGuild, view2.generic, ctx, [custom_id, 1])
                view = None
                        
            elif custom_id_ == 1:
                value = None
                if custom_id == 3: value = "FFFFFF"
                view = self.view
                exec('dataGuild.{0}{1} = value'.format(view2.option[custom_id], view2.generic.capitalize()))
                embed.description = view2.bot.tools.embeds(dataGuild, view2.generic, ctx, [custom_id, 0])    
                await dbGI.update([dataGuild.getAll()], ctx)
                view.remove_item(view.children[1])
                 
            elif custom_id_ == 2:
                embed.description = view2.bot.tools.embeds(dataGuild, view2.generic, ctx, [-1])
                view = view2

            await interaction.response.edit_message(content=None, embed=embed, view=view, attachments=[]) 
            
            if verify:
                embed.colour = config.errorColor
                flag = False
                try: 
                    message = await view2.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60.0)
                except asyncio.exceptions.TimeoutError:
                    embed.description = f'{config.emojiError} La configuración de la sección `{view2.textEmbed}` ha sido cancelada. Ejecute `{ctx.prefix}{ctx.command.name}` para configurar nuevamente.'
                    view = None
                                            
                else:
                    cancel = ['cancel', 'cancelar']
                    content = message.content
                    embed.description = view2.bot.tools.embeds(dataGuild, view2.generic, ctx, [custom_id, 0])
                    view = None
                    if not (content in cancel): 
                        if custom_id == 0:
                            if re.search(config.URL_REGEX, content):
                                file = requests.get(content).content
                            elif len(message.attachments) >= 1:
                                file = await message.attachments[0].read()
                            else:
                                file = None
                            
                            msgError = f'{config.emojiError} No se encontraron imágenes. Intenta pegar el enlace de la imagen o subirla. Ejecute `{ctx.prefix}{ctx.command.name}` para configurar nuevamente.'
        
                            if filetype.is_image(io.BytesIO(file)):
                                flag = True
                                value = file
                            
                        elif custom_id == 1:
                            msgError = f'{config.emojiError} ¡El mensaje no debe ser mayor a 1000 caracteres!'
                            if not len(message.content) > 1000:
                                value = content
                                flag = True
                        
                        elif custom_id == 2:
                            channel = discord.utils.get(ctx.guild.channels, name=content)
                            channels = message.channel_mentions
                            msgError = f'{config.emojiError} El canal indicado parece no ser válido. Ejecute `{ctx.prefix}{ctx.command.name}` para configurar nuevamente.'
                            if channel:
                                value = channel.id
                                flag = True
                            elif channels and isinstance(channels[0], discord.TextChannel):
                                value = channels[0].id
                                flag = True
                        elif custom_id == 3:        
                            msgError = f'{config.emojiError} El número hexadecimal del color es inválido. Ejecute `{ctx.prefix}{ctx.command.name}` para configurar nuevamente.'
                            if all(letter in string.hexdigits for letter in message.content):
                                flag = True
                                value = content
                        embed.description = msgError
                        if flag:
                            view = self.view             
                            exec('dataGuild.{0}{1} = value'.format(view2.option[custom_id], view2.generic.capitalize()))
                            embed.description = view2.bot.tools.embeds(dataGuild, view2.generic, ctx, [custom_id, 0])
                            embed.colour = config.defaultColor
                            await dbGI.update([dataGuild.getAll()], ctx)
                    else: 
                        view = self.view 
                        embed.colour = config.defaultColor     
                    if dataGuild.imageJoin:
                        self.view.clear_items()
                        for item in view2.buttons[6:]:
                            self.view.add_item(item)    
                try: await message.delete()
                except: pass                          
                await interaction.edit_original_response(embed=embed, view=view)


class ButtonGeneric(Button):
    def __init__(self, emoji, custom_id, **kwargs):
        super().__init__(emoji=emoji, custom_id=custom_id)
        
    async def callback(self, interaction: discord.Interaction):
        dataGuild = self.view.dataGuild
        ctx = self.view.ctx
        if self.custom_id.isnumeric():
            custom_id = int(self.custom_id)
            try:
                image, text, channel, color, textEmbed = dataGuild.getAll(self.view.generic)
                channel = ctx.guild.get_channel(channel if channel else 0)
            except: pass
        else:
            custom_id = self.custom_id
        embed = interaction.message.embeds[0]
        view = ViewGeneric(view2=self.view, custom_id_=custom_id)
        content, verify = None, False
        if interaction.user == ctx.author:
            if custom_id in self.view.option:
                for button in self.view.buttons[4:]:
                    view.add_item(button)
                embed.description = self.view.bot.tools.embeds(dataGuild, custom_id, ctx, [4, 0])
                exec('if not dataGuild.{0}: view.remove_item(view.children[1])'.format(custom_id))
                if not dataGuild.idRoleMute and custom_id == 'idRoleMute': view.add_item(ButtonEditRole('🆕', '3'))
            elif custom_id < 4:
                embed.description = self.view.bot.tools.embeds(dataGuild, self.view.generic, ctx, [custom_id, 0])
                for button in self.view.buttons[6:]:
                    view.add_item(button)
                exec('if not dataGuild.{0}{1}: view.remove_item(view.children[1])'.format(self.view.option[custom_id], self.view.generic.capitalize()))
                
            elif custom_id == 4:
                view.add_item(self.view.buttons[8])
                file = await self.view.bot.tools.image(ctx, dataGuild, self.view.generic)
                verify = True
                embed = None
                content = text.format_map(self.view.bot.tools.FormatMap(
                member=ctx.author,
                member_name=ctx.author.name,
                member_mention=ctx.author.mention,
                server=ctx.guild.name)) if text else '᲼᲼᲼᲼᲼᲼'
            else:
                view = None
                embed.description = f'{config.emojiError} La configuración de la sección `{self.view.textEmbed}` ha sido cancelada. Ejecute `{ctx.prefix}{ctx.command.name}` para configurar nuevamente.'
                embed.colour = self.view.bot.config.errorColor
                
            
            await interaction.response.edit_message(content=content, embed=embed, view=view)
            if verify:
                await interaction.edit_original_response(content=content, embed=embed, view=view, attachments=[file])  
                
    
class ButtonEditRole(Button):
    def __init__(self, emoji, custom_id):
        super().__init__(emoji=emoji, custom_id=custom_id)
        
    async def callback(self, interaction: discord.Interaction):
        view2 = self.view.view2
        custom_id_, custom_id = int(self.custom_id), self.view.custom_id_ 
        verify = False       
        ctx = view2.ctx
        dataGuild = view2.dataGuild
        embed = interaction.message.embeds[0]
        if interaction.user == ctx.author:
            if custom_id_ == 0:
                verify = True
                embed.description = view2.bot.tools.embeds(dataGuild, custom_id, ctx, [4, 1])
                view = None
            elif custom_id_ == 1:
                view = self.view
                exec('dataGuild.{0} = None'.format(custom_id))
                embed.description = view2.bot.tools.embeds(dataGuild, custom_id, ctx, [4, 0])    
                view.remove_item(view.children[1])
                if custom_id == 'idRoleMute': view.add_item(ButtonEditRole('🆕', '3'))
                await dbGC.update([dataGuild.getAll()], ctx)
                 
            elif custom_id_ == 2:
                embed.description = view2.bot.tools.embeds(dataGuild, custom_id, ctx, [-2])
                view = view2
            elif custom_id_ == 3:
                view = self.view
                self.view.children = view2.buttons[4:]
                role = await ctx.guild.create_role(name='Silenciado')
                dataGuild.idRoleMute = role.id
                embed.description = view2.bot.tools.embeds(dataGuild, custom_id, ctx, [4, 0])
                view2.bot.tools.rolPerms(ctx, role, view2.bot)
                view2.bot.roles[ctx.guild.id][custom_id] = role.id
                await dbGC.update([dataGuild.getAll()], ctx)
            
            await interaction.response.edit_message(embed=embed, view=view) 
            
            if verify:
                embed.colour = config.errorColor
                flag = False
                try: 
                    message = await view2.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60.0)
                except asyncio.exceptions.TimeoutError:
                    embed.description = f'{config.emojiError} La configuración de la sección `{view2.textEmbed}` ha sido cancelada. Ejecute `{ctx.prefix}{ctx.command.name}` para configurar nuevamente.'
                    view = None
                else:
                    cancel = ['cancel', 'cancelar']
                    content = message.content
                    embed.description = view2.bot.tools.embeds(dataGuild, custom_id, ctx, [4, 0])
                    view = None
                    if not (content in cancel):
                        role = discord.utils.get(ctx.guild.roles, name=content)
                        roles = message.role_mentions
                        msgError = f'{config.emojiError} El rol indicado parece no ser válido. Ejecute `{ctx.prefix}{ctx.command.name}` para configurar nuevamente.'
                        if role:
                            value, flag = role, True
                        elif roles:
                            value, flag = roles[0], True
                        embed.description = msgError
                        if flag:
                            view = self.view
                            exec('dataGuild.{0} = value.id'.format(custom_id))      
                            embed.description = view2.bot.tools.embeds(dataGuild, custom_id, ctx, [4, 0]); embed.colour = config.defaultColor                      
                            view2.bot.roles[ctx.guild.id][custom_id] = value.id
                            if custom_id == 'idRoleMute':
                                view2.bot.tools.rolPerms(ctx, value, view2.bot)
                            await dbGC.update([dataGuild.getAll()], ctx)
                    else: 
                        embed.colour = config.defaultColor
                        view = self.view
                    exec('if dataGuild.{0}: self.view.children = view2.buttons[4:]'.format(custom_id))
                try: await message.delete()
                except: pass                          
                await interaction.edit_original_response(embed=embed, view=view)