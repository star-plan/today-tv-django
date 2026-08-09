# Generated manually to keep the data migration explicit and reviewable.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('television', '0007_alter_tvprogram_status'),
    ]

    operations = [
        # 允许历史记录暂时为 NULL，新的采集记录则总会拥有来源唯一键。
        migrations.AddField(
            model_name='video',
            name='source_key',
            field=models.CharField(blank=True, help_text='由采集器根据来源详情页地址生成，用于增量去重。', max_length=64, null=True, unique=True, verbose_name='来源唯一标识'),
        ),
        migrations.AddIndex(
            model_name='video',
            index=models.Index(fields=['program', '-time'], name='tv_video_program_time_idx'),
        ),
    ]
