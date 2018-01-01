# -*- coding: utf-8 -*-

import requests
import cookielib
import re

session = requests.session()

agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'

header = {
    'HOST': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com',
    'User-Agent': agent
}


def get_xsrf():
    response = session.get('https://www.zhihu.com', headers=header)
    print response.text


def zhihu_login(account, password):
    # 知乎登入
    if re.match("1\d{10}", account):
        print '手机号登入'
        post_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        post_data = {

            'phone_num': account,
            'password': password
        }

        response = session.post(post_url, data=post_data, headers=header)
        # session.cookies.save()

        print response.text


zhihu_login('18817314957', 'MCC0420')

