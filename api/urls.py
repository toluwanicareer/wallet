from django.conf.urls import url
from django.urls import path
from . import views

app_name='api'

urlpatterns = [
    path('account/login', views.LoginView, name='login'),
    ]