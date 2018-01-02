# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import re

import scrapy
from datetime import datetime
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_jobbole(value):
    return 'jobbole-' + value


def date_convert(value):
    try:
        create_date = datetime.strptime(value, '%Y/%m/%d').date()
    except Exception:
        create_date = datetime.now().date()
    return create_date


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_comment_tag(value):
    # 去掉tags中提取的评论
    if '评论' in value:
        return ''
    else:
        return value


def return_value(value):
    return value


class ArticleItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
        # 对item的值进行预处理,可传入多个函数,按顺序执行这些函数
        input_processor=MapCompose(add_jobbole)
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tag),
        output_processor=Join(',')
    )
    content = scrapy.Field()