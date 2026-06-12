from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import User, ActivityLog
from .forms import LoginForm, UserCreateForm, UserUpdateForm
from .decorators import manager_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user:
            login(request, user)
            ActivityLog.objects.create(user=user, action='login', description=f"{user.full_name} logged in", ip_address=request.META.get('REMOTE_ADDR'))
            return redirect(request.GET.get('next', 'dashboard:index'))
        messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    ActivityLog.objects.create(user=request.user, action='logout', description=f"{request.user.full_name} logged out", ip_address=request.META.get('REMOTE_ADDR'))
    logout(request)
    messages.success(request, 'You have been signed out.')
    return redirect('accounts:login')


@login_required
@manager_required
def user_list(request):
    search = request.GET.get('search', '')
    role = request.GET.get('role', '')
    users = User.objects.all().order_by('-date_joined')
    if search:
        users = users.filter(username__icontains=search) | users.filter(first_name__icontains=search) | users.filter(last_name__icontains=search)
    if role:
        users = users.filter(role=role)
    page = Paginator(users, 15).get_page(request.GET.get('page'))
    return render(request, 'accounts/user_list.html', {'users': page, 'search': search, 'role': role})


@login_required
@manager_required
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        ActivityLog.objects.create(user=request.user, action='user_created', description=f"Created user: {user.full_name} ({user.role})")
        messages.success(request, f'User "{user.full_name}" created.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Add User', 'action': 'Create'})


@login_required
@manager_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserUpdateForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        ActivityLog.objects.create(user=request.user, action='user_updated', description=f"Updated user: {user.full_name}")
        messages.success(request, f'User "{user.full_name}" updated.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Edit User', 'action': 'Update', 'edit_user': user})


@login_required
@manager_required
def user_toggle(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot deactivate yourself.')
        return redirect('accounts:user_list')
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f'User "{user.full_name}" {"activated" if user.is_active else "deactivated"}.')
    return redirect('accounts:user_list')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'profile_user': request.user})


@login_required
@manager_required
def activity_log(request):
    logs = ActivityLog.objects.select_related('user').all()
    page = Paginator(logs, 20).get_page(request.GET.get('page'))
    return render(request, 'accounts/activity_log.html', {'logs': page})
