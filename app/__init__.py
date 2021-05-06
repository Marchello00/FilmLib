import typing as tp
import aiogram
import aiohttp
import sqlalchemy as sql
from app import omdb_api
from app import rus_title
from app import database
from app import strings
from app.debug import DEBUG  # noqa: ignore

session = aiohttp.ClientSession()
omdb = omdb_api.OMDB('', session)
bot: aiogram.Bot
converter = rus_title.Converter(session)
db: database.DB
dp: aiogram.Dispatcher


def init_omdb(apikey: str) -> None:
    global omdb
    omdb.set_apikey(apikey)


def init_bot(token: str) -> None:
    global bot
    global dp
    bot = aiogram.Bot(token)
    dp = aiogram.Dispatcher(bot)


def init_db(db_url: str) -> None:
    from app.models import Base
    db_url = db_url.replace('postgres://', 'postgresql://')
    engine = sql.create_engine(db_url, echo=True)
    Base.metadata.create_all(engine)
    global db
    db = database.DB(engine)


def init(configs: tp.Dict[str, str], debug: bool = False) -> None:
    global DEBUG
    DEBUG = debug
    init_omdb(configs[strings.APIKEY_CONFIG])
    init_bot(configs[strings.TOKEN_CONFIG])
    init_db(configs[strings.DATABASE_URL_CONFIG])
    from app import models  # noqa: ignore
    from app import tg_bot  # noqa: ignore


def run() -> None:
    global dp
    aiogram.executor.start_polling(dp)
