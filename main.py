# -*- coding: utf-8 -*-
# Created by HM on 2023-07-08


import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from fastapi.staticfiles import StaticFiles


from routes import heartbeat_route, system_route, monitor_route, folders_route, files_route, recycle_route
from utils.scheduled_operator import remove_old_file, daily_tatistics
from conf.setting_env import SettingDev, SettingProd
from log import logger


openapi_tags = [
    {'name': 'heartbeat', 'description': '心跳检测'},
    {'name': 'system', 'description': '系统接口'},
    {'name': 'monitor', 'description': '监控页'},
    {'name': 'raw_file_folders', 'description': '文件夹管理'},
    {'name': 'files', 'description': '文件管理'},
    {'name': 'recycle', 'description': '回收站'},
]

# 创建FastAPI以及Swagger UI
root_app = FastAPI()
app = FastAPI(openapi_tags=openapi_tags)
root_app.mount('/v1/mss', app)
root_app.mount('/static', StaticFiles(directory='static'), name='static')

# prod为生产环境、dev为开发环境
APP_ENV = os.getenv('APP_ENV')

# 接受跨域
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=['*'],  # 允许所有域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == 422:
        resp = JSONResponse(content={"msg": "参数类型错误", "code": 422, "data": None})
        resp.status_code = 422
        return resp
    return response


@root_app.on_event("startup")
async def app_start():
    scheduler = AsyncIOScheduler()
    scheduler.add_executor(AsyncIOExecutor())

    await remove_old_file()
    await daily_tatistics()

    scheduler.add_job(func=remove_old_file, trigger='cron', hour=0, id='remove_old_file')
    scheduler.add_job(func=daily_tatistics, trigger='cron', minute=10, id='daily_tatistics')
    scheduler.start()


def make_setting():
    config = {
        'dev': SettingDev(),
        'prod': SettingProd(),
    }
    env_value = os.environ.get('APP_ENV')

    _settings = config[env_value]

    # 检查数据库是否存在，如果不存在则创建
    _engine = create_engine(_settings.SQLALCHEMY_DATABASE_URI_TEST)
    _Session = sessionmaker(bind=_engine)
    session = _Session()
    try:
        session.execute(text(f"USE {_settings.DB_DATABASE}"))
    except Exception as e:
        logger.error(e)
        session.execute(
            text(f"CREATE DATABASE {_settings.DB_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
        )

    logger.info(f'当前环境值 {_settings.ENVNAME}')
    return _settings, session


_st = make_setting()[0]

app.include_router(heartbeat_route.router)
app.include_router(system_route.router)
app.include_router(monitor_route.router)
app.include_router(folders_route.raw_file_router)
app.include_router(files_route.router)
app.include_router(recycle_route.router)


if __name__ == '__main__':
    os.system('python migrate.py init')
    import uvicorn
    uvicorn.run('main:root_app', port=_st.PORT, host=_st.HOST, reload=False)
