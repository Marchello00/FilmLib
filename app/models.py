import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Film(Base):
    __tablename__ = 'film'

    imdbid = sa.Column(sa.String, primary_key=True)
    year = sa.Column(sa.Integer)
    poster = sa.Column(sa.String)
    title = sa.Column(sa.String)
    type = sa.Column(sa.String)
    rated = sa.Column(sa.String)
    released = sa.Column(sa.String)
    runtime = sa.Column(sa.String)
    genre = sa.Column(sa.String)
    director = sa.Column(sa.String)
    writer = sa.Column(sa.String)
    actors = sa.Column(sa.String)
    plot = sa.Column(sa.String)
    country = sa.Column(sa.String)
    awards = sa.Column(sa.String)
    ratings = sa.Column(sa.String)
    metascore = sa.Column(sa.String)
    imdbrating = sa.Column(sa.String)
    imdbvotes = sa.Column(sa.String)
    dvd = sa.Column(sa.String)
    boxoffice = sa.Column(sa.String)
    production = sa.Column(sa.String)
    website = sa.Column(sa.String)

    def __repr__(self):
        return '<Film({id}, {title}, {year}, {tp})>'.format(
            id=self.id,
            title=self.title,
            year=self.year,
            tp=self.tp
        )


class ChatXFilm(Base):
    __tablename__ = 'chat_x_film'

    chat_id = sa.Column(sa.Integer, primary_key=True)
    film_id = sa.Column(sa.String, sa.ForeignKey('film.imdbid'),
                        primary_key=True)
    watched = sa.Column(sa.Boolean, default=False)
    favourite = sa.Column(sa.Boolean, default=False)

    def __repr__(self):
        return '<ChatXFilm({chat_id}, {film_id}, favourite:{fav})>'.format(
            chat_id=self.chat_id,
            film_id=self.film_id,
            fav=self.favourite
            )
