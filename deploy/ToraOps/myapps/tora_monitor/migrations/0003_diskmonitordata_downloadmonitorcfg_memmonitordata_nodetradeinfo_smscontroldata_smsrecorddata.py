# Generated by Django 3.1.5 on 2021-09-08 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tora_monitor', '0002_auto_20210319_1338'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiskMonitorData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inner_ip', models.GenericIPAddressField(verbose_name='内网IP')),
                ('file_dir', models.CharField(choices=[('date', '一次性'), ('interval', '固定间隔'), ('cron', 'crontab格式')], default='cron', max_length=20, verbose_name='目录')),
                ('total_disk', models.CharField(max_length=40, verbose_name='总量')),
                ('used_disk', models.CharField(max_length=40, verbose_name='已使用量')),
                ('usage', models.CharField(max_length=40, verbose_name='使用率')),
                ('is_warning', models.CharField(choices=[('0', '暂停'), ('1', '激活')], default='0', max_length=2, verbose_name='是否需要报警')),
                ('is_handled', models.CharField(choices=[('0', '暂停'), ('1', '激活')], default='0', max_length=2, verbose_name='是否已处理')),
                ('send_phone', models.CharField(blank=True, max_length=254, null=True, verbose_name='接收警告的手机号')),
                ('send_mail', models.CharField(blank=True, max_length=254, null=True, verbose_name='接收警告的邮箱')),
                ('comment', models.CharField(blank=True, max_length=254, null=True, verbose_name='备注')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '磁盘使用监控数据',
                'verbose_name_plural': '磁盘使用监控数据',
            },
        ),
        migrations.CreateModel(
            name='DownloadMonitorCfg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business', models.CharField(choices=[('stock', '现货股票'), ('sp', '期权'), ('credit', '两融'), ('cffex', '中金期货')], max_length=20, verbose_name='业务')),
                ('node_no', models.CharField(max_length=4, unique=True, verbose_name='节点编号')),
                ('is_monitor', models.CharField(choices=[('0', '否'), ('1', '是')], default='1', max_length=2, verbose_name='是否监控')),
                ('cur_status', models.CharField(choices=[('0', '异常'), ('1', '正常'), ('2', '升级中'), ('3', '回退中'), ('4', '其他')], default='1', max_length=2, verbose_name='当前状态')),
                ('AppInfo', models.IntegerField(blank=True, null=True, verbose_name='组件行数')),
                ('AppRunningInfo', models.IntegerField(blank=True, null=True, verbose_name='数据库项')),
                ('DbmtIbfo', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('Exchange', models.CharField(blank=True, max_length=50, null=True, verbose_name='证券交易所ExchangeOrderNo')),
                ('ExchangeSyncStatus', models.CharField(blank=True, max_length=50, null=True, verbose_name='DateSyncStatus(3/4/4)')),
                ('Front', models.IntegerField(blank=True, null=True, verbose_name='前端连接数')),
                ('FundTransferDetail', models.CharField(blank=True, max_length=50, null=True, verbose_name='StatusMsg处理状态')),
                ('OrderLocalSeqPrefix', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSEBondConversionInfo', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSEBondPutbackInfo', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSEETFBasket', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSEETFFile', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSEIPOInfo', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSEInvestorPositionLimit', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSEInvestorTradingFee', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSEPBU', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSEPosition', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSEPositionLimitTemplate', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSEPositionParam', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSESecurity', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSETrader', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSETraderOffer', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSETradingFee', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSETradingFeeLimitTemplate', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSETradingFeeTemplate', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SSETradingRightTemplate', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('SystemParam', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('TerminalFloatingCommission', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('TradingAccount', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('TransNum_Trading', models.CharField(blank=True, max_length=50, null=True, verbose_name='盘钟transnum')),
                ('XMDserver', models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库项')),
                ('TransNum_Closed', models.CharField(blank=True, max_length=50, null=True, verbose_name='盘后transnum')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '数据库download日常监控项',
                'verbose_name_plural': '数据库download日常监控项',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='MemMonitorData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inner_ip', models.GenericIPAddressField(verbose_name='内网IP')),
                ('total_mem', models.CharField(max_length=40, verbose_name='总内存')),
                ('used_mem', models.CharField(max_length=40, verbose_name='已使用量')),
                ('usage', models.CharField(max_length=40, verbose_name='已使用率')),
                ('is_warning', models.CharField(choices=[('0', '暂停'), ('1', '激活')], default='0', max_length=2, verbose_name='是否需要报警')),
                ('is_handled', models.CharField(choices=[('0', '暂停'), ('1', '激活')], default='0', max_length=2, verbose_name='是否已处理')),
                ('send_phone', models.CharField(blank=True, max_length=254, null=True, verbose_name='接收警告的手机号')),
                ('send_mail', models.CharField(blank=True, max_length=254, null=True, verbose_name='接收警告的邮箱')),
                ('comment', models.CharField(blank=True, max_length=254, null=True, verbose_name='备注')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '内存使用监控数据',
                'verbose_name_plural': '内存使用监控数据',
            },
        ),
        migrations.CreateModel(
            name='NodeTradeInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('engine_room', models.CharField(choices=[('shwp', '上海宛平'), ('shgq', '上海外高桥'), ('shjq', '上海金桥'), ('shkj', '上海科技网'), ('shxt', '上海斜土路'), ('dgnf', '东莞南方')], max_length=10, verbose_name='机房')),
                ('business', models.CharField(choices=[('stock', '现货股票'), ('sp', '期权'), ('credit', '两融'), ('cffex', '中金期货')], max_length=20, verbose_name='业务')),
                ('node_no', models.CharField(max_length=4, unique=True, verbose_name='节点编号')),
                ('cur_status', models.CharField(choices=[('0', '异常'), ('1', '正常'), ('2', '升级中'), ('3', '回退中'), ('4', '其他')], default='1', max_length=2, verbose_name='当前状态')),
                ('online_cust_count', models.IntegerField(blank=True, null=True, verbose_name='在线用户数')),
                ('order_count', models.IntegerField(blank=True, null=True, verbose_name='委托笔数')),
                ('cancel_count', models.IntegerField(blank=True, null=True, verbose_name='撤单笔数')),
                ('trade_count', models.IntegerField(blank=True, null=True, verbose_name='成交笔数')),
                ('turnover', models.FloatField(blank=True, null=True, verbose_name='成交金额')),
                ('tora_version', models.CharField(blank=True, max_length=20, null=True, verbose_name='奇点版本信息')),
                ('start_time', models.DateTimeField(auto_now_add=True, verbose_name='启动时间')),
                ('stop_time', models.DateTimeField(auto_now_add=True, verbose_name='关闭时间')),
                ('error_msg', models.CharField(blank=True, max_length=254, null=True, verbose_name='异常信息')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '节点交易监控信息',
                'verbose_name_plural': '节点交易监控信息',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='SmsControlData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('init_day', models.DateField(verbose_name='初始化日期')),
                ('ps_port', models.IntegerField(default=0, verbose_name='进程端口监控已用')),
                ('disk', models.IntegerField(default=0, verbose_name='硬盘监控已发')),
                ('mem', models.IntegerField(default=0, verbose_name='内存监控已发')),
                ('ping', models.IntegerField(default=0, verbose_name='ping监控已发')),
                ('db_trade', models.IntegerField(default=0, verbose_name='数据库盘中监控已发')),
                ('core', models.IntegerField(default=0, verbose_name='core监控已发')),
                ('errorID', models.IntegerField(default=0, verbose_name='errorID监控已发')),
                ('errorlog', models.IntegerField(default=0, verbose_name='errorlog监控已发')),
                ('ipmi', models.IntegerField(default=0, verbose_name='ipmi监控已发')),
                ('NoLimit', models.IntegerField(default=0, verbose_name='NoLimit已发')),
                ('total_used_count', models.IntegerField(default=0, verbose_name='当日已用总量')),
                ('single_limit', models.IntegerField(default=20, verbose_name='单项限制次数')),
                ('total_limit', models.IntegerField(default=500, verbose_name='每日总限量')),
                ('comment', models.CharField(blank=True, max_length=254, null=True, verbose_name='备注')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '短信发送数量配置',
                'verbose_name_plural': '短信发送数量配置',
            },
        ),
        migrations.CreateModel(
            name='SmsRecordData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sms_type', models.CharField(max_length=32, verbose_name='短信类型')),
                ('send_msg', models.CharField(blank=True, max_length=254, null=True, verbose_name='发送内容')),
                ('send_phones', models.CharField(blank=True, max_length=254, null=True, verbose_name='发送的手机号')),
                ('send_status', models.CharField(choices=[('0', '否'), ('1', '是')], default='1', max_length=2, verbose_name='发送状态')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '短信发送记录',
                'verbose_name_plural': '短信发送记录',
            },
        ),
    ]
