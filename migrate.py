# -*- coding: utf-8 -*-
# Created by HM on 2023-07-08


import typer
import os
import re

from utils.db import settings, minio_client


app = typer.Typer()


@app.command()
def hello():
    print('Mss!!!')


@app.command(help='初始化数据库，新增Minio bucket')
def init():
    res = open('alembic.ini', 'r', encoding='utf8').read()
    with open('alembic.ini', 'w', encoding='utf8') as f:
        mysql_url = settings.SQLALCHEMY_DATABASE_URI_TEST + '/' + settings.DB_DATABASE + '?charset=utf8mb4'
        response = re.sub(r'mysql\+pymysql://.*', mysql_url, res)
        f.write(response)
        f.close()

    os.system('alembic upgrade head')

    try:
        is_exists = minio_client.bucket_exists(settings.MINIO_BUCKET_NAME)
        if not is_exists:
            minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
            print('init minio complete')

    except Exception as e:
        print('初始化失败：', e)


if __name__ == "__main__":
    app()
