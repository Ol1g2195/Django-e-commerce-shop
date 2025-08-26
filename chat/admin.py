from django.contrib import admin
from .models import ChatRoom, Message, BotResponse


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'last_message_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'last_message_at']
    ordering = ['-last_message_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['chat_room', 'message_type', 'content_short', 'timestamp', 'is_read']
    list_filter = ['message_type', 'is_read', 'timestamp']
    search_fields = ['content', 'chat_room__user__username']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = 'Содержание'


@admin.register(BotResponse)
class BotResponseAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'response_short', 'is_active']
    list_filter = ['is_active']
    search_fields = ['keyword', 'response']
    ordering = ['keyword']
    
    def response_short(self, obj):
        return obj.response[:50] + '...' if len(obj.response) > 50 else obj.response
    response_short.short_description = 'Ответ'