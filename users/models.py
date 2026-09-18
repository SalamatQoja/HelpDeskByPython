from django.db import models
from django.contrib.auth.models import AbstractUser
from django.views.generic import CreateView


class User(AbstractUser):
    class Roles(models.TextChoices):
        CLIENT = 'client', 'Клиент'
        SUPPORT = 'support', 'Сотрудник поддержки'
        ADMIN = 'admin', 'Администратор'

    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.CLIENT)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', null=True, blank=True, verbose_name='Фотография')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
