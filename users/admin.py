from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active', 'is_superuser']  # фильтры справа
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    # ---------- Форма редактирования пользователя создать етемиз----------
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {
            'fields': ('role', 'photo', 'birth_date'),
        }),
    )

    # ---------- Форма пользователя создать етемиз----------
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительно', {
            'fields': ('role', 'photo', 'birth_date'),
        }),
    )
