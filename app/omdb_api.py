import typing as tp
import aiohttp
import json
import datetime


class FilmOMDB:
    def __init__(self, dct: tp.Dict[tp.Any, tp.Any]) -> None:
        self.poster = ""
        self.favourite = False
        self.watched = False
        self.inlib = False
        self.created_tm = datetime.datetime.utcnow()

        self.dct = {key.lower(): value for key, value in dct.items()}
        self.__dict__.update(dct)

    def __getattr__(self, item: tp.Any) -> tp.Any:
        if item in self.dct:
            return self.dct[item]
        raise AttributeError

    def __repr__(self) -> str:
        return ''.join(
            '{name}: {value}\n'.format(name=param, value=getattr(self, param))
            for param in self.__dict__
            if not callable(param) and not param.startswith('_')
        )


class OMDB:
    # dict { <alias> : <real param name> }
    __args = {
        'apikey': 'apikey',
        'title': 't',
        'id': 'i',
        'year': 'y',
        'search': 's',
        'type': 'type'
    }

    __site = 'http://www.omdbapi.com/'

    def __init__(self, key: str, session: aiohttp.ClientSession):
        self.__apikey = key
        self.session = session

    async def get_film(self, name: str, year: tp.Optional[str] = None,
                       m_type: tp.Optional[str] = None) -> FilmOMDB:
        """
        Search film by concrete correct title
        (optional year, type)
        :param name: Film title
        :param year: Film year
        :param m_type: Type: movie, series, episode
        :return: Information about the film found (FilmOMDB)
        """
        url = self.__get_url(title=name, year=year, type=m_type)
        async with self.session.get(url) as resp:
            text = await resp.text()
        try:
            return FilmOMDB(json.loads(text))
        except Exception:
            return FilmOMDB({'response': 'False'})

    async def search_film(self, search: str, year: tp.Optional[str] = None,
                          m_type: tp.Optional[str] = None) \
            -> tp.List[FilmOMDB]:
        """
        Search films/series/episodes by keywords
        :param search: Keywords
        :param year: Film year
        :param m_type: Type: movie, series, episode
        :return: Information about the films found (FilmOMDB)
        """
        url = self.__get_url(search=search, year=year, type=m_type)
        async with self.session.get(url) as resp:
            text = await resp.text()
        return [FilmOMDB(film) for film in json.loads(text)['Search']]

    async def get_by_id(self, film_id: str) -> FilmOMDB:
        """
        Search movie by IMDBid's
        :param film_id: IMDBid
        :return: Information about the film found (FilmOMDB)
        """
        url = self.__get_url(id=film_id)
        async with self.session.get(url) as resp:
            text = await resp.text()
        return FilmOMDB(json.loads(text))

    def __get_url(self, **kwargs: tp.Optional[str]) -> str:
        url = self.__site
        if url[-1] != '/':
            url += '/'
        url += '?'
        if 'apikey' not in kwargs:
            kwargs.update({'apikey': self.__apikey})
        for key, val in kwargs.items():
            if key not in self.__args:
                raise AttributeError("No such attribute (check OMDB.args)")
            if not val:
                val = ""
            url += '{param}={val}&'.format(param=self.__args[key],
                                           val=str(val))
        return url

    def set_apikey(self, apikey: str) -> None:
        self.__apikey = apikey
