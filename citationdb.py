import json
import re
import logging

from pypinyin import lazy_pinyin

import db_node


logging.basicConfig(level=logging.DEBUG)


class Db:
    def __init__(self, filename: str):
        self.data: dict = json.load(open(filename, 'r', encoding='utf-8'))
        self.filename = filename

    def add_author(self, **kwargs):
        """
        :param kwargs:
            name: str. Name of the author. Also used as the key for indexing this author. Should be fullname or the most
                       commonly used name if it is not a redirection.
            redirect_target: str. Name other than the fullname or mostly commonly used name. Searching process will be
                                  redirected to its target.
            title: list[str]. A list of titles of this author.
            institution: str. The institution this author belongs to.
        """
        if kwargs['name'] in self.data['author']:
            logging.error(f'[add_author()]: {kwargs["name"]} already exists')
            return
        author = db_node.Author(**kwargs)
        if author.redirect_target:
            logging.error(f'[add_author()]: You are adding {author.name} as a redirect. '
                          f'Use add_author_redirect() instead')
        self.data['author'][kwargs['name']] = author.__dict__

        # Possible alias
        name_split = re.split(r'-|\s+', author.name)
        alias = []
        if re.search(r'[\u4e00-\u9fa5]', author.name):  # Chinese characters
            pinyin_list = lazy_pinyin(author.name)
            given_1 = ''.join(pinyin_list[1:])
            given_2 = '-'.join([f'{s[0].upper()}{s[1:]}' for s in pinyin_list[1:]])
            family = pinyin_list[0]
            alias.append(f'{given_1[0].upper()}{given_1[1:]} {family[0].upper()}{family[1:]}')  # Hongmei Zhang
            alias.append(f'{given_1} {family}')  # hongmei zhang
            alias.append(f'{given_2} {family[0].upper()}{family[1:]}')  # Hong-Mei Zhang
            alias.append(f'{family[0].upper()}{family[1:]}, {given_1[0].upper()}{given_1[1:]}')
            alias.append(f'{given_1[0].upper()} {family[0].upper()}{family[1:]}')
            alias.append(f'{given_1[0].upper()}. {family[0].upper()}{family[1:]}')
        else:
            alias = [author.name.lower(), author.name.upper(),
                     '.'.join([s[0] for s in name_split[:-1]]) + '. ' + name_split[-1],
                     '. '.join([s[0] for s in name_split[:-1]]) + '. ' + name_split[-1],
                     ' '.join([s[0] for s in name_split[:-1]]) + ' ' + name_split[-1],
                     '-'.join(name_split[:-1]) + ' ' + name_split[-1],
                     name_split[-1] + ', ' + ' '.join(name_split[:-1])]

        alias = list(set(alias))
        for item in alias:
            if item == author.name:
                continue
            self.add_author_redirect(item, author.name)

        # Check Titles
        for item in author.title:
            if item not in self.data['title']:
                self.add_title(name=item)
            title = db_node.Title(**self.data['title'][item])
            while title.redirect_target:
                title = db_node.Title(**self.data['title'][title.redirect_target])
            title.author.append(author.name)

            self.data['title'][title.name] = title.__dict__

    def add_author_redirect(self, name: str, target: str):
        redirect = db_node.Author(name=name, redirect_target=target)
        if target not in self.data['author']:
            logging.error(f'[add_author_redirect()]: Target {target} does not exist.')
            return

        target_author = db_node.Author(**self.data['author'][target])
        while target_author.redirect_target:
            target_author = db_node.Author(**self.data['author'][target_author.redirect_target])
        redirect.redirect_target = target_author.name

        if name in self.data['author']:
            logging.warning(f'[add_author_redirect()]: {name} already exists.')
            old_author = db_node.Author(**self.data['author'][name])

            target_author.title.extend(old_author.title)

        self.data['author'][name] = redirect.__dict__

    def edit_author(self, name, **kwargs):
        if name not in self.data['author']:
            logging.error(f'[edit_author()]: Author {name} does not exist. Use add_author() instead.')
            return
        if kwargs.get('redirect_target', ''):
            logging.error(f'[edit_author()]: Set redirect with add_redirect() instead.')
            return
        old_author = db_node.Author(**self.data['author'][name])
        new_author = db_node.Author(**self.data['author'][name])
        for key in kwargs:
            exec(f'new_author.{key} = kwargs["{key}"]')
        removed_title = set(old_author.title) - set(new_author.title)
        added_title = set(new_author.title) - set(old_author.title)
        for title_name in removed_title:
            title = db_node.Title(**self.data['title'][title_name])
            title.author.remove(old_author.name)
            self.data['title'][title_name] = title.__dict__
        for title_name in added_title:
            title = db_node.Title(**self.data['title'].get(title_name, {'name': title_name}))
            title.author.append(old_author.name)
            self.data['title'][title_name] = title.__dict__
        self.data['author'][new_author.name] = new_author.__dict__

    def remove_author(self, name: str):
        if name not in self.data['author']:
            logging.error(f'[remove_author()]: {name} does not exist.')
            return
        author = db_node.Author(**self.data['author'][name])
        for title_name in author.title:
            title = db_node.Title(**self.data['title'][title_name])
            title.author.remove(name)
            self.data['title'][title_name] = title.__dict__
        del self.data['author'][name]

    def add_title(self, **kwargs):
        if kwargs['name'] in self.data['title']:
            logging.error(f'[add_title()]: {kwargs["name"]} already exists.')
            return
        title = db_node.Title(**kwargs)

        for title_name in title.sub_title:
            if title_name not in self.data['title']:
                self.add_title(name=title_name)
        self.data['title'][kwargs['name']] = title.__dict__

    def add_title_redirect(self, name: str, target: str):
        redirect = db_node.Title(name=name, redirect_target=target)
        if target not in self.data['title']:
            logging.error(f'[add_title_redirect()]: Target {target} does not exist.')
            return

        target_title = db_node.Title(**self.data['title'][target])
        while target_title.redirect_target:
            target_title = db_node.Title(**self.data['title'][target_title.redirect_target])
        redirect.redirect_target = target_title.name

        if name in self.data['title']:
            logging.warning(f'[add_title_redirect()]: {name} already exists.')
            old_title = db_node.Title(**self.data['title'][name])

            target_title.sub_title.extend(old_title.sub_title)
            target_title.author.extend(old_title.author)
        self.data['title'][name] = redirect.__dict__

    def write_db(self):
        json.dump(self.data, open(self.filename, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    def clean_up(self):
        for name in list(self.data['author'].keys()):
            data = self.data['author'][name]
            author = db_node.Author(**data)
            if author.redirect_target and author.redirect_target not in self.data['author']:
                del self.data['author'][name]
        for name in list(self.data['title'].keys()):
            data = self.data['title'][name]
            title = db_node.Title(**data)
            if title.redirect_target and title.redirect_target not in self.data['title']:
                del self.data['title'][name]
            for sub_title_name in title.sub_title:
                if sub_title_name not in self.data['title']:
                    title.sub_title.remove(sub_title_name)
