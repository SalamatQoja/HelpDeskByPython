from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
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

    # def get_success_url(self):
    #     user = self.request.user
    #     if user.role == User.Roles.ADMIN:
    #         return reverse_lazy('users:admin_dashboard')
    #     elif user.role == User.Roles.SUPPORT:
    #         return reverse_lazy('users:support_dashboard')
    #     return reverse_lazy('users:client_dashboard')

    #
    # def get_success_url(self):
    #     return   reverse_lazy("home")


class RegisterUser(CreateView):
    form_class = RegisterFormUsers
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
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


User = get_user_model()


@login_required
@role_required('admin')
def manage_users(request):
    users = User.objects.exclude(id=request.user.id).order_by('username')
    return render(request, 'users/manage_users.html', {'users': users})


@login_required
@role_required('admin')
def change_user_role(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    if target_user == request.user:
        return redirect('users:manage_users')

    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in User.Roles.values:
            target_user.role = new_role
            target_user.save(update_fields=['role'])

    return redirect('users:manage_users')

