class Member:
    def __init__(
        self, 
        idMember,
        numInvites,
        regularInvites,
        leaveInvites,
        bonusInvites,
        fakeInvites,
        idMemberInvite,
        joinLeave,
        idGuild
                 ):
        
        self.numInvites = numInvites
        self.regularInvites = regularInvites
        self.leaveInvites = leaveInvites
        self.bonusInvites = bonusInvites
        self.fakeInvites = fakeInvites
        self.idMemberInvite = int(idMemberInvite) if idMemberInvite else None
        self.joinLeave = joinLeave
        self.idMember = int(idMember)
        self.idGuild = int(idGuild)
        
    def __str__(self):
        return f'idMember: {self.idMember}, numInvites: {self.numInvites}, regularInvites: {self.regularInvites}, leaveInvites: {self.leaveInvites}, bonusInvites: {self.bonusInvites}, fakeInvites: {self.fakeInvites}, idMemberInvite: {self.idMemberInvite}, joinLeave: {self.joinLeave}, idGuild: {self.idGuild}'
    
    
    def getAll(self):
        return list(self.__dict__.values())
    
    def setterInv(
        self, 
        numInvites, 
        regularInvites, 
        leaveInvites, 
        fakeInvites
        ):
        
        self.numInvites += numInvites
        self.regularInvites += regularInvites
        self.leaveInvites += leaveInvites
        self.fakeInvites += fakeInvites
    
    def clearInv(self):
        self.numInvites = 0
        self.regularInvites = 0
        self.leaveInvites = 0
        self.fakeInvites = 0
        self.bonusInvites = 0
        
   
    
        
        
        