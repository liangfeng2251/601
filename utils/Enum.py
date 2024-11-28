# -*- coding: utf-8 -*-
# Created by HM on 2023-07-08


from enum import Enum


class FileType(Enum):
    # 单文件
    FILE = 1
    # 文件夹
    FOLDER = 2


class RoleType(Enum):
    # 管理员
    ADMIN = 1
    # 普通员工
    STAFF = 2


class PermissionType(Enum):
    # 使用
    READ = 1
    # 编辑
    WRITE = 2
    # 管理
    EXECUTE = 4


class SceneStatusType(Enum):
    INIT = 1
    SUCCESS = 2
    PENDING = 3
    PARSING = 4
    FAIL = 5


class TaskStatus(Enum):
    PENDING = 0
    PARSING = 1
    UNPARSED = -1
    FINISH = 2
    ERROR = 4


class FileTypes(str, Enum):
    pdf_page = "pdf_page"
    pdf_image = "pdf_image"
    json = "json"
    md = "md"
    docx = "docx"
