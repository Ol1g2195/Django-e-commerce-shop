from django.db import models
from django.conf import settings
from django.utils import timezone


class ChatRoom(models.Model):
    """Модель для чат-комнаты"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    last_message_at = models.DateTimeField(auto_now=True, verbose_name="Последнее сообщение")

    class Meta:
        verbose_name = "Чат-комната"
        verbose_name_plural = "Чат-комнаты"
        ordering = ['-last_message_at']

    def __str__(self):
        return f"Чат с {self.user.username}"


class Message(models.Model):
    """Модель для сообщений в чате"""
    MESSAGE_TYPES = [
        ('user', 'Пользователь'),
        ('bot', 'Бот'),
        ('admin', 'Администратор'),
    ]

    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name="Чат-комната")
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, verbose_name="Тип сообщения")
    content = models.TextField(verbose_name="Содержание")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время отправки")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.get_message_type_display()}: {self.content[:50]}..."


class BotResponse(models.Model):
    """Модель для ответов бота на ключевые слова"""
    keyword = models.CharField(max_length=100, verbose_name="Ключевое слово")
    response = models.TextField(verbose_name="Ответ бота")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Ответ бота"
        verbose_name_plural = "Ответы бота"

    def __str__(self):
        return f"{self.keyword} -> {self.response[:50]}..."