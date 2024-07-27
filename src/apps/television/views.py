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
    item = get_object_or_404(TvProgram, pk=pk)

    ctx = {
        'program': item,
        'videos': Video.objects.filter(program=item).order_by('-time'),
    }

    return render(request, 'television/detail.html', ctx)


def video(request, pk):
    item = get_object_or_404(Video, pk=pk)
    ctx = {
        'video': item,
    }

    return render(request, 'television/video.html', ctx)

