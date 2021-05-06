import re
import bs4
from . import strings


class Converter:
    types = {
        'movie': 'movie',
        'series': 'tv'
    }

    __site = 'https://www.themoviedb.org/'

    def __init__(self, session):
        self.session = session

    async def get_russian(self, search, m_type='movie', lang='en'):
        url = self.__get_url(search=search, m_type=m_type, lang=lang)
        async with self.session.get(url) as resp:
            text = await resp.text()
        soup = bs4.BeautifulSoup(text, 'lxml')
        results = []
        for part in soup.find_all('div', {'class': 'card v4 tight'}):
            film = FilmRus()
            img_src = part.find('div', {'class': 'poster'}).a.img
            if img_src:
                film.poster = self.__site + img_src.get('src')
            film_info = part.find('div', {'class': 'title'})
            film.title = film_info.div.a.h2.text
            film.url = self.__site + film_info.div.a['href']
            film.date = ""
            if film_info.span:
                film.date = film_info.span.text
            film.type = m_type
            overview = part.find('div', {'class': 'overview'}).p
            film.plot = ""
            if overview:
                film.plot = overview.text
            results.append(film)
        return results

    def __get_url(self, search, m_type='movie', lang='ru'):
        if self.__site[-1] != '/':
            self.__site += '/'
        url = '{site}search/{type}?query={query}'.format(
            site=self.__site, type=m_type, query=search
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
        return ''.join(
            '{name}: {value}\n'.format(name=param, value=getattr(self, param))
            for param in self.__dict__
            if not callable(param) and not param.startswith('_')
        )

    def __setattr__(self, key, value):
        if key == 'date' and value:
            self.year = re.findall(r'\d\d\d\d', value)[0]
        super().__setattr__(key, value)

    def __type_omdb(self):
        return self.retypes[self.type]

    def __getattr__(self, item):
        if item == 'type_omdb':
            return self.__type_omdb()
        raise AttributeError

    async def set_omdb(self):
        from . import omdb
        if self.omdb:
            return
        self.omdb = await omdb.get_film(name=self.title, year=self.year,
                                        m_type=self.type_omdb)
        if (
                self.omdb.response == 'False'
                or self.title.lower() != self.omdb.title.lower()
                or self.omdb.poster == strings.NONE_OMDB
        ):
            self.title = self.title.replace('(', '')
            self.title = self.title.replace(')', '')
            self.omdb = await omdb.get_film(name=self.title)
        if not hasattr(self.omdb,
                       'poster') or self.omdb.poster == strings.NONE_OMDB:
            self.omdb.poster = self.poster

    async def get_omdb(self):
        from . import omdb
        if self.omdb:
            return self.omdb
        return await omdb.get_film(name=self.title, year=self.year,
                                   m_type=self.type_omdb)
