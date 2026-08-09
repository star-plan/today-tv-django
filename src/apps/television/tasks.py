from celery import shared_task
from apps.television.crawls.swatow_tv import TodayTVCrawler


@shared_task(name='television.sync_today_tv')
def sync_today_tv(pages: int = 3) -> dict:
    """供 Celery Beat 调度的增量同步入口，返回摘要以便后台观察任务结果。"""
    return TodayTVCrawler().sync(pages=pages)
