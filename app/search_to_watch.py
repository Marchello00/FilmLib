from app import session
from fake_useragent import UserAgent
import re
import bs4


async def search_where_to_watch(title: str) -> str:
    ua = UserAgent()
    film_service = 'https://www.kinopoisk.ru/'
    query = f'{film_service}index.php?kp_query={title}'
    async with session.get(query, headers={
        'User-Agent': ua.random
    }) as resp:
        text = await resp.text()
    soup = bs4.BeautifulSoup(text, 'lxml')
    search_res = soup.find('div', {'class': 'search_results'})
    if search_res is None:
        return ""
    for a in search_res.find_all('a', href=True):
        url: str = a['href']
        if match := re.match(r'/(film/\d+).*', url):
            return film_service + match.group(1)
    return ""
