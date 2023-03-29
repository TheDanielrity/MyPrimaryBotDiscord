import config

class GuildConfig:
    
    def __init__(self, idGuild, prefix = None, idRoleMute = None, idRoleAdmin = None, idRoleJoin = None):
        
        self.prefix = prefix if prefix else '.'
        self.idRoleMute = int(idRoleMute) if idRoleMute else None
        self.idRoleAdmin = int(idRoleAdmin) if idRoleAdmin else None
        self.idRoleJoin = int(idRoleJoin) if idRoleJoin else None
        self.idGuild = int(idGuild)
           
    def getAll(self, atrr = None):
        if not atrr:
            return list(self.__dict__.values())
        elif atrr == 'idRoleMute':
            return [self.idRoleMute, 'Mute']
        elif atrr == 'idRoleJoin':
            return [self.idRoleJoin, 'Ingreso']
        else:
            return [self.idRoleAdmin, 'Administrador']
        
    def setNone(self):
        for atrr in self.__dict__.keys():
            if atrr == 'idGuild': continue
            setattr(self, atrr, None)

class GuildInvites(GuildConfig):
    def __init__(self, idGuild, timeFake = None, msgRegularInvite = None, msgSelfInvite = None, msgUnknownInvite = None, msgVanityInvite = None, idChannelInvite = None):
        
        self.timeFake = timeFake if timeFake else 604800
        self.msgRegularInvite = msgRegularInvite if msgRegularInvite else config.messagesInvites.get('invitación regular')
        self.msgSelfInvite = msgSelfInvite if msgSelfInvite else config.messagesInvites.get('invitación a sí mismo')
        self.msgUnknownInvite = msgUnknownInvite if msgUnknownInvite else config.messagesInvites.get('invitación desconocida')
        self.msgVanityInvite = msgVanityInvite if msgVanityInvite else config.messagesInvites.get('invitación personalizada')
        self.idChannelInvite = int(idChannelInvite) if idChannelInvite else None
        self.idGuild = int(idGuild)
    
        
class GuildImages(GuildConfig):
    def __init__(self, idGuild, imageJoin = None, textJoin = None, idChannelJoin = None, colorJoin = None, imageLeave = None, textLeave = None, idChannelLeave = None, colorLeave = None, imageBoost = None, textBoost = None, idChannelBoost = None, colorBoost = None):
        self.imageJoin = imageJoin
        self.textJoin = textJoin
        self.idChannelJoin = int(idChannelJoin) if idChannelJoin else None
        self.colorJoin = colorJoin if colorJoin else 'FFFFFF'
        self.imageLeave = imageLeave
        self.textLeave = textLeave
        self.idChannelLeave = int(idChannelLeave) if idChannelLeave else None
        self.colorLeave = colorLeave if colorLeave else 'FFFFFF'
        self.imageBoost = imageBoost
        self.textBoost = textBoost
        self.idChannelBoost = int(idChannelBoost) if idChannelBoost else None
        self.colorBoost = colorBoost if colorBoost else 'FFFFFF'
        self.idGuild = int(idGuild)
        
    def getAll(self, generic = None):
        if not generic:
            return list(self.__dict__.values())
        elif generic == 'join':
            return [self.imageJoin, self.textJoin, self.idChannelJoin, self.colorJoin, 'bienvenida']
        elif generic == 'leave':
            return [self.imageLeave, self.textLeave, self.idChannelLeave, self.colorLeave, 'despedida'] 
        else: 
            return [self.imageBoost, self.textBoost, self.idChannelBoost, self.colorBoost, 'booster']
        
    def getImgText(self, generic):
        if generic == 'join':
           return [self.imageJoin, self.colorJoin, '¡Bienvenid@!'] 
        elif generic == 'leave':
            return [self.imageLeave, self.colorLeave, '¡Hasta Luego!']
        else:
            return [self.imageBoost, self.colorBoost, '¡Nuevo Booster!']
