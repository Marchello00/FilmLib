from app import strings
from app import db


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


def add_favourite_button(premarkup, index=None, favourite=True):
    if index is None:
        index = '{index}'
    if favourite:
        txt = strings.ADD_TO_FAVOURITE_BUTTON
    else:
        txt = strings.REMOVE_FROM_FAVOURITE_BUTTON
    premarkup.append([
        {
            'text': txt,
            'callback_data': '{cq}{index}'.format(index=index,
                                                  cq=strings.ADDTOFAVOURITE_CQ)
        }
    ])


def add_lib_button(premarkup, index=None, lib=True):
    if index is None:
        index = '{index}'
    if lib:
        txt = strings.ADD_TO_FILMLIB_BUTTON
    else:
        txt = strings.REMOVE_FROM_FILMLIB_BUTTON
    premarkup.append([
        {
            'text': txt,
            'callback_data': '{cq}{index}'.format(index=index,
                                                  cq=strings.ADDTOLIBRARY_CQ)
        }
    ])


def add_watched_button(premarkup, index=None, watched=True):
    if index is None:
        index = '{index}'
    if watched:
        txt = strings.WATCHED_BUTTON
    else:
        txt = strings.UNWATCHED_BUTTON
    premarkup.append([
        {
            'text': txt,
            'callback_data': '{cq}{index}'.format(index=index,
                                                  cq=strings.WATCHED_CQ)
        }
    ])


class Buttons:
    __bttns = []

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

    def get(self, index, max_len):
        # TODO: add db check for changing buttons
        markup = []
        for bttn in self.__bttns:
            if bttn == strings.WATCHED_CQ:
                add_watched_button(markup, index=index, watched=False)
            elif bttn == strings.ADDTOLIBRARY_CQ:
                add_lib_button(markup, index, True)
            elif bttn == strings.ADDTOFAVOURITE_CQ:
                add_favourite_button(markup, index=index, favourite=True)
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
