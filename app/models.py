import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Film(Base):
    __tablename__ = 'film'

    id = sql.Column(sql.String, primary_key=True)
    year = sql.Column(sql.Integer)
    img = sql.Column(sql.String)
    title = sql.Column(sql.String)
    tp = sql.Column(sql.String)

    def __repr__(self):
        return '<Film({id}, {title}, {year}, {tp})>'.format(
            id=self.id,
            title=self.title,
            year=self.year,
            tp=self.tp
        )


class ChatXFim(Base):
    __tablename__ = 'chat_x_film'

    chat_id = sql.Column(sql.Integer, primary_key=True)
    film_id = sql.Column(sql.String, sql.ForeignKey('film.id'),
                         primary_key=True)
    watched = sql.Column(sql.Boolean, default=False)
    favourite = sql.Column(sql.Boolean, default=False)

    def __repr__(self):
        return '<ChatXFilm({chat_id}, {film_id}, favourite:{fav})>'.format(
            chat_id=self.chat_id,
            film_id=self.film_id,
            fav=self.favourite
            )
