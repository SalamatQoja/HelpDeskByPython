from django.contrib.auth import  login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from helpdesk import settings
from .decorators import role_required
from .forms import LoginFormUsers, RegisterFormUsers, ProfileUserForm, PasswordChangeForm, AdminSetPasswordForm
from .models import User
from django.contrib import messages


class LoginUser(LoginView):
    form_class = LoginFormUsers
    template_name = 'users/login.html'
    extra_context = {'title': 'Вход'}
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


@login_required
@role_required('admin')
def users_list(request):
    all_users = User.objects.all().order_by('username')
    paginator = Paginator(all_users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'users/users_list.html', {'page_obj': page_obj})


@login_required
@role_required('admin')
def change_user_password(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = AdminSetPasswordForm(target_user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Пароль пользователя {target_user.username} изменён'
            )
            # return redirect('users:users_list')
    else:
        form = AdminSetPasswordForm(target_user)

    return render(request, 'users/change_users_password.html', {
        'form': form,
        'target_user': target_user,
    })


@login_required
@role_required('admin')
def block_user(request, user_id):
    target_user_block = get_object_or_404(User, pk=user_id)

    if target_user_block == request.user:
        messages.error(request, 'Нельзя заблокировать самого себя')
        return redirect('users:users_list')

    # защита: обычный админ суперпользователди блок кыла алмайды
    if target_user_block.is_superuser and not request.user.is_superuser:
        messages.error(request, 'Только суперпользователь может блокировать суперпользователя')
        return redirect('users:users_list')

    if request.method == 'POST':
        target_user_block.is_active = False
        target_user_block.save(update_fields=['is_active'])

        # разлогиниваем все активные сессии target
        # _kill_user_sessions(target)

        messages.success(request, f'Пользователь {target_user_block.username} заблокирован')
        # return redirect('users:users_list')

    return render(request, 'users/block_user_confirm.html', {
        'target_user': target_user_block,
    })


@login_required
@role_required('admin')
def unblock_user(request, user_id):
    target_user_unblock = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        target_user_unblock.is_active = True
        target_user_unblock.save(update_fields=['is_active'])
        messages.success(request, f'Пользователь {target_user_unblock.username} разблокирован')
        # return redirect('users:users_list')

    return render(request, 'users/unblock_user_confirm.html', {
        'target_user': target_user_unblock,
    })


# def _kill_user_sessions(user):
#     """Удаляет все активные сессии пользователя — мгновенный логаут."""
#     sessions = Session.objects.filter(expire_date__gte=timezone.now())
#     for s in sessions:
#         data = s.get_decoded()
#         if data.get('_auth_user_id') == str(user.pk):
#             s.delete()
