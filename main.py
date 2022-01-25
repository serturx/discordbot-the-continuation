import os

import discord
from discord.ext import commands
from discord_slash import SlashCommand
from dotenv import load_dotenv
import logging
import sys
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN_RESA")
TENOR_TOKEN = os.getenv("TENOR_TOKEN")

intents = discord.Intents.all()
bot_client = commands.Bot(intents=intents, command_prefix="!")
slash = SlashCommand(bot_client, sync_commands=True)
bot_client.load_extension("MusicBot")
bot_client.load_extension("ReactionRoleBot")
bot_client.load_extension("RandomStuffBot")


@bot_client.event
async def on_ready():
    print("Ready!")


@bot_client.event
async def on_message(message):
    pass


@bot_client.event
async def on_member_update(before, after):
    pass


@bot_client.event
async def on_voice_state_update(member, before, after):
    pass


bot_client.run(DISCORD_TOKEN)
