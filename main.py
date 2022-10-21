import os
import nextcord
import wavelink

from utility import TOKEN
from nextcord.ext import commands

from music_cog import music_cog

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='m!', intents=intents)

def setup(bot):
    bot.add_cog(music_cog(bot))

@bot.event
async def on_ready():
    bot.add_cog(music_cog(bot))
    print("1/1 Music Cog loaded!")
    print("Bot is up and ready!")

bot.run(TOKEN)