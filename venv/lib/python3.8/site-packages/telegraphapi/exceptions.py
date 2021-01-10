# _*_ coding: utf-8 _*_

"""
@author: MonsterDeveloper
@contact: https://github.com/MonsterDeveloper
@license: MIT License, see LICENSE file

Copyright (C) 2017
"""

class TelegraphAPIException(Exception):
    pass


class ParsingException(Exception):
    pass


class NotAllowedTag(ParsingException):
    pass


class InvalidHTML(ParsingException):
    pass
