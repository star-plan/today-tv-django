"""提供给 Windows 任务计划程序和运维人员的今日视线手动同步命令。"""

import json

from django.core.management.base import BaseCommand, CommandError

from apps.television.crawls.swatow_tv import TodayTVCrawler


class Command(BaseCommand):
    help = '采集今日视线节目元数据，并更新本地节目库。'

    def add_arguments(self, parser):
        parser.add_argument('--pages', type=int, default=3, help='要扫描的最新列表页数，默认 3 页。')
        parser.add_argument('--dry-run', action='store_true', help='仅展示解析结果，不写入数据库。')

    def handle(self, *args, **options):
        pages = options['pages']
        if not 1 <= pages <= 20:
            raise CommandError('--pages 必须在 1 到 20 之间。')

        crawler = TodayTVCrawler()
        if options['dry_run']:
            # 演练模式用于源站改版后的人工验收，输出可直接保存为排障记录。
            videos = [item.as_dict() for item in crawler.crawl(pages=pages)]
            self.stdout.write(json.dumps(videos, ensure_ascii=False, indent=2))
            return

        result = crawler.sync(pages=pages)
        self.stdout.write(self.style.SUCCESS(json.dumps(result, ensure_ascii=False)))
