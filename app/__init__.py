import aiotg as tg
from app import omdb_api
from app import rus_title

omdb = omdb_api.OMDB('')
bot = tg.Bot('')
converter = rus_title.Converter()


def init_omdb(apikey):
    global omdb
    omdb.set_apikey(apikey)


def init_bot(token):
    global bot
    bot.api_token = token


def init(apikey, token):
    init_omdb(apikey)
    init_bot(token)
    from app import tg_bot
