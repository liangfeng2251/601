# -*- coding: utf-8 -*-
# Created by HM on 2023-11-23

import os.path
from configparser import ConfigParser

from log import logger
from type import *
import os


def load_custom_config(config_path):
    if not (config_path and os.path.isfile(config_path)):
        logger.info('Config file not found, using default config.')
        return
    logger.info('Using config file: {}'.format(config_path))
    config_parser.read(config_path)


def get_config(config_name):
    # dict to object attributes
    return Objdict(config_parser[config_name])


module_name = 'MAS'
module_path = os.path.dirname(os.path.abspath(__file__))

config_parser = ConfigParser(allow_no_value=True)

default_config_path = os.path.join(module_path, 'default.ini')
config_parser.read(default_config_path)
sec = config_parser.sections()


# result file url
config_prod = get_config(module_name + '_PROD')
config_dev = get_config(module_name + '_DEV')

mysql_database_config_prod = get_config('MYSQL_DATABASE_PROD')
mysql_database_config_dev = get_config('MYSQL_DATABASE_DEV')

minio_config_prod = get_config('MINIO_OBJECT_STORAGE_PROD')
minio_config_dev = get_config('MINIO_OBJECT_STORAGE_DEV')


class SettingGloble(object):
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'echo_pool': True,
        'pool_size': 50,
        'max_overflow': 100,
        'pool_recycle': 30
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
