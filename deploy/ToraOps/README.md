下载项目
```
git clone http://10.168.8.206:8888/tora/backend.git
```
安装依赖： 
```
pip3 install -r requirements.txt
```

创建数据表
```
python manage.py makemigrations
python manage.py migrate
```

创建管理员
```
python manage.py createsuperuser
```

项目本地跑起来:
```
python manage.py runserver 9090
```

登录后台：
```
http://127.0.0.1:9090/
```
查看后台api：
```
http://127.0.0.1:9090/docs/
```

