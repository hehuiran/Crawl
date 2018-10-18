# -*-coding:utf-8-*-标识
import bs4
import requests


class CrawlBook(object):

    def __init__(self, tab_url: str):
        self.__target = tab_url
        self._start_crawl()

    def _start_crawl(self):
        html = requests.get(url=self.__target).text
        self.__bs = bs4.BeautifulSoup(html, 'html.parser')
        div_article = self.__bs.find('div', id='content').find('div', 'article')
        # self.__bs.children
        h2s = div_article.find_all('h2')
        # divs = div_article.children
        # print("book-divs-type=" + str(type(divs)))
        for h2 in h2s:
            title = h2.find('span').string
            print("book-title=" + title)
