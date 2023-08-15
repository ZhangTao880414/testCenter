from rest_framework import serializers, generics
from django.contrib.auth.models import User
from toraapp.models import UserInfo


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='userinfo.role')
    phone = serializers.CharField(source='userinfo.phone')
    avatar = serializers.ImageField(source='userinfo.avatar', required=False)
    wechat = serializers.ImageField(source='userinfo.wechat', required=False)
    token = serializers.CharField(source='userToken.key', required=False)

    class Meta:
        model = User
        # fields = '__all__'
        fields = ['username', 'first_name', 'last_name', 'email', 'role'
                  , 'phone', 'avatar', 'wechat', 'token']

    def update(self, instance, validated_data):
        print(validated_data['userinfo'])
        userinfo_data = validated_data.pop('userinfo')
        userinfo = instance.userinfo

        # User
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # UserInfo
        userinfo.role = userinfo_data.get('role', userinfo.role)
        userinfo.phone = userinfo_data.get('phone', userinfo.phone)
        userinfo.avatar = userinfo_data.get('avatar', userinfo.avatar)
        userinfo.avatar = userinfo_data.get('wechat', userinfo.wechat)
        userinfo.save()

        return instance



class UserInfoSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = UserInfo

        
        fields = '__all__'


class UserRegisterSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='userinfo.role')
    phone = serializers.CharField(source='userinfo.phone')
    avatar = serializers.ImageField(source='userinfo.avatar', required=False)
    # first_name = serializers.CharField(required=False)
    # last_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'role'
                  , 'phone', 'avatar']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], password=validated_data['password'],
                                        email=validated_data['email'])
        print(validated_data)
        validated_data.pop('username')
        validated_data.pop('password')
        validated_data.pop('email')
        '''
        # {'username': 'User1', 'password': 'yqh123', 'email': '', 'userinfo': {'role': 'ADmin', 'phone': '182381241'}, 
        # 'user': <django.contrib.auth.models.AnonymousUser object at 0x00000289DA8D4C08>}
        '''
        # print(validated_data)
        userinfo = validated_data.pop('userinfo')
        role = userinfo.pop('role')
        phone = userinfo.pop('phone')
        # print(role)
        userinfo = UserInfo.objects.create(user=user, role=role, phone=phone)
        userinfo.save()

        return user


