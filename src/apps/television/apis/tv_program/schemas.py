from ninja import ModelSchema
from apps.television.models import *


class TvProgramIn(ModelSchema):
    class Meta:
        model = TvProgram
        # 旧的管理端 CRUD 模块保留为内部扩展，字段与当前模型保持一致。
        fields = ['name', 'logo', 'status', 'source_url']


class TvProgramOut(ModelSchema):
    class Meta:
        model = TvProgram
        fields = [
            'id', 'created_time', 'updated_time', 'name', 'logo', 'status', 'source_url',
            'first_detected_update_time', 'last_synced_time', 'local_update_time',
        ]
