# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os, re, requests
from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline
from Xav import settings

post_url = 'http://82bts.com/downs.php'
form_data = '''
------WebKitFormBoundarytSSJnQRn44XkKiuL
Content-Disposition: form-data; name="code"

{name}
------WebKitFormBoundarytSSJnQRn44XkKiuL
Content-Disposition: form-data; name="Submit"

Download!
------WebKitFormBoundarytSSJnQRn44XkKiuL--
'''

def get_dir(category, title):
    if category == '1':
        dir_name = '亚洲无码/%s' % title
    elif category == '2':
        dir_name = '亚洲有码/%s' % title
    elif category == '8':
        dir_name = '国产专区/%s' % title
    elif category == '9':
        dir_name = '中文字幕/%s' % title

    return dir_name

class XavPipeline(object):
    def process_item(self, item, spider):
        title = item['title']
        post_time = item['post_time']
        torrent_url = item['torrent_url']
        detail = item['detail']
        category = item['category']
        store = settings.IMAGES_STORE

        dir_name = os.path.join(store, get_dir(category, title))
        torrent_name = torrent_url.split('=')[1]
        torrent_path = os.path.join(dir_name, torrent_name + '.rar')
        detail_path = os.path.join(dir_name, '资源说明.txt')
        headers = {
            'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundarytSSJnQRn44XkKiuL',
            'Referer': 'http://82bts.com/rlink.php?ref=' + torrent_name,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        }

        if not os.path.isfile(torrent_path):
  #          os.makedirs(dir_name)
            print('开始写入说明,', title)
            with open(detail_path, 'w') as f1:
                f1.write(detail)
            print('写入说明完成。')
            print('开始下载种子', torrent_url)
            if 'hash' in torrent_url:
                head = {
                    'Referer': 'http://82bts.com/tlink.php?hash=' + torrent_name,
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
                }
                url = 'http://82bts.com/downt.php?ref=' + torrent_name + '&Submit=Download%21'
                res = requests.get(url, headers=head)
            else:
                data = form_data.format(name=torrent_name)
                res = requests.post(post_url, data=data, headers=headers)
            with open(torrent_path, 'wb') as f2:
                f2.write(res.content)
            print('下载种子完成', torrent_url)
        else:
            print('文件已存在。')


class XavImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        image_urls = item['image_urls']
        category = item['category']
        title = item['title']

        for image_url in image_urls:
            yield Request(image_url, meta={'image_url': image_url, 'category': category, 'title': title})

    def file_path(self, request, response=None, info=None):
        title = request.meta['title']
        category = request.meta['category']
     #   images_store = settings.IMAGES_STORE   # 默认会读取配置文件下的IMAGES_STORE，不用再手动调用
        dir_name = get_dir(category, title)
        name = request.meta['image_url'].split('/')[-1]
        img_name = os.path.join(dir_name, name)

        return  img_name

    def item_completed(self, results, item, info):
        if results[0][0]:
            print('图片下载完成-->', results[0][1]['path'].split('/')[:2])
        else:
            print('图片下载失败-->', results[0][1]['path'].split('/')[:2])

        return item   # 后续还要用到item需返回