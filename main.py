from typing import Final
import os
from dotenv import load_dotenv
import asyncio
import nest_asyncio
nest_asyncio.apply()

from datetime import datetime
from pytz import timezone

import discord
from discord import Intents, Message
from discord.ext import commands

import yt_dlp
import ffmpeg
import botfuncs

"""
i started with code for this from Indently's tutorial on creating a Discord bot with Python: https://www.youtube.com/watch?v=UYJDKSah-Ww
"""

# load token from the .env
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# bot setup
intents: Intents = Intents.default()
intents.message_content = True
bot: commands.Bot = commands.Bot(command_prefix="juul ", intents=intents)


# startup
@bot.event
async def on_ready() -> None:
    print(f"{bot.user} is now running")
    # trying to send a message on startup to general
    # this code is from: https://stackoverflow.com/questions/49446882/how-to-get-all-text-channels-using-discord-py
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if "bot" in channel.name:
                await channel.send("I'M ALIVE")



# handling incoming messages
@bot.event
async def on_message(message: Message) -> None:
    # checks if the bot sent the message. we do not want the bot to respond to its own messages
    if message.author == bot.user:
        return

    server: str = str(message.guild)
    username: str = str(message.author)
    user_message: str = str(message.content)
    channel: str = str(message.channel)

    print(f'[{server}: #{channel}] {username}: "{user_message}"')
    await bot.process_commands(message)


@bot.command()
async def hello(ctx):
    """says hello! :)"""
    await ctx.send(botfuncs.hello(ctx.author.mention))


@bot.command()
async def roll(ctx, dice: str):
    """rolls a dice in NdN format"""
    await ctx.send(botfuncs.roll(dice))


@bot.command()
async def cat(ctx):
    """a cute cat gif :3"""
    await ctx.send(botfuncs.cat())


@bot.command()
async def insult(ctx):
    """insults the person who called it"""
    await ctx.send(botfuncs.insult(ctx.author.mention))


@bot.command()
async def riddle(ctx):
    """a riddle with a censored answer"""
    await ctx.send(botfuncs.riddle())


@bot.command(aliases=["dad joke", "dad"])
async def dadjoke(ctx):
    """a corny dad joke! :D"""
    await ctx.send(botfuncs.dadjoke())


@bot.command()
async def haiku(ctx):
    """a haiku from a pregenerated list"""
    await ctx.send(botfuncs.haiku())


@bot.command()
async def flirt(ctx):
    """a cheesy pickup line :p"""
    await ctx.send(botfuncs.flirt(ctx.author.mention))
    
@bot.command()
async def voice_test(ctx):
    """DEBUG checks if bot is connected to a VC"""
    voice = ctx.guild.voice_client
    await ctx.send(f"{voice}\nin {voice.guild}, connected to channel {voice.channel}.\nis_connected: ***{voice.is_connected()}*** is_playing: ***{voice.is_playing()}***")


@bot.command(description="this searches through every single message to find instances of the keyword argument from the given user, so it may take a while depending on how many messages have been sent in the server\nusage: juul count [word/\"multi-word phrase\"] @user")
async def count(ctx, kwarg: str = commands.parameter(description="keyword or \"multi-word phrase\" you want to search"), member: discord.Member = commands.parameter(description="@ the user whose messages u wanna search")):
    """number of times a user has said a keyword. MAY TAKE A WHILE"""
    kwarg = kwarg.lower()
    if not member:
        member = ctx.author
    counter: int = 0
    async with ctx.typing():
        for channel in ctx.guild.text_channels:
            async for message in channel.history(limit=None):
                if message.author == member and kwarg in message.content.lower():
                    #this is kinda messy but basically the last 16 chars of this datetime str are seconds and microseconds, so i'm trimming them off to make the log more readable
                    timestamp = str(message.created_at.astimezone(timezone('US/Central')))[:-16] + " CST"
                    counter += message.content.count(kwarg)
                    print(f"{ctx.guild}, {ctx.author.display_name}'s count command for \"{kwarg}\" is at: {counter}. From {timestamp}")
    await ctx.reply(f"{member.mention}, you have said \"{kwarg}\" **{counter}** times in this server")


# the following code for playing music is from the examples on the Discord.py GitHub
# Suppress noise about console usage from errors
yt_dlp.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options, executable="ffmpeg"), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {query}')

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""
        
        voice = ctx.guild.voice_client

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            voice.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


# start the bot
async def main() -> None:
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.run(token=TOKEN)



loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# planned feature/commands:
# plays music with FFMPEG -- MAY NOT BE POSSIBLE?? DISCORD.PY MIGHT NEED UPDATE
# leaves server if enough people use the command within a certain timeframe per Jae
# removes images if it detects mustard tone per Mae
# animal persona generator tied to Discord User ID so that it returns the same one each time per Mae
#
# implemeneted already:
# dice roller per Ana -- DONE 2024-01-30
# riddles per Echo, i found API: https://riddles-api.vercel.app -- DONE 2024-01-31
# dad jokes per Baz and Tanya, i found API: https://icanhazdadjoke.com -- DONE 2024-01-31
# cat gifs per Prof. Alexandra, SHE EVEN PULLED THROUGH WITH AN API: https://thecatapi.com -- DONE 2024-01-31
# insults per Jude, i found API: https://github.com/EvilInsultGenerator/website -- DONE 2024-01-31
# haikus per Roshni -- DONE 2024-01-31
# pickup lines per Emaan -- DONE 2024-01-31
# returns how many times a user has said a given keyword per Carlos -- DONE 2024-02-03
