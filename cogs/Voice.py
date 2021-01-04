import discord
import os
import youtube_dl
from discord import Spotify
from discord.ext import commands
from discord.utils import get

class Voice(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def listening(self, ctx, member : discord.Member = None):
        member = member or ctx.author
        for activity in member.activities:
            if isinstance(activity, Spotify):
                await ctx.send(f"{member} is listening to {activity.title} by {activity.artist}.")

    """@commands.command()
    async def join(self, ctx):
        global voice
        channel = ctx.message.author.voice.channel
        voice = get(self.bot.voice_clients, guild = ctx.guild)

        if voice and voice.is_connected():
            await voice.move_to(channel)"""

def setup(bot):
    bot.add_cog(Voice(bot))
