import json
import os
from datetime import datetime

import requests

#TODO сделать загрузку полей в конфиг перед публикацией на гите
field_id_phone = 195595
enum_id_phone = 266633

errors = {
    400: 'Bad request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not found',
    500: 'Internal server error',
    502: 'Bad gateway',
    503: 'Service unavailable',
}


class AmoCRM:
    def __init__(self, client_id=None, secret=None, code=None, username=None):
        self.client_id = client_id
        self.secret = secret
        self.code = code
        config = self.get_tokens_from_file()
        self.refresh_token = None if config is None else config['refresh_token']
        self.access_token = None if config is None else config['access_token']
        self.redirect_url = "https://limitless-fjord-01277.herokuapp.com/api"
        self.url = "https://" + username + ".amocrm.ru/"

    def make_request(self, method, method_url, headers=None, data={}):
        response = requests.request(method, self.url + method_url, headers=headers, json=data)
        # print(response.text)
        return response

    def get_first_access_token(self):
        params = {
            "client_id": self.client_id,
            "client_secret": self.secret,
            "grant_type": "authorization_code",
            "code": self.code,
            "redirect_uri": self.redirect_url
        }
        response = self.make_request("post", "oauth2/access_token", {}, params)
        if response.ok:
            return response.json()
        return None

    def get_access_token(self):
        params = {
            "client_id": self.client_id,
            "client_secret": self.secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "redirect_uri": self.redirect_url
        }
        response = self.make_request("post", "oauth2/access_token", {}, params)
        print(response.text)
        if response.ok:
            return response.json()
        return None

    def create_lead(self, contact_id):
        data = [{
            "_embedded": {
                "contacts": [
                    {
                        'id': contact_id
                    }
                ]}}]
        return self.make_request("post", "api/v4/leads", self.get_headers(), data)

    def create_contact(self, phone_number):
        data = [{
            "custom_fields_values": [
                {
                    "field_id": field_id_phone,
                    "values": [
                        {
                            "enum_id": enum_id_phone,
                            "value": phone_number
                        }
                    ]
                }
            ]}]
        return self.make_request("post", "api/v4/contacts", self.get_headers(), data)

    def create_note(self, lead_id, text):
        data = [{
            "entity_id": lead_id,
            "note_type": "common",
            "params": {
                "text": text
            }
        }]
        return self.make_request("post", "api/v4/leads/notes", self.get_headers(), data)

    def create_contact_and_lead(self, phone_number, note):
        if self.get_token() == -1:
            return

        response = self.create_contact(phone_number)
        if response.ok:
            contact_id = response.json()["_embedded"]["contacts"][0]['id']
            resp = self.create_lead(contact_id=contact_id)
            lead_id = resp.json()["_embedded"]["leads"][0]["id"]
            self.create_note(lead_id, note)
        return 0

    def get_token(self):
        config = self.get_tokens_from_file()
        if config is not None:
            print("Сколько сек. назад был заменен токен: " + str(int(datetime.timestamp(datetime.now())) - config['timestamp']))
            print("Время, которое он был годен: " + str(config['expires_in']) + '\n')
            if int(datetime.timestamp(datetime.now())) - config['timestamp'] < config['expires_in']:
                print("Момент, когда токен еще не истек. \n")
                self.refresh_token = config['refresh_token']
                self.access_token = config['access_token']
                return 0
            elif 0 < config['expires_in'] - int(datetime.timestamp(datetime.now())) - config['timestamp'] < 400:
                print("Момент, когда токен почти истек. \n")
                self.access_token = config['access_token']
                self.refresh_token = config['refresh_token']
                self.set_tokens_in_file(config)
        config = self.get_access_token()
        if config is not None:
            print("Момент, когда токен истек. \n")
            self.access_token = config['access_token']
            self.refresh_token = config['refresh_token']
            self.set_tokens_in_file(config)
            return 0
        config = self.get_first_access_token()
        if config is not None:
            print("Момент, когда токена вообще нет. \n")
            self.access_token = config['access_token']
            self.refresh_token = config['refresh_token']
            self.set_tokens_in_file(config)
            return 0
        return -1

    def get_tokens_from_file(self):
        if not os.path.exists('config.txt'):
            return None
        with open('config.txt', 'r') as file:
            if file:
                config = file.read()
                return json.loads(config)

    def set_tokens_in_file(self, config):
        with open('config.txt', 'w') as file:
            config['timestamp'] = int(datetime.timestamp(datetime.now()))
            config['date'] = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")

            file.write(json.dumps(config))

    def get_list_contacts_custom_fields(self):
        return self.make_request("get", "api/v4/contacts/custom_fields", self.get_headers())

    def get_headers(self):
        return {'Authorization': 'Bearer ' + self.access_token}
