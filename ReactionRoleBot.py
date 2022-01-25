import discord
from discord.ext import commands
import json
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord import Embed
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType


class ReactionRoleBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open("roles.json", "r", encoding="utf-16") as fp:
            self.roles = json.load(fp)
        print(self.roles)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.member.bot:
            return

        role_ctx = self.get_ctx(payload.guild_id)
        if (add_role := role_ctx["role_add_message_id"] == payload.message_id) or \
                role_ctx[
                    "role_remove_message_id"] == payload.message_id:  # reacted to role add or remove message
            if str(payload.emoji) in role_ctx["roles"].keys():  # reacted a valid emoji
                role_emojis = role_ctx["roles"]
                role = discord.utils.get(payload.member.guild.roles, name=role_emojis[str(payload.emoji)])

                if role is not None:  # found according role

                    if add_role:
                        await payload.member.add_roles(role)
                    else:
                        await payload.member.remove_roles(role)
                    if channel := self.bot.get_channel(role_ctx["role_message_channel_id"]):  # found ctx channel
                        msg = await channel.fetch_message(payload.message_id)
                        await msg.remove_reaction(payload.emoji, payload.member)
                else:
                    print("Error: Role not found")

    @cog_ext.permission(865264006326779914,
                        create_permission(915369038811656203, SlashCommandPermissionType.ROLE, True))
    @cog_ext.permission(811342158858027018,
                        create_permission(811342455920263269, SlashCommandPermissionType.ROLE, True))
    @cog_ext.cog_slash(
        name="init_role_emoji_bot",
        description="Sends the role add and remove message."
    )
    async def init_role_emoji_bot(self, ctx: SlashContext):
        await ctx.send("Sending Role Bot Messages", delete_after=10)
        add_id = (await self.send_role_message(ctx)).id
        remove_id = (await self.send_role_message(ctx, remove=True)).id

        self.roles[str(ctx.guild_id)]["role_message_channel_id"] = ctx.channel_id
        self.roles[str(ctx.guild_id)]["role_add_message_id"] = add_id
        self.roles[str(ctx.guild_id)]["role_remove_message_id"] = remove_id

        self.save_roles()
        await self.react_all_roles(ctx)

    @cog_ext.permission(865264006326779914,
                        create_permission(915369038811656203, SlashCommandPermissionType.ROLE, True))
    @cog_ext.permission(811342158858027018,
                        create_permission(811342455920263269, SlashCommandPermissionType.ROLE, True))
    @cog_ext.cog_slash(
        name="add_role_emoji",
        description="Adds a new role-emoji association",
        options=[
            {
                "type": 3,
                "name": "emoji",
                "description": "emoji to associate the role with",
                "required": True
            },
            {
                "type": 8,
                "name": "role",
                "description": "role",
                "required": True
            }
        ]
    )
    async def add_role_emoji(self, ctx: SlashContext, emoji, role: discord.Role):
        self.roles[str(ctx.guild_id)]["roles"][emoji] = role.name
        self.save_roles()
        await ctx.send(f"Associated {emoji} with {role}")

    @cog_ext.permission(865264006326779914,
                        create_permission(915369038811656203, SlashCommandPermissionType.ROLE, True))
    @cog_ext.permission(811342158858027018,
                        create_permission(811342455920263269, SlashCommandPermissionType.ROLE, True))
    @cog_ext.cog_slash(
        name="remove_role_emoji",
        description="Removes a role-emoji association ",
        options=[
            {
                "type": 8,
                "name": "role",
                "description": "role to remove",
                "required": True
            }
        ]
    )
    async def remove_role_emoji(self, ctx: SlashContext, role: discord.Role):
        role = role.name
        if role in self.roles[str(ctx.guild_id)]:
            del self.roles[str(ctx.guild_id)]
            self.save_roles()
            await ctx.send(f"Removed {role}")
        else:
            await ctx.send("Couldn't find the role to remove")

    async def send_role_message(self, ctx: SlashContext, remove=False):
        role_ctx = self.get_ctx(ctx.guild_id)
        embed = Embed(
            type="rich",
            title="Role Bot",
            description=f"React with these emojis to {'remove' if remove else 'add'} these roles!",
            color=0xb477c1,
        )

        if not remove:
            for emoji, role_name in role_ctx["roles"].items():
                embed.add_field(name=emoji, value=role_name, inline=False)

        return await ctx.channel.send(embed=embed)

    async def react_all_roles(self, ctx: SlashContext):
        role_ctx = self.get_ctx(ctx.guild_id)

        channel: discord.TextChannel = self.bot.get_channel(role_ctx["role_message_channel_id"])
        add_msg: discord.Message = await channel.fetch_message(role_ctx["role_add_message_id"])
        rem_msg: discord.Message = await channel.fetch_message(role_ctx["role_remove_message_id"])

        for emoji in role_ctx["roles"]:
            await add_msg.add_reaction(emoji)
            await rem_msg.add_reaction(emoji)

    def get_ctx(self, guild_id: int):
        return self.roles[str(guild_id)]

    def save_roles(self):
        with open("roles.json", "w", encoding="utf-16") as fp:
            json.dump(self.roles, fp)


def setup(bot: commands.Bot):
    bot.add_cog(ReactionRoleBot(bot))
