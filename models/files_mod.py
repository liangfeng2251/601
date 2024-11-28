# -*- coding: utf-8 -*-
# Created by HM on 2023-11-23


import os
import zipfile
from uuid import uuid4
from datetime import datetime
from hashlib import md5
from sqlalchemy.sql import select, update, false, true, func

from utils.db import async_session, settings, minio_client
from utils.SQLModels import Files, Folders, Recycle
from log import logger
from utils.Rest import ResponseCode, request_handle


async def get_file(file_id, user_id):
    """获取文件信息"""

    async with async_session() as db:
        sql = select(
            Files.file_id, Files.file_name, Files.source, Files.raw_file,
            Files.update_time, Files.create_time
        ).filter(Files.file_id == file_id, Files.user_id == user_id)
        res = (await db.execute(sql)).fetchone()
        await db.close()

    if not res:
        return None

    file_id, file_name,  source, raw_file, create_time, update_time = res
    res = {
        "file_id": file_id,
        "file_name": file_name,
        "source": source,
        "create_time": str(create_time),
        "update_time": str(update_time),
        "raw_file": raw_file
    }
    return res


async def get_folder(folder_id, user_id):
    """获取文件夹"""
    async with async_session() as db:
        sql = select(Folders.folder_id, Folders.folder_name).filter(
            Folders.folder_id == folder_id, Folders.user_id == user_id, Folders.is_delete == false()
        )
        res = (await db.execute(sql)).fetchone()
        await db.close()

    if not res:
        return None

    folder_id, folder_name = res
    res = {'folder_name': folder_name, 'folder_id': folder_id}
    return res


async def get_file_path(file_name, current_path=None, folder=False):
    """生成本地文件路径"""
    if current_path:
        file_path = os.path.join(current_path, file_name)
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        return file_path
    save_files = os.path.join(os.path.dirname(__file__), 'save_files')
    if not os.path.exists(save_files):
        os.mkdir(save_files)
    local_path = os.path.join(save_files, datetime.now().date().__str__())
    if not os.path.exists(local_path):
        os.mkdir(local_path)
    file_path = os.path.join(local_path, file_name)
    if folder:
        if not os.path.exists(file_path):
            os.mkdir(file_path)
    return file_path


async def get_ocr_file_path(file_name, current_path=None, folder=False):
    """生成本地文件路径"""
    if current_path:
        file_path = os.path.join(current_path, file_name)
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        return file_path
    save_files = os.path.join(os.path.dirname(__file__), 'ocr')
    if not os.path.exists(save_files):
        os.mkdir(save_files)
    local_path = os.path.join(save_files, datetime.now().date().__str__())
    if not os.path.exists(local_path):
        os.mkdir(local_path)
    file_path = os.path.join(local_path, file_name)
    if folder:
        if not os.path.exists(file_path):
            os.mkdir(file_path)
    return file_path


async def get_zip_file_path(file_name):
    """生成压缩包路径"""
    save_files = os.path.join(os.path.dirname(__file__), 'save_files')
    if not os.path.exists(save_files):
        os.mkdir(save_files)
    local_path = os.path.join(save_files, datetime.now().date().__str__())
    if not os.path.exists(local_path):
        os.mkdir(local_path)
    zip_extract_path = os.path.join(local_path, os.path.splitext(file_name)[0])
    if not os.path.exists(zip_extract_path):
        os.mkdir(zip_extract_path)
    file_path = os.path.join(local_path, file_name)
    return file_path, zip_extract_path


async def upload_minio(local_path, file_id, file_name):
    """本地文件上传Minio"""
    today = datetime.now().date().__str__().replace('-', '/')
    minio_path = f'{today}/{file_id}/{file_name}'
    with open(local_path, "rb") as file_data:
        minio_client.put_object(settings.MINIO_BUCKET_NAME, minio_path, file_data, length=os.stat(local_path).st_size)
    return minio_path


@request_handle
async def upload(file, folder_id, labels, source, user_id):
    """上传文件"""
    upload_files = []
    file_name = file.filename
    file_type = os.path.splitext(file_name)[1].lower()

    if not source:
        source = '本地上传'
    elif file_type == '.zip' and source != '数据自产生系统':
        return ResponseCode.CONFLICT, 'zip格式还需优化', None

    folder_info = await get_folder(folder_id, user_id)
    if not folder_info:
        return ResponseCode.CONFLICT, '无目录信息', None

    if file_type == '.zip' and source != '数据自产生系统':
        res = await upload_minio_zip(file, folder_id, user_id)
        res_status, res_value = res
        if not res_status:
            return res_value
        else:
            file_lists = res_value
    else:
        file_lists = [{'file': file, 'folder_id': folder_id}]

    for i in file_lists:
        if 'file_name' in i:
            file_name, file_path, folder_id = i['file_name'], i['file_path'], i['folder_id']
            file_id = md5(str(file_name + uuid4().__str__()).encode('utf8')).hexdigest()
        else:
            file, folder_id = i['file'], i['folder_id']
            file_id = md5(str(file_name + uuid4().__str__()).encode('utf8')).hexdigest()
            file_path = await get_file_path(file_name)
            with open(file_path, 'wb') as f:
                f.write(file.file.read())
                f.close()

        minio_path = await upload_minio(file_path, file_id, file_name)

        async with async_session() as db:
            file_new = Files(
                folder_id=folder_id, file_id=file_id, file_name=file_name,
                raw_file=minio_path, user_id=user_id, labels=labels, source=source
            )
            db.add(file_new)
            await db.commit()
            await db.close()
        logger.info(f'{file_name} 已创建')
        file_res = await get_file(file_id, user_id)
        if file_res:
            upload_files.append(file_res)

    return ResponseCode.SUCCESS, '上传完成', upload_files


async def upload_minio_zip(file, folder_id, user_id):
    """上传压缩文件"""
    upload_files = []
    folders = {}
    temp_files = []
    folder_ids = {}
    upload_folder_files = []
    file_paths = []
    first_level_folder_id = ''

    file_name = file.filename
    file_path, zip_extract_path = await get_zip_file_path(file_name)
    with open(file_path, 'wb') as f:
        f.write(file.file.read())
        f.close()
    with zipfile.ZipFile(file_path, 'r') as zip_file:
        for file in zip_file.infolist():
            if '__MACOSX' in file.filename:
                continue
            file.filename = file.filename.encode('cp437').decode('gbk')
            zip_file.extract(file, path=zip_extract_path)
            file_paths.append(os.path.join(zip_extract_path, file.filename))

    if len(file_paths) == 1:
        file_name = file_paths[0]
        file_type = os.path.splitext(file_name)[1]
        if file_type not in settings.ALLOWED_FILE_TYPE_LIST:
            return False, (ResponseCode.CONFLICT, '文件类型不支持', {})
        return True, [{'file': file, 'folder_id': folder_id}]
    else:
        for i in file_paths:
            if i[-1] == '/':
                _fps = md5(i[:-1].encode()).hexdigest()
                if len(_fps.split('/')) == 1:
                    first_level_folder_id = uuid4().__str__()
                    folders[_fps] = {'parent_id': None, 'uuid': first_level_folder_id, 'file_path': i[:-1]}
                elif len(_fps.split('/')) > 10:
                    continue
                else:
                    parent_id = md5(_fps[:_fps.rfind('/')].encode()).hexdigest()
                    folders[_fps] = {
                        'parent_id': parent_id, 'uuid': uuid4().__str__(), 'file_path': _fps[:_fps.rfind('/')]
                    }
            else:
                file_type = os.path.splitext(i)[1]
                if file_type not in settings.ALLOWED_FILE_TYPE_LIST:
                    continue
                if len(i.split('/')) == 1:
                    upload_files.append({'folder_id': None, 'file_path': i})
                elif len(i.split('/')) > 10:
                    temp_files.append({'folder_id': None, 'file_path': i})
                else:
                    folder = md5(i[:i.rfind('/')].encode()).hexdigest()
                    upload_files.append({'folder_id': folder, 'file_path': i})

    for k, v in folders.items():
        tmp_k = v['file_path'].replace('\\', '/')
        folder_ids[v['uuid']] = {
            'folder_name': tmp_k.split('/')[-1],
            'parent_id': folders[v['parent_id']]['uuid'] if v['parent_id'] else None
        }
    for i in upload_files:
        upload_folder_files.append(
            {
                'folder_id': folders[i['folder_id']]['uuid'] if i['folder_id'] else None,
                'file_path': i['file_path'],
                'file_name': os.path.basename(i['file_path'])
            }
        )

    if temp_files:
        other_folder_id = uuid4().__str__()
        folder_ids[other_folder_id] = {'folder_name': 'other', 'parent_id': first_level_folder_id}
        for i in temp_files:
            file_name = os.path.basename(i['file_path'])
            upload_folder_files.append(
                {'folder_id': other_folder_id, 'file_path': i['file_path'], 'file_name': file_name}
            )

    folder_new_ids = {}
    for k, v in folder_ids.items():
        folder_name, parent_id = v['folder_name'], v['parent_id']
        if not parent_id:
            parent_id = folder_id
        add_folder_res = await add_folder(folder_name, k, parent_id, user_id)
        af_status, _folder = add_folder_res
        if af_status:
            folder_new_ids[k] = {'folder_name': folder_name, 'parent_id': parent_id, 'folder_id': _folder['folder_id']}
        else:
            folder_new_ids[k] = {'folder_name': folder_name, 'parent_id': parent_id, 'folder_id': k}

    for i in upload_folder_files:
        folder_id = folder_new_ids[i['folder_id']]['folder_id']
        i['folder_id'] = folder_id
    return True, upload_folder_files


async def add_folder(folder_name, folder_id, parent_id, user_id):
    """新建文件夹"""
    async with async_session() as db:
        sql = select(Folders.folder_id).filter(
            Folders.folder_name == folder_name, Folders.is_delete == false(), Folders.parent_id == parent_id
        )
        res = (await db.execute(sql)).fetchone()
        if res:
            return True, {'folder_id': res[0]}

        if parent_id:
            sql = select(Folders.folder_id).filter(Folders.folder_id == parent_id)
            res = (await db.execute(sql)).fetchone()
            if not res:
                return False, {}

        folder = Folders(folder_id=folder_id, parent_id=parent_id, folder_name=folder_name, user_id=user_id)
        db.add(folder)
        await db.commit()
        await db.close()
        res = {'folder_id': folder_id, 'folder_name': folder_name}
        return True, res


@request_handle
async def delete_file(file_ids, user_id):
    """删除文件"""
    data = []
    msg = '删除成功'

    async with async_session() as db:
        for i in file_ids:
            sql = update(Files).filter(
                Files.file_id == i, Files.user_id == user_id, Files.is_delete == false()
            ).values(is_delete=true(), update_time=datetime.now())
            res = (await db.execute(sql)).rowcount
            await db.commit()

            if not res:
                data.append({'file_id': i, 'status': 'ERROR'})
                msg = '部分删除失败'
                continue

            file_info = await get_file(i, user_id)
            file_name = file_info['file_name']
            recycle_file = Recycle(file_id=i, file_name=file_name, user_id=user_id)
            db.add(recycle_file)
            await db.commit()
            data.append({'file_id': i, 'status': 'SUCCESS'})
        await db.close()
    return ResponseCode.SUCCESS, msg, data


@request_handle
async def update_file(file_id, labels, user_id):
    async with async_session() as db:
        sql = update(Files).filter(
            Files.file_id == file_id, Files.is_delete == false(), Files.user_id == user_id
        ).values(labels=labels)
        res = (await db.execute(sql)).rowcount
        await db.commit()
        await db.close()

    if not res:
        return ResponseCode.CONFLICT, '修改失败', None
    return ResponseCode.SUCCESS, '修改成功', None


@request_handle
async def files(folder_id, file_name, time_sort, page, page_size, user_id):
    """查询文件夹下文件"""
    data = []

    folder_info = await get_folder(folder_id, user_id)

    if not folder_info:
        return ResponseCode.CONFLICT, '文件夹错误', []
    folder_name = folder_info['folder_name']

    async with async_session() as db:
        sql = select(
            Files.file_id, Files.file_name, Files.create_time, Files.source, Files.raw_file,
            Files.labels
        ).filter(
            Files.folder_id == folder_id, Files.file_name.like(f'%{file_name}%'),
            Files.user_id == user_id, Files.is_delete == false()
        )
        if time_sort == 'desc':
            sql = sql.order_by(Files.create_time.desc()).offset(page).limit(page_size)
        else:
            sql = sql.order_by(Files.create_time.asc()).offset(page).limit(page_size)
        res = (await db.execute(sql)).fetchall()

        for i in res:
            file_id, filename, create_time, source, raw_file, labels = i
            res = {
                "file_id": file_id,
                "file_name": filename,
                "source": source,
                "labels": labels.split(',') if labels else [],
                "folder_name": folder_name,
                "create_time": str(create_time),
                "raw_file": raw_file
            }
            data.append(res)

        sql = select(func.count(Files.id)).filter(
            Files.folder_id == folder_id, Files.file_name.like(f'%{file_name}%'),
            Files.user_id == user_id, Files.is_delete == false()
        )
        count = (await db.execute(sql)).scalar()

    response = {'offset': page, 'limit': page_size, 'total_nums': count, 'list': data}
    return ResponseCode.SUCCESS, '查询成功', response


@request_handle
async def download(file_id, file_path, user_id):
    """下载文件"""
    file_name = os.path.basename(file_path)
    local_file_path = await get_ocr_file_path(file_name)

    async with async_session() as db:
        sql = select(Files.id).filter(
            Files.file_id == file_id, Files.user_id == user_id, Files.is_delete == false()
        )
        res = (await db.execute(sql)).fetchone()
        await db.close()
        if not res:
            return ResponseCode.CONFLICT, '文件信息错误', None

    try:
        minio_client.fget_object(settings.MINIO_BUCKET_NAME, file_path, local_file_path)
    except Exception as e:
        logger.error(e)
        return ResponseCode.NOT_FOUNT, '无可用文件', {}
    return ResponseCode.SUCCESS, '下载成功', {'local_file_path': local_file_path, 'file_name': file_name}
