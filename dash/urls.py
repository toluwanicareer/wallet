from django.conf.urls import url
from django.urls import path
from . import views

app_name='dash'

urlpatterns = [
    path('wallet/<str:coin_symbol>/', views.WalletView.as_view(), name='match'),
    path('generate_address/', views.generate_address.as_view(), name='generate_addr'),
    path('receive_coin/', views.receive_coin.as_view(), name='receive_coin'),
    path('send_coin/', views.send_coin.as_view(), name='send_coin')
]