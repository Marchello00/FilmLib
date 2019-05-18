# Core
TOKEN_ENVIRON = 'TOKEN'
TOKEN_ENVIRON_DEBUG = 'TOKEN_DEBUG'
APIKEY_ENVIRON = 'APIKEY'
APIKEY_ENVIRON_DEBUG = 'APIKEY_DEBUG'
DATABASE_URL_ENVIRON = 'DATABASE_URL'
DATABASE_URL_ENVIRON_DEBUG = 'DATABASE_URL_DEBUG'
FAILED_TO_LOAD_CONFIG = 'Failed to load config'

TOKEN_CONFIG = 'token'
APIKEY_CONFIG = 'apikey'
DATABASE_URL_CONFIG = 'db_url'

# Bot core
NONE_OMDB = 'N/A'
MOVIE_TYPE = 'movie'
SERIES_TYPE = 'tv'
NEXT_CQ = '>'
PREV_CQ = '<'
MOREINFO_CQ = '?'
MOREINFO_CQ_RE = '\\?'
ADDTOLIBRARY_CQ = '+'
REMOVEFROMLIBRARY_CQ = '-'
ADDTOLIBRARY_CQ_RE = '\\+'
ADDTOFAVOURITE_CQ = '!'
WATCHED_CQ = '_'
REMOVEFROMFAVOURITE_CQ = '&'
REMOVEFROMWATCHED_CQ = '@'

# Bot messages
FILM_NOT_FOUND = 'К сожалению, я не нашёл фильмов с таким названием'
SERIES_NOT_FOUND = 'К сожалению, я не нашёл сериалов с таким названием'
FILM_ALREADY_IN_DB = 'Фильм уже в вашей фильмотеке'
FILM_ALREADY_NOT_IN_DB = 'Фильм уже удалён из вашей фильмотеки'
FILM_ADDED_TO_DB = 'Теперь фильм в вашей фильмотеке!'
FILM_REMOVED_FROM_DB = 'Фильм удалён из вашей фильмотеки'
FILM_ALREADY_IN_FAVOURITES = 'Фильм уже в избранных'
FILM_ALREADY_NOT_IN_FAVOURITES = 'Фильм уже удалён из избранных'
FILM_ADDED_TO_FAVOURITES = 'Фильм добавлен в избранные'
FILM_REMOVED_FROM_FAVOURITES = 'Фильм удалён из избранных'
FILM_ALREADY_WATCHED = 'Фильм уже помечен как просмотренный'
FILM_ALREADY_NOT_WATCHED = 'Фильм уже помечен как непросмотренный'
FILM_ADDED_TO_WATCHED = 'Фильм помечен как просмотренный'
FILM_REMOVED_FROM_WATCHED = 'Фильм помечен как непросмотренный'
SHORT_DESC = "{title} ({year})\n{plot}"
FULL_DESC = '''{title} ({year})
Rated: {rated}
Released: {released}
Runtime: {runtime}
Genre: {genre}
Director: {director}
Writer: {writer}
Actors: {actors}
Country: {country}
IMDb rating: {imdbrating}
{plot}
'''
PREV_FILM_BUTTON = 'Назад'
NEXT_FILM_BUTTON = 'Вперёд'
MORE_INFO_BUTTON = 'Подробнее'
ADD_TO_FILMLIB_BUTTON = 'Добавить в фильмотеку'
REMOVE_FROM_FILMLIB_BUTTON = 'Удалить из фильмотеки'
ADD_TO_FAVOURITE_BUTTON = 'Добавить в избранное'
REMOVE_FROM_FAVOURITE_BUTTON = 'Удалить из избранного'
WATCHED_BUTTON = 'Отметить как просмотренное'
UNWATCHED_BUTTON = 'Отметить как непросмотренное'
OLD_MSG = 'Это старое сообщение, пожалуйста, вполните поиск ещё раз'
UNKNOWN = 'unknown'
NO_FILMS_IN_YOUR_DB = 'В твоей фильмотеке ещё нет фильмов. ' \
                      'Добавь их через поиск /search'
NO_FAVOURITES = 'В твоей фильмотеке ещё нет избранныхъ фильмов. ' \
                'Выбери избранные в своей фильмотеке /myfilms'
NO_UNWATCHED = 'Видимо, ты посмотрел все фильмы из своей фильмотеки. ' \
               'Найди новые фильмы через поиск /search'
GOODBYE = 'Пока, я буду скучать 😢'
HELLO = '''Привет!
Я твоя личная фильмотека.'''
HELP = '''
Ты можешь найти фильм просто отправив мне его название
или с помощью команды /search, например:
Карты, деньги, два ствола
или
/search Avatar
Также я умею искать сериалы:
Кремниевая долина
или
/searchseries Игра престолов
Чтобы посмотреть добавленные фильмы, используй команду /myfilms
Чтобы посмотреть избранные используй /favourites
Чтобы увидеть те фильмы, которые еще не отмечены тобой 
как просмотренные, напиши /unwatched
Если ты забыл команды, можешь ввести /help
Приятного пользования и интересных фильмов!
😜😜😜
'''
SEARCH_HELP = '''Если хочешь использовать поиск, введи: 
/search <название фильма>
Например:
/search Аватар
'''

# Other
NO_PICTURE_URL = 'https://fasttorrent.org/templates/tor-baza-utf/images/no_poster.jpg'
