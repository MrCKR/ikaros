# -*- coding: utf-8 -*-

import os
import json
import logging
import time

from flask import request, Response

from src.bizlogic.schedulertask import cleanRecordsTask

from . import web
from flask import current_app
from ..service.configservice import notificationConfService

@web.route("/api/options/loglevel", methods=['GET', 'PUT'])
def loglevel():
    """
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
    """
    try:
        if request.method == 'GET':
            level = current_app.logger.level
            ret = {'loglevel': level}
            return json.dumps(ret)
        if request.method == 'PUT':
            content = request.get_json()
            if content and 'loglevel' in content:
                level = int(content.get('loglevel'))
                current_app.logger.setLevel(level)
            else:
                current_app.logger.setLevel(logging.INFO)
            return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/options/cleanrecord", methods=['GET'])
def cleanErrData():
    """ clean record file not exist
    """
    try:
        cleanRecordsTask(True)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)

# TODO refactor log

def flask_logger():
    """creates logging information"""
    localPath = os.path.dirname(os.path.abspath(__file__))
    # TODO get web.log
    logfile = os.path.join(localPath, "..", "..", "database", "web.log")
    with open(logfile, encoding='UTF-8') as log_info:
        for i in range(25):
            data = log_info.read()
            yield data.encode()
            time.sleep(1)


@web.route("/api/options/logstream", methods=["GET"])
def stream():
    """returns logging information"""
    return Response(flask_logger(), mimetype="text/plain", content_type="text/event-stream; charset=utf-8")


@web.route("/api/options/notification", methods=["GET"])
def getNotificationConfig():
    """returns notification config"""
    try:
        content = notificationConfService.getConfig().serialize()
        return json.dumps(content)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)

@web.route("/api/options/notification", methods=['PUT'])
def updateNotifiConf():
    try:
        content = request.get_json()
        notificationConfService.updateConfig(content)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)
