from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem
from products.models import Product
from orders.models import Order, OrderItem
from django.utils import timezone

# Create your views here.

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(
        user=request.user,
        defaults={
            'created_at': timezone.now(),
            'updated_at': timezone.now(),
        }
    )
    cart_items = cart.items.select_related('product').all()
    total = sum(item.total_price for item in cart_items)
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def add_to_cart(request, product_id):
    cart, _ = Cart.objects.get_or_create(
        user=request.user,
        defaults={
            'created_at': timezone.now(),
            'updated_at': timezone.now(),
        }
    )
    product = get_object_or_404(Product, id=product_id)
    if product.stock < 1:
        messages.error(request, f'Товар {product.name} отсутствует на складе')
        return redirect('cart')
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            'quantity': 1,
            'created_at': timezone.now(),
            'updated_at': timezone.now(),
        }
    )
    if not created:
        if cart_item.quantity + 1 > product.stock:
            messages.error(request, f'Нельзя добавить больше товара, чем есть на складе ({product.stock})')
        else:
            cart_item.quantity += 1
            cart_item.updated_at = timezone.now()
            cart_item.save()
            messages.success(request, f'Товар {product.name} добавлен в корзину')
    else:
        messages.success(request, f'Товар {product.name} добавлен в корзину')
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart, _ = Cart.objects.get_or_create(
        user=request.user,
        defaults={
            'created_at': timezone.now(),
            'updated_at': timezone.now(),
        }
    )
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    messages.success(request, 'Товар удален из корзины')
    return redirect('cart')

@login_required
def update_cart(request, item_id):
    cart, _ = Cart.objects.get_or_create(
        user=request.user,
        defaults={
            'created_at': timezone.now(),
            'updated_at': timezone.now(),
        }
    )
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        messages.error(request, 'Некорректное количество')
        return redirect('cart')
    if quantity > 0:
        if quantity > cart_item.product.stock:
            messages.error(request, f'На складе только {cart_item.product.stock} шт.')
        else:
            cart_item.quantity = quantity
            cart_item.updated_at = timezone.now()
            cart_item.save()
            messages.success(request, 'Количество товара обновлено')
    else:
        cart_item.delete()
        messages.success(request, 'Товар удален из корзины')
    return redirect('cart')

@login_required
def place_order(request):
    cart, _ = Cart.objects.get_or_create(
        user=request.user,
        defaults={
            'created_at': timezone.now(),
            'updated_at': timezone.now(),
        }
    )
    cart_items = cart.items.select_related('product').all()
    if not cart_items:
        messages.error(request, 'Ваша корзина пуста!')
        return redirect('cart')
    # Проверка наличия на складе
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f'Недостаточно товара "{item.product.name}" на складе.')
            return redirect('cart')
    # Создание заказа
    order = Order.objects.create(
        user=request.user,
        status='pending',
        created_at=timezone.now()
    )
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
        # Списание товара со склада
        item.product.stock -= item.quantity
        item.product.save()
    # Очистка корзины
    cart.items.all().delete()
    messages.success(request, 'Заказ успешно оформлен!')
    return redirect('cart')
