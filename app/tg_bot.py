import json
import re
import asyncio
from app.search_to_watch import search_where_to_watch
from collections import defaultdict
from aiogram import types
from app.buttons import Buttons
from app import strings
from app import db, dp, converter

film_lists = defaultdict(list)
last_film_msg = defaultdict(int)
buttons_list = defaultdict(Buttons)


@dp.message_handler(commands=['echo'])
async def echo(message: types.Message):
    await message.reply(message.text)


@dp.message_handler(commands=['ping'])
async def ping(message: types.Message):
    await message.reply('Pong!')


@dp.message_handler(commands=['search'])
async def search_films(message: types.Message):
    if not message.get_args():
        await message.reply(strings.SEARCH_HELP)
        return
    await search_internet(message.get_args(), message)


@dp.message_handler(commands=['searchseries'])
async def search_series(message: types.Message):
    if not message.get_args():
        await message.reply(strings.SEARCHSERIES_HELP)
        return
    return await search_internet(message.get_args(), message,
                                 m_type=strings.SERIES_TYPE)


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith(strings.ADDTOLIBRARY_CQ))
async def add_to_lib(callback_query: types.CallbackQuery):
    if not check_callback(callback_query):
        await callback_query.answer(text=strings.OLD_MSG)
        return
    chat = callback_query.message.chat
    index = int(callback_query.data[len(strings.ADDTOLIBRARY_CQ):])
    film = film_lists[chat.id][index]
    if hasattr(film, 'omdb'):
        film = film.omdb
    if not db.film_in_db(chat.id):
        db.insert_film(film)
    if db.film_in_chat_db(chat.id, film.imdbid):
        return callback_query.answer(text=strings.FILM_ALREADY_IN_DB)
    db.add_dependence(chat_id=chat.id, film_id=film.imdbid)
    film_lists[chat.id][index].inlib = True
    await show_film(callback_query.message, index,
                    callback_query.message.message_id)
    await callback_query.answer(text=strings.FILM_ADDED_TO_DB)


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith(strings.REMOVEFROMLIBRARY_CQ))
async def remove_from_lib(callback_query: types.CallbackQuery):
    if not check_callback(callback_query):
        await callback_query.answer(text=strings.OLD_MSG)
        return
    chat = callback_query.message.chat
    index = int(callback_query.data[len(strings.REMOVEFROMLIBRARY_CQ):])
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
    await show_film(callback_query.message, index,
                    callback_query.message.message_id)
    await callback_query.answer(text=strings.FILM_REMOVED_FROM_DB)


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith(strings.PREV_CQ))
async def show_prev_film(callback_query: types.CallbackQuery):
    if not check_callback(callback_query):
        await callback_query.answer(text=strings.OLD_MSG)
        return
    index = int(callback_query.data[len(strings.PREV_CQ):]) - 1
    await show_film(callback_query.message, index,
                    callback_query.message.message_id)
    await callback_query.answer()


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith(strings.NEXT_CQ))
async def show_next_film(callback_query: types.CallbackQuery):
    if not check_callback(callback_query):
        await callback_query.answer(text=strings.OLD_MSG)
        return
    index = int(callback_query.data[len(strings.NEXT_CQ):]) + 1
    await show_film(callback_query.message, index,
                    callback_query.message.message_id)
    await callback_query.answer()


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith(strings.MOREINFO_CQ))
async def show_more(callback_query: types.CallbackQuery):
    if not check_callback(callback_query):
        await callback_query.answer(text=strings.OLD_MSG)
        return
    index = int(callback_query.data[len(strings.MOREINFO_CQ):])
    film = film_lists[callback_query.message.chat.id][index]
    if hasattr(film, 'omdb'):
        film = film.omdb
    btns = Buttons()
    btns.add_watch()
    btns.add_share()
    markup = btns.get(film=film)
    desc = get_film_full_desc(film)
    if len(desc) > 1000:
        desc = desc[:997] + '...'
    await dp.bot.send_photo(chat_id=callback_query.message.chat.id,
                            photo=film.poster,
                            caption=desc,
                            reply_markup=json.dumps(markup)
                            )
    await callback_query.answer()


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith(strings.ADDTOFAVOURITE_CQ))
async def add_to_favourites(callback_query: types.CallbackQuery):
    if not check_callback(callback_query):
        await callback_query.answer(text=strings.OLD_MSG)
        return
    index = int(callback_query.data[len(strings.ADDTOFAVOURITE_CQ):])
    await set_favourite(callback_query.message.chat, callback_query, index,
                        True)
    await show_film(callback_query.message, index,
                    callback_query.message.message_id)
    await callback_query.answer()


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith(strings.REMOVEFROMFAVOURITE_CQ))
async def remove_from_favourites(callback_query: types.CallbackQuery):
    if not check_callback(callback_query):
        await callback_query.answer(text=strings.OLD_MSG)
        return
    index = int(callback_query.data[len(strings.REMOVEFROMFAVOURITE_CQ):])
    await set_favourite(callback_query.message.chat, callback_query, index,
                        False)
    await show_film(callback_query.message, index,
                    callback_query.message.message_id)
    await callback_query.answer()


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith(strings.WATCHED_CQ))
async def add_to_watched(callback_query: types.CallbackQuery):
    if not check_callback(callback_query):
        await callback_query.answer(text=strings.OLD_MSG)
        return
    index = int(callback_query.data[len(strings.WATCHED_CQ):])
    await set_watched(callback_query.message.chat, callback_query, index, True)
    await show_film(callback_query.message, index,
                    callback_query.message.message_id)
    await callback_query.answer()


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith(strings.REMOVEFROMWATCHED_CQ))
async def remove_from_watched(callback_query: types.CallbackQuery):
    if not check_callback(callback_query):
        await callback_query.answer(text=strings.OLD_MSG)
        return
    index = int(callback_query.data[len(strings.REMOVEFROMWATCHED_CQ):])
    await set_watched(callback_query.message.chat, callback_query, index,
                      False)
    await show_film(callback_query.message, index,
                    callback_query.message.message_id)
    await callback_query.answer()


@dp.message_handler(commands=['myfilms'])
async def get_my_films(message: types.Message):
    chat = message.chat
    films = db.get_films_by_chat(chat_id=chat.id)
    if not films:
        await message.reply(text=strings.NO_FILMS_IN_YOUR_DB)
        return
    global film_lists, buttons_list
    film_lists[chat.id] = films
    buttons = Buttons()
    buttons.add_info()
    buttons.add_favourites()
    buttons.add_watched()
    buttons.add_lib()
    buttons.add_navigate()
    buttons_list[chat.id] = buttons
    return await show_film(message, 0)


@dp.message_handler(commands=['favourites'])
async def get_favourite_films(message: types.Message):
    chat = message.chat
    films = db.get_films_by_chat(chat_id=chat.id, favourite=True)
    if not films:
        await message.reply(text=strings.NO_FAVOURITES)
        return
    global film_lists, buttons_list
    film_lists[chat.id] = films
    buttons = Buttons()
    buttons.add_info()
    buttons.add_favourites()
    buttons.add_watched()
    buttons.add_lib()
    buttons.add_navigate()
    buttons_list[chat.id] = buttons
    return await show_film(message, 0)


@dp.message_handler(commands=['unwatched'])
async def get_unwatched_films(message: types.Message):
    chat = message.chat
    films = db.get_films_by_chat(chat_id=chat.id, watched=False)
    if not films:
        await message.reply(text=strings.NO_UNWATCHED)
        return
    global film_lists, buttons_list
    film_lists[chat.id] = films
    buttons = Buttons()
    buttons.add_info()
    buttons.add_favourites()
    buttons.add_watched()
    buttons.add_lib()
    buttons.add_navigate()
    buttons_list[chat.id] = buttons
    await show_film(message, 0)


@dp.message_handler(commands=['stop'])
async def stop(message: types.Message):
    await message.reply(strings.GOODBYE)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(
        '{hello}\n{help}'.format(hello=strings.HELLO, help=strings.HELP))


@dp.message_handler(commands=['help'])
async def helper(message: types.Message):
    await message.reply(strings.HELP)


@dp.message_handler()
async def default_search(message: types.Message):
    await search_internet(message.text, message, tp2=strings.SERIES_TYPE)


async def set_favourite(chat: types.Chat, callback_query: types.CallbackQuery,
                        index,
                        favourite):
    if not check_callback(callback_query):
        await callback_query.answer(text=strings.OLD_MSG)
        return
    global film_lists
    film = film_lists[chat.id][index]
    if hasattr(film, 'omdb'):
        film = film.omdb
    if not db.film_in_db(film.imdbid):
        db.insert_film(film)
    if db.film_in_chat_db(chat.id, film.imdbid, favourite=favourite):
        if favourite:
            await callback_query.answer(
                text=strings.FILM_ALREADY_IN_FAVOURITES)
        else:
            await callback_query.answer(
                text=strings.FILM_ALREADY_NOT_IN_FAVOURITES)
        return
    db.set_favourite(chat_id=chat.id, film_id=film.imdbid,
                     favourite=favourite)
    film_lists[chat.id][index].favourite = favourite
    if favourite:
        await callback_query.answer(text=strings.FILM_ADDED_TO_FAVOURITES)
    else:
        await callback_query.answer(text=strings.FILM_REMOVED_FROM_FAVOURITES)


async def set_watched(chat: types.Chat, callback_query: types.CallbackQuery,
                      index,
                      watched):
    if not check_callback(callback_query):
        await callback_query.answer(text=strings.OLD_MSG)
        return
    global film_lists
    film = film_lists[chat.id][index]
    if hasattr(film, 'omdb'):
        film = film.omdb
    if not db.film_in_db(film.imdbid):
        db.insert_film(film)
    if db.film_in_chat_db(chat.id, film.imdbid, watched=watched):
        if watched:
            await callback_query.answer(text=strings.FILM_ALREADY_WATCHED)
        else:
            await callback_query.answer(text=strings.FILM_ALREADY_NOT_WATCHED)
        return
    db.set_watched(chat_id=chat.id, film_id=film.imdbid, watched=watched)
    film_lists[chat.id][index].watched = watched
    if watched:
        await callback_query.answer(text=strings.FILM_ADDED_TO_WATCHED)
    else:
        await callback_query.answer(text=strings.FILM_REMOVED_FROM_WATCHED)


async def search_media(title, m_type=strings.MOVIE_TYPE):
    return [film for film in
            await converter.get_russian(title, m_type=m_type, lang=None)
            if film.poster]


async def search_internet(title: str,
                          message: types.Message,
                          m_type=strings.MOVIE_TYPE,
                          limit=10,
                          tp2=None):
    films = await search_media(title, m_type=m_type)
    chat = message.chat
    if tp2 is not None:
        films += await search_media(title, m_type=tp2)
    cnt = 0
    for film, i in zip(films, range(len(films))):
        await film.set_omdb()
        cnt += film.omdb.response == 'True'
        if cnt == limit:
            films = films[:i + 1]
            break
    films = [film for film in films if film.omdb.response == 'True']
    if not films:
        if m_type == strings.MOVIE_TYPE:
            await message.reply(text=strings.FILM_NOT_FOUND)
        else:
            await message.reply(text=strings.SERIES_NOT_FOUND)
        return
    global film_lists, buttons_list
    watch_links = await asyncio.gather(
        *[search_where_to_watch(film.title) for film in films])
    for film, link in zip(films, watch_links):
        film.watch_link = link
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
    buttons.add_watch()
    buttons.add_navigate()
    buttons_list[chat.id] = buttons
    return await show_film(message, 0)


def check_callback(callback_query: types.CallbackQuery):
    chat = callback_query.message.chat
    return bool(
        callback_query.message.message_id == last_film_msg[chat.id]
        and film_lists[chat.id]
    )


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
            if len(attr) > 200:
                attr = attr[:197] + '...'
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
    return {
        'type': 'photo',
        'media': poster,
        'caption': caption
    }


async def show_film(message: types.Message, index, msg_id=None):
    films = film_lists[message.chat.id]
    film = films[index]
    if not hasattr(film, 'watch_link'):
        film.watch_link = await search_where_to_watch(film.title)
    markup = buttons_list[message.chat.id].get(index=index,
                                               max_len=len(films),
                                               film=film)
    if hasattr(film, 'omdb'):
        film = film.omdb
    if not hasattr(film, 'poster') or not film.poster or \
            film.poster == strings.NONE_OMDB:
        film.poster = strings.NO_PICTURE_URL
    if msg_id is None:
        resp = await dp.bot.send_photo(chat_id=message.chat.id,
                                       photo=film.poster,
                                       caption=get_film_desc(film),
                                       reply_markup=json.dumps(markup))
        last_film_msg[message.chat.id] = resp.message_id
    else:
        await dp.bot.edit_message_media(chat_id=message.chat.id,
                                        message_id=msg_id,
                                        media=json.dumps(
                                            input_media_photo(film.poster,
                                                              get_film_desc(
                                                                  film))),
                                        reply_markup=json.dumps(markup))
