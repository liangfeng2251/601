# -*- coding: utf-8 -*-
# Created by HM on 2023-11-23


from fastapi import APIRouter, Response

from utils.Rest import *
from models.monitor_mod import *


router = APIRouter(prefix='/monitor', tags=['monitor'])


class Monitor:
    @staticmethod
    @router.get('', responses=ResponseModel, summary='监控页')
    async def get(
            uf: dict = Depends(login_required),
            response: Response = Response()
    ):
        """
        获取目录:
        /v1/mss/monitor, GET方法提交
        返回：
        - 如果查询成功，则返回监控数据
        - 如果查询失败，则返回500 *****
        """

        user_name = uf['user_name']
        if user_name == 'root':
            res = await admin_ms(uf)
        else:
            res = await ms(uf)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        return resp
