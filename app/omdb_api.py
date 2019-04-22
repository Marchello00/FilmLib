import requests
import json


class FilmOMDB:
    def __init__(self, dct=None):
        self.__dct = {key.lower(): value for key, value in dct.items()}
        self.__dict__.update(dct)

    def __getattr__(self, item):
        if item in self.__dct:
            return self.__dct[item]
        raise AttributeError

    def __repr__(self):
        text = ''
        for param in self.__dict__:
            if not callable(param) and not param.startswith('_'):
                text += '{name}: {value}\n'.format(
                    name=param,
                    value=getattr(self, param)
                )
        return text


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

    def __init__(self, key):
        self.__apikey = key

    def get_film(self, name, year=None, tp=None):
        """
        Search film by concrete correct title
        (optional year, type)
        :param name: Film title
        :param year: Film year
        :param tp: Type: movie, series, episode
        :return: Information about the film found (FilmOMDB)
        """
        url = self.__get_url(title=name, year=year, type=tp)
        r = requests.get(url)
        return FilmOMDB(json.loads(r.text))

    def search_film(self, search, year=None, tp=None):
        """
        Search films/series/episodes by keywords
        :param search: Keywords
        :param year: Film year
        :param tp: Type: movie, series, episode
        :return: Information about the films found (FilmOMDB)
        """
        url = self.__get_url(search=search, year=year, type=tp)
        print(url)
        r = requests.get(url)
        return [FilmOMDB(film) for film in json.loads(r.text)['Search']]

    def get_by_id(self, film_id):
        """
        Search movie by IMDBid's
        :param film_id: IMDBid
        :return: Information about the film found (FilmOMDB)
        """
        url = self.__get_url(id=film_id)
        r = requests.get(url)
        return FilmOMDB(json.loads(r.text))

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
