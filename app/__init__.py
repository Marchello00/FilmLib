import aiotg as tg
from app import omdb_api as om

omdb = None
bot = None


def init_omdb(apikey):
    global omdb
    omdb = om.OMDB(apikey)


def init_bot(token):
    global bot
    bot = tg.Bot(token)
