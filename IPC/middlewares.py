# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
from urllib.parse import urlsplit, parse_qsl
from scrapy_splash import SplashTextResponse
import logging
import random
import proxy_pool

logger = logging.getLogger(__name__)


class GetFromLocalityMiddleware(object):
    def process_request(self, request, spider):
        """
        尝试从本地获取源文件，如果存在，则直接获取
        :param request:
        :param spider:
        :return:
        """
        splash_url = spider.crawler.settings.get('SPLASH_URL')
        splash_result = urlsplit(splash_url)
        # 提取出code
        url = request.url
        result = urlsplit(url)
        # 不进行
        if result.scheme == splash_result.scheme and result.netloc == splash_result.netloc:
            return None
        # 获取code
        code = url.split('/')[-1]
        filename = '%s.html' % code
        # 文件存放位置
        path = request.meta['path']
        # 该路径存在该文件
        filepath = os.path.join(path, filename)
        # 是否从本地文件夹获取到的文件
        request.meta['loaded_from_locality'] = os.path.exists(filepath)
        if os.path.exists(filepath):
            fp = open(filepath, 'rb')
            bytes = fp.read()
            fp.close()
            return SplashTextResponse(url=url, headers=request.headers, body=bytes, request=request)
        return None


class ProxyMiddleware(object):

    def process_request(self, request, spider):
        # 最大重试次数
        retry_times = request.meta.get('retry_times', 0)
        max_retry_times = spider.crawler.settings.get('MAX_RETRY_TIMES')
        proxy = proxy_pool.get_random_proxy()
        # 最后一次尝试不使用代理
        if proxy and retry_times != max_retry_times:
            logger.info('使用代理%s' % proxy)
            request.meta['splash']['args']['proxy'] = 'http://%s' % proxy
        else:
            reason = '代理获取失败' if proxy else ('达到最大重试次数[%d/%d]' % (retry_times, max_retry_times))
            logger.warning('%s，使用自己的IP' % reason)


class RandomUserAgentMiddleware(object):

    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50',
        ]

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agents)