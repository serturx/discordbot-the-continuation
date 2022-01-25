import time
from os import getenv
from typing import Optional

import discord
import discordSuperUtils
from discord import Embed
from discord.ext import commands
from discordSuperUtils import MusicManager
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.model import ButtonStyle, SlashMessage
from discord_slash.utils.manage_components import create_button, create_actionrow
from pygicord import Config, Paginator

from StatusMessages import StatusMessages


class MusicBot(commands.Cog, discordSuperUtils.CogManager.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.music_status_msg = None
        self.voice_channel = None
        self.music_manager = MusicManager(
            bot,
            spotify_support=True,
            client_id="4ac99ffe261d4f3596b2dfbe312393ce",
            client_secret=getenv("SPOTIFY_SECRET")
        )
        self.music_paused = False
        super().__init__()

    @staticmethod
    def __format_duration(duration: Optional[float]) -> str:
        return (
            time.strftime("%H:%M:%S", time.gmtime(duration))
            if duration != "LIVE"
            else duration
        )

    async def send_status_embed_with_interaction(self, ctx, player=None):
        if player is None:
            player = await self.music_manager.now_playing(ctx)
        song_embed = await self.build_status_embed(ctx, player)

        buttons = [
            create_button(style=ButtonStyle.primary, label="<<", custom_id="prev", ),
            create_button(style=ButtonStyle.primary, label="Play / Pause", custom_id="playpause"),
            create_button(style=ButtonStyle.primary, label=">>", custom_id="next"),

        ]

        buttons2 = [
            create_button(style=ButtonStyle.secondary, emoji="🔀", custom_id="shuffle"),
            create_button(style=ButtonStyle.secondary, label="Show Queue", custom_id="queue"),
            create_button(style=ButtonStyle.secondary, emoji="❌", custom_id="leave"),
        ]

        buttons3 = [
            create_button(style=ButtonStyle.secondary, emoji="🔁", custom_id="loop")
        ]

        song_components = create_actionrow(*buttons)
        song_components2 = create_actionrow(*buttons2)
        song_components3 = create_actionrow(*buttons3)

        self.music_status_msg = await ctx.send(embed=song_embed, components=[song_components, song_components2, song_components3])

    async def build_status_embed(self, ctx, player) -> discord.Embed:
        if queue := await self.music_manager.get_queue(ctx):
            loop = queue.loop
            shuffle = queue.shuffle

            return Embed(
                type="rich",
                title="Music Bot",
                description="",
                color=0xb477c1,
            ).add_field(
                name="Current Song",
                value=f"[{player}]({player.url})",
                inline=False,
            ).add_field(
                name="Duration",
                value=f"{self.__format_duration(await self.music_manager.get_player_played_duration(ctx, player))}/"
                      f"{self.__format_duration(player.duration)}",
                inline=False,
            ).add_field(
                name="\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_",
                value=f"\n{'**Loop: ** :white_check_mark:' if loop == discordSuperUtils.Loops.LOOP else ''}"
                      f"{'**Queue Loop: **:white_check_mark:' if loop == discordSuperUtils.Loops.QUEUE_LOOP else ''}"
                      f"\n**Shuffle**: {':white_check_mark:' if shuffle else ':x:'}",
                inline=False
            ).add_field(
                name="Requester:",
                value=player.requester and player.requester.mention
            )

    async def update_status_embed(self, ctx, player=None):
        msg: SlashMessage = self.music_status_msg
        if player is None:
            player = await self.music_manager.now_playing(ctx)

        await msg.edit(embed=await self.build_status_embed(ctx, player))

    async def resend_status_embed(self, ctx):
        # await self.music_status_msg.delete()
        self.music_status_msg = None
        await self.send_status_embed_with_interaction(ctx)

    @cog_ext.cog_slash(
        name="join",
        description="Joins the current channel"
    )
    async def join(self, ctx: SlashContext):
        await self.join_bot(ctx)
        await ctx.send(StatusMessages.Status.value.join_success.value)

    @cog_ext.cog_slash(
        name="play",
        description="Joins the current channel, and plays the given song",
        options=[{
            "type": 3,
            "name": "song",
            "description": "Name of the Song to play",
            "required": True
        }])
    async def play(self, ctx: SlashContext, song=""):
        await ctx.defer()

        if self.voice_channel is None:
            await self.join_bot(ctx)

        player = await self.music_manager.create_player(song, ctx.author)

        if not await self.music_manager.queue_add(
                players=player, ctx=ctx
        ):
            await ctx.send(StatusMessages.Errors.value.query_not_found.value)
        else:
            await self.music_manager.play(ctx)
            await ctx.send(embed=Embed(
                type="rich",
                title="Music Bot",
                description="",
                color=0xb477c1,
            ).add_field(
                name=StatusMessages.Status.value.added_to_queue.value,
                value=song,
                inline=False
            ).add_field(
                name="Requester:",
                value=ctx.author and ctx.author.mention,
                inline=False
            ))

            if self.music_status_msg is not None:
                await self.resend_status_embed(ctx)

    @cog_ext.cog_slash(
        name="skip",
        description="Skips the current song, or to the given index",
        options=[{
            "type": 4,
            "name": "index",
            "description": "Index to skip to"
        }]
    )
    async def skip(self, ctx, index: int = None):
        await self.skip_bot(ctx, index)

    @cog_ext.cog_slash(
        name="shuffle",
        description="Shuffles the queue"
    )
    async def shuffle(self, ctx):
        await self.shuffle_bot(ctx)

    @cog_ext.cog_slash(
        name="pause",
        description="Pauses the current song"
    )
    async def pause(self, ctx):
        await self.pause_bot(ctx)

    @cog_ext.cog_slash(
        name="leave",
        description="The bot leaves :("
    )
    async def leave(self, ctx: SlashContext):
        await self.leave_bot(ctx)

    @cog_ext.cog_slash(
        name="queue",
        description="Shows the music queue"
    )
    async def queue(self, ctx: SlashContext):
        await self.queue_bot(ctx)

    @cog_ext.cog_slash(
        name="history",
        description="Shows the played songs"
    )
    async def history(self, ctx: SlashContext):
        await self.history_bot(ctx)

    @cog_ext.cog_slash(
        name="clear",
        description="Clears the queue"
    )
    async def clear(self, ctx: SlashContext):
        await self.clear_bot(ctx)

    @cog_ext.cog_slash(
        name="loop",
        description="Loops the song"
    )
    async def loop(self, ctx: SlashContext):
        await self.loop_bot(ctx)

    @cog_ext.cog_component(components="playpause")
    async def playpause_interaction(self, ctx: ComponentContext):
        if self.music_paused:
            await self.play_bot(ctx)
        else:
            await self.pause_bot(ctx)

    @cog_ext.cog_component(components="next")
    async def next_interaction(self, ctx: ComponentContext):
        await self.skip_bot(ctx)

    @cog_ext.cog_component(components="prev")
    async def prev_interaction(self, ctx: ComponentContext):
        await self.prev_bot(ctx)

    @cog_ext.cog_component(components="leave")
    async def leave_interaction(self, ctx: ComponentContext):
        await self.leave_bot(ctx)

    @cog_ext.cog_component(components="shuffle")
    async def shuffle_interaction(self, ctx: ComponentContext):
        await self.shuffle_bot(ctx)

    @cog_ext.cog_component(components="queue")
    async def queue_interaction(self, ctx: ComponentContext):
        await self.queue_bot(ctx)

    @cog_ext.cog_component(components="loop")
    async def loop_interaction(self, ctx: ComponentContext):
        await self.loop_bot(ctx)

    @discordSuperUtils.CogManager.event(discordSuperUtils.MusicManager)
    async def on_music_error(self, ctx, error):
        errors = {
            discordSuperUtils.NotPlaying: StatusMessages.Errors.value.not_playing.value,
            discordSuperUtils.NotConnected: StatusMessages.Errors.value.not_connected_to_voice.value,
            discordSuperUtils.NotPaused: StatusMessages.Errors.value.not_paused.value,
            discordSuperUtils.QueueEmpty: StatusMessages.Errors.value.queue_empty.value,
            discordSuperUtils.AlreadyConnected: StatusMessages.Errors.value.already_connected.value,
            discordSuperUtils.RemoveIndexInvalid: StatusMessages.Errors.value.invalid_remove_index.value,
            discordSuperUtils.SkipError: StatusMessages.Errors.value.skip_error.value,
            discordSuperUtils.UserNotConnected: StatusMessages.Errors.value.user_not_connected_to_voice.value,
            discordSuperUtils.InvalidSkipIndex: StatusMessages.Errors.value.invalid_skip_index.value,
        }

        for error_type, response in errors.items():
            if isinstance(error, error_type):
                await ctx.send(response, delete_after=5)
                return

        print("unexpected error")
        raise error

    @discordSuperUtils.CogManager.event(discordSuperUtils.MusicManager)
    async def on_play(self, ctx, player):
        if self.music_status_msg is None:
            await self.send_status_embed_with_interaction(ctx, player)
        else:
            await self.update_status_embed(ctx, player)

    @discordSuperUtils.CogManager.event(discordSuperUtils.MusicManager)
    async def on_queue_end(self, ctx):
        await ctx.send(StatusMessages.Status.Errors.value.queue_empty.value)

    @discordSuperUtils.CogManager.event(discordSuperUtils.MusicManager)
    async def on_activity_disconnect(self, ctx):
        await self.leave_bot(ctx, True)

    async def join_bot(self, ctx):
        self.voice_channel = await self.music_manager.join(ctx)

    async def skip_bot(self, ctx, index: int = None):
        if not await self.is_in_channel(ctx):
            return

        if skipped_player := await self.music_manager.skip(ctx, index):
            await self.update_status_embed(ctx, skipped_player)
            await ctx.send("Skipped!", delete_after=5)

    async def prev_bot(self, ctx):
        if not await self.is_in_channel(ctx):
            return

        if await self.music_manager.previous(ctx):
            await ctx.send("Previous", delete_after=5)

    async def shuffle_bot(self, ctx):
        if not await self.is_in_channel(ctx):
            return

        if await self.music_manager.now_playing(ctx):
            shuffle = await self.music_manager.shuffle(ctx)
            await ctx.send(StatusMessages.Status.value.shuffle_enabled.value
                           if shuffle else StatusMessages.Status.value.shuffle_disabled.value, delete_after=5)
            await self.update_status_embed(ctx)

    async def queue_bot(self, ctx):
        if not await self.is_in_channel(ctx):
            return

        if queue := await self.music_manager.get_queue(ctx):
            formatted_queue = [f"**{s.title}**\nLänge: {self.__format_duration(s.duration)}" for s in queue.queue[1:]]

            embeds = discordSuperUtils.generate_embeds(
                formatted_queue,
                "Queue",
                f"Now Playing: {await self.music_manager.now_playing(ctx)}",
                10,
                string_format="{}"
            )

            page_manager = Paginator(pages=embeds, config=Config.PLAIN)
            await page_manager.start(ctx)
            await self.resend_status_embed(ctx)

    async def history_bot(self, ctx):
        if not await self.is_in_channel(ctx):
            return

        if queue := await self.music_manager.get_queue(ctx):
            formatted_history = [
                f"**{s.title}\nRequester: {s.requester and s.requester.mention}"
                for s in queue.history
            ]

            embeds = discordSuperUtils.generate_embeds(
                formatted_history,
                "History",
                f"Shows all played songs",
                10,
                string_format="{}"
            )

            page_manager = Paginator(pages=embeds, config=Config.PLAIN)
            await page_manager.start(ctx)

    async def pause_bot(self, ctx):
        if not await self.is_in_channel(ctx):
            return

        if await self.music_manager.pause(ctx):
            await ctx.send("Paused", delete_after=5)
            self.music_paused = True

    async def play_bot(self, ctx):
        if not await self.is_in_channel(ctx):
            return

        if await self.music_manager.resume(ctx):
            await ctx.send("Play", delete_after=5)
            self.music_paused = False

    async def leave_bot(self, ctx, inactivity=False):
        if not await self.is_in_channel(ctx):
            return

        if await self.music_manager.leave(ctx):

            msg: discord.Message = self.music_status_msg
            await msg.delete()

            self.voice_channel = None
            self.music_paused = False
            self.music_status_msg = None

            if inactivity:
                await ctx.send("Left because of inactivity :(")
            else:
                await ctx.send("Bye :cry:", delete_after=10)

    async def loop_bot(self, ctx):
        if not await self.is_in_channel(ctx):
            return

        if await self.music_manager.now_playing(ctx):
            loop = await self.music_manager.loop(ctx)
            await ctx.send(StatusMessages.Status.value.loop_enabled.value
                           if loop else StatusMessages.Status.value.loop_disabled.value, delete_after=5)
            await self.update_status_embed(ctx)

    async def is_in_channel(self, ctx):
        if ctx.author.voice.channel.id != self.voice_channel.id:
            await ctx.send("You're not in the same channel as the bot!")
            return False
        return True

    async def clear_bot(self, ctx):
        if not await self.is_in_channel(ctx):
            return

        queue = await self.music_manager.get_queue(ctx)
        queue.clear()
        await ctx.send(embed=Embed(
            type="rich",
            title="Music Bot",
            description="",
            color=0xb477c1,
        ).add_field(
            name="Cleared the queue!",
            value=ctx.author and ctx.author.mention,
            inline=False
        ))


def setup(bot: commands.Bot):
    bot.add_cog(MusicBot(bot))
