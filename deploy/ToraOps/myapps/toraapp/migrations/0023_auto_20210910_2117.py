# Generated by Django 3.1.5 on 2021-09-10 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toraapp', '0022_auto_20210909_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='shareserverinfo',
            name='vpn_list',
            field=models.TextField(blank=True, null=True, verbose_name='可访问的vpn列表'),
        ),
        migrations.AlterField(
            model_name='taskflow',
            name='ownership',
            field=models.CharField(choices=[('1', '客户自购'), ('2', '华鑫采购'), ('3', '华鑫自有'), ('4', '全创自组机'), ('5', '营业部提供'), ('9', '不确定')], default='9', max_length=2, verbose_name='物主身份'),
        ),
    ]
