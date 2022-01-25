import discord
from discord.ext import commands
import json
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord import Embed


class RandomStuffBot(commands.Cog):
    @cog_ext.cog_slash(
        name="kopiernudel",
        description="Gets a random Kopiernudel"
    )
    async def kopiernudel(self, ctx: SlashContext):
        await ctx.send("not implemented yet :o")

    @cog_ext.cog_slash(
        name="muschel",
        description="Frag die magische Miesmuschel nach ihren Weisheiten"
    )
    async def muschel(self, ctx):
        await ctx.send("not implemented yet :o")


def setup(bot: commands.Bot):
    bot.add_cog(RandomStuffBot(bot))
