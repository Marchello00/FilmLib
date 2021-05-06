import aiogram
import aiohttp
import sqlalchemy as sql
from app.debug import DEBUG
from app import omdb_api
from app import rus_title
from app import database
from app import strings

session = aiohttp.ClientSession()
omdb = omdb_api.OMDB('', session)
bot: aiogram.Bot
converter = rus_title.Converter(session)
db: database.DB
dp: aiogram.Dispatcher


sessions = {}


def init_omdb(apikey):
    global omdb
    omdb.set_apikey(apikey)


def init_bot(token):
    global bot
    global dp
    bot = aiogram.Bot(token)
    dp = aiogram.Dispatcher(bot)


def init_db(db_url: str):
    from app.models import Base
    db_url = db_url.replace('postgres://', 'postgresql://')
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
    from app import models
    from app import tg_bot


def run():
    aiogram.executor.start_polling(dp)
