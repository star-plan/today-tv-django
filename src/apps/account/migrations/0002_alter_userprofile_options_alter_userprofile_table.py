# Generated by Django 5.0.3 on 2024-06-03 15:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': '用户资料', 'verbose_name_plural': '用户资料'},
        ),
        migrations.AlterModelTable(
            name='userprofile',
            table='djs_user_profile',
        ),
    ]
