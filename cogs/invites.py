from discord.ext.commands import (Cog, command, has_permissions,
                                  bot_has_permissions, has_role,
                                  group, cooldown, BucketType, Context)
from discord.ext import tasks
import discord, datetime, random, math, typing, asyncio, logging, babel, pytz
from database.dao.classesDAO import MemberDAO as dbM, GuildInvitesDAO as dbG
from database.classes import Member as MemberInv
from bot import Bot, class_errors as err
from components.components_invites import ButtonInvite, ButtonMessagesInv, ViewGeneric, ButtonEditMessages
from bot.converters import Number, convertTime, Member, TextChannel, DoubleParam
from utils import checks
logging.getLogger('discord')

class Invites(Cog, name='<a:ta:819086560855064597> Invitaciones', description='Categoría de comandos de invitación.'):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.invites = {}

    @tasks.loop(seconds=0.5)
    async def getInvites(self):
        for guild in self.bot.guilds:
            guild = self.bot.get_guild(guild.id)
            try:
                self.invites[guild.id] = await guild.invites()
            except:
                pass
            
    @staticmethod
    def findInviteByCode(inviteList, code):
        for inv in inviteList:
            if inv.code == code:
                return inv

    @Cog.listener()
    async def on_ready(self):
        self.getInvites.start()

    @Cog.listener()
    async def on_member_join(self, member):
        if member.id == self.bot.botUser.id: return 
        verify = finish = verify2 = False
        inviter, inviter_name, inviter_mention, numInvites, regularInvites, leaveInvites, bonusInvites, fakeInvites = 'inviter', 'inviter_name', 'inviter_mention', 'inviter_invites', 'inviter_reg_invites', 'inviter_leave_invites', 'inviter_bonus_invites', 'inviter_fake_invites'
        guild = member.guild
        timeFake, messageRegular, messageSelf, messageUnknown, messageVanity, idChannelInvite = dbG.selectGuildInvites(guild.id).getAll()[:6]  
        channel = guild.get_channel(idChannelInvite) if idChannelInvite else None
        
        if member.bot:
            msg = f'{member.mention} es un bot invitado por alguien al servidor.'
            if channel:
                await channel.send(msg)
            return
        try:
            invitesBefore = self.invites[guild.id]
            invitesAfter = await guild.invites()
        except Exception as e:
            msg = f'{member.mention} se unió al servidor, pero no tengo suficientes permisos para rastrear quien lo invitó.'
            if channel:
                await channel.send(msg)
            return
        try:
            vanityInvite = await guild.vanity_invite()
        except:
            vanityInvite = None
            
        print(vanityInvite)
            
        dataMembers = dbM.selectDataMembers(guild.id)
        data = []
        memberInvited = self.bot.tools.searchMember(dataMembers, member)
        for invite in invitesBefore:
            print(invite)
            joinInvite = Invites.findInviteByCode(invitesAfter, invite.code)
            if not joinInvite:
                msg = messageUnknown
                finish = True
                break
            if invite.uses < joinInvite.uses:
                inviter = invite.inviter
                inviter_name, inviter_mention = inviter.name, inviter.mention
                
                memberInviter = self.bot.tools.searchMember(dataMembers, inviter)
                
                if not memberInviter:
                    print('a')
                    memberInviter = MemberInv(inviter.id, 0, 0, 0, 0, 0, None, 1, guild.id) 
                         
                
                if member == inviter:
                    msg = messageSelf
                    break
                elif (member.id == (memberInvited.idMember if memberInvited else None)):
                    
                    if inviter.id == memberInvited.idMemberInvite:
                        
                        print('b')
                        if memberInvited.joinLeave:
                            numInvites, regularInvites, leaveInvites, fakeInvites = 0, 0, 0, 0
                            print('c')
                        else:
                            print('d')
                            
                            numInvites, regularInvites, leaveInvites, fakeInvites = 1, 0, -1, 0
                            
                    
                    else:
                        print('e')
                        if memberInvited.idMemberInvite:
                            memberInvited.idMemberInvite = None 
                        numInvites, regularInvites, leaveInvites, fakeInvites = 0, 1, 0, 1
                
                elif (datetime.datetime.now(datetime.timezone.utc) - member.created_at).total_seconds() < timeFake:
                    numInvites, regularInvites, leaveInvites, fakeInvites = 0, 1, 0, 1
                    verify2 = True
                else:
                    print('f')
                    verify = True
                    numInvites, regularInvites, leaveInvites, fakeInvites = 1, 1, 0, 0                           
                        
                memberInviter.setterInv(numInvites, regularInvites, leaveInvites, fakeInvites)
                numInvites, regularInvites, leaveInvites, bonusInvites, fakeInvites = memberInviter.getAll()[:5]
                data = [memberInviter.getAll()]
                msg = messageRegular
                print(data)
            
            elif vanityInvite:
                print('aea')
                msg = messageVanity
                break

        if not memberInvited:
            memberInvited = MemberInv(member.id, 0, 0, 0, 0, 0, None if verify2 else inviter.id, 1, guild.id)
        memberInvited.joinLeave = 1
        data.append(memberInvited.getAll())
        
        
        format = self.bot.tools.FormatMap(member=member,
                           member_name=member.name,
                           member_mention=member.mention,
                           inviter=inviter,
                           inviter_name=inviter_name,
                           inviter_mention=inviter_mention,
                           inviter_invites=numInvites,
                           inviter_reg_invites=regularInvites,
                           inviter_leave_invites=leaveInvites,
                           inviter_fake_invites=fakeInvites,
                           inviter_bonus_invites=bonusInvites, )
        if not finish:
            eval = await dbM.update(data, channel)
            print(eval)
            if not eval:
                print('g')
                await dbM.insertMembers(data, channel)
            elif verify:
                print('h')
                await dbM.insertMembers([data[1]], channel)
                
        if channel:
            await channel.send(msg.format_map(format))
            
        return

    @Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.bot:
            return
        guild = member.guild
        dataMembers = dbM.selectDataMembers(guild.id)
        thisLeave = self.bot.tools.searchMember(dataMembers, member)
        
        if thisLeave:
            leave = self.bot.tools.searchMember(dataMembers, await self.bot.fetch_user(thisLeave.idMemberInvite)) if thisLeave.idMemberInvite else None
        else:
            leave = None
        
        leaveI = invites = joinLeave = 0

        if thisLeave and leave:
            
            print('j')
            if not thisLeave.joinLeave:
                print('k')
                pass
            else:
                print('l')
                leaveI = 1
                invites = -1            
            
            leave.setterInv(invites, 0, leaveI, 0)
            thisLeave.joinLeave = joinLeave
            data = [leave.getAll(),
                    thisLeave.getAll()]
            
            await dbM.update(data)
        else:
            if not thisLeave:
                memberClass = MemberInv(member.id, 0, 0, 0, 0, 0, None, joinLeave, guild.id)
                await dbM.insertMembers([memberClass.getAll()])
            else:
                thisLeave.joinLeave = joinLeave
                await dbM.update([thisLeave.getAll()])
        return
    
            


    @command(description="Configure los mensajes de invitación.",
             usage="setMessagesInvite",
             brief=["setMessagesInvite"],
             aliases=["configinvite", 
                      "sci"],
             extras=['manage_guild', 'rol_admin', 'send_messages'])
    @checks.rolAdmin(manage_guild=True)
    @bot_has_permissions(embed_links=True)
    @cooldown(1, 15.0, BucketType.member)
    async def setConfigInvite(self, ctx):
        embed = self.bot.tools.embed(self, ctx)
        emojis = ['👤', '⛔', '❓', '🌐', '✉️', '⏱️', '❌']
        emojis2 = ['✏', '🗑', '↩️']
        _custom_id = 0
        custom_id = 1
        buttons = []
        embeds = [
            ["f'El mensaje de `{keyVariable}` actual es:\\n```{getattr(dataGuild, dbVariable)}```\\n\\n:pencil2: Editar\\n:wastebasket: Restablecer a predeterminado\\n:leftwards_arrow_with_hook: Regresar'",
             
             "f'Estás editando el mensaje de `{keyVariable}`. El mensaje no debe ser mayor a 1000 caracteres. \\nEl mensaje configurado actual es:\\n' + (f'```{getattr(dataGuild, dbVariable)}```\\n\\nEl mensaje predeterminado es:\\n```{config.messagesInvites.get(keyVariable)}```' if (getattr(dataGuild, dbVariable) != config.messagesInvites.get(keyVariable)) else f'```{getattr(dataGuild, dbVariable)}```') + '\\n\\nEscriba su mensaje en este canal. Escriba `cancel` para regresar.'"],
            
            [
            'f"**Establecer el canal para los mensajes de invitación**\\n\\nEl canal establecido para los mensajes de invitación actual es: {ctx.guild.get_channel(dataGuild.idChannelInvite).mention if ctx.guild.get_channel(dataGuild.idChannelInvite) else None}.\\n\\n:pencil2: Establecer canal.\\n:wastebasket: Borrar canal.\\n:leftwards_arrow_with_hook: Regresar" if dataGuild.idChannelInvite else "**Establecer el canal para los mensajes de invitación**\\n\\nNo hay un canal establecido para los mensajes de invitación actual.\\n:pencil2: Establecer un canal\\n:leftwards_arrow_with_hook: Regresar"', 
            '"\\nMencione el canal para los mensajes de invitación.\\nEscriba `cancel` para regresar."'],
            [
              'f"Establecer el recuento mínimo de días desde la creación de la cuenta del miembro que se une. Si su cuenta se creó antes del recuento de días especificado, la invitación se contará como `Fake`.\\nEl tiempo establecido actual es `{dataGuild.timeFake//(60*60*24)}d`\\n\\n:pencil2: Establecer tiempo.\\n:wastebasket: Restablecer a predeterminado\\n:leftwards_arrow_with_hook: Regresar"',
              '"Escriba el tiempo mínimo. Introducir el tiempo en días.\\nEjemplo: `7d` \\nEscriba `cancel` para regresar."'  
            ],
            
            
                
            '**Configurar los mensajes de invitación del servidor**\n\nSelecciona una opción:\n:bust_in_silhouette: Invitación regular.\n:no_entry: Invitación a si mismo.\n:question: Invitación desconocida.\n:globe_with_meridians: Invitaciones personalizadas.\n:envelope: Canal de invitaciones\n:stopwatch: TimeFake.\n:x: Cancelar.',
                ]
        dataGuild = dbG.selectGuildInvites(ctx.guild.id)
        view = ViewGeneric(embeds=embeds, ctx=ctx, buttons=buttons, bot=self.bot, dataGuild=dataGuild)
        
        for emoji in emojis2:
            buttons.append(ButtonEditMessages(emoji=emoji, custom_id=str(_custom_id)))
            _custom_id += 1

        for emoji in emojis:
            view.add_item(ButtonMessagesInv(emoji=emoji, custom_id=str(custom_id)))
            custom_id += 1
        embed.description = embeds[-1]
        await ctx.reply(embed=embed, view=view, mention_author=False)



    @command(description="Conocer el número de invitaciones que un usuario tiene en el servidor.",
             usage="invites [usuario]",
             brief=["invites @! TheDanielrity"],
             aliases=["inv", "invite"],
             extras=['send_messages'])
    @bot_has_permissions(embed_links=True)
    @cooldown(1, 5.0, BucketType.member)
    async def invites(self, ctx: Context, member: Member = None):
        embed = self.bot.tools.embed(self, ctx)
        if not member: member = ctx.author
        
        memberData = self.bot.tools.searchMember(dbM.selectDataMembers(ctx.guild.id), member) 
        if memberData:
            numInvites, regularInvites, leaveInvites, bonusInvites, fakeInvites = memberData.getAll()[:5]
            embed.title = f"Invitaciones"
            
            embed.description = f"{member.mention}, has invitado a {numInvites} usuarios.\n\n:white_check_mark: **{regularInvites}** regular\n:x: **{leaveInvites}** leave\n:poop: **{fakeInvites}** fake\n:sparkles: **{bonusInvites}** bonus"
            
        else:
            embed.description = f"{member.mention}, has invitado a 0 usuarios.\n\n:white_check_mark: **0** regular\n:x: **0** leave\n:poop: **0** fake\n:sparkles: **0** bonus"
        await ctx.reply(embed=embed, mention_author=False)

    @command(description="Muestra el top de invitaciones del servidor.",
             usage="topInvites [página]",
             brief=["topInvites 2"],
             aliases=["leaderboard", "lb", "top"],
             extras=['send_messages'])
    @bot_has_permissions(embed_links=True)
    @cooldown(1, 5.0, BucketType.member)
    async def topInvites(self, ctx: Context, page: Number = None):
        embed = self.bot.tools.embed(self, ctx)
        embed.colour = self.bot.config.errorColor
        embeds = []
        
        dataMembers = dbM.selectDataMembers(ctx.guild.id)

        records = [[record.idMember]+record.getAll()[:5] for record in dataMembers if sum(record.getAll()[:5]) > 0]
        records = sorted(records, reverse=True, key=lambda records: records[1])
        if records:
            page = page-1 if page else 0
            if page<0: 
                raise err.BadArgument_('[página]')
            position = 1
            for i in range(0, len(records) + 10, 10):
                if i == 0:
                    continue
                description = ''
                for idMember, numInvites, regularInvites, leaveInvites, bonusInvites, fakeInvites in records[i-10:i]:
                    
                    description += f"`{position}. ` <@{idMember}> • **{numInvites}** invitaciones. (**{regularInvites}**  regular, **{leaveInvites}** left, **{fakeInvites}** fake, **{bonusInvites} bonus**)\n"
                    position += 1

                embeds.append(discord.Embed(title='Top de Invitaciones',
                                            description=description,
                                            timestamp=datetime.datetime.now(),
                                            color=self.bot.config.defaultColor)
                              .set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar.url))

            if page+1 > len(embeds):
                page = 0
                
            if not page:
                if len(embeds) == 1:
                    disabledNext = True
                else:
                    disabledNext = False
                disabledPrevious = True
            elif page+1 == len(embeds):
                disabledNext, disabledPrevious = True, False
            else:
                disabledNext = disabledPrevious = False

            yourRank = await ViewGeneric.getRank(ctx, records)
            yourRank = f"• Tu posición en el top es: {yourRank + 1}" if isinstance(yourRank, int) else ''
            index = page+1
            embed = embeds[page].set_footer(text=f"Página {index}/{len(embeds)}"+yourRank)
            view = ViewGeneric(ctx=ctx,
                              page=page,
                              yourRank=yourRank,
                              embeds=embeds)

            buttons = [ButtonInvite(label='Anterior Página',
                                    disabled=disabledPrevious,
                                    style=discord.ButtonStyle.primary),
                       ButtonInvite(label='Siguiente Página',
                                    disabled=disabledNext,
                                    style=discord.ButtonStyle.primary)]
            for button in buttons: view.add_item(button)
        else:
            embed.description = f"Nada para mostrar..."
            view=None
        await ctx.reply(embed=embed, view=view, mention_author=False)

    """ @command(description="Muestra los códigos de invitación de un usuario.",
             usage="invitecodes [usuario]",
             brief=["invitecodes @! TheDanielrity"],
             aliases=["invcodes"],
             extras=['send_messages'])
    @bot_has_permissions(embed_links=True)
    async def inviteCodes(self, ctx: Context, member: Member = None):
        embed = self.bot.tools.embed(self, ctx)
        if not member: member = ctx.author """
        
    @command(description="Muestra los usuarios invitados por alguien en específico.",
             usage="invitedList [usuario]",
             brief=["invitedList @! TheDanielrity"],
             aliases=["invlist"],
             extras=['send_messages'])
    @bot_has_permissions(embed_links=True)
    async def inviteList(self, ctx: Context, member: Member = None):
        embed = self.bot.tools.embed(self, ctx)
        embed.description = self.bot.config.charging
        message = await ctx.reply(embed=embed, mention_author=False)
        if not member: member = ctx.author
        dataMembers = dbM.selectDataMembers(ctx.guild.id)
        dataMembers = [user for user in dataMembers if user.idMemberInvite == member.id]
        embeds = []
        if dataMembers:
            for i in range(0, len(dataMembers) + 10, 10):
                if i == 0:
                    continue
                description = ''
                position = 1
                for user in dataMembers[i-10:i]:
                    
                    description += f"`{position}. ` <@{user.idMember}> \n"
                    position += 1

                embeds.append(discord.Embed(title=f'Usuarios invitados por {member}',
                                            description=description,
                                            timestamp=datetime.datetime.now(),
                                            color=self.bot.config.defaultColor)
                              .set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar.url))
            
            if len(embeds) == 1:
                disabledNext = True
            else:
                disabledNext = False
            disabledPrevious = True
            view = ViewGeneric(ctx=ctx,
                              page=0,
                              yourRank='',
                              embeds=embeds)

            buttons = [ButtonInvite(label='Anterior Página',
                                    disabled=disabledPrevious,
                                    style=discord.ButtonStyle.primary),
                       ButtonInvite(label='Siguiente Página',
                                    disabled=disabledNext,
                                    style=discord.ButtonStyle.primary)]
            for button in buttons: view.add_item(button)
            embed = embeds[0].set_footer(text=f"Página 1/{len(embeds)}")
        else:
            view = None
            embed.description = 'No se encontraron usuarios...'
            embed.colour = self.bot.config.errorColor
        
        await message.edit(embed=embed, view=view)
        
    @command(description="Muestra quien invitó a un usuario.",
             usage="inviter <usuario>",
             brief=["inviter @! TheDanielrity"],
             aliases=[],
             extras=['send_messages'])
    @bot_has_permissions(embed_links=True)
    async def inviter(self, ctx: Context, member: Member):
        embed = self.bot.tools.embed(self, ctx)
        embed.description = self.bot.config.charging
        message = await ctx.reply(embed=embed, mention_author=False)
        user = self.bot.tools.searchMember(dbM.selectDataMembers(ctx.guild.id), member)
        if user:
            embed.description = f'{member.mention} fue invitado por <@{user.idMemberInvite}> {babel.dates.format_timedelta(-(datetime.datetime.now(tz=pytz.utc)-member.joined_at).total_seconds(), threshold=1.1, add_direction=True, locale="es")}'
        else:
            embed.description = f'No pude saber quien invitó al usuario {member.mention}.'
            embed.colour = self.bot.config.errorColor        
        await message.edit(embed=embed)
            
    @command(description="Agregar invitaciones adicionales a un usuario del servidor.",
             usage="addInvites <usuario> <invitaciones>",
             brief=["addInvites @! TheDanielrity 2"],
             aliases=["addinv"],
             extras=['manage_guild', 'rol_admin', 'send_messages'])
    @checks.rolAdmin(manage_guild=True)
    @bot_has_permissions(embed_links=True)
    @cooldown(1, 5.0, BucketType.member)
    async def addInvites(self, ctx: Context, member: Member, amount: Number):
        embed = self.bot.tools.embed(self, ctx)
        embed.colour = self.bot.config.checkColor                 
        memberData = self.bot.tools.searchMember(dbM.selectDataMembers(ctx.guild.id), member)
        
        if amount:
            if memberData:
                memberData.bonusInvites += amount
                memberData.numInvites += amount 
                await dbM.update([memberData.getAll()], ctx)
            else:
                memberData = MemberInv(member.id, amount, 0, 0, amount, 0, None, True, ctx.guild.id)
                await dbM.insertMembers([memberData.getAll()], ctx)
            embed.description = f'{self.bot.config.emojiCheck} {ctx.author.mention}, le agregaste {amount} invitaciones a {member.mention}.'
        else:
            embed.description = f'{self.bot.config.emojiError} El número de invitaciones para agregar debe estar entre 1 y 100 000 000.'
            embed.colour = self.bot.config.errorColor
        await ctx.send(embed=embed)
        
    @command(description="Remover invitaciones a un usuario del servidor.",
             usage="removeInvites <usuario> <invitaciones>",
             brief=["removeInvites @! TheDanielrity 2"],
             aliases=["removeinv"],
             extras=['manage_guild', 'rol_admin', 'send_messages'])
    @checks.rolAdmin(manage_guild=True)
    @bot_has_permissions(embed_links=True)
    @cooldown(1, 5.0, BucketType.member)
    async def removeInvites(self, ctx: Context, member: Member, amount: Number):
        embed = self.bot.tools.embed(self, ctx)
        embed.colour = self.bot.config.checkColor                 
        memberData = self.bot.tools.searchMember(dbM.selectDataMembers(ctx.guild.id), member)
        
        if amount:
            if memberData:
                memberData.bonusInvites -= amount
                memberData.numInvites -= amount 
                await dbM.update([memberData.getAll()], ctx)
            else:
                memberData = MemberInv(member.id, -amount, 0, 0, -amount, 0, None, True, ctx.guild.id)
                await dbM.insertMembers([memberData.getAll()], ctx)
            embed.description = f'{self.bot.config.emojiCheck} {ctx.author.mention}, le removiste {amount} invitaciones a {member.mention}.'
        else:
            embed.description = f'{self.bot.config.emojiError} El número de invitaciones para remover debe estar entre 1 y 100 000 000.'
            embed.colour = self.bot.config.errorColor
        await ctx.reply(embed=embed, mention_author=False)
    
    @command(description="Eliminar todas las invitaciones del servidor o de un usuario en específico.",
             usage="resetInvites <all | usuario>",
             brief=["resetInvites @! TheDanielrity"],
             aliases=["resetinv"],
             extras=['manage_guild', 'rol_admin', 'send_messages'])
    @checks.rolAdmin(manage_guild=True)
    @bot_has_permissions(embed_links=True)
    @cooldown(1, 10.0, BucketType.member)
    async def resetInvites(self, ctx: Context, param: DoubleParam):
        embed = self.bot.tools.embed(self, ctx)
        embed.description = self.bot.config.charging
        message = await ctx.reply(embed=embed, mention_author=False)
        dataMembers = dbM.selectDataMembers(ctx.guild.id)
        dataMembers = [member for member in dataMembers if sum(member.getAll()[:5]) > 0]
        msgError = f'{self.bot.config.emojiError} No se encontraron invitaciones'
        if dataMembers:  
            embed.colour = self.bot.config.checkColor               
            membersUpdate = []
            if param == 'all':
                for member in dataMembers:
                    member.clearInv()
                    membersUpdate.append(member.getAll())
                embed.description = f'{self.bot.config.emojiCheck} El top de invitaciones a sido restablecido.'
            else:
                member = self.bot.tools.searchMember(dataMembers, param)
                if member:
                    member.clearInv()
                    membersUpdate.append(member.getAll())
                    embed.description = f'{self.bot.config.emojiCheck} Las invitaciones de {param.mention} han sido restablecidas correctamente.'
                else:
                    embed.description = msgError
                    embed.colour = self.bot.config.errorColor
                
            await dbM.update(membersUpdate, ctx)
        else:
            embed.description = msgError
            embed.colour = self.bot.config.errorColor
        await message.edit(embed=embed)
    
    @command(description="Muestra los tags que se pueden utilizar para la configuración del mensaje de invitación.",
             usage="tagsInvites",
             brief=["tagsInvites"],
             aliases=["tagsInv", 'ti'],
             extras=['send_messages'])
    @bot_has_permissions(embed_links=True)
    async def tagsInvites(self, ctx):
        embed = self.bot.tools.embed(self, ctx)
        embed.description = f'Estas son las variables que puede utilizar para el mensaje de invitación.\n\n'
        variables = self.bot.config.VARIABLES_INVITE.keys()
        for variable in variables:
            embed.description += f'`{variable}`: {self.bot.config.VARIABLES_INVITE.get(variable)}\n'
        await ctx.reply(embed=embed, mention_author=False)
    
    @command(description="Sincronice los usos actuales de las invitaciones con el bot para todo el servidor o solo para el miembro mencionado. Ejemplo: Imagine que tiene 0 invitaciones regulares y tiene 2 enlaces de invitación en su servidor, una invitación tiene 80 usos y la otra tiene 20 usos. Después de usar el comando, tendrá un total de 100 invitaciones regulares.",
             usage="syncInvites <all | @usuario>",
             brief=["syncInvites @! TheDanielrity"],
             aliases=["syncinv", ],
             extras=['manage_guild','rol_admin', 'send_messages'])
    @checks.rolAdmin(manage_guild=True)
    @bot_has_permissions(embed_links=True)
    @cooldown(1, 20.0, BucketType.member)
    async def syncInvites(self, ctx: Context, param: DoubleParam):
        embed = self.bot.tools.embed(self, ctx)
        embed.description = self.bot.config.charging
        message = await ctx.reply(embed=embed, mention_author=False)
        update = []
        insert = []
        users = []
        invites = await ctx.guild.invites()
        if not invites:
            embed.description = 'No hay invitaciones en tu servidor.'
            embed.colour = self.bot.config.errorColor
        else:
            members = dbM.selectDataMembers(ctx.guild.id)
            if param == 'all':
                for member in members:
                    invites = self.bot.tools.syncInvites(invites, member, update)

                for invite in invites:
                    if discord.utils.get(ctx.guild.members, id=invite.inviter.id): i = 1
                    else: i = 0
                    users.append(MemberInv(invite.inviter.id, 0,0,0,0,0,None,i,ctx.guild.id))
                for user in users:
                    invites = self.bot.tools.syncInvites(invites, user, insert)
                    
            else:
                member = self.bot.tools.searchMember(members, param)
                if member:
                    self.bot.tools.syncInvites(invites, member, update)
                else:
                    if discord.utils.get(ctx.guild.members, id=param.id): i = 1
                    else: i = 0
                    member = MemberInv(param.id, 0,0,0,0,0,None,i,ctx.guild.id)
                    self.bot.tools.syncInvites(invites, member, insert)
            await dbM.update(update, ctx)
            if insert: await dbM.insertMembers(insert, ctx)
            embed.description = f'{self.bot.config.emojiCheck} Se sincronizaron correctamente las invitaciones. '
            embed.colour = self.bot.config.checkColor
        await message.edit(embed=embed)
        
    
        
        
async def setup(bot):
    await bot.add_cog(Invites(bot))
