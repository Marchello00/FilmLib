import json
import re
from collections import defaultdict
from aiotg import Chat
from app.buttons import Buttons
from app import strings
from app import bot, db, converter

film_lists = defaultdict(list)
last_film_msg = defaultdict(int)
buttons_list = defaultdict(Buttons)


@bot.command(r'/echo (.+)')
async def echo(chat: Chat, match):
    return await chat.send_text(match.group(1))


@bot.command(r'/ping')
async def ping(chat: Chat, match):
    return await chat.send_text(strings.PONG)


@bot.command(r'/search (.+)')
async def search_films(chat: Chat, match):
    title = match.group(1)
    return await search_internet(chat, title=title)


@bot.command(r'/searchseries (.+)')
async def search_series(chat: Chat, match):
    title = match.group(1)
    return await search_internet(chat, title=title, m_type=strings.SERIES_TYPE)


@bot.command(r'/search')
async def show_search_help(chat: Chat, match):
    return await chat.send_text(strings.SEARCH_HELP)


@bot.callback(
    r'{callback_query}(\d+)'.format(callback_query=strings.ADDTOLIBRARY_CQ_RE))
async def add_to_lib(chat: Chat, callback_query, match):
    if not check_callback(chat, callback_query):
        return callback_query.answer(text=strings.OLD_MSG)
    index = int(match.group(1))
    film = film_lists[chat.id][index]
    if hasattr(film, 'omdb'):
        film = film.omdb
    if not db.film_in_db(chat.id):
        db.insert_film(film)
    if db.film_in_chat_db(chat.id, film.imdbid):
        return callback_query.answer(text=strings.FILM_ALREADY_IN_DB)
    db.add_dependence(chat_id=chat.id, film_id=film.imdbid)
    film_lists[chat.id][index].inlib = True
    await show_film(chat, index, get_mes_id_from_cq(callback_query))
    return callback_query.answer(text=strings.FILM_ADDED_TO_DB)


@bot.callback(r'{callback_query}(\d+)'.format(
    callback_query=strings.REMOVEFROMLIBRARY_CQ))
async def remove_from_lib(chat: Chat, callback_query, match):
    if not check_callback(chat, callback_query):
        return callback_query.answer(text=strings.OLD_MSG)
    index = int(match.group(1))
    film = film_lists[chat.id][index]
    if hasattr(film, 'omdb'):
        film = film.omdb
    if not db.film_in_db(chat.id):
        db.insert_film(film)
    if not db.film_in_chat_db(chat.id, film.imdbid):
        return callback_query.answer(text=strings.FILM_ALREADY_NOT_IN_DB)
    db.del_dependence(chat_id=chat.id, film_id=film.imdbid)
    film_lists[chat.id][index].inlib = False
    film_lists[chat.id][index].favourite = False
    film_lists[chat.id][index].watched = False
    await show_film(chat, index, get_mes_id_from_cq(callback_query))
    return callback_query.answer(text=strings.FILM_REMOVED_FROM_DB)


@bot.callback(r'{callback_query}(\d+)'.format(callback_query=strings.PREV_CQ))
async def show_prev_film(chat: Chat, callback_query, match):
    if not check_callback(chat, callback_query):
        return callback_query.answer(text=strings.OLD_MSG)
    index = int(match.group(1)) - 1
    await show_film(chat, index, get_mes_id_from_cq(callback_query))
    return callback_query.answer()


@bot.callback(r'{callback_query}(\d+)'.format(callback_query=strings.NEXT_CQ))
async def show_next_film(chat: Chat, callback_query, match):
    if not check_callback(chat, callback_query):
        return callback_query.answer(text=strings.OLD_MSG)
    index = int(match.group(1)) + 1
    await show_film(chat, index, get_mes_id_from_cq(callback_query))
    return callback_query.answer()


@bot.callback(
    r'{callback_query}(\d+)'.format(callback_query=strings.MOREINFO_CQ_RE))
async def show_more(chat: Chat, callback_query, match):
    if not check_callback(chat, callback_query):
        return callback_query.answer(text=strings.OLD_MSG)
    index = int(match.group(1))
    film = film_lists[chat.id][index]
    if hasattr(film, 'omdb'):
        film = film.omdb
    await chat.send_photo(photo=film.poster,
                          caption=get_film_full_desc(film))
    return callback_query.answer()


@bot.callback(
    r'{callback_query}(\d+)'.format(callback_query=strings.ADDTOFAVOURITE_CQ))
async def add_to_favourites(chat: Chat, callback_query, match):
    if not check_callback(chat, callback_query):
        return callback_query.answer(text=strings.OLD_MSG)
    index = int(match.group(1))
    set_favourite(chat, callback_query, index, True)
    return await show_film(chat, index, get_mes_id_from_cq(callback_query))


@bot.callback(r'{callback_query}(\d+)'.format(
    callback_query=strings.REMOVEFROMFAVOURITE_CQ))
async def remove_from_favourites(chat: Chat, callback_query, match):
    if not check_callback(chat, callback_query):
        return callback_query.answer(text=strings.OLD_MSG)
    index = int(match.group(1))
    set_favourite(chat, callback_query, index, False)
    return await show_film(chat, index, get_mes_id_from_cq(callback_query))


@bot.callback(
    r'{callback_query}(\d+)'.format(callback_query=strings.WATCHED_CQ))
async def add_to_watched(chat: Chat, callback_query, match):
    if not check_callback(chat, callback_query):
        return callback_query.answer(text=strings.OLD_MSG)
    index = int(match.group(1))
    set_watched(chat, callback_query, index, True)
    return await show_film(chat, index, get_mes_id_from_cq(callback_query))


@bot.callback(r'{callback_query}(\d+)'.format(
    callback_query=strings.REMOVEFROMWATCHED_CQ))
async def remove_from_watched(chat: Chat, callback_query, match):
    if not check_callback(chat, callback_query):
        return callback_query.answer(text=strings.OLD_MSG)
    index = int(match.group(1))
    set_watched(chat, callback_query, index, False)
    return await show_film(chat, index, get_mes_id_from_cq(callback_query))


@bot.command(r'/myfilms')
async def get_my_films(chat: Chat, match):
    films = db.get_films_by_chat(chat_id=chat.id)
    if not films:
        return await chat.send_text(text=strings.NO_FILMS_IN_YOUR_DB)
    global film_lists, buttons_list
    film_lists[chat.id] = films
    buttons = Buttons()
    buttons.add_info()
    buttons.add_favourites()
    buttons.add_watched()
    buttons.add_lib()
    buttons.add_navigate()
    buttons_list[chat.id] = buttons
    return await show_film(chat, 0)


@bot.command(r'/favourites')
async def get_favourite_films(chat: Chat, match):
    films = db.get_films_by_chat(chat_id=chat.id, favourite=True)
    if not films:
        return await chat.send_text(text=strings.NO_FAVOURITES)
    global film_lists, buttons_list
    film_lists[chat.id] = films
    buttons = Buttons()
    buttons.add_info()
    buttons.add_favourites()
    buttons.add_watched()
    buttons.add_lib()
    buttons.add_navigate()
    buttons_list[chat.id] = buttons
    return await show_film(chat, 0)


@bot.command(r'/unwatched')
async def get_unwatched_films(chat: Chat, match):
    films = db.get_films_by_chat(chat_id=chat.id, watched=False)
    if not films:
        return await chat.send_text(text=strings.NO_UNWATCHED)
    global film_lists, buttons_list
    film_lists[chat.id] = films
    buttons = Buttons()
    buttons.add_info()
    buttons.add_favourites()
    buttons.add_watched()
    buttons.add_lib()
    buttons.add_navigate()
    buttons_list[chat.id] = buttons
    return await show_film(chat, 0)


@bot.command(r'/stop')
async def stop(chat: Chat, match):
    return await chat.send_text(strings.GOODBYE)


@bot.command(r'/start')
async def start(chat: Chat, match):
    return await chat.send_text(
        '{hello}\n{help}'.format(hello=strings.HELLO, help=strings.HELP))


@bot.command(r'/help')
async def helper(chat: Chat, match):
    return await chat.send_text(strings.HELP)


@bot.default
async def default_search(chat: Chat, message):
    title = message['text']
    return await search_internet(chat, title=title, tp2=strings.SERIES_TYPE)


def set_favourite(chat: Chat, callback_query, index, favourite):
    if not check_callback(chat, callback_query):
        return callback_query.answer(text=strings.OLD_MSG)
    global film_lists
    film = film_lists[chat.id][index]
    if hasattr(film, 'omdb'):
        film = film.omdb
    if not db.film_in_db(film.imdbid):
        db.insert_film(film)
    if db.film_in_chat_db(chat.id, film.imdbid, favourite=favourite):
        if favourite:
            return callback_query.answer(
                text=strings.FILM_ALREADY_IN_FAVOURITES)
        else:
            return callback_query.answer(
                text=strings.FILM_ALREADY_NOT_IN_FAVOURITES)
    db.set_favourite(chat_id=chat.id, film_id=film.imdbid,
                     favourite=favourite)
    film_lists[chat.id][index].favourite = favourite
    if favourite:
        return callback_query.answer(text=strings.FILM_ADDED_TO_FAVOURITES)
    else:
        return callback_query.answer(text=strings.FILM_REMOVED_FROM_FAVOURITES)


def set_watched(chat: Chat, callback_query, index, watched):
    if not check_callback(chat, callback_query):
        return callback_query.answer(text=strings.OLD_MSG)
    global film_lists
    film = film_lists[chat.id][index]
    if hasattr(film, 'omdb'):
        film = film.omdb
    if not db.film_in_db(film.imdbid):
        db.insert_film(film)
    if db.film_in_chat_db(chat.id, film.imdbid, watched=watched):
        if watched:
            return callback_query.answer(text=strings.FILM_ALREADY_WATCHED)
        else:
            return callback_query.answer(text=strings.FILM_ALREADY_NOT_WATCHED)
    db.set_watched(chat_id=chat.id, film_id=film.imdbid, watched=watched)
    film_lists[chat.id][index].watched = watched
    if watched:
        return callback_query.answer(text=strings.FILM_ADDED_TO_WATCHED)
    else:
        return callback_query.answer(text=strings.FILM_REMOVED_FROM_WATCHED)


def search_media(title, m_type=strings.MOVIE_TYPE):
    return [film for film in
            converter.get_russian(title, m_type=m_type, lang=None)
            if film.poster]


async def search_internet(chat: Chat, title, m_type=strings.MOVIE_TYPE,
                          limit=10,
                          tp2=None):
    films = search_media(title, m_type=m_type)
    if tp2 is not None:
        films += search_media(title, m_type=tp2)
    cnt = 0
    for film, i in zip(films, range(len(films))):
        film.set_omdb()
        cnt += film.omdb.response == 'True'
        if cnt == limit:
            films = films[:i + 1]
            break
    films = [film for film in films if film.omdb.response == 'True']
    if not films:
        if m_type == strings.MOVIE_TYPE:
            return await chat.send_text(text=strings.FILM_NOT_FOUND)
        else:
            return await chat.send_text(text=strings.SERIES_NOT_FOUND)
    global film_lists, buttons_list
    film_lists[chat.id] = films
    for i, film in enumerate(films):
        inlib = db.film_in_chat_db(chat_id=chat.id,
                                   film_id=film.omdb.imdbid)
        film_lists[chat.id][i].inlib = inlib
        film_lists[chat.id][i].favourite = False
        film_lists[chat.id][i].watched = False
    buttons = Buttons()
    buttons.add_info()
    buttons.add_favourites()
    buttons.add_watched()
    buttons.add_lib()
    buttons.add_navigate()
    buttons_list[chat.id] = buttons
    return await show_film(chat, 0)


def check_callback(chat: Chat, callback_query):
    if get_mes_id_from_cq(callback_query) != last_film_msg[chat.id] or not \
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


def get_mes_id_from_cq(callback_query):
    return callback_query.src['message']['message_id']


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
                                       max_len=len(films),
                                       film=film)
    if not hasattr(film, 'poster') or not film.poster or \
            film.poster == strings.NONE_OMDB:
        film.poster = strings.NO_PICTURE_URL
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
