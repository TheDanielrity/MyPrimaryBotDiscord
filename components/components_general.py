from discord.ui import Select, Button, Item, View, button
from discord.ext.commands import (Cog, command, Context, Command)
from bot import Bot
import discord, typing, datetime, asyncio, logging

logging.getLogger(__name__)


class ButtonCommand(Button):
    def __init__(self, label, bot: Bot, ctx: Context):
        self.bot = bot
        self.ctx = ctx
        super().__init__(style=discord.ButtonStyle.green, label=label)

    async def callback(self, interaction: discord.Interaction):
        command = self.bot.get_command(self.label)
        msg = SelectCog.commandHelp(self.bot, self.ctx, command)
        if interaction.user == self.ctx.author:
            self.view.stop()
            await interaction.response.edit_message(content='', embed=msg, view=None)


class SelectCog(Select):
    def __init__(self, placeholder, options, bot: Bot, ctx: Context, cogs):
        self.bot = bot
        self.ctx = ctx
        self.cogs = cogs
        super().__init__(placeholder=placeholder, options=options)

    @staticmethod
    def commandHelp(bot, ctx, command: Command):
        s = '`'
        prefix = ctx.prefix
        perms = [ bot.config.permissions.get(perm) for perm in command.extras]
        msg = discord.Embed(color=bot.config.defaultColor, description=f'Ayuda sobre el comando `{command.name}`').set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar.url)
        msg.add_field(name="Descripción del comando:", value=f"{command.description}", inline=False)
        msg.add_field(name="Categoría del comando:", value=f"{command.cog_name}", inline=False)
        msg.add_field(name=f"Alias del comando ({len(command.aliases)}):", value=(
            s + "`, `".join(command.aliases) + s if len(command.aliases) > 1 else f"`{command.aliases[0]}`" if len(command.aliases) != 0 else 'Ninguno'),
                      inline=False)
        msg.add_field(name='Permisos necesarios:', value=s + '`, `'.join(perms) + s, inline=False)
        msg.add_field(name="Sintaxis del comando:", value=f"`{prefix}{command.signature}`", inline=False)
        msg.add_field(name="Ejemplo", value=f"`{prefix}" + (f"\n{prefix}".join(command.brief) if len(command.brief) > 1 else command.brief[0]) + s, inline=False)
        msg.set_footer(
            text="<> = obligatorio | [] = opcional. | No incluyas estos símbolos al momento de ejecutar el comando.",
            icon_url=bot.botUser.display_avatar.url)
        return msg
        
    async def callback(self, interaction: discord.Interaction):
            categoria = self.values[-1]
            cog = None
            for name, cog in self.cogs:
                if name.lower() == categoria.lower():
                    cog = cog
                    break
            commands = cog.get_commands()
            commandsList = []
            for command in commands:
                name = command.name.split()[-1]
                commandsList.append(ButtonCommand(label=name, ctx=self.ctx, bot=self.bot))

            for item in self.view.children:
                if isinstance(item, Select):
                    select = item
            self.view.clear_items()
            for buttonCommand in commandsList:
                self.view.add_item(buttonCommand)
            self.view.add_item(select)
            if interaction.user == self.ctx.author:
                await interaction.response.edit_message(
                    content='Haga click en un botón para obtener más información sobre el comando o seleccione otra categoría.',
                    embed=None,
                    view=self.view
                )
    





