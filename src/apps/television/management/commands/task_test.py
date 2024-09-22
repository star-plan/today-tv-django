#  Copyright (c) intmain 2020.

import os
import time
import json
import random
from datetime import datetime, date
from math import copysign

from django.core.management.base import BaseCommand, CommandError
from apps.television.models import TvProgram, Video
from django_q.tasks import async_task, Task, AsyncTask
from apps.television.tasks_bak import swatow_tv


def task_test():
    r = random.randint(1, 100)
    print(f'generate random number: {r}')
    return r


def task_finish(task: Task):
    print(f'任务 {task.name}（ID：{task.id}）完成！')


class Command(BaseCommand):
    help = 'TodayTV: A test task'

    def handle(self, *args, **options):
        try:
            # task_id = async_task(
            #     swatow_tv.init_cfg,
            #     task_name='初始化配置',
            #     hook=task_finish,
            # )
            # task_id = async_task(
            #     swatow_tv.get_updated_date,
            #     task_name='获取最新视频更新日期',
            #     hook=task_finish,
            # )
            # task_id = async_task(
            #     swatow_tv.get_videos,
            #     date(2024, 7, 29),
            #     task_name='获取指定日期的视频',
            #     hook=task_finish,
            # )
            task_id = async_task(
                task_test,
                task_name='测试任务-生成随机数',
                hook=task_finish,
            )
            self.stdout.write(f'task_id: {task_id}')

        except Exception as e:
            raise CommandError(e)
        else:
            self.stdout.write(self.style.SUCCESS('task finished'))
