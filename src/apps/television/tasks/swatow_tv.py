from datetime import date
from django.utils import timezone
from loguru import logger

from django_starter.contrib.config import services as cfg
from apps.television.crawls import swatow_tv as spider
from apps.television.models import TvProgram, Video


def init_cfg():
    cfg.set_bool('use_proxy', False, '爬虫使用代理')
    cfg.set_str('proxy_url', '', '代理URL')
    cfg.set_bool('use_proxy_pool', False, '使用代理池')
    cfg.set_str('proxy_pool_api_base', '')
    cfg.set_json('headers', spider.default_headers)


def get_updated_date():
    p = TvProgram.objects.get(name='今日视线')
    p.status = TvProgram.Status.SCRAPING
    p.save()
    d = spider.get_updated_date()
    if d:
        p.first_detected_update_time = d
        p.status = TvProgram.Status.UPDATED
    else:
        p.status = TvProgram.Status.FAILED
    p.last_synced_time = timezone.now()
    p.save()
    return d


def get_videos(assign_date: date):
    program = TvProgram.objects.get(name='今日视线')
    local_videos = Video.objects.filter(
        time__date=assign_date,
    )
    fragments = spider.get_fragments(assign_date)

    videos_to_insert = []

    for fragment in fragments:
        if local_videos.filter(name=fragment.title).exists():
            logger.debug(f'{fragment.title} already exists')
            continue
        videos_to_insert.append(Video(
            program=program,
            name=fragment.title,
            time=assign_date,
            origin_link=fragment.link,
            cover_link=fragment.cover_url,
            video_link=fragment.video_url,
        ))

    logger.info(f'inserting {len(videos_to_insert)} videos')
    Video.objects.bulk_create(videos_to_insert)
