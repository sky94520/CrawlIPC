# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IPCItem(scrapy.Item):
    # define the fields for your item here like:
    code = scrapy.Field()
    title = scrapy.Field()
    children = scrapy.Field()
    ancestors = scrapy.Field()
    response = scrapy.Field()
