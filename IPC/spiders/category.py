# -*- coding: utf-8 -*-
import os
import scrapy
import random
from urllib.parse import urljoin

from IPC.items import IPCItem


class CategorySpider(scrapy.Spider):
    name = 'category'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = 'http://www.soopat.com/IPC/Parent/'

    def start_requests(self):
        for delta in range(8):
            code = chr(ord('A') + delta)
            url = self.base_url + code
            path = os.path.join(self.crawler.settings.get('BASEDIR'), code)
            meta = {
                'max_retry_times': self.crawler.settings.get('MAX_RETRY_TIMES'),
                'path': path
            }
            yield scrapy.Request(url, callback=self.parse, meta=meta)

    def parse(self, response):
        parents, children = self._parse(response)
        if len(parents) == 0 or len(children) == 0:
            yield response.request
        # 前缀
        index, prefix = 1, parents[-1]['code']
        while index < len(parents):
            front = parents[index - 1]['code']
            back = parents[index]['code']
            if front != back[:len(front)]:
                prefix = front
                break
            index += 1
        # TODO:第一次进入时的赋值 其他则是重复赋值
        item = IPCItem()
        if prefix != parents[-1]['code']:
            item['code'] = '%s%s' % (prefix, parents[-1]['code'])
        else:
            item['code'] = prefix
        item['title'] = parents[-1]['title']
        item['children'] = []
        item['response'] = response

        urls = []
        for child in children:
            min_len = min(len(prefix), len(child['code']))
            if prefix[:min_len] != child['code'][:min_len]:
                child['code'] = '%s%s' % (prefix, child['code'])
            item['children'].append(child)

            link = child.get('url', None)
            if link:
                del child['url']
                urls.append(link)
        yield item
        meta = {
            'max_retry_times': self.crawler.settings.get('MAX_RETRY_TIMES'),
            'path': response.meta['path']
        }
        for url in urls:
            yield scrapy.Request(url, callback=self.parse, meta=meta)

    def _parse(self, response):
        """
        解析response并得到parents children
        :param response:
        :return:
        """
        parents, children = [], []
        # 得到的为code title url
        try:
            table = response.css('table.IPCTable')[1]
        except Exception as e:
            self.logger.error('解析失败: %s' % e)
            return parents, children

        tr_parents = table.xpath('.//tr[@class="IPCParentRow"]')
        tr_children = table.xpath('.//tr[@class="IPCContentRow"]')

        for tr in tr_parents:
            code = tr.css('td.IPCCode a::text').extract_first()
            title = tr.css('td.IPCContent a::text').extract_first()

            parents.append({'code': code, 'title': title})

        for tr in tr_children:
            url = tr.css('td.IPCContent a::attr(href)').extract_first()
            if url:
                code = tr.css('td.IPCChild a::text').extract_first()
                title = tr.css('td.IPCContent a::text').extract_first()
                url = urljoin(self.base_url, url)
                children.append({'code': code, 'title': title, 'url': url})
            else:
                code = tr.css('td.IPCChild::text').extract_first()
                title = tr.css('td.IPCContent::text').extract_first()
                children.append({'code': code, 'title': title})

        return parents, children
