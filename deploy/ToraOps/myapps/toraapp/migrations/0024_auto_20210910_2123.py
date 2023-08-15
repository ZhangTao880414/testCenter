# Generated by Django 3.1.5 on 2021-09-10 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toraapp', '0023_auto_20210910_2117'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskflow',
            name='room_no',
            field=models.DateField(blank=True, max_length=50, null=True, verbose_name='房间号'),
        ),
        migrations.AddField(
            model_name='taskflow',
            name='row_no',
            field=models.DateField(blank=True, max_length=50, null=True, verbose_name='排编号'),
        ),
    ]
