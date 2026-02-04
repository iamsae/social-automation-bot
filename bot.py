import os
import discord
import asyncio
import feedparser
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from xai_sdk import Client  # Fixed for Grok

# ====== RAILWAY CONFIG ======
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))
GROK_API_KEY = os.getenv("GROK_API_KEY")

grok_client = Client(api_key=GROK_API_KEY)

# ====== VIBE LORE ======
VIBE_LORE = (
    "You are the Vibe Digital Agent. Your world is neon aesthetics, "
    "stylized cars, and underground music. You know NORTH26 and DX."
)

PERSONALITIES = {
    "vibe": f"{VIBE_LORE} Tone: Chill, neon-coded, rhythmic.",
    "goblin": f"{VIBE_LORE} Tone: Unhinged Gen Z energy, chaotic brainrot.",
    "savage": f"{VIBE_LORE} Tone: Savage roast-heavy, judgmental of mid cars.",
    "angel": f"{VIBE_LORE} Tone: Soft, uplifting, pure aesthetic vibes."
}

class VibeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="s!", intents=intents)
        self.current_mode = "vibe"

    async def setup_hook(self):
        await self.tree.sync()

bot = VibeBot()

@bot.tree.command(name="mode", description="Switch the bot's vibe")
@app_commands.choices(vibe=[
    app_commands.Choice(name="Default Vibe", value="vibe"),
    app_commands.Choice(name="Unhinged Goblin", value="goblin"),
    app_commands.Choice(name="Savage Roast", value="savage"),
    app_commands.Choice(name="Soft Angel", value="angel"),
])
async def mode(interaction: discord.Interaction, vibe: app_commands.Choice[str]):
    bot.current_mode = vibe.value
    await interaction.response.send_message(f"Vibe shifted to **{vibe.name}** ⚡")

@bot.tree.command(name="chat", description="Talk to the Vibe Agent")
async def chat(interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    try:
        system_prompt = PERSONALITIES.get(bot.current_mode, VIBE_LORE)
        response = grok_client.chat.completions.create(
            model="grok-2-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        await interaction.followup.send(response.choices[0].message.content)
    except Exception as e:
        await interaction.followup.send(f"Brain fog... 💀 `{e}`")

bot.run(TOKEN)