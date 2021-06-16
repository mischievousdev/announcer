# -*- coding: utf-8 -*-

import traceback
import logging

logging.basicConfig(
    filename=None, format="[%(levelname)s] - %(message)s", level=logging.INFO
)
from datetime import datetime

import discord
import jishaku
from discord.ext import commands

from utils.cache import Cache
from utils.db import Connection, Blacklist
from utils.utlities import load_config


async def get_prefix(bot, message):
    record = bot.cache.get_setting(message.guild.id)
    return record.prefix


class Announcer(commands.Bot):
    """Announcer is the most simplistic bot when it comes to announcing! No complicated commands, no weird setup!"""

    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            description=self.__doc__,
            pm_help=None,
            help_attrs=dict(hidden=True),
            fetch_offline_members=False,
            heartbeat_timeout=150.0,
            allowed_mentions=discord.AllowedMentions(
                everyone=True, roles=True, users=True
            ),
            intents=discord.Intents.default(),
            chunk_guilds_at_startup=True,
            reconnect=True
        )

        # storing something
        self.log = logging.getLogger(__name__)
        self.started_at = datetime.utcnow()
        self.first_startup = True
        self.config = load_config()

        # Initializing internal cache
        self.cache = Cache()

        # Initializing postgres server connection
        self.pool = Connection()

        # Initializing blacklist class
        self.blacklist = Blacklist()

        # load extensions
        extensions = ["jishaku", "cogs.dev", "cogs.config", "cogs.restore", "cogs.help"]
        for ext in extensions:
            try:
                self.load_extension(ext)
                self.log.info(f"Extension loaded: {ext}")
            except Exception:
                self.log.critical(traceback.format_exc())

    # event handlers
    async def on_connect(self):
        self.log.info("Connected to discord websocket!")

    async def on_ready(self):
        if self.first_startup:
            # establishing postgres connection
            await self.pool.create_pool(
                self.config.dsn
            )
            self.log.info("Successfully established postgres connection")

            # Caching records
            self.cache.init(bot=self)
            await self.cache.cache_settings()
            await self.cache.cache_announcements()
            await self.cache.cache_timed_announcements()
            await self.cache.cache_raw_announcements()
            await self.cache.cache_timed_raw_announcements()
            await self.cache.cache_backup_timed_announcements()
            await self.cache.cache_timed_raw_announcement_backups()
            await self.cache.list_timed_announcements()
            await self.cache.list_timed_raw_announcements()
            self.log.info("Succesfully cached records")

            self.load_extension('cogs.announcement')
            self.log.info("Extension loaded: cogs.announcement")

            # Cache channels
            self.status_log_channel = await self.fetch_channel(849272565478326282)
            self.log.info("Successfully cached log channels")

            # cache blacklist data
            self.blacklist.cache()
            self.log.info("Successfully cached blacklist data")

            # update status message
            await self.status_log_channel.send(
                content=f":robot: | Connected to discord websocket(Average latency: `{round(self.latency * 1000)}ms`)"
            )
            self.log.info("Successfully sent status message")

            self.log.info(
                f"{str(self.user)} started - Average latency: {round(self.latency * 1000)}ms"
            )
        else:
            self.log.info(f"Restarted {str(self.user)}")

    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.guild:
            return
        await self.process_commands(message)

    async def on_message_edit(self, before, after):
        if before.content != after.content:
            await self.process_commands(after)

    async def on_guild_join(self, guild):
        if self.blacklist.is_blacklisted(guild_id=guild.id):
            await guild.leave()
            return
        await self.pool.execute("INSERT INTO settings(guild_id, allowed_roles) VALUES($1, $2)", guild.id, [])
        await self.cache.cache_settings()

    async def on_guild_remove(self, guild):
        # deleting data's since they removed the bot
        # announcement data would be still exists they won't be deleted
        await self.pool.execute("DELETE FROM settings WHERE guild_id = $1", guild.id)
        await self.cache.cache_settings()
