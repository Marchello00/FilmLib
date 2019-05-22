import aiotg as tg
import sqlalchemy as sql
from app import omdb_api
from app import rus_title
from app import database
from app import strings

omdb = omdb_api.OMDB('')
bot: tg.Bot
converter = rus_title.Converter()
db: database.DB
DEBUG = False


sessions = {}


def init_omdb(apikey):
    global omdb
    omdb.set_apikey(apikey)


def init_bot(token):
    global bot
    bot = tg.Bot(token)


def init_db(db_url):
    from app.models import Base
    engine = sql.create_engine(db_url, echo=True)
    Base.metadata.create_all(engine)
    global db
    db = database.DB(engine)


def init(configs: dict, debug=False):
    global DEBUG
    DEBUG = debug
    init_omdb(configs[strings.APIKEY_CONFIG])
    init_bot(configs[strings.TOKEN_CONFIG])
    init_db(configs[strings.DATABASE_URL_CONFIG])
    if not DEBUG:
        from app import tg_bot
        from app import models
