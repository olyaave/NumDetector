import asyncio
import re
import time

from telethon import TelegramClient
from telethon.tl.types import PeerUser
from AmoCRM import AmoCRM
from NumDetector import NumDetector
from Numbuster import Numbuster
from telegraph import Telegraph

from Textmaker import Textmaker

telegram_token = "1564102967:AAFglz5bImv28kqjdfhzGzl8AUUK7Emt3TQ"
nb_token = "JjgsIAHlzFGcyPJr0tCpWpnxkWUiv0B1JoOy87XvSnEv4bWJaR"
tgph_token = "ae8e2911eeaa9cb6b1e32d5bd154bb758fb131999070809c72a34c399d60"

amocrm = AmoCRM(client_id="2d5141e3-aa54-4007-8c8a-b132f7711368",
                secret="xVt5wbpkRBw4X5dOKbSYeudbGvlU2n5aeSOxDA72063wYfcJpmicjFpu4I6Y91vL",
                code="def50200965e700ce541a4d9d38c12572ce795d62aaa9138491e08dd86a3953bc0b828a5ae01b605081e36c3a0d8f9e8c5e0ae51708f8f848c1e7c1a176debeb7f1c3053f6e1c24eb427786afc8913a50cc41c3ff4ff87b26baa1f964e9e91cff443d7baecaab112c4f11bd09c5aee90d1856a040e5f4cb05fc1dbb7e5dd74d3161ab7f784262c5ab2213bc9c5fe1e03913801bbb0305ac3f0c75c5a14c626ab97c36559e707e12e4df15d9527603b2c9341d2d7a4993c793a4de444a0f37ed377ca80a7a0d56d1a7afceb46d56676a842daf6e721c86b424132f40fa8645847ea8808a0859119d531e9371042188ff538b27b8e3ebb5cbf850b233fb83bd9d6d09aebcf2819ea26f4c34fbc0e62495608d49a48a027f45784999018b977768aae616dd502eb58932dd9f757ca53f63015015e08efea457e821d484a6f506a3015f0089135e5e14e565970929284638b11b822dae6896c09d464996719ecb08802cf53b59947b769407764e85cbe5c1a9a399aa42878b372c8d7a7f56e842fe7c43ec9f417960eb13782649b111afa42472a69750bfc6e4229c7ab3790e1284f1dce65caf474ac1a16cd39a59d0f3bae6edf30e1538563bdd367876b7130ad301d0f8f1717f398d80a5f5444795ce812590b76f423878777c998",
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

        if last_update is not None and 'message' in last_update:
            if 'text' not in last_update['message'] or len(re.findall('/start', last_update['message']['text'])) > 0:
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

                text_for_telegram = textmaker.get_text_for_telegram(last_chat_text, rate_line, entities)
                bot.delete_message(last_chat_id, last_message_id)
                result = bot.send_message(last_chat_id, text_for_telegram)

                text_for_amocrm = textmaker.get_text_for_amocrm(last_chat_text, rate_line, entities)

                if phone_number:
                    amocrm.create_contact_and_lead(phone_number, text_for_amocrm)
                else:
                    amocrm.create_contact_and_lead(None, text_for_amocrm)

                time.sleep(10)
                # if result != -1:
                new_offset = last_update_id + 1


def get_number(text, entities):
    phone_entity = None
    for entity in entities:
        if 'type' in entity and entity['type'] == 'phone_number':
            phone_entity = entity

    if phone_entity:
        phone_number = text[phone_entity['offset']:phone_entity['offset'] + phone_entity['length']]
        phone_number = ''.join(phone_number)
        phone_number = re.sub(r'[^0-9]', '', phone_number)
        if phone_number[0] == '8':
            phone_number = '7' + phone_number[1:]
        return phone_number

    phone_number = re.findall(r'(\+?7|8)[( -]{0,2}([\d]{3})[) -]{0,2}([\d]{2,3}[( -]{0,2}[\d]{2,3}[) -]{0,2}[\d]{2,3})', text)
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
