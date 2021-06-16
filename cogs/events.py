from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.NotOwner):
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Command `{ctx.command.name}` requires `{error.param.name}` argument, you missed giving that! For more information see: `{ctx.prefix}help {ctx.command.qualified_name}`")
        
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(f"{''.join(error.args)} not found!")

def setup(bot):
    bot.add_cog(Events(bot))