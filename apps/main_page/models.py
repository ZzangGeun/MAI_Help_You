from django.db import models

# Create your models here.
class id(models.Model):
    user_id = models.CharField(max_length=100, primary_key=True)
    password = models.CharField(max_length=100)
    nick_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    nexon_api_key = models.CharField(max_lensssgth=200)
