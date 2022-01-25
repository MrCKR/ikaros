# -*- coding: utf-8 -*-
"""
    init app
"""
import logging
import flask_migrate
from concurrent.futures import ThreadPoolExecutor
from flask import Flask
from logging.handlers import TimedRotatingFileHandler
from flask_sqlalchemy import SQLAlchemy

from .config import Config

db = SQLAlchemy()
migrate = flask_migrate.Migrate()
app = None

# DOCS https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
executor = ThreadPoolExecutor(1)

def create_app():
    """ create application
    """
    global app
    app = Flask(__name__, static_url_path='', static_folder='../web/static/', template_folder='../web/templates/')
    app.config.from_object(Config)
    # Configure logging
    formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
    handler = TimedRotatingFileHandler(app.config['LOGGING_LOCATION'], encoding="utf-8", when="midnight", interval=1)
    handler.suffix = "%Y%m%d"
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config['LOGGING_LEVEL'])

    db.app = app
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    from . import controller
    from . import model
    controller.register(app)
    model.load_models()

    db.create_all()
    with app.app_context():
        try:
            print("Upgrade db")
            flask_migrate.upgrade()
        except Exception as e:
            print(e)
            print("Fix alembic version")
            flask_migrate.stamp()

    # reset
    executor.submit(resetDefaults)

    return app


def resetDefaults():
    from .service.taskservice import autoTaskService
    from .bizlogic.automation import checkTaskQueue
    print("Init task started!")
    autoTaskService.reset()
    with app.app_context():
        checkTaskQueue()
    print("Init task is done!")
