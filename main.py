import datetime
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands
from discord_slash import SlashCommand, SlashContext
import os
import random
import asyncio
from Bot import Bot
from Tenor import Tenor

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN_DEV")
TENOR_TOKEN = os.getenv("TENOR_TOKEN")

intents = discord.Intents.all()
bot_client = commands.Bot(intents=intents, command_prefix="!")
slash = SlashCommand(bot_client, sync_commands=True)
bot_client.load_extension("MusicBot")

bot = Bot(bot_client, "Sertury", "Sertury")
tenor = Tenor(TENOR_TOKEN)


@bot_client.event
async def on_ready():
    print("Ready!")
    bot.init_settings(787968359521976323)


@bot_client.event
async def on_message(message):
    try:
        if message.channel.id == message.author.dm_channel.id:  # if dm
            if message.author.name == bot.forwarding_user:  # if user is me
                user = discord.utils.get(bot_client.get_all_members(), name=bot.target_user)
                print("sending: " + message.content)
                await user.send(message.content)
            else:
                with open("received.txt", "a") as f:
                    f.write(message.content)
                    f.write(f" - {message.author.name}, {datetime.datetime.now()}\n")

                print("Received: " + message.content)

                gif = "https://tenor.com/view/anime-pfp-gif-24100488"

                while gif == "https://tenor.com/view/anime-pfp-gif-24100488":
                    gif = tenor.get_random_gif_with_query("cute anime")

                await message.author.send(gif)
    except:
        pass


@bot_client.event
async def on_member_update(before, after):
    if before.name == bot.target_user:
        if before.status == discord.Status.offline and after.status == discord.Status.online:
            print("sending msg...")
            await after.send("Na du Trucker-Babe ;)")


@bot_client.event
async def on_voice_state_update(member, before, after):
    if member.name == bot.target_user:  # if target
        if before.channel is None and after.channel is not None:  # joined channel
            await bot.connect_to_voice_channel(after.channel)
        if before.channel is not None and after.channel is not None and before.channel != after.channel:  # switched channel
            await bot.switch_channel(after.channel)
        if before.channel is not None and after.channel is None:  # disconnected :(
            await bot.disconnect_voice_channel()


bot_client.run(DISCORD_TOKEN)
