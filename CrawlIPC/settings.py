# -*- coding: utf-8 -*-

# Scrapy settings for IPCCrawler.project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os

BOT_NAME = 'CrawlIPC'

SPIDER_MODULES = ['CrawlIPC.spiders']
NEWSPIDER_MODULE = 'CrawlIPC.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'IPCCrawler.(+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
# 最大重试次数
MAX_RETRY_TIMES = 20
BASEDIR = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
BASEDIR = os.path.join(BASEDIR, 'files')
INCOPAT_DIR = os.path.join(BASEDIR, 'json')

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'CrawlIPC.middlewares.GetFromLocalityMiddleware': 543,
    'CrawlIPC.middlewares.ProxyMiddleware': 843,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'CrawlIPC.pipelines.SavePagePipeline': 300,
    'CrawlIPC.pipelines.FilterPipeline': 301,
    'CrawlIPC.pipelines.JsonPipeline': 302,
}
