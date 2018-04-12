# -*- coding:utf-8 -*-
import json
import re
from datetime import datetime

import scrapy

import urlparse

import os

from scrapy.loader import ItemLoader

from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu_sel'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com']

    # question的第一页answer的请求url
    start_answer_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,upvoted_followees;data[*].mark_infos[*].url;data[*].author.follower_count,badge[?(type=best_answerer)].topics&limit={1}&offset={2}'

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
        all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)
        for url in all_urls:
            # print url
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)

                yield scrapy.Request(url=request_url, meta={'question_id': question_id}, headers=self.headers,
                                     callback=self.parse_question)
            else:
                # 深度优先：不是question路由就继续追踪
                yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):

        # 处理question页面， 从页面中提取出具体的question item
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        if 'QuestionHeader-title' in response.text:
            # 处理新版本
            item_loader.add_css('title', 'h1.QuestionHeader-title::text')
            item_loader.add_css('content', '.QuestionHeader-detail')
            item_loader.add_value('url', response.url)
            item_loader.add_value('zhihu_id', int(response.meta.get('question_id')))
            item_loader.add_css('answer_num', '.List-headerText span::text')
            item_loader.add_css('comments_num', '.QuestionHeader-Comment button::text')
            item_loader.add_css('watch_user_num', '.NumberBoard-itemValue::text')
            item_loader.add_css('topics', '.QuestionHeader-tags .Popover div::text')

            question_item = item_loader.load_item()

            yield scrapy.Request(url=self.start_answer_url.format(response.meta.get('question_id'), 20, 0),
                                 callback=self.parse_answer, headers=self.headers)
            yield question_item

            all_urls = response.css('a::attr(href)').extract()
            all_urls = [urlparse.urljoin(response.url, url) for url in all_urls]
            all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)
            for url in all_urls:
                # print url
                match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
                if match_obj:
                    request_url = match_obj.group(1)
                    question_id = match_obj.group(2)

                    yield scrapy.Request(url=request_url, meta={'question_id': question_id}, headers=self.headers,
                                         callback=self.parse_question)
                else:
                    # 深度优先：不是question路由就继续追踪
                    yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse_answer(self, response):

        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json['paging']['is_end']
        next_url = ans_json['paging']['next']

        # 提取answer的具体字段
        for answer in ans_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if 'id' in answer['author'] else None
            answer_item['content'] = answer['content'] if 'content' in answer else answer['excerpt']
            answer_item['parise_num'] = answer['voteup_count']
            answer_item['comments_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            answer_item['crawl_time'] = datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(url=next_url, callback=self.parse_answer, headers=self.headers)

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
        browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys('phone_number')
        browser.find_element_by_css_selector(".SignFlow-password input").send_keys('password')
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

    def dept(self, response):
        """
        深度优先：
        if question相关路由交给parse_question处理， else 交给parse函数继续抓取
        :param response:
        :return:
        """
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [urlparse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)
        for url in all_urls:
            # print url
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)

                yield scrapy.Request(url=request_url, meta={'question_id': question_id}, headers=self.headers,
                                     callback=self.parse_question)
            else:
                # 深度优先：不是question路由就继续追踪
                yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)
