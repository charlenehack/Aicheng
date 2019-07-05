# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from pyquery import PyQuery as pq
import re
from Xav.items import XavItem


class XavSpider(Spider):
    name = 'xav'
    allowed_domains = ['xcaoav.com']
    start_urls = ['https://xcaoav.com/forum-1.htm']

    def parse(self, response):
        res = re.findall('forum-(\d)-(.*?)-tid.htm">... (.*?)</a>', response.text)
        category = res[0][0]
        total_page = res[0][2]
        #    for page in range(1, int(total_page)+1):
        for page in range(1, 2):
            page_url = 'https://xcaoav.com/forum-%s-%s-tid.htm' % (str(category), str(page))

            yield Request(url=page_url, callback=self.parse_page, meta={'category': category})

        category_list = [1,2,8,9]
        for category in category_list:
            category_url = 'https://xcaoav.com/forum-%s.htm' % str(category)

            yield Request(url=category_url, callback=self.parse)


    def parse_page(self, response):
        category = response.meta['category']
        pattern = re.compile('class="thread thread_agrees_0 " href="(.*?)"', re.S)
        uris = re.findall(pattern, response.text)
        for uri in uris:
            link = 'https://xcaoav.com/%s' % uri

            yield Request(url=link, callback=self.parse_detail, meta={'category': category})

    def parse_detail(self, response):
        category = response.meta['category']
        img_url_list = []
        doc = pq(response.text)
        title = doc('h3').eq(0).text()
        post_time = doc.find('.light').eq(1).text()
        detail = doc.find('#thread_post div').text()
        torrent_url = re.findall('下載地址：(.*?)\n', detail)[0]
        img_list = doc('#thread_post img').items()
        for i in img_list:
            img = i.attr.src
            img_url_list.append(img)

        yield XavItem(title=title, category=category, post_time=post_time, torrent_url=torrent_url, detail=detail, image_urls=img_url_list)