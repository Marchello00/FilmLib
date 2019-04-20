import aiotg as tg
from app import omdb_api

omdb = omdb_api.OMDB('')
bot = tg.Bot('')

from app import rus_title

converter = rus_title.Converter()


def init_omdb(apikey):
    global omdb
    omdb.set_apikey(apikey)


def init_bot(token):
    global bot
    bot.api_token = token


def init(apikey, token):
    global converter
    init_omdb(apikey)
    init_bot(token)
