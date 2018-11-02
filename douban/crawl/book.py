# -*-coding:utf-8-*-标识
import bs4
import requests

from douban.impl.book_parse import NewBookParser, InformationBookParser, AttentionBookParser
from douban.interface.parse import BookParser
from douban.sql import BookCategory, BookSimple, SqlFactory, sql_Factory
from douban.utils import CollectionUtils


class CrawlBook(object):

    def __init__(self, tab_url: str):
        self.__target = tab_url
        self.__book_array = []
        self._start_crawl()

    def _start_crawl(self):
        html = requests.get(url=self.__target).text
        self.__bs = bs4.BeautifulSoup(html, 'html.parser')
        div_content = self.__bs.find('div', id='content')
        div_article = div_content.find('div', 'article')

        h2s = div_article.find_all('h2')[:3]
        for h2 in h2s:
            title = h2.find('span').string
            self.__book_array.append(BookCategory(str(title)))

        div_block = div_content.find('div', 'aside').find('div', 'block5')
        top_title = div_block.find('span').string
        self.__book_array.append(BookCategory(str(top_title)))

        div_block

        parsers = [NewBookParser(), InformationBookParser(), AttentionBookParser()]

        div_bds = div_article.find_all('div', 'bd')[:3]
        for i in range(len(div_bds)):
            book_category = self.__book_array[i]
            div_bd = div_bds[i]
            self._crawl_book(div_bd, parsers[i], book_category)

        session = sql_Factory.get_session()
        print('session是')
        print(session)
        session.add_all(self.__book_array)
        # div_block = div_content.find('div', 'aside').find('div', 'block5')
        # div_block.find('span').string

    def _crawl_book(self, div_bd: bs4.Tag, parser: BookParser, book_category: BookCategory):
        uls = div_bd.find_all('ul')
        items = parser.get_items(uls)
        for i in range(len(items)):
            item = items[i]
            array = parser.get_data(item)
            if array is not None:
                book_simple = BookSimple(img=CollectionUtils.get_list_value(array, 0),
                                         book_id=CollectionUtils.get_list_value(array, 1),
                                         title=CollectionUtils.get_list_value(array, 2),
                                         author=CollectionUtils.get_list_value(array, 3),
                                         score=CollectionUtils.get_list_value(array, 4),
                                         information_title=CollectionUtils.get_list_value(array, 5),
                                         source=CollectionUtils.get_list_value(array, 6),
                                         information_des=CollectionUtils.get_list_value(array, 7))
                book_category.book_simple_array.append(book_simple)
                # print('img=' + CollectionUtils.get_list_value(array, 0) + '\n'
                #       + 'book_id=' + CollectionUtils.get_list_value(array, 1) + '\n'
                #       + 'title=' + CollectionUtils.get_list_value(array, 2) + '\n'
                #       + 'author=' + CollectionUtils.get_list_value(array, 3) + '\n'
                #       + 'score=' + CollectionUtils.get_list_value(array, 4) + '\n'
                #       + 'information_title=' + CollectionUtils.get_list_value(array, 5) + '\n'
                #       + 'source=' + CollectionUtils.get_list_value(array, 6) + '\n'
                #       + 'information_des=' + CollectionUtils.get_list_value(array, 7) + '\n')
