from toraapp.serializer.userSerializer import UserSerializer, UserRegisterSerializer, UserInfoSerializer
from django.contrib.auth.models import User
from rest_framework import generics, permissions, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from toraapp.models import *


# Register API
class RegisterApi(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        # serializer.save() should call after is_valid()
        serializer.is_valid(raise_exception=True)
        userinfo = serializer.save(user=request.user)
        return Response({
            "userinfo": UserSerializer(userinfo, context=self.get_serializer_context()).data,
            "message": "User Created Successfully",
        })


# 重写Django rest的token视图
class LoginAPI(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        data = {
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'password': user.password
        }

        return Response({
            'data': data,
            # 自定义返回成功状态20000
            'code': 20000
            # "menulist": getmenu()
        })

'''
    "userInfo": {
        "key": "01f8045aab0766f997f2272b4c6f20f575a84c6a",
        "created": "2020-12-20T18:11:22.202207+08:00",
        "user": {
            "username": "admin",
            "first_name": "",
            "last_name": "",
            "email": "",
            "role": "admin",
            "phone": "",
            "avatar": null,
            "token": "01f8045aab0766f997f2272b4c6f20f575a84c6a"
        }
'''
class GetUserInfo(generics.GenericAPIView, mixins.RetrieveModelMixin):
    lookup_field = 'key'
    serializer_class = UserInfoTokenSerializer
    queryset = AuthtokenToken.objects.all()

    def get(self, request, *args, **kwargs):
        userInfo_data = self.retrieve(self, request, *args, **kwargs)
        userInfo = userInfo_data.data['user']
        # print(userInfo['role'])
        data = {
            'roles': userInfo['role'],
            'introduction': 'I am a super administrator',
            # 'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
            'avatar': userInfo['avatar'],
            'name': userInfo['username'],
        }
        return Response({
            'data': data,
            'code': 20000,
            'userInfo': userInfo
        })


# 用户Logout的视图，此处简单返回状态码和成功数据即可
class UserLogout(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response({
            'data': 'success',
            # 自定义返回成功状态20000
            'code': 20000
        })


# 编辑用户
class UserUpdate(generics.GenericAPIView, mixins.UpdateModelMixin):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    """
    Update a model instance.
    """
    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        # 自定义返回信息
        data = serializer.data
        return Response({
            'data': data,
            'code': 20000
        })

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


# 删除用户
class UserDel(generics.GenericAPIView, mixins.DestroyModelMixin):
    serializer_class = UserInfoTokenSerializer
    queryset = User.objects.all()
    """
    Destroy a model instance.
    """
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'data': status.HTTP_204_NO_CONTENT,
            'code': 20000
        })

    def perform_destroy(self, instance):
        instance.delete()


# 测试返回用户信息的userInfo
class UserTest(generics.GenericAPIView, mixins.RetrieveModelMixin):

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(self, request, *args, **kwargs)
