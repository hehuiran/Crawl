# -*-coding:utf-8-*-标识

# 创建对象的基类:
import threading

from singleton.singleton import Singleton
from sqlalchemy import create_engine, Column, INT, VARCHAR, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

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


class BookSimple(Base):
    __tablename__ = 'book_simple'

    id = Column(INT(), primary_key=True)
    img = Column(VARCHAR(255))
    book_id = Column(VARCHAR(255))
    title = Column(VARCHAR(255))
    author = Column(VARCHAR(255))
    score = Column(VARCHAR(255))
    information_title = Column(VARCHAR(255))
    source = Column(VARCHAR(255))
    information_des = Column(VARCHAR(255))
    book_category_id = Column(INT(), ForeignKey('book_category.id', ondelete='CASCADE'))

    def __init__(self, img, book_id, title, author, score, information_title, source, information_des):
        self.img = img
        self.book_id = book_id
        self.title = title
        self.author = author
        self.score = score
        self.information_title = information_title
        self.source = source
        self.information_des = information_des


class BookCategory(Base):
    # 表名
    __tablename__ = 'book_category'

    id = Column(INT(), primary_key=True)
    name = Column(VARCHAR(255))
    book_simple_array = relationship('BookSimple', backref='book_category', cascade='all, delete-orphan',
                                     passive_deletes=True)

    def __init__(self, name: str):
        self.name = name
        self.book_simple_array = []


class SqlFactory(object):

    def __init__(self):
        # 创建表
        # Base.metadata.create_all(engine)
        self._session = DBSession()

    def get_session(self):
        return self._session


sql_Factory = SqlFactory()
