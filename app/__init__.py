import aiotg as tg
from app import omdb_api
from app import rus_title
import aiopg.sa

omdb = omdb_api.OMDB('')
bot = tg.Bot('')
converter = rus_title.Converter()
engine: aiopg.sa.Engine
cleaner = None


sessions = {}


def init_omdb(apikey):
    global omdb
    omdb.set_apikey(apikey)


def init_bot(token):
    global bot
    bot.api_token = token


def init_db(db_url):
    global engine
    engine = aiopg.sa.create_engine(db_url, echo=True)


def init(configs: dict):
    init_omdb(configs['apikey'])
    init_bot(configs['token'])
    init_db(configs['db_url'])
    # Cleaner for future
    # from app import cleenup
    # global cleaner
    # cleaner = cleenup.Cleaner()
    # cleaner.start()
    from app import tg_bot
    from app import models
    from app import database as db
