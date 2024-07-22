from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags

from .models import *


@admin.register(TvProgram)
class TvProgramAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'last_updated_at', 'logo_thumb_tag', ]
    list_display_links = ['id', 'name', 'last_updated_at', ]
    readonly_fields = ['id', 'created_time', 'updated_time', 'is_deleted', 'logo_tag', ]
    fieldsets = (
        ('电视节目', {'fields': ('id', 'name', 'last_updated_at',)}),
        ('节目Logo', {'fields': ('logo', 'logo_tag')}),
        ('通用信息', {'fields': ('created_time', 'updated_time', 'is_deleted')}),
    )

    @admin.display(description='节目Logo')
    def logo_tag(self, obj: TvProgram) -> str:
        if not obj.logo: return ''
        return html_tags.image(obj.logo.url, '节目Logo', width=250)

    @admin.display(description='节目Logo-缩略图')
    def logo_thumb_tag(self, obj: TvProgram) -> str:
        if not obj.logo: return ''
        return html_tags.image(obj.logo.url, '节目Logo-缩略图', width=50, height=50)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'program', 'name', 'time', 'related_link', 'origin_link', 'cover_thumb_tag', ]
    list_display_links = ['id', 'name', 'time', 'related_link', 'origin_link', ]
    readonly_fields = ['id', 'created_time', 'updated_time', 'is_deleted', 'cover_tag', ]
    fieldsets = (
        ('视频', {'fields': ('id', 'program', 'name', 'time', 'related_link', 'origin_link',)}),
        ('视频封面', {'fields': ('cover', 'cover_tag')}),
        ('通用信息', {'fields': ('created_time', 'updated_time', 'is_deleted')}),
    )

    @admin.display(description='视频封面')
    def cover_tag(self, obj: Video) -> str:
        if not obj.cover: return ''
        return html_tags.image(obj.cover.url, '视频封面', width=250)

    @admin.display(description='视频封面-缩略图')
    def cover_thumb_tag(self, obj: Video) -> str:
        if not obj.cover: return ''
        return html_tags.image(obj.cover.url, '视频封面-缩略图', width=50, height=50)
