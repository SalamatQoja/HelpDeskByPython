# helpdeskside/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee
from users.models import User


@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, **kwargs):
    if instance.role in (User.Roles.SUPPORT, User.Roles.ADMIN):
        Employee.objects.get_or_create(user=instance)
