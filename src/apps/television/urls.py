from django.urls import path
from . import views

app_name = 'television'

urlpatterns = [
    path('', views.index, name='index'),
    path('program/<int:pk>/', views.detail, name='detail'),
    path('video/<int:pk>/', views.video, name='video'),
]
