import os
import discord
import asyncio
import feedparser
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from xai_sdk import Client  # Corrected SDK import for Railway

# ====== RAILWAY VARIABLE CONFIG ======
# No load_dotenv() needed; Railway handles this automatically.
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))
GROK_API_KEY = os.getenv("GROK_API_KEY")

# Initialize Grok Client
grok_client = Client(api_key=GROK_API_KEY)

# ====== VIBE LORE & PERSONALITIES ======
VIBE_LORE = (
    "You are the Vibe Digital Agent. You live in a world of stylized car visuals, "
    "neon aesthetics, and underground remixed music. You represent the Vibe brand."
)

PERSONALITIES = {
    "vibe": f"{VIBE_LORE} Tone: Chill, neon-coded, rhythmic.",
    "goblin": f"{VIBE_LORE} Tone: Unhinged Gen Z energy, max brainrot, chaotic.",
    "savage": f"{VIBE_LORE} Tone: Roast-heavy, high-key judgmental of mid music.",
    "angel": f"{VIBE_LORE} Tone: Soft, uplifting, aesthetic, pure vibes.",
    "suit": f"{VIBE_LORE} Tone: Clean, corporate, professional, 'best regards' energy."
}

class VibeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="s!", intents=intents)
        self.current_mode = "vibe"

    async def setup_hook(self):
        # Syncs the slash commands to your server on startup
        await self.tree.sync()

bot = VibeBot()

# ====== SLASH COMMANDS ======

@bot.tree.command(name="mode", description="Switch the bot's personality vibe")
@app_commands.describe(vibe="Choose the new energy for the bot")
@app_commands.choices(vibe=[
    app_commands.Choice(name="Default Vibe (Neon/Chill)", value="vibe"),
    app_commands.Choice(name="Unhinged (Gen Z Chaos)", value="goblin"),
    app_commands.Choice(name="Savage (Roast Mode)", value="savage"),
    app_commands.Choice(name="Soft Angel (Uplifting)", value="angel"),
    app_commands.Choice(name="Corporate (Clean/Suit)", value="suit"),
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

@bot.tree.command(name="status", description="Check current personality mode")
async def status(interaction: discord.Interaction):
    await interaction.response.send_message(f"Current energy: `{bot.current_mode.upper()}` 🔋")

# ====== RUN ======
bot.run(TOKEN)