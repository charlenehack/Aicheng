# -*- coding: utf-8 -*-
from scrapy import  Spider, Request
from pyquery import PyQuery as pq
from Aicheng.items import AichengItem

class AichengSpider(Spider):
    name = 'aicheng'
    allowed_domains = ['dasemm.com']
    start_urls = ['https://as.dasemm.com/bt/thread.php?fid=22']

    has_urls_set = set()

    def parse(self, response):
        doc = pq(response.text)
        title_list = doc('.tr3.t_one h3 a').items()
        for t in title_list:
            title = t.text()
            link = 'https://as.dasemm.com/bt/%s' % t.attr.href

            yield Request(url=link, callback=self.parse_detail, meta={'title': title})

        page_list = doc('.pages a').items()
        for a in page_list:
            uri = a.attr.href
            md5_url = self.md5(uri)
            if md5_url not in self.has_urls_set:
                self.has_urls_set.add(md5_url)
                page_url = 'https://as.dasemm.com%s' % uri

                yield Request(url=page_url, callback=self.parse)

    def parse_detail(self, response):
        img_urls_list = []
        title = response.meta['title']
        doc = pq(response.text)
        torrent_url = doc.find('#read_tpc a').eq(2).attr.href
        post_time = doc.find('.gray').eq(1).text()
        img_list = doc('#read_tpc img').items()
        for i in img_list:
            img = i.attr.src
            img_urls_list.append(img)

        yield AichengItem(title=title, image_urls=img_urls_list, torrent_url=torrent_url, post_time=post_time)

    def md5(self,url):
        import hashlib
        obj = hashlib.md5()
        obj.update(bytes(url,encoding='utf-8'))

        return obj.hexdigest()