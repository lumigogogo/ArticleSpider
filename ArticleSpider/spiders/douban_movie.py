# -*- coding: utf-8 -*-
import urlparse

import scrapy
from scrapy.http import Request


class DoubanMovieSpider(scrapy.Spider):
    name = 'douban_movie'
    allowed_domains = ['movie.douban.com/top250']
    start_urls = ['https://movie.douban.com/top250']
    heards = {
        'HOST': 'movie.douban.com',
        'Referer': 'https://movie.douban.com/top250',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'
    }

    def parse(self, response):
        self.heards['Referer'] = 'https://movie.douban.com/subject'
        post_nodes = response.css('.item')

        for _p_node in post_nodes:
            is_watch = _p_node.css('.playable ')
            image_url = _p_node.css('img::attr(src)').extract_first()
            post_url = _p_node.css('.hd a::attr(href)').extract_first()
            yield Request(url=post_url, callback=self.detail_parse, dont_filter=True,
                          meta={'front_img_url': urlparse.urljoin(response.url, image_url)}, headers=self.heards)
        next_url = response.css('.next a::attr(href)').extract_first()
        if next_url:
            yield Request(url=urlparse.urljoin(response.url, next_url), callback=self.parse, dont_filter=True, headers=self.heards)

    def start_requests(self):
        return [scrapy.Request(url='https://movie.douban.com/top250', headers=self.heards, callback=self.parse)]

    def detail_parse(self, response):

        front_img_url = response.meta.get('front_img_url', '')
