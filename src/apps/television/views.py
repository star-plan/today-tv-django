from django.shortcuts import render
from .models import TvProgram, Video


# Create your views here.
def index(request):
    ctx = {
        'tv_programs': TvProgram.objects.all(),
    }
    return render(request, 'television/index.html', ctx)
