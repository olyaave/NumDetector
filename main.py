import asyncio
import re
import time

from telethon import TelegramClient
from AmoCRM import AmoCRM
from NumDetector import NumDetector
from Numbuster import Numbuster
from telegraph import Telegraph

from Textmaker import Textmaker

telegram_token = ""
nb_token = ""
tgph_token = ""

amocrm = AmoCRM(client_id="",
                secret="",
                code="",
                username="")

bot = NumDetector(telegram_token)
numbaster = Numbuster(nb_token)
telegraph = Telegraph(tgph_token)
api_id = 2181011
api_hash = 'ae2924cd92241aaa3153218feb7032cf'
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
