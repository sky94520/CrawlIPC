# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import re
import json


class FilterPipeline(object):

    def __init__(self):
        self.pattern = re.compile(r'\s')

    def process_item(self, item, spider):
        if 'response' in item:
            del item['response']
        # 统一处理
        items = item['children']
        items.append(item)
        # 去掉空格
        for child in items:
            child['title'] = re.sub(self.pattern, '', child['title'])
        items.pop()

        return item


class JsonPipeline(object):

    def __init__(self):
        # 互斥
        self.categories = {}

    def process_item(self, item, spider):
        # 统一处理
        items = item['children']
        items.insert(0, item)
        # 添加或更新
        for child in items:
            code = child['code']
            datum = self.categories.get(code, {})
            datum.update(child)
            self.categories[code] = datum
        items.pop(0)
        return item

    def close_spider(self, spider):
        with open('categories.json', "w", encoding='utf-8') as fp:
            fp.write(json.dumps(list(self.categories.values()), ensure_ascii=False, indent=2))


class SavePagePipeline(object):
    def process_item(self, item, spider):
        response = item['response']

        path = response.meta['path']
        code = item['code']
        code = re.sub('/', '-', code)

        if not os.path.exists(path):
            os.makedirs(path)

        filename = os.path.join(path, '%s.html' % code)
        with open(filename, "wb") as fp:
            fp.write(response.body)
        return item


