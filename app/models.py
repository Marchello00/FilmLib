from datetime import datetime
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Film(Base):
    __tablename__ = 'film'

    imdbid = sql.Column(sql.String, primary_key=True)
    year = sql.Column(sql.String)
    poster = sql.Column(sql.String)
    title = sql.Column(sql.String)
    type = sql.Column(sql.String)
    rated = sql.Column(sql.String)
    released = sql.Column(sql.String)
    runtime = sql.Column(sql.String)
    genre = sql.Column(sql.String)
    director = sql.Column(sql.String)
    writer = sql.Column(sql.String)
    actors = sql.Column(sql.String)
    plot = sql.Column(sql.String)
    country = sql.Column(sql.String)
    awards = sql.Column(sql.String)
    ratings = sql.Column(sql.String)
    metascore = sql.Column(sql.String)
    imdbrating = sql.Column(sql.String)
    imdbvotes = sql.Column(sql.String)
    dvd = sql.Column(sql.String)
    boxoffice = sql.Column(sql.String)
    production = sql.Column(sql.String)
    website = sql.Column(sql.String)

    def __repr__(self):
        return '<Film({id}, {title}, {year}, {tp})>'.format(
            id=self.imdbid,
            title=self.title,
            year=self.year,
            tp=self.type
        )


class ChatXFilm(Base):
    __tablename__ = 'chat_x_film'

    chat_id = sql.Column(sql.Integer, primary_key=True)
    film_id = sql.Column(sql.String, sql.ForeignKey('film.imdbid'),
                         primary_key=True)
    watched = sql.Column(sql.Boolean, default=False)
    favourite = sql.Column(sql.Boolean, default=False)
    created_tm = sql.Column(sql.TIMESTAMP,
                            default=datetime.utcnow)
    updated_tm = sql.Column(sql.TIMESTAMP, default=datetime.utcnow,
                            onupdate=datetime.utcnow)

    def __repr__(self):
        return '<ChatXFilm({chat_id}, {film_id}, f:{f}, w:{w})>'.format(
            chat_id=self.chat_id,
            film_id=self.film_id,
            f=self.favourite,
            w=self.watched
        )
