# -*- coding: utf-8 -*-
# Created by HM on 2023-07-08


from fastapi import Form, APIRouter, Response

from utils.Rest import *
from models.system_mod import *


router = APIRouter(prefix='/system', tags=['system'])


class User:
    @staticmethod
    @router.post('/login', responses=ResponseModel, summary='用户登录')
    async def post(
            username: str = Form(..., description='用户名'),
            password: str = Form(..., description='密码'),
            response: Response = Response()
    ):
        """
        用户登录:
        /v1/mss/system/login, POST方法提交
        - **username**: 用户名
        - **password**: 密码

        返回：
        - 如果登录成功，则返回Token信息
        - 如果登录失败，则返回500 *****
        """
        res = await login(username, password)
        code, msg, data = res
        resp = DResponse(code=code, msg=msg, data=data)
        response.status_code = code
        data = {"access_token": resp.data['_token'], "token_type": "bearer"}
        data.update(resp.body)
        return data
