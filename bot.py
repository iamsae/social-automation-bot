import os
import asyncio
import discord
import feedparser
from discord.ext import commands

# ====== ENV CONFIG ======
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ROLE_ID = 1465252354600337459

YOUTUBE_CHANNEL_ID = "UCKXtEuNAVfhSID-5yNFSp7Q"
INSTAGRAM_RSS = "https://rsshub.app/instagram/user/vibe.music_39"
TIKTOK_RSS = "https://rsshub.app/tiktok/user/@vibe.music_39"

intents = discord.Intents.default()
intents.message_content = True

# ====== BOT CLASS ======
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="sae", intents=intents)
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

# ====== COMMANDS ======
@bot.command()
async def test(ctx):
    await ctx.send(f"<@&{ROLE_ID}> Bot is alive and ready saar")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="you kicking without a reason?"):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} was kicked. 🦶 Reason: {reason} damn...")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="GIVE ME A REASON"):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} was banned. 🔨 Reason: {reason}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, duration: int):
    try:
        await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=duration))
        await ctx.send(f"{member.mention} has been muted for {duration} minutes. 🤐")
    except Exception as e:
        await ctx.send(f"Failed to mute: {e}")
# ====== EVENTS ======
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# ====== RUN ======
bot.run(TOKEN)