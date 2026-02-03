import discord
import asyncio
import os
import feedparser

TOKEN = os.getenv("TOKEN")
channel_id_raw = os.getenv("CHANNEL_ID")
if not channel_id_raw:
    raise ValueError("CHANNEL_ID environment variable is missing")
CHANNEL_ID = int(channel_id_raw)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

last_video_id = None

async def check_youtube():
    global last_video_id
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    while not client.is_closed():
        feed = feedparser.parse("https://www.youtube.com/feeds/videos.xml?channel_id=UCKxEuNAvfh5ID-5yN_FSp7Q")
        latest = feed.entries[0]
        if latest.id != last_video_id:
            last_video_id = latest.id
            await channel.send(f"<@&1465252354600337459> New YouTube video just dropped! 📹\n{latest.link}")
        await asyncio.sleep(300)

async def check_instagram():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    last_post = None

    while not client.is_closed():
        feed = feedparser.parse("https://rsshub.app/instagram/user/vibe.music_39")
        latest = feed.entries[0]

        if latest.id != last_post:
            last_post = latest.id
            await channel.send(
                f"<@&1465252354600337459> New Instagram post! 📸\n{latest.link}"
            )

        await asyncio.sleep(300) 

async def check_tiktok():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    last_tt_post = None

    while not client.is_closed():
        feed = feedparser.parse("https://rsshub.app/tiktok/user/@vibe.music_39")
        latest = feed.entries[0]

        if latest.id != last_tt_post:
            last_tt_post = latest.id
            await channel.send(
                f"<@&1465252354600337459> New TikTok just dropped! 🎵\n{latest.link}"
            )

        await asyncio.sleep(300)
client.loop.create_task(check_youtube())
client.loop.create_task(check_instagram())
client.loop.create_task(check_tiktok())
client.run(TOKEN)