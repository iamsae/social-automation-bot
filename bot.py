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

client.loop.create_task(check_youtube())
client.run(TOKEN)
