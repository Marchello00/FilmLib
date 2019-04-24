from app import strings


def add_showinfo_button(premarkup, index=None):
    if index is None:
        index = '{index}'
    premarkup.append([
        {
            'text': strings.MORE_INFO_BUTTON,
            'callback_data': '{cq}{index}'.format(index=index,
                                                  cq=strings.MOREINFO_CQ)
        }
    ])


def add_favourite_button(premarkup, index=None, favourite=False):
    if index is None:
        index = '{index}'
    if not favourite:
        txt = strings.ADD_TO_FAVOURITE_BUTTON
        cq = strings.ADDTOFAVOURITE_CQ
    else:
        txt = strings.REMOVE_FROM_FAVOURITE_BUTTON
        cq = strings.REMOVEFROMFAVOURITE_CQ
    premarkup.append([
        {
            'text': txt,
            'callback_data': '{cq}{index}'.format(index=index,
                                                  cq=cq)
        }
    ])


def add_lib_button(premarkup, index=None, lib=False):
    if index is None:
        index = '{index}'
    if not lib:
        txt = strings.ADD_TO_FILMLIB_BUTTON
        cq = strings.ADDTOLIBRARY_CQ
    else:
        txt = strings.REMOVE_FROM_FILMLIB_BUTTON
        cq = strings.REMOVEFROMLIBRARY_CQ
    premarkup.append([
        {
            'text': txt,
            'callback_data': '{cq}{index}'.format(index=index,
                                                  cq=cq)
        }
    ])


def add_watched_button(premarkup, index=None, watched=False):
    if index is None:
        index = '{index}'
    if not watched:
        txt = strings.WATCHED_BUTTON
        cq = strings.WATCHED_CQ
    else:
        txt = strings.UNWATCHED_BUTTON
        cq = strings.REMOVEFROMWATCHED_CQ
    premarkup.append([
        {
            'text': txt,
            'callback_data': '{cq}{index}'.format(index=index,
                                                  cq=cq)
        }
    ])


class Buttons:
    def __init__(self):
        self.__bttns = []

    def dbg(self):
        return self.__bttns

    def add_info(self):
        self.__bttns.append(strings.MOREINFO_CQ)

    def add_lib(self):
        self.__bttns.append(strings.ADDTOLIBRARY_CQ)

    def add_favourites(self):
        self.__bttns.append(strings.ADDTOFAVOURITE_CQ)

    def add_watched(self):
        self.__bttns.append(strings.WATCHED_CQ)

    def get(self, index, max_len, film):
        markup = []
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
        page_buttons = []
        if index > 0:
            page_buttons.append({
                'text': strings.PREV_FILM_BUTTON,
                'callback_data': '{cq}{index}'.format(index=index,
                                                      cq=strings.PREV_CQ)
            })
        if index < max_len - 1:
            page_buttons.append({
                'text': strings.NEXT_FILM_BUTTON,
                'callback_data': '{cq}{index}'.format(index=index,
                                                      cq=strings.NEXT_CQ)
            })
        if page_buttons:
            markup.append(page_buttons)
        res_markup = {
            'type': 'InlineKeyboardMarkup',
            'inline_keyboard': markup
        }
        return res_markup
