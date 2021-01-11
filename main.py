import re
import time

from NumDetector import NumDetector
from Numbuster import Numbuster
from telegraph import Telegraph

tgrm_token = "1564102967:AAFglz5bImv28kqjdfhzGzl8AUUK7Emt3TQ"
nb_token = "p6Xu1TGJseMaS1EUj8lF6HK1go4mluzjPUma05YTVypaISE8pV"
tgph_token = "ae8e2911eeaa9cb6b1e32d5bd154bb758fb131999070809c72a34c399d60"

bot = NumDetector(tgrm_token)
numb_api = Numbuster(nb_token)
tgph_api = Telegraph(tgph_token)


def main():
    new_offset = None

    while True:
        last_update = bot.get_last_update(new_offset)
        if last_update is not None and 'message' in last_update:
            # Проверка на отправителя сообщения
            if last_update['message']['from']['username'] != 'GroupAnonymousBot' and last_update['message']['from']['username'] != 'glossy_pink_pony' :
                new_offset = last_update['update_id'] + 1

            elif 'username' in last_update['message']['from'] and last_update['message']['from']['username'] == 'GroupAnonymousBot' and \
                    (find_entity_user(last_update['message']['entities']) and
                     find_entity_user(last_update['message']['entities'])['user']['username'] == 'NumDetector_bot'):
                bot.delete_message(last_update['message']['chat']['id'], last_update['message']['message_id'])
                # new_offset = last_update['update_id'] + 1

            else:
                last_update_id = last_update['update_id']
                message = 'message' if ('message' in last_update) else 'edited_message'
                last_chat_text = last_update[message]['text']
                last_chat_id = last_update[message]['chat']['id']
                last_message_id = last_update[message]['message_id']
                entities = last_update[message]['entities']
                phone_numbers = get_number(last_chat_text)

                if len(phone_numbers) != 0:

                    text_carrier_rate = numb_api.get_text_rate(phone_numbers[0])

                    response = tgph_api.create_page(phone_numbers[0].format() + " • " + text_carrier_rate[1],
                                                    html_content=text_carrier_rate[0])
                    rate_text = "[Рейтинг " + text_carrier_rate[2][0] + "," + text_carrier_rate[2][2:3] + "](" + \
                                'https://telegra.ph/{}'.format(response['path']) + ")"
                else:
                    rate_text = 'Рейтинг \\-'

                result_text = pretty_text_result(last_chat_text, rate_text, entities)

                print(result_text)

                bot.delete_message(last_chat_id, last_message_id)

                time.sleep(10)
                result = bot.send_message(last_chat_id, result_text)
                time.sleep(10)
                if result != -1:
                    new_offset = last_update_id + 1


def find_entity_user(entities):
    for entity in entities:
        if 'user' in entity:
            return entity
    return None


def find_entity_url(entities):
    for entity in entities:
        if 'url' in entity:
            return entity
    return None


def find_entity_phone(entities):
    for entity in entities:
        if 'phone_number' in entity:
            return entity
    return None


def find_author(text):
    return str(text).rfind('Автор')


def pretty_text_result(old_text, rate_text, entities):
    raw_text = old_text[: find_author(old_text)]
    raw_text = replace_all(raw_text, [r'_', r'*', r'[', ']', r'(', ')', r'~', r'`', r'>',
                                      r'#', r'+', r'-', r'=', r'|', r'{', r'}', r'.', r'!'])
    raw_text += rate_text + "\n"
    user_entity = find_entity_user(entities)
    if user_entity:
        raw_text += "[Автор](tg://user?id=" + str(user_entity['user']['id']) + ")\n"
    else:
        raw_text += "Автор\n"

    url_entity = find_entity_url(entities)
    if url_entity:
        raw_text += "[Канал](" + str(url_entity['url']) + ")"
    else:
        raw_text += "Канал\n"

    print(raw_text)
    return raw_text


def replace_all(text: str, characters):
    for character in characters:
        text = text.replace(character, '\\' + character)
    return text


def get_number(text):
    phone_numbers = re.findall(r'(\+?7|8)[( -]?([\d]{3})[) -]{0,2}?([\d]{2}[) -]?[\d]{2}[) -]?[\d]{3}|[\d]{3}'
                               r'[) -]?[\d]{2}[) -]?[\d]{2})', text)
    result_numbers = []
    for i in range(len(phone_numbers)):
        number = ''.join(phone_numbers[i])
        number = re.sub(r'[^0-9]', '', number)
        if number[0] == '8':
            number = '7' + number[1:]

        result_numbers.append(number)
    return result_numbers


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
