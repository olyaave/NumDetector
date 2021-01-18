import requests
import signatures

requests.adapters.DEFAULT_RETRIES = 500


class Numbuster:
    def __init__(self, access_token):
        self.access_token = access_token
        self.api_url = 'https://api.numbuster.com/api/'
        self.headers = {'Host': 'api.numbuster.com',
                        'User-Agent': 'okhttp/3.12.1',  # 'okhttp/3.12.1',
                        'Accept-Encoding': 'gzip',
                        'Connection': 'keep-alive'}

    def _v6_old_phone(self, phone, locale='ru'):
        timestamp = signatures.get_timestamp()
        cnonce = signatures.get_cnonce()
        signature = signatures.signature_v6_old_phone(phone, self.access_token, cnonce, timestamp, locale)
        url = self.api_url + f'v6/old/phone/{phone}?access_token={self.access_token}&locale={locale}&timestamp={timestamp}&signature={signature}&cnonce={cnonce}'
        data = requests.get(url, headers=self.headers)
        return data.json()

    def pretty_json(self, resp_json):
        text = "<p><strong>РЕЙТИНГ " + str(resp_json['index']) + "</strong></p>"
        text += "<p>📍 " + str(resp_json['region']) + "</p>"
        if resp_json['phoneType'] == 'PERSON':
            text += "<p>🧍‍♂️  Человек</p>"
        else:
            text += "<p>🧍‍♂️  " + resp_json['phoneType'] + "</p>"
        text += "<p>🚫  Блокировки - " + str(resp_json['bans']) + "</p>"
        text += '<br>'
        text += '<p><strong>Записи в контактах:</strong></p>'
        if len(resp_json['contacts']) == 0:
            text = '<p>Записей не найдено</p>'
        for name in resp_json['contacts']:
            text += '<p>' + str(name['firstName']) + " " + str(name['lastName']) + '</p>'
        text_carrier_rate = [text, str(resp_json['carrier']), str(resp_json['index'])]
        return text_carrier_rate

    def get_text_for_telegraph(self, phone):
        response = self._v6_old_phone(phone)
        text_and_rate = self.pretty_json(response)
        return text_and_rate
