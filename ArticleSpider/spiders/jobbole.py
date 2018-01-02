# -*- encoding:utf-8 -*-

import scrapy
from datetime import datetime
from scrapy.http import Request
from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from scrapy.loader import ItemLoader
import urlparse
import sys
import re
reload(sys)
sys.setdefaultencoding('utf8')  # python在加载引入的模块的时候会禁用setdefaultencoding函数，所以需要reload（）


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取文件列表页中的文章url并交给scrapy下载后交给解析函数进行具体字段的解析
        2. 获取下一页的url并交给scrapy进行下载
        :param response:
        :return:
        """

        post_nodes = response.css('#archive .floated-thumb .post-thumb a')

        for post_node in post_nodes:
            image_url = post_node.css('img::attr(src)').extract_first()
            post_url = post_node.css('::attr(href)').extract_first()
            yield Request(url=urlparse.urljoin(response.url, post_url), callback=self.detail_parse,
                          meta={"front_image_url": urlparse.urljoin(response.url, image_url)})

        next_url = response.css('.next.page-numbers::attr(href)').extract_first('')
        if next_url:
            yield Request(url=next_url, callback=self.parse)

    def detail_parse(self, response):
        # article_item = JobBoleArticleItem()

        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        # create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace(' ·', '').strip()
        # praise_nums = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract()[0]
        # fav_nums = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract()[0]
        # match_re = re.match(".*?(\d+).*", fav_nums)
        # if match_re:
        #     fav_nums = match_re.group()[1]
        # else:
        #     fav_nums = 0
        # comment_nums = response.xpath('//span[contains(@class, "href-style hide-on-480")]/text()').extract()[0]
        # match_re = re.match(".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums = match_re.group()[1]
        # content = response.xpath('//div[@class="entry"]').extract()[0]
        # tag_list = response.xpath('//*[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ','.join(tag_list)

        # front_image_url = response.meta.get('front_image_url', '')
        # title = response.css('.entry-header h1::text').extract_first("")
        # create_date = response.css('p.entry-meta-hide-on-mobile::text').extract_first("").strip().replace(' ·', '').strip()
        # praise_nums = response.css('.vote-post-up h10::text').extract_first("")
        # fav_nums = response.css('.bookmark-btn::text').extract_first("")
        # match_re = re.match(".*?(\d+).*", fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        # comment_nums = response.css('a[href="#article-comment"] span::text').extract_first("")
        # match_re = re.match(".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        # content = response.css('div.entry').extract_first("")
        # tag_list = response.css('p.entry-meta-hide-on-mobile a::text').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ','.join(tag_list)
        #
        # article_item['title'] = title
        # article_item['url'] = response.url
        # article_item['url_object_id'] = get_md5(response.url)
        # try:
        #     create_date = datetime.strptime(create_date, '%Y/%m/%d').date()
        # except Exception:
        #     create_date = datetime.now().date()
        # article_item['create_date'] = create_date
        # article_item['front_image_url'] = [front_image_url]
        # article_item['praise_nums'] = praise_nums
        # article_item['fav_nums'] = fav_nums
        # article_item['comment_nums'] = comment_nums
        # article_item['tags'] = tags
        # article_item['content'] = content

        # 通过item_loader加载item
        front_image_url = response.meta.get('front_image_url', '')
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_value('front_image_url', [front_image_url])
        item_loader.add_css('title', '.entry-header h1::text')
        item_loader.add_css('create_date', 'p.entry-meta-hide-on-mobile::text')
        item_loader.add_css('praise_nums', '.vote-post-up h10::text')
        item_loader.add_css('fav_nums', '.bookmark-btn::text')
        item_loader.add_css('comment_nums', 'a[href="#article-comment"] span::text')
        item_loader.add_css('content', 'div.entry')
        item_loader.add_css('tags', 'p.entry-meta-hide-on-mobile a::text')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))

        article_item = item_loader.load_item()
        yield article_item
