# -*-coding:utf-8-*-标识
import re
from multiprocessing.pool import Pool
from urllib import parse

import requests
from bs4 import BeautifulSoup

from douban.sql import BookMainLabel, BookSubLabel, sql_Factory, BookDes
from douban.utils import StringUtils


class LabelBook(object):

    def __init__(self):
        self.__label_books = []
        self.__label_url = 'https://book.douban.com/tag/'
        self._crawl_label_book()

    def _crawl_label_book(self):
        all_tag_html = requests.get(url=self.__label_url).text
        soup = BeautifulSoup(all_tag_html, 'html.parser')
        div_all = soup.find('div', id='content').find('div', 'article').find_all('div')[1]
        divs = div_all.find_all('div')[:1]
        # pool = Pool(len(divs))
        for div in divs:
            main_label = div.find('a').get('name')
            book_main_label = BookMainLabel(repr(main_label))
            self.__label_books.append(book_main_label)
            trs = div.find_all('tr')[:1]
            self._crawl_sub_label(trs, book_main_label)
            # pool.apply_async(self._crawl_sub_label, (trs, book_main_label))
        # pool.close()
        # join方法会等待所有进程执行完毕，必须先调用close
        # pool.join()
        session = sql_Factory.get_session()
        session.add_all(self.__label_books)
        session.commit()
        session.close()

    def _crawl_sub_label(self, trs, book_main_label: BookMainLabel):
        start = 0
        for tr in trs:
            a_tags = tr.find_all('a')[:1]
            for a in a_tags:
                sub_label = str(a.string)
                book_sub_label = BookSubLabel(sub_label)
                book_main_label.book_sub_label_array.append(book_sub_label)
                url = self.__label_url + parse.quote(sub_label) + '?start='
                # self._crawl_book_des(url, str(start), book_sub_label)
                # while True:
                #     if self._crawl_book_des(url, str(start), book_sub_label):
                #         start = start + 20
                #     else:
                #         break
                while True:
                    if start < 180:
                        self._crawl_book_des(url, str(start), book_sub_label)
                        start = start + 20
                    else:
                        break

    def _crawl_book_des(self, url, start, book_sub_label: BookSubLabel):
        url = url + start
        html = requests.get(url=url).text
        bs = BeautifulSoup(html, 'html.parser')
        # div_subject_list = bs.find('div', id='subject_list')
        # ul_subject_list = div_subject_list.find('ul', 'subject-list')
        # lis = ul_subject_list.find_all('li', 'subject-item')
        lis = bs.find('div', id='subject_list').find('ul', 'subject-list').find_all('li', 'subject-item')
        if lis is None:
            return False
        # img, book_id, title, author, score, press,producers, sub_title,origin_name, translator,
        # publish_time, page, price, comment_num, star, content_des, author_des, tags
        for li in lis:
            book_id = re.sub('\D', '', li.find('a', 'nbg').get('href'))
            url = 'https://book.douban.com/subject/' + book_id
            html = requests.get(url=url).text
            bs = BeautifulSoup(html, 'html.parser')
            # div_wrapper = bs.find('div', id='wrapper')
            # title = div_wrapper.find('span').string

            div_article = bs.find('div', id='content').find('div', 'article')
            img_tag = div_article.find('div', id='mainpic').find('img')
            img = img_tag.get('src')
            title = img_tag.get('alt')

            div_info = div_article.find('div', id='info')
            a_tags = div_info.find_all('a')
            author = a_tags[0].string

            origin_str = str(div_info)
            press = _get_middle_str(origin_str, '出版社:')

            producers = _get_pattern_middle_str(r'<span class="pl">出品方:</span>(.*?)</a>', origin_str)  # type:str
            if not StringUtils.is_empty(producers):
                producers = re.sub('<.*?>', '', producers)

            sub_title = _get_middle_str(origin_str, '副标题:')
            origin_name = _get_middle_str(origin_str, '原作名:')
            translator = _get_pattern_middle_str(r'<span class="pl"> 译者</span>(.*?)</a>', origin_str)
            if not StringUtils.is_empty(translator):
                translator = re.sub('<.*?>', '', re.sub('[:\n\xa0 ·]', '', translator))

            publish_time = _get_middle_str(origin_str, '出版年:')
            page = _get_middle_str(origin_str, '页数:')
            price = _get_middle_str(origin_str, '定价:')

            div_interest = div_article.find('div', id='interest_sectl')

            score = div_interest.find('strong', 'll rating_num ').string
            comment_num = div_interest.find('a', 'rating_people').find('span').string

            star = ''
            spans = div_interest.find_all('span', 'rating_per')
            for span in spans:
                star = star + span.string

            div_related_info = div_article.find('div', 'related_info')

            content_des = ''
            div_indent_content = div_related_info.find('div', 'indent', id='link-report')
            if div_indent_content is not None:
                content_all = div_indent_content.find('span', 'all hidden')
                if content_all is not None:
                    div_intro_content = content_all.find('div', 'intro')
                else:
                    div_intro_content = div_indent_content.find('div', 'intro')
                if div_intro_content is not None:
                    p_array_content = div_intro_content.find_all('p')
                    for i in range(len(p_array_content)):
                        text = p_array_content[i].string
                        if text is not None:
                            content = text if i == len(p_array_content) - 1 else text + '\\n'
                            content_des = content_des + content

            author_des = ''
            div_indent_author = div_related_info.find_all('div', 'indent')[1]
            if div_indent_author is not None:
                author_all = div_indent_author.find('span', 'all hidden')
                if author_all is not None:
                    div_intro_author = author_all.find('div', 'intro')
                else:
                    div_intro_author = div_indent_author.find('div', 'intro')
                if div_intro_author is not None:
                    p_array_author = div_intro_author.find_all('p')
                    for i in range(len(p_array_author)):
                        text = p_array_author[i].string
                        if text is not None:
                            des = text if i == len(p_array_author) - 1 else text + '\\n'
                            author_des = author_des + des

            div_tag = div_related_info.find('div', id='db-tags-section')
            spans_tag = div_tag.find('div', 'indent').find_all('span')
            tags = ''
            for i in range(len(spans_tag)):
                tag_text = spans_tag[i].find('a').string
                des = tag_text if i == len(spans_tag) - 1 else tag_text + ','
                tags = tags + des

            print(img + '->' + book_id + '->' + title + '->' + author + '->' + score + '->'
                  + press + '->' + producers + '->' + sub_title + '->' + origin_name + '->'
                  + translator + '->' + publish_time + page + '->' + price + '->' + comment_num + '->'
                  + star + '->' + content_des + '->' + author_des + '->' + tags)

            book_des = BookDes(str(img), str(book_id), str(title), str(author), str(score), str(press), str(producers),
                               str(sub_title), str(origin_name), str(translator),
                               str(publish_time), str(page), str(price), str(comment_num), str(star), str(content_des),
                               str(author_des), str(tags))
            book_sub_label.book_des_array.append(book_des)

        return True


def _get_middle_str(content, tag):
    p = re.compile(r'<span class="pl">' + tag + '</span>(.*?)<br[/]?>', re.S)
    array = re.findall(p, content)
    if array is not None and len(array) > 0:
        return array[0]
    return ''


def _get_pattern_middle_str(pattern, content):
    p = re.compile(pattern, re.S)
    array = re.findall(p, content)
    if array is not None and len(array) > 0:
        return array[0]
    return ''
