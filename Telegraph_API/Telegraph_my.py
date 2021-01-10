import json
from urllib.request import urlopen
from urllib.parse import urlencode


class Telegraph:
    def __init__(self, token=None):
        self.token = token

    def make_request(self, method, **params):
        url = 'https://api.telegra.ph/' + method
        params = {k: v if isinstance(v, str) else json.dumps(v) for k, v in params.items()}
        url_address = urlopen(url + '?' + urlencode(params))
        r = json.loads(url_address.read())
        if not r['ok']:
            raise ValueError(str(r))
        return r['result']

    # def _get_access_token(self, short_name):
    #     return self._make_request('createAccount', short_name=short_name)['access_token']

    def create_page(self, **params):
        return self.make_request('createPage', **params)

    def get_new_page(self, content):
        # token = get_access_token("1337")

        page = self.create_page(access_token=self.token,
                                title="NumDetector",
                                content=content)
        print(page['url'])
        return page['url']
