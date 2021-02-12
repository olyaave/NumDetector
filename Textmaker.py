import asyncio
import json
import re

from telethon import utils
from telethon.tl.types import PeerUser


class Textmaker:
    def __init__(self, client):
        self.client = client

    def get_text_for_telegram(self, old_text, rate_text, entities):
        text = self.replace_all(old_text[: self.find_author(old_text)], [r'_', r'*', r'[', ']', r'(', ')', r'~',
                                                                         r'`', r'>', r'#', r'+', r'-', r'=', r'|',
                                                                         r'{', r'}', r'.', r'!'])
        text += rate_text + "\n"
        user_entity = self.find_entity(entities, 'user')

        if user_entity:
            # ioloop = asyncio.get_event_loop()
            # link = ioloop.run_until_complete(
            #     self.get_user_link(user_entity['user']['id'], self.get_chat_name(entities)))
            # print(link)
            # text += "[Автор](" + link + ")\n"
            text += "[Автор](tg://user?id=" + str(user_entity['user']['id']) + ")\n"
        else:
            text += "Автор\n"
        text = self.add_url_line(entities, text)
        return text

    async def get_user_link(self, user_id, chat_name):
        await self.client.connect()
        await self.client.get_participants(chat_name)
        entity = await self.client.get_entity(PeerUser(user_id))
        enter = str(entity).find('access_hash')
        access_hash = str(entity)[enter+13:enter+32]
        link = "https://web.telegram.org/#/im?p=u" + str(user_id) + "_" + access_hash
        return link

    def get_chat_name(self, entities):
        url_entity = self.find_entity(entities, 'url')
        if url_entity:
            return (url_entity['url'])

    def get_text_for_amocrm(self, old_text, rate_text, entities):
        print(old_text)
        phone_entity = self.find_entity(entities, 'type')
        if phone_entity and phone_entity['type'] == 'phone_number':
            old_text = re.sub(r'(\+?7|8)[( -]?([\d]{3})[) -]{0,2}?([\d]{2}[) -]?[\d]{2}[) -]?[\d]{3}|[\d]{3}'
                                       r'[) -]?[\d]{2}[) -]?[\d]{2})', r'', old_text)
        text = old_text[: self.find_author(old_text)] + rate_text + "\n"

        text = self.add_user_line(entities, text)
        text = self.add_url_line(entities, text)
        print(text)
        return text

    def add_user_line(self, entities, text):
        user_entity = self.find_entity(entities, 'user')
        if user_entity and str(self.get_chat_name(entities)).find('https://t.me/c/') == -1:
                ioloop = asyncio.get_event_loop()
                link = ioloop.run_until_complete(
                    self.get_user_link(user_entity['user']['id'], self.get_chat_name(entities)[13:]))
                print(link)
                text += "[Автор](" + link + ")\n"
        else:
            text += "Автор\n"
        return text

    def add_url_line(self, entities, text):
        url_entity = self.find_entity(entities, 'url')
        if url_entity:
            text += "[Канал](" + str(url_entity['url']) + ")"
        else:
            text += "Канал\n"
        return text

    @staticmethod
    def get_rate_line(rate=None, path=None):
        if rate is None:
            return 'Рейтинг'
        else:
            sign = "" if len(rate) == 1 else ","
            return "[Рейтинг " + rate[0] + sign + rate[2:] + "](" + "https://telegra.ph/{}".format(path) + ")"

    @staticmethod
    def find_author(text):
        return str(text).rfind('Автор')

    @staticmethod
    def replace_all(text: str, characters):
        for character in characters:
            text = text.replace(character, '\\' + character)
        return text

    @staticmethod
    def find_entity(entities, key):
        for entity in entities:
            if key in entity:
                return entity
        return None

