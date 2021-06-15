# -*- coding: utf-8 -*-

import asyncio

import asyncpg
import click

from utils.utlities import load_config

@click.group(chain=True)
def cli():
    """Announcer db-launcher"""


@cli.command("initdb", help="Creates database tables.")
def initdb():
    schemas = []

    # Opening the schema file
    with open("schema.sql", "r", encoding="utf-8") as schema_file:
        data = schema_file.read()
        schemas = [schema.strip() for schema in data.split(";") if schema.strip()]

    config = load_config()

    # Committing changes on database
    async def do_database_operations():
        conn = await asyncpg.create_pool(
            config.dsn
        )
        for schema in schemas:
            try:
                await conn.execute(f"{schema.strip()};")
            except Exception as e:
                print(e)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_database_operations())

    print("CLI >> Database oprations done.")


@cli.command("start", help="Start the bot")
def start():
    from bot import Announcer

    bot = Announcer()
    bot.run(bot.config.token)


if __name__ == "__main__":
    cli()
