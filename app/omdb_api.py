import requests
import json


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
        :return: Information about the film found (in JSON)
        """
        url = self._get_query(title=name, year=year, type=tp)
        r = requests.get(url)
        return json.loads(r.text)

    def search_film(self, search, year=None, tp=None):
        """
        Search films/series/episodes by keywords
        :param search: Keywords
        :param year: Film year
        :param tp: Type: movie, series, episode
        :return: Information about the films found (in JSON)
        """
        url = self._get_query(search=search, year=year, type=tp)
        print(url)
        r = requests.get(url)
        return json.loads(r.text)

    def get_by_id(self, film_id):
        """
        Search movie by IMDBid's
        :param film_id: IMDBid
        :return: Information about the film found (in JSON)
        """
        url = self._get_query(id=film_id)
        r = requests.get(url)
        return json.loads(r.text)

    def _get_query(self, **kwargs):
        query = self.__site
        if query[-1] != '/':
            query += '/'
        query += '?'
        if 'apikey' not in kwargs:
            kwargs.update({'apikey': self.__apikey})
        for key, val in kwargs.items():
            if key not in self.__args:
                raise AttributeError("No such attribute (check OMDB.args)")
            if not val:
                val = ""
            query += '{param}={val}&'.format(param=self.__args[key],
                                             val=str(val))
        return query
