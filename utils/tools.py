from typing import Union
import discord, aiohttp, io, datetime
from discord.ext.commands import when_mentioned_or
from database import classes as c
import logging as log
from PIL import Image, ImageDraw, ImageFont
from discord.ext.commands import Context
log.getLogger(__name__)

class FormatMap(dict):
    def __missing__(self, key):
        return key
async def setPerms(role, c):
    await c.set_permissions(role, send_messages=False)
    

async def moderation(self, member, ctx, guild, sanction, reason, embed):
    fields = [("Usuario:", f"{member.mention}", False),
            ("Sanción:", f'{sanction}', False ),
            ("Razón:", f"{reason}", False),
            ("Realizado por:", f"{ctx.author.mention}",False)]
    rolAdmin = ctx.guild.get_role(guild.idRoleAdmin if guild.idRoleAdmin else 0)
    
    if isinstance(member, discord.User):
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.color = self.bot.config.defaultColor
        await ctx.guild.ban(member, reason=f"{ctx.author} - {reason}")
        
    elif ctx.guild.me == member:
        embed.description = f"{self.bot.config.emojiError} No puedes " + ('banearme.' if sanction == 'Baneado' else 'expulsarme.')
        
        
    elif ctx.author.id == member.id:
        embed.description = f"{self.bot.config.emojiError} No puedes " + ('banearte' if sanction == 'Baneado' else 'expulsarte')+ ' a ti mismo.'
    
    elif ctx.guild.me.top_role.position < member.top_role.position or (rolAdmin in member.roles):
        embed.description = f"{self.bot.config.emojiError} Verifica que mi rol este por encima de los demás."        
    else:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.color = self.bot.config.defaultColor
        try:
            await member.send(embed=embed)
        except:
            pass
        
        await member.kick(reason=f"{ctx.author} - {reason}")
    await ctx.reply(embed=embed, mention_author=False)
    
def rolPerms(ctx, role, bot):
    for category in ctx.guild.categories:
        bot.loop.create_task(setPerms(role, category))
    for channel in ctx.guild.text_channels:
        bot.loop.create_task(setPerms(role, channel))
        
def syncInvites(invites, member, l):
    
    invites_ = list(filter(lambda invite: invite.inviter.id == member.idMember, invites))
    for invite in invites_: member.setterInv(invite.uses, invite.uses,0,0)
    l.append(member.getAll())
    invites = list(filter(lambda invite: invite.inviter.id != member.idMember, invites))
    return invites


def embed(self, ctx) -> discord.Embed:
    embed = discord.Embed(timestamp=datetime.datetime.now(),
                            color=self.bot.config.defaultColor) \
            .set_author(name=f'{ctx.author}',
                        icon_url=ctx.author.display_avatar.url) \
            .set_footer(text=f'{self.bot.botUser}•Solicitado por {ctx.author}',
                        icon_url=self.bot.botUser.display_avatar.url)
    return embed
    
def embeds(guild: Union[c.GuildImages, c.GuildConfig], generic: str, ctx: Context, select):
    image = text = idChannel = color = textEmbed = idRole = None
    if isinstance(guild, c.GuildImages):
        image, text, idChannel, color, textEmbed = guild.getAll(generic)
    else:
        idRole, textEmbed = guild.getAll(generic)
    embeds = [
            [
                f'**Establecer la imagen de {textEmbed}**\n\nHay una imagen de {textEmbed} establecida.\n\n:pencil2: Establecer imagen.\n:wastebasket: Borrar imagen.\n:leftwards_arrow_with_hook: Regresar.' if image else f'**Establecer una imagen de {textEmbed}**\n\nAún no se ha establecido una imagen de {textEmbed}.\n\n:pencil2: Establecer imagen.\n:leftwards_arrow_with_hook: Regresar.',
                'Suba la imagen o escriba el link de esta misma.\nEscriba `cancel` para regresar.'
            ],
            [
                f'**Establecer el mensaje de {textEmbed}**\n\nEl mensaje de {textEmbed} actual es: \n```{text}```\n\n:pencil2: Establecer mensaje.\n:wastebasket: Borrar mensaje.\n:leftwards_arrow_with_hook: Regresar.' if text else f'**Establecer el mensaje de {textEmbed}.**\n\nAún no se ha establecido un mensaje de {textEmbed}.\n\n:pencil2: Establecer mensaje.\n:leftwards_arrow_with_hook: Regresar.',
                
                f'Estás editando el mensaje de {textEmbed}. El mensaje no debe ser mayor a 1000 caracteres.\n' + (f'El mensaje configurado actual es:\n```{text}```\n\n' if text else '\n') + 'Escriba su mensaje en este canal. Escriba `cancel` para regresar.'

            ],
            [
                f'**Establecer el canal para los mensajes de {textEmbed}**\n\nEl canal establecido para los mensajes de {textEmbed} actual es: {ctx.guild.get_channel(idChannel).mention if ctx.guild.get_channel(idChannel) else "#delete-channel"}.\n\n:pencil2: Establecer canal.\n:wastebasket: Borrar canal.\n:leftwards_arrow_with_hook: Regresar.' if idChannel else f'**Establecer el canal para los mensajes de {textEmbed}**\n\nNo hay un canal establecido para los mensajes de {textEmbed} actual.\n\n:pencil2: Establecer canal\n:leftwards_arrow_with_hook: Regresar.',
                
                f'\nMencione el canal para los mensajes de {textEmbed}.\nEscriba `cancel` para regresar.'
            ],
            [
                f'**Establecer el color del texto de {textEmbed}**\n\nEl color establecido actual es: `{color}`.\n\n:pencil2: Establecer color.\n:wastebasket: Color predeterminado.\n:leftwards_arrow_with_hook: Regresar.',
                '\nEscriba el número hexadecimal del color. Te recomendamos esta página para obtener colores https://htmlcolorcodes.com/es/\nEjemplo: `FFFFFF -> Color Blanco`\nEscriba `cancel` para regresar.'
            ],
            [
                f'**Establecer el rol de {textEmbed}**\n\nEl rol establecido para {textEmbed} actual es: {ctx.guild.get_role(idRole).mention if ctx.guild.get_role(idRole) else "@deleted-role"}.\n\n:pencil2: Establecer rol.\n:wastebasket: Borrar rol.\n:leftwards_arrow_with_hook: Regresar.' if idRole else f'**Establecer el canal para los mensajes de {textEmbed}**\n\nNo hay un rol establecido para {textEmbed}.\n\n:pencil2: Establecer rol\n:leftwards_arrow_with_hook: Regresar.' + ('\n:new: Crear rol' if textEmbed == 'Mute' and (not idRole) else ''),
                
                f'\nMencione el rol para {textEmbed}.\nEscriba `cancel` para regresar.'
                ],
            f'**Configurar la sección de Roles del servidor**\n\nSelecciona una opción:\n<a:muted:881910991305187380> Configurar rol Mute.\n<:admin:881910502861709385> Configurar rol Admin.\n<a:join:881952082612060190> Configura rol Ingreso\n:x: Cancelar.',
            
            f'**Configurar la sección de {textEmbed} del servidor**\n\nSelecciona una opción:\n:dividers: Configurar el banner.\n:scroll: Configurar el mensaje.\n:envelope: Configurar el canal.\n:crayon: Configurar color\n:pencil: Testear {textEmbed}.\n:x: Cancelar.'
                 ]
    if len(select) == 1:
        return embeds[select[0]]
    else:
        return embeds[select[0]][select[1]]

def searchMember(data, member) -> c.Member or None:
    memberReturn = None
    for m in data:
        if member.id == m.idMember:
            memberReturn = m
            return memberReturn 
    return memberReturn          

async def image(ctx_member, dataGuild, generic):
    image, color, textGeneral = dataGuild.getImgText(generic)
    if not image: return None
    
    if isinstance(ctx_member, Context):
        member = ctx_member.author
    else:
        member = ctx_member
        
    background_image = Image.open(io.BytesIO(image)).resize((1024,500)) 
    background_image = background_image.convert('RGBA')
    AVATAR_SIZE = 252

    draw = ImageDraw.Draw(background_image) 


    text = f'{member}'
    text1 = textGeneral
    
    font = ImageFont.truetype(font='./utils/uni.ttf', size=85)
    font1 = ImageFont.truetype(font='./utils/uni.ttf', size=50)


    x,y = draw.textsize(text, font=font1)
    x1,y1 = draw.textsize(text1, font=font)
    draw.text(((1024-x1)/2,320), text1, fill=f'#{color}', font=font)
    draw.text(((1024-x)/2,410), text, fill=f'#{color}',font=font1)
    
    
    avatar_asset = member.display_avatar.replace(size=1024,format='png')

    buffer_avatar = io.BytesIO(await avatar_asset.read())

    avatar_image = Image.open(buffer_avatar)

    avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE)) 


    circle_image = Image.new('L', (AVATAR_SIZE, AVATAR_SIZE))
    circle_draw = ImageDraw.Draw(circle_image)
    circle_draw.ellipse((8,8, AVATAR_SIZE, AVATAR_SIZE), fill=255)
    
    new_img = Image.new('RGB', (AVATAR_SIZE+8, AVATAR_SIZE+8), f'#{color}')
    border = Image.new('L', (AVATAR_SIZE+8, AVATAR_SIZE+8))
    draw_border = ImageDraw.Draw(border)
    draw_border.ellipse((0, 0, AVATAR_SIZE+8, AVATAR_SIZE+8),fill=255)
    background_image.paste(new_img, (386, 45), border)
    background_image.paste(avatar_image, (386, 45),circle_image)



    buffer_output = io.BytesIO()


    background_image.save(buffer_output, format='PNG')


    buffer_output.seek(0)
    
    return discord.File(buffer_output, f'{member}.png')


def getPrefix(bot, message):
    prefix = bot.prefixes.get(message.guild.id)
    return when_mentioned_or(prefix, "daniel ")(bot, message)