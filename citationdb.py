import json
import re
import logging

import neo4j

from pypinyin import lazy_pinyin


class CitationDB:
    def __init__(self, config='config.json'):
        self.config: dict = json.load(open(config, 'r', encoding='utf-8'))
        self.driver = neo4j.GraphDatabase.driver(self.config['neo4j_uri'],
                                                 auth=(self.config['neo4j_user'],
                                                       self.config['neo4j_password']))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def write_query(self, query_text):
        def _write_query(tx):
            result = tx.run(query_text)
            return list(result)

        with self.driver.session() as session:
            res = session.write_transaction(_write_query)
            for item in res:
                print(item)
            return res

    def read_query(self, query_text):
        def _write_query(tx):
            result = tx.run(query_text)
            return list(result)

        with self.driver.session() as session:
            res = session.read_transaction(_write_query)
            for item in res:
                print(item)
            return res

    def add_author(self, **kwargs):
        name = kwargs.get('name', '')
        if not name:
            logging.error(f'[add_author()]: No name provided.')
            return
        ref_link = kwargs.get('ref_link', '')
        institution = kwargs.get('institution', '')
        title = kwargs.get('title', [])
        dup_check = self.read_query(f'MATCH (a:Author) WHERE a.name="{kwargs["name"]}" RETURN a')
        if len(dup_check) != 0:
            logging.error(f'[add_author()]: {kwargs["name"]} already exists')
            return
        if kwargs.get('alias_of'):
            logging.error(f'[add_author()]: You are adding {kwargs.get("name")} as a redirect. '
                          f'Use add_author_redirect() instead')
            return
        self.write_query(f'CREATE (a:Author {{name="{name}", ref_link="{ref_link}", institution="{institution}"}})')

        # Possible alias
        name_split = re.split(r'-|\s+', name)
        alias = []
        if re.search(r'[\u4e00-\u9fa5]', name):  # Chinese characters
            pinyin_list = lazy_pinyin(name)
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
            alias = [name.lower(), name.upper(),
                     '.'.join([s[0] for s in name_split[:-1]]) + '. ' + name_split[-1],
                     '. '.join([s[0] for s in name_split[:-1]]) + '. ' + name_split[-1],
                     ' '.join([s[0] for s in name_split[:-1]]) + ' ' + name_split[-1],
                     '-'.join(name_split[:-1]) + ' ' + name_split[-1],
                     name_split[-1] + ', ' + ' '.join(name_split[:-1])]

        alias = list(set(alias))
        for item in alias:
            if item == name:
                continue
            self.add_author_redirect(item, name)

            # Check Titles
        for item in title:
            self.add_title(item)    # Dup check is in add_title()
            self.write_query(f'MATCH (t:Title) WHERE t.name="{item}"'
                             f'MATCH (a:Author) WHERE a.name="{name}"'
                             f'CREATE (a)-[:Has]->(t)')

    def add_author_redirect(self, name: str, target: str):
        dup_check = self.read_query(f'MATCH (a:Author) WHERE a.name="{name}" RETURN a')
        if len(dup_check) != 0:
            logging.error(f'[add_author_redirect()]: {name} already exists.')
            return
        target_existence_check = self.read_query(f'MATCH (a:Author) WHERE a.name="{target}" RETURN a')
        if len(target_existence_check) == 0:
            logging.error(f'[add_author_redirect()]: Target {target} does not exist.')
            return
        self.write_query(f'MATCH (tar:Author) WHERE tar.name="{target}"'
                         f'CREATE (a:Author {{name="{name}"}})'
                         f'CREATE (a)-[:Alias_of]->(tar)')

    def add_title(self, name: str):
        dup_check = self.read_query(f'MATCH (t:Title) WHERE t.name="{name}" RETURN t')
        if len(dup_check) == 0:
            logging.error(f'[add_title()]: Title {name} already exists.')
            return

        self.write_query(f'CREATE (t:Title{{name: "{name}"}})')

    def check_dup_author(self, name: str):
        return bool(self.read_query(f'MATCH (a:Author) WHERE a.name="{name}" RETURN a'))
