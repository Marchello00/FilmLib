from app import bot, db, converter as cv
from aiotg import Chat
from collections import defaultdict
from app import strings
import json
import re
from app.buttons import Buttons

film_lists = defaultdict(list)
last_film_msg = defaultdict(int)
buttons_list = defaultdict(Buttons)


@bot.command(r'/echo (.+)')
async def echo(chat: Chat, match):
    return await chat.send_text(match.group(1))


@bot.command(r'/ping')
async def ping(chat: Chat, match):
    return await chat.send_text('Pong!')


@bot.command(r'/search (.+)')
async def search_films(chat: Chat, match):
    title = match.group(1)
    return await search_internet(chat, title=title)


@bot.command(r'/searchseries (.+)')
async def search_series(chat: Chat, match):
    title = match.group(1)
    return await search_internet(chat, title=title, tp='tv')


@bot.callback(r'{cq}(\d+)'.format(cq=strings.ADDTOLIBRARY_CQ_RE))
def add_to_myfilmdb(chat: Chat, cq, match):
    if not check_callback(chat, cq):
        return cq.answer(text=strings.OLD_MSG)
    index = int(match.group(1))
    film = film_lists[chat.id][index]
    if not db.film_in_db(chat.id):
        db.insert_film(film.omdb)
    if db.film_in_chat_db(chat.id, film.omdb.imdbid):
        return cq.answer(text=strings.FILM_ALREADY_IN_DB)
    db.add_dependence(chat_id=chat.id, film_id=film.omdb.imdbid)
    return cq.answer(text=strings.FILM_ADDED_TO_DB)


@bot.callback(r'{cq}(\d+)'.format(cq=strings.PREV_CQ))
async def show_prev_film(chat: Chat, cq, match):
    if not check_callback(chat, cq):
        return cq.answer(text=strings.OLD_MSG)
    index = int(match.group(1)) - 1
    await show_film(chat, index, get_mes_id_from_cq(cq))
    return cq.answer()


@bot.callback(r'{cq}(\d+)'.format(cq=strings.NEXT_CQ))
async def show_next_film(chat: Chat, cq, match):
    if not check_callback(chat, cq):
        return cq.answer(text=strings.OLD_MSG)
    index = int(match.group(1)) + 1
    await show_film(chat, index, get_mes_id_from_cq(cq))
    return cq.answer()


@bot.callback(r'{cq}(\d+)'.format(cq=strings.MOREINFO_CQ_RE))
async def show_more(chat: Chat, cq, match):
    if not check_callback(chat, cq):
        return cq.answer(text=strings.OLD_MSG)
    index = int(match.group(1))
    if hasattr(film_lists[chat.id][index], 'omdb'):
        film = film_lists[chat.id][index].omdb
    else:
        film = film_lists[chat.id][index]
    await chat.send_photo(photo=film.poster,
                          caption=get_film_full_desc(film))
    return cq.answer()


@bot.callback(r'{cq}(\d+)'.format(cq=strings.ADDTOFAVOURITE_CQ))
async def add_to_favourites(chat: Chat, cq, match):
    index = int(match.group(1))
    return set_favourite(chat, cq, index, True)


@bot.callback(r'{cq}(\d+)'.format(cq=strings.REMOVEFROMFAVOURITE_CQ))
async def remove_from_favourites(chat: Chat, cq, match):
    index = int(match.group(1))
    return set_favourite(chat, cq, index, False)


@bot.callback(r'{cq}(\d+)'.format(cq=strings.WATCHED_CQ))
async def add_to_watched(chat: Chat, cq, match):
    index = int(match.group(1))
    return set_watched(chat, cq, index, True)


@bot.callback(r'{cq}(\d+)'.format(cq=strings.REMOVEFROMWATCHED_CQ))
async def remove_from_watched(chat: Chat, cq, match):
    index = int(match.group(1))
    return set_watched(chat, cq, index, False)


@bot.command(r'/myfilms')
async def get_my_films(chat: Chat, match):
    films = db.get_films_by_chat(chat_id=chat.id)
    if not films:
        return await chat.send_text(text=strings.NO_FILMS_IN_YOUR_DB)
    global film_lists, buttons_list
    film_lists[chat.id] = films
    b = Buttons()
    b.add_info()
    b.add_favourites()
    b.add_watched()
    buttons_list[chat.id] = b
    return await show_film(chat, 0)


def set_favourite(chat: Chat, cq, index, favourite):
    if not check_callback(chat, cq):
        return cq.answer(text=strings.OLD_MSG)
    film = film_lists[chat.id][index]
    if not db.film_in_db(film.omdb.imdbid):
        db.insert_film(film.omdb)
    if db.film_in_chat_db(chat.id, film.omdb.imdbid, favourite=favourite):
        if favourite:
            return cq.answer(text=strings.FILM_ALREADY_IN_FAVOURITES)
        else:
            return cq.answer(text=strings.FILM_ALREADY_NOT_IN_FAVOURITES)
    if not db.film_in_chat_db(chat.id, film.omdb.imdbid):
        db.add_dependence(chat_id=chat.id, film_id=film.omdb.imdbid)
    db.set_favourite(chat_id=chat.id, film_id=film.omdb.imdbid,
                     favourite=favourite)
    if favourite:
        return cq.answer(text=strings.FILM_ADDED_TO_FAVOURITES)
    else:
        return cq.answer(text=strings.FILM_REMOVED_FROM_FAVOURITES)


def set_watched(chat: Chat, cq, index, watched):
    if not check_callback(chat, cq):
        return cq.answer(text=strings.OLD_MSG)
    film = film_lists[chat.id][index]
    if not db.film_in_db(film.omdb.imdbid):
        db.insert_film(film.omdb)
    if db.film_in_chat_db(chat.id, film.omdb.imdbid, watched=watched):
        if watched:
            return cq.answer(text=strings.FILM_ALREADY_WATCHED)
        else:
            return cq.answer(text=strings.FILM_ALREADY_NOT_WATCHED)
    if not db.film_in_chat_db(chat.id, film.omdb.imdbid):
        db.add_dependence(chat_id=chat.id, film_id=film.omdb.imdbid)
    db.set_watched(chat_id=chat.id, film_id=film.omdb.imdbid, watched=watched)
    if watched:
        return cq.answer(text=strings.FILM_ADDED_TO_WATCHED)
    else:
        return cq.answer(text=strings.FILM_REMOVED_FROM_WATCHED)


def search_media(title, tp='movie'):
    return [film for film in cv.get_russian(title, tp=tp, lang=None)
            if film.poster]


async def search_internet(chat: Chat, title, tp='movie'):
    films = search_media(title, tp=tp)
    for film in films:
        film.set_omdb()
    films = [film for film in films if film.omdb.response == 'True']
    if not films:
        return await chat.send_text(text=strings.FILM_NOT_FOUND)
    global film_lists, buttons_list
    film_lists[chat.id] = films
    b = Buttons()
    b.add_info()
    b.add_lib()
    buttons_list[chat.id] = b
    return await show_film(chat, 0)


def check_callback(chat: Chat, cq):
    if get_mes_id_from_cq(cq) != last_film_msg[chat.id] or not \
            film_lists[chat.id]:
        return False
    return True


def get_film_desc(film):
    return strings.SHORT_DESC.format(
        title=film.title,
        year=film.year,
        plot=film.plot
    )


def get_film_full_desc(film):
    dct = {}
    for pattern in re.findall(r'{(\w+)}', strings.FULL_DESC):
        if not hasattr(film, pattern):
            dct.update({pattern: strings.UNKNOWN})
        else:
            attr = film.__getattr__(pattern)
            if not attr:
                attr = strings.UNKNOWN
            dct.update({pattern: attr})
    return strings.FULL_DESC.format(
        **dct
    )


def get_mes_id_from_cq(cq):
    return cq.src['message']['message_id']


def get_mes_id_from_resp(msg):
    if msg['ok']:
        return msg['result']['message_id']
    return None


def input_media_photo(poster, caption):
    inlinemedia = {
        'type': 'photo',
        'media': poster,
        'caption': caption
    }
    return inlinemedia


async def show_film(chat: Chat, index, mes_id=None):
    films = film_lists[chat.id]
    film = films[index]
    markup = buttons_list[chat.id].get(index=index,
                                       max_len=len(film_lists[chat.id]))
    if not mes_id:
        msg = await chat.send_photo(photo=film.poster,
                                    caption=get_film_desc(film),
                                    reply_markup=json.dumps(markup))
        mes_id = get_mes_id_from_resp(msg)
        last_film_msg[chat.id] = mes_id
    else:
        bot.api_call('editMessageMedia', chat_id=chat.id, message_id=mes_id,
                     media=json.dumps(
                         input_media_photo(film.poster, get_film_desc(film))),
                     reply_markup=json.dumps(markup))
