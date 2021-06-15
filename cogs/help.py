import discord
from discord.ext import commands

from utils.paginator import Paginator

class PaginatedHelpMenu(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot
        pages = []

        to_hide = [
            "HelpCommand",
            "Dev"
        ]
        for cog in bot.cogs.values():
            if not cog.qualified_name in to_hide:
                embed = discord.Embed(
                    title="Announcer Help Menu",
                    color=0xFEC80B,
                    description=f"\nTo See info about a command use `{ctx.prefix}help <command>` (or) To see info about a Category use `{ctx.prefix}help <category>`",
                )
                cmds = cog.get_commands()
                if len(cmds) == 0:
                    embed.description = f"\n\nCategory - {cog.qualified_name} doesn't have any command or they are hidden by the developer"
                    pages.append(embed)
                else:
                    embed.set_thumbnail(url=ctx.bot.user.avatar_url)
                    for x in cmds:
                        embed.add_field(
                            name=f" Category - {cog.qualified_name}",
                            value=f"`{ctx.prefix}{x.name} {x.signature}`",
                        )
                    pages.append(embed)
        em = pages[0]
        em.set_footer(
            text=f"Requested by {str(ctx.author)} | Page 1/{len(pages)}",
            icon_url=ctx.author.avatar_url,
        )
        paginator = Paginator(bot, ctx.channel, ctx.author, pages)
        await paginator.paginate()

    async def send_cog_help(self, cog):
        cmds = cog.get_commands()
        embed = discord.Embed(
            title=f"Category - {cog.qualified_name}",
            color=0xFEC80B,
            description=cog.description,
        )
        embed.add_field(
            name="Commands", value=" , ".join(x.name for x in cmds if not x.hidden)
        )
        await self.context.channel.send(embed=embed)

    async def send_group_help(self, group):
        cmds = group.commands
        embed = discord.Embed(
            title=f"Group - {group.qualified_name}", color=0xFEC80B
        )
        embed.description = group.short_doc
        embed.set_footer(
            text=f"Requested by {self.context.author.display_name}",
            icon_url=self.context.author.avatar_url,
        )
        embed.add_field(
            name="Commands", value=" , ".join(x.name for x in cmds if not x.hidden)
        )
        await self.context.channel.send(embed=embed)

    async def send_command_help(self, command):
        ctx = self.context
        embed = discord.Embed(
            color=0xFEC80B,
            title=f"Command Information - {command.name}",
            description=f"**Usage**: {ctx.prefix}{command.qualified_name} {command.signature}\n**Description**: {command.short_doc}\n**Category**: {command.cog_name}",
        )
        await self.context.channel.send(embed=embed)


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = PaginatedHelpMenu()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(HelpCommand(bot))
