# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
import time
import logging
from scrapy.exceptions import IgnoreRequest
from scrapy_splash import SplashTextResponse
from scrapy.downloadermiddlewares.retry import RetryMiddleware

from proxy import Proxy, GetProxyError

logger = logging.getLogger(__name__)
PROXY = Proxy()


class GetFromLocalityMiddleware(object):
    def process_request(self, request, spider):
        """
        尝试从本地获取源文件，如果存在，则直接获取
        :param request:
        :param spider:
        :return:
        """
        url = request.url
        # 获取code
        code, suffix = url.split('/')[-1], request.meta['suffix']
        filename = '%s.%s' % (code, suffix)
        # 文件存放位置
        path = request.meta['path']
        # 该路径存在该文件
        filepath = os.path.join(path, filename)
        if os.path.exists(filepath):
            fp = open(filepath, 'rb')
            bytes = fp.read()
            fp.close()
            return SplashTextResponse(url=url, headers=request.headers, body=bytes, request=request)
        return None


class RetryOrErrorMiddleware(RetryMiddleware):
    """在官方的基础上增加了一条判断语句，当重试次数超过阈值时，发出错误"""
    def _retry(self, request, reason, spider):
        # 获取当前的重试次数
        return self._process(request, spider)

    def process_exception(self, request, exception, spider):
        if isinstance(exception, IgnoreRequest):
            return
        if isinstance(exception, TimeoutError):
            return self._process(request, spider)
        # 代理获取失败，一秒后再访问
        logger.warning(exception)
        if isinstance(exception, GetProxyError):
            time.sleep(1)
        # 出现错误，再次请求
        PROXY.dirty = True
        return request

    def _process(self, request, spider):
        """
        处理请求，如果超过最大次数，则在数据队列中删除这个请求，并且会抛出IgnoreRequest异常
        :param request:
        :param spider:
        :return:
        """
        retry_times = request.meta.get('retry_times', 0) + 1
        request.meta['retry_times'] = retry_times
        # 最大重试次数
        max_retry_times = self.max_retry_times
        if 'max_retry_times' in request.meta:
            max_retry_times = request.meta['max_retry_times']

        PROXY.dirty = True
        # 超出重试次数，记录
        if retry_times >= max_retry_times:
            spider.request_error()
            # logger.error('%s %s retry times beyond the bounds' % (request.url, datum))
            logger.error('%s retry times beyond the bounds' % request.url)
            return IgnoreRequest()
        else:
            return request
        # super()._retry(request, reason, spider)


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        # 最大重试次数
        retry_times = request.meta.get('retry_times', 0)
        max_retry_times = spider.crawler.settings.get('MAX_RETRY_TIMES')
        # 代理更新失败，则重新请求
        proxy = PROXY.get_proxy()
        if proxy is None:
            return request
        # 最后一次尝试不使用代理
        if proxy and retry_times != max_retry_times:
            logger.info('使用代理%s' % proxy)
            request.meta['proxy'] = 'http://%s' % proxy
        else:
            reason = '代理获取失败' if proxy is None else ('达到最大重试次数[%d/%d]' % (retry_times, max_retry_times))
            logger.warning('%s，使用自己的IP' % reason)
