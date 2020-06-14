# -*- encoding: utf-8 -*-
"""
@File    : md5.py
@Time    : 2020/6/3 11:15
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
import hashlib
from . import app_secret


def get_sign(data_dict: dict):
    '''
    生成签名
    '''
    params_list = sorted(data_dict.items(), key=lambda e: e[0], reverse=False)
    params_str = "&".join(u"{}={}".format(k, v) for k, v in params_list ) + '&' + app_secret
    md5 = hashlib.md5()
    md5.update(params_str.encode('utf-8'))
    sign = md5.hexdigest().upper()
    return sign
def check_sign(data_dict:dict):
    """
    检查sign是否正确
    :param data_dict:
    :return:
    """
    return True
    print("获取数据:",data_dict)
    sign=data_dict.pop('sign')
    if not sign:
        return False
    if sign!=get_sign(data_dict):
        return False
    return True
def add_sign(data_dict:dict):
    """
    给数据增加sign字段
    :param data_dict:
    :return:
    """
    sign=get_sign(data_dict)
    data_dict['sign']=sign
    return data_dict