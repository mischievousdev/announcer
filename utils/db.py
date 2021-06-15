# -*- coding: utf-8 -*-

import json
from datetime import datetime
from typing import Union, List

import asyncpg
from discord import Embed


class SettingsRecord:
    """Represent a `setting` record"""

    def __init__(self, record: dict) -> None:
        self.record = record
        self.id: int = record["id"]
        self.guild_id: int = record["guild_id"]
        self.allowed_roles: Union[List[int], None] = (
            record["allowed_roles"] if record["allowed_roles"] else None
        )
        self.prefix: str = record["prefix"]

    def __repr__(self) -> str:
        return f"<SettingsRecord id={self.id} guild_id={self.guild_id} allowed_roles={self.allowed_roles} prefix={self.prefix}>"


class AnnouncementsRecord:
    """Represent a `announcements` record"""

    def __init__(self, record: dict) -> None:
        self.record = record
        self.id: int = record["id"]
        self.announcement_id: int = record["announcement_id"]
        self.channel_id: int = record["channel_id"]
        self.embed_details: dict = json.loads(record["embed_details"])

    def build_embed(self):
        return Embed.from_dict(self.embed_details)

    def __repr__(self) -> str:
        return f"<AnnouncementsRecord id={self.id} channel_id={self.channel_id} embed_details={self.embed_details}>"

class TimedAnnouncementRecord:
    """Represent a `timed_announcements` record"""

    def __init__(self, record: dict) -> None:
        self.record = record
        self.id: int = record["id"]
        self.announcement_id: int = record["announcement_id"]
        self.expires: datetime = record["expires"]
        self.channel_id: int = record["channel_id"]
        self.embed_details: dict = json.loads(record["embed_details"])

    def build_embed(self):
        return Embed.from_dict(self.embed_details)

    def __repr__(self) -> str:
        return f"<AnnouncementsRecord id={self.id} expires={self.expires} channel_id={self.channel_id} embed_details={self.embed_details}>"


class TimedRawAnnouncementRecord:
    """Represent a `timed_raw_announcements` record"""

    def __init__(self, record: dict) -> None:
        self.record = record
        self.id: int = record["id"]
        self.announcement_id: int = record["announcement_id"]
        self.expires: datetime = record["expires"]
        self.channel_id: int = record["channel_id"]
        self.content: str = record["content"]

    def __repr__(self) -> str:
        return f"<RawAnnouncementRecord id={self.id} expires={self.expires} channel_id={self.channel_id}>"

class RawAnnouncementRecord:
    """Represent a `raw_announcements` record"""

    def __init__(self, record: dict) -> None:
        self.record = record
        self.id: int = record["id"]
        self.announcement_id: int = record["announcement_id"]
        self.channel_id: int = record["channel_id"]
        self.content: str = record["content"]

    def __repr__(self) -> str:
        return f"<RawAnnouncementRecord id={self.id} channel_id={self.channel_id}>"


class NotConnected(Exception):
    def __init__(self, message=None, *args: object) -> None:
        self.message = message
        self.args = args

    def __str__(self) -> str:
        return self.message


class Connection:
    """Represents the connection to postgres"""

    async def create_pool(self, uri):
        """Establish connection to the postgres with given uri"""
        pool = await asyncpg.create_pool(uri)
        self.pool = pool
        return pool

    async def close(self):
        """Close the connection to the postgres server only if the connection is made"""
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        await self.pool.close()

    async def fetch_setting(self, guild_id: int):
        """Fetch a record on `setting` column by given `guild_id`

        Parameters
        ----------
        guild_id: int
            The guild id to lookup
        """
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        query = """SELECT * FROM settings WHERE guild_id = $1"""
        record = await self.pool.fetchrow(query, guild_id)
        return SettingsRecord(record=record)

    async def fetch_announcement(self, announcement_id: int):
        """Fetch a record on `announcements` column by given `announcement_id`

        Parameters
        ----------
        announcement_id: int
            The announcement id to lookup
        """
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        query = """SELECT * FROM announcements WHERE announcement_id = $1"""
        record = await self.pool.fetchrow(query, announcement_id)
        if not record:
            return None
        return AnnouncementsRecord(record=record)

    async def fetch_timed_announcement(self, announcement_id: int):
        """Fetch a record on `timed_announcements` column by given `announcement_id`

        Parameters
        ----------
        announcement_id: int
            The announcement id to lookup
        """
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        query = """SELECT * FROM timed_announcement_backups WHERE announcement_id = $1"""
        record = await self.pool.fetchrow(query, announcement_id)
        if not record:
            return None
        return AnnouncementsRecord(record=record)

    async def fetch_raw_announcement(self, announcement_id: int):
        """Fetch a record on `raw_announcements` column by given `announcement_id`

        Parameters
        ----------
        announcement_id: int
            The announcement id to lookup
        """
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        query = """SELECT * FROM raw_announcements WHERE announcement_id = $1"""
        record = await self.pool.fetchrow(query, announcement_id)
        if not record:
            return None
        return RawAnnouncementRecord(record=record)
    
    async def fetch_timed_raw_announcement(self, announcement_id: int):
        """Fetch a record on `timed_raw_announcements` column by given `announcement_id`

        Parameters
        ----------
        announcement_id: int
            The announcement id to lookup
        """
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        query = """SELECT * FROM timed_raw_announcements WHERE announcement_id = $1"""
        record = await self.pool.fetchrow(query, announcement_id)
        if not record:
            return None
        return TimedRawAnnouncementRecord(record=record)

    async def fetch_all_settings(self) -> List[SettingsRecord]:
        """Fetch all record in `settings` table"""
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        query = """SELECT * FROM settings;"""
        records = []
        datas = await self.pool.fetch(query=query)
        for data in datas:
            records.append(SettingsRecord(record=data))
        return records

    async def fetch_all_announcements(self) -> List[AnnouncementsRecord]:
        """Fetch all record in `announcements` table"""
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        query = """SELECT * FROM announcements;"""
        records = []
        datas = await self.pool.fetch(query=query)
        for data in datas:
            records.append(AnnouncementsRecord(record=data))
        return records

    async def fetch_all_timed_announcements(self) -> List[TimedAnnouncementRecord]:
        """Fetch all record in `timed_announcements` table"""
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        query = """SELECT * FROM timed_announcements;"""
        records = []
        datas = await self.pool.fetch(query=query)
        for data in datas:
            records.append(TimedAnnouncementRecord(record=data))
        return records

    async def fetch_all_backup_announcements(self) -> List[TimedAnnouncementRecord]:
        """Fetch all record in `timed_announcement_backups` table"""
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        query = """SELECT * FROM timed_announcement_backups;"""
        records = []
        datas = await self.pool.fetch(query=query)
        for data in datas:
            records.append(TimedAnnouncementRecord(record=data))
        return records

    async def fetch_all_raw_announcements(self) -> List[RawAnnouncementRecord]:
        """Fetch all record in `raw_announcements` table"""
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        query = """SELECT * FROM raw_announcements;"""
        records = []
        datas = await self.pool.fetch(query=query)
        for data in datas:
            records.append(RawAnnouncementRecord(record=data))
        return records

    async def fetch_all_timed_raw_announcements(self) -> List[TimedRawAnnouncementRecord]:
        """Fetch all record in `timed_raw_announcements` table"""
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        query = """SELECT * FROM timed_raw_announcements;"""
        records = []
        datas = await self.pool.fetch(query=query)
        for data in datas:
            records.append(TimedRawAnnouncementRecord(record=data))
        return records

    async def fetch_all_backup_raw_announcements(self) -> List[TimedRawAnnouncementRecord]:
        """Fetch all record in `timed_announcement_backups` table"""
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        query = """SELECT * FROM timed_raw_announcement_backups;"""
        records = []
        datas = await self.pool.fetch(query=query)
        for data in datas:
            records.append(TimedRawAnnouncementRecord(record=data))
        return records

    async def execute(self, query, *args):
        """Execute SQL Query"""
        if not hasattr(self, "pool"):
            raise NotConnected(
                "connection to postgres server haven't established yet, call `Pool.create_pool` method first"
            )
        await self.pool.execute(query, *args)


class Blacklist:
    """Handle blacklisting guild"""

    def add(self, guild_id: int):
        """Add the given guild id to the blacklist

        Parameters
        ----------
        guild_id: int
            the guild id which is going to blacklisted
        """
        with open("data/blacklist.json", "r") as f:
            data = json.load(f)

        data["list"].append(guild_id)

        with open("data/blacklist.json", "w") as f:
            json.dump(data, f, indent=4)

        # updating cache
        self.cache()

    def remove(self, guild_id: int):
        """Remove the given guild id to the blacklist

        Parameters
        ----------
        guild_id: int
            the guild id which is going to removed from blacklisted lists
        """
        with open("data/blacklist.json", "r") as f:
            data = json.load(f)

        data["list"].remove(guild_id)

        with open("data/blacklist.json", "w") as f:
            json.dump(data, f, indent=4)

        # updating cache
        self.cache()

    def is_blacklisted(self, guild_id: int, cache=True):
        """Check if the given guild_id is blacklisted

        Parameters
        ----------
        guild_id: int
            The guild ID to check whether it's blacklisted or not

        cache: bool
            Whether to lookup in internal cache
        """
        if cache:
            if not hasattr(self, "_cache"):
                self.cache()
                return guild_id in self._cache
            return guild_id in self._cache

        with open("data/blacklist.json", "r") as f:
            data = json.load(f)

        return guild_id in data["list"]

    def cache(self):
        """Cache the blacklist data"""
        with open("data/blacklist.json", "r") as f:
            data = json.load(f)

        self._cache = data["list"]
