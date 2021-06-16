# -*- coding: utf-8 -*-

import re
import asyncio
from datetime import datetime

import discord
import pytz
from discord.ext import commands, tasks

from utils.utlities import generate_embed, check_allowed, generate_id
from utils.time import parse

class Announcement(commands.Cog):
    """Announcement commands with which you can make announcements!"""

    def __init__(self, bot):
        self.bot = bot
        self.timed_announcements.start()
        self.raw_timed_announcements.start()
        self.bot.log.info("Timed announcements tasks started")

    @tasks.loop(seconds=1)
    async def timed_announcements(self):
        announcements = self.bot.cache.all_timed_announcements
        utc = pytz.UTC
        now = datetime.utcnow().replace(tzinfo=utc)
        if len(announcements) == 0:
            return
        for data in announcements:
            if now >= data.expires.replace(tzinfo=utc):
                channel = self.bot.get_channel(data.channel_id)
                embed = discord.Embed.from_dict(data.embed_details)
                await self.bot.pool.execute("DELETE FROM timed_announcements WHERE announcement_id = $1", data.announcement_id)
                await self.bot.cache.cache_timed_announcements()
                await self.bot.cache.list_timed_announcements()
                return await channel.send(embed=embed)
        
    @tasks.loop(seconds=1)
    async def raw_timed_announcements(self):
        announcements = self.bot.cache.all_raw_ta
        utc = pytz.UTC
        now = datetime.utcnow().replace(tzinfo=utc)
        if len(announcements) == 0:
            return
        for data in announcements:
            if now >= data.expires.replace(tzinfo=utc):
                channel = self.bot.get_channel(data.channel_id)
                await self.bot.pool.execute("DELETE FROM timed_raw_announcements WHERE announcement_id = $1", data.announcement_id)
                await self.bot.cache.cache_timed_raw_announcements()
                await self.bot.cache.list_timed_raw_announcements()
                return await channel.send(data.content)

    @commands.group(invoke_without_command=True, aliases=["a"])
    async def announcement(self, ctx):
        """Base group command for announcement category! Sends all sub-commands it has and those who have administrator permissions and those who have role which is in allowed role list can only make announcement!"""
        return await ctx.send_help(ctx.command)

    @announcement.command()
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def quick(self, ctx, channel: discord.TextChannel):
        """Interactively creates an embed to suit your needs"""
        allowed = await check_allowed(ctx)
        if (
            ctx.author == ctx.guild.owner
            or ctx.author.guild_permissions.administrator
            or allowed
        ):

            # i'm lazy to make these checks, so used from officialpiyush/modmail-plugins/announcement
            def check(msg: discord.Message):
                return ctx.author == msg.author and ctx.channel == msg.channel

            def field_check(msg: discord.Message):
                return (
                    ctx.author == msg.author
                    and ctx.channel == msg.channel
                    and (len(msg.content) < 256)
                )

            def description_check(msg: discord.Message):
                return (
                    ctx.author == msg.author
                    and ctx.channel == msg.channel
                    and (len(msg.content) < 2048)
                )

            def footer_check(msg: discord.Message):
                return (
                    ctx.author == msg.author
                    and ctx.channel == msg.channel
                    and (len(msg.content) < 2048)
                )

            def cancel_check(msg: discord.Message):
                if msg.content == "cancel" or msg.content == f"{ctx.prefix}cancel":
                    return True
                else:
                    return False

            embed = discord.Embed()
            title_msg = await ctx.send(
                embed=generate_embed("Would the announcement embed have title? [y/n]")
            )
            try:
                title = await self.bot.wait_for("message", check=check, timeout=60.0)
                if cancel_check(title):
                    await title_msg.delete()
                    return await ctx.send("Cancelled!")
                elif not title.content.strip().lower() in ["y", "n"]:
                    await title_msg.delete()
                    await ctx.send("Invalid option, starting the command again..")
                    await asyncio.sleep(1)
                    return await ctx.invoke(ctx.command, channel)
                elif title.content.strip().lower() == "y":
                    await title_msg.delete()
                    msg = await ctx.send(
                        embed=generate_embed(
                            "What would be the title of the embed?(Should be within 256 characters)"
                        )
                    )
                    try:
                        answer = await self.bot.wait_for(
                            "message", check=field_check, timeout=60.0
                        )
                        if cancel_check(answer):
                            await msg.delete()
                            return await ctx.send("Cancelled!")
                        await msg.delete()
                        embed.title = answer.content
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return await ctx.send("Cancelled the session as it's inactive!")
                elif title.content.strip().lower() == "n":
                    await title_msg.delete()
            except asyncio.TimeoutError:
                await title_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            desc_msg = await ctx.send(
                embed=generate_embed(
                    "Would the announcement embed have description? [y/n]"
                )
            )
            try:
                desc = await self.bot.wait_for("message", check=check, timeout=60.0)
                if cancel_check(desc):
                    await desc_msg.delete()
                    return await ctx.send("Cancelled!")
                elif not desc.content.strip().lower() in ["y", "n"]:
                    await desc_msg.delete()
                    await ctx.send("Invalid option, starting the command again..")
                    await asyncio.sleep(1)
                    return await ctx.invoke(ctx.command, channel)
                elif desc.content.strip().lower() == "y":
                    await desc_msg.delete()
                    msg = await ctx.send(
                        embed=generate_embed(
                            "What would be the descirption of the embed?(Should be within 2048 characters)"
                        )
                    )
                    try:
                        answer = await self.bot.wait_for(
                            "message", check=description_check, timeout=60.0
                        )
                        if cancel_check(answer):
                            await msg.delete()
                            return await ctx.send("Cancelled!")
                        await msg.delete()
                        embed.description = answer.content
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return await ctx.send("Cancelled the session as it's inactive!")
                elif desc.content.strip().lower() == "n":
                    await desc_msg.delete()
            except asyncio.TimeoutError:
                await desc_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            thumb_msg = await ctx.send(
                embed=generate_embed(
                    "Would the announcement embed have thumbnail? [y/n]"
                )
            )
            try:
                thumbnail = await self.bot.wait_for(
                    "message", check=check, timeout=60.0
                )
                if cancel_check(thumbnail):
                    return await ctx.send("Cancelled!")
                elif not thumbnail.content.strip().lower() in ["y", "n"]:
                    await thumb_msg.delete()
                    await ctx.send("Invalid option, starting the command again..")
                    await asyncio.sleep(1)
                    return await ctx.invoke(ctx.command, channel)
                elif thumbnail.content.strip().lower() == "y":
                    await thumb_msg.delete()
                    msg = await ctx.send(
                        embed=generate_embed(
                            "What would the thumbnail of the embed?(Please send a valid URL)"
                        )
                    )
                    try:
                        answer = await self.bot.wait_for(
                            "message", check=check, timeout=60.0
                        )
                        if cancel_check(answer):
                            await msg.delete()
                            return await ctx.send("Cancelled!")

                        match = re.match(
                            r"(?i)(https?:\/\/.*\.(?:png|jpg|gif|jpeg|JPG|JPEG|PNG|gif|gifv|webm))",
                            answer.content,
                        )
                        if match:
                            await msg.delete()
                            embed.set_thumbnail(url=answer.content)
                        else:
                            await msg.delete()
                            await ctx.send("Invalid URL, starting the command again..")
                            await asyncio.sleep(1)
                            return await ctx.invoke(ctx.command, channel)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return await ctx.send("Cancelled the session as it's inactive!")
                elif thumbnail.content.strip().lower() == "n":
                    await thumb_msg.delete()
            except asyncio.TimeoutError:
                await thumb_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            img_msg = await ctx.send(
                embed=generate_embed("Would the announcement embed have image? [y/n]")
            )
            try:
                image = await self.bot.wait_for("message", check=check, timeout=60.0)
                if cancel_check(image):
                    await img_msg.delete()
                    return await ctx.send("Cancelled!")
                elif not image.content.strip().lower() in ["y", "n"]:
                    await img_msg.delete()
                    await ctx.send("Invalid option, starting the command again..")
                    await asyncio.sleep(1)
                    return await ctx.invoke(ctx.command, channel)
                elif image.content.lower() == "y":
                    await img_msg.delete()
                    msg = await ctx.send(
                        embed=generate_embed(
                            "What would be the URL of the image?(Should be a valid URL)"
                        )
                    )
                    try:
                        answer = await self.bot.wait_for(
                            "message", check=check, timeout=60.0
                        )
                        if cancel_check(answer):
                            await msg.delete()
                            return await ctx.send("Cancelled!")
                        match = re.match(
                            r"(?i)(https?:\/\/.*\.(?:png|jpg|gif|jpeg|JPG|JPEG|PNG|gif|gifv|webm))",
                            answer.content,
                        )
                        if match:
                            await msg.delete()
                            embed.set_image(url=answer.content)
                        else:
                            await msg.delete()
                            await ctx.send("Invalid URL, starting the command again..")
                            await asyncio.sleep(1)
                            return await ctx.invoke(ctx.command, channel)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return await ctx.send("Cancelled the session as it's inactive!")
                elif image.content.strip().lower() == "n":
                    await img_msg.delete()
            except asyncio.TimeoutError:
                await img_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            color_msg = await ctx.send(
                embed=generate_embed("Would the embed have color? [y/n]")
            )
            try:
                color = await self.bot.wait_for("message", check=check, timeout=60.0)
                if cancel_check(color):
                    await color_msg.delete()
                    return await ctx.send("Cancelled!")
                elif not color.content.strip().lower() in ["y", "n"]:
                    await color_msg.delete()
                    await ctx.send("Invalid option, starting the command again..")
                    await asyncio.sleep(1)
                    return await ctx.invoke(ctx.command, channel)
                elif color.content.strip().lower() == "y":
                    await color_msg.delete()
                    msg = await ctx.send(
                        embed=generate_embed(
                            "What would be the embed color?(Should be a valid hex color)"
                        )
                    )
                    try:
                        answer = await self.bot.wait_for(
                            "message", check=check, timeout=60.0
                        )
                        if cancel_check(answer):
                            await msg.delete()
                            return await ctx.send("Cancelled!")
                        match = re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", answer.content)
                        if match:
                            color = answer.content.replace("#", "0x")
                            embed.color = int(color, 16)
                            await msg.delete()
                        else:
                            await msg.delete()
                            await ctx.send(
                                "Invalid Hex string, starting the command again.."
                            )
                            await asyncio.sleep(1)
                            return await ctx.invoke(ctx.command, channel)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return await ctx.send("Cancelled the session as it's inactive!")
                elif color.content.strip().lower() == "n":
                    await color_msg.delete()
            except asyncio.TimeoutError:
                await color_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            footer_msg = await ctx.send(embed=generate_embed('Would the announcement embed have footer? [y/n]'))
            try:
                footer = await self.bot.wait_for('message', check=check, timeout=60.0)
                if cancel_check(footer):
                    return await ctx.send('Cancelled!')
                elif not footer.content.strip().lower() in ["y", "n"]:
                    await footer_msg.delete()
                    await ctx.send("Invalid option, starting the command again..")
                    await asyncio.sleep(1)
                    return await ctx.invoke(ctx.command, channel)
                elif footer.content.strip().lower() == 'y':
                    await footer_msg.delete()
                    msg = await ctx.send(embed=generate_embed('What would be the footer text?(Must be within 2048 characters)'))
                    try:
                        answer = await self.bot.wait_for("message", check=footer_check, timeout=60.0)
                        if cancel_check(answer):
                            return await ctx.send("Cancelled!")
                        embed.set_footer(text=answer.content)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return await ctx.send("Cancelled the session as it's inactive!")
                elif footer.content.strip().lower() == 'n':
                    await footer_msg.delete()
            except asyncio.TimeoutError:
                await footer_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            announcement_id = generate_id()
            embed_details = f'{embed.to_dict()}'.replace("'", '"')
            await self.bot.pool.execute("INSERT INTO announcements(announcement_id, channel_id, embed_details) VALUES($1, $2, $3);", announcement_id, channel.id, embed_details)
            await self.bot.cache.cache_announcements()
            await ctx.reply(f":thumbsup: | Your announcement has been successfully posted! If you would like to restore this announcement, please use the following command `{ctx.prefix}restore quick {announcement_id}`.")
            return await channel.send(embed=embed)
        else:
            return await ctx.send("You don't have permissions to use this command!")

    @announcement.command()
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def timed(self, ctx, channel: discord.TextChannel):
        """Interactively created a timed announcement to suit your needs!"""
        allowed = await check_allowed(ctx)
        if (
            ctx.author == ctx.guild.owner
            or ctx.author.guild_permissions.administrator
            or allowed
        ):

            # i'm lazy to make these checks, so used from officialpiyush/modmail-plugins/announcement
            def check(msg: discord.Message):
                return ctx.author == msg.author and ctx.channel == msg.channel

            def field_check(msg: discord.Message):
                return (
                    ctx.author == msg.author
                    and ctx.channel == msg.channel
                    and (len(msg.content) < 256)
                )

            def description_check(msg: discord.Message):
                return (
                    ctx.author == msg.author
                    and ctx.channel == msg.channel
                    and (len(msg.content) < 2048)
                )

            def footer_check(msg: discord.Message):
                return (
                    ctx.author == msg.author
                    and ctx.channel == msg.channel
                    and (len(msg.content) < 2048)
                )

            def cancel_check(msg: discord.Message):
                if msg.content == "cancel" or msg.content == f"{ctx.prefix}cancel":
                    return True
                else:
                    return False

            embed = discord.Embed()
            title_msg = await ctx.send(
                embed=generate_embed("Would the announcement embed have title? [y/n]")
            )
            try:
                title = await self.bot.wait_for("message", check=check, timeout=60.0)
                if cancel_check(title):
                    await title_msg.delete()
                    return await ctx.send("Cancelled!")
                elif not title.content.strip().lower() in ["y", "n"]:
                    await title_msg.delete()
                    await ctx.send("Invalid option, starting the command again..")
                    await asyncio.sleep(1)
                    return await ctx.invoke(ctx.command, channel)
                elif title.content.strip().lower() == "y":
                    await title_msg.delete()
                    msg = await ctx.send(
                        embed=generate_embed(
                            "What would be the title of the embed?(Should be within 256 characters)"
                        )
                    )
                    try:
                        answer = await self.bot.wait_for(
                            "message", check=field_check, timeout=60.0
                        )
                        if cancel_check(answer):
                            await msg.delete()
                            return await ctx.send("Cancelled!")
                        await msg.delete()
                        embed.title = answer.content
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return await ctx.send("Cancelled the session as it's inactive!")
                elif title.content.strip().lower() == "n":
                    await title_msg.delete()
            except asyncio.TimeoutError:
                await title_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            desc_msg = await ctx.send(
                embed=generate_embed(
                    "Would the announcement embed have description? [y/n]"
                )
            )
            try:
                desc = await self.bot.wait_for("message", check=check, timeout=60.0)
                if cancel_check(desc):
                    await desc_msg.delete()
                    return await ctx.send("Cancelled!")
                elif not desc.content.strip().lower() in ["y", "n"]:
                    await desc_msg.delete()
                    await ctx.send("Invalid option, starting the command again..")
                    await asyncio.sleep(1)
                    return await ctx.invoke(ctx.command, channel)
                elif desc.content.strip().lower() == "y":
                    await desc_msg.delete()
                    msg = await ctx.send(
                        embed=generate_embed(
                            "What would be the descirption of the embed?(Should be within 2048 characters)"
                        )
                    )
                    try:
                        answer = await self.bot.wait_for(
                            "message", check=description_check, timeout=60.0
                        )
                        if cancel_check(answer):
                            await msg.delete()
                            return await ctx.send("Cancelled!")
                        await msg.delete()
                        embed.description = answer.content
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return await ctx.send("Cancelled the session as it's inactive!")
                elif desc.content.strip().lower() == "n":
                    await desc_msg.delete()
            except asyncio.TimeoutError:
                await desc_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            thumb_msg = await ctx.send(
                embed=generate_embed(
                    "Would the announcement embed have thumbnail? [y/n]"
                )
            )
            try:
                thumbnail = await self.bot.wait_for(
                    "message", check=check, timeout=60.0
                )
                if cancel_check(thumbnail):
                    return await ctx.send("Cancelled!")
                elif not thumbnail.content.strip().lower() in ["y", "n"]:
                    await thumb_msg.delete()
                    await ctx.send("Invalid option, starting the command again..")
                    await asyncio.sleep(1)
                    return await ctx.invoke(ctx.command, channel)
                elif thumbnail.content.strip().lower() == "y":
                    await thumb_msg.delete()
                    msg = await ctx.send(
                        embed=generate_embed(
                            "What would the thumbnail of the embed?(Please send a valid URL)"
                        )
                    )
                    try:
                        answer = await self.bot.wait_for(
                            "message", check=check, timeout=60.0
                        )
                        if cancel_check(answer):
                            await msg.delete()
                            return await ctx.send("Cancelled!")

                        match = re.match(
                            r"(?i)(https?:\/\/.*\.(?:png|jpg|gif|jpeg|JPG|JPEG|PNG|gif|gifv|webm))",
                            answer.content,
                        )
                        if match:
                            await msg.delete()
                            embed.set_thumbnail(url=answer.content)
                        else:
                            await msg.delete()
                            await ctx.send("Invalid URL, starting the command again..")
                            await asyncio.sleep(1)
                            return await ctx.invoke(ctx.command, channel)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return await ctx.send("Cancelled the session as it's inactive!")
                elif thumbnail.content.strip().lower() == "n":
                    await thumb_msg.delete()
            except asyncio.TimeoutError:
                await thumb_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            img_msg = await ctx.send(
                embed=generate_embed("Would the announcement embed have image? [y/n]")
            )
            try:
                image = await self.bot.wait_for("message", check=check, timeout=60.0)
                if cancel_check(image):
                    await img_msg.delete()
                    return await ctx.send("Cancelled!")
                elif not image.content.strip().lower() in ["y", "n"]:
                    await img_msg.delete()
                    await ctx.send("Invalid option, starting the command again..")
                    await asyncio.sleep(1)
                    return await ctx.invoke(ctx.command, channel)
                elif image.content.lower() == "y":
                    await img_msg.delete()
                    msg = await ctx.send(
                        embed=generate_embed(
                            "What would be the URL of the image?(Should be a valid URL)"
                        )
                    )
                    try:
                        answer = await self.bot.wait_for(
                            "message", check=check, timeout=60.0
                        )
                        if cancel_check(answer):
                            await msg.delete()
                            return await ctx.send("Cancelled!")
                        match = re.match(
                            r"(?i)(https?:\/\/.*\.(?:png|jpg|gif|jpeg|JPG|JPEG|PNG|gif|gifv|webm))",
                            answer.content,
                        )
                        if match:
                            await msg.delete()
                            embed.set_image(url=answer.content)
                        else:
                            await msg.delete()
                            await ctx.send("Invalid URL, starting the command again..")
                            await asyncio.sleep(1)
                            return await ctx.invoke(ctx.command, channel)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return await ctx.send("Cancelled the session as it's inactive!")
                elif image.content.strip().lower() == "n":
                    await img_msg.delete()
            except asyncio.TimeoutError:
                await img_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            color_msg = await ctx.send(
                embed=generate_embed("Would the embed have color? [y/n]")
            )
            try:
                color = await self.bot.wait_for("message", check=check, timeout=60.0)
                if cancel_check(color):
                    await color_msg.delete()
                    return await ctx.send("Cancelled!")
                elif not color.content.strip().lower() in ["y", "n"]:
                    await color_msg.delete()
                    await ctx.send("Invalid option, starting the command again..")
                    await asyncio.sleep(1)
                    return await ctx.invoke(ctx.command, channel)
                elif color.content.strip().lower() == "y":
                    await color_msg.delete()
                    msg = await ctx.send(
                        embed=generate_embed(
                            "What would be the embed color?(Should be a valid hex color)"
                        )
                    )
                    try:
                        answer = await self.bot.wait_for(
                            "message", check=check, timeout=60.0
                        )
                        if cancel_check(answer):
                            await msg.delete()
                            return await ctx.send("Cancelled!")
                        match = re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", answer.content)
                        if match:
                            color = answer.content.replace("#", "0x")
                            embed.color = int(color, 16)
                            await msg.delete()
                        else:
                            await msg.delete()
                            await ctx.send(
                                "Invalid Hex string, starting the command again.."
                            )
                            await asyncio.sleep(1)
                            return await ctx.invoke(ctx.command, channel)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return await ctx.send("Cancelled the session as it's inactive!")
                elif color.content.strip().lower() == "n":
                    await color_msg.delete()
            except asyncio.TimeoutError:
                await color_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            footer_msg = await ctx.send(embed=generate_embed('Would the announcement embed have footer? [y/n]'))
            try:
                footer = await self.bot.wait_for('message', check=check, timeout=60.0)
                if cancel_check(footer):
                    return await ctx.send('Cancelled!')
                elif not footer.content.strip().lower() in ["y", "n"]:
                    await footer_msg.delete()
                    await ctx.send("Invalid option, starting the command again..")
                    await asyncio.sleep(1)
                    return await ctx.invoke(ctx.command, channel)
                elif footer.content.strip().lower() == 'y':
                    await footer_msg.delete()
                    msg = await ctx.send(embed=generate_embed('What would be the footer text?(Must be within 2048 characters)'))
                    try:
                        answer = await self.bot.wait_for("message", check=footer_check, timeout=60.0)
                        if cancel_check(answer):
                            return await ctx.send("Cancelled!")
                        embed.set_footer(text=answer.content)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        return await ctx.send("Cancelled the session as it's inactive!")
                elif footer.content.strip().lower() == 'n':
                    await footer_msg.delete()
            except asyncio.TimeoutError:
                await footer_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            time_msg = await ctx.send(embed=generate_embed('When the announcment embed should be posted?(Must be a valid human time eg. 10s/10m/10h, max time is 24hr)'))
            try:
                time = await self.bot.wait_for("message", check=check, timeout=60.0)
                if cancel_check(time):
                    return await ctx.send("Cancelled!")
                await time_msg.delete()
                try:
                    parsed_time = parse(time.content)
                except Exception:
                    return await ctx.send(f":negative_squared_cross_mark: | The given time is invalid or the given time is more than max time(24hr)")
            except asyncio.TimeoutError:
                await time_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            announcement_id = generate_id()
            embed_details = f'{embed.to_dict()}'.replace("'", '"')
            await self.bot.pool.execute("INSERT INTO timed_announcements(announcement_id, channel_id, embed_details, expires) VALUES($1, $2, $3, $4);", announcement_id, channel.id, embed_details, parsed_time)
            await self.bot.cache.cache_timed_announcements()
            await self.bot.cache.list_timed_announcements()
            await self.bot.pool.execute("INSERT INTO timed_announcement_backups(announcement_id, channel_id, embed_details, expires) VALUES($1, $2, $3, $4);", announcement_id, channel.id, embed_details, parsed_time)
            await self.bot.cache.cache_backup_timed_announcements()
            await ctx.reply(f":thumbsup: | Your announcement has been successfully added to the queue! If you would like to restore this announcement, please use the following command `{ctx.prefix}restore timed {announcement_id}`.")
        else:
            return await ctx.send("You don't have permissions to use this command!")

    @announcement.command()
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def timedRaw(self, ctx, channel: discord.TextChannel):
        """Interactively creates a timed raw announcement!"""
        allowed = await check_allowed(ctx)
        def check(msg: discord.Message):
                return ctx.author == msg.author and ctx.channel == msg.channel
        if (
            ctx.author == ctx.guild.owner
            or ctx.author.guild_permissions.administrator
            or allowed
        ):
            content_msg = await ctx.channel.send(embed=generate_embed('What would be the content of the embed?(Must be within 2048 characters)'))
            try:
                content = await self.bot.wait_for("message", check=check, timeout=300.0)
                if content.content.lower() == 'cancel' or content.content.lower() == f'{ctx.prefix}cancel':
                    return await ctx.send("Cancelled!")
                elif len(content.content) >= 2048:
                    return await ctx.send("Content is too long, must be within 2048 characters!")
                await content_msg.delete()
            except asyncio.TimeoutError:
                await content_msg.delete()
                return await ctx.send("Cancelled as the session is inactive!")
            time_msg = await ctx.send(embed=generate_embed('When the announcment embed should be posted?(Must be a valid human time eg. 10s/10m/10h, max time is 24hr)'))
            try:
                time = await self.bot.wait_for("message", check=check, timeout=60.0)
                if content.content.lower() == 'cancel' or content.content.lower() == f'{ctx.prefix}cancel':
                    return await ctx.send("Cancelled!")
                await time_msg.delete()
                try:
                    parsed_time = parse(time.content)
                except Exception:
                    return await ctx.send(f":negative_squared_cross_mark: | The given time is invalid or the given time is more than max time(24hr)")
            except asyncio.TimeoutError:
                await time_msg.delete()
                return await ctx.send("Cancelled the session as it's inactive!")
            announcement_id = generate_id()
            await self.bot.pool.execute("INSERT INTO timed_raw_announcements(announcement_id, channel_id, content, expires) VALUES($1, $2, $3, $4);", announcement_id, channel.id, content.content, parsed_time)
            await self.bot.pool.execute("INSERT INTO timed_raw_announcement_backups(announcement_id, channel_id, content, expires) VALUES($1, $2, $3, $4);", announcement_id, channel.id, content.content, parsed_time)
            await self.bot.cache.cache_timed_raw_announcements()
            await self.bot.cache.list_timed_raw_announcements()
            await self.bot.cache.cache_timed_raw_announcement_backups()
            return await ctx.reply(f":thumbsup: | Your announcement has been successfully added to the queue! If you would like to restore this announcement, please use the following command `{ctx.prefix}restore timedRaw {announcement_id}`.")
        else:
            return await ctx.send("You don't have permissions to use this command!")

    @announcement.command()
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def raw(self, ctx, channel: discord.TextChannel):
        """Interactively creates a raw announcement!"""
        allowed = await check_allowed(ctx)
        def check(msg: discord.Message):
                return ctx.author == msg.author and ctx.channel == msg.channel
        if (
            ctx.author == ctx.guild.owner
            or ctx.author.guild_permissions.administrator
            or allowed
        ):
            content_msg = await ctx.channel.send(embed=generate_embed('What would be the content of the embed?(Must be within 2048 characters)'))
            try:
                content = await self.bot.wait_for("message", check=check, timeout=300.0)
                if content.content.lower() == 'cancel' or content.content.lower() == f'{ctx.prefix}cancel':
                    return await ctx.send("Cancelled!")
                elif len(content.content) >= 2048:
                    return await ctx.send("Content is too long, must be within 2048 characters!")
                await content_msg.delete()
                announcement_id = generate_id()
                await self.bot.pool.execute("INSERT INTO raw_announcements(announcement_id, channel_id, content) VALUES($1, $2, $3);", announcement_id, channel.id, content.content.strip())
                await self.bot.cache.cache_raw_announcements()
                await ctx.reply(f":thumbsup: | Your announcement has been successfully posted! If you would like to restore this announcement, please use the following command `{ctx.prefix}restore timedRaw {announcement_id}`.")
                await channel.send(content.content)
            except asyncio.TimeoutError:
                await content_msg.delete()
                return await ctx.send("Cancelled as the session is inactive!")
        else:
            return await ctx.send("You don't have permissions to use this command!")

def setup(bot):
    bot.add_cog(Announcement(bot))
