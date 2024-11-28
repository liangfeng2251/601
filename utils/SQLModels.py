# -*- coding: utf-8 -*-
# Created by HM on 2023-07-08


from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Date

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Folders(Base):
    __tablename__ = 'folders'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    folder_id = Column(String(225), nullable=False, primary_key=True, comment='文件夹ID')
    parent_id = Column(String(225), comment='父级ID')
    folder_name = Column(String(255), comment='文件夹名称')
    user_id = Column(String(255), nullable=False, comment='用户ID')
    folder_type = Column(Integer, default=False, comment='文件夹类型，必要：1，非必要：0')
    create_time = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    is_delete = Column(Integer, default=False, nullable=False, comment='删除：1')

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci'
    }


class Files(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    folder_id = Column(String(225), comment='文件夹ID')
    file_id = Column(String(255), nullable=False, comment='文件唯一id', primary_key=True)
    file_name = Column(String(255), nullable=False, comment='文件名')
    labels = Column(String(255), comment='标签')
    source = Column(String(255), comment='来源')
    raw_file = Column(String(255), nullable=False, comment='数据下载地址')
    user_id = Column(String(255), nullable=False, comment='用户ID')
    create_time = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, nullable=False, comment='更新时间')
    is_delete = Column(Boolean, default=False, nullable=False, comment='删除：1')

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci'
    }


class Recycle(Base):
    __tablename__ = 'recycle'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    file_id = Column(String(255), comment='文件ID')
    file_name = Column(String(255), comment='文件名')
    file_path = Column(String(255), comment='原始路径')
    user_id = Column(String(255), nullable=False, comment='用户ID')
    create_time = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    is_delete = Column(Boolean, default=False, nullable=False, comment='删除：1')

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci'
    }


class DailyNums(Base):
    __tablename__ = 'daily_nums'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    today_num = Column(Integer, comment='今日数据量')
    create_date = Column(Date, default=datetime.today(), comment='创建时间')

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci'
    }
