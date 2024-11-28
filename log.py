# -*- coding: utf-8 -*-
# Created by HM on 2023-07-08


import logging
import os

from logging.handlers import TimedRotatingFileHandler

APP_ENV = os.getenv('APP_ENV')

work_dir = os.path.dirname(os.path.abspath(__file__))
work_dir = os.path.join(work_dir, 'logs')
log_path = os.path.join(work_dir, 'mss_backend.log')
if not os.path.isdir(work_dir):
    os.mkdir(work_dir)

logger = logging.getLogger(__name__)
logger.handlers.clear()
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s [line:%(lineno)d] - %(message)s')

# 1
file_handler = TimedRotatingFileHandler(log_path, when="H", interval=1, backupCount=24)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
if APP_ENV == 'prod':
    logger.addHandler(file_handler)
# 2
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
