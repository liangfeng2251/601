#!/usr/bin/env bash

#cd /data/deploy/file_engine || exit 1

# 更新 minio
flask init-minio || exit 1

# 如果存在 alembic_version，删除 alembic_version 表
flask rm-alembic-table || exit 1

flask db stamp head || exit 1

# 创建迁移脚本
flask db migrate

# 执行变更
flask db upgrade || exit 1

# 数据初始化
flask init-db || exit 1

# 创建RSA密钥
flask init-rsa-keys || exit 1

# 修复 airflow 数据字段
#flask airflow-db || exit 1
#alembic init alembic
#alembic revision --autogenerate -m "1.0.0"
