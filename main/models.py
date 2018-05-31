from django.db import models

# Create your models here.
class test_model(models.Model):
    data=models.TextField()
    created_date=models.DateTimeField(auto_now_add=True)
