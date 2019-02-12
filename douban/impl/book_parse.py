# -*-coding:utf-8-*-标识
import re

import requests
from bs4 import BeautifulSoup

from douban.interface.parse import BookParser
from douban.utils import StringUtils


class NewBookParser(BookParser):

    def get_data(self, item):
        img = item.find('img').get('src')
        a_tag = item.find('a')
        book_id = re.sub('\D', '', a_tag.get('href'))
        title = a_tag.get('title')
        author = StringUtils.filter_space_and_enter(item.find('div', 'author').string)
        return [img, book_id, title, author]


class InformationBookParser(BookParser):

    def get_data(self, item):
        url = item.find('a').get('href')  # type:str
        information_title = item.find('span', 'title').string
        source = item.find('span', 'meta').string
        information_des = StringUtils.filter_space_and_enter(item.find('p', 'abstract').string)
        html = requests.get(url).text
        bs = BeautifulSoup(html, 'html.parser')
        # [img, book_id, title, author, score, information_title, source, information_des]
        array = InformationBookParser.parse_note(bs) if url.find('note') >= 0 else InformationBookParser.parse_review(
            bs)
        if array is None:
            return None
        array.append(information_title)
        array.append(source)
        array.append(information_des)
        return array

    @staticmethod
    def parse_note(bs: BeautifulSoup):
        div_note = bs.find('div', 'note', id='link-report')
        div_wrapper = div_note.find('div', 'subject-wrapper')
        if div_wrapper is None:
            return None
        img = div_wrapper.find('img').get('src')
        book_id = re.sub('\D', '', div_wrapper.find('a').get('href'))
        title = div_wrapper.find('span', 'title-text').string
        author = div_wrapper.find('div', 'subject-summary').string
        score = div_wrapper.find('span', 'rating-score').string
        return [img, book_id, title, author, score]

    @staticmethod
    def parse_review(bs: BeautifulSoup):
        div_content = bs.find('div', id='content')
        div_wrapper = div_content.find('div', 'sidebar-info-wrapper')
        div_img = div_wrapper.find('div', 'subject-img')
        a_tag = div_img.find('a')
        img_tag = a_tag.find('img')
        img = img_tag.get('src')
        book_id = re.sub('\D', '', a_tag.get('href'))
        title = img_tag.get('title')
        author = div_wrapper.find('span', 'info-item-val').string
        return [img, book_id, title, author, '']


class AttentionBookParser(BookParser):

    def get_data(self, item):
        img_tag = item.find('img')
        img = img_tag.get('src')
        book_id = re.sub('\D', '', item.find('a').get('href'))
        title = img_tag.get('alt')
        author = StringUtils.filter_space_and_enter(item.find('p', 'author').string)
        score = StringUtils.filter_space_and_enter(item.find('span', 'average-rating').string)
        source = StringUtils.filter_space_and_enter(item.find('p', 'book-list-classification').string)
        p_review_tag = item.find('p', 'reviews')
        information_title = p_review_tag.find('a').string
        texts = p_review_tag.get_text("|", strip=True)
        information_des = StringUtils.filter_space_and_enter(str(texts).split("|")[0])
        return [img, book_id, title, author, score, information_title, source,
                re.sub('\(', '', information_des)]


class Top250BookParser(BookParser):

    def get_items(self, uls):
        html = requests.get(url=uls).text
        soup = BeautifulSoup(html, 'html.parser')
        div_article = soup.find('div', id='content').find('div', 'article')
        return div_article.find_all('table')

    def get_data(self, item):
        img = item.find('img').get('src')
        div_tag = item.find('div', 'pl2')
        a_tag = div_tag.find('a')
        book_id = re.sub('\D', '', a_tag.get('href'))
        title = a_tag.get('title')
        author = item.find('p', 'pl').string
        score = item.find('span', 'rating_nums').string
        source = StringUtils.filter_space_and_enter(item.find('span', 'pl').string)
        span_tag = div_tag.find('span')
        information_title = '' if span_tag is None else span_tag.string
        des_tag = item.find('span', 'inq')
        information_des = '' if des_tag is None else des_tag.string
        return [img, book_id, title, author, score, information_title, source, information_des]
