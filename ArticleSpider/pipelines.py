# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi
import codecs
import MySQLdb
import MySQLdb.cursors


class ArticlespiderPipeline(object):

    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeLine(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipeLine(object):
    # 调用scrapy提供的json export 导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class ArticleImagePipeLine(ImagesPipeline):

    def item_completed(self, results, item, info):
        if 'front_image_path' in item:
            for ok, value in results:
                image_file_path = value['path']
                item['front_image_path'] = image_file_path

        return item


class MysqlPipeLine(object):
    """
    同步执行插入数据库操作,但是scrapy的爬取速度可能超过mysql的插入速度,这样处理会拖慢scrapy的爬取
    """
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', 'MCC0420', 'article_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
                insert into article(title, url, create_date, fav_nums, url_object_id)
                VALUES (%s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item['title'], item['url'], item['create_date'], item['fav_nums'], item['url_object_id']))
        self.conn.commit()


class MysqlTwistedPipeLine(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    """
    使用twisted提供的异步容器执行插入数据库操作
    """
    @classmethod
    def from_settings(cls, settings):

        dbparams = dict(
                host=settings['MYSQL_HOST'],
                db=settings['MYSQL_DBNAME'],
                user=settings['MYSQL_USER'],
                passwd=settings['MYSQL_PASSWORD'],
                charset='utf8',
                cursorclass=MySQLdb.cursors.DictCursor,
                use_unicode=True
                )

        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)  # 处理异常

    def handle_error(self, failure):
        # 处理异步插入的一场
        print(failure)

    def do_insert(self, cursor, item):

        insert_sql = """
                        insert into article(title, url, create_date, fav_nums, url_object_id)
                        VALUES (%s, %s, %s, %s, %s)
                """
        cursor.execute(insert_sql,
                            (item['title'], item['url'], item['create_date'], item['fav_nums'], item['url_object_id']))
