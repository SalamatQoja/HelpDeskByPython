from django.contrib import admin
from .models import Ticket, Comment, Employee, TicketHistory

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created']
    search_fields = ['user__username', 'user__email', 'phone_number']
    list_select_related = ['user']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'author', 'assigned_to', 'status', 'priority', 'created']
    list_filter = ['status', 'priority', 'created']
    search_fields = ['title', 'description', 'author__username']
    list_select_related = ['author', 'assigned_to']
    date_hierarchy = 'created'


# ========== COMMENT ==========
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'author', 'created', 'short_text']
    list_select_related = ['ticket', 'author']
    search_fields = ['text', 'author__username']

    @admin.display(description='Текст')
    def short_text(self, obj):
        return obj.text[:50] + ('…' if len(obj.text) > 50 else '')


# ========== TICKET HISTORY ==========
@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'field_changed', 'old_value', 'new_value', 'changed_by', 'changed_at']
    list_filter = ['field_changed', 'changed_at']
    search_fields = ['ticket__title', 'changed_by__username']
    list_select_related = ['ticket', 'changed_by']
    date_hierarchy = 'changed_at'
    readonly_fields = ['ticket', 'changed_by', 'field_changed',
                       'old_value', 'new_value', 'changed_at']
