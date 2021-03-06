import sys
import signal
import threading
import asyncio
from copy import deepcopy
import aiohttp
import conf_loader
import notifier
import bili_sched
import printer
import bili_statistics
from console_cmd import ConsoleCmd
from tasks.login import LoginTask
from tasks.live_daily_job import (HeartBeatTask, OpenSilverBoxTask, RecvDailyBagTask, SignTask, WatchTvTask,
                                  SignFansGroupsTask, SendGiftTask, ExchangeSilverCoinTask)
from tasks.main_daily_job import (JudgeCaseTask, BiliMainTask, DahuiyuanTask)
from tasks.manga_daily_job import (ShareComicTask, MangaSignTask, )
from tasks.utils import UtilsTask
# 弹幕
from danmu.bili_danmu_monitor import DanmuPrinter, DanmuRaffleMonitor
from danmu.yj_monitor import TcpYjMonitorClient
from danmu import raffle_handler
# 实物抽奖
from substance.monitor_substance_raffle import SubstanceRaffleMonitor
from dyn.monitor_dyn_raffle import DynRaffleMonitor
from Service.Crsa import rsa_long_decrypt
from multiprocessing import connection


def run(user_info: dict, pipe: connection.Connection):
    """
    :param user_info: 用户信息
    :param pipe:进程间通信管道
    :return:
    """
    notifier.register_pipe(pipe)
    user_info['password'] = rsa_long_decrypt(eval(user_info['password']))
    user_info_copy = deepcopy(user_info)
    # print(user_info['password'])
    loop = asyncio.get_event_loop()
    dict_bili = conf_loader.read_bili()
    dict_color = conf_loader.read_color()
    dict_ctrl = conf_loader.read_ctrl()
    dict_task = conf_loader.read_task()
    printer.init_config(dict_color, dict_ctrl['print_control']['danmu'])

    ############################################################################
    ############################################################################
    # 👇users 录入程序

    async def init_users():
        global_task_control = dict_task['global_task_control']
        custom_task_control = dict_task['custom_task_control']
        global_task_arrangement = dict_task['global_task_arrangement']
        custom_task_arrangement = dict_task['custom_task_arrangement']
        users = notifier.Users(global_task_control=global_task_control,
                               global_task_arrangement=global_task_arrangement,
                               dict_bili=dict_bili,
                               force_sleep=bili_sched.force_sleep)
        notifier.init(users=users)
        username = user_info['username']
        await notifier.add_user(user_info=user_info_copy,
                                custom_task_control=custom_task_control.get(username, {}),
                                custom_task_arrangement=custom_task_arrangement.get(username, {}))
    loop.run_until_complete(init_users())
    ############################################################################
    ############################################################################
    # 👇重复任务录入程序

    # 时间间隔为小时，同时每次休眠结束都会计时归零，重新从当前时间计算时间间隔
    # 下面表示每隔多少小时执行一次
    def add_daily_jobs(tasks):
        for task in tasks:
            if task['status']:
                if task['frequency_unit'] == 2:
                    fre = 1
                elif task['frequency_unit'] == 1:
                    fre = 60
                elif task['frequency_unit'] == 3:
                    fre = 1 / 24
                elif task['frequency_unit'] == 0:
                    fre = 3600
                else:
                    raise Exception("fre不能为空！")
                    # fre = 1
                bili_sched.add_daily_jobs(globals()[task['task']], every_hours=task['frequency_num'] / fre)  # 心跳
                print("成功添加任务：", task['task'])
        bili_sched.add_daily_jobs(HeartBeatTask, every_hours=6)  # 心跳
        # bili_sched.add_daily_jobs(OpenSilverBoxTask, every_hours=6)  # 每日开宝箱任务
        bili_sched.add_daily_jobs(RecvDailyBagTask, every_hours=3)  #
        # bili_sched.add_daily_jobs(SignTask, every_hours=6)  # 直播签到
        # bili_sched.add_daily_jobs(WatchTvTask, every_hours=6)  # 双端观看任务
        # bili_sched.add_daily_jobs(SignFansGroupsTask, every_hours=6)  # 签名粉丝组任务
        # bili_sched.add_daily_jobs(SendGiftTask, every_hours=2)  # 送礼物的任务
        # bili_sched.add_daily_jobs(ExchangeSilverCoinTask, every_hours=6)  # 硬币兑换
        bili_sched.add_daily_jobs(JudgeCaseTask, every_hours=0.75)  # 风纪委员任务
        bili_sched.add_daily_jobs(BiliMainTask, every_hours=4)  # 主任务
        # bili_sched.add_daily_jobs(MangaSignTask, every_hours=6)  # 漫画签到
        # bili_sched.add_daily_jobs(ShareComicTask, every_hours=6)  # 漫画分享任务
        bili_sched.add_daily_jobs(DahuiyuanTask, every_hours=6)

    if user_info.get('tasks'):
        tasks = user_info.get('tasks')
    else:
        tasks = []
    add_daily_jobs(tasks)
    ############################################################################
    ############################################################################
    # 登录
    loop.run_until_complete(notifier.exec_task(LoginTask))
    other_control = dict_ctrl['other_control']
    area_ids = loop.run_until_complete(notifier.exec_func(UtilsTask.fetch_blive_areas))
    area_duplicated = other_control['area_duplicated']
    if area_duplicated:
        area_ids *= 2
    bili_statistics.init(area_num=len(area_ids), area_duplicated=area_duplicated)
    default_roomid = other_control['default_monitor_roomid']

    ############################################################################
    ############################################################################
    # 👇录入 monitors
    # aiohttp sb session
    async def init_monitors():
        session = aiohttp.ClientSession()
        monitors_ = []
        # 弹幕打印功能
        danmu_printer_ = DanmuPrinter(
            room_id=default_roomid,
            area_id=-1,
            session=session)

        # 弹幕抽奖监控
        for area_id in area_ids:
            monitor = DanmuRaffleMonitor(
                room_id=0,
                area_id=area_id,
                session=session)
            monitors_.append(monitor)

        # yjmonitor 弹幕监控
        yjmonitor_tcp_addr = other_control['yjmonitor_tcp_addr']
        yjmonitor_tcp_key = other_control['yjmonitor_tcp_key']
        if yjmonitor_tcp_key:
            monitor = TcpYjMonitorClient(
                key=yjmonitor_tcp_key,
                url=yjmonitor_tcp_addr,
                area_id=0)
            monitors_.append(monitor)
        if other_control['substance_raffle']:
            monitors_.append(SubstanceRaffleMonitor())
        if other_control['dyn_raffle']:
            monitors_.append(DynRaffleMonitor(
                should_join_immediately=other_control['join_dyn_raffle_at_once']))
        return danmu_printer_, monitors_

    danmu_printer, monitors = loop.run_until_complete(init_monitors())
    ############################################################################
    ############################################################################

    bili_sched.init(monitors=monitors, sleep_ranges=dict_ctrl['other_control']['sleep_ranges'])

    # 初始化控制台
    if sys.platform != 'linux' or signal.getsignal(signal.SIGHUP) == signal.SIG_DFL:
        console_thread = threading.Thread(
            target=ConsoleCmd(loop, default_roomid, danmu_printer).cmdloop)
        console_thread.start()
    else:
        console_thread = None

    tasks = [monitor.run() for monitor in monitors]
    other_tasks = [
        bili_sched.run(),
        raffle_handler.run(),
        danmu_printer.run()
    ]
    if other_tasks:
        loop.run_until_complete(asyncio.wait(tasks + other_tasks))
    loop.run_forever()
    if console_thread is not None:
        console_thread.join()

from Service.wbs import Client, test_cbk

if __name__ == '__main__':
    client = Client()
    client.register_cbk(test_cbk)
    client.work("ws://127.0.0.1:8000/ws/Slaver", run)