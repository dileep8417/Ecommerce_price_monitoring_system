from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Searches(models.Model):
    pass
class Monitor(models.Model):
    user_id = models.IntegerField()
    title = models.CharField(max_length=100)
    actual_price = models.IntegerField()
    current_price = models.IntegerField()
    url = models.TextField()
    site = models.CharField(max_length=20)
    email = models.EmailField(max_length=50,default=User.EMAIL_FIELD,blank=True)
