from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserUpdateForm
from orders.models import Order, OrderItem
from django.contrib.auth import get_user_model
from reviews.models import Review
import os

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('users:profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'users/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('index')

@login_required
def profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        profile_image = request.FILES.get('profile_image')
        
        # Проверяем, не занято ли имя пользователя
        if username != request.user.username and get_user_model().objects.filter(username=username).exists():
            messages.error(request, 'Это имя пользователя уже занято')
        else:
            request.user.username = username
            request.user.email = email
            request.user.save()
            
            if profile_image:
                # Удаляем старое изображение, если оно есть
                if request.user.profile.profile_image:
                    old_image = request.user.profile.profile_image
                    if hasattr(old_image, 'path') and os.path.exists(old_image.path):
                        os.remove(old_image.path)
                request.user.profile.profile_image = profile_image
                request.user.profile.save()
            
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('users:profile')
    
    # Получаем заказы и отзывы пользователя
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    # Проверяем наличие профиля
    user_profile = getattr(request.user, 'profile', None)
    return render(request, 'users/profile.html', {
        'orders': orders,
        'reviews': reviews,
        'user_profile': user_profile,
        'profile_image': request.user.profile.profile_image if hasattr(request.user, 'profile') else None,
    })

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related('items__product')
    return render(request, 'users/my_orders.html', {'orders': orders})
