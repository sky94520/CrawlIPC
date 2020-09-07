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
        data = [
            {'code': 'A', 'title': '人类生活必需品'},
            {'code': 'B', 'title': '作业；运输'},
            {'code': 'C', 'title': '化学；冶金'},
            {'code': 'D', 'title': '纺织；造纸'},
            {'code': 'E', 'title': '固定建筑物'},
            {'code': 'F', 'title': '机械工程；照明；加热；武器；爆破'},
            {'code': 'G', 'title': '物理'},
            {'code': 'H', 'title': '电学'},
        ]
        for datum in data:
            yield self._generate_request(datum['code'], datum['title'], '1', 0, None)

    def parse(self, response):
        # 转换为json
        text = response.text
        json_data = json.loads(text)
        # 数据填充
        item = IPCItem()
        item['title'] = response.meta['title']
        item['code'] = response.meta['code']
        item['parent_code'] = response.meta['parent_code']
        item['depth'] = response.meta['depth']
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
            yield self._generate_request(code, title, id_, response.meta['depth']+1, response.meta['code'])
        item['children'] = children
        yield item

    def _generate_request(self, code, title, id_, depth, parent_code):
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
            'depth': depth,
            'parent_code': parent_code,
            'title': title,
            'suffix': 'json'
        }
        return FormRequest(self.base_url, formdata=formdata, callback=self.parse, meta=meta)
