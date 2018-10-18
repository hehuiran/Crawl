# -*-coding:utf-8-*-标识
import multiprocessing
import time

import requests
from bs4 import BeautifulSoup

from image import ImageLoader


class Downloader(object):
    """docstring for downloader"""

    def __init__(self):
        self.server = 'http://www.biqukan.com/'
        self.target = 'https://www.biqukan.com/1_1094/'
        self.names = []
        self.urls = []
        self.nums = 0

    def get_download_url(self):
        req = requests.get(url=self.target)
        html = req.text
        div_bf = BeautifulSoup(html, 'html.parser')
        div = div_bf.find_all('div', class_='listmain')
        div_text = str(div[0])
        a_bf = BeautifulSoup(div_text, 'html.parser')
        a = a_bf.find_all('a')
        self.nums = len(a[15:])
        for value in a[15:]:
            self.names.append(value.string)
            self.urls.append(self.server + value.get('href'))

    @staticmethod
    def get_content(target):
        req = requests.get(url=target)
        html = req.text
        bf = BeautifulSoup(html, 'html.parser')
        texts = bf.find_all('div', id='content', class_='showtxt')
        text = texts[0].text.replace('\xa0' * 8, '\n\n')
        return text

    @staticmethod
    def writer(name, path, text):
        with open(path, 'a', encoding='utf-8') as f:
            f.write(name + '\n')
            f.writelines(text)
            f.write('\n\n')


# if __name__ == '__main__':
    # dl = Downloader()
    # dl.get_download_url()
    # print("开始下载...")
    # for i in range(dl.nums):
    #     dl.writer(dl.names[i], 'text.txt', dl.get_content(dl.urls[i]))
    #     sys.stdout.write("已下载:%.3f%%" % float(i / dl.nums) + '\r')
    #     sys.stdout.flush()
    # print("下载完成")
    # url = 'https://unsplash.com/'
    # html = requests.get(url).text
    # soup = BeautifulSoup(html, 'html.parser')
    # div = soup.find_all('div', class_='yVU8k')
    # for each in div:
    #     div_text = str(each)
    #     a_soup = BeautifulSoup(div_text, 'html.parser')
    #     texts = a_soup.find_all('a')
    #     print("下载id=" + texts[0].get('href'))
    # image = ImageLoader()
    # image.get_image_url()
    # size = len(image.urls)
    # t_start = time.time()
    # pool = multiprocessing.Pool(40)
    # tasks = []
    # for i in range(size):
    #     # task = image.download_image(image.urls[i], '%d.jpg' % (i + 1))
    #     pool.apply_async(image.download_image, (image.urls[i], '%d.jpg' % (i + 1)))
    # pool.close()
    # pool.join()
    # t_stop = time.time()
    # print("Download completed!Enjoy now！Time of use：%.2fS" % (t_stop - t_start))
