#  Copyright (c) intmain 2020.

import os
import time
import json
from datetime import datetime
from math import copysign

from django.core.management.base import BaseCommand, CommandError
from apps.television.models import TvProgram, Video
from django_q.tasks import async_task, Task
from apps.television.tasks import swatow_tv


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
            task_id = async_task(
                swatow_tv.get_updated_date,
                task_name='获取最新视频更新日期',
                hook=task_finish,
            )
            self.stdout.write(f'task_id: {task_id}')

        except Exception as e:
            raise CommandError(e)
        else:
            self.stdout.write(self.style.SUCCESS('task finished'))
