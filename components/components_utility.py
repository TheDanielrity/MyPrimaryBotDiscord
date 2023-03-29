from discord.ui import Select, Button, Item, View, button
from discord.ext.commands import (Cog, command, Context, Command)
from bot import Bot
import discord, typing, datetime, asyncio, logging

class ViewGeneric(View):
    def __init__(self, label, url):
        super().__init__()
        self.add_item(Button(style=discord.ButtonStyle.url, label=label, url=url))
    

        