from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from django.db.models import Avg, Count, Q
from django.contrib import messages
from reviews.models import Review
from orders.models import OrderItem
from django.contrib.auth.decorators import login_required
from django.template.defaulttags import register

def index(request):
    products = Product.objects.all().annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    categories = Category.objects.all()
    sort_options = [
        ('price', 'цене'),
        ('rating', 'рейтингу'),
        ('date', 'дате'),
        ('reviews', 'отзывам'),
    ]

    # Фильтрация
    search = request.GET.get('search', '')
    if search:
        products = products.filter(name__icontains=search)
    category = request.GET.get('category')
    if category:
        products = products.filter(category_id=category)
    min_price = request.GET.get('min_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    max_price = request.GET.get('max_price')
    if max_price:
        products = products.filter(price__lte=max_price)
    rating = request.GET.get('rating')
    if rating:
        products = products.filter(average_rating__gte=4)

    # Сортировка с направлением
    sort = request.GET.get('sort')
    direction = request.GET.get('direction', 'desc')
    sort_map = {
        'price': 'price',
        'rating': 'average_rating',
        'date': 'created_at',
        'reviews': 'review_count',
    }
    if sort in sort_map:
        field = sort_map[sort]
        if direction == 'asc':
            products = products.order_by(field)
        else:
            products = products.order_by(f'-{field}')
    else:
        products = products.order_by('-created_at')

    return render(request, 'products/index.html', {
        'products': products,
        'categories': categories,
        'current_sort': sort,
        'current_direction': direction,
        'sort_options': sort_options,
    })

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    reviews = product.reviews.all().order_by('-created_at')
    
    # Проверяем, является ли текущий пользователь покупателем
    is_buyer = False
    if request.user.is_authenticated:
        is_buyer = OrderItem.objects.filter(
            order__user=request.user,
            product=product
        ).exists()
    
    # Создаем словарь с информацией о покупателях для отзывов
    review_buyers = {}
    for review in reviews:
        review_buyers[review.id] = OrderItem.objects.filter(
            order__user=review.user,
            product=product
        ).exists()
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'is_buyer': is_buyer,
        'review_buyers': review_buyers,
    })
