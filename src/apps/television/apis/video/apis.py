from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.television.models import *
from apps.television.apis.video.schemas import *

router = Router(tags=['video'])


@router.post('/video', response=VideoOut, url_name='television/video/create')
def create(request, payload: VideoIn):
    item = Video.objects.create(**payload.dict())
    return item


@router.get('/video/{item_id}', response=VideoOut, url_name='television/video/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Video, id=item_id)
    return item


@router.get('/video', response=List[VideoOut], url_name='television/video/list')
@paginate
def list_items(request):
    qs = Video.objects.all()
    return qs


@router.put('/video/{item_id}', response=VideoOut, url_name='television/video/update')
def update(request, item_id, payload: VideoIn):
    item = get_object_or_404(Video, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/video/{item_id}', response=VideoOut, url_name='television/video/partial_update')
def partial_update(request, item_id, payload: VideoIn):
    item = get_object_or_404(Video, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/video/{item_id}', url_name='television/video/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Video, id=item_id)
    item.delete()
    return responses.ok('已删除')