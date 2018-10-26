# -*-coding:utf-8-*-标识
from abc import ABCMeta, abstractmethod, ABC

import bs4


class Parser(metaclass=ABCMeta):
    # 抽象方法
    @abstractmethod
    def get_data(self, item):
        pass


# 首页解析
class HomeParser(Parser, ABC):

    def get_items(self, ul: bs4.Tag):
        return ul.find_all('li')


class BookParser(Parser, ABC):
    def get_items(self, uls: list):
        items = []
        for ul in uls:
            lis = ul.find_all('li')
            for li in lis:
                items.append(li)
        return items
