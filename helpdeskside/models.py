from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    phone_number = models.CharField(max_length=20, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return f'{self.first_name} {self.last_name}'
    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        ordering = ['user__first_name', 'user__last_name']


class Ticket(models.Model):
    class Status(models.TextChoices):
        NEW = 'NEW', 'Новая'
        IN_PROGRESS = 'IN_PROGRESS', 'В работе'
        WAITING = 'WT', 'Ожидание'
        RESOLVED = 'RL', 'Решена'
        CLOSED = 'CL', 'Закрыта'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Низкий'
        MEDIUM = 'MEDIUM', 'Средний'
        HIGH = 'HIGH', 'Высокий'
        CRITICAL = 'CRITICAL', 'Критический'

    title = models.CharField(max_length=250, verbose_name='Заголовка')
    description = models.TextField(verbose_name='Описание')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets')
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW)
    priority = models.CharField(max_length=8, choices=Priority.choices, default=Priority.LOW, verbose_name='Приоритет')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = ['-created']


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.text[:50]}'

    class Meta:
        ordering = ['-created']


class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='ticket_changes')
    field_changed = models.CharField(max_length=50)
    old_value = models.TextField(blank=True, default='')
    new_value = models.TextField(blank=True, default='')
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.ticket} — {self.field_changed} ({self.changed_at:%d.%m.%Y %H:%M})'

    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'История заявки'
        verbose_name_plural = 'Истории заявок'
