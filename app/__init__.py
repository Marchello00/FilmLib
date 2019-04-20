import aiotg as tg
from app import omdb_api, rus_title

omdb = None
bot = None
converter = None


def init_omdb(apikey):
    global omdb
    omdb = omdb_api.OMDB(apikey)


def init_bot(token):
    global bot
    bot = tg.Bot(token)


def init(apikey, token):
    global converter
    init_omdb(apikey)
    init_bot(token)
    converter = rus_title.Converter()
