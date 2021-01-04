import discord
import os
from discord.ext import commands

class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    # The listener decorator is an equivalent of the events decorator.
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send("Welcome {0.mention}.".format(member))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send("{0.mention} has left.".format(member))

    # The command decorator.
    @commands.command()
    async def hi(self, ctx, *, member : discord.Member = None):
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send("Hello {0.name}!".format(member))
        else:
            await ctx.send("Hello {0.name} again!".format(member))
        self._last_member = member

def setup(bot):
    bot.add_cog(Welcome(bot))
