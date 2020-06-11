# -*- encoding: utf-8 -*-
"""
@File    : test_wbsocket.py
@Time    : 2020/6/11 18:26
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :测试服务器websocket链接
"""
import websocket

from Service import server_id


def on_message(ws, message):
    print(ws)
    print(message)


def on_error(ws, error):
    print(ws)
    print(error)


def on_close(ws):
    print(ws)
    print("### closed ###")


websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://127.0.0.1:8000/ws/Slaver/"+server_id.replace('-','')+"/",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)

ws.run_forever()