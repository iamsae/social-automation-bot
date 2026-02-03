import os
import re
import asyncio
import discord
import feedparser
import aiohttp
import random
from discord.ext import commands
from datetime import timedelta

# ====== ENV CONFIG ======
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))

YOUTUBE_CHANNEL_ID = "UCKXtEuNAVfhSID-5yNFSp7Q"
INSTAGRAM_RSS = "https://rsshub.app/instagram/user/vibe.music_39"
TIKTOK_RSS = "https://rsshub.app/tiktok/user/@vibe.music_39"

MAX_TIMEOUT_MINUTES = 28 * 24 * 60  # 28 days

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# ====== GEN Z REPLY ======
def genz_reply(text: str) -> str:
    if len(text) > 180:
        text = text[:170] + "…"
    slang = ["fr", "no cap", "deadass", "lowkey", "highkey", "💀", "bro", "vibe", "slaps", "sus", "bet"]
    text += " " + random.choice(slang)
    return text

# ====== DURATION PARSER ======
def parse_duration(duration_str: str) -> int | None:
    pattern = r"(\d+)([dhms])"
    matches = re.findall(pattern, duration_str.lower())
    if not matches:
        return None
    total_seconds = 0
    for value, unit in matches:
        value = int(value)
        if unit == "d":
            total_seconds += value * 86400
        elif unit == "h":
            total_seconds += value * 3600
        elif unit == "m":
            total_seconds += value * 60
        elif unit == "s":
            total_seconds += value
    return total_seconds // 60

# ====== BOT CLASS ======
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="s!", intents=intents)
        self.last_youtube_id = None
        self.last_instagram_id = None
        self.last_tiktok_id = None

    async def setup_hook(self):
        self.loop.create_task(self.check_youtube())
        self.loop.create_task(self.check_instagram())
        self.loop.create_task(self.check_tiktok())

    async def check_youtube(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        while not self.is_closed():
            feed = feedparser.parse(f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}")
            if feed.entries:
                latest = feed.entries[0]
                if latest.id != self.last_youtube_id:
                    self.last_youtube_id = latest.id
                    await channel.send(f"<@&{ROLE_ID}> New YouTube video just dropped! 📹\n{latest.link}")
            await asyncio.sleep(300)

    async def check_instagram(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        while not self.is_closed():
            feed = feedparser.parse(INSTAGRAM_RSS)
            if feed.entries:
                latest = feed.entries[0]
                if latest.id != self.last_instagram_id:
                    self.last_instagram_id = latest.id
                    await channel.send(f"<@&{ROLE_ID}> New Instagram post! 📸\n{latest.link}")
            await asyncio.sleep(300)

    async def check_tiktok(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        while not self.is_closed():
            feed = feedparser.parse(TIKTOK_RSS)
            if feed.entries:
                latest = feed.entries[0]
                if latest.id != self.last_tiktok_id:
                    self.last_tiktok_id = latest.id
                    await channel.send(f"<@&{ROLE_ID}> New TikTok just dropped! 🎵\n{latest.link}")
            await asyncio.sleep(300)

bot = MyBot()

# ====== EVENTS ======
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot or message.channel.id != TARGET_CHANNEL_ID:
        return

    prompt = message.content
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    payload = {
        "contents": [
            {
                "parts": [{"text": f"Reply shortly, Gen Z slang, simple: {prompt}"}]
            }
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
        "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent",
        headers=headers,
        json=payload
    ) as response:
            if response.status != 200:
                error_text = await response.text()
                await message.channel.send(f"Gemini error {response.status}: `{error_text}`")
                return

            data = await response.json()
            try:
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                reply = genz_reply(reply)
                await message.channel.send(reply)
            except Exception as e:
                await message.channel.send(f"bro the AI glitched 💀 `{e}`")
                return

    await bot.process_commands(message)

# ====== COMMANDS ======
@bot.command()
async def test(ctx):
    await ctx.send(f"<@&{ROLE_ID}> Bot is alive and ready! ✅")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} was kicked. 🦶 Reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} was banned. 🔨 Reason: {reason}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, duration: str = None):
    if duration is None:
        minutes = MAX_TIMEOUT_MINUTES
        duration_label = "28d"
    else:
        minutes = parse_duration(duration)
        if minutes is None:
            await ctx.send("Invalid duration. Use formats like `8d`, `5h`, `30m`, `10s`, or combos like `1d12h`.")
            return
        duration_label = duration

    if minutes > MAX_TIMEOUT_MINUTES:
        await ctx.send("⚠️ Max mute duration is 28 days.")
        return

    try:
        until = discord.utils.utcnow() + timedelta(minutes=minutes)
        await member.timeout(until)
        await ctx.send(f"{member.mention} muted for **{duration_label}** 🤐")
    except Exception as e:
        await ctx.send(f"Failed to mute: {e}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    try:
        await member.timeout(None)
        await ctx.send(f"{member.mention} unmuted 🔊")
    except Exception as e:
        await ctx.send(f"Failed to unmute: {e}")

# ====== RUN ======
bot.run(TOKEN)