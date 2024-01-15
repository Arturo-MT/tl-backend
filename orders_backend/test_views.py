from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from orders_backend.models import User, Store, Product, Order, OrderItem
from decimal import Decimal

class UserCreateViewTest(APITestCase):
    def test_create_user(self):
        url = reverse('user-create')
        data = {'email': 'test@example.com', 'username': 'Test User', 'password': 'testpass123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')

class UserDetailViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', username='Normal User', password='testpass123')
        self.superuser = User.objects.create_superuser(email='superuser@example.com', username='Superuser', password='superpass123')

    def test_user_access_own_details(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_access_user_details(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_cannot_access_other_user_details(self):
        other_user = self.superuser
        self.client.force_authenticate(user=self.user)
        url = reverse('user-detail', kwargs={'pk': other_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class StoreViewSetTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', username='User 1', password='testpass123', is_seller=True)
        self.user2 = User.objects.create_user(email='user2@example.com', username='User 2', password='testpass123', is_seller=True)
        self.user3 = User.objects.create_user(email='user3@example.com', username='User 3', password='testpass123', is_seller=False)
        self.superuser = User.objects.create_superuser(email='superuser@example.com', username='Superuser', password='superpass123')
        Store.objects.create(name='Store 1', owner=self.user1, address='123 Main St', email='store1@example.com')
        Store.objects.create(name='Store 2', owner=self.user2, address='456 Elm St', email='store2@example.com')
        Store.objects.create(name='Store 3', owner=self.user2, address='789 Oak St', email='store3@example.com')

    def test_superuser_sees_all_stores(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('store-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_unauthenticated_user_can_see_stores(self):
        response = self.client.get(reverse('store-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_no_sellers_cannot_create_stores(self):
        self.client.force_authenticate(user=self.user3)
        url = reverse('store-list')
        data = {'name': 'Store 4', 'address': '123 Main St', 'email': 'store4@example.com', 'owner': self.user3.pk, 'phone_number': '1234567890'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Store.objects.count(), 3)
    
    def test_sellers_can_create_stores(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('store-list')
        data = {'name': 'Store 4', 'address': '123 Main St', 'email': 'store4@example.com', 'owner': self.user1.pk, 'phone_number': '1234567890'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Store.objects.count(), 4)
    
    def test_sellers_cannot_create_stores_for_other_sellers(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('store-list')
        data = {'name': 'Store 4', 'address': '123 Main St', 'email': 'store5@example.com', 'owner': self.user2.pk, 'phone_number': '1234567890'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Store.objects.count(), 3)
    
    def test_sellers_can_update_own_stores(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('store-detail', kwargs={'pk': Store.objects.get(name='Store 1').pk})
        data = {'name': 'Store 1', 'address': '123 Main St', 'email': 'store1@example.com', 'owner': self.user1.pk, 'phone_number': '1234567890'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Store.objects.get(name='Store 1').phone_number, '1234567890')

    def test_sellers_cannot_update_other_sellers_stores(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('store-detail', kwargs={'pk': Store.objects.get(name='Store 2').pk})
        data = {'name': 'Store 2', 'address': '123 Main St', 'email': 'store2@example.com', 'owner': self.user2.pk, 'phone_number': '1234567890'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(Store.objects.get(name='Store 2').phone_number, '1234567890')
    
    def test_sellers_cannot_delete_other_sellers_stores(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('store-detail', kwargs={'pk': Store.objects.get(name='Store 2').pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Store.objects.count(), 3)
    
    def test_unauthenticated_user_cannot_create_stores(self):
        url = reverse('store-list')
        data = {'name': 'Store 4', 'address': '123 Main St', 'email': 'store3@example.com', 'owner': self.user3.pk, 'phone_number': '1234567890'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Store.objects.count(), 3)

    def test_unauthenticated_user_cannot_update_stores(self):
        url = reverse('store-detail', kwargs={'pk': Store.objects.get(name='Store 1').pk})
        data = {'name': 'Store 1', 'address': '123 Main St', 'email': 'store4@example.com', 'owner': self.user1.pk, 'phone_number': '1234567890'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(Store.objects.get(name='Store 1').phone_number, '1234567890')
    
    def test_unauthenticated_user_cannot_delete_stores(self):
        url = reverse('store-detail', kwargs={'pk': Store.objects.get(name='Store 1').pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Store.objects.count(), 3)
    
    def test_non_seller_users_cannot_create_stores(self):
        self.client.force_authenticate(user=self.user3)
        url = reverse('store-list')
        data = {'name': 'Store 4', 'address': '123 Main St', 'email': 'store3@example.com', 'owner': self.user3.pk, 'phone_number': '1234567890'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Store.objects.count(), 3)
    
    def test_non_seller_users_cannot_update_stores(self):
        self.client.force_authenticate(user=self.user3)
        url = reverse('store-detail', kwargs={'pk': Store.objects.get(name='Store 1').pk})
        data = {'name': 'Store 1', 'address': '123 Main St', 'email': 'store3@example.com', 'owner': self.user1.pk, 'phone_number': '1234567890'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(Store.objects.get(name='Store 1').phone_number, '1234567890')
    
    def test_non_seller_users_cannot_delete_stores(self):
        self.client.force_authenticate(user=self.user3)
        url = reverse('store-detail', kwargs={'pk': Store.objects.get(name='Store 1').pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Store.objects.count(), 3)

class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', username='User 1', password='testpass123')
        self.user2 = User.objects.create_user(email='user2@example.com', username='User 2', password='testpass123')
        self.superuser = User.objects.create_superuser(email='superuser@example.com', username='Superuser', password='superpass123')
        Store.objects.create(name='Store 1', owner=self.user1, address='123 Main St', email='store1@example.com')
        Store.objects.create(name='Store 2', owner=self.user2, address='456 Elm St', email='store2@example.com')
        Product.objects.create(name='Product 1', price=10.00, store=Store.objects.get(name='Store 1'))
        Product.objects.create(name='Product 2', price=20.00, store=Store.objects.get(name='Store 2'))
        Product.objects.create(name='Product 3', price=30.00, store=Store.objects.get(name='Store 2'))
    
    def test_superuser_sees_all_products(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_authenticated_user_cam_see_all_products(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_unauthenticated_user_can_see_products(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_no_store_owner_cannot_create_products(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('product-list')
        data = {'name': 'Product 4', 'price': 40.00, 'store': Store.objects.get(name='Store 1').pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 3)

    def test_store_owner_can_create_products(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('product-list')
        data = {'name': 'Product 4', 'price': 40.00, 'store': Store.objects.get(name='Store 1').pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 4)
    
    def test_store_owner_cannot_create_products_for_other_stores(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('product-list')
        data = {'name': 'Product 4', 'price': 40.00, 'store': Store.objects.get(name='Store 2').pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 3)
    
    def test_store_owner_can_update_own_products(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('product-detail', kwargs={'pk': Product.objects.get(name='Product 1').pk})
        data = {'name': 'Product 1', 'price': 10.00, 'store': Store.objects.get(name='Store 1').pk}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(name='Product 1').price, 10.00)
    
    def test_store_owner_cannot_update_other_store_products(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('product-detail', kwargs={'pk': Product.objects.get(name='Product 2').pk})
        data = {'name': 'Product 2', 'price': 20.00, 'store': Store.objects.get(name='Store 2').pk}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.get(name='Product 2').price, Decimal('20.00'))
    
    def test_store_owner_cannot_delete_other_store_products(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('product-detail', kwargs={'pk': Product.objects.get(name='Product 2').pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 3)
    
    def test_unauthenticated_user_cannot_create_products(self):
        url = reverse('product-list')
        data = {'name': 'Product 4', 'price': 40.00, 'store': Store.objects.get(name='Store 1').pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 3)
    
    def test_unauthenticated_user_cannot_update_products(self):
        url = reverse('product-detail', kwargs={'pk': Product.objects.get(name='Product 1').pk})
        data = {'name': 'Product 1', 'price': 10.00, 'store': Store.objects.get(name='Store 1').pk}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Product.objects.get(name='Product 1').price, 10.00)

    def test_unauthenticated_user_cannot_delete_products(self):
        url = reverse('product-detail', kwargs={'pk': Product.objects.get(name='Product 1').pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Product.objects.count(), 3)
    
    def test_non_seller_users_cannot_create_products(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('product-list')
        data = {'name': 'Product 4', 'price': 40.00, 'store': Store.objects.get(name='Store 1').pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 3)
    
    def test_non_seller_users_cannot_update_products(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('product-detail', kwargs={'pk': Product.objects.get(name='Product 1').pk})
        data = {'name': 'Product 1', 'price': 10.00, 'store': Store.objects.get(name='Store 1').pk}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.get(name='Product 1').price, 10.00)
    
    def test_non_seller_users_cannot_delete_products(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('product-detail', kwargs={'pk': Product.objects.get(name='Product 1').pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 3)

class OrderViewSetTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', username='User 1', password='testpass123')
        self.user2 = User.objects.create_user(email='user2@example.com', username='User 2', password='testpass123')
        self.superuser = User.objects.create_superuser(email='superuser@example.com', username='Superuser', password='superpass123')

        self.store1 = Store.objects.create(name='Store 1', owner=self.user1, address='123 Main St', email='store1@example.com')
        self.store2 = Store.objects.create(name='Store 2', owner=self.user2, address='456 Elm St', email='store2@example.com')

        self.product1 = Product.objects.create(name='Product 1', price=10.00, store=self.store1)
        self.product2 = Product.objects.create(name='Product 2', price=20.00, store=self.store2)
        self.product3 = Product.objects.create(name='Product 3', price=30.00, store=self.store2)

        self.order1 = Order.objects.create(customer=self.user1, store=self.store1)
        self.order2 = Order.objects.create(customer=self.user2, store=self.store2)
        self.order3 = Order.objects.create(customer=self.user2, store=self.store2)
        self.order4 = Order.objects.create(customer_email='user@example.com', store=self.store1)

        OrderItem.objects.create(order=self.order1, product=self.product1, quantity=2)
        OrderItem.objects.create(order=self.order2, product=self.product2, quantity=1)
        OrderItem.objects.create(order=self.order2, product=self.product3, quantity=3)
        OrderItem.objects.create(order=self.order4, product=self.product1, quantity=2)

    def test_user_sees_own_orders(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_user_cannot_see_other_user_orders(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_superuser_sees_all_orders(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
    
    def test_seller_only_sees_orders_from_their_stores(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_seller_cannot_see_orders_from_other_stores(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def non_aunthenticated_user_can_create_orders_giving_email(self):
        url = reverse('order-list')
        data = {'customer_email': 'user@example.com', 'store': self.store1.pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 4)
    
    def non_aunthenticated_user_cannot_create_orders_without_email(self):
        url = reverse('order-list')
        data = {'store': self.store1.pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 3)
    
    def test_authenticated_user_can_create_orders(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('order-list')
        data = {'store': self.store1.pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 5)
    
    def tes_nobody_can_delete_orders(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('order-detail', kwargs={'pk': self.order1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 4)
    
    def test_non_authenticated_user_can_edit_order(self):
        url = reverse('order-detail', kwargs={'pk': self.order4.pk})
        data = {'status': 'X', 'customer_email': 'user@example.com'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class OrderItemViewSetTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', username='User 1', password='testpass123')
        self.user2 = User.objects.create_user(email='user2@example.com', username='User 2', password='testpass123')
        self.superuser = User.objects.create_superuser(email='superuser@example.com', username='Superuser', password='superpass123')

        self.store1 = Store.objects.create(name='Store 1', owner=self.user1, address='123 Main St', email='store1@example.com')
        self.store2 = Store.objects.create(name='Store 2', owner=self.user2, address='456 Elm St', email='store2@example.com')

        self.product1 = Product.objects.create(name='Product 1', price=10.00, store=self.store1)
        self.product2 = Product.objects.create(name='Product 2', price=20.00, store=self.store2)
        self.product3 = Product.objects.create(name='Product 3', price=30.00, store=self.store2)

        self.order1 = Order.objects.create(customer=self.user1, store=self.store1)
        self.order2 = Order.objects.create(customer=self.user2, store=self.store2)
        self.order3 = Order.objects.create(customer=self.user2, store=self.store2)
        self.order4 = Order.objects.create(customer_email='anonuser@example.com', store=self.store1)

        OrderItem.objects.create(order=self.order1, product=self.product1, quantity=2)
        OrderItem.objects.create(order=self.order2, product=self.product2, quantity=1)
        OrderItem.objects.create(order=self.order2, product=self.product3, quantity=3)
    
    def test_user_sees_own_order_items(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('orderitem-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_user_cannot_see_other_user_order_items(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('orderitem-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_superuser_sees_all_order_items(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('orderitem-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_seller_only_sees_order_items_from_their_stores(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('orderitem-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_seller_cannot_see_order_items_from_other_stores(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('orderitem-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_non_aunthenticated_user_can_create_order_items_to_an_order_with_customer_email(self):
        url = reverse('orderitem-list')
        data = {'order': self.order4.pk, 'product': self.product1.pk, 'quantity': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrderItem.objects.count(), 4)
    