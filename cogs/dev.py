# -*- coding: utf-8 -*-

import os
from utils.utlities import generate_embed

import discord
from discord.ext import commands


class Dev(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.backup_index = 0

    @commands.is_owner()
    @commands.group(aliases=["bl"], invoke_without_command=True)
    async def blacklist(self, ctx):
        """Commands related to blacklisting"""
        await ctx.send_help(ctx.command)

    @blacklist.command()
    async def add(self, ctx, guild_id: int, *, reason):
        """Add the given guild id to blacklist"""
        guild = self.bot.get_guild(guild_id)
        if guild:
            self.bot.blacklist.add(guild_id)
            await guild.leave()
            return await ctx.reply(
                f":thumbsup: | Successfully blacklisted {guild.name} reason being: `{reason}`"
            )

    @blacklist.command()
    async def remove(self, ctx, guild_id: int):
        """Remove the given guild id from blacklist"""
        self.bot.blacklist.remove(guild_id)
        return await ctx.reply(
            f":thumbsup: | Successfully un-blacklisted guild(`ID: {guild_id}`)"
        )

    @blacklist.command()
    async def list(self, ctx):
        """Show the list of blacklisted Guild ID'S"""
        desc = ""
        index = 1
        if len(self.bot.blacklist._cache) == 0:
            return await ctx.send("Blacklist data file is empty.")
        for guild in self.bot.blacklist._cache:
            desc += f"#{index} - {guild}"
            index += 1
        embed = generate_embed(desc)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def backup(self, ctx):
        """Backup the postgresql records"""
        self.backup_index += 1
        os.system(f'pg_dump --dbname={self.bot.config.dsn} -F c -b -v -f backups/00{self.backup_index}.backup')
        file = discord.File(fp=f'backups/00{self.backup_index}.backup')
        await ctx.send(file=file)


def setup(bot):
    bot.add_cog(Dev(bot))
