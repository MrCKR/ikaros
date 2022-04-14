# -*- coding: utf-8 -*-
'''
'''
import os
import time

from flask import current_app
from ..service.configservice import autoConfigService, transConfigService, scrapingConfService
from ..service.taskservice import autoTaskService, taskService
from .manager import startScrapingAll, startScrapingSingle
from .transfer import autoTransfer
from ..notifications import notificationService


def start(client_path: str):
    """
    """
    task = autoTaskService.getPath(client_path)
    if task:
        current_app.logger.info("自动任务: 已经存在任务")
        return 200
    else:
        current_app.logger.info("自动任务: 加入队列[{}]".format(client_path))
        task = autoTaskService.init(client_path)

    runningTask = autoTaskService.getRunning()
    if runningTask:
        current_app.logger.debug("自动任务: 正在执行其他任务")
    else:
        checkTaskQueue()


def checkTaskQueue():
    """ 任务循环队列
    """
    running = True
    while running:
        runningTask = autoTaskService.getRunning()
        if runningTask:
            current_app.logger.debug("任务循环队列: 正在执行其他任务")
            break

        task = autoTaskService.getFirst()
        if task:
            current_app.logger.info("任务循环队列: 开始[{}]".format(task.path))
            task.status = 1
            autoTaskService.commit()
            try:
                # 在已经有任务要进行情况下
                # 其他任务会加入队列，当前任务等待手动任务完成
                while taskService.haveRunningTask():
                    current_app.logger.debug("任务循环队列: 等待手动任务结束")
                    time.sleep(5)

                runTask(task.path)
            except Exception as e:
                current_app.logger.error(e)
                notificationService.sendtext("自动任务:[{}], 异常:{}".format(task.path,str(e)))
            current_app.logger.info("任务循环队列: 清除任务[{}]".format(task.path))
            autoTaskService.deleteTask(task.id)
        else:
            current_app.logger.info("任务循环队列: 无新任务")
            running = False


def runTask(client_path: str):
    # 1. convert path to real path for flask
    conf = autoConfigService.getSetting()
    real_path = client_path.replace(conf.original, conf.prefixed)
    if not os.path.exists(real_path):
        current_app.logger.debug("任务详情: 不存在路径[{}]".format(real_path))
        return
    current_app.logger.debug("任务详情: 实际路径[{}]".format(real_path))
    # 2. select scrape or transfer
    flag_scraping = False
    scrapingConfId = 0
    flag_transfer = False
    transConfigId = 0
    if conf.scrapingconfs:
        scrapingIds = conf.scrapingconfs.split(';')
        if scrapingIds:
            for sid in scrapingIds:
                sconfig = scrapingConfService.getSetting(sid)
                if sconfig and real_path.startswith(sconfig.scraping_folder):
                    flag_scraping = True
                    scrapingConfId = sid
                    break
    else:
        current_app.logger.error("任务详情: 未配置 自动-刮削配置,请配置后再使用")
    if conf.transferconfs:
        transferIds = conf.transferconfs.split(';')
        if transferIds:
            for tid in transferIds:
                tconfig = transConfigService.getConfigById(tid)
                if tconfig and real_path.startswith(tconfig.source_folder):
                    flag_transfer = True
                    transConfigId = tid
                    break
    else:
        current_app.logger.error("任务详情: 未配置 自动-转移配置,请配置后再使用")
    # 3. run
    status = 99
    if flag_scraping:
        current_app.logger.debug("任务详情: JAV")
        if os.path.isdir(real_path):
            status = startScrapingAll(scrapingConfId, real_path)
        else:
            status = startScrapingSingle(scrapingConfId, real_path)
        if status == 1:
            notificationService.sendtext("自动任务:[{}], 刮削完成,已推送媒体库".format(real_path))
        elif status == 2:
            notificationService.sendtext("自动任务:[{}], 刮削完成,推送媒体库异常".format(real_path))
        else:
            notificationService.sendtext("自动任务:[{}], 刮削异常,详情请查看日志".format(real_path))
    elif flag_transfer:
        status = autoTransfer(transConfigId, real_path)
        if status == 1:
            notificationService.sendtext("自动任务:[{}], 转移完成,已推送媒体库".format(real_path))
        elif status == 2:
            notificationService.sendtext("自动任务:[{}], 转移完成,推送媒体库异常".format(real_path))
        else:
            notificationService.sendtext("自动任务:[{}], 转移异常,详情请查看日志".format(real_path))
    else:
        current_app.logger.error("无匹配的目录")


def clean():
    """ clean all task
    """
    tasks = autoTaskService.getTasks()
    for single in tasks:
        autoTaskService.deleteTask(single.id)
