# Generated by Django 5.0.6 on 2024-07-28 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('television', '0005_video_cover_link_video_video_link_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='duration',
            field=models.DurationField(blank=True, null=True, verbose_name='视频时长'),
        ),
    ]
