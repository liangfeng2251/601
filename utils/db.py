# -*- coding: utf-8 -*-
# Created by HM on 2023-07-08


import os
from minio import Minio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import Callable

from conf.setting_env import SettingDev, SettingProd


def make_setting():
    config = {
        'dev': SettingDev(),
        'prod': SettingProd(),
    }
    env_value = os.environ.get('APP_ENV')
    _settings = config[env_value]
    return _settings


# 获取当前配置
settings = make_setting()

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)

async_session: Callable[..., AsyncSession] = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


minio_client = Minio(
    endpoint=settings.MINIO_ENDPOINT, access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY, secure=False
)
