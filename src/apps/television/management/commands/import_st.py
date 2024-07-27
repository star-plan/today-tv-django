#  Copyright (c) intmain 2020.

import os
import time
import json
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from apps.television.models import TvProgram, Video


class Command(BaseCommand):
    help = 'StudyBus: Update av library.'

    def handle(self, *args, **options):
        try:
            start_time = time.time()

            st_program = TvProgram.objects.get(name='今日视线')

            print(f'styles: {self.style}')

            video_list = []

            base_path = r'E:\Code\python\crawl\all_crawl\temp_crawls\crawl_swatow_tv\downloads'
            for file in os.listdir(base_path):
                file_path = os.path.join(base_path, file)
                self.stdout.write(f'loaded file: {file_path}')
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for item in data:
                    v = Video(
                        program=st_program,
                        name=item['title'],
                        time=datetime.strptime(item['date'], '%Y-%m-%d'),
                        origin_link=item['link'],
                        cover_link=item['cover_url'],
                        video_link=item['video_url'],
                    )
                    video_list.append(v)
                    self.stdout.write(f'导入视频：{v}')

            self.stdout.write(f'批量导入 {len(video_list)} 个视频')
            Video.objects.bulk_create(video_list, batch_size=100)

            end_time = time.time()
            took_time = end_time - start_time
        except Exception as e:
            raise CommandError(e)
        else:
            self.stdout.write(self.style.SUCCESS('import finished. Took {} seconds.'.format(took_time)))
