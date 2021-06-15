# -*- coding: utf-8 -*-

from typing import Union

from .utlities import DottedDict


class Cache:
    """Asynchronous cache-manager for announcer bot"""

    def init(self, bot):
        """Initialize internal cache"""
        self.log = bot.log
        self.bot = bot
        self.pool = bot.pool
        self.settings = {}
        self.announcements = {}
        self.timed_announcements = {}
        self.all_timed_announcements = []
        self.backups = {}
        self.raw_announcements = {}
        self.timed_raw_announcements = {}
        self.all_raw_ta = []
        self.raw_backups = {}
        self.log.info("Initialised postgres connection and prepared internal cache")

    async def cache_settings(self):
        """Retreive all records from `settings` table and cache it"""
        records = await self.pool.fetch_all_settings()
        del self.settings
        self.settings = {}
        for record in records:
            self.settings[record.guild_id] = {
                "allowed_roles": record.allowed_roles,
                "prefix": record.prefix,
            }
        return self.settings

    async def cache_announcements(self):
        """Retreive all records from `announcements` table and cache it"""
        records = await self.pool.fetch_all_announcements()
        del self.announcements
        self.announcements = {}
        for record in records:
            self.announcements[record.announcement_id] = {
                "channel_id": record.channel_id,
                "embed_details": record.embed_details,
            }
        return self.announcements

    async def cache_timed_announcements(self):
        """Retreive all records from `timed_announcements` table and cache it"""
        records = await self.pool.fetch_all_timed_announcements()
        del self.timed_announcements
        self.timed_announcements = {}
        for record in records:
            self.timed_announcements[record.announcement_id] = {
                "channel_id": record.channel_id,
                "embed_details": record.embed_details,
                "expires": record.expires
            }
        return self.timed_announcements

    async def list_timed_announcements(self):
        """Retreive all records from `timed_announcements` table and cache it"""
        records = await self.pool.fetch_all_timed_announcements()
        self.all_timed_announcements = records

    async def cache_backup_timed_announcements(self):
        """Retreive all records from `timed_announcements` table and cache it"""
        records = await self.pool.fetch_all_backup_announcements()
        del self.backups
        self.backups = {}
        for record in records:
            self.backups[record.announcement_id] = {
                "channel_id": record.channel_id,
                "embed_details": record.embed_details,
                "expires": record.expires
            }
        return self.backups

    async def cache_timed_raw_announcements(self):
        """Retreive all records from `timed_raw_announcements` table and cache it"""
        records = await self.pool.fetch_all_timed_raw_announcements()
        del self.timed_raw_announcements
        self.timed_raw_announcements = {}
        for record in records:
            self.timed_raw_announcements[record.announcement_id] = {
                "channel_id": record.channel_id,
                "expires": record.expires,
                "content": record.content,
            }
        return self.timed_raw_announcements

    async def list_timed_raw_announcements(self):
        """Retreive all records from `timed_raw_announcements` table and cache it"""
        records = await self.pool.fetch_all_timed_raw_announcements()
        self.all_raw_ta = records

    async def cache_timed_raw_announcement_backups(self):
        """Retreive all records from `timed_raw_announcements` table and cache it"""
        records = await self.pool.fetch_all_backup_raw_announcements()
        del self.raw_backups
        self.raw_backups = {}
        for record in records:
            self.raw_backups[record.announcement_id] = {
                "channel_id": record.channel_id,
                "expires": record.expires,
                "content": record.content,
            }
        return self.raw_backups

    async def cache_raw_announcements(self):
        """Retreive all records from `raw_announcements` table and cache it"""
        records = await self.pool.fetch_all_raw_announcements()
        del self.raw_announcements
        self.raw_announcements = {}
        for record in records:
            self.raw_announcements[record.announcement_id] = {
                "channel_id": record.channel_id,
                "content": record.content,
            }
        return self.raw_announcements

    def get_setting(self, guild_id: int) -> Union[DottedDict, None]:
        """Retreive a `settings` record from internal cache if exists

        Parameters
        ----------
        guild_id: int
            The guild ID to lookup
        """
        try:
            return DottedDict(self.settings[guild_id])
        except KeyError:
            return None

    def get_announcement(self, announcement_id: int) -> Union[DottedDict, None]:
        """Retreive a `announcements` record from internal cache if exists

        Parameters
        ----------
        announcement_id: int
            The announcement ID to lookup
        """
        try:
            return DottedDict(self.announcements[announcement_id])
        except KeyError:
            return None

    def get_timed_announcement(self, announcement_id: int) -> Union[DottedDict, None]:
        """Retreive a `announcements` record from internal cache if exists

        Parameters
        ----------
        announcement_id: int
            The announcement ID to lookup
        """
        try:
            return DottedDict(self.backups[announcement_id])
        except KeyError:
            return None

    def get_raw_announcement(self, announcement_id: int) -> Union[DottedDict, None]:
        """Retreive a `raw_announcements` record from internal cache if exists

        Parameters
        ----------
        announcement_id: int
            The announcement ID to lookup
        """
        try:
            return DottedDict(self.raw_announcements[announcement_id])
        except KeyError:
            return None

    def get_timed_raw_announcement(self, announcement_id: int) -> Union[DottedDict, None]:
        """Retreive a `timed_raw_announcements` record from internal cache if exists

        Parameters
        ----------
        announcement_id: int
            The announcement ID to lookup
        """
        try:
            return DottedDict(self.raw_backups[announcement_id])
        except KeyError:
            return None

    def wipe(self):
        """Wipe all the internal cache"""
        del self.settings
        del self.announcements
        del self.raw_announcements
        del self.timed_announcements
        del self.all_raw_ta
        del self.all_timed_announcements
        del self.backups
        del self.raw_backups
