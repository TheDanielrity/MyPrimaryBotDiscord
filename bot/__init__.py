import sys, traceback, asyncio, discord, config, datetime, aiohttp
from discord.ext.commands import AutoShardedBot as BaseBot, errors, when_mentioned_or
from database.classes.member import Member
from database.dao.classesDAO import MemberDAO
from database.cursor import Cursor
from utils import tools
import logging as log
log.getLogger(__name__)
class Bot(BaseBot):
    BOTUSER = None
    _prefixes = {}
    _roles = {}
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = datetime.datetime.utcnow()
        # self.session = aiohttp.ClientSession(loop=self.loop)
        self.cluster = kwargs.get("cluster_id")
        self.cluster_count = kwargs.get("cluster_count")
        self.version = kwargs.get("version")

    @property
    def prefixes(self):
        return Bot._prefixes

    @property
    def roles(self):
        return Bot._roles
    
    @property
    def config(self):
        return config
    
    @property
    def tools(self):
        return tools
    
    @property
    def botUser(cls):
        return cls.BOTUSER

    @classmethod
    async def getallData(cls):
        with Cursor() as cur:
            cur.execute('SELECT idGuild, prefix, idRoleAdmin, idRoleMute, idRoleJoin FROM guildConfig')
            prefixes = cur.fetchall()
            
        for idGuild, prefix, idRoleAdmin, idRoleMute, idRoleJoin in prefixes:
            cls._prefixes[int(idGuild)] = prefix if prefix else '.'
            cls._roles[int(idGuild)] = {'idRoleMute':int(idRoleMute) if idRoleMute else 0, 'idRoleAdmin': int(idRoleAdmin) if idRoleAdmin else 0, 'idRoleJoin':int(idRoleJoin) if idRoleJoin else 0 }
    async def on_ready(self):
        """ count = 0
        for guild in self.guilds:
            count += 1
            print(f'{guild} {count}')
            print(guild.id)
            for invite in await guild.invites():
                print(invite) """            
        inicio = datetime.datetime.now()
        await self.getallData()
        print(f'tiempo de carga getData {(datetime.datetime.now()-inicio).total_seconds()}')
        await self.change_presence(activity=discord.Streaming(
            name=f"{self.config.PREFIX}help",
            url="http://www.twitch.tv/thedanielrity"))
        self.BOTUSER = self.user
        
        print('listo')


    async def start_bot(self):
        for extension in self.config.cogs:
            try:
                await self.load_extension(extension)
                print(f'cog {extension} listo')
            except Exception:
                log.error(f"Failed to load extension {extension}.", file=sys.stderr)
                log.error(traceback.print_exc())
        await self.start('NzU5NTgzOTg5NzU2ODU0Mjg0.X2_ntw.JsCa0TVQeUTH_V-koeD7Ny3p9P8')


