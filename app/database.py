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
        'tp': 'type'
    }
    Session = None

    def __init__(self, engine):
        self.Session = saorm.sessionmaker(bind=engine)

    def get_films_by_chat(self, chat_id):
        session = self.Session()
        films = []
        for res in session.query(md.Film).join(md.ChatXFim).filter(
                md.ChatXFim.chat_id == chat_id):
            films.append(FilmOMDB({
                self.__convert[key]: value for key, value in
                res.__dict__.items() if not callable(key)
            }))
        return films

    def insert_film(self, film):
        session = self.Session()
        if not session.query(md.Film).filter(md.Film.id == film.imdbid).all():
            ins_film = md.Film(id=film.imdbid, year=film.year, img=film.poster,
                               title=film.title, tp=film.type)
            session.add(ins_film)
            session.commit()

    def get_films_by_title(self, title, year=None):
        session = self.Session()
        q = session.query(md.Film).filter(md.Film.title == title)
        if year:
            q = q.filter(md.Film.year == year)
        return q.all()

    def get_favourite_films(self, chat_id):
        session = self.Session()
        films = []
        for res in session.query(md.Film).join(md.ChatXFim).filter(
                sa.and_(md.ChatXFim.chat_id == chat_id,
                        md.ChatXFim.favourite)):
            films.append(FilmOMDB({
                self.__convert[key]: value for key, value in
                res.__dict__.items() if not callable(key)
            }))
        return films
