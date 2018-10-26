# -*-coding:utf-8-*-标识
import re

import bs4
import requests
from bs4 import BeautifulSoup
from sqlalchemy import Column, ForeignKey, INT, VARCHAR, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from douban.crawl.book import CrawlBook
from douban.impl.home_parse import HotHomeParser, TimeHomeParser, VideoHomeParser, MovieHomeParser, GroupHomeParser, \
    BookHomeParser, MusicHomeParser, MarketHomeParser, EventsHomeParser
from douban.interface.parse import HomeParser
# 创建对象的基类:
from douban.utils import CollectionUtils

Base = declarative_base()

# 初始化数据库连接:
engine = create_engine('mysql+mysqlconnector://root:yzkj1234@localhost:3306/sqltest?charset=utf8', echo=True,
                       encoding='utf-8', convert_unicode=True)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)


class Tab(Base):
    # 表名
    __tablename__ = 'tab'

    id = Column(INT(), primary_key=True)
    name = Column(VARCHAR(255))
    url = Column(VARCHAR(255))

    def __init__(self, name, url):
        self.name = name
        self.url = url


class HomeSubData(Base):
    # 表名
    __tablename__ = 'home_sub_data'

    id = Column(INT(), primary_key=True)
    img = Column(VARCHAR(255))
    url = Column(VARCHAR(255))
    title = Column(VARCHAR(255))
    des = Column(VARCHAR(255))
    name = Column(VARCHAR(255))
    time = Column(VARCHAR(255))
    """通过外键约束建立关系,耦合性大,数据删除需删除从表后才能删除主表

            home_sub_id = Column(INT(), ForeignKey('home_sub.id'))"""
    home_sub_id = Column(INT(), ForeignKey('home_sub.id', ondelete='CASCADE'))

    # 不通过外键约束建立一对多关系
    # home_sub_id = Column(INT())

    def __init__(self, img, url, title, des, name, time):
        self.img = img
        self.url = url
        self.title = title
        self.des = des
        self.name = name
        self.time = time


class HomeSub(Base):
    # 表名
    __tablename__ = 'home_sub'

    id = Column(INT(), primary_key=True)
    title = Column(VARCHAR(255))
    type = Column(VARCHAR(255))
    """通过外键约束建立关系,耦合性大,数据删除需删除从表后才能删除主表

            home_sub_data_array = relationship('HomeSubData', backref='home_sub')
            
            home_id = Column(INT(), ForeignKey('home.id'))"""
    home_sub_data_array = relationship('HomeSubData', backref='home_sub', cascade='all, delete-orphan',
                                       passive_deletes=True)
    home_id = Column(INT(), ForeignKey('home.id', ondelete='CASCADE'))

    # 不通过外键约束建立一对多关系
    # home_sub_data_array = relationship('HomeSubData', primaryjoin=foreign(HomeSubData.home_sub_id) == remote(id),
    #                                    backref='home_sub')
    # home_id = Column(INT())

    def __init__(self, title, tp):
        self.title = title
        self.type = tp
        self.home_sub_data_array = []


class Home(Base):
    # 表名
    __tablename__ = 'home'

    id = Column(INT(), primary_key=True)
    title = Column(VARCHAR(255))
    type = Column(VARCHAR(255))
    """通过外键约束建立关系,耦合性大,数据删除需删除从表后才能删除主表
    
            home_sub_array = relationship('HomeSub', backref='home')"""
    home_sub_array = relationship('HomeSub', backref='home', cascade='all, delete-orphan', passive_deletes=True)

    # 不通过外键约束建立一对多关系
    # home_sub_array = relationship('HomeSub', primaryjoin=foreign(HomeSub.home_id) == remote(id), backref='home')

    def __init__(self, title, tp):
        self.title = title
        self.type = tp
        self.home_sub_array = []


# noinspection PyTypeChecker
class Crawl(object):

    def __init__(self):
        self.__target = 'https://www.douban.com/'
        # tab标签信息
        self.__tabs = []
        # 所有列表数据
        self.__all_data = []
        self.__bs = None

    @staticmethod
    def _get_albums_uls(main_bs: bs4.Tag):
        div_albums = main_bs.find('div', 'albums')
        return div_albums.find_all('ul')

    def handler_html(self):
        # 创建表
        # Base.metadata.create_all(engine)
        session = DBSession()
        html = requests.get(self.__target).text  # type:str
        self.__bs = BeautifulSoup(html, 'html.parser')
        self._crawl_tabs()

        tab = self.__tabs[0]  # type:Tab
        CrawlBook(tab.url)

        tag_ids = ['sns', 'time', 'video', 'movie', 'group', 'book', 'music', 'market', 'events']
        parsers = [HotHomeParser(), TimeHomeParser(), VideoHomeParser(), MovieHomeParser(), GroupHomeParser(),
                   BookHomeParser(), MusicHomeParser(),
                   MarketHomeParser(), EventsHomeParser()]
        for i in range(len(tag_ids)):
            self._crawl_data(tag_ids[i], i != 0, parsers[i])

        # 清空表中的数据
        tabs = session.query(Tab).all()
        for tab in tabs:
            session.delete(tab)
        homes = session.query(Home).all()
        for home in homes:
            session.delete(home)

        # 添加到session
        # 添加tab
        session.add_all(self.__tabs)
        # 添加页面数据
        session.add_all(self.__all_data)
        # 提交即保存到数据库:
        session.commit()

        # homes = session.query(Home).all()
        # Crawl._write_data(homes)

        # 关闭session
        session.close()

    @staticmethod
    def _write_data(homes: list):
        # print('size=' + str(len(homes)))
        for home in homes:
            home_text = "title=" + home.title + "\n" + "type=" + home.type + "\n"
            # print('\xa0' * 4 + home.title + 'size=' + str(len(home.home_sub_array)))
            Crawl.writer('data.txt', home_text)
            for home_sub in home.home_sub_array:
                home_sub_text = '\xa0' * 4 + "title=" + home_sub.title + "\n" \
                                + '\xa0' * 4 + "type=" + home_sub.type + "\n" \
                                + '\xa0' * 4 + "home_id=" + str(home_sub.home_id) + "\n"
                Crawl.writer('data.txt', home_sub_text)
                # print('\xa0' * 8 + home_sub.title + 'size=' + str(len(home_sub.home_sub_data_array)))
                for home_sub_data in home_sub.home_sub_data_array:
                    home_sub_data_text = '\xa0' * 8 + "img=" + home_sub_data.img + "\n" \
                                         + '\xa0' * 8 + "url=" + home_sub_data.url + "\n" \
                                         + '\xa0' * 8 + "title=" + home_sub_data.title + "\n" \
                                         + '\xa0' * 8 + "des=" + home_sub_data.des + "\n" \
                                         + '\xa0' * 8 + "name=" + home_sub_data.name + "\n" \
                                         + '\xa0' * 8 + "time=" + home_sub_data.time + "\n" \
                                         + '\xa0' * 8 + "home_sub_id=" + str(home_sub_data.home_sub_id) + "\n" * 2
                    Crawl.writer('data.txt', home_sub_data_text)

    @staticmethod
    def writer(path: str, text: str):
        with open(path, 'a', encoding='utf-8') as f:
            f.writelines(text)

    # 保存详细数据
    def _crawl_data(self, tag_id: str, has_section_title: bool, parser: HomeParser):
        div_main, home = self._crawl_title(tag_id, has_section_title)
        uls = div_main.find_all('ul') if has_section_title else Crawl._get_albums_uls(div_main)
        for i in range(len(uls)):
            ul = uls[i]
            items = parser.get_items(ul)

            home_sub = home.home_sub_array[i]  # type:HomeSub
            for j in range(len(items)):
                item = items[j]
                array = parser.get_data(item)  # type:list
                home_sub_data = HomeSubData(img=CollectionUtils.get_list_value(array, 0),
                                            url=CollectionUtils.get_list_value(array, 1),
                                            title=CollectionUtils.get_list_value(array, 2),
                                            des=CollectionUtils.get_list_value(array, 3),
                                            name=CollectionUtils.get_list_value(array, 4),
                                            time=CollectionUtils.get_list_value(array, 5))
                home_sub.home_sub_data_array.append(home_sub_data)
        self.__all_data.append(home)

    # 保存标题与副标题
    def _crawl_title(self, tag_id: str, has_section_title: bool):
        div = self.__bs.find('div', id="anony-" + tag_id)

        section_title = None
        if has_section_title:
            section_title = re.sub('[\n\xa0 ·]', '', div.find('a').string)

        home = Home(title=section_title, tp=tag_id)

        div_main = div.find('div', 'main')
        hs = div_main.find_all('h2')
        for i in range(len(hs)):
            h = hs[i]
            text = h.get_text("|", strip=True)
            sub_title = re.sub('[\n\xa0 ·]', '', str(text).split("|")[0])

            if not has_section_title:
                home.title = sub_title
            home_sub = HomeSub(title=sub_title, tp=tag_id + str(i + 1))
            home.home_sub_array.append(home_sub)
        return div_main, home

    # 爬取tab标签
    def _crawl_tabs(self):
        div = self.__bs.find('div', id='anony-nav')
        a = div.find_all('a', target='_blank')
        for value in a:
            tab = Tab(name=str(value.string), url=str(value.get('href')))
            self.__tabs.append(tab)
