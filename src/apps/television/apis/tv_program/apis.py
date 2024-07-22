from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.television.models import *
from apps.television.apis.tv_program.schemas import *

router = Router(tags=['tv_program'])


@router.post('/tv_program', response=TvProgramOut, url_name='television/tv_program/create')
def create(request, payload: TvProgramIn):
    item = TvProgram.objects.create(**payload.dict())
    return item


@router.get('/tv_program/{item_id}', response=TvProgramOut, url_name='television/tv_program/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(TvProgram, id=item_id)
    return item


@router.get('/tv_program', response=List[TvProgramOut], url_name='television/tv_program/list')
@paginate
def list_items(request):
    qs = TvProgram.objects.all()
    return qs


@router.put('/tv_program/{item_id}', response=TvProgramOut, url_name='television/tv_program/update')
def update(request, item_id, payload: TvProgramIn):
    item = get_object_or_404(TvProgram, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/tv_program/{item_id}', response=TvProgramOut, url_name='television/tv_program/partial_update')
def partial_update(request, item_id, payload: TvProgramIn):
    item = get_object_or_404(TvProgram, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/tv_program/{item_id}', url_name='television/tv_program/destroy')
def destroy(request, item_id):
    item = get_object_or_404(TvProgram, id=item_id)
    item.delete()
    return responses.ok('已删除')