# -*- coding: utf-8 -*-

import re
from datetime import datetime, timedelta

from discord.ext import commands


def parse(time=0, as_datetime=True):
    """Converts human time to seconds/datetime objects

    Parameters
    ----------
    time: str
        the data which we need to parse it as int/datetime object, should be in this format: x[s/m/h] where x is the time, minimum is 1s and max is 24h
    as_datetime: bool
        defaults to `True` which will convert human time into `datetime` object, if set to `False` the converted time will return in seconds as `int`
    """
    time_list = re.split("(\d+)", time)
    try:
        if time_list[2] == "s":
            sec = int(time_list[1])
        if time_list[2] == "m":
            sec = int(time_list[1]) * 60
        if time_list[2] == "h":
            if int(time_list[1]) > 24:
                raise commands.BadArgument("given time is more than 24hrs", time)
            sec = int(time_list[1]) * 60 * 60
        if as_datetime:
            now = datetime.utcnow()
            return now + timedelta(seconds=sec)
        return sec
    except IndexError:
        raise commands.BadArgument("given time format is invalid", time)
