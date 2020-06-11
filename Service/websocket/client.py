# -*- encoding: utf-8 -*-
"""
@File    : t2.py
@Time    : 2020/6/3 12:44
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
# coding:utf-8

import websocket
import ujson as json
import time
import threading
from Chise.Secret.md5 import add_sign, check_sign
from typing import Callable, Optional
# import logging
# logger = logging.getLogger(__name__)


class WebsocketClient(object):
    """docstring for WebsocketClient"""

    def __init__(self, address, message_callback: Optional[Callable] = None):
        """
        :param address:
        :param message_callback: 收到信息之后处理的回调函数
        """
        super(WebsocketClient, self).__init__()
        self.address = address
        self.message_callback = message_callback

    def on_message(self, ws, message):
        """
        处理数据
        :param ws:
        :param message:
        :return:
        """
        msg: dict = json.loads(message)
        if check_sign(msg):
            if self.message_callback:
                self.message_callback(msg)
            else:
                print(msg)
        else:
            print("签名错误：", msg)
            self.send_message({"code": 401, "msg": '签名错误'})

    def on_error(self, ws, error):
        print("client error:", error)

    def on_close(self, ws):
        print("### client closed ###")
        self.ws.close()
        self.is_running = False

    def on_open(self, ws):
        self.is_running = True
        print("on open")

    def close_connect(self):
        self.ws.close()

    def send_message(self, message: dict):
        """
        对数据进行签名，并发送数据
        :param message:
        :return:
        """
        data = json.dumps(add_sign(message))
        try:
            self.ws.send(data)
        except BaseException as err:
            print(err)

    def __run(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.address,
                                         on_message=lambda ws, message: self.on_message(ws, message),
                                         on_error=lambda ws, error: self.on_error(ws, error),
                                         on_close=lambda ws: self.on_close(ws))
        self.ws.on_open = lambda ws: self.on_open(ws)
        self.is_running = False
        while True:
            print(self.is_running)
            if not self.is_running:
                self.ws.run_forever()
            time.sleep(3)

    def run_client(self):
        self.client_thread = threading.Thread(target=self.__run)  # 线程参数
        self.client_thread.start()