#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   singals.py
@Time    :   2021/01/09 21:55:18
@Author  :   wei.zhang 
@Version :   1.0
@Desc    :   None
'''

# here put the import lib
from django.dispatch import Signal
post_update = Signal(providing_args=["sys_user_passwd"])
task_update = Signal(providing_args=["req_data"])