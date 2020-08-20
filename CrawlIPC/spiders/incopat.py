# -*- coding: utf-8 -*-
import os
import json
import scrapy
from scrapy.http import FormRequest
from ..items import IPCItem


class IncopatSpider(scrapy.Spider):
    name = 'incopat'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = 'https://www.incopat.com/ipcFindTool/ipcquery'
        self.path = None

    def start_requests(self):
        self.path = os.path.join(self.crawler.settings.get('INCOPAT_DIR'), 'A')
        yield self._generate_request('A', '人类生活必需品', '1')

    def parse(self, response):
        # 转换为json
        text = response.text
        json_data = json.loads(text)
        # 数据填充
        item = IPCItem()
        item['title'] = response.meta['title']
        item['code'] = response.meta['code']
        item['response'] = response
        children = []
        for datum in json_data['data']:
            code, id_ = datum['code'], datum['id']
            title = datum['name'][len(datum['code']):]
            children.append({
                'code': code,
                'id': id_,
                'title': title,
            })
            # 请求
            yield self._generate_request(code, title, id_)
        item['children'] = children
        # item['children'] = data
        yield item

    def _generate_request(self, code, title, id_):
        formdata = {
            'code': code,
            'id': id_,
            'version': '2018',
            'format': 'zh'
        }
        meta = {
            'max_retry_times': self.crawler.settings.get('MAX_RETRY_TIMES'),
            'path': self.path,
            'code': code,
            'title': title,
            'suffix': 'json'
        }
        return FormRequest(self.base_url, formdata=formdata, callback=self.parse, meta=meta)
