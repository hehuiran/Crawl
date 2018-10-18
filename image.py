# -*-coding:utf-8-*-标识
import asyncio

import requests
from bs4 import BeautifulSoup


class ImageLoader(object):

    def __init__(self):
        self.target = 'https://unsplash.com'
        self.suffix = '/download?force=true'
        self.urls = []

    def get_image_url(self):
        html = requests.get(self.target).text
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find_all('div', class_='yVU8k')
        for each in div:
            div_text = str(each)
            a_soup = BeautifulSoup(div_text, 'html.parser')
            texts = a_soup.find_all('a')
            self.urls.append(self.target + texts[0].get('href') + self.suffix)

    @staticmethod
    def download_image(url, path):
        response = requests.get(url)
        img = response.content
        with open(path, 'wb') as f:
            f.write(img)
