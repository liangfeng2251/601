# -*- coding: utf-8 -*-
# Created by HM on 2023-11-23

from pydantic_settings import BaseSettings

from conf.config import *


# 数据库连接
class SettingDev(SettingGloble, BaseSettings):
    config: dict = config_dev
    HOST: str = config['server_host']
    PORT: int = config['server_port']
    USER_NAME: str = config['user_name']
    USER_PASS: str = config['user_pass']
    AUTH_PATH: str = config['auth_path']

    ENVNAME: str = '开发环境'
    DEBUG_MODEL_SWITCH: bool = True  # 服务debug模式只在dev环境开启
    # 数据库连接
    mysql_database_config: dict = mysql_database_config_dev
    DB_HOST: str = mysql_database_config['db_host']
    DB_USER: str = mysql_database_config['db_user']
    DB_PASSWORD: str = mysql_database_config['db_password']
    DB_PORT: int = int(mysql_database_config['db_port'])
    DB_DATABASE: str = mysql_database_config['db_database']
    SQLALCHEMY_DATABASE_URI_TEST: str = "mysql+pymysql://{}:{}@{}:{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    SQLALCHEMY_DATABASE_URI: str = "mysql+aiomysql://{}:{}@{}:{}/{}".format(
        DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE
    )
    # MINIO
    minio_object_storage_config: dict = minio_config_dev
    MINIO_ENDPOINT: str = minio_object_storage_config['minio_endpoint']
    MINIO_CONSOLE_PORT: str = minio_object_storage_config['minio_console_port']
    MINIO_ACCESS_KEY: str = minio_object_storage_config['minio_access_key']
    MINIO_SECRET_KEY: str = minio_object_storage_config['minio_secret_key']
    MINIO_BUCKET_NAME: str = minio_object_storage_config['minio_bucket_name']


class SettingProd(SettingGloble, BaseSettings):
    config: dict = config_prod
    HOST: str = config['server_host']
    PORT: int = config['server_port']
    USER_NAME: str = config['user_name']
    USER_PASS: str = config['user_pass']
    AUTH_PATH: str = config['auth_path']

    ENVNAME: str = '生产环境'
    DEBUG_MODEL_SWITCH: bool = False  # 服务debug模式只在dev环境开启
    # 数据库连接
    mysql_database_config: dict = mysql_database_config_prod
    DB_HOST: str = mysql_database_config['db_host']
    DB_USER: str = mysql_database_config['db_user']
    DB_PASSWORD: str = mysql_database_config['db_password']
    DB_PORT: int = int(mysql_database_config['db_port'])
    DB_DATABASE: str = mysql_database_config['db_database']
    SQLALCHEMY_DATABASE_URI_TEST: str = "mysql+pymysql://{}:{}@{}:{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    SQLALCHEMY_DATABASE_URI: str = "mysql+aiomysql://{}:{}@{}:{}/{}".format(
        DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE
    )
    # MINIO
    minio_object_storage_config: dict = minio_config_prod
    MINIO_ENDPOINT: str = minio_object_storage_config['minio_endpoint']
    MINIO_CONSOLE_PORT: str = minio_object_storage_config['minio_console_port']
    MINIO_ACCESS_KEY: str = minio_object_storage_config['minio_access_key']
    MINIO_SECRET_KEY: str = minio_object_storage_config['minio_secret_key']
    MINIO_BUCKET_NAME: str = minio_object_storage_config['minio_bucket_name']
