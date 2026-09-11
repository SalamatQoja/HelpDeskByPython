from django.db import models
from django.contrib.auth.models import AbstractUser
from django.views.generic import CreateView


class User(AbstractUser):
    photo = models.ImageField(upload_to='users/%Y/%m/%d', null=True, blank=True, verbose_name='Фотография')
    birth_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата рождение')

    
