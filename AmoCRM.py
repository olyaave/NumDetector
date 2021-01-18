import json
from datetime import datetime

import requests

field_id_phone = 513405
enum_id_phone = 307917
field_id_note = 677323

errors = {
    400: 'Bad request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not found',
    500: 'Internal server error',
    502: 'Bad gateway',
    503: 'Service unavailable',
}


class amoCRM:
    def __init__(self, client_id=None, secret=None, code=None, username=None):
        self.client_id = client_id
        self.secret = secret
        self.code = code
        self.refresh_token = None
        self.access_token = None
        self.redirect_url = "https://limitless-fjord-01277.herokuapp.com/api"
        self.url = "https://" + username + ".amocrm.ru/"

    def make_request(self, method, method_url, headers=None, data={}):
        response = requests.request(method, self.url + method_url, headers=headers, json=data)
        print(response.text)

        if response.status_code in errors:
            print("ERROR: " + errors[response.status_code] + '\n')
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
            resp_json = response.json()
            self.access_token = resp_json['access_token']
            self.refresh_token = resp_json['refresh_token']
            self.set_refresh_token_in_file(resp_json['refresh_token'])
            return "OK"
        return "ERROR"

    def get_access_token(self):
        self.refresh_token = self.get_refresh_token_from_file()

        params = {
            "client_id": self.client_id,
            "client_secret": self.secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "redirect_uri": self.redirect_url
        }
        response = self.make_request("post", "oauth2/access_token", {}, params)
        if response.ok:
            resp_json = response.json()
            self.access_token = resp_json['access_token']
            self.refresh_token = resp_json['refresh_token']
        return response

    def create_lead(self, contact_id):
        data = [{
            "_embedded": {
                "contacts": [
                    {
                        'id': contact_id
                    }
                ]}}]
        print(data)
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
        print(data)
        return self.make_request("post", "api/v4/contacts", self.get_headers(), data)

    def create_note(self, lead_id, text):
        data = [{
                "entity_id": lead_id,
                "note_type": "common",
                "params": {
                    "text": text
                }
                }]
        print(data)
        return self.make_request("post", "api/v4/leads/notes", self.get_headers(), data)

    def create_contact_and_lead(self, phone_number, note):
        self.refresh_token = self.get_refresh_token_from_file()

        result = self.get_access_token()
        if not result.ok:
            result = self.get_first_access_token()

        response = self.create_contact(phone_number)
        if response.ok:
            contact_id = response.json()["_embedded"]["contacts"][0]['id']
            resp = self.create_lead(contact_id=contact_id)
            lead_id = resp.json()["_embedded"]["leads"][0]["id"]
            self.create_note(lead_id, note)
        return 0

    def get_refresh_token_from_file(self):
        with open('refresh_token.txt', 'r') as file:
            return file.read()

    def set_refresh_token_in_file(self, refresh_token):
        with open('refresh_token.txt', 'w') as file:
            file.write(refresh_token)

    def get_list_contacts_custom_fields(self):
        return self.make_request("get", "api/v4/contacts/custom_fields", self.get_headers())

    def get_headers(self):
        return {'Authorization': 'Bearer ' + self.access_token}

# if __name__ == '__main__':
#     api = amoCRM(client_id="876aa1e4-c4a7-49a1-92ab-0d895f8a9b9f",
#                  secret="7gkZMFjCK0Jqj3G5SQ8aWeuYlM3BZkE0jbqVgr08TGUjGGwx4hEv5gKXF1fwiPfD",
#                  code="def502000be898fae799dcbcfc16010dab7e493e439bc0ba4b9079857f7edae57dedab46d847b702b006f6fd38228766f01b572b733459b3ab6ffc0a80e4eba52b63e28d71d7de749379e161d3549ccccfd2f08c59c4d49e01df5e8a7368aac8e616b851f04bb724c9a7b417c896c07e35accda19abbbb1e10623e90d02fd4cda646ca1d16f86115cd75dfd1c3f2ddb900ebee922d5d0cfc4ff929fc18f3032741f902087377b58b5ba04ec770443b15f4453d7715da480f0c0748233d4639061a5fcbc70fabfec3c7534544d70f570beb6b8f797b08dfceb8eed91d82fdc2125f43386b64cb5dcf4c2eb173f3b3c088c0f3260b1596bb97a889498bdfa1c82ed1d776908261de3d97de6a3b326b30c910e54e8842d999ae7f9605dda3a7334a504c93d7b1db0f77295d69d1e5a4b6fff6fa45dd63528d7a952cb9e7740b36e61e29dd6c450c328d09e96663f88c97e5183220b12fc2c4b1b0a7e5221ffcd5237b37a735651d057be6b5265b976483fc26f6352bce13d6ff0dfa0fa347a04c59b21a0e5f1435529360794ce3b9d290ad33e878c8591895e537bcffdaf6926488fc0900a9b156986be7b2d15602b109630297c9272c5fc2d4a7fc1b6a5d615348c5242e3b7382599f25369b383d9457ce1308516a8141ad505022",
#                  username="averinaos")
#
#     api.get_access_token()
#     # api.create_contact_and_lead("89230323243", "hello sdfsdfsdfsd")
#     # api.get_list_contacts_custom_fields()
#     # print(int(datetime.timestamp(datetime.now())))
