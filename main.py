import json
import re

from pypinyin import lazy_pinyin

import db_node

db = json.load(open('db.json', 'r', encoding='utf-8'))


def add_author(**kwargs):
    """
    :param kwargs:
        name: str. Name of the author. Also used as the key for indexing this author. Should be fullname or the most
                   commonly used name if it is not a redirection.
        redirect_target: str. Name other than the fullname or mostly commonly used name. Searching process will be
                              redirected to its target.
        title: list[str]. A list of titles of this author.
        institution: str. The institution this author belongs to.
    """
    if kwargs['name'] in db['author']:
        print(kwargs['name'], 'already exists. [add_author()]')
        return
    author = db_node.Author(**kwargs)
    db['author'][kwargs['name']] = author.__dict__

    # Possible alias
    name_split = re.split(r'-|\s+ ', author.name)
    alias = [author.name.lower(), author.name.upper()]
    alias.append('.'.join([s[0] for s in name_split[:-1]]) + ' ' + name_split[-1])  # A.B. Charlie
    alias.append('. '.join([s[0] for s in name_split[:-1]]) + name_split[-1])  # A. B. Charlie
    alias.append(' '.join([s[0] for s in name_split[:-1]]) + ' ' + name_split[-1])  # A B Charlie
    alias.append('-'.join(name_split[:-1]) + ' ' + name_split[-1])  # Alice-Bob Charlie
    alias.append(name_split[-1] + ', ' + ' '.join(name_split[:-1]))
    if re.search(r'[\u4e00-\u9fa5]', author.name):  # Chinese characters
        pinyin_list = lazy_pinyin(author.name)
        given_1 = ''.join(pinyin_list[:-1])
        given_2 = '-'.join([f'{s[0].upper()}{s[1:]}' for s in pinyin_list[:-1]])
        family = pinyin_list[-1]
        alias.append(f'{given_1[0].upper()}{given_1[1:]} {family[0].upper()}{family[1:]}')  # Hongmei Zhang
        alias.append(f'{given_1} {family}')  # hongmei zhang
        alias.append(f'{given_2} {family[0].upper()}{family[1:]}')  # Hong-Mei Zhang
        alias.append(f'{family[0].upper()}{family[1:]}, {given_1[0].upper()}{given_1[1:]}')
    for item in alias:
        add_author_redirect(item, author.name)

    # Check Titles
    for item in author.title:
        if item not in db['title']:
            add_title(name=item)


def add_author_redirect(name: str, target: str):
    if target not in db['author'] or name in db['author']:
        print(name, 'already exists. [add_author_redirect()]')
        return False
    redirect = db_node.Author(name=name, redirect_target=target)
    db['author'][name] = redirect.__dict__


def add_title(**kwargs):
    pass


def write_db():
    json.dump(db, open('db.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)


if __name__ == '__main__':
    pass
