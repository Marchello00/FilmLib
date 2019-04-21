from app import engine
from app import models
import aiopg.sa
import sqlalchemy as sa


async def get_films(self, chat_id, engine: aiopg.sa.Engine):
    async with engine.acquire() as conn:
        film_table = models.Film.__table__
        cxf_table = models.ChatXFim.__table__
        # conn.execute(film_table.join(cxf_table).select())

