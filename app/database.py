from app import models as md
import sqlalchemy.orm as saorm
import sqlalchemy as sa
from app.omdb_api import FilmOMDB


class DB:
    __convert = {
        'id': 'imdbid',
        'year': 'year',
        'img': 'poster',
        'title': 'title',
        'type': 'type'
    }
    Session = None

    def __film_from_query(self, q):
        films = []
        for res in q:
            films.append(FilmOMDB({
                self.__convert[key]: value for key, value in
                res.__dict__.items() if
                not callable(key) and not key.startswith('_')
            }))
        return films

    def __init__(self, engine):
        self.Session = saorm.sessionmaker(bind=engine)

    def film_in_db(self, film_id):
        session = self.Session()
        return bool(
            session.query(md.Film).filter(md.Film.imdbid == film_id).all())

    def film_in_chat_db(self, chat_id, film_id, favourite=None, watched=None):
        session = self.Session()
        q = session.query(md.Film).join(md.ChatXFilm).filter(
            sa.and_(md.Film.imdbid == film_id,
                    md.ChatXFilm.chat_id == chat_id))
        if favourite:
            q = q.filter(md.ChatXFilm.favourite == favourite)
        if watched:
            q = q.filter(md.ChatXFilm.watched == watched)
        return bool(q.all())

    def get_films_by_chat(self, chat_id, favourite=None, watched=None):
        session = self.Session()
        q = session.query(md.Film).join(md.ChatXFilm).filter(
            md.ChatXFilm.chat_id == chat_id)
        if favourite is not None:
            q = q.filter(md.ChatXFilm.favourite)
        if watched is not None:
            q = q.filter(md.ChatXFilm.watched == watched)
        return self.__film_from_query(q)

    def insert_film(self, film):
        session = self.Session()
        if not self.film_in_db(film.imdbid):
            data = {key: value for key, value in film.__dict__
                    if key in md.Film.__dict__ and
                    not key.startswith('_') and
                    not callable(key)}
            # ins_film = md.Film(imdbid=film.imdbid, year=film.year,
            #                    poster=film.poster, title=film.title,
            #                    type=film.type)
            ins_film = md.Film(**data)
            session.add(ins_film)
            session.commit()

    def add_dependence(self, chat_id, film_id):
        session = self.Session()
        dep = md.ChatXFilm(chat_id=chat_id, film_id=film_id)
        session.add(dep)
        session.commit()

    def del_dependence(self, chat_id, film_id):
        session = self.Session()
        dep = session.query(md.ChatXFilm).filter(
            sa.and_(md.ChatXFilm.film_id == film_id,
                    md.ChatXFilm.chat_id == chat_id)).first()
        if dep:
            session.delete(dep)
            session.commit()

    def get_films_by_title(self, title, year=None, chat_id=None):
        session = self.Session()
        q = session.query(md.Film).join(md.ChatXFilm).filter(
            md.Film.title == title)
        if year:
            q = q.filter(md.Film.year == year)
        if chat_id:
            q = q.filter(md.ChatXFilm.chat_id == chat_id)
        return self.__film_from_query(q)

    def set_favourite(self, chat_id, film_id, favourite):
        session = self.Session()
        film = session.query(md.ChatXFilm).filter(
            sa.and_(md.ChatXFilm.chat_id == chat_id,
                    md.ChatXFilm.film_id == film_id)
        ).first()
        film.favourite = favourite
        session.commit()

    def set_watched(self, chat_id, film_id, watched):
        session = self.Session()
        film = session.query(md.ChatXFilm).filter(
            sa.and_(md.ChatXFilm.chat_id == chat_id,
                    md.ChatXFilm.film_id == film_id)
        ).first()
        film.watched = watched
        session.commit()
