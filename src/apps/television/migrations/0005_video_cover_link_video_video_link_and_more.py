# Generated by Django 5.0.6 on 2024-07-27 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('television', '0004_remove_tvprogram_last_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='cover_link',
            field=models.URLField(blank=True, null=True, verbose_name='封面图片链接'),
        ),
        migrations.AddField(
            model_name='video',
            name='video_link',
            field=models.URLField(blank=True, null=True, verbose_name='视频链接'),
        ),
        migrations.AlterField(
            model_name='video',
            name='origin_link',
            field=models.URLField(blank=True, null=True, verbose_name='来源链接'),
        ),
    ]
