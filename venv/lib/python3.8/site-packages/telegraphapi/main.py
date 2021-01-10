# _*_ coding: utf-8 _*_

"""
@author: MonsterDeveloper
@contact: https://github.com/MonsterDeveloper
@license: MIT License, see LICENSE file

Copyright (C) 2017
"""

import requests
import json
from .utils import html_to_nodes, nodes_to_html
from .exceptions import TelegraphAPIException

BASE_URL = "https://api.telegra.ph/"

class Telegraph(object):
    def __init__(self, access_token=None):
        """Creates Telegraph object

        :param access_token: Telegraph API Access token
        :type access_token: str
        """
        self.access_token = access_token
    def make_method(self, method_name, data):

        post_request = requests.post(BASE_URL + method_name,
                             data=data)
        if post_request.json()['ok'] is not True:
            raise TelegraphAPIException("Error while executing " + method_name + ": " +
                                        post_request.json()['error'])
        return post_request.json()['result']
    def createAccount(self, short_name, author_name=None, author_url=None):
        """Creates Telegraph account

        :param short_name: Required. Account name, helps users with several accounts remember which they are currently using.
        Displayed to the user above the "Edit/Publish" button on Telegra.ph, other users don't see this name.
        :type short_name: str

        :param author_name: Optional. Default author name used when creating new articles.
        :type author_name: str

        :param author_url: Optional. Default profile link, opened when users click on the author's name below the title.
        Can be any link, not necessarily to a Telegram profile or channel.
        :type author_url: str

        :returns: Account object with the regular fields and an additional access_token field.
        """
        r = self.make_method("createAccount", {
            "short_name": short_name,
            "author_name": author_name,
            "author_url": author_url
        })
        self.access_token = r['access_token']
        return r
    def getAccessToken(self):
        """Get current access token

        :returns: Current access token.
        """
        return self.access_token
    def editAccountInfo(self, short_name=None, author_name=None, author_url=None):
        """Use this method to update information about a Telegraph account.

        :param short_name: Optional. New account name.
        :type short_name: str

        :param author_name: Optional. New default author name used when creating new articles.
        :type author_name: str

        :param author_url: Optional. New default profile link, opened when users click on
        the author's name below the title.
        Can be any link, not necessarily to a Telegram profile or channel.
        :type author_url: str

        :returns: Account object with the default fields.
        """
        return self.make_method("editAccountInfo", {
            "access_token": self.access_token,
            "short_name": short_name,
            "author_name": author_name,
            "author_url": author_url
        })
    def getAccountInfo(self, fields=None):
        """Use this method to get information about a Telegraph account.

        :param fields: List of account fields to return.
        Available fields: short_name, author_name, author_url, auth_url, page_count.
        :type fields: list

        :returns: Account object on success.
        """
        return self.make_method("getAccountInfo", {
            "access_token": self.access_token,
            "fields": json.dumps(fields) if fields else None
        })
    def revokeAccessToken(self):
        """Use this method to revoke access_token and generate a new one, for example,
        if the user would like to reset all connected sessions,
        or you have reasons to believe the token was compromised.

        :returns: Account object with new access_token and auth_url fields.
        """
        return self.make_method("revokeAccessToken", {
            "access_token": self.access_token
        })
    def createPage(self, title, author_name=None, author_url=None,
                   content=None, html_content=None, return_content=False):
        """Use this method to create a new Telegraph page.
        :param title: Required. Page title.
        :type title: str

        :param author_name: Optional. Author name, displayed below the article's title.
        :type author_name: str

        :param author_url: Optional. Profile link, opened when users click on the author's name below the title.
        Can be any link, not necessarily to a Telegram profile or channel.
        :type author_url: str

        :param content: Required. Content of the page in NODES format.

        :param html_content: Optional. Content of the page in HTML format.
        :type html_content: str

        :param return_content: Optional. If true, a content field will be returned in the Page object
        :type return_content: bool

        :returns: Page object.
        """
        if content is None:
            content = html_to_nodes(html_content)
        return self.make_method("createPage", {
            "access_token": self.access_token,
            "title": title,
            "author_name": author_name,
            "author_url": author_url,
            "content": json.dumps(content),
            "return_content": return_content
        })
    def editPage(self, path, title, content=None, html_content=None,
                 author_name=None, author_url=None, return_content=False):
        """Use this method to edit an existing Telegraph page.

        :param path: Required. Path to the page.
        :type path: str

        :param title: Required. Page title.
        :type title: str

        :param content: Required. Content of the page in NODES format.

        :param html_content: Optional. Content of the page in HTML format.
        :type html_content: str

        :param author_name: Optional. Author name, displayed below the article's title.
        :type author_name: str

        :param author_url: Optional. Profile link, opened when users click on the author's name below the title.
        Can be any link, not necessarily to a Telegram profile or channel.
        :type author_url: str

        :param return_content: Optional. If true, a content field will be returned in the Page object.
        :type return_content: bool

        :returns: Page object.
        """
        if content is None:
            content = html_to_nodes(html_content)
        if path is None:
            raise TelegraphAPIException("Error while executing editPage: "
                                        "PAGE_NOT_FOUND")
        r = requests.post(BASE_URL + "editPage/" + path, data={
            "access_token": self.access_token,
            "title": title,
            "content": json.dumps(content),
            "author_name": author_name,
            "author_url": author_url,
            "return_content": return_content
        })
        if r.json()['ok'] is not True:
            raise TelegraphAPIException("Error while executing editPage: " +
                                        r.json()['error'])
        return r.json()['result']
    def getPage(self, path, return_content=True, return_html=True):
        """Use this method to get a Telegraph page.

        :param path: Required. Path to the Telegraph page
        (in the format Title-12-31, i.e. everything that comes after http://telegra.ph/).
        :type path: str

        :param return_content: Optional. If true, content field will be returned in Page object.
        :type return_content: bool

        :param return_html: Optional. If true, content field will be HTML formatted.
        :type return_html: bool

        :returns: Page object on success.
        """
        if path is None:
            raise TelegraphAPIException("Error while executing getPage: "
                                        "PAGE_NOT_FOUND")
        r = requests.post(BASE_URL + "getPage/" + path, data={
            "return_content": return_content
        })
        if r.json()['ok'] is not True:
            raise TelegraphAPIException("Error while executing getPage: " +
                                        r.json()['error'])
        if return_content and return_html:
            r.json()['result']['content'] = nodes_to_html(r.json()['result']['content'])
        return r.json()['result']
    def getPageList(self, offset=0, limit=50):
        """Use this method to get a list of pages belonging to a Telegraph account.

        :param offset: Optional. Sequential number of the first page to be returned.
        :type offset: int

        :param limit: Optional. Limits the number of pages to be retrieved.
        :type limit: int

        :returns: PageList object, sorted by most recently created pages first.
        """

        return self.make_method("getPageList", {
            "access_token": self.access_token,
            "offset": offset,
            "limit": limit
        })
    def getViews(self, path, year=None, month=None, day=None, hour=None):
        """Use this method to get the number of views for a Telegraph article.

        :param path: Required. Path to the Telegraph page
        (in the format Title-12-31, where 12 is the month and 31 the day the article was first published).
        :type path: str

        :param year: Required if month is passed.
        If passed, the number of page views for the requested year will be returned.
        :type year: int

        :param month: Required if day is passed.
        If passed, the number of page views for the requested month will be returned.
        :type month: int

        :param day: Required if hour is passed.
        If passed, the number of page views for the requested day will be returned.
        :type day: int

        :param hour: If passed, the number of page views for the requested hour will be returned.
        :type hour: int

        :return:
        """
        if path is None:
            raise TelegraphAPIException("Error while executing getViews: "
                                        "PAGE_NOT_FOUND")
        r = requests.post(BASE_URL + "getViews/" + path, data={
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
        })
        if r.json()['ok'] is not True:
            raise TelegraphAPIException("Error while executing getViews: " +
                                        r.json()['error'])
        return r.json()['result']
