# Generated by Django 3.1.5 on 2021-08-27 13:53

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('toraapp', '0018_auto_20210827_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nodeinfo',
            name='business',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('hxzq', '现货股票'), ('sp', '期权'), ('rzrq', '两融'), ('qh', '期货')], max_length=15, null=True, verbose_name='业务'),
        ),
    ]
