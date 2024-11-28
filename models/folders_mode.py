# -*- coding: utf-8 -*-
# Created by HM on 2023-11-23


import uuid
from sqlalchemy import false, null, true
from sqlalchemy.sql import select, update

from utils.SQLModels import Folders
from utils.db import async_session
from utils.Rest import ResponseCode, request_handle
from log import logger


@request_handle
async def add_folder(folder_name, parent_id, user_id):
    """新增文件夹"""
    async with async_session() as db:
        sql = select(Folders.folder_id).filter(
            Folders.folder_name == folder_name, Folders.parent_id == parent_id, Folders.is_delete == false()
        )
        res = (await db.execute(sql)).fetchone()
        if res:
            return ResponseCode.CONFLICT, '文件夹已存在', {}

        if parent_id:
            sql = select(Folders.folder_id).filter(Folders.folder_id == parent_id, Folders.is_delete == false())
            res = (await db.execute(sql)).fetchone()
            if not res:
                return ResponseCode.CONFLICT, '父级不存在', {}

        folder_id = str(uuid.uuid4())
        folder = Folders(folder_id=folder_id, parent_id=parent_id, folder_name=folder_name, user_id=user_id)
        db.add(folder)
        await db.commit()
        res = {'folder_id': folder_id, 'folder_name': folder_name, 'parent_id': parent_id}
        logger.info('创建文件夹成功')
        return ResponseCode.SUCCESS, '创建成功', res


@request_handle
async def delete_folder(folder_id, user_id):
    """删除文件夹"""
    async with async_session() as db:
        sql = select(Folders.folder_id, Folders.folder_name, Folders.folder_type).filter(
            Folders.folder_id == folder_id, Folders.user_id == user_id,
            Folders.is_delete == false()
        )
        res = (await db.execute(sql)).fetchone()
        if not res:
            return ResponseCode.CONFLICT, '文件夹不存在', []
        elif res[2]:
            return ResponseCode.CONFLICT, '该文件夹无法被删除', []

        res = [{'id': res[0], 'name': res[1]}]

        async def f(fd):
            for i in fd:
                _id = i['id']
                _sql = select(Folders.folder_id, Folders.folder_name).filter(
                    Folders.user_id == user_id, Folders.parent_id == _id, Folders.is_delete == false())
                _res = (await db.execute(_sql)).fetchall()
                if not _res:
                    continue
                else:
                    dr = list(map(lambda x: {'id': x[0], 'name': x[1]}, _res))
                    fd += await f(dr)
            return fd
        res = await f(res)

        for u in res:
            sql = update(Folders).filter(
                Folders.folder_id == u['id'], Folders.user_id == user_id
            ).values(is_delete=true())
            await db.execute(sql)
            await db.commit()
        return ResponseCode.SUCCESS, '删除成功', res


@request_handle
async def rename_folder(folder_id, folder_name, user_id):
    """重命名文件夹"""
    async with async_session() as db:
        sql = update(Folders).filter(
            Folders.folder_id == folder_id, Folders.user_id == user_id, Folders.folder_type == false(),
            Folders.is_delete == false()
        ).values(folder_name=folder_name)
        res = (await db.execute(sql)).rowcount
        await db.commit()
        if not res:
            return ResponseCode.CONFLICT, '修改失败', []
        return ResponseCode.SUCCESS, '修改成功', {'id': folder_id, 'name': folder_name}


@request_handle
async def get_folder(user_id):
    """获取用户下目录树"""
    async with async_session() as db:
        sql = select(Folders.folder_id, Folders.folder_name).filter(
            Folders.user_id == user_id, Folders.parent_id == null(),
            Folders.is_delete == false()
        )
        res = (await db.execute(sql)).fetchall()
        if not res:
            folder_id = str(uuid.uuid4())
            new_folder = Folders(folder_id=folder_id, folder_name='我的文件夹', user_id=user_id, folder_type=true())
            db.add(new_folder)
            await db.commit()
            folder_id = str(uuid.uuid4())
            new_folder = Folders(folder_id=folder_id, folder_name='数据自产生系统', user_id=user_id, folder_type=true())
            db.add(new_folder)
            await db.commit()
            await db.close()
            return await get_folder(user_id)

        res = list(map(lambda x: {'id': x[0], 'name': x[1]}, res))

        async def f(fd, level=0):
            """递归查询子目录"""
            for i in fd:
                if 'children' in i:
                    continue
                _id = i['id']
                i['level'] = level
                _sql = select(Folders.folder_id, Folders.folder_name).filter(
                    Folders.user_id == user_id, Folders.parent_id == _id, Folders.is_delete == false()
                )
                _res = (await db.execute(_sql)).fetchall()
                if not _res:
                    i['children'] = []
                else:
                    dr = list(map(lambda x: {'id': x[0], 'name': x[1]}, _res))
                    i['children'] = await f(dr, level + 1)
            return fd

        data = await f(res)
        await db.close()
        return ResponseCode.SUCCESS, '查询成功', data
