# -*- coding: utf-8 -*-
# Created by HM on 2023-11-23


from fastapi import Query, Form, APIRouter, Response, File, UploadFile, Body
from fastapi.responses import FileResponse

from utils.Rest import *
from models.files_mod import *


router = APIRouter(prefix='/files', tags=['files'])


class RawFiles:
    @staticmethod
    @router.post('', responses=ResponseModel, summary='上传文件')
    async def upload_file(
            uf: dict = Depends(login_required),
            file: UploadFile = File(..., description='文件'),
            folder_id: str = Form(..., description='文件夹ID'),
            labels: str = Form(None, description='标签'),
            source: str = Form(None, description='来源'),
            response: Response = Response()
    ):
        """
        上传文件:
        /v1/mss/files, POST方法提交
        - **file**: 文件
        - **folder_id**: 文件夹ID
        - **labels**: 标签（标签1,标签2,...,...）
        - **source**: 来源，默认本地上传

        返回：
        - 如果上传成功，则返回文件信息
        - 如果上传失败，则返回500 *****
        """
        user_id = uf['user_id']

        res = await upload(file, folder_id, labels, source, user_id)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp

    @staticmethod
    @router.delete('', responses=ResponseModel, summary='删除文件')
    async def delete_file(
            uf: dict = Depends(login_required),
            file_ids: list = Body(..., description='文件ID列表'),
            response: Response = Response()
    ):
        """
        删除文件:
        /v1/mss/files, DELETE方法提交
        - **file_ids**: 文件ID列表

        返回：
        - 如果删除成功，则返回文件信息
        - 如果部分删除失败，则返回删除成功的文件信息 *****
        """
        user_id = uf['user_id']

        res = await delete_file(file_ids, user_id)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp

    @staticmethod
    @router.put('', responses=ResponseModel, summary='修改文件')
    async def update_file(
            uf: dict = Depends(login_required),
            file_id: str = Query(..., description='文件ID'),
            labels: str = Query(..., description='标签'),
            response: Response = Response()
    ):
        """
        修改文件:
        /v1/mss/files, PUT方法提交
        - **file_id**: 文件ID
        - **labels**: 标签（标签1,标签2,标签3,...,...）

        返回：
        - 如果修改成功，则返回文件信息
        - 如果修改失败，则返回500 *****
        """
        user_id = uf['user_id']

        res = await update_file(file_id, labels, user_id)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp

    @staticmethod
    @router.get('', responses=ResponseModel, summary='查询文件')
    async def get_files(
            uf: dict = Depends(login_required),
            folder_id: str = Query(..., description='文件夹ID'),
            file_name: str = Query('', description='文件名'),
            time_sort: str = Query('desc', description='倒序：desc，正序：asc'),
            page: int = Query(0, description='页'),
            page_size: int = Query(20, description='页容量'),
            response: Response = Response()
    ):
        """查询文件:
        /v1/mss/files, GET方法提交
        - **folder_id**: 文件夹ID
        - **file_id**: 文件ID
        - **file_name**: 文件名
        - **time_sort**: 倒序：desc，正序：asc
        - **page**: 页
        - **page_size**: 页容量

        返回：
        - 如果查询成功，则返回文件信息
        - 如果查询失败，则返回500 *****
        """
        user_id = uf['user_id']

        page: int = int(page) if str(page).isdigit() else 0
        page_size: int = int(page_size) if str(page_size).isdigit() else 20
        page: int = page * page_size

        res = await files(folder_id, file_name, time_sort, page, page_size, user_id)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp

    @staticmethod
    @router.get('/download', responses=ResponseModel, summary='下载文件')
    async def download(
            uf: dict = Depends(login_required),
            file_id: str = Query(..., description='文件ID'),
            file_path: str = Query(..., description='文件路径'),
            response: Response = Response()
    ):
        """
        下载文件:
        /v1/mss/files/download, GET方法提交
        - **file_id**: 文件ID
        - **file_path**: 文件路径

        返回：
        - 如果下载成功，则返回200
        - 如果下载失败，则返回500 *****
        """

        user_id = uf['user_id']
        code, msg, data = await download(file_id, file_path, user_id)
        if code == ResponseCode.SUCCESS:
            local_file_path, file_name = data.values()
            return FileResponse(local_file_path, content_disposition_type='attachment', filename=file_name)

        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp
