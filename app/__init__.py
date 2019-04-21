import aiotg as tg
from app import omdb_api
from app import rus_title
import sqlalchemy
from sqlalchemy import create_engine

omdb = omdb_api.OMDB('')
bot = tg.Bot('')
converter = rus_title.Converter()
engine: sqlalchemy.engine.Engine


def init_omdb(apikey):
    global omdb
    omdb.set_apikey(apikey)


def init_bot(token):
    global bot
    bot.api_token = token


def init_db(db_url):
    global engine
    engine = create_engine(db_url, echo=True)
    from app import models
    models.Base.metadata.create_all(engine)


def init(configs: dict):
    init_omdb(configs['apikey'])
    init_bot(configs['token'])
    init_db(configs['db_url'])
    from app import tg_bot
    from app import models
    from app import database as db
