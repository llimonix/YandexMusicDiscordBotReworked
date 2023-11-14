from bot.core import Bot
from bot.cfg import token
import bot.interactions
import bot.music
import discord

@Bot.event
async def on_ready():
    await Bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/play"))
    print("Бот запущен!")

Bot.run(token)
