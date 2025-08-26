from django.core.management.base import BaseCommand
from django.db import connections
from products.models import Category, Product
from reviews.models import Review
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Import data from old MySQL database'

    def handle(self, *args, **options):
        # Получаем соединение со старой базой данных
        with connections['old_db'].cursor() as cursor:
            # Импорт категорий
            cursor.execute("SELECT * FROM categories")
            categories = cursor.fetchall()
            for cat in categories:
                Category.objects.get_or_create(
                    id=cat[0],
                    defaults={
                        'name': cat[1],
                        'description': cat[2],
                        'created_at': cat[3]
                    }
                )
            self.stdout.write(self.style.SUCCESS('Categories imported successfully'))

            # Импорт пользователей
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            for user in users:
                is_staff = user[4] == 'admin'
                is_superuser = user[4] == 'admin'
                User.objects.get_or_create(
                    id=user[0],
                    defaults={
                        'username': user[1],
                        'email': user[2],
                        'password': make_password(user[3]),
                        'is_staff': is_staff,
                        'is_superuser': is_superuser,
                        'date_joined': user[5],
                        # profile_image_url: user[6] — если нужно, можно добавить в профиль
                    }
                )
            self.stdout.write(self.style.SUCCESS('Users imported successfully'))

            # Импорт товаров
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
            for prod in products:
                Product.objects.update_or_create(
                    id=prod[0],
                    defaults={
                        'name': prod[1],
                        'description': prod[2],
                        'price': prod[3],
                        'image_url': prod[4],
                        'category_id': prod[5],
                        'stock': prod[6],
                        'created_at': prod[7],
                    }
                )
            self.stdout.write(self.style.SUCCESS('Products imported successfully'))

            # Импорт отзывов
            cursor.execute("SELECT * FROM reviews")
            reviews = cursor.fetchall()
            for review in reviews:
                user_id = review[1]
                product_id = review[2]
                try:
                    user_obj = User.objects.get(id=user_id)
                    product_obj = Product.objects.get(id=product_id)
                except User.DoesNotExist:
                    continue
                except Product.DoesNotExist:
                    continue
                Review.objects.update_or_create(
                    id=review[0],
                    defaults={
                        'product': product_obj,
                        'user': user_obj,
                        'rating': review[3],
                        'comment': review[4],
                        'created_at': review[5]
                    }
                )
            self.stdout.write(self.style.SUCCESS('Reviews imported successfully'))

            # Импорт корзин
            cursor.execute("SELECT * FROM cart")
            carts = cursor.fetchall()
            from cart.models import Cart
            for cart in carts:
                Cart.objects.get_or_create(
                    id=cart[0],
                    defaults={
                        'user_id': cart[1],
                        'created_at': cart[2]
                    }
                )
            self.stdout.write(self.style.SUCCESS('Carts imported successfully'))

            # Импорт позиций корзины
            cursor.execute("SELECT * FROM cart_items")
            cart_items = cursor.fetchall()
            from cart.models import CartItem
            for item in cart_items:
                CartItem.objects.get_or_create(
                    id=item[0],
                    defaults={
                        'cart_id': item[1],
                        'product_id': item[2],
                        'quantity': item[3],
                        'price': item[4]
                    }
                )
            self.stdout.write(self.style.SUCCESS('Cart items imported successfully'))

            # Импорт заказов
            cursor.execute("SELECT * FROM orders")
            orders = cursor.fetchall()
            from orders.models import Order
            for order in orders:
                Order.objects.get_or_create(
                    id=order[0],
                    defaults={
                        'user_id': order[1],
                        'status': order[2],
                        'created_at': order[3]
                    }
                )
            self.stdout.write(self.style.SUCCESS('Orders imported successfully'))

            # Импорт позиций заказа
            cursor.execute("SELECT * FROM order_items")
            order_items = cursor.fetchall()
            from orders.models import OrderItem
            for item in order_items:
                OrderItem.objects.get_or_create(
                    id=item[0],
                    defaults={
                        'order_id': item[1],
                        'product_id': item[2],
                        'quantity': item[3],
                        'price': item[4]
                    }
                )
            self.stdout.write(self.style.SUCCESS('Order items imported successfully')) 