# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

from utils.utlities import generate_embed, check_allowed


class Backup(commands.Cog):
    """Backup commands used to backup announcements"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def restore(self, ctx):
        """Parent command, sends the list of subcommands!"""
        return await ctx.send_help(ctx.command)

    @restore.command()
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def quick(self, ctx, announcement_id: int):
        """Command that restores saved announcements"""
        allowed = await check_allowed(ctx)
        if (
            ctx.author == ctx.guild.owner
            or ctx.author.guild_permissions.administrator
            or allowed
        ):
            announcement = self.bot.cache.get_announcement(announcement_id)
            if not announcement:
                return await ctx.reply("Announcement not found!")
            embed = discord.Embed.from_dict(announcement.embed_details)
            channel = self.bot.get_channel(announcement.channel_id)
            await self.bot.pool.execute("DELETE FROM announcements WHERE announcement_id = $1", announcement_id)
            await self.bot.cache.cache_announcements()
            await channel.send(embed=embed)
            await ctx.reply(f":thumbsup: | Your announcment(#`{announcement_id}`) has been restored successfully!")

    @restore.command()
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def timed(self, ctx, announcement_id: int):
        """Command that restores saved timed announcements"""
        allowed = await check_allowed(ctx)
        if (
            ctx.author == ctx.guild.owner
            or ctx.author.guild_permissions.administrator
            or allowed
        ):
            announcement = self.bot.cache.get_timed_announcement(announcement_id)
            if not announcement:
                return await ctx.reply("Announcement not found!")
            content = announcement.content
            channel = self.bot.get_channel(announcement.channel_id)
            await self.bot.pool.execute("DELETE FROM timed_announcement_backups WHERE announcement_id = $1", announcement_id)
            await self.bot.cache.cache_backup_timed_announcements()
            await channel.send(content)
            await ctx.reply(f":thumbsup: | Your announcment(#`{announcement_id}`) has been restored successfully!")

    @restore.command()
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def timedRaw(self, ctx, announcement_id: int):
        """Command that restores saved raw announcements"""
        allowed = await check_allowed(ctx)
        if (
            ctx.author == ctx.guild.owner
            or ctx.author.guild_permissions.administrator
            or allowed
        ):
            announcement = self.bot.cache.get_timed_raw_announcement(announcement_id)
            if not announcement:
                return await ctx.reply("Announcement not found!")
            content = announcement.content
            channel = self.bot.get_channel(announcement.channel_id)
            await self.bot.pool.execute("DELETE FROM timed_raw_announcement_backups WHERE announcement_id = $1", announcement_id)
            await self.bot.cache.cache_timed_raw_announcement_backups()
            await channel.send(content)
            await ctx.reply(f":thumbsup: | Your announcment(#`{announcement_id}`) has been restored successfully!")

def setup(bot):
    bot.add_cog(Backup(bot))