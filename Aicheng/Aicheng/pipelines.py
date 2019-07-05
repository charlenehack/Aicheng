# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os, re, requests, random, string
from scrapy.pipelines.images import ImagesPipeline
from Aicheng import settings

post_url = 'http://82bts.com/downc.php'
payload = '''
------WebKitFormBoundarynhhhfB2ns2kf56yh
Content-Disposition: form-data; name="code"

{name}
------WebKitFormBoundarynhhhfB2ns2kf56yh
Content-Disposition: form-data; name="Submit"

 Download!
------WebKitFormBoundarynhhhfB2ns2kf56yh--
'''

class AichengPipeline(object):
    def process_item(self, item, spider):
        title = item['title']
        torrent = item['torrent_url'].split('/?')[1]
        post_time = item['post_time']

        date = re.findall('Posted: 20(.*) ', post_time)[0]
        dir_name = '/tmp/tmp/%s.%s' % (date, title)

        response = requests.get(url=torrent)
        torrent_url = re.findall('url=(.*)"', response.text)[0].strip()

        torrent_name = torrent_url.split('=')[1]
        torrent_path = os.path.join(dir_name, torrent_name + '.rar')
        headers = {
            'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundarynhhhfB2ns2kf56yh',
            'Referer': 'http://www.82bts.com/slink.php?ref=' + torrent_name,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36}'
        }

        if not os.path.isfile(torrent_path):
            print('开始下载', torrent_url)
            data = payload.format(name=torrent_name)
            res = requests.post(post_url, data=data, headers=headers)
            with open(torrent_path, 'wb') as f:
                f.write(res.content)
            print('下载完成', torrent_url)
        else:
            print('文件已存在。')

class AichengImagesPipeline(ImagesPipeline):   # 继承内置ImagesPipeline
    def get_media_requests(self, item, info):
        request_objs = super(AichengImagesPipeline, self).get_media_requests(item, info)  # 从items获取item对象
        for request_obj in request_objs:
            request_obj.item = item
        return request_objs

    def file_path(self, request, response=None, info=None):   # 重写保存路径
        path = super(AichengImagesPipeline, self).file_path(request, response, info)
        title = request.item.get('title')
        post_time = request.item.get('post_time')
        date = re.findall('Posted: 20(.*) ', post_time)[0]
        images_store = settings.IMAGES_STORE  # 从配置文件获取保存目录
        dir_name = os.path.join(images_store, date + '.' + title)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        img_name = path.replace('full/','')    # 去除默认创建的full目录
        img_path = os.path.join(dir_name, img_name)

        return img_path

