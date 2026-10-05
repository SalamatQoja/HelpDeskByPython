from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone



class User(AbstractUser):
    class Roles(models.TextChoices):
        CLIENT = 'client', 'Клиент'
        SUPPORT = 'support', 'Сотрудник поддержки'
        ADMIN = 'admin', 'Администратор'

    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.CLIENT)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', null=True, blank=True, verbose_name='Фотография')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    ONLINE_THRESHOLD = timedelta(minutes=15)

    def get_status(self):
        if not self.is_active:
            return 'blocked'
        if self.last_login and self.last_login >= timezone.now() - self.ONLINE_THRESHOLD:
            return 'online'
        return 'offline'

    def is_online(self):
        return self.get_status() == 'online'

    def is_blocked(self):
        return not self.is_active
