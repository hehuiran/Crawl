# -*-coding:utf-8-*-标识
import json
import re

import requests

from douban.interface.parse import HomeParser
from douban.utils import StringUtils


# 豆瓣热点内容模块解析
class HotHomeParser(HomeParser):

    def get_data(self, item):
        img_tag = item.find('img')
        img = img_tag.get('data-origin')
        a = item.find_all('a')
        url = a[1].get('href')
        title = a[1].string
        des = item.find('span', 'num').string
        return [img, url, title, des]


# 豆瓣时间模块解析
class TimeHomeParser(HomeParser):

    def get_data(self, item):
        img = item.find('img').get('src')
        a_title = item.find('a', 'title')
        url = a_title.get('href')
        title = a_title.string
        des = item.find('span', 'type').string
        return [img, url, title, des]


# 豆瓣视频模块解析
class VideoHomeParser(HomeParser):

    def get_items(self, ul):
        data_id = ul.get('data-id')
        url = 'https://m.douban.com/rexxar/api/v2/muzzy/columns/' + data_id + '/items?start=0&count=3'
        text = requests.get(url).text
        json_text = json.loads(text)
        return json_text['items']

    def get_data(self, item):
        img = item['cover']
        url = item['uri']
        title = item['title']
        return [img, url, title]


# 豆瓣电影模块解析
class MovieHomeParser(HomeParser):

    def get_data(self, item):
        img_tag = item.find('img')
        img = img_tag.get('data-origin')
        url = item.find('a').get('href')
        title = img_tag.get('alt')
        des = item.find('i').string
        return [img, url, title, des]


# 豆瓣小组模块解析
class GroupHomeParser(HomeParser):
    def get_data(self, item):
        img_tag = item.find('img')
        img = img_tag.get('data-origin')
        div_info = item.find('div', 'info')
        a_title = div_info.find('a')
        url = a_title.get('href')
        title = a_title.string
        texts = div_info.get_text("|", strip=True)
        des = str(texts).split("|")[1]
        return [img, url, title, des]


# 豆瓣读书模块解析
class BookHomeParser(HomeParser):

    def get_data(self, item):
        img_tag = item.find('img')
        img = img_tag.get('data-origin')
        url = item.find('a').get('href')
        title = img_tag.get('alt')
        div_price = item.find('div', 'price')
        des = '' if div_price is None else StringUtils.filter_space_and_enter(div_price.string)
        name = item.find('div', 'author').string
        return [img, url, title, des, name]


# 豆瓣音乐模块解析
class MusicHomeParser(HomeParser):

    def get_data(self, item):
        img_tag = item.find('img')
        img = img_tag.get('data-origin')
        new_music = img is not None
        url = item.find('a').get('href')
        title = img_tag.get('alt') if new_music else item.find('div', 'title').string
        des = name = ''
        if new_music:
            name = item.find('div', 'artist').get_text(strip=True)
            des = item.find('i').string
        else:
            img = img_tag.get('src')
        return [img, url, title, des, name]


# 豆瓣豆品模块解析
class MarketHomeParser(HomeParser):

    def get_data(self, item):
        div_pic = item.find('div', 'market-spu-pic')
        style = div_pic.get('style')
        p = re.compile(r'[(](.*?)[)]', re.S)
        img = re.findall(p, style)[0]
        a_title = item.find('a', 'market-spu-title')
        url = a_title.get('href')
        title = StringUtils.filter_space_and_enter(a_title.string)
        des = StringUtils.filter_space_and_enter(item.find('span', 'market-spu-price').string)
        return [img, url, title, des]


# 豆瓣同城模块解析
class EventsHomeParser(HomeParser):

    def get_data(self, item):
        img_tag = item.find('img')
        img = img_tag.get('data-origin')
        div_title = item.find('div', 'title')
        a_title = div_title.find('a')
        url = a_title.get('href')
        title = a_title.get('title')
        des = StringUtils.filter_space_and_enter(item.find('div', 'follow').string)
        name = item.find('address').get('title')
        time = StringUtils.filter_space_and_enter(item.find('div', 'datetime').string)
        return [img, url, title, des, name, time]
