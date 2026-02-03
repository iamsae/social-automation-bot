import os
import asyncio
import discord
import feedparser
from discord.ext import commands
from discord import app_commands
from xai import Client

# ====== ENV CONFIG ======
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))
GROK_API_KEY = os.getenv("GROK_API_KEY")

grok = Client(api_key=GROK_API_KEY)

# ====== VIBE LORE & PERSONALITY MAP ======
# This defines the "brain" for each mode
VIBE_BASE_LORE = (
    "You are the Vibe Digital Agent, part of an ecosystem of stylized car visuals, "
    "neon aesthetics, and underground music. You know about NORTH26 remixes and DX thumbnails."
)

PERSONALITIES = {
    "vibe": f"{VIBE_BASE_LORE} Tone: Default, chill, neon-coded, rhythmic.",
    "goblin": f"{VIBE_BASE_LORE} Tone: Unhinged Gen Z energy, max brainrot, chaotic, funny.",
    "angel": f"{VIBE_BASE_LORE} Tone: Soft, uplifting, aesthetic, pure positive vibes.",
    "savage": f"{VIBE_BASE_LORE} Tone: Savage, roast-heavy, high-key judgmental about mid music.",
    "suit": f"{VIBE_BASE_LORE} Tone: Clean, corporate, professional, overly polite."
}

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="s!", intents=intents)
        # Default personality
        self.current_mode = "vibe"

    async def setup_hook(self):
        # Syncs the slash commands to your server
        await self.tree.sync()

bot = MyBot()

# ====== SLASH COMMANDS ======

@bot.tree.command(name="mode", description="Switch the bot's personality vibe")
@app_commands.describe(vibe="Choose the new energy for the bot")
@app_commands.choices(vibe=[
    app_commands.Choice(name="Default Vibe (Neon/Chill)", value="vibe"),
    app_commands.Choice(name="Unhinged (Gen Z Chaos)", value="goblin"),
    app_commands.Choice(name="Soft Angel (Uplifting)", value="angel"),
    app_commands.Choice(name="Savage (Roast Mode)", value="savage"),
    app_commands.Choice(name="Corporate (Clean/Suit)", value="suit"),
])
async def mode(interaction: discord.Interaction, vibe: app_commands.Choice[str]):
    bot.current_mode = vibe.value
    responses = {
        "vibe": "Vibe shifted. Neon lights on. 🌌",
        "goblin": "Mode: GOBLIN. No cap, let's get weird. 💀",
        "angel": "Energy purified. Sending love. ✨",
        "savage": "Locked in. Don't cry when I roast your fit. 🔨",
        "suit": "Understood. I shall maintain professional decorum. 💼"
    }
    await interaction.response.send_message(responses[vibe.value])

@bot.tree.command(name="status", description="Check which personality is active")
async def status(interaction: discord.Interaction):
    mode_name = bot.current_mode.capitalize()
    await interaction.response.send_message(f"Current Vibe: **{mode_name}** 🔋")

@bot.tree.command(name="chat", description="Chat with the bot in its current personality")
async def chat(interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    
    try:
        # Get the specific system prompt based on the chosen mode
        system_prompt = PERSONALITIES.get(bot.current_mode, PERSONALITIES["vibe"])
        
        response = grok.chat.completions.create(
            model="grok-2-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        
        reply = response.choices[0].message["content"]
        await interaction.followup.send(reply)
        
    except Exception as e:
        await interaction.followup.send(f"Brain fog... 💀 `{e}`")

# ====== RUN ======
bot.run(TOKEN)