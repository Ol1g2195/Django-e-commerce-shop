from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('send-message/', views.send_message, name='send_message'),
    path('messages/<int:chat_room_id>/', views.get_messages, name='get_messages'),
    path('admin/', views.admin_chat_list, name='admin_chat_list'),
    path('admin/<int:chat_room_id>/', views.admin_chat_detail, name='admin_chat_detail'),
    path('admin/<int:chat_room_id>/send/', views.admin_send_message, name='admin_send_message'),
]
