# -*- encoding: utf-8 -*-
"""
@File    : __init__.py.py
@Time    : 2020/6/3 10:49
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :
"""
from multiprocessing import Pipe
from typing import Dict, Callable, Optional
from multiprocessing import Process
from Chise.wsoket.client import WebsocketClient
from Chise.Secret.md5 import check_sign
from Service import server_id
from Service.user_info import get_all_userInfo, get_userInfo
import ujson as json
from main import run


class Client(WebsocketClient):
    account_pipe: Dict[str, Pipe] = {}
    pro_list: Dict[int, Process] = {}
    cbk: Optional[Callable] = None  # 获取信息之后如果该参数不为None则调用

    def register_cbk(self, cbk: Callable):
        """
        注册回调函数
        :param cbk:
        :return:
        """
        self.cbk = cbk

    def add_account(self, account_id: int):
        """
        增加项目
        :param account_id:
        :return:
        """
        pass

    def create_process(self, pipe: Pipe, user_info) -> Process:
        """
        生成一个工作进程，并执行
        :param pipe:
        :return:
        """
        process = Process(target=run, args=(user_info, pipe))
        process.start()
        return process

    def on_message(self, ws, message):
        """
        根据websocket获取信息然后操作进程和线程数据,
        根据获取到的account_id，启动或重启account_id对应的进程,
        :return:
        """
        msg: dict = json.loads(message)
        if check_sign(msg):
            if self.cbk:
                self.cbk(self, msg)
            else:
                print(msg)
        else:
            print("签名错误：", msg)
            self.send_message({"code": 401, "msg": '签名错误'})

    def work(self, address):
        users = get_all_userInfo()
        for user_info in users:
            parent_pipe, child_pipe = Pipe()  #
            self.account_pipe[user_info['id']] = (parent_pipe, child_pipe)
            process = self.create_process(child_pipe, user_info)
            self.pro_list[user_info['id']] = process
        self.run(address + "/" + server_id.replace('-','')+"/")


def test_cbk(self: Client, msg: dict):
    print(msg)
    if msg['info'] == "restart":  # 重启进程
        for i in self.pro_list:
            if i == msg['account_id']:
                self.pro_list[i].terminate()
                # 更新user_info数据
                # 重启
                user_info = get_userInfo(msg['account_id'])
                self.pro_list[i] = self.create_process(self.account_pipe[i][1], user_info=user_info)
        else:
            raise Exception("未找到对应account！")
    raise Exception("未找到对应指令")


if __name__ == '__main__':
    client = Client()
    client.register_cbk(test_cbk)
    client.work("ws://127.0.0.1:8000/ws/Slaver")
