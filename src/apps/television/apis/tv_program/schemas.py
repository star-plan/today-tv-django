from ninja import ModelSchema
from apps.television.models import *


class TvProgramIn(ModelSchema):
    

    class Meta:
        model = TvProgram
        fields = ['is_deleted', 'created_time', 'updated_time', 'name', 'logo', 'last_updated_at', ]


class TvProgramOut(ModelSchema):
    class Meta:
        model = TvProgram
        fields = ['id', 'is_deleted', 'created_time', 'updated_time', 'name', 'logo', 'last_updated_at', ]
