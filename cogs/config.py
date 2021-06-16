# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

from utils.utlities import generate_embed

class Config(commands.Cog):
    """Configuration commands which allows you to modify bot according to your specifications!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        """Base group command, reply all the sub-commands it has! All the sub-commands can only be used if the user has `adminstrator` permissions!"""
        return await ctx.send_help(ctx.command)

    @config.command()
    async def changePrefix(self, ctx, prefix: str):
        """Set a customised server prefix!"""
        prefix = prefix.strip()
        if len(prefix) > 3:
            return await ctx.reply(
                ":negative_squared_cross_mark: | The prefix must be within 3 characters!"
            )
        await self.bot.pool.execute(
            "UPDATE settings SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id
        )
        # updating the cache
        guild = self.bot.cache.get_setting(ctx.guild.id)
        self.bot.cache.settings[ctx.guild.id] = {
            "prefix": prefix,
            "allowed_roles": guild["allowed_roles"],
        }
        await ctx.reply(
            embed=generate_embed(
                f":thumbsup: | Successfully changed the prefix to: `{prefix}`!",
                delete_after=10.0,
            )
        )

    @config.command()
    async def addRole(self, ctx, role: discord.Role):
        """Enable specific roles for making announcements!"""
        guild = self.bot.cache.get_setting(ctx.guild.id)
        allowed_roles = guild.allowed_roles
        if not allowed_roles:
            roles = []
            roles.append(role.id)
            await self.bot.pool.execute(
                "UPDATE settings SET allowed_roles = $1 WHERE guild_id = $2",
                roles,
                ctx.guild.id,
            )
            # updating the cache
            self.bot.cache.settings[ctx.guild.id] = {
                "prefix": guild["prefix"],
                "allowed_roles": roles,
            }
            embed = generate_embed(
                f":thumbsup: | Successfully added `{role.name}` to allowed roles list, now any person with `{role.name}` can make announcements!"
            )
            embed.set_footer(
                text=f"Tip: To remove a role from making announcements, use: `{ctx.prefix}config remRole <role>`",
                icon_url=ctx.guild.icon_url,
            )
            await ctx.reply(embed=embed)
            return
        if role.id in allowed_roles:
            return await ctx.reply(
                f":negative_squared_cross_mark: | `{role.name}` role  already has permissions to make announcements!"
            )
        allowed_roles.append(role.id)
        await self.bot.pool.execute(
            "UPDATE settings SET allowed_roles = $1 WHERE guild_id = $2",
            allowed_roles,
            ctx.guild.id,
        )
        # updating the cache
        self.bot.cache.settings[ctx.guild.id] = {
            "prefix": guild["prefix"],
            "allowed_roles": allowed_roles,
        }
        embed = generate_embed(
            f":thumbsup: | Successfully added `{role.name}` to allowed roles list, now any person with `{role.name}` role can make announcements!"
        )
        embed.set_footer(
            text=f"Tip: To remove a role from making announcements, use: `{ctx.prefix}config remRole <role>`",
            icon_url=ctx.guild.icon_url,
        )
        await ctx.reply(embed=embed)

    @config.command()
    async def remRole(self, ctx, role: discord.Role):
        """Removes permissions for active roles to make announcements."""
        guild = self.bot.cache.get_setting(ctx.guild.id)
        allowed_roles = guild.allowed_roles
        if not allowed_roles:
            return await ctx.reply(
                f":negative_squared_cross_mark: | You haven't added any roles to make announcements yet, to add a role use: `{ctx.prefix}config addRole <role>`!"
            )
        if not role.id in allowed_roles:
            return await ctx.reply(
                f":negative_squared_cross_mark: | `{role.name}` doesn't exist in the allowed roles list!"
            )
        allowed_roles.remove(role.id)
        await self.bot.pool.execute(
            "UPDATE settings SET allowed_roles = $1 WHERE guild_id = $2",
            allowed_roles,
            ctx.guild.id,
        )
        # updating the cache
        self.bot.cache.settings[ctx.guild.id] = {
            "prefix": guild["prefix"],
            "allowed_roles": allowed_roles,
        }
        embed = generate_embed(
            f":thumbsup: | Successfully removed `{role.name}` from allowed roles list, now any person with `{role.name}` role cannot able make announcements!"
        )
        embed.set_footer(
            text=f"Tip: To add a role on making announcements, use: `{ctx.prefix}config addRole <role>`",
            icon_url=ctx.guild.icon_url,
        )
        await ctx.reply(embed=embed)

    @config.command()
    async def roleList(self, ctx):
        """Replys the allowed roles list"""
        guild = self.bot.cache.get_setting(ctx.guild.id)
        allowed_roles = guild.allowed_roles
        if not allowed_roles:
            return await ctx.reply(
                f":negative_squared_cross_mark: | You haven't added any roles to make announcements yet, to add a role use: `{ctx.prefix}config addRole <role>`!"
            )
        desc = ""
        index = 1
        for role_id in allowed_roles:
            role = ctx.guild.get_role(role_id)
            desc += f"{index}) {role.mention}\n"
            index += 1
        embed = generate_embed(
            desc, title="Allowed roles list", thumbnail=ctx.guild.icon_url
        )
        return await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Config(bot))
