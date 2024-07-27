from django.db import models
from django_starter.db.models import ModelExt


class TvProgram(ModelExt):
    class Status(models.TextChoices):
        UPDATED = 'updated', '已更新'
        PENDING_UPDATE = 'pending_update', '待更新'
        DOWNLOADING = 'downloading', '下载中'
        FAILED = 'failed', '下载失败'

    name = models.CharField('节目名称', max_length=100)
    logo = models.ImageField('节目Logo', upload_to='tv/program/logos', null=True, blank=True)
    status = models.CharField(
        '状态', max_length=20,
        help_text='用于记录节目的当前状态，便于管理和调度。',
        choices=Status.choices,
        default=Status.PENDING_UPDATE,
    )
    source_url = models.URLField(
        '节目来源URL', null=True, blank=True,
        help_text='节目的数据来源网址，以便于爬虫程序获取更新。'
    )
    first_detected_update_time = models.DateTimeField(
        '节目更新时间', null=True, blank=True,
        help_text='节目在官网或订阅源网站上首次检测到更新的时间。'
    )
    last_synced_time = models.DateTimeField(
        '上次同步时间', null=True, blank=True,
        help_text='爬虫程序上一次去视频发布源检索节目的时间。'
    )
    local_update_time = models.DateTimeField(
        '本地更新时间', null=True, blank=True,
        help_text='节目最新的视频文件下载到本地的时间。'
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tv_program'
        verbose_name = '电视节目'
        verbose_name_plural = verbose_name


class Video(ModelExt):
    program = models.ForeignKey(
        'TvProgram', related_name='videos', verbose_name='电视节目',
        db_constraint=False, on_delete=models.CASCADE
    )
    name = models.CharField('视频名称', max_length=200)
    time = models.DateTimeField('时间', null=True, blank=True)
    related_link = models.URLField('相关链接', null=True, blank=True)
    origin_link = models.URLField('来源链接', null=True, blank=True)
    cover_link = models.URLField('封面图片链接', null=True, blank=True)
    cover = models.ImageField('视频封面', upload_to='tv/video/covers', null=True, blank=True)
    video_link = models.URLField('视频链接', null=True, blank=True)
    video = models.FileField('视频文件', upload_to='tv/video/raw-videos', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tv_video'
        verbose_name = '视频'
        verbose_name_plural = verbose_name
