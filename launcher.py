from bot import Bot
from utils.tools import getPrefix
import asyncio
import json
import logging 
import sys
import discord
from os import system

system('cls')

if len(sys.argv) < 5:
    shard_ids = [0]
    shard_count = 1
    cluster_id = 1
    cluster_count = 1
else:
    shard_ids = json.loads(sys.argv[1])
    shard_count = int(sys.argv[2])
    cluster_id = int(sys.argv[3])
    cluster_count = int(sys.argv[4])

logging.basicConfig(level=logging.INFO, datefmt='%I:%M:%S %p')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename=f"discord-{cluster_id}.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s] %(message)s"))
logger.addHandler(handler)
log = logging.getLogger(__name__)
    

bot = Bot(
    intents=discord.Intents().all(),
    member_cache_flags=None,
    command_prefix=getPrefix,
    case_insensitive=True,
    help_command=None,
    heartbeat_timeout=300,
    shard_ids=shard_ids,
    shard_count=shard_count,
    cluster_id=cluster_id,
    cluster_count=cluster_count,
    version="2.1.1",
)

loop = asyncio.get_event_loop()
loop.run_until_complete(bot.start_bot())