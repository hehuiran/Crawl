# -*-coding:utf-8-*-标识
import bs4
import requests

from douban.impl.book_parse import NewBookParser, InformationBookParser
from douban.interface.parse import BookParser
from douban.utils import CollectionUtils


class CrawlBook(object):

    def __init__(self, tab_url: str):
        self.__target = tab_url
        self._start_crawl()

    def _start_crawl(self):
        html = requests.get(url=self.__target).text
        self.__bs = bs4.BeautifulSoup(html, 'html.parser')
        div_article = self.__bs.find('div', id='content').find('div', 'article')

        h2s = div_article.find_all('h2')[:2]
        for h2 in h2s:
            title = h2.find('span').string
            print("book-title=" + title)

        parsers = [NewBookParser(), InformationBookParser()]

        div_bds = div_article.find_all('div', 'bd')[:2]
        for i in range(len(div_bds)):
            div_bd = div_bds[i]
            self._crawl_book(div_bd, parsers[i])

    def _crawl_book(self, div_bd: bs4.Tag, parser: BookParser):
        uls = div_bd.find_all('ul')
        items = parser.get_items(uls)
        for i in range(len(items)):
            item = items[i]
            array = parser.get_data(item)
            print('img=' + CollectionUtils.get_list_value(array, 0) + '\n'
                  + 'book_id=' + CollectionUtils.get_list_value(array, 1) + '\n'
                  + 'title=' + CollectionUtils.get_list_value(array, 2) + '\n'
                  + 'author=' + CollectionUtils.get_list_value(array, 3) + '\n'
                  + 'score=' + CollectionUtils.get_list_value(array, 4) + '\n'
                  + 'information_title=' + CollectionUtils.get_list_value(array, 5) + '\n'
                  + 'source=' + CollectionUtils.get_list_value(array, 6) + '\n'
                  + 'information_des=' + CollectionUtils.get_list_value(array, 7) + '\n')
