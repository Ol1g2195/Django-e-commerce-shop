from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
import re
from .models import ChatRoom, Message, BotResponse
from .utils import generate_bot_response


@login_required
def chat_view(request):
    """Основная страница чата"""
    # Получаем или создаем чат-комнату для пользователя
    chat_room, created = ChatRoom.objects.get_or_create(
        user=request.user,
        defaults={'is_active': True}
    )
    
    # Получаем последние сообщения
    messages = chat_room.messages.all()[:50]
    
    return render(request, 'chat/chat.html', {
        'chat_room': chat_room,
        'messages': messages,
    })


@login_required
@require_POST
@csrf_exempt
def send_message(request):
    """Отправка сообщения пользователем"""
    try:
        data = json.loads(request.body)
        content = data.get('message', '').strip()
        
        if not content:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)
        
        # Получаем чат-комнату пользователя
        chat_room, created = ChatRoom.objects.get_or_create(
            user=request.user,
            defaults={'is_active': True}
        )
        
        # Создаем сообщение пользователя
        user_message = Message.objects.create(
            chat_room=chat_room,
            message_type='user',
            content=content
        )
        
        # Генерируем ответ бота
        bot_response = generate_bot_response(content)
        
        # Создаем ответ бота
        bot_message = Message.objects.create(
            chat_room=chat_room,
            message_type='bot',
            content=bot_response
        )
        
        # Обновляем время последнего сообщения
        chat_room.last_message_at = timezone.now()
        chat_room.save()
        
        return JsonResponse({
            'success': True,
            'user_message': {
                'id': user_message.id,
                'content': user_message.content,
                'timestamp': user_message.timestamp.strftime('%H:%M'),
                'type': 'user'
            },
            'bot_message': {
                'id': bot_message.id,
                'content': bot_message.content,
                'timestamp': bot_message.timestamp.strftime('%H:%M'),
                'type': 'bot'
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_messages(request, chat_room_id):
    """Получение сообщений чата"""
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id, user=request.user)
    messages = chat_room.messages.all()
    
    messages_data = []
    for message in messages:
        messages_data.append({
            'id': message.id,
            'content': message.content,
            'type': message.message_type,
            'timestamp': message.timestamp.strftime('%H:%M'),
            'is_read': message.is_read
        })
    
    return JsonResponse({'messages': messages_data})


@login_required
def admin_chat_list(request):
    """Список всех чатов для администратора"""
    if not request.user.is_staff:
        return redirect('chat')
    
    chat_rooms = ChatRoom.objects.filter(is_active=True).order_by('-last_message_at')
    
    return render(request, 'chat/admin_chat_list.html', {
        'chat_rooms': chat_rooms,
    })


@login_required
def admin_chat_detail(request, chat_room_id):
    """Детальный просмотр чата для администратора"""
    if not request.user.is_staff:
        return redirect('chat')
    
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    messages = chat_room.messages.all()
    
    return render(request, 'chat/admin_chat_detail.html', {
        'chat_room': chat_room,
        'messages': messages,
    })


@login_required
@require_POST
@csrf_exempt
def admin_send_message(request, chat_room_id):
    """Отправка сообщения администратором"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)
    
    try:
        data = json.loads(request.body)
        content = data.get('message', '').strip()
        
        if not content:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)
        
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        
        # Создаем сообщение администратора
        admin_message = Message.objects.create(
            chat_room=chat_room,
            message_type='admin',
            content=content
        )
        
        # Обновляем время последнего сообщения
        chat_room.last_message_at = timezone.now()
        chat_room.save()
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': admin_message.id,
                'content': admin_message.content,
                'timestamp': admin_message.timestamp.strftime('%H:%M'),
                'type': 'admin'
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)