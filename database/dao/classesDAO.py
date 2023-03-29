from typing import List
import discord, datetime, config
from database.cursor import Cursor
from database.dao.metaclass import DAO
from database.classes.guild import GuildConfig, GuildInvites, GuildImages
from database.classes.member import Member
import logging as log
log.getLogger(__name__)

class MemberDAO(metaclass=DAO):
    _SELECT = "SELECT * FROM memberInvites WHERE idGuild = '%s'"
    
    _INSERT = "INSERT INTO memberInvites(numInvites, regularInvites, leaveInvites,"\
              "bonusInvites, fakeInvites, idMemberInvite, joinLeave, idMember, idGuild)" \
              "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    _UPDATE = "UPDATE memberInvites SET numInvites = %s, regularInvites = %s, leaveInvites = %s, bonusInvites = %s, fakeInvites = %s, idMemberInvite = %s, joinLeave = %s WHERE idMember = '%s' AND idGuild = '%s'"
    
    @classmethod
    def selectDataMembers(cls, idGuild) -> List[Member] or List[None]:
        with Cursor() as cur:
            cur.execute(cls._SELECT, (idGuild, ))
            data = cur.fetchall()
        members = []
        for record in data:
            members.append(Member(*record))
        return members
    
    @classmethod
    async def insertMembers(cls, data, ctx_or_channel=None):
        try:
            members = cls.selectDataMembers(data[0][-1])
            for d in data:
                for member in members:
                    if (d[-2] == member.idMember and d[-1] == member.idGuild):        
                        data.remove(d)
                        break
            with Cursor() as cur:
                cur.executemany(cls._INSERT, data)
                        
                
        except Exception as e:
            try: await ctx_or_channel.bot.close()
            except: pass
            if ctx_or_channel:
                embed = cls.embed(ctx_or_channel)
                await ctx_or_channel.send(embed=embed)


class GuildConfigDAO(metaclass=DAO):
    _SELECT = "SELECT * FROM guildConfig WHERE idGuild = '%s'"
    
    _UPDATE = "UPDATE guildConfig SET prefix = %s, idRoleMute = %s, idRoleAdmin = %s, idRoleJoin = %s WHERE idGuild = '%s'"
    _DELETE = "DELETE FROM guildConfig WHERE idGuild = '%s'"
    
    @classmethod
    def deleteGuild(cls, idGuild):
        with Cursor() as cur:
            cur.execute("DELETE FROM guildConfig WHERE idGuild = '%s'", (idGuild,))
            
    @classmethod
    def selectGuildConfig(cls, idGuild) -> GuildConfig:
        with Cursor() as cur:
            cur.execute(cls._SELECT, (idGuild, ))
            guild = cur.fetchone()
            return GuildConfig(*guild)
    
    @classmethod
    async def insertGuild(cls, idGuild, ctx_or_channel=None):
        try:
            for table in ['guildConfig', 'guildImages', 'guildInvites']:
                with Cursor() as cur:
                    cur.execute(f'INSERT INTO {table}(idguild) VALUES(%s)', (idGuild,))
        except Exception as e:
            try: await ctx_or_channel.bot.close()
            except: pass
            if ctx_or_channel:
                embed = cls.embed(ctx_or_channel)
                await ctx_or_channel.send(embed=embed)
        
class GuildInvitesDAO(metaclass=DAO):
    _SELECT = "SELECT * FROM guildInvites WHERE idGuild = '%s'"
    
    _UPDATE = "UPDATE guildInvites SET timeFake = %s, msgRegularInvite = %s, msgSelfInvite = %s, msgUnknownInvite = %s, msgVanityInvite = %s, idChannelInvite = %s WHERE idGuild = '%s'"
    
    @classmethod
    def selectGuildInvites(cls, idGuild) -> GuildInvites:
        with Cursor() as cur:
            cur.execute(cls._SELECT, (idGuild, ))
            guild = cur.fetchone()
            return GuildInvites(*guild)
        

class GuildImagesDAO(metaclass=DAO):
    _SELECT = "SELECT * FROM guildImages WHERE idGuild = '%s'"
    
    _UPDATE = "UPDATE guildImages SET imageJoin = %s, textJoin = %s, idChannelJoin = %s, colorJoin = %s, imageLeave = %s, textLeave = %s, idChannelLeave = %s, colorLeave = %s, imageBoost = %s, textBoost = %s, idChannelBoost = %s, colorBoost = %s WHERE idGuild = '%s'"
    
    @classmethod
    def selectGuildImages(cls, idGuild) -> GuildImages:
        with Cursor() as cur:
            cur.execute(cls._SELECT, (idGuild, ))
            guild = cur.fetchone()
            return GuildImages(*guild)
    
    
        

        
    
    