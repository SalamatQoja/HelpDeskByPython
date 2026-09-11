from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from .forms import TicketForm, CommentForm
from .models import Ticket, Comment


# from .forms import RegisterForm


def index(request):
    return render(request, "helpdeskside/index.html", {"title": "Главная"})


def is_employee(user):
    return hasattr(user, 'employee_profile')


@login_required
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
def my_tickets(request):
    tickets = Ticket.objects.filter(author=request.user)
    return render(request, 'helpdeskside/my_tickets.html', {'tickets': tickets})


@login_required
def ticket_detail(request, pk):

    ticket = get_object_or_404(Ticket, pk=pk, author=request.user)
    comments = ticket.comments.all()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            return redirect('helpdeskside:ticket_detail', pk=pk)
    else:
        comment_form = CommentForm()

    return render(request, 'helpdeskside/ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
    })


@login_required
def close_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, author=request.user)
    ticket.status = Ticket.Status.CLOSED
    ticket.save()
    return redirect('helpdeskside:ticket_detail', pk=pk)



@user_passes_test(is_employee)
def all_tickets(request):
    tickets = Ticket.objects.all()
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'helpdeskside/all_tickets.html', {'page_obj': page_obj})


@user_passes_test(is_employee)
def change_status(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        ticket.status = request.POST.get('status')
        ticket.save()
        return redirect('helpdeskside:ticket_detail', pk=pk)
    return render(request, 'helpdeskside/change_status.html', {'ticket': ticket})


@user_passes_test(is_employee)
def assign_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        ticket.assigned_to_id = employee_id
        ticket.save()
        return redirect('helpdeskside:ticket_detail', pk=pk)
    return render(request, 'helpdeskside/assign_ticket.html', {'ticket': ticket})


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдено</h1>")
