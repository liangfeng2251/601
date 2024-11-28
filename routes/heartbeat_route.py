# -*- coding: utf-8 -*-
# Created by HM on 2023-11-23


from fastapi import APIRouter, Response

from utils.Rest import *

router = APIRouter(prefix='/heartbeat', tags=['heartbeat'])


class HeartbeatCurrent:
    @staticmethod
    @router.get('/current', responses=ResponseModel, summary='当前服务的心跳检测')
    async def get(response: Response):
        """
        当前服务的心跳检测:
        /v1/dgp/heartbeat/current, GET方法提交

        返回：
        - 如果提交成功，则返回200
        - 如果提交失败，则返回500 *****
        """
        resp = DResponse()
        response.status_code = ResponseCode.SUCCESS
        return resp
