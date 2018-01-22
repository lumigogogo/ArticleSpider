# -*- coding: utf-8 -*-
import json
import re

import scrapy


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    heards = {
        'HOST': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
    }

    def parse(self, response):
        pass

    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/signup?next=%2F', callback=self.login)]

    def login(self, response):

        response_text = response.text
        # re.DOTALL 匹配全部数据
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        xsrf = ''
        if match_obj:
            xsrf = match_obj.groups(1)

        if xsrf:
            return [scrapy.FormRequest(
                url='https://www.zhihu.com/api/v3/oauth/sign_in',
                formdata={
                    '_xsrf': xsrf,
                    'phone_num': '18817314957',
                    'password': 'MCC0420'
                },
                headers=self.heards,
                callback=self.check_login
            )]

    def check_login(self, response):

        # 验证服务器的返回数据判断是否成功
        text_json = json.loads(response.text)
        if 'msg' in text_json and text_json['msg'] == '登入成功':
            for url in self.start_urls:
                yield scrapy.Request(url=url, dont_filter=True, headers=self.heards)