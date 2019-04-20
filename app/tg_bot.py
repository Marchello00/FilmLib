from app import bot
from aiotg import Chat


@bot.command(r'/echo (.+)')
async def echo(chat: Chat, match):
    return await chat.send_text(match.group(1))

