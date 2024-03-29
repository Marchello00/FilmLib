import typing as tp
from app import strings
from app.omdb_api import FilmOMDB

MarkupT = tp.List[tp.List[tp.Dict[str, str]]]


def form_share_link(url: str, text: str) -> str:
    return strings.SHARE_LINK.format(
        url=url, text=text
    )


def form_film_url(film: FilmOMDB) -> str:
    return strings.FILM_URL.format(imdbid=film.imdbid)


def add_showinfo_button(premarkup: MarkupT,
                        index: int = strings.DEFAULT_INDEX) -> None:
    premarkup.append([
        {
            strings.TG_TEXT_IN_KEYBOARD: strings.MORE_INFO_BUTTON,
            strings.TG_CALLBACK_IN_KEYBOARD:
                strings.TG_CALLBACK_FORMAT.format(
                    index=index,
                    callback_query=strings.MOREINFO_CQ)
        }
    ])


def add_favourite_button(premarkup: MarkupT,
                         index: int = strings.DEFAULT_INDEX,
                         favourite: bool = False) -> None:
    if not favourite:
        txt = strings.ADD_TO_FAVOURITE_BUTTON
        callback_query = strings.ADDTOFAVOURITE_CQ
    else:
        txt = strings.REMOVE_FROM_FAVOURITE_BUTTON
        callback_query = strings.REMOVEFROMFAVOURITE_CQ
    premarkup.append([
        {
            strings.TG_TEXT_IN_KEYBOARD: txt,
            strings.TG_CALLBACK_IN_KEYBOARD:
                strings.TG_CALLBACK_FORMAT.format(
                    index=index,
                    callback_query=callback_query)
        }
    ])


def add_lib_button(premarkup: MarkupT, index: int = strings.DEFAULT_INDEX,
                   lib: bool = False) -> None:
    if not lib:
        txt = strings.ADD_TO_FILMLIB_BUTTON
        callback_query = strings.ADDTOLIBRARY_CQ
    else:
        txt = strings.REMOVE_FROM_FILMLIB_BUTTON
        callback_query = strings.REMOVEFROMLIBRARY_CQ
    premarkup.append([
        {
            strings.TG_TEXT_IN_KEYBOARD: txt,
            strings.TG_CALLBACK_IN_KEYBOARD:
                strings.TG_CALLBACK_FORMAT.format(
                    index=index,
                    callback_query=callback_query)
        }
    ])


def add_watched_button(premarkup: MarkupT, index: int = strings.DEFAULT_INDEX,
                       watched: bool = False) -> None:
    if not watched:
        txt = strings.WATCHED_BUTTON
        callback_query = strings.WATCHED_CQ
    else:
        txt = strings.UNWATCHED_BUTTON
        callback_query = strings.REMOVEFROMWATCHED_CQ
    premarkup.append([
        {
            strings.TG_TEXT_IN_KEYBOARD: txt,
            strings.TG_CALLBACK_IN_KEYBOARD:
                strings.TG_CALLBACK_FORMAT.format(
                    index=index,
                    callback_query=callback_query)
        }
    ])


def add_navigate_button(premarkup: MarkupT, index: int, max_len: int) -> None:
    page_buttons = []
    if index > 0:
        page_buttons.append({
            strings.TG_TEXT_IN_KEYBOARD: strings.PREV_FILM_BUTTON,
            strings.TG_CALLBACK_IN_KEYBOARD:
                strings.TG_CALLBACK_FORMAT.format(
                    index=index,
                    callback_query=strings.PREV_CQ)
        })
    if index < max_len - 1:
        page_buttons.append({
            strings.TG_TEXT_IN_KEYBOARD: strings.NEXT_FILM_BUTTON,
            strings.TG_CALLBACK_IN_KEYBOARD:
                strings.TG_CALLBACK_FORMAT.format(
                    index=index,
                    callback_query=strings.NEXT_CQ)
        })
    if page_buttons:
        premarkup.append(page_buttons)


def add_share_button(premarkup: MarkupT, url: str,
                     index: int = strings.DEFAULT_INDEX,
                     text: str = strings.DEFAULT_SHARE_TEXT) -> None:
    premarkup.append([{
        strings.TG_TEXT_IN_KEYBOARD:
            strings.SHARE_BUTTON,
        strings.TG_URL_IN_KEYBOARD:
            form_share_link(url=url,
                            text=text),
        strings.TG_CALLBACK_IN_KEYBOARD:
            strings.TG_CALLBACK_FORMAT.format(
                index=index,
                callback_query=strings.SHARE_CQ)
    }])


def add_watch_button(premarkup: MarkupT, url: str,
                     index: int = strings.DEFAULT_INDEX) -> None:
    premarkup.append([{
        strings.TG_TEXT_IN_KEYBOARD:
            strings.WATCH_BUTTON,
        strings.TG_URL_IN_KEYBOARD:
            url,
        strings.TG_CALLBACK_IN_KEYBOARD:
            strings.TG_CALLBACK_FORMAT.format(
                index=index,
                callback_query=strings.WATCH_CQ)
    }])


class Buttons:
    def __init__(self) -> None:
        self.__bttns: tp.List[str] = []

    def add_info(self) -> None:
        self.__bttns.append(strings.MOREINFO_CQ)

    def add_lib(self) -> None:
        self.__bttns.append(strings.ADDTOLIBRARY_CQ)

    def add_favourites(self) -> None:
        self.__bttns.append(strings.ADDTOFAVOURITE_CQ)

    def add_watched(self) -> None:
        self.__bttns.append(strings.WATCHED_CQ)

    def add_navigate(self) -> None:
        self.__bttns.append(strings.NEXT_CQ)

    def add_share(self) -> None:
        self.__bttns.append(strings.SHARE_CQ)

    def add_watch(self) -> None:
        self.__bttns.append(strings.WATCH_CQ)

    def get(self, film: FilmOMDB, index: int = strings.DEFAULT_INDEX,
            max_len: int = strings.DEFAULT_MAXLEN) -> tp.Dict[str, tp.Any]:
        markup: MarkupT = []
        for bttn in self.__bttns:
            if bttn == strings.WATCHED_CQ and film.inlib:
                add_watched_button(markup, index=index, watched=film.watched)
            elif bttn == strings.ADDTOLIBRARY_CQ:
                add_lib_button(markup, index, film.inlib)
            elif bttn == strings.ADDTOFAVOURITE_CQ and film.inlib:
                add_favourite_button(markup, index=index,
                                     favourite=film.favourite)
            elif bttn == strings.MOREINFO_CQ:
                add_showinfo_button(markup, index=index)
            elif bttn == strings.NEXT_CQ:
                add_navigate_button(markup, index=index,
                                    max_len=max_len)
            elif bttn == strings.SHARE_CQ:
                add_share_button(markup, index=index,
                                 url=form_film_url(film),
                                 text=film.title)
            elif bttn == strings.WATCH_CQ:
                if film.watch_link is not None:
                    add_watch_button(markup, index=index,
                                     url=film.watch_link)
        return {
            strings.TG_TYPE_IN_MARKUP: strings.TG_INLINE_MARKUP_TYPE,
            strings.TG_INLINE_KEYBOARD_IN_MARKUP: markup
        }
