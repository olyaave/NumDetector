class Textmaker:

    def pretty_text_telegram(self, old_text, rate_text, entities):
        raw_text = self.replace_all(old_text[: self.find_author(old_text)], [r'_', r'*', r'[', ']', r'(', ')', r'~',
                                                                             r'`', r'>', r'#', r'+', r'-', r'=', r'|',
                                                                             r'{', r'}', r'.', r'!'])
        raw_text += rate_text + "\n"
        user_entity = self.find_entity(entities, 'user')
        if user_entity:
            raw_text += "[Автор](tg://user?id=" + str(user_entity['user']['id']) + ")\n"
        else:
            raw_text += "Автор\n"

        url_entity = self.find_entity(entities, 'url')
        if url_entity:
            raw_text += "[Канал](" + str(url_entity['url']) + ")"
        else:
            raw_text += "Канал\n"
        return raw_text

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
                print(entity)
                return entity
        return None
