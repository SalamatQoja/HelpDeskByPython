from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Count, Q
from django.shortcuts import render
from users.decorators import role_required
from users.models import User
from .forms import TicketForm, CommentForm
from .models import Ticket, Comment, Employee, TicketHistory


def index(request):
    return render(request, "helpdeskside/index.html", {"title": "Главная"})


@login_required
@role_required('client')
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.author = request.user
            ticket.save()
            return redirect('helpdeskside:my_tickets')
    else:
        form = TicketForm()
    return render(request, 'helpdeskside/create_ticket.html', {'form': form})


@login_required
@role_required('client')
def my_tickets(request):
    tickets = Ticket.objects.filter(author=request.user).order_by('-created')
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'helpdeskside/my_tickets.html', {'page_obj': page_obj})


@login_required
@role_required('client')
def client_ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, author=request.user)
    comments = ticket.comments.all().order_by('-created')

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            return redirect('helpdeskside:client_ticket_detail', pk=pk)
    else:
        comment_form = CommentForm()

    return render(request, 'helpdeskside/client_ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
    })


@login_required
@role_required('client')
def close_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, author=request.user)
    old_status = ticket.status
    ticket.status = Ticket.Status.CLOSED
    ticket.save(update_fields=['status'])

    TicketHistory.objects.create(
        ticket=ticket,
        changed_by=request.user,
        field_changed='status',
        old_value=old_status,
        new_value=Ticket.Status.CLOSED,
    )
    return redirect('helpdeskside:client_ticket_detail', pk=pk)


@login_required
@role_required('support', 'admin')
def all_tickets(request):
    tickets = Ticket.objects.all().order_by('-created')
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'helpdeskside/all_tickets.html', {'page_obj': page_obj})


@login_required
@role_required('support', 'admin')
def employee_ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    action = request.POST.get('action') if request.method == 'POST' else None

    if action == 'update':
        if 'status' in request.POST:
            new_status = request.POST.get('status')
            if new_status and new_status != ticket.status:
                TicketHistory.objects.create(
                    ticket=ticket, changed_by=request.user,
                    field_changed='status',
                    old_value=ticket.status, new_value=new_status,
                )
                ticket.status = new_status

        if 'priority' in request.POST:
            new_priority = request.POST.get('priority')
            if new_priority and new_priority != ticket.priority:
                TicketHistory.objects.create(
                    ticket=ticket, changed_by=request.user,
                    field_changed='priority',
                    old_value=ticket.priority, new_value=new_priority,
                )
                ticket.priority = new_priority

        if 'assigned_to' in request.POST:
            new_assignee = request.POST.get('assigned_to') or None
            old_assignee = ticket.assigned_to_id
            if str(old_assignee or '') != str(new_assignee or ''):
                TicketHistory.objects.create(
                    ticket=ticket, changed_by=request.user,
                    field_changed='assigned_to',
                    old_value=str(old_assignee or '—'),
                    new_value=str(new_assignee or '—'),
                )
                ticket.assigned_to_id = new_assignee

        ticket.save()
        return redirect('helpdeskside:employee_ticket_detail', pk=pk)

    if action == 'comment':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
        return redirect('helpdeskside:employee_ticket_detail', pk=pk)

    comment_form = CommentForm()
    comments = ticket.comments.all().order_by('created')
    history = ticket.history.all().order_by('-changed_at')
    employees = Employee.objects.filter(
        user__role__in=[User.Roles.SUPPORT, User.Roles.ADMIN],
        user__is_active=True,
    ).select_related('user').order_by('user__first_name')

    return render(request, 'helpdeskside/employee_ticket_detail.html', {
        'ticket': ticket,
        'comment_form': comment_form,
        'comments': comments,
        'history': history,
        'employees': employees,
        'status_choices': Ticket.Status.choices,
        'priority_choices': Ticket.Priority.choices,
    })


@login_required
@role_required('support', 'admin')
def history_tickets(request):
    history_tickets = TicketHistory.objects.select_related(
        'ticket', 'changed_by'
    ).order_by('-changed_at')
    paginator = Paginator(history_tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'helpdeskside/history_tickets.html', {'page_obj': page_obj})


@login_required
@role_required('support', 'admin')
def dashboard_statistic(request):
    stats = Ticket.objects.aggregate(
        total=Count('id'),
        new=Count('id', filter=Q(status=Ticket.Status.NEW)),
        in_progress=Count('id', filter=Q(status=Ticket.Status.IN_PROGRESS)),
        waiting=Count('id', filter=Q(status=Ticket.Status.WAITING)),
        resolved=Count('id', filter=Q(status=Ticket.Status.RESOLVED)),
        closed=Count('id', filter=Q(status=Ticket.Status.CLOSED)),
        critical=Count('id', filter=Q(priority=Ticket.Priority.CRITICAL)),
        unassigned=Count('id', filter=Q(assigned_to__isnull=True)),
        my_tickets=Count('id', filter=Q(assigned_to__user=request.user)),
    )

    users_count = User.objects.count()
    support_count = User.objects.filter(role=User.Roles.SUPPORT).count()
    latest_tickets = Ticket.objects.select_related(
        'author', 'assigned_to'
    ).order_by('-created')[:5]

    context = {
        **stats,
        'users_count': users_count,
        'support_count': support_count,
        'latest_tickets': latest_tickets,
    }
    return render(request, 'helpdeskside/dashboard_statistic.html', context)


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдено</h1>")
