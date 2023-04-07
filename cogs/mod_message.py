"""Provide app commands to post canned mod messages."""

import logging
import typing

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class ModMessage(commands.Cog):
    """Provide canned bot messages."""

    qualified_name = "Mod Message"

    def __init__(
        self,
        bot: commands.Bot,
        canned_messages: dict[str, str],
        debug: bool,
        exercism_guild_id: int,
    ) -> None:
        self.bot = bot
        self.canned_messages = canned_messages
        self.exercism_guild_id = exercism_guild_id
        if debug:
            logger.setLevel(logging.DEBUG)

    @app_commands.command(name="mod_message")  # type: ignore
    @commands.guild_only()
    @commands.has_role("moderators")
    @commands.bot_has_permissions(send_messages=True)
    async def mod_message(
        self,
        interaction: discord.Interaction,
        message: typing.Literal[
            "flagged", "criticize_language", "support", "forum",
        ],
        mention: typing.Optional[discord.Member],
    ) -> None:
        """App command to post a mod message via the bot."""
        channel = interaction.channel
        if not isinstance(channel, discord.abc.Messageable):
            logger.debug("Interaction is not in a messageable channel.")
            return

        member = interaction.user
        if not isinstance(member, discord.Member):
            logger.debug("Interaction user is not a guild member.")
            return

        guild = channel.guild
        if not isinstance(guild, discord.Guild):
            logger.debug("Interaction channel is not in a guild.")
            return

        if "moderators" not in {r.name for r in member.roles}:
            await interaction.response.send_message(
                "That command is only for moderators; sorry!",
                ephemeral=True,
            )
            logger.debug("Interaction member is not a moderator.")
            return

        if message not in self.canned_messages:
            await interaction.response.send_message(
                "That canned message was not found! This is a bug.",
                ephemeral=True
            )
            logger.warning("Message type %s not valid.", message)
            return

        permissions = channel.permissions_for(guild.me)
        if not permissions.send_messages:
            await interaction.response.send_message(
                "I do not have permissions to send messages in this channel.",
                ephemeral=True,
                delete_after=30,
            )
            logger.warning("No permission to post in %s (%d)", channel, channel.id)
            return

        await interaction.response.send_message(
            "Sending canned message.",
            ephemeral=True,
            delete_after=5,
        )
        content = self.canned_messages[message]
        if mention:
            content = f"{mention.mention} {content}"
        await channel.send(content)

    @commands.is_owner()
    # @commands.dm_only()
    @commands.command()
    async def sync_mod_message(self, ctx: commands.Context) -> None:
        """Sync app commands to the Guild."""
        _ = ctx
        logger.info("Syncing ModMessage.")
        await self.bot.tree.sync(guild=discord.Object(self.exercism_guild_id))
