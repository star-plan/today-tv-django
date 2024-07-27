from django.contrib.auth.decorators import login_required
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
        'tv_programs': item,
    }

    return render(request, 'television/detail.html', ctx)
