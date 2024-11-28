# -*- coding: utf-8 -*-
# Created by HM on 2023-07-08


import requests
from sqlalchemy.sql import select, extract, desc, func, false
from typing import Any

from utils.db import async_session, settings
from utils.Rest import ResponseCode, request_handle
from utils.SQLModels import DailyNums, Files
from log import logger


@request_handle
async def admin_ms(user_info):
    """管理员监控"""
    token = user_info['token']

    try:
        session = requests.Session()
        minio_url = str(settings.MINIO_ENDPOINT).split(':')[0] + ':' + settings.MINIO_CONSOLE_PORT
        url = f'http://{minio_url}/api/v1/login'
        res = session.post(url, json={"accessKey": settings.MINIO_ACCESS_KEY, "secretKey": settings.MINIO_SECRET_KEY})
        session.cookies.update({'Cookie': res.headers.get('Set-Cookie')})
        url = f'http://{minio_url}/api/v1/admin/info'
        res = session.get(url).json()
        session.close()

        servers_status = {}
        for i in res['servers']:
            s = {
                "data_ratio": '%.2f' % (i['drives'][0]['usedSpace'] / i['drives'][0]['totalSpace']),
                "capacity": "%d GB" % (i['drives'][0]['totalSpace'] / (1024 ** 3)),
                "userd_space": "%d GB" % (i['drives'][0]['usedSpace'] / (1024 ** 3)),
                "remaining_space": "%d GB" % (i['drives'][0]['availableSpace'] / (1024 ** 3)),
            }
            servers_status = s
            break

        one_week = {}
        async with async_session() as db:
            ct: Any = DailyNums.create_date
            sql = select(DailyNums.today_num, extract('month', ct), extract('day', ct)).order_by(desc(ct)).limit(7)
            res = (await db.execute(sql)).fetchall()
            res = res[::-1]
            one_week['date'] = ['-'.join([str(i[1]), str(i[2])]) for i in res]
            one_week['file_total'] = [i[0] for i in res]

            six_months = {}
            sql = select(extract('month', ct), func.count(ct)).group_by(extract('month', ct)).limit(7)
            res = (await db.execute(sql)).fetchall()
            six_months['date'] = [str(i[0]) + '月' for i in res]
            six_months['file_total'] = [i[1] for i in res]

        data = {
            'admin': True, "server_status": servers_status, "data_delta_chart": {
                'one_week': one_week, 'six_months': six_months
            }
        }

        session = requests.Session()
        ust_url = settings.AUTH_PATH
        head = {'Authorization': f'Bearer {token}'}
        res = session.get(ust_url + '/v1/ust/system/system-info', headers=head).json()
        user_system_info = res['data']
        data.update(user_system_info)
        session.close()

        return ResponseCode.SUCCESS, '查询成功', data
    except Exception as e:
        logger.error(e)
        logger.error('数据监控更新失败!')

    return ResponseCode.SUCCESS, '查询失败', None


@request_handle
async def ms(user_info):
    """普通用户监控页面"""
    user_id, user_name, token = user_info['user_id'], user_info['user_name'], user_info['token']
    role_user = {'1': '管理员', '2': '普通用户'}

    session = requests.Session()
    ust_url = settings.AUTH_PATH
    head = {'Authorization': f'Bearer {token}'}
    res = session.get(ust_url + f'/v1/ust/user/userinfo?user_id={user_id}', headers=head).json()
    user_info_all = res['data']
    group_name, role = user_info_all['group_name'], user_info_all['role']
    role = str(role)
    if role in role_user:
        role = role_user[role]
    else:
        role = ''
    session.close()

    async with async_session() as db:
        sql = select(func.count(Files.id)).filter(Files.user_id == user_id)
        res = (await db.execute(sql)).fetchone()
        total_nums = res[0]

        one_week = {}
        ct: Any = Files.create_time
        sql = select(Files.id, extract('month', ct), extract('day', ct)).filter(
            Files.user_id == user_id
        ).order_by(desc(ct)).limit(7)
        res = (await db.execute(sql)).fetchall()
        res = res[::-1]
        one_week['date'] = ['-'.join([str(i[1]), str(i[2])]) for i in res]
        one_week['file_total'] = [i[0] for i in res]

        six_months = {}
        sql = select(extract('month', ct), func.count(ct)).filter(
            Files.user_id == user_id
        ).group_by(extract('month', ct)).limit(7)
        res = (await db.execute(sql)).fetchall()
        six_months['date'] = [str(i[0]) + '月' for i in res]
        six_months['file_total'] = [i[1] for i in res]

        recent_files = []
        sql = select(Files.file_id, Files.file_name, Files.folder_id, Files.raw_file).filter(
            Files.user_id == user_id, Files.is_delete == false()
        )
        res = (await db.execute(sql)).fetchall()
        for i in res:
            file_id, file_name, folder_id, raw_file = i
            recent_files.append({
                'file_name': file_name, 'file_id': file_id, 'folder_id': folder_id, 'raw_file': raw_file
            })

        await db.close()

    data = {
        'admin': False,
        "user_info": {'user_name': user_name, 'department': group_name, 'role': role},
        "total_data": {
            'total_nums': total_nums,
            'unstructured': total_nums,
            'structuring': 0
        },
        "data_delta_chart": {'one_week': one_week, 'six_months': six_months},
        'recent_files': recent_files
    }

    return ResponseCode.SUCCESS, '查询成功', data
