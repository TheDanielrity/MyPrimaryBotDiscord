import discord, datetime, logging
from discord.ext.commands import Cog, Context
from bot import class_errors as err
from babel.dates import format_timedelta
logging.getLogger(__name__)


class ErrorHandlers(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.on_command_error = self._on_command_error

    async def _on_command_error(self, ctx, error):
        embed: discord.Embed = self.bot.tools.embed(self, ctx)
        embed.colour = self.bot.config.errorColor
        prefix = ctx.prefix
        command = ctx.command
        
        
        if isinstance(error, err.BadArgument):
            embed.description = f"{self.bot.config.emojiError} El argumento `{error.message}` proporcionado es inválido.\n\nSintaxis del comando:\n`{prefix}{command.signature}`\n\nEjemplo:\n`{prefix}" + (
            f"\n{prefix}".join(command.brief) if len(command.brief) > 1 else command.brief[0]) + '`'
        
        elif isinstance(error, err.MissingRequiredArgument):
            embed.description = f'{self.bot.config.emojiError} Se han dado muy pocos argumentos.\n\nSintaxis del comando:\n`{prefix}{command.signature}`\n\nEjemplo:\n`{prefix}' + (
            f"\n{prefix}".join(command.brief) if len(command.brief) > 1 else command.brief[0]) + '`'
        
        elif isinstance(error, err.BotMissingPermissions):
            if 'embed_links' in error.missing_permissions:
                await ctx.send(f'{self.bot.config.emojiError} Necesito el permiso: `Insertar enlaces`.\n\nAsegúrese de verificar los permisos de mis roles y también los permisos específicos del canal. Gracias.')
                return
            perms = []
            for perm in error.missing_permissions:
                perms.append(self.bot.config.permissions.get(perm))
            embed.description = f'{self.bot.config.emojiError} No tengo permisos suficientes para ejecutar este comando.\nNecesito: `{"`, `".join(perms)}`'
        
        elif isinstance(error, err.MissingPermissions):
            perms = []
            for perm in error.missing_permissions:
                perms.append(self.bot.config.permissions.get(perm))
            embed.description = f'{self.bot.config.emojiError} No tienes permiso para usar el comando `{ctx.command}`. \nNecesitas: `{"`, `".join(perms)}`'
        
        elif isinstance(error, err.CommandOnCooldown):
            embed.description = f"{self.bot.config.emojiError} Debes esperar `{format_timedelta(datetime.timedelta(seconds=round(error.retry_after)), threshold=0.9, locale='es')}` para usar el comando `{ctx.prefix}{ctx.command.name}` nuevamente."
        elif isinstance(error, err.NotOwnerGuild):
            embed.description = f'{self.bot.config.emojiError} Solo el propietario del servidor puede ejecutar este comando.'
        elif isinstance(error, err.NoPrivateMessage):
            pass
        
        elif isinstance(error, Exception):
            raise error

        await ctx.send(embed=embed)
async def setup(bot):
    await bot.add_cog(ErrorHandlers(bot))