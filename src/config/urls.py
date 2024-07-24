from django.contrib import admin
from django.urls import path, include
from apps.home.views import index

from config.apis import api

urlpatterns = [
    path('', index),
    path('api/', api.urls),
    path('demo', include('apps.demo.urls')),
    path('home/', include('apps.home.urls')),
    path('tv', include('apps.television.urls')),

    # DjangoStarter
    path('django-starter/', include('django_starter.urls')),

    # 管理后台
    path('admin/', include('django_starter.contrib.admin.urls')),  # 实现 admin 登录验证码
    path('admin/', admin.site.urls),

    # 验证码
    path('captcha/', include('captcha.urls')),
]
