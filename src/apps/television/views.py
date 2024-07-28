from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from .models import TvProgram, Video


def index(request):
    ctx = {
        'tv_programs': TvProgram.objects.all(),
    }
    return render(request, 'television/index.html', ctx)


@login_required()
def detail(request, pk):
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
    item = get_object_or_404(Video.objects.select_related('program'), pk=pk)
    # 获取与当前视频相同日期的其他视频
    same_date_videos = Video.objects.filter(
        program=item.program,
        time__date=item.time.date()
    )

    ctx = {
        'video': item,
        'same_date_videos': same_date_videos,
    }

    return render(request, 'television/video.html', ctx)
