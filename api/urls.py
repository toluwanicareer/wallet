from django.conf.urls import url
from django.urls import path
from . import views

app_name='api'

urlpatterns = [
    path('account/login', views.LoginView, name='login'),
    path('account/signup', views.signupView, name='signup'),
    path('dash', views.dash, name='dash'),
    path('wallet/<str:coin_symbol>', views.WalletView, name='match'),
    path('wallet/<str:coin_symbol>/send', views.send_coin, name='send_coin'),
    path('wallet/<str:coin_symbol>/receive', views.receive_coin, name='receive_coin')
    ]