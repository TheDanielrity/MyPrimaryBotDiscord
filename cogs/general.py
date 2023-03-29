from discord.ext.commands import (Cog, command, Context)
import discord, random, typing, logging
from bot import Bot
from components.components_general import SelectCog, View
logging.getLogger(__name__)


class General(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message = None
        
    @Cog.listener()
    async def on_message(self, message):
        
        self.message = message
        

    @command()
    async def help(self, ctx: Context, cmd: typing.Optional[str] = None):
        prefix = ctx.prefix
        msg = discord.Embed(color=self.bot.config.defaultColor).set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar.url)
        cogs = []
        for cog in self.bot.cogs:
            if cog == 'General' or cog == 'Events' or cog == 'ErrorHandlers':
                continue
            cog = self.bot.get_cog(cog)
            cogs.append((cog.qualified_name.split()[-1], cog))
        options = []
        for name, cog in cogs:
            options.append(
                discord.SelectOption(
                    label=cog.qualified_name.split()[-1],
                    description=cog.description,
                    value=f'{name}',
                    emoji=cog.qualified_name.split()[0],
                )
            )

        select = SelectCog(
            placeholder='Selecciona una categoría',
            options=options,
            bot=self.bot,
            ctx=ctx,
            cogs=cogs,
        )

        if cmd:
            command = self.bot.get_command(cmd)
            if command:
                msg = SelectCog.commandHelp(self.bot, ctx, command)
            else:
                msg.description = f':x: **__Comando desconocido__**\n\nEscriba `{prefix}help` para la lista de categorías.'
                msg.set_footer(
                    text=f'{self.bot.botUser}•Solicitado por {ctx.author}',
                    icon_url=self.bot.botUser.display_avatar.url
                )
            view = None
        else:
            msg.description = f"Bienvenido a la ayuda de {self.bot.botUser.mention}. Mi prefix en este servidor es `{prefix}`. Para obtener la ayuda de un comando, escriba `{prefix}help <comando>`."
            msg.set_footer(
                    text=f'{self.bot.botUser}•Desarrollado por ! CAMARADA DANIEL#5372',
                    icon_url=self.bot.botUser.display_avatar.url
            )
            view = View()
            view.add_item(select)
            
        await ctx.reply(embed=msg, view=view, mention_author=False)


async def setup(bot):
    await bot.add_cog(General(bot))