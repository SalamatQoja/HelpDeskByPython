from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from users import views as login_users

app_name = 'helpdeskside'

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login, name='login'),
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/my/', views.my_tickets, name='my_tickets'),
    path('tickets/<int:pk>/', views.client_ticket_detail, name='client_ticket_detail'),
    path('tickets/<int:pk>/close/', views.close_ticket, name='close_ticket'),
    path('all-tickets/', views.all_tickets, name='all_tickets'),
    path('all-tickets/<int:pk>/', views.employee_ticket_detail, name='employee_ticket_detail'),
    path('history-tickets/', views.history_tickets, name='history_tickets'),
    path('dashboard/statistics', views.dashboard_statistic, name='dashboard_statistics'),
]
