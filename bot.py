import os
import asyncio
import discord
import feedparser
from discord.ext import commands

# ====== CONFIG ======
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN environment variable is missing")

channel_id_raw = os.getenv("CHANNEL_ID")
if not channel_id_raw:
    raise ValueError("CHANNEL_ID environment variable is missing")
CHANNEL_ID = int(channel_id_raw)

ROLE_ID = 1465252354600337459  # role to ping

YOUTUBE_CHANNEL_ID = "UCKXtEuNAVfhSID-5yNFSp7Q"
INSTAGRAM_RSS = "https://rsshub.app/instagram/user/vibe.music_39"
TIKTOK_RSS = "https://rsshub.app/tiktok/user/@vibe.music_39"

intents = discord.Intents.default()
intents.message_content = True  # needed for commands

# ====== BOT CLASS ======
class MyBot(commands.Bot):
    async def setup_hook(self):
        # register background tasks
        self.loop.create_task(check_youtube(self))
        self.loop.create_task(check_instagram(self))
        self.loop.create_task(check_tiktok(self))


bot = MyBot(command_prefix="!", intents=intents)

# ====== EVENTS ======
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# ====== WATCHERS ======
last_youtube_id = None
last_ig_id = None
last_tt_id = None


async def check_youtube(bot: commands.Bot):
    global last_youtube_id
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    while not bot.is_closed():
        feed = feedparser.parse(
            f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
        )
        if not feed.entries:
            await asyncio.sleep(300)
            continue

        latest = feed.entries[0]
        if latest.id != last_youtube_id:
            last_youtube_id = latest.id
            await channel.send(
                f"<@&{ROLE_ID}> New YouTube video just dropped! 📹\n{latest.link}"
            )

        await asyncio.sleep(300)  # 5 minutes


async def check_instagram(bot: commands.Bot):
    global last_ig_id
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    while not bot.is_closed():
        feed = feedparser.parse(INSTAGRAM_RSS)
        if not feed.entries:
            await asyncio.sleep(300)
            continue

        latest = feed.entries[0]
        if latest.id != last_ig_id:
            last_ig_id = latest.id
            await channel.send(
                f"<@&{ROLE_ID}> New Instagram post! 📸\n{latest.link}"
            )

        await asyncio.sleep(300)


async def check_tiktok(bot: commands.Bot):
    global last_tt_id
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    while not bot.is_closed():
        feed = feedparser.parse(TIKTOK_RSS)
        if not feed.entries:
            await asyncio.sleep(300)
            continue

        latest = feed.entries[0]
        if latest.id != last_tt_id:
            last_tt_id = latest.id
            await channel.send(
                f"<@&{ROLE_ID}> New TikTok just dropped! 🎵\n{latest.link}"
            )

        await asyncio.sleep(300)


# ====== COMMANDS ======
@bot.command()
async def test(ctx: commands.Context):
    await ctx.send(f"<@&{ROLE_ID}> Bot is alive and ready! ✅")


# ====== RUN ======
bot.run(TOKEN)