from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, LogoutView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from helpdesk import settings
from .decorators import role_required
from .forms import LoginFormUsers, RegisterFormUsers, ProfileUserForm, PasswordChangeForm
from .models import User


class LoginUser(LoginView):
    form_class = LoginFormUsers
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}
    success_url = reverse_lazy('home')


class RegisterUser(CreateView):
    form_class = RegisterFormUsers
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('helpdeskside:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(
            self.request,
            self.object,
            backend='django.contrib.auth.backends.ModelBackend',
        )
        return response


class ProfilUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': 'Профиль пользовителя',
                     'default_image': settings.DEFAULT_USER_IMAGE}

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserPasswordChange(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


@login_required
def post_login_redirect(request):
    role = request.user.role

    if role == User.Roles.ADMIN:
        return redirect('users:admin_dashboard')
    elif role == User.Roles.SUPPORT:
        return redirect('users:support_dashboard')
    elif role == User.Roles.CLIENT:
        return redirect('users:client_dashboard')
    else:
        return redirect('users:login')


@login_required
@role_required(User.Roles.ADMIN)
def admin_dashboard(request):
    return render(request, 'users/admin_dashboard.html')


@login_required
@role_required(User.Roles.SUPPORT, User.Roles.ADMIN)  # админ тоже может видеть
def support_dashboard(request):
    return render(request, 'users/support_dashboard.html')


@login_required
@role_required(User.Roles.CLIENT)
def client_dashboard(request):
    return render(request, 'users/client_dashboard.html')
