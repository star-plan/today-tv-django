from django.db.models import Count, Max
from django.shortcuts import render

from apps.television.models import TvProgram, Video


# Create your views here.
def index(request):
    """将首页作为今日节目入口，而不是框架功能的导航页。"""
    program = TvProgram.objects.filter(name='今日视线').annotate(
        episode_count=Count('videos'),
        latest_published_at=Max('videos__time'),
    ).first()
    latest_videos = Video.objects.select_related('program').order_by('-time', '-id')[:8]
    return render(request, 'home/index.html', {
        'program': program,
        'featured_video': latest_videos[0] if latest_videos else None,
        'latest_videos': latest_videos,
    })
