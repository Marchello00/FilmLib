from app import bot, db, omdb, converter as cv
from aiotg import Chat
from collections import defaultdict
from app import answers
import json
import re

film_lists = defaultdict(list)
last_film_msg = defaultdict(int)


@bot.command(r'/echo (.+)')
async def echo(chat: Chat, match):
    return await chat.send_text(match.group(1))


@bot.command(r'/search (.+)')
async def search_films(chat: Chat, match):
    title = match.group(1)
    films = [film for film in cv.get_russian(title, lang=None)
             if film.poster]
    for film in films:
        film.set_omdb()
    films = [film for film in films if film.omdb.response == 'True']
    if not films:
        return await chat.send_text(text=answers.FILM_NOT_FOUND)

    global film_lists

    film_lists[chat.id] = films
    return await show_film(chat, 0)


@bot.callback(r'\+(.+)')
def add_to_favourite(chat: Chat, cq, match):
    index = int(match.group(1))
    film = film_lists[chat.id][index]
    if db.film_in_chat_db(chat.id, film.imdbid, favourite=True):
        return cq.answer(text=answers.FILM_ALREADY_IN_DB,
                         show_alert='true')
        # return bot.api_call('answerCallbackQuery',
        #                     text=answers.FILM_ALREADY_IN_DB,
        #                     show_alert='true')
    if not db.film_in_db(chat.id):
        db.insert_film(film)
    db.add_dependence(chat_id=chat.id, film_id=film.imdbid)
    return cq.answer(text=answers.FILM_ADDED_TO_DB,
                     ahow_alert='true')
    # return bot.api_call('answerCallbackQuery',
    #                     text=answers.FILM_ADDED_TO_DB,
    #                     show_alert='true')


@bot.callback(r'<(.+)')
async def show_prev_film(chat: Chat, cq, match):
    if cq['message'] != last_film_msg[chat.id]:
        return cq.answer()
    index = int(match.group(1)) - 1
    return await show_film(chat, index)


@bot.callback(r'>(.+)')
async def show_next_film(chat: Chat, cq, match):
    index = int(match.group(1)) + 1
    return await show_film(chat, index)


@bot.callback(r'\?(.+)')
async def show_more(chat: Chat, cq, match):
    index = int(match.group(1))
    film = film_lists[chat.id][index].omdb
    return await chat.send_photo(photo=film.poster,
                                 caption=get_film_full_desc(film))


def get_film_desc(film):
    return answers.SHORT_DESC.format(
        title=film.title,
        year=film.year,
        plot=film.plot
    )


def get_film_full_desc(film):
    dct = {}
    for pattern in re.findall(r'{(\w+)}', answers.FULL_DESC):
        if not hasattr(film, pattern):
            dct.update({pattern: answers.UNKNOWN})
        else:
            dct.update({pattern: film.__getattr__(pattern)})
    return answers.FULL_DESC.format(
        **dct
    )


def get_mes_id(msg):
    if msg['ok']:
        return msg['result']['message_id']
    return None


def get_inline_films(chat: Chat, index):
    page_buttons = []
    if index > 0:
        page_buttons.append({
            'text': answers.PREV_FILM_BUTTON,
            'callback_data': '<{index}'.format(index=index)
        })
    if index < len(film_lists[chat.id]) - 1:
        page_buttons.append({
            'text': answers.NEXT_FILM_BUTTON,
            'callback_data': '>{index}'.format(index=index)
        })
    keyboard = [
        # 1-st row
        [
            {
                'text': answers.MORE_INFO_BUTTON,
                'callback_data': '?{index}'.format(index=index)
            }
        ],
        # 2-nd row
        [
            {
                'text': answers.ADD_TO_FILMLIB_BUTTON,
                'callback_data': '+{index}'.format(index=index)
            }
        ]
    ]
    if page_buttons:
        keyboard.append(page_buttons)
    markup = {
        'type': 'InlineKeyboardMarkup',
        'inline_keyboard': keyboard
    }
    return markup


def input_media_photo(poster, caption):
    inlinemedia = {
        'type': 'photo',
        'media': poster,
        'caption': caption
    }
    return inlinemedia


async def show_film(chat: Chat, index, mes_id=None):
    film = film_lists[chat.id][index]
    if not mes_id:
        msg = await chat.send_photo(photo=film.poster,
                                    caption=get_film_desc(film))
        mes_id = get_mes_id(msg)
        await chat.edit_reply_markup(mes_id,
                                     markup=get_inline_films(chat, index))
        last_film_msg[chat.id] = mes_id
    else:
        bot.api_call('editMessageMedia', chat_id=chat.id, message_id=mes_id,
                     media=json.dumps(
                         input_media_photo(film.poster, get_film_desc(film))),
                     reply_markup=json.dumps(
                         get_inline_films(chat, index)
                     ))
