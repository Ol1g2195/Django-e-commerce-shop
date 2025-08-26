from django.core.management.base import BaseCommand
from users.models import User, UserProfile

class Command(BaseCommand):
    help = 'Создает профили для пользователей, у которых их нет'

    def handle(self, *args, **options):
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            try:
                user.profile
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(user=user)
                created_count += 1
                self.stdout.write(f'Создан профиль для пользователя {user.username}')
        
        self.stdout.write(self.style.SUCCESS(f'Успешно создано {created_count} профилей')) 