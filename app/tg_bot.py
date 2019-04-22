from app import bot, db, omdb, converter as cv
from aiotg import Chat


def get_film_desc(film):
    return "{title}({year})\n{plot}".format(
        title=film.title,
        year=film.year,
        plot=film.plot
    )


@bot.command(r'/echo (.+)')
async def echo(chat: Chat, match):
    return await chat.send_text(match.group(1))


@bot.command(r'/search (.+)')
async def search_films(chat: Chat, match):
    title = match.group(1)
    films = cv.get_russian(title)
    for film in films:
        chat.send_photo(photo=film.url, caption=get_film_desc(film))
