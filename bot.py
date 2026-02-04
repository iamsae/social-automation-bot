import os
import re
import asyncio
import discord
import feedparser
import random
from discord.ext import commands, tasks
from discord import app_commands
from datetime import timedelta
from xai_sdk import Client  # Grok SDK

# ====== RAILWAY CONFIG ======
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) # Notification channel
GROK_API_KEY = os.getenv("GROK_API_KEY")

grok_client = Client(api_key=GROK_API_KEY)

# Social Media IDs
YOUTUBE_ID = "UCKXtEuNAVfhSID-5yNFSp7Q"
INSTA_RSS = "https://rsshub.app/instagram/user/vibe.music_39"
TIKTOK_RSS = "https://rsshub.app/tiktok/user/@vibe.music_39"

# ====== BUTTON VIEW ======
class NotificationView(discord.ui.View):
    def __init__(self, url):
        super().__init__(timeout=None)
        # Adds a functional link button to the message
        self.add_item(discord.ui.Button(label="View Post", url=url, style=discord.ButtonStyle.link))

    @discord.ui.button(label="Vibe Check", style=discord.ButtonStyle.blurple)
    async def vibe_check(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Vibe is currently: **IMMACULATE** ⚡", ephemeral=True)

# ====== THE BOT ======
class VibeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="s!", intents=intents)
        self.last_posts = {"yt": None, "ig": None, "tt": None}

    async def setup_hook(self):
        self.check_socials.start() # Start the background loop
        await self.tree.sync()

bot = VibeBot()

# ====== NOTIFICATION LOOP ======
@tasks.loop(minutes=10)
async def check_socials():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel: return

    # Simple YouTube RSS Example
    yt_feed = feedparser.parse(f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_ID}")
    if yt_feed.entries:
        latest = yt_feed.entries[0]
        if latest.id != bot.last_posts["yt"]:
            bot.last_posts["yt"] = latest.id
            view = NotificationView(latest.link)
            await channel.send(f"⚡ **NEW VIBE DROPPED ON YOUTUBE**\n{latest.title}", view=view)

# ====== TEST COMMAND ======
@bot.tree.command(name="test_notif", description="Preview a notification with buttons")
async def test_notif(interaction: discord.Interaction):
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Example URL
    view = NotificationView(test_url)
    
    embed = discord.Embed(
        title="🎬 New Content Preview",
        description="This is how your social media alerts will look!",
        color=0x00ffcc # Neon Vibe Color
    )
    embed.set_footer(text="Vibe Digital Agent • Notification System")
    
    await interaction.response.send_message(embed=embed, view=view)

# (Keep your s!kick, s!ban, and /chat commands from the previous version here)

bot.run(TOKEN)