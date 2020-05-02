#! /usr/bin/env python3
'''
    Firmware Analysis and Comparison Tool (FACT)
    Copyright (C) 2015-2019  Fraunhofer FKIE

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import logging
import signal
import sys
from time import sleep

from statistic.work_load import WorkLoadStatistic
from storage.MongoMgr import MongoMgr
from helperFunctions.program_setup import program_setup, was_started_by_start_fact

PROGRAM_NAME = 'FACT DB-Service'
PROGRAM_DESCRIPTION = 'Firmware Analysis and Compare Tool (FACT) DB-Service'

# 通过run进行程序运行开关控制 信号处理函数
def shutdown(*_):
    global run
    logging.info('shutting down {}...'.format(PROGRAM_NAME))
    run = False

# start_fact_db Mongodb数据用于存储固件数据
if __name__ == '__main__':
    # print('was_started_by_start_fact():',was_started_by_start_fact())
    if was_started_by_start_fact():
        # 设置信号处理函数 signal.signal(signalnum,handler)
        # SIGUSR1 用户信号,进程可自定义用途
        signal.signal(signal.SIGUSR1, shutdown)
        # signal.SIGINT 由键盘引起的终端终止Ctrl-c
        signal.signal(signal.SIGINT, lambda *_: None)
    else:
        signal.signal(signal.SIGINT, shutdown)

    args, config = program_setup(PROGRAM_NAME, PROGRAM_DESCRIPTION)
    # 初始化mongodb类型的对象的属性,并运行mongo数据库
    mongo_server = MongoMgr(config=config)
    # 更新系统状态
    work_load_stat = WorkLoadStatistic(config=config, component='database')

    run = True
    while run:
        work_load_stat.update()
        sleep(5)
        if args.testing:
            break

    work_load_stat.shutdown()
    mongo_server.shutdown()

    sys.exit()
