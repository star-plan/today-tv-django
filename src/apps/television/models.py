from django.db import models
from django_starter.db.models import ModelExt


class TvProgram(ModelExt):
    name = models.CharField('节目名称', max_length=100)
    logo = models.ImageField('节目Logo', upload_to='tv/program/logos', null=True, blank=True)
    last_updated_at = models.DateTimeField('上次更新时间', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tv_program'
        verbose_name = '电视节目'
        verbose_name_plural = verbose_name


class Video(ModelExt):
    program = models.ForeignKey(
        'TvProgram', related_name='videos',
        db_constraint=False, on_delete=models.CASCADE
    )
    name = models.CharField('视频名称', max_length=200)
    time = models.DateTimeField('时间', null=True, blank=True)
    related_link = models.URLField('相关链接', null=True, blank=True)
    origin_link = models.URLField('原始视频链接', null=True, blank=True)
    cover = models.ImageField('视频封面', upload_to='tv/video/cover', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tv_video'
        verbose_name = '视频'
        verbose_name_plural = verbose_name
