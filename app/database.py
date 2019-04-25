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

    @staticmethod
    def __film_from_query(q, inlib=False):
        films = []
        for film, watched, favourite, ct in q:
            films.append(FilmOMDB({
                key: value for key, value in
                film.__dict__.items() if
                not callable(key) and not key.startswith('_')
            }))
            films[-1].favourite = favourite
            films[-1].watched = watched
            films[-1].inlib = inlib
            films[-1].created_tm = ct
        films.sort(key=lambda x: x.created_tm, reverse=True)
        return films

    def __init__(self, engine):
        self.Session = saorm.sessionmaker(bind=engine)

    def film_in_db(self, film_id):
        film_id = str(film_id)
        session = self.Session()
        ret = bool(
            session.query(md.Film.imdbid).filter(
                md.Film.imdbid == film_id).all())
        session.close()
        return ret

    def film_in_chat_db(self, chat_id, film_id, favourite=None, watched=None):
        film_id = str(film_id)
        session = self.Session()
        q = session.query(md.ChatXFilm).filter(
            sa.and_(md.ChatXFilm.film_id == film_id,
                    md.ChatXFilm.chat_id == chat_id))
        if favourite is not None:
            q = q.filter(md.ChatXFilm.favourite == favourite)
        if watched is not None:
            q = q.filter(md.ChatXFilm.watched == watched)
        ret = bool(q.all())
        session.close()
        return ret

    def get_films_by_chat(self, chat_id, favourite=None, watched=None):
        session = self.Session()
        q = session.query(md.Film, md.ChatXFilm.watched,
                          md.ChatXFilm.favourite,
                          md.ChatXFilm.created_tm).filter(
            sa.and_(md.ChatXFilm.chat_id == chat_id,
                    md.ChatXFilm.film_id == md.Film.imdbid))
        if favourite is not None:
            q = q.filter(md.ChatXFilm.favourite)
        if watched is not None:
            q = q.filter(md.ChatXFilm.watched == watched)
        ret = self.__film_from_query(q, inlib=True)
        session.close()
        return ret

    def insert_film(self, film):
        session = self.Session()
        if not self.film_in_db(film.imdbid):
            data = {key: str(value) for key, value in film.dct.items()
                    if key in md.Film.__dict__ and
                    not key.startswith('_') and
                    not callable(key)}
            ins_film = md.Film(**data)
            session.add(ins_film)
            session.commit()
        session.close()

    def add_dependence(self, chat_id, film_id):
        film_id = str(film_id)
        session = self.Session()
        dep = md.ChatXFilm(chat_id=chat_id, film_id=film_id)
        session.add(dep)
        session.commit()
        session.close()

    def del_dependence(self, chat_id, film_id):
        film_id = str(film_id)
        session = self.Session()
        dep = session.query(md.ChatXFilm).filter(
            sa.and_(md.ChatXFilm.film_id == film_id,
                    md.ChatXFilm.chat_id == chat_id)).first()
        if dep:
            session.delete(dep)
            session.commit()
        session.close()

    def set_favourite(self, chat_id, film_id, favourite):
        film_id = str(film_id)
        session = self.Session()
        film = session.query(md.ChatXFilm).filter(
            sa.and_(md.ChatXFilm.chat_id == chat_id,
                    md.ChatXFilm.film_id == film_id)
        ).first()
        film.favourite = favourite
        session.commit()
        session.close()

    def set_watched(self, chat_id, film_id, watched):
        print('Watched switched to {w}'.format(w=watched))
        film_id = str(film_id)
        session = self.Session()
        film = session.query(md.ChatXFilm).filter(
            sa.and_(md.ChatXFilm.chat_id == chat_id,
                    md.ChatXFilm.film_id == film_id)
        ).first()
        film.watched = watched
        session.commit()
        session.close()
