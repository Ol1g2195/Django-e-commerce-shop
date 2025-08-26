from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from products.models import Product
from django.utils import timezone

# Create your views here.

@login_required
def review_list(request):
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'reviews/review_list.html', {'reviews': reviews})

@login_required
def create_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        
        if not rating or not text:
            messages.error(request, 'Пожалуйста, заполните все поля')
            return redirect('product_detail', pk=product_id)
        
        # Проверяем, существует ли уже отзыв от этого пользователя
        review, created = Review.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={
                'rating': rating,
                'text': text,
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }
        )
        
        if not created:
            # Если отзыв уже существует, обновляем его
            review.rating = rating
            review.text = text
            review.updated_at = timezone.now()
            review.save()
            messages.success(request, 'Отзыв успешно обновлен')
        else:
            messages.success(request, 'Отзыв успешно добавлен')
        
        return redirect('product_detail', pk=product_id)
    
    return render(request, 'reviews/create_review.html', {'product': product})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        
        if not rating or not text:
            messages.error(request, 'Пожалуйста, заполните все поля')
            return redirect('edit_review', review_id=review_id)
        
        review.rating = rating
        review.text = text
        review.save()
        
        messages.success(request, 'Отзыв успешно обновлен')
        return redirect('product_detail', pk=review.product.id)
    
    return render(request, 'reviews/edit_review.html', {'review': review})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_id = review.product.id
    review.delete()
    messages.success(request, 'Отзыв успешно удален')
    return redirect('product_detail', pk=product_id)
