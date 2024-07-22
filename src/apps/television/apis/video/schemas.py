from ninja import ModelSchema
from apps.television.models import *


class VideoIn(ModelSchema):
    
    program_id: int
    

    class Meta:
        model = Video
        fields = ['is_deleted', 'created_time', 'updated_time', 'name', 'time', 'related_link', 'origin_link', 'cover', ]


class VideoOut(ModelSchema):
    class Meta:
        model = Video
        fields = ['id', 'is_deleted', 'created_time', 'updated_time', 'program', 'name', 'time', 'related_link', 'origin_link', 'cover', ]
