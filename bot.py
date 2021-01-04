import asyncio
import discord
import os
import random
import youtube_dl
from discord import Activity
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
from itertools import cycle

# Load bot token from a separate .env file for privacy.
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

bot = commands.Bot(command_prefix = "!")
status = cycle(["Eins", "Zwei", "Drei", "Vier", "Funf"])

# Event decorator
@bot.event
async def on_ready():
    change_status.start()
    for guild in bot.guilds:
        #await bot.change_presence(status = discord.Status.online, activity = discord.Game("A game."))
        if guild.name == GUILD:
            break
    print(f"{bot.user} has been connected to "
          f"{guild.name}(id: {guild.id})")

# Join and leave events handled in Welcome.py cog.
"""@bot.event
async def on_member_join(member):
    print(f"{member} has joined the server.")

@bot.event
async def on_member_remove(member):
    print(f"{member} has left the server.")"""

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith("Hello"):
        await message.channel.send("Hi!")
    await bot.process_commands(message)

# Provides general error messages for all commands.
# If an error is not included here, the error will not be displayed in the terminal.
"""@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.MissingRequiredArgument):
        await ctx.send("Please add the required arguments.")"""

# Command decorator
# ctx is the context parameter
# Latency is just printed for demonstration.
@bot.command(aliases = ["tets"])
async def test(ctx):
    await ctx.send(f"This is a test command. {bot.latency*1000}ms")

# A command that takes in an argument and has the bot spit it back out.
@bot.command()
async def resp(ctx, *, arg):
    await ctx.send(arg)

# Demonstration of a check
# ex_check checks that a specific user uses the command - if false, the command !ex is ignored.
def ex_check(ctx):
    return ctx.author.id == 727634068937900134

@bot.command()
@commands.check(ex_check)
async def ex(ctx):
    await ctx.send(f"You are {ctx.author}.")

# Demonstration of a command that requires certain permissions.
@bot.command()
@commands.has_permissions(manage_messages = True)
async def clear(ctx, amount : int):
    await ctx.channel.purge(limit = amount)

# Handling errors specifically for the clear command
# Must be placed after the function definition
@clear.error
async def clear_error(ctx, err):
    if isinstance(err, commands.MissingRequiredArgument):
        await ctx.send("Please add the required arguments.")
    if isinstance(err, commands.MissingPermissions):
        await ctx.send("You do not have the permissions to use this command.")

# Commands for cogs
@bot.command()
async def load(ctx, ext):
    bot.load_extension(f"cogs.{ext}")

@bot.command()
async def reload(ctx, ext):
    bot.unload_extension(f"cogs.{ext}")
    bot.load_extension(f"cogs.{ext}")

@reload.error
async def reload_error(ctx, err):
    if isinstance(err, commands.CommandInvokeError):
        await ctx.send("Unable to reload the cog.")

@bot.command()
async def unload(ctx, ext):
    bot.unload_extension(f"cogs.{ext}")

@bot.command(aliases = ["j"])
async def join(ctx):
    #global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"The bot has entered the channel")

@bot.command(aliases = ["l"])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left the channel")
    else:
        print(f"Bot was unable to leave a/the channel")

@bot.command(aliases = ["p"])
async def play(ctx, url: str):
    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice is None:
        await ctx.send("The bot is not connected to a voice channel.")
        return

    song_exists = os.path.isfile("audio.mp3")
    try:
        if song_exists:
            os.remove("audio.mp3")
            print("Previous audio file was removed.")
    except PermissionError:
        print("Unable to delete audio file because it is in use.")
        await ctx.send("ERROR: Audio already playing")
        return

    await ctx.send("Retrieving audio.")

    # Establishes the format and quality for the audio download from YouTube.
    yt_dl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }

    print("Downloading audio file now.")
    youtube_dl.YoutubeDL(yt_dl_opts).download([url])

    for filename in os.listdir("./"):
        if filename.endswith(".mp3"):
            name = filename
            print(f"{filename} renamed.")
            os.rename(filename, "audio.mp3")

    # Lambda function deletes the file after it is finished playing to clear up space.
    voice.play(discord.FFmpegPCMAudio("audio.mp3"), after = lambda e: os.remove("audio.mp3"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.value = 0.05

    # Removes the dash before the file string from YouTube.
    # newname[0] is the title of the video as shown on YouTube.
    newname = name.rsplit("-", 1)
    await ctx.send(f"**Now Playing**: ***{newname[0]}***")
    print("Now playing audio.")

@play.error
async def play_error(ctx, err):
    if isinstance(err, commands.MissingRequiredArgument):
        print("There was no url given.")
        await ctx.send("Please enter a YouTube video url for the bot to play audio.")

@bot.command()
async def pause(ctx):
    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_playing():
        print("Pausing audio.")
        voice.pause()
        await ctx.send("Now pausing audio.")
    else:
        print("No audio is being played.")
        await ctx.send("No audio is being played.")

@bot.command(aliases = ["r"])
async def resume(ctx):
    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_paused():
        print("Resuming audio.")
        voice.resume()
        await ctx.send("Now resuming audio.")
    else:
        print("There is no audio to be resumed.")
        await ctx.send("There is no audio to be resumed.")

@bot.command()
async def stop(ctx):
    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_playing():
        print("Stopping audio.")
        voice.stop()
        await ctx.send("Audio has been stopped.")
    else:
        print("No audio is being played.")
        await ctx.send("No audio is being played.")

# Creating background tasks
@tasks.loop(seconds = 10)
async def change_status():
    await bot.change_presence(activity = discord.Game(next(status)))

# For loop to iterate through files in the cogs folder
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        # File name is spliced to remove the .py extension
        bot.load_extension(f"cogs.{filename[:-3]}")

#TODO: automated messages when I go live on Twitch, Spotify music, and more...
bot.run(TOKEN)
