"""面向网页和移动客户端的只读公共节目 API。"""

from datetime import date, datetime
from typing import Optional

from django.db.models import Count, Max
from django.shortcuts import get_object_or_404
from django.urls import reverse
from ninja import Router, Schema

from apps.television.models import TvProgram, Video


router = Router(tags=['今日视线'])


class ProgramOut(Schema):
    """节目概览，适合客户端首页和设置页展示。"""

    id: int
    name: str
    source_url: Optional[str]
    status: str
    last_synced_at: Optional[datetime]
    latest_published_at: Optional[datetime]
    episode_count: int


class EpisodeOut(Schema):
    """客户端播放一条节目所需的完整、稳定字段集合。"""

    id: int
    title: str
    published_at: Optional[datetime]
    cover_url: Optional[str]
    playback_url: Optional[str]
    source_url: Optional[str]
    webpage_url: str


class EpisodeListOut(Schema):
    """偏移量分页结果，便于非 Python 客户端直接增量加载。"""

    count: int
    limit: int
    offset: int
    items: list[EpisodeOut]


def serialize_episode(request, item: Video) -> dict:
    """将数据库记录转换为公共契约，始终附带项目内播放页地址。"""
    playback_url = item.video.url if item.video else item.video_link
    return {
        'id': item.id,
        'title': item.name,
        'published_at': item.time,
        'cover_url': item.cover.url if item.cover else item.cover_link,
        'playback_url': playback_url,
        'source_url': item.related_link,
        'webpage_url': request.build_absolute_uri(
            reverse('television:video', kwargs={'pk': item.id}),
        ),
    }


@router.get('/program', response=Optional[ProgramOut], summary='获取今日视线节目概览')
def program(request):
    """返回当前节目库存和同步状态；未首次同步时返回 null 而非错误。"""
    item = TvProgram.objects.filter(name='今日视线').annotate(
        episode_count=Count('videos'),
        latest_published_at=Max('videos__time'),
    ).first()
    if not item:
        return None
    return {
        'id': item.id,
        'name': item.name,
        'source_url': item.source_url,
        'status': item.status,
        'last_synced_at': item.last_synced_time,
        'latest_published_at': item.latest_published_at,
        'episode_count': item.episode_count,
    }


@router.get('/episodes', response=EpisodeListOut, summary='分页获取可播放的节目片段')
def episodes(
    request,
    publish_date: Optional[date] = None,
    limit: int = 24,
    offset: int = 0,
):
    """按发布时间倒序返回节目，publish_date 使用 YYYY-MM-DD 格式筛选。"""
    # 显式限制分页参数，既保护数据库，也保证客户端拿到可预期的数据量。
    limit = min(max(limit, 1), 100)
    offset = max(offset, 0)
    query = Video.objects.select_related('program').order_by('-time', '-id')
    if publish_date:
        query = query.filter(time__date=publish_date)
    total = query.count()
    return {
        'count': total,
        'limit': limit,
        'offset': offset,
        'items': [serialize_episode(request, item) for item in query[offset:offset + limit]],
    }


@router.get('/episodes/{episode_id}', response=EpisodeOut, summary='获取单条节目的播放信息')
def episode_detail(request, episode_id: int):
    """为客户端从推送、收藏等场景恢复单条播放记录。"""
    item = get_object_or_404(Video.objects.select_related('program'), id=episode_id)
    return serialize_episode(request, item)
