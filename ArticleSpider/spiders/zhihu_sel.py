# -*- coding:utf-8 -*-

import scrapy

import urlparse

import os


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu_sel'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com']

    # question的第一页answer的请求url
    start_answer_url = ''

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        """
        提取出html页面中的所有url 并跟踪这些url进行一步爬取
        如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
        """
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [urlparse.urljoin(response.url, url) for url in all_urls]
        for url in all_urls:
            pass

    def parse_question(self, response):
        # 处理question页面， 从页面中提取出具体的question item
        pass

    def parse_answer(self, reponse):
        pass

    def start_requests(self):

        _path = '/home/lumi/GitHub/ArticleSpider/cookies'
        files = os.listdir('/home/lumi/GitHub/ArticleSpider/cookies')
        import pickle
        if files:
            cookie_dict = {}
            # cookie 已经存在
            for _f in files:
                _name = _f.split('|')[1].split('.')[0]
                _value = pickle.load(open(_path + '/' + _f))
                cookie_dict[_name] = _value
            return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict, headers=self.headers)]

        from selenium import webdriver
        browser = webdriver.Firefox(executable_path='/home/lumi/Downloads/geckodriver')

        browser.get('https:/www.zhihu.com/signin')
        browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys('18817314957')
        browser.find_element_by_css_selector(".SignFlow-password input").send_keys('MCC0420')
        browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
        import time
        time.sleep(10)
        Cookies = browser.get_cookies()
        print Cookies
        cookie_dict = {}
        for cookie in Cookies:
            # 写入文件
            with open(_path + '/zhihu|' + cookie['name'] + '.zhihu', 'wb') as f:
                pickle.dump(cookie['value'], f)
                cookie_dict[cookie['name']] = cookie['value']
        browser.close()
        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict, headers=self.headers)]
