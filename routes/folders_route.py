# -*- coding: utf-8 -*-
# Created by HM on 2023-11-23


from fastapi import Query, Form, APIRouter, Response

from utils.Rest import *
from models.folders_mode import *


raw_file_router = APIRouter(prefix='/raw_file_folders', tags=['raw_file_folders'])


class RawFileFolders:
    @staticmethod
    @raw_file_router.post('', responses=ResponseModel, summary='创建文件夹')
    async def post(
            uf: dict = Depends(login_required),
            parent_id: str = Form(None, title='父级ID，为空则在根节点下创建'),
            folder_name: str = Form(..., title='文件夹名'),
            response: Response = Response()
    ):
        """
        新建文件夹:
        /v1/mas/raw_file_folders, POST方法提交
        - **parent_id**: 父级ID
        - **folder_name**: 文件夹名称

        返回：
        - 如果创建成功，则返回文件夹信息
        - 如果创建失败，则返回500 *****
        """
        user_id = uf['user_id']

        res = await add_folder(folder_name, parent_id, user_id)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp

    @staticmethod
    @raw_file_router.delete('', responses=ResponseModel, summary='删除文件夹')
    async def delete(
            uf: dict = Depends(login_required),
            folder_id: str = Query(..., title='文件夹ID'),
            response: Response = Response()
    ):
        """
        删除文件夹:
        /v1/mas/raw_file_folders, DELETE方法提交

        - **folder_id**: 文件夹ID

        返回：
        - 如果删除成功，则返回删除的文件夹信息
        - 如果删除失败，则返回500 *****
        """
        user_id = uf['user_id']

        res = await delete_folder(folder_id, user_id)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp

    @staticmethod
    @raw_file_router.put('', responses=ResponseModel, summary='重命名文件夹')
    async def update(
            uf: dict = Depends(login_required),
            folder_id: str = Form(..., title='文件夹ID'),
            folder_name: str = Form(..., title='文件夹名'),
            response: Response = Response()
    ):
        """
        重命名文件夹:
        /v1/mas/raw_file_folders, PUT方法提交

        - **folder_id**: 文件夹ID
        - **folder_name**: 文件夹名

        返回：
        - 如果修改成功，则返回修改过的文件夹信息
        - 如果删除失败，则返回500 *****
        """
        user_id = uf['user_id']

        res = await rename_folder(folder_id, folder_name, user_id)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp

    @staticmethod
    @raw_file_router.get('', responses=ResponseModel, summary='获取目录')
    async def get_folder(
            uf: dict = Depends(login_required),
            response: Response = Response()
    ):
        """
        获取目录:
        /v1/mas/raw_file_folders, GET方法提交
        返回：
        - 如果查询成功，则返回该用户下所有文件夹
        - 如果查询失败，则返回500 *****
        """
        user_id = uf['user_id']

        res = await get_folder(user_id)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp
