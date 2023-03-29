from discord.ext.commands import Converter, MemberConverter, TextChannelConverter, UserConverter
from discord.ext.commands.converter import EmojiConverter, GuildConverter, ObjectConverter, RoleConverter
from bot import class_errors as err
import logging, discord, re
logging.getLogger(__name__)

class DoubleParam(UserConverter):
    async def convert(self, ctx, arg):
        try:
            user = await super().convert(ctx, arg)
            return user
        except err.CommandError as e:
            if arg == 'all':
                return arg
            raise err.BadArgument_('<all | usuario>')
    
class Member(MemberConverter):    
    async def convert(self, ctx, arg):
        try:
            member = await super().convert(ctx, arg)
            return member
        except err.CommandError as e:
            raise err.BadArgument_('<usuario>')
class User(UserConverter):    
    async def convert(self, ctx, arg):
        try:
            member = await super().convert(ctx, arg)
            return member
        except err.CommandError as e:
            raise err.BadArgument_('<usuario>')

class TextChannel(TextChannelConverter):    
    async def convert(self, ctx, arg):
        try:
            channel = await super().convert(ctx, arg)
            return channel
        except err.CommandError as e:
            raise err.BadArgument_('<canal>')

class Number(Converter):
    async def convert(self, ctx, num):
        try:
            return int(num)
        except:
            raise err.BadArgument_(f'{ctx.command.signature.split(" ")[-1]}')
        
class Role(RoleConverter):
    async def convert(self, ctx, arg):
        try:
            role = await super().convert(ctx, arg)
            return role
        except err.CommandError as e:
            raise err.BadArgument_('<rol>')

class Emoji(EmojiConverter):
    async def convert(self, ctx, arg):
        try:
            emoji = await super().convert(ctx, arg)
            return emoji
        except err.CommandError as e:
            raise err.BadArgument_('<emoji>')
    
    
def verifyParam(param):
    l = ['all', 'invites', 'config']
    if param in l:
        return param
    else:
        raise err.BadArgument_('<all | invites | config>')

def convertTime(duration):
    time = ["s", "m", "h", "d", "y"]
    times = {"s": "segundo(s)", "m": "minuto(s)", "h": "hora(s)", "d": "día(s)", "y": "año(s)"}
    dates = {"s": 1, "m": 60, "h": 60 * 60, "d": 60 * 60 * 24, "y": 31536000}

    if duration.isalnum():
        duration = duration.lower()
        unit_time = duration[-1]
        try:
            val_time = int(duration[:-1])

        except:
            return 0
        if unit_time not in time or not val_time:
            return 0
        
        return [val_time * dates[unit_time], times[unit_time], val_time]
    
    return 0


def gconvertTime(duration):
    time = ["s", "m", "h", "d"]
    dates = {"s": 1, "m": 60, "h": 60 * 60, "d": 60 * 60 * 24}
    
    if duration.isalnum():
        duration = duration.lower()
        unit_time = duration[-1]
        if unit_time not in time:
            return 0
        try:
            val_time = int(duration[:-1])
        except:
            return 0
        if val_time == 0:
            return 1
        if unit_time == "s" and val_time < 10:
            return 1
        elif unit_time == "d" and val_time > 14:
            return 1
        elif unit_time == "s":
            segundos = val_time % 60
            minutos = val_time // 60
            if minutos == 0:
                return [f"**{segundos}** segundos.", val_time * dates[unit_time]]
            else:
                return [f"**{minutos}** " + ("minuto" if minutos == 1 else "minutos") + (
                    "." if minutos == 0 else f", **{minutos}** " + ("minuto." if minutos == 1 else "minutos.")),
                        val_time * dates[unit_time]]
        elif unit_time == "m":
            minutos = val_time % 60
            horas = val_time // 60
            if horas == 0:
                return [f"**{minutos}** " + ("minuto." if minutos == 1 else "minutos."), val_time * dates[unit_time]]
            else:
                return [f"**{horas}** " + ("hora" if horas == 1 else "horas") + (
                    "." if minutos == 0 else f", **{minutos}** " + ("minuto." if minutos == 1 else "minutos.")),
                        val_time * dates[unit_time]]
        elif unit_time == "h":
            horas = val_time % 24
            dias = val_time // 24
            if dias == 0:
                return [f"**{horas}** " + ("hora." if horas == 1 else "horas."), val_time * dates[unit_time]]
            else:
                return [f"**{dias}** " + ("día" if dias == 1 else "días") + (
                    "." if horas == 0 else f", **{horas}** " + ("hora." if horas == 1 else "horas.")),
                        val_time * dates[unit_time]]
        elif unit_time == "d":
            dias = val_time % 7
            semanas = val_time // 7
            if semanas == 0:
                return [f"**{dias}** " + ("día." if dias == 1 else "días."), val_time * dates[unit_time]]
            else:
                return [f"**{semanas}** " + ("semana" if semanas == 1 else "semanas") + (
                    "." if dias == 0 else f", **{dias}** " + ("día." if dias == 1 else "días.")),
                        val_time * dates[unit_time]]
        else:
            pass
    else:
        return 0