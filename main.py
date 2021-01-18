import re
import time

from AmoCRM import amoCRM
from NumDetector import NumDetector
from Numbuster import Numbuster
from telegraph import Telegraph

telegram_token = "1564102967:AAFglz5bImv28kqjdfhzGzl8AUUK7Emt3TQ"
nb_token = "p6Xu1TGJseMaS1EUj8lF6HK1go4mluzjPUma05YTVypaISE8pV"
tgph_token = "ae8e2911eeaa9cb6b1e32d5bd154bb758fb131999070809c72a34c399d60"

amocrm = amoCRM(client_id="55ad718d-9e8a-4f73-b00b-2c2cd01c4a7e",
                secret="zo43cack3wPDLM2EFx7zrAsyC61ly5QRyEQPQvCE3BxuSWiZOfLCAyloaZ3FKiNi",
                code="def5020076bbef283a2ced75ae8aad00528409f7bd5fc13fdeb8457f2922d501696e58eea6b31985db930674828efeb539b71121976132c7733cde39a7935c5bcbf497e965ad2b635630b93961e99ec085ec37d6c0896b8dd0fad891a697357f179cf50449b979d1bd3f5fbaf535b0b7d265b4848b9cf016cc3378f5e751785851fbd7248f5bc86d2cebed3ea691946f6058abda806e20f4d7d26905ad9a7e86148eff1d6201b7ddd77488533e7462f2871d10fa907284a17d74d7036a41aec69563487acd4ba9f4be43c484cf648b6b4c170ef3423983db6cbb100ca407b03212fceb4b1c04632d6865d991d5d22c849dd849f9100a08d23759ffebb23ed03cff3bf6d601aaa5464753fd4a77ee7b1f7e3e146d29f4fe3623a10e0ae7a0deb50aae432cb1c889a6e0968c58bac32a025b3248c3106938c8f9bc931ff5b4c043567262efe9c46152c2b290cc439899a1ae814de081c6004a1aedd1762c18ea4ac07bfec11fcbc32a99d7e1fc7fc254c76ea1e67217727dd020394b0865dde1e16f4c483f47a9e42b19aede0fd4a462ac60f43f4bf1ece0654d3133716550fac9f908401d8d8411937215594c29a7b44f7ea2a441d810dc3e06acfa71c152b92ff8977105f6bb28ca9a6bc1d98e82adc2df46b3f82a35e3257421",
                username="averinaos")
# amocrm.get_first_access_token()


bot = NumDetector(telegram_token)
numbaster = Numbuster(nb_token)
telegraph = Telegraph(tgph_token)



def main():
    new_offset = None

    while True:
        last_update = bot.get_last_update(new_offset)
        if last_update is not None and 'message' in last_update:
            print(last_update)
            if last_update['message']['from']['username'] != 'GroupAnonymousBot' and last_update['message']['from'][
                'username'] != 'glossy_pink_pony':
                new_offset = last_update['update_id'] + 1

            else:
                last_update_id = last_update['update_id']
                message = 'message' if ('message' in last_update) else 'edited_message'
                last_chat_text = last_update[message]['text']
                last_chat_id = last_update[message]['chat']['id']
                last_message_id = last_update[message]['message_id']
                entities = last_update[message]['entities']
                phone_numbers = get_number(last_chat_text)

                if len(phone_numbers) != 0:
                    text_carrier_rate = numbaster.get_text_for_telegraph(phone_numbers[0])
                    response = telegraph.create_page(phone_numbers[0].format() + " • " + text_carrier_rate[1],
                                                     html_content=text_carrier_rate[0])
                    rate_text = "[Рейтинг " + text_carrier_rate[2][0] + "," + text_carrier_rate[2][2:] + "](" + \
                                'https://telegra.ph/{}'.format(response['path']) + ")"
                else:
                    rate_text = 'Рейтинг \\-'

                result_text = pretty_text_telegram(last_chat_text, rate_text, entities)
                # if len(phone_numbers) > 0:
                # amocrm.create_contact_and_lead(phone_numbers[0], result_text)
                # else:
                # amocrm.create_contact_and_lead(None, result_text)

                bot.delete_message(last_chat_id, last_message_id)

                time.sleep(5)
                result = bot.send_message(last_chat_id, result_text)
                time.sleep(5)
                if result != -1:
                    new_offset = last_update_id + 1


def find_entity(entities, key):
    for entity in entities:
        if key in entity:
            print(entity)
            return entity
    return None


def pretty_text_telegram(old_text, rate_text, entities):
    raw_text = replace_all(old_text[: find_author(old_text)], [r'_', r'*', r'[', ']', r'(', ')', r'~', r'`', r'>',
                                                               r'#', r'+', r'-', r'=', r'|', r'{', r'}', r'.', r'!'])
    raw_text += rate_text + "\n"
    user_entity = find_entity(entities, 'user')
    if user_entity:
        raw_text += "[Автор](tg://user?id=" + str(user_entity['user']['id']) + ")\n"
    else:
        raw_text += "Автор\n"

    url_entity = find_entity(entities, 'url')
    if url_entity:
        raw_text += "[Канал](" + str(url_entity['url']) + ")"
    else:
        raw_text += "Канал\n"
    return raw_text


def find_author(text):
    return str(text).rfind('Автор')


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
