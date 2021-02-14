import asyncio
import re
import time

from telethon import TelegramClient
from AmoCRM import AmoCRM
from NumDetector import NumDetector
from Numbuster import Numbuster
from telegraph import Telegraph

from Textmaker import Textmaker

telegram_token = "1564102967:AAFglz5bImv28kqjdfhzGzl8AUUK7Emt3TQ"
nb_token = "JjgsIAHlzFGcyPJr0tCpWpnxkWUiv0B1JoOy87XvSnEv4bWJaR"
tgph_token = "ae8e2911eeaa9cb6b1e32d5bd154bb758fb131999070809c72a34c399d60"

amocrm = AmoCRM(client_id="048231f3-172f-471f-874e-cd50e3f42db0",
                secret="3NuQRwEzbr1H1JCe7YtwTgL5DVxWBD2TNqMc2VeXEz5fY6jRUeTj3oYdqecOcm7K",
                code="def5020056fe97fed6f5c5cff4a9285ce01a65c8adec97b20f1ff49a4bb1ff3f9044f312b5e3996c27994941a980522da7b6c145d6ada3cb7d924488b6a69a4c86b716bec0fceeb2d8f78f6db3f579c893fc558f7333a289c66aa04677a261cfcbbb474a07c9286fa596e30cef2d620724ba732243951dc990c5f2a614081def6d7d77388eb0bd127674a5560d07c3cf3e1e9c9867244210e3de3c12d662def05dfc1b2e3aa6fa51c3998eeb357a75f3b13dc9aa77311df33870174a395bb7709e213d17e54cf0ec6393ceb46152aaef45b6e82e8269a0f6679073c312a26b9ce5f259c39e62bbbe78d3433bc3832ba1bf39b1ec837ea962fa75b817481ee7ea524d100b2c8749334e683ffbec9578eb355f71741797cf3d7e35d46765f213c2d58ce08fb1bb06ba4aa928d8aae89cb84d105abb1f69300af5ffdaf3af76842f8dc32783f99e0e914cb4aab5afaabe7854b50f67dc3fa9b8528f300f80dd6fb8dfdee4f8da24f9e1b1e6a153ed50252f96d74b4329bbe2df4521ec1c40c610a06274c5ab8f6720e694a4f6cf583dcc98bbd7db1cbcc7bc976577862bcc27d8c6bf3fb80718fc81d5cadbd9038567d713b8d2b3e3b645bd323022cd7ec01c4f817af9599df728b93f4b2d8a8784fdd7e65bf8922569179d1b8001",
                username="recoru")

bot = NumDetector(telegram_token)
numbaster = Numbuster(nb_token)
telegraph = Telegraph(tgph_token)
api_id = 2181011
api_hash = 'ae2924cd92241aaa3157218feb7032cf'
client = TelegramClient('session_name', api_id, api_hash)
textmaker = Textmaker(client)


def main():
    new_offset = None

    while True:

        last_update = bot.get_last_update(new_offset)
        amocrm.get_token()
        # amocrm.get_first_access_token()
        # bot.delete_message(-1001213300671, 2474)

        if last_update is not None and 'message' in last_update:
            if 'text' not in last_update['message'] or len(re.findall('/start', last_update['message']['text'])) > 0 or 'entities' not in last_update['message']:
                new_offset = last_update['update_id'] + 1
            # elif last_update['message']['from']['username'] == 'NumDetector_bot':
            #     new_offset = last_update['update_id'] + 1

            else:
                last_update_id = last_update['update_id']
                message = 'message' if ('message' in last_update) else 'edited_message'
                last_chat_text = last_update[message]['text']
                last_chat_id = last_update[message]['chat']['id']
                last_message_id = last_update[message]['message_id']
                entities = last_update[message]['entities']
                phone_number = get_number(last_chat_text, entities)

                if phone_number:
                    text_carrier_rate = numbaster.get_text_for_telegraph(phone_number)
                    response = telegraph.create_page(phone_number.format() + " • " + text_carrier_rate[1],
                                                     html_content=text_carrier_rate[0])
                    rate_line = textmaker.get_rate_line(text_carrier_rate[2], response['path'])
                else:
                    rate_line = textmaker.get_rate_line()

                text_for_amocrm = textmaker.get_text_for_amocrm(last_chat_text, rate_line, entities)

                if phone_number:
                    result_lead = amocrm.create_contact_and_lead(phone_number, text_for_amocrm)
                else:
                    result_lead = amocrm.create_contact_and_lead(None, text_for_amocrm)

                if result_lead == -1:
                    continue

                text_for_telegram = textmaker.get_text_for_telegram(last_chat_text, rate_line, entities)
                bot.delete_message(last_chat_id, last_message_id)
                result = bot.send_message(last_chat_id, text_for_telegram)


                time.sleep(10)
                if result != -1:
                    new_offset = last_update_id + 1


def get_number(text, entities):
    phone_entity = None
    # for entity in entities:
    #     if 'type' in entity and entity['type'] == 'phone_number':
    #         phone_entity = entity

    # if phone_entity:
    #     phone_number = text[phone_entity['offset']:phone_entity['offset'] + phone_entity['length']]
    #     phone_number = ''.join(phone_number)
    #     phone_number = re.sub(r'[^0-9]', '', phone_number)
    #     if phone_number[0] == '8':
    #         phone_number = '7' + phone_number[1:]
    #     return phone_number

    phone_number = re.findall(r'(\+?[\d][\d() -]{9,15})', text)
    # phone_number = re.findall(r'((\+?7|\+?9|8)[( -]{
    # 0,2}([\d]{3})[) -]{0,2}([\d]{2,3}[( -]{0,2}[\d]{2,3}[) -]{0,2}[\d]{2,3}))', text)

    if phone_number:
        phone_number = ''.join(phone_number[0])
        phone_number = re.sub(r'[^0-9]', '', phone_number)
        if phone_number[0] == '8':
            phone_number = '7' + phone_number[1:]
        return phone_number
    return None


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
