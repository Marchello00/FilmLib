import bs4
import requests
import re
from app.strings import NONE_OMDB


class Converter:
    types = {
        'movie': 'movie',
        'series': 'tv'
    }

    __site = 'https://www.themoviedb.org/'

    def __init__(self):
        pass

    def get_russian(self, search, tp='movie', lang='ru'):
        url = self.__get_url(search=search, tp=tp, lang=lang)
        text = requests.get(url).text
        soup = bs4.BeautifulSoup(text, 'lxml')
        results = []
        for part in soup.find_all('div', {'class': 'item poster card'}):
            film = FilmRus()
            img_src = part.find('div', {'class': 'image_content'}).a.img
            if img_src:
                film.poster = img_src.get('data-src')
            film_info = part.find('div', {'class': 'flex'})
            film.title = film_info.a['title']
            film.url = self.__site + film_info.a['href']
            film.date = film_info.span.text
            film.type = tp
            film.plot = part.find('p', {'class': 'overview'}).text
            results.append(film)
        return results

    def __get_url(self, search, tp='movie', lang='ru'):
        if self.__site[-1] != '/':
            self.__site += '/'
        url = '{site}search/{type}?query={query}'.format(
            site=self.__site, type=tp, query=search
        )
        if lang:
            url += '&language={lang}'.format(lang=lang)
        return url


class FilmRus:
    retypes = {key: value for value, key in Converter.types.items()}

    def __init__(self):
        self.title = None
        self.poster = None
        self.url = None
        self.date = None
        self.year = None
        self.type = None
        self.plot = None
        self.omdb = None

    def __repr__(self):
        text = ''
        for param in self.__dict__:
            if not callable(param) and not param.startswith('_'):
                text += '{name}: {value}\n'.format(
                    name=param,
                    value=getattr(self, param)
                )
        return text

    def __setattr__(self, key, value):
        if key == 'date':
            if value:
                self.year = re.findall(r'\d\d\d\d', value)[0]
        super().__setattr__(key, value)

    def __type_omdb(self):
        return self.retypes[self.type]

    def __getattr__(self, item):
        if item == 'type_omdb':
            return self.__type_omdb()
        raise AttributeError

    def set_omdb(self):
        from app import omdb
        if self.omdb:
            return
        self.omdb = omdb.get_film(name=self.title, year=self.year,
                                  tp=self.type_omdb)
        if self.omdb.response == 'False' or \
                not self.title.lower() == self.omdb.title.lower() or \
                self.omdb.poster == NONE_OMDB:
            self.title = self.title.replace('(', '')
            self.title = self.title.replace(')', '')
            self.omdb = omdb.get_film(name=self.title)
        if not hasattr(self.omdb, 'poster') or self.omdb.poster == NONE_OMDB:
            self.omdb.poster = self.poster

    def get_omdb(self):
        from app import omdb
        if self.omdb:
            return self.omdb
        return omdb.get_film(name=self.title, year=self.year,
                             tp=self.type_omdb)
