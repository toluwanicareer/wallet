from django.conf.urls import url
from django.urls import path
from . import views
from django.conf import settings

app_name='main'

urlpatterns = [
    path(settings.CALLBACK_URL, views.handle_tx, name='match'),

    ]