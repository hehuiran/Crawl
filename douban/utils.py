# -*-coding:utf-8-*-标识
import re


class CollectionUtils(object):

    def __init__(self):
        raise RuntimeError("u can't init me")

    @staticmethod
    def get_list_value(array: list, index: int):
        size = len(array)
        return str(array[index]) if index < size else ''


class StringUtils(object):

    def __init__(self):
        raise RuntimeError("u can't init me")

    @staticmethod
    def filter_space_and_enter(value: str):
        return re.sub('[\n\xa0 ·]', '', value)
