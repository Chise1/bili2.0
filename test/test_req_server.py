# -*- encoding: utf-8 -*-
"""
@File    : test_req_server.py
@Time    : 2020/6/9 19:14
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :测试和服务器的交互
"""
from Service.user_info import get_userInfo, get_all_userInfo


def test_get_userinfo():
    print(get_userInfo(1))
def test_get_alluser():
    print(get_all_userInfo())

if __name__ == '__main__':
    # test_get_userinfo()
    test_get_alluser()
