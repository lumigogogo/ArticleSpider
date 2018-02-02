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

    def get_insert_sql(self):
        insert_sql = """
                                insert into article(title, url, create_date, fav_nums, url_object_id, front_image_url, 
                                front_image_path, praise_nums, comment_nums, tags, content)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
        params = (self['title'], self['url'], self['create_date'], self['fav_nums'], self['url_object_id'],
                  self['front_image_url'], self['front_image_path'], self['praise_nums'], self['comment_nums'],
                  self['tags'], self['content'])
        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    # 知乎的问题item

    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title, content, create_time, update_time, answer_num, 
            comments_nums, watch_user_num, click_num, crawl_time, crawl_update_time)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        zhihu_id = int(self['zhihu_id'][0])
        topics = ','.join(self['topics'])
        url = self['url'][0]
        title = self['title'][0]
        content = self['content']
        answer_num = self


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()


class DouBanMovieTop250(scrapy.Item):
    # 豆瓣电影top250item
    title = scrapy.Field()
    front_img_url = scrapy.Field()
    director = scrapy.Field()
    screenwriter = scrapy.Field()
    starring = scrapy.Field()
    type = scrapy.Field()
    country = scrapy.Field()
    language = scrapy.Field()
    release_date = scrapy.Field()
    score = scrapy.Field()
    comment_num = scrapy.Field()
    ranking = scrapy.Field()
    description = scrapy.Field()
    is_watch = scrapy.Field()
    watch_path = scrapy.Field()
