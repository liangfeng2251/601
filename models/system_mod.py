# -*- coding: utf-8 -*-
# Created by HM on 2023-11-23


import requests

from utils.Rest import ResponseCode
from log import logger
from utils.db import settings


async def login(username, password):
    data = {'token': '', '_token': '', 'user_id': ''}

    try:
        req_data = {'username': username, 'password': password}
        res = requests.post(f'{settings.AUTH_PATH}/v1/ust/system/login', data=req_data)
        if res.status_code == 200:
            response = res.json()
            data['token'] = response['data']['token']
            data['_token'] = response['data']['_token']
            data['user_id'] = response['data']['user_id']
            return ResponseCode.SUCCESS, '登录成功', data
        return ResponseCode.UNAUTHORIZED, '用户名或密码错误', data
    except Exception as e:
        logger.error(e)
        return ResponseCode.UNAUTHORIZED, '用户名或密码错误', data
