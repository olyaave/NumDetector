import re
import time

from AmoCRM import amoCRM
from NumDetector import NumDetector
from Numbuster import Numbuster
from telegraph import Telegraph

from Textmaker import Textmaker

telegram_token = "1564102967:AAFglz5bImv28kqjdfhzGzl8AUUK7Emt3TQ"
nb_token = "p6Xu1TGJseMaS1EUj8lF6HK1go4mluzjPUma05YTVypaISE8pV"
tgph_token = "ae8e2911eeaa9cb6b1e32d5bd154bb758fb131999070809c72a34c399d60"

amocrm = amoCRM(client_id="efc03ed1-c1b2-46a7-8af7-22159866ba3a",
                secret="sMTD3vyRDJuC1RLWuQpA9eaUuDIe2MPVcWKNXtWUDPP7ZhiHnHG7gjqT89cNWScA",
                code="def502008efbf9e9330d964c8108736fe96f26ae6b407f2174cd0b3efbd6306b4a92c3022bbbd6a627ad7ec50071d7b89084aaa9c1fa75cea8797d6c3032adf2d13d1358e47275fdf4bff1101ee8b0ee1f017f33a80e27a797a0bb54c174384bfcf7aed5fbdf064fbb4b8a86d8c0d815f11214b1c4c29e30f361838a5de1402de2d640c8f747ad53c5cf09063eaa01a0aa820f79a961fdcb060d4d56f64def9ace2de403cadf81286fc46b154b836a5bda3b2152f1eac54d592d4bd70d92731c31747d3426f14dacec7a50b033f2a95d0965692ca7cc333577dc8ee0c0972c815b814598919d3f4a16b1c6e56d44c4cf317d551e02303e911a88901d20d0aff0466d9caee29a22ec9be1b19db45f25e1973f2475fcb896856f55a1c272aa1753c2a6165a555f79f8716c65f1f3d93fcbf04d3867d9e337b7657976b1a721edaa00772c1bafe9a99e8d50096278dc4b6d8005a73083447d1211a205f5980ad06eadc88ffa71dc40c5b908aa6693870e175983d6b53f4270f7ffe6fc6b4779b4eb010c99114341e1bbce138dc1bd1107f5f9d44f86c38f6ead362227837189b6008f8870a3eabde53d42d75a5c630320c818ecdb6d05030b12d1ad788011a2f77e696257091973067ddfd1e28eacc764b2c449a0ed1d5e6713e0be",
                username="recoru")

bot = NumDetector(telegram_token)
numbaster = Numbuster(nb_token)
telegraph = Telegraph(tgph_token)
textmaker = Textmaker()


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
                    rate_line = textmaker.get_rate_line(text_carrier_rate[2], response['path'])
                else:
                    rate_line = textmaker.get_rate_line()

                text_for_telegram = textmaker.get_text_for_telegram(last_chat_text, rate_line, entities)
                bot.delete_message(last_chat_id, last_message_id)
                result = bot.send_message(last_chat_id, text_for_telegram)

                text_for_amocrm = textmaker.get_text_for_amocrm(last_chat_text, rate_line, entities)
                if len(phone_numbers) > 0:
                    amocrm.create_contact_and_lead(phone_numbers[0], text_for_amocrm)
                else:
                    amocrm.create_contact_and_lead(None, text_for_amocrm)

                # time.sleep(5)
                if result != -1:
                    new_offset = last_update_id + 1


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
