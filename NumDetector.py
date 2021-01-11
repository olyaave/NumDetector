import requests
import time


class NumDetector:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def make_request(self, method, **params):
        resp_json = requests.get(self.api_url + method, params).json()
        print(resp_json)
        if resp_json['ok']:
            result_json = resp_json['result']
            return result_json
        elif resp_json['error_code'] == 429:
            counter = 3
            while counter > 0 or resp_json['ok'] == False:
                time.sleep(resp_json['parameters']['retry_after'] + 10)
                print(resp_json['parameters']['retry_after'] + 10)
                resp_json = requests.get(self.api_url + method, params).json()
                print(resp_json)
                counter -= 1
            return resp_json if resp_json['ok'] else -1
        else:
            return -1

    def get_updates(self, offset=None, limit=0, timeout=30):
        params = {'timeout': timeout, 'offset': offset, 'limit': limit}
        return self.make_request('getUpdates', **params)

    def send_message(self, chat_id, text, parse_mode='MarkdownV2'):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
        return self.make_request('sendMessage', **params)

    def edit_message(self, chat_id, message_id, text):
        params = {'chat_id': chat_id, 'message_id': message_id, 'text': text}
        return self.make_request('editMessageText', **params)

    def delete_message(self, chat_id, message_id):
        params = {'chat_id': chat_id, 'message_id': message_id}
        return self.make_request('deleteMessage', **params)

    def get_last_update(self, offset):
        get_result = self.get_updates(offset)
        if get_result != -1 and len(get_result) > 0:
            last_update = get_result[len(get_result) - 1]
            return last_update
