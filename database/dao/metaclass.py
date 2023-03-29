import datetime, discord, config
from database.cursor import Cursor

@classmethod
def embed(cls, ctx_or_channel):
    embed = discord.Embed(timestamp=datetime.datetime.now(),
                            description=':x: Ha ocurrido un error inesperado al conectarse a la base de datos. Ejecute el comando nuevamente.',
                            color=config.errorColor)\
            .set_footer(text=f'{ctx_or_channel.guild.me}', icon_url=ctx_or_channel.guild.me.avatar.url)
    return embed

@classmethod
async def insert(cls, data, ctx_or_channel=None):
    try:
        with Cursor() as cur:
            cur.execute(cls._INSERT, data) 
    except Exception as e:
        try: await ctx_or_channel.bot.close()
        except: pass
        if ctx_or_channel:
            embed = cls.embed(ctx_or_channel)
            await ctx_or_channel.send(embed=embed)
            
@classmethod
async def update(cls, data, ctx_or_channel=None):
    try:
        with Cursor() as cur:
            cur.executemany(cls._UPDATE, data) 
            rowsAffected = cur.rowcount
        return rowsAffected
    except Exception as e:
        try: await ctx_or_channel.bot.close()
        except: pass
        if ctx_or_channel:
            embed = cls.embed(ctx_or_channel)
            await ctx_or_channel.send(embed=embed)

class DAO(type):
    def __new__(cls, clsName, bases, attr):
        attr['embed'] = embed
        attr['insert'] = insert
        attr['update'] = update
        return type(clsName, bases, attr)