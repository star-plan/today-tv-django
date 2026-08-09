from collections import defaultdict
from datetime import datetime

from django.db.models import Count, Max
from django.shortcuts import render, get_object_or_404
from .models import TvProgram, Video


def index(request):
    """展示可按日期浏览的节目归档，默认从最新内容开始。"""
    selected_date = request.GET.get('date', '')
    videos = Video.objects.select_related('program').order_by('-time', '-id')
    if selected_date:
        try:
            parsed_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            videos = videos.filter(time__date=parsed_date)
        except ValueError:
            # 非法筛选条件回退到完整归档，避免用户因为错误链接看到 500 页面。
            selected_date = ''
    available_dates = list(
        Video.objects.exclude(time__isnull=True).dates('time', 'day', order='DESC')[:14],
    )
    ctx = {
        'videos': videos[:60],
        'available_dates': available_dates,
        'selected_date': selected_date,
        'program': TvProgram.objects.filter(name='今日视线').first(),
    }
    return render(request, 'television/index.html', ctx)


def detail(request, pk):
    """公开节目页；不要求登录，方便搜索与分享链接直接访问。"""
    program = get_object_or_404(TvProgram, pk=pk)
    videos = Video.objects.filter(program=program).order_by('-time')

    # 按日期分组
    grouped_videos = defaultdict(list)
    for e in videos:
        date_str = e.time.strftime('%Y-%m-%d') if e.time else '未知日期'
        grouped_videos[date_str].append(e)

    ctx = {
        'program': program,
        'videos': videos,
        'grouped_videos': dict(grouped_videos),
    }

    return render(request, 'television/detail.html', ctx)


def video(request, pk):
    """渲染播放器并组织同日选集，支持用户开启自动连播。"""
    item = get_object_or_404(Video.objects.select_related('program'), pk=pk)
    # 获取与当前视频相同日期的其他视频
    same_date_videos = Video.objects.filter(program=item.program).order_by('time', 'id')
    if item.time:
        same_date_videos = same_date_videos.filter(time__date=item.time.date())
    else:
        same_date_videos = same_date_videos.none()
    playlist = list(same_date_videos)
    current_index = next((index for index, value in enumerate(playlist) if value.id == item.id), -1)
    next_video = playlist[current_index + 1] if 0 <= current_index < len(playlist) - 1 else None

    ctx = {
        'video': item,
        'same_date_videos': playlist,
        'next_video': next_video,
        # 已上传本地视频优先；采集场景通常使用源站直连地址。
        'playback_url': item.video.url if item.video else item.video_link,
    }

    return render(request, 'television/video.html', ctx)
