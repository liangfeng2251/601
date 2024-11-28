# -*- coding: utf-8 -*-
# Created by HM on 2023-07-08

from sqlalchemy import false, true
from sqlalchemy.sql import select, update, delete

from utils.SQLModels import Recycle, Files
from utils.db import async_session
from utils.Rest import ResponseCode, request_handle
from log import logger


@request_handle
async def recover_file(fids, user_id):
    """恢复"""
    msg = '恢复失败'

    async with async_session() as db:
        for i in fids:
            sql = delete(Recycle).where(
                Recycle.file_id == i, Recycle.user_id == user_id
            )
            res = (await db.execute(sql)).rowcount
            await db.commit()

            if res:
                sql = update(Files).where(Files.file_id == i, Files.user_id == user_id).values(is_delete=false())
                await db.execute(sql)
                await db.commit()
        await db.close()

    if res:
        logger.info('恢复成功')
        msg = '恢复成功'
    return ResponseCode.SUCCESS, msg, None


@request_handle
async def delete_file(fids, user_id):
    """删除文件"""
    msg = '删除失败'

    async with async_session() as db:
        for i in fids:
            sql = update(Recycle).where(Recycle.file_id == i, Recycle.user_id == user_id).values(is_delete=true())
            res = (await db.execute(sql)).rowcount
            await db.commit()
        await db.close()
    if res:
        msg = '删除成功'

    return ResponseCode.SUCCESS, msg, None


@request_handle
async def clear_recycle(user_id):
    """清空回收站"""
    async with async_session() as db:
        sql = update(Recycle).where(Recycle.user_id == user_id).values(is_delete=true())
        await db.execute(sql)
        await db.commit()
        await db.close()
    return ResponseCode.SUCCESS, '清空成功', None


@request_handle
async def get_folder(user_id):
    """获取用户下回收站"""
    data = []

    async with async_session() as db:
        sql = select(Recycle.file_id, Recycle.file_name, Recycle.create_time).filter(
            Recycle.is_delete == false(), Recycle.user_id == user_id
        )
        res = (await db.execute(sql)).fetchall()
        if not res:
            return ResponseCode.SUCCESS, '查询成功', []

        await db.close()

    for i in res:
        file_id, file_name, create_time = i
        data.append({'file_id': file_id, 'file_name': file_name, 'create_time': str(create_time)})
    return ResponseCode.SUCCESS, '查询成功', data
