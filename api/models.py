from django.db import models

# Create your models here.
from rest_framework import serializers

class Rate(models.Model):
    eth=models.DecimalField(decimal_places=10, max_digits=30)
    btc=models.DecimalField(decimal_places=10, max_digits=30)

