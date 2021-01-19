class Textmaker:

    def get_text_for_telegram(self, old_text, rate_text, entities):
        text = self.replace_all(old_text[: self.find_author(old_text)], [r'_', r'*', r'[', ']', r'(', ')', r'~',
                                                                             r'`', r'>', r'#', r'+', r'-', r'=', r'|',
                                                                             r'{', r'}', r'.', r'!'])
        text += rate_text + "\n"
        user_entity = self.find_entity(entities, 'user')
        if user_entity:
            text += "[Автор](tg://user?id=" + str(user_entity['user']['id']) + ")\n"
        else:
            text += "Автор\n"

        text = self.add_url_line(entities, text)
        return text

    def get_text_for_amocrm(self, old_text, rate_text, entities):
        text = old_text[: self.find_author(old_text)] + rate_text + "\n"
        user_entity = self.find_entity(entities, 'user')
        if user_entity and 'username' in user_entity['user']:
            text += "[Автор](https://t.me/" + str(user_entity['user']['username']) + ")\n"
        else:
            text += "Автор\n"

        text = self.add_url_line(entities, text)
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
            return "[Рейтинг " + rate[0] + "," + rate[2:] + "](" + "https://telegra.ph/{}".format(path) + ")"

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

