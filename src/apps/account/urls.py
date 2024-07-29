from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('login/sso/', views.login_sso, name='login-sso'),
    path('sign-up/', views.signup_view, name='sign-up'),
    path('logout/', views.logout_view, name='logout'),
]
