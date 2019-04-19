import bs4
import requests
import lxml


class Converter:
    __types = {
        'movie': 'movie',
        'series': 'tv'
    }

    __site = 'https://www.themoviedb.org/'

    def get_russian(self, search, tp='movie'):
        url = self.__get_url(search=search, tp=tp)
        text = requests.get(url).text
        soup = bs4.BeautifulSoup(text, lxml)
        for part in soup.find_all('div', {'class': 'info'}):
            print(part.text)

    def __get_url(self, search, tp='movie'):
        if self.__site[-1] != '/':
            self.__site += '/'
        url = '{site}search/{type}?query={query}'.format(
            site=self.__site, type=tp, query=search
        )
        return url
