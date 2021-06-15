# -*- coding: utf-8 -*-

import json
import random

from discord import Embed


def generate_embed(description, color=0xFEC80B, **kwargs):
    """Generate embed from given arguments"""
    embed = Embed()
    embed.color = color
    embed.description = description
    title = kwargs.get("title")
    thumbnail = kwargs.get("thumbnail")
    image = kwargs.get("image")
    footer = kwargs.get("footer")
    if title:
        embed.title = title
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    if footer:
        embed.set_footer(text=footer)
    return embed


async def check_allowed(ctx):
    """Check if the top_role of author is allowed to use announcement commands"""
    settings = ctx.bot.cache.get_setting(ctx.guild.id)
    if not settings.allowed_roles:
        return None
    return ctx.author.top_role.id in settings.allowed_roles


def generate_id():
    """Generate a random 4 digit unique number"""
    val = 0
    while len(set(str(val))) != 4:
        val = random.randint(1000, 9999)
    return val

class DottedDict(object):
    def __init__(self, data: dict):
        for x in data.items():
            self.__setattr__(x[0], x[1])

def load_config():
    """Load the data in config.json file"""
    with open("config.json", "r") as f:
        return DottedDict(json.load(f))