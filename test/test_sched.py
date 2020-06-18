# -*- encoding: utf-8 -*-
"""
@File    : test_sched.py
@Time    : 2020/6/18 12:26
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :测试动态删除执行中的任务会不会导致崩溃
"""
import schedule
import time

def job():
    # time.sleep(10)
    # while True:
    #     pass
    print("I'm working...")

schedule.every(1).seconds.do(job).tag('test')
flag=False
def clear():
    time.sleep(10)
    schedule.clear('test')
    print("已清理")
def run():
    while True:
        print("开始执行")
        schedule.run_pending()
        time.sleep(1)
from  threading import Thread
th=Thread(target=clear,).start()
run()

# time.sleep(20)