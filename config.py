cogs = [
    'cogs.events',
    'cogs.general',
    'cogs.invites',
    'cogs.error_handler',
    'cogs.configuration',
    'cogs.moderation',
    'cogs.utility',
]
URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

PREFIX = '.'
defaultColor, checkColor, errorColor= 0xF4E902, 0x4AE125, 0xDE2E2E
emojiError = '<a:cancel:881726350224932884>'
emojiCheck = '<a:check:881727269654126592>'
emojiCharging = '<a:charging:881729325005680679>'
charging = f'{emojiCharging} cargando...'

messagesInvites = {
    'invitación regular': "{member_mention} se ha unido. Invitado por {inviter}, ({inviter_invites}).",
    'invitación a sí mismo': '{member.mention} se invitó a si mismo.',
    'invitación desconocida' :'No pude saber quien invitó a {member.mention}. Seguramente una invitación temporal.',
    'invitación personalizada': '{member.mention} se unió usando una invitación personalizada.',
    'idChannelInvite': None,
    'timeFake': 604800
}


event_channel = 881435587503071272
permissions = {
    'add_reactions': 'añadirReacciones',
    'administrator': 'administrador',
    'attach_files': 'adjuntarArchivos',
    'ban_members': 'banearMiembros',
    'change_nickname': 'cambiarApodo',
    'connect': 'conectar',
    'create_instant_invite': 'crearInvitación',
    'deafen_members': 'ensordecerMiembros',
    'embed_links': 'insertarEnlaces',
    'external_emojis': 'usarEmojisExternos',
    'kick_members': 'expulsarMiembros',
    'manage_channels': 'gestionarCanales',
    'manage_emojis': 'gestionarEmojis',
    'manage_guild': 'gestionarServidor',
    'manage_messages': 'gestionarMensajes',
    'manage_nicknames': 'gestionarApodos',
    'manage_roles': 'gestionarRoles',
    'manage_permissions': 'gestionarPermisos',
    'manage_webhooks': 'gestionarWebhooks',
    'mention_everyone': 'mencionarEveryone',
    'move_members': 'moverMiembros',
    'mute_members': 'silenciarMiembros',
    'priority_speaker': 'prioridadDePalabra',
    'read_message_history': 'leerHistorialDeMensajes',
    'read_messages': 'leerMensajes',
    'request_to_speak': 'solicitarHablar',
    'send_messages': 'enviarMensajes',
    'send_tts_messages': 'enviarMensajesDeTextoAVoz',
    'speak': 'hablar',
    'stream': 'video',
    'use_external_emojis': 'usarEmojisExternos',
    'use_slash_commands': 'usarComandosBarraDiagonal',
    'use_voice_activation': 'usarActividadDeVoz',
    'view_audit_log': 'verRegistroDeAuditoria',
    'view_channel': 'verCanales',
    'view_guild_insights': 'verInformacionDelServidor',
    'rol_admin': 'rolAdministrador',
    'owner': 'Owner del servidor'
}

VARIABLES_INVITE = {
    'member': 'Nick completo del miembro invitado.',
    'member_name': 'Nombre del miembro invitado.',
    'member_mention': 'Menciona al miembro invitado.',
    'inviter': 'Nick completo del invitador.',
    'inviter_name': 'Nombre del invitador.',
    'inviter_mention': 'Menciona al invitador.',
    'inviter_invites': 'Número de invitaciones válidas del invitador.',
    'inviter_reg_invites': 'Número de invitaciones regulares del invitador.',
    'inviter_leave_invites': 'Número de invitaciones abandonadas del invitador.',
    'inviter_fake_invites': 'Número de invitaciones falsas del invitador.',
    'inviter_bonus_invites': 'Número de invitaciones bonus del invitador.',
}

VARIABLES_CONFIG = {
    'member': 'Nick completo del miembro.',
    'member_name': 'Nombre del miembro.',
    'member_mention': 'Menciona al miembro.',
    'server': 'Menciona el nombre del servidor.'
}