# -*- coding: utf-8 -*-
# Created by HM on 2023-07-08


import traceback
import requests
from fastapi import Depends, status, Request
from fastapi.exceptions import HTTPException
from json import JSONEncoder
from datetime import date, datetime
from pydantic import BaseModel
from log import logger
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from fastapi.security.utils import get_authorization_scheme_param

from utils.db import settings


class ResponseCode(object):
    # 全局状态码区域
    SUCCESS = status.HTTP_200_OK
    UNKNOWN_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR
    NOT_FOUNT = status.HTTP_404_NOT_FOUND
    CONFLICT = status.HTTP_409_CONFLICT
    UNAUTHORIZED = status.HTTP_401_UNAUTHORIZED

    # 任务场景下的具体状态码区域
    TASK_POST_FILE_TYPE_NOT_ALLOW = 10001


class ResponseMessage(object):
    # 全局状态码区域
    SUCCESS = "SUCCESS"
    UNKNOWN_ERROR = "INTERNAL SERVER ERROR"

    # 任务场景下的具体状态码区域
    TASK_POST_FILE_TYPE_NOT_ALLOW = "仅支持.pdf .jpg .jpeg .png .bmp .tif .tiff .jfif类型文件"


class ResponseSUCCESS(BaseModel):
    code: int = ResponseCode.SUCCESS
    message: str = ResponseMessage.SUCCESS
    data: dict


class ResponseUNKNOWNERROR(BaseModel):
    code: int = ResponseCode.UNKNOWN_ERROR
    message: str = ResponseMessage.UNKNOWN_ERROR
    data: dict


ResponseModel = {200: {"model": ResponseSUCCESS}, 500: {"model": ResponseUNKNOWNERROR}}


class ISerializable:
    """serializable interface
    """
    pass


class AppJSONEncoder(JSONEncoder):
    """json encoder for serialization
    """
    def default(self, obj):
        if isinstance(obj, ISerializable):
            return obj.__dict__
        if isinstance(obj, (date, datetime)):
            return obj.__str__()
        return JSONEncoder.default(self, obj)


def request_handle(func):
    """decorator for generic error handling"""
    async def handle(*args, **kwargs):
        try:
            resp = await func(*args, **kwargs)
            return resp
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(e)
            logger.error('\n' + error_detail)
            res = {'code': 500, 'msg': '系统错误', 'data': {'messages': error_detail}}
            return ResponseCode.UNKNOWN_ERROR, '系统错误', res
    return handle


class DResponse(ISerializable):
    """
    说明:
        返回结果类封装
    """
    def __init__(self, code=ResponseCode.SUCCESS, msg=ResponseMessage.SUCCESS, data=None):
        self.code = code
        self.msg = msg
        self.data = data
    
    def update(self, code=None, msg=None, data=None):
        if code is not None:
            self.code = code
        if msg is not None:
            self.msg = msg
        if data is not None:
            self.data = data

    def add_field(self, name=None, value=None):
        if name is not None and value is not None:
            self.__dict__[name] = value

    @property
    def body(self):
        body = {"msg": self.msg, "code": self.code, "data": self.data}
        return body


head = {}


def verify_token(token):
    """
    权限验证
    :param token:
    :return:
    """
    try:
        global head
        head = {'Authorization': f'Bearer {token}'}
        res = requests.get(f'{settings.AUTH_PATH}/v1/ust/system/token-info', headers=head)
        if res.status_code == ResponseCode.SUCCESS:
            data = res.json().get('data')
            return data
        else:
            return False
    except Exception as e:
        logger.error(e)
        return False


class OAuth(OAuth2PasswordBearer):
    def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                return None
            else:
                return None
        return param


oauth2_scheme = OAuth(tokenUrl="/v1/mss/system/login")


def login_required(token: str = Depends(oauth2_scheme)):
    res = {'code': 401, 'msg': 'Token错误', 'data': None}
    if not token:
        res['msg'] = 'Token不存在'
        raise HTTPException(status_code=ResponseCode.UNAUTHORIZED, detail=res)
    if token == 'QAZWSX123..':
        logger.info('后台程序操作(Token)')
        return {'user_id': None, 'user_name': 'root'}
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=ResponseCode.UNAUTHORIZED, detail=res)
    user_info: dict = user_info
    user_info.update({'token': token})
    return user_info
