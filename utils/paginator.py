# -*- coding: utf-8 -*-

import asyncio

import discord


class Paginator(object):
    """A simple paginator implementation
    
    Parameters
    ----------
    bot: `commands.Bot`
        instance of a bot
    channel: `discord.TextChannel`
        The channel to start the paginator
    user: `discord.Member`
        the command author
    pages: `List[discord.Embed]`
        embeds to paginate
    """

    # TODO: Improve this

    def __init__(self, bot, channel: discord.TextChannel, user, pages):
        self.bot = bot
        self.channel = channel
        self.user = user
        self.index = 0
        self.pages = pages

    async def paginate(self) -> None:
        """Starts a paginator session"""
        pages = self.pages
        message = await self.channel.send(embed=pages[self.index])

        emotes = [
            "\u23EA",
            "\u2B05",  # left arrow emoji
            "🛑",  # stop button emoji
            "\u27A1",  # right arrow emoji
            "\u23E9",
        ]

        running = True

        while running:
            for emote in emotes:
                await message.add_reaction(emote)

            def check(r, u):
                return r.message.id == message.id and u.id == self.user.id

            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=check, timeout=60.0
                )
                if str(reaction.emoji) == emotes[1]:
                    await message.remove_reaction(reaction.emoji, user)
                    if self.index <= 0:
                        continue
                    self.index -= 1
                    embed = pages[self.index]
                    embed.set_footer(
                        text=f"Requested by {str(self.user)} | Page {self.index+1}/{len(pages)}",
                        icon_url=self.user.avatar_url,
                    )
                    await message.edit(content=None, embed=pages[self.index])
                if str(reaction.emoji) == emotes[2]:
                    await message.remove_reaction(reaction.emoji, user)
                    self.index = 0
                    await message.clear_reactions()
                    running = False
                if str(reaction.emoji) == emotes[3]:
                    await message.remove_reaction(reaction.emoji, user)
                    if self.index >= len(pages) - 1:
                        continue
                    self.index += 1
                    embed = pages[self.index]
                    embed.set_footer(
                        text=f"Requested by {str(self.user)} | Page {self.index+1}/{len(pages)}",
                        icon_url=self.user.avatar_url,
                    )
                    await message.edit(content=None, embed=pages[self.index])
                if str(reaction.emoji) == emotes[4]:
                    await message.remove_reaction(reaction.emoji, user)
                    if self.index >= len(pages) - 1:
                        continue
                    self.index = len(pages) - 1
                    embed = pages[self.index]
                    embed.set_footer(
                        text=f"Requested by {str(self.user)} | Page {len(pages)}/{len(pages)}",
                        icon_url=self.user.avatar_url,
                    )
                    await message.edit(content=None, embed=pages[self.index])
                if str(reaction.emoji) == emotes[0]:
                    await message.remove_reaction(reaction.emoji, user)
                    if self.index <= 0:
                        continue
                    self.index = 0
                    embed = pages[self.index]
                    embed.set_footer(
                        text=f"Requested by {str(self.user)} | Page 1/{len(pages)}",
                        icon_url=self.user.avatar_url,
                    )
                    await message.edit(content=None, embed=pages[self.index])

            except asyncio.TimeoutError:
                await message.clear_reactions()
                running = False
