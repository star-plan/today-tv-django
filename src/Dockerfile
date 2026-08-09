# Django 5 需要 Python 3.10+；选择 3.11 与项目的运行时约束一致。
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /code

# 先单独复制依赖清单，使后续业务代码修改可以复用依赖层缓存。
COPY requirements.txt /code/requirements.txt
RUN pip install --upgrade pip && pip install -r /code/requirements.txt

COPY . /code
