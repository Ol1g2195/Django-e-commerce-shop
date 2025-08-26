from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from cart.models import Cart, CartItem

# Create your views here.

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def create_order(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]
    if not cart.items.exists():
        messages.error(request, 'Ваша корзина пуста')
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        # Создаем заказ
        order = Order.objects.create(
            user=request.user,
            status='pending',
            total_amount=cart.get_total_price()
        )

        # Переносим товары из корзины в заказ
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        # Очищаем корзину
        cart.items.all().delete()

        messages.success(request, 'Заказ успешно создан!')
        return redirect('orders:order_detail', order_id=order.id)

    return render(request, 'orders/create_order.html', {'cart': cart})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
