# -*- coding: utf-8 -*-
# Created by HM on 2023-07-08


import os
import shutil
import time
import requests
from sqlalchemy import select, update

from log import logger
from utils.db import settings, async_session
from utils.SQLModels import DailyNums


async def remove_old_file():
    logger.info('自动清理文件')
    delete_folder = ['ocr', 'save_files']

    for d in delete_folder:
        save_files = os.path.join(os.getcwd(), 'models', d)
        if not os.path.exists(save_files):
            continue

        local_files = os.listdir(save_files)
        if not local_files:
            continue

        for u in local_files:
            file_path = os.path.join(save_files, u)
            if os.path.isdir(file_path):
                if not os.path.exists(file_path):
                    logger.info(f'文件夹：{u} 删除失败')
                    continue
                try:
                    shutil.rmtree(file_path)
                except Exception as e:
                    logger.error(e)
                    continue
                logger.info(f'文件夹：{u} 已删除')
            else:
                if not os.path.exists(file_path):
                    logger.info(f'压缩文件：{u} 删除失败')
                    continue
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(e)
                    continue
                logger.info(f'文件：{u} 已删除')


async def daily_tatistics():
    logger.info('自动更新数据监控')
    try:
        session = requests.Session()

        minio_url = str(settings.MINIO_ENDPOINT).split(':')[0] + ':' + settings.MINIO_CONSOLE_PORT
        url = f'http://{minio_url}/api/v1/login'
        res = session.post(url, json={"accessKey": settings.MINIO_ACCESS_KEY, "secretKey": settings.MINIO_SECRET_KEY})
        session.cookies.update({'Cookie': res.headers.get('Set-Cookie')})
        url = f'http://{minio_url}/api/v1/admin/info'
        res = session.get(url).json()
        session.close()
        total_data = res['objects']

        async with async_session() as db:
            today = time.strftime('%Y-%m-%d')
            sql = select(DailyNums.today_num).filter(DailyNums.create_date == today)
            res = (await db.execute(sql)).fetchone()
            if res:
                sql = update(DailyNums).filter(DailyNums.create_date == today).values(today_num=total_data)
                await db.execute(sql)
                await db.commit()
            else:
                new_daily_nums = DailyNums(today_num=total_data)
                db.add(new_daily_nums)
                await db.commit()
            await db.close()
        return None
    except Exception as e:
        logger.error(e)
        logger.error('数据监控更新失败!')
    return None
