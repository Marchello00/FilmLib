import aiotg as tg
from app import omdb_api
from app import rus_title
from app import database
import sqlalchemy as sa

omdb = omdb_api.OMDB('')
bot: tg.Bot
converter = rus_title.Converter()
db: database.DB


sessions = {}


def init_omdb(apikey):
    global omdb
    omdb.set_apikey(apikey)


def init_bot(token):
    global bot
    bot = tg.Bot(token)


def init_db(db_url):
    from app.models import Base
    engine = sa.create_engine(db_url, echo=True)
    Base.metadata.create_all(engine)
    global db
    db = database.DB(engine)


def init(configs: dict):
    init_omdb(configs['apikey'])
    init_bot(configs['token'])
    init_db(configs['db_url'])
    from app import tg_bot
    from app import models
    from app import database as db
