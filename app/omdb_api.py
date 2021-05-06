import json


class FilmOMDB:
    def __init__(self, dct=None):
        self.dct = {key.lower(): value for key, value in dct.items()}
        self.__dict__.update(dct)

    def __getattr__(self, item):
        if item in self.dct:
            return self.dct[item]
        raise AttributeError

    def __repr__(self):
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

    def __init__(self, key, session):
        self.__apikey = key
        self.session = session

    async def get_film(self, name, year=None, m_type=None):
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

    async def search_film(self, search, year=None, m_type=None):
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

    async def get_by_id(self, film_id):
        """
        Search movie by IMDBid's
        :param film_id: IMDBid
        :return: Information about the film found (FilmOMDB)
        """
        url = self.__get_url(id=film_id)
        async with self.session.get(url) as resp:
            text = await resp.text()
        return FilmOMDB(json.loads(text))

    def __get_url(self, **kwargs):
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

    def set_apikey(self, apikey):
        self.__apikey = apikey
