# -*- coding: utf-8 -*-

import requests
import cookielib
import re

# 会话：使用session就不用每次请求都要建立一次链接
session = requests.session()

# 使用cookielib.LWPCookieJar函数保存cookie
session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
try:
    session.cookies.load(ignore_discard=True)
except:
    print 'cookie未能加载'

agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
header = {
    'HOST': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com',
    'User-Agent': agent
}


def is_login():
    # 通过个人中心页面返回状态码来判断是否为登入状态
    inbox_url = 'https://www.zhihu.com/settings/profile'
    # allow_redirects 参数设置是否要根据服务器返回去重定向，如果为True（默认是True）就总是返回200code（无法根据状态码判断是否已经成功登入）
    response = session.get(url=inbox_url, headers=header, allow_redirects=False)
    if response.status_code != 200:
        return False
    return True


def get_xsrf():

    # 获取xsrf code
    response = session.get('https://www.zhihu.com', headers=header)
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text)
    if match_obj:
        return match_obj.groups(1)
    return ""


def get_index():

    # 测试session.cookies.load() 是否正确的将cookie加载进来
    response = session.get('https://www.zhihu.com', headers=header)
    with open('index_page.html', 'wb') as f:
        f.write(response.text.encode('utf-8'))
    print 'OK'


def zhihu_login(account, password):

    # 知乎登入
    if re.match("1\d{10}", account):
        print '手机号登入'
        post_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        post_data = {
            '_xsrf': get_xsrf(),
            'phone_num': account,
            'password': password
        }
    else:
        print '邮箱登入'
        post_url = 'https://www.zhihu.com/login/email'
        post_data = {
            '_xsrf': get_xsrf(),
            'email': account,
            'password': password
        }
    response_text = session.post(url=post_url, data=post_data, headers=header)

    # 如果登入成功保存cookie
    session.cookies.save()


zhihu_login('18817314957', 'MCC0420')

