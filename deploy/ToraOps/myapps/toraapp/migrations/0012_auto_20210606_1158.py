# Generated by Django 3.1.5 on 2021-06-06 11:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toraapp', '0011_auto_20210606_1119'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nodeinfo',
            old_name='cust_mail_module',
            new_name='node_cfg_module',
        ),
    ]
