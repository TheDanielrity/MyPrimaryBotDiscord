from discord.ui import Select, Button, Item, View, button
from discord.ext.commands import (Cog, command, Context)
import discord, typing, datetime, asyncio, config, logging
from bot import converters
from database.classes.guild import GuildInvites
from database.dao.classesDAO import GuildInvitesDAO as dbG
logging.getLogger(__name__)

# Command LeaderBoard
class ViewGeneric(View):
    @staticmethod
    async def getRank(ctx, records):
        for idMember, numInvites, regularInvites, leaveInvites, bonusInvites, fakeInvites in records:
            if ctx.author.id == int(idMember):
                yourRank = records.index(
                    [idMember, numInvites, regularInvites, leaveInvites, bonusInvites, fakeInvites])
                return yourRank

    def __init__(self, **kwargs):
        self.ctx = kwargs.get('ctx')
        self.page = kwargs.get('page')
        self.yourRank = kwargs.get('yourRank')
        self.embeds = kwargs.get('embeds')
        self.buttons = kwargs.get('buttons')
        self.bot = kwargs.get('bot')
        self.dataGuild: GuildInvites = kwargs.get('dataGuild')
        self.view2 = kwargs.get('view2')
        self.db = ['msgRegularInvite', 'msgSelfInvite', 'msgUnknownInvite', 'msgVanityInvite', 'idChannelInvite', 'timeFake']
        self.custom_id_ = kwargs.get('custom_id_')
        self.key = list(config.messagesInvites.keys())
        super().__init__()

class ButtonInvite(Button):
    def __init__(self,label, disabled, style):
        super().__init__(label=label, disabled=disabled, style=style)

    async def callback(self, interaction: discord.Interaction):
        items = self.view.children
        for item in items:
            if item is not self:
                item = item
                break

        if self.label == 'Siguiente Página':
            if self.view.page == len(self.view.embeds)-2: self.disabled = True
            else: item.disabled = False
            self.view.page += 1
            index = self.view.page + 1
            msg = self.view.embeds[self.view.page] \
                .set_footer(text=f"Página {index}/{len(self.view.embeds)}"+self.view.yourRank)

        elif self.label == 'Anterior Página':
            if self.view.page == 1: self.disabled = True
            else: item.disabled = False
            self.view.page -= 1
            index = self.view.page + 1
            msg = self.view.embeds[self.view.page] \
                .set_footer(text=f"Página {index}/{len(self.view.embeds)}"+self.view.yourRank)

        if interaction.user == self.view.ctx.author:
            await interaction.response.edit_message(embed=msg, view=self.view)


# Command setMessagesInvite
class ButtonEditMessages(Button):
    def __init__(self, emoji, custom_id, **kwargs):
        super().__init__(emoji=emoji, custom_id=custom_id)
        
    
    async def callback(self, interaction: discord.Interaction):
        view2 = self.view.view2
        custom_id_, custom_id = int(self.custom_id), self.view.custom_id_ 
        embed = interaction.message.embeds[0]
        verify = False       
        ctx = view2.ctx
        dataGuild = view2.dataGuild
        keyVariable = self.view.key[custom_id-1] 
        dbVariable = self.view.db[custom_id-1]
        i = 0
        if custom_id in (5, 6):
            i = custom_id - 4
        if interaction.user == ctx.author:
            if custom_id_ == 0:
                embed.description = eval(view2.embeds[i][1])
                view = None       
                verify = True

            elif custom_id_ == 1:
                setattr(dataGuild, dbVariable, config.messagesInvites.get(keyVariable))
                
                if not dataGuild.idChannelInvite and custom_id == 5:
                    self.view.remove_item(view2.buttons[1])  
                embed.description = eval(view2.embeds[i][0])
                view = self.view
                await dbG.update([dataGuild.getAll()], ctx)
                
            elif custom_id_ == 2:
                embed.description = view2.embeds[-1]
                view = view2

            await interaction.response.edit_message(embed=embed, view=view) 
            
            if verify:
                try: 
                    message = await view2.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60.0)
                except asyncio.exceptions.TimeoutError:
                    embed.description = f'{config.emojiError} La configuración de los mensajes de invitación ha sido cancelada. Ejecute `{ctx.prefix}{ctx.command.name}` para configurar nuevamente.'
                    embed.colour = config.errorColor
                    view = None
                                            
                else:
                    cancel = ['cancel', 'cancelar']
                    if message.content in cancel: 
                        embed.description = eval(view2.embeds[i][0])
                        view = self.view
                    elif custom_id < 5:
                        if not len(message.content) > 1000: 
                            setattr(dataGuild, dbVariable, message.content)
                            embed.description = eval(view2.embeds[i][0])
                            await dbG.update([dataGuild.getAll()], ctx)
                            view = self.view
                        else:
                            embed.description = f'{config.emojiError} El mensaje no debe ser mayor a 1000 caracteres. Ejecute `{ctx.prefix}{ctx.command.name}` para configurar nuevamente.'
                            embed.colour = config.errorColor
                            view = None  
                    elif custom_id == 5:
                        msgError = f'{config.emojiError} El canal indicado parece no ser válido. Ejecute `{ctx.prefix}{ctx.command.name}` para configurar nuevamente.'
                        channel = discord.utils.get(ctx.guild.channels, name=message.content)
                        channels = message.channel_mentions
                        if channel:
                            view = self.view
                            dataGuild.idChannelInvite = channel.id
                            await dbG.update([dataGuild.getAll()], ctx)
                            embed.description = eval(view2.embeds[i][0])
                        elif channels and isinstance(channels[0], discord.TextChannel):
                            view = self.view
                            dataGuild.idChannelInvite = channels[0].id
                            await dbG.update([dataGuild.getAll()], ctx)
                            embed.description = eval(view2.embeds[i][0])
                        
                        else:
                            view = None        
                            embed.description = msgError
                            embed.colour = config.errorColor
                        if dataGuild.idChannelInvite: self.view.children = view2.buttons[:]
                    else:
                        duration = converters.convertTime(message.content)
                        if duration:
                            dataGuild.timeFake = duration[0]
                            view = self.view
                            await dbG.update([dataGuild.getAll()], ctx)
                            embed.description = eval(view2.embeds[i][0])
                        else:
                            view = None        
                            embed.description = f'{config.emojiError} El formato ingresado no es válido. Ejecute `{ctx.prefix}{ctx.command.name}` para configurar nuevamente.'
                            embed.colour = config.errorColor
                try: await message.delete()
                except: pass                          
                await interaction.edit_original_message(embed=embed, view=view)

class ButtonMessagesInv(Button):
    def __init__(self, emoji, custom_id, **kwargs):
        super().__init__(emoji=emoji, custom_id=custom_id)
        
    async def callback(self, interaction: discord.Interaction):
        
        custom_id = int(self.custom_id)
        embed = interaction.message.embeds[0]
        ctx = self.view.ctx
        if interaction.user == self.view.ctx.author:
            if custom_id != 7:
                view = ViewGeneric(view2=self.view, 
                                custom_id_=custom_id)
                for button in self.view.buttons:
                    view.add_item(button)
                keyVariable = self.view.key[custom_id-1] 
                dbVariable = self.view.db[custom_id-1]
                dataGuild = self.view.dataGuild
                i = 0
                if custom_id in (5,6): 
                    i = custom_id - 4
                    if not dataGuild.idChannelInvite and custom_id == 5:
                        view.remove_item(self.view.buttons[1])
                                    
                embed.description = eval(self.view.embeds[i][0])
                     
            else:
                
                embed.description = f'{config.emojiError} La configuración de los mensajes de invitación ha sido cancelada. Ejecute `{self.view.ctx.prefix}{self.view.ctx.command.name}` para configurar nuevamente.'
                embed.colour = config.errorColor
                view = None
            
            await interaction.response.edit_message(embed=embed, view=view)
        
