from django.urls import path
from . import views

app_name = 'television'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.detail, name='detail'),
]
