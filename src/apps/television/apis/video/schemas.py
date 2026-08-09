from ninja import ModelSchema
from apps.television.models import *


class VideoIn(ModelSchema):
    class Meta:
        model = Video
        # 内部维护接口使用当前视频模型的真实字段，避免早期模板字段漂移。
        fields = [
            'program', 'name', 'time', 'related_link', 'origin_link', 'cover_link',
            'cover', 'video_link', 'video', 'duration', 'source_key',
        ]


class VideoOut(ModelSchema):
    class Meta:
        model = Video
        fields = [
            'id', 'created_time', 'updated_time', 'program', 'name', 'time', 'related_link',
            'origin_link', 'cover_link', 'cover', 'video_link', 'video', 'duration', 'source_key',
        ]
