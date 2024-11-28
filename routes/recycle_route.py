# -*- coding: utf-8 -*-
# Created by HM on 2023-11-23


from fastapi import APIRouter, Response, Body

from utils.Rest import *
from models.recycle_mode import *


router = APIRouter(prefix='/recycle', tags=['recycle'])


class Recycle:
    @staticmethod
    @router.post('', responses=ResponseModel, summary='恢复')
    async def post(
            uf: dict = Depends(login_required),
            fids: list[str] = Body(..., title='回收站ID'),
            response: Response = Response()
    ):
        """
        恢复:
        /v1/mss/recycle, POST方法提交
        - **fids**: 文件ID

        返回：
        - 如果恢复成功，则返回文件信息
        - 如果恢复失败，则返回500 *****
        """
        user_id = uf['user_id']

        res = await recover_file(fids, user_id)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp

    @staticmethod
    @router.delete('', responses=ResponseModel, summary='彻底删除')
    async def delete(
            uf: dict = Depends(login_required),
            fids: list[str] = Body(..., title='回收站ID'),
            response: Response = Response()
    ):
        """
        彻底删除:
        /v1/mas/recycle, DELETE方法提交

        - **fids**: 文件ID

        返回：
        - 如果删除成功，则返回删除的文件信息
        - 如果删除失败，则返回500 *****
        """
        user_id = uf['user_id']

        res = await delete_file(fids, user_id)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp

    @staticmethod
    @router.delete('/clear_recycle', responses=ResponseModel, summary='清空回收站')
    async def clear_recycle(
            uf: dict = Depends(login_required),
            response: Response = Response()
    ):
        """
        清空回收站:
        /v1/mss/recycle/clear_recycle, DELETE方法提交

        返回：
        - 如果清空成功，则返回成功信息
        - 如果清空失败，则返回500 *****
        """
        user_id = uf['user_id']

        res = await clear_recycle(user_id)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp

    @staticmethod
    @router.get('', responses=ResponseModel, summary='获取目录')
    async def get(
            uf: dict = Depends(login_required),
            response: Response = Response()
    ):
        """
        获取目录:
        /v1/mss/recycle, GET方法提交
        返回：
        - 如果查询成功，则返回该用户下回收站所有文件
        - 如果查询失败，则返回500 *****
        """
        user_id = uf['user_id']

        res = await get_folder(user_id)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp
