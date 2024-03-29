import typing as tp
from contextlib import contextmanager
import sqlalchemy.orm as sqlorm
import sqlalchemy as sql
from app import models
from app.omdb_api import FilmOMDB


class DB:
    __convert = {
        'id': 'imdbid',
        'year': 'year',
        'img': 'poster',
        'title': 'title',
        'type': 'type'
    }
    session_maker: sqlorm.sessionmaker

    @contextmanager
    def connect(self) -> tp.Iterator[sqlorm.sessionmaker]:
        session = self.session_maker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def __film_from_query(query: sqlorm.query, inlib: bool = False) \
            -> tp.List[FilmOMDB]:
        films: tp.List[FilmOMDB] = []
        for film, watched, favourite, created_tm in query:
            films.append(FilmOMDB({
                key: value for key, value in
                film.__dict__.items() if
                not callable(key) and not key.startswith('_')
            }))
            films[-1].favourite = favourite
            films[-1].watched = watched
            films[-1].inlib = inlib
            films[-1].created_tm = created_tm
        films.sort(key=lambda x: x.created_tm, reverse=True)
        return films

    def __init__(self, engine: sql.engine.Engine) -> None:
        self.session_maker = sqlorm.sessionmaker(bind=engine)

    def film_in_db(self, film_id: int) -> bool:
        film_id_s = str(film_id)
        with self.connect() as session:
            return bool(session.query(models.Film.imdbid).filter(
                models.Film.imdbid == film_id_s).all())

    def film_in_chat_db(self, chat_id: int, film_id: int,
                        favourite: tp.Optional[bool] = None,
                        watched: tp.Optional[bool] = None) -> bool:
        film_id_s = str(film_id)
        with self.connect() as session:
            query = session.query(models.ChatXFilm).filter(
                sql.and_(models.ChatXFilm.film_id == film_id_s,
                         models.ChatXFilm.chat_id == chat_id))
            if favourite is not None:
                query = query.filter(
                    models.ChatXFilm.favourite == favourite)
            if watched is not None:
                query = query.filter(models.ChatXFilm.watched == watched)
            return bool(query.all())

    def get_films_by_chat(self, chat_id: int,
                          favourite: tp.Optional[bool] = None,
                          watched: tp.Optional[bool] = None) \
            -> tp.List[FilmOMDB]:
        with self.connect() as session:
            query = session.query(models.Film, models.ChatXFilm.watched,
                                  models.ChatXFilm.favourite,
                                  models.ChatXFilm.created_tm).filter(
                sql.and_(models.ChatXFilm.chat_id == chat_id,
                         models.ChatXFilm.film_id ==
                         models.Film.imdbid))
            if favourite is not None:
                query = query.filter(models.ChatXFilm.favourite)
            if watched is not None:
                query = query.filter(models.ChatXFilm.watched == watched)
            return self.__film_from_query(query, inlib=True)

    def insert_film(self, film: FilmOMDB) -> None:
        with self.connect() as session:
            if not self.film_in_db(film.imdbid):
                data = {key: str(value) for key, value in film.dct.items()
                        if key in models.Film.__dict__ and
                        not key.startswith('_') and
                        not callable(key)}
                ins_film = models.Film(**data)
                session.add(ins_film)

    def add_dependence(self, chat_id: int, film_id: int) -> None:
        film_id_s = str(film_id)
        with self.connect() as session:
            dep = models.ChatXFilm(chat_id=chat_id, film_id=film_id_s)
            session.add(dep)
            return

    def del_dependence(self, chat_id: int, film_id: int) -> None:
        film_id_s = str(film_id)
        with self.connect() as session:
            dep = session.query(models.ChatXFilm).filter(
                sql.and_(models.ChatXFilm.film_id == film_id_s,
                         models.ChatXFilm.chat_id == chat_id)).first()
            if dep:
                session.delete(dep)
            return

    def set_favourite(self, chat_id: int, film_id: int,
                      favourite: bool) -> None:
        film_id_s = str(film_id)
        with self.connect() as session:
            film = session.query(models.ChatXFilm).filter(
                sql.and_(models.ChatXFilm.chat_id == chat_id,
                         models.ChatXFilm.film_id == film_id_s)
            ).first()
            film.favourite = favourite
            return

    def set_watched(self, chat_id: int, film_id: int, watched: bool) -> None:
        film_id_s = str(film_id)
        with self.connect() as session:
            film = session.query(models.ChatXFilm).filter(
                sql.and_(models.ChatXFilm.chat_id == chat_id,
                         models.ChatXFilm.film_id == film_id_s)
            ).first()
            film.watched = watched
            return
