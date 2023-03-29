import discord, datetime, logging, io
from discord.ext.commands import Cog, Context, command, errors
from database.dao.classesDAO import GuildConfigDAO as dbGC, GuildImagesDAO as dbGI
from database.classes import GuildConfig
from PIL import Image, ImageDraw, ImageFont
logging.getLogger(__name__)


class Events(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.on_message = self._on_message 

    async def _on_message(self, message):
        if len(message.mentions) == 1:
            if message.mentions[0].id == self.bot.botUser.id:
                prefix = self.bot.prefixes[message.guild.id]
                embed = discord.Embed(timestamp=datetime.datetime.now(),
                                    color=self.bot.config.defaultColor,
                                    description=f'Mi prefix aquí es `{prefix}`\n Si escribes `{prefix}help` puedes ver mi lista de categorías.') \
                .set_author(name=f'{message.author}',
                            icon_url=message.author.display_avatar.url) \
                .set_footer(text=f'{self.bot.botUser}',
                            icon_url=self.bot.botUser.display_avatar.url)
                
                await message.reply(embed=embed, mention_author=False)
        await self.bot.process_commands(message)
        return
    
    @Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not member.id == self.bot.botUser.id:
            guild = dbGI.selectGuildImages(member.guild.id)
            channel = member.guild.get_channel(guild.idChannelJoin)
            role = member.guild.get_role(self.bot.roles.get(member.guild.id).get('idRoleJoin'))
            if role:
                await member.add_roles(role, reason='Nuevo Usuario')
            if channel:
                if guild.textJoin or guild.imageJoin:
                    text = guild.textJoin.format_map(self.bot.tools.FormatMap(
                        member=member,
                        member_name=member.name,
                        member_mention=member.mention,
                        server=member.guild.name)) if guild.textJoin else ''              
                    file = await self.bot.tools.image(member, guild, 'join')
                    await channel.send(text, file=file)
        return
    
    @Cog.listener()
    async def on_member_remove(self, member):
        if not member.id == self.bot.botUser.id:
            guild = dbGI.selectGuildImages(member.guild.id)
            channel = member.guild.get_channel(guild.idChannelLeave)
            if channel:
                if guild.textLeave or guild.imageLeave:
                    text = guild.textLeave.format_map(self.bot.tools.FormatMap(
                        member=member,
                        member_name=member.name,
                        member_mention=member.mention,
                        server=member.guild.name)) if guild.textLeave else ''              
                    file = await self.bot.tools.image(member, guild, 'leave')
                    await channel.send(text, file=file)
        return
    @Cog.listener()
    async def on_guild_join(self, guild):
        await dbGC.insertGuild(guild.id)
        self.bot.prefixes[guild.id] = '.'
        self.bot.roles[guild.id] = {'idRoleMute': 0, 'idRoleAdmin': 0, 'idRoleJoin': 0}
        return
    
    @Cog.listener()
    async def on_guild_remove(self, guild):
        dbGC.deleteGuild(guild.id)
        self.bot.prefixes.pop(guild.id)
        self.bot.roles.pop(guild.id)
    
    @Cog.listener()
    async def on_member_update(self, before, after):
        if not (before.id == self.bot.botUser.id):
            guild = dbGI.selectGuildImages(before.guild.id)
            channel = after.guild.get_channel(guild.idChannelBoost)
            if before.premium_since is None and after.premium_since is not None and channel:
                    if guild.textBoost or guild.imageBoost:
                        text = guild.textBoost.format_map(self.bot.tools.FormatMap(
                            member=before,
                            member_name=before.name,
                            member_mention=before.mention,
                            server=before.guild.name)) if guild.textBoost else ''
                        file = await self.bot.tools.image(before, guild, 'boost')
                        await channel.send(text, file=file)
        return
    

    @Cog.listener()
    async def on_shard_ready(self, shard):
        
        embed = discord.Embed(
            title=f"[Cluster {self.bot.cluster}] Shard {shard} Ready",
            colour=0x00FF00,
            timestamp=datetime.datetime.now(),
        )
        if self.bot.config.event_channel:
            c = await self.bot.fetch_channel(self.bot.config.event_channel)
            await c.send(embed=embed)

    @Cog.listener()
    async def on_shard_connect(self, shard):
        embed = discord.Embed(
            title=f"[Cluster {self.bot.cluster}] Shard {shard} Connected",
            colour=0x00FF00,
            timestamp=datetime.datetime.now(),
        )
        if self.bot.config.event_channel:
            c = await self.bot.fetch_channel(self.bot.config.event_channel)
            await c.send(embed=embed)

    @Cog.listener()
    async def on_shard_disconnect(self, shard):
        embed = discord.Embed(
            title=f"[Cluster {self.bot.cluster}] Shard {shard} Disconnected",
            colour=0xFF0000,
            timestamp=datetime.datetime.now(),
        )
        if self.bot.config.event_channel:
            c = await self.bot.fetch_channel(self.bot.config.event_channel)
            await c.send(embed=embed.to_dict())

    @Cog.listener()
    async def on_shard_resumed(self, shard):
        embed = discord.Embed(
            title=f"[Cluster {self.bot.cluster}] Shard {shard} Resumed",
            colour=self.bot.config.defaultColor,
            timestamp=datetime.datetime.now(),
        )
        if self.bot.config.event_channel:
            c = await self.bot.fetch_channel(self.bot.config.event_channel)
            await c.send(embed=embed.to_dict())
            
async def setup(bot):
    await bot.add_cog(Events(bot))