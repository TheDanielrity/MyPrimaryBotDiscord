from inspect import Parameter
from typing import List, Tuple, Type
from discord.ext.commands.errors import *
import logging

logging.getLogger(__name__)

class BadArgument_(BadArgument):
    def __init__(self, message):
        self.message = message
        
class NotOwnerGuild(CheckFailure):
    pass

class NotRoleAdmin(CheckFailure):
    pass        
