from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from orders_backend.models import User, Store, Product

class UserCreateViewTest(APITestCase):
    def test_create_user(self):
        url = reverse('user-create')
        data = {'email': 'test@example.com', 'name': 'Test User', 'password': 'testpass123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')

class UserDetailViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', name='Normal User', password='testpass123')
        self.superuser = User.objects.create_superuser(email='superuser@example.com', name='Superuser', password='superpass123')

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
        self.user1 = User.objects.create_user(email='user1@example.com', name='User 1', password='testpass123')
        self.user2 = User.objects.create_user(email='user2@example.com', name='User 2', password='testpass123')
        Store.objects.create(name='Store 1', owner=self.user1, address='123 Main St', email='store1@example.com')
        Store.objects.create(name='Store 2', owner=self.user2, address='456 Elm St', email='store2@example.com')

    def test_user_sees_own_stores(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('store-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_superuser_sees_all_stores(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('store-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', name='User 1', password='testpass123')
        self.user2 = User.objects.create_user(email='user2@example.com', name='User 2', password='testpass123')
        self.superuser = User.objects.create_superuser(email='superuser@example.com', name='Superuser', password='superpass123')
        Store.objects.create(name='Store 1', owner=self.user1, address='123 Main St', email='store1@example.com')
        Store.objects.create(name='Store 2', owner=self.user2, address='456 Elm St', email='store2@example.com')
        Product.objects.create(name='Product 1', price=10.00, store=Store.objects.get(name='Store 1'))
        Product.objects.create(name='Product 2', price=20.00, store=Store.objects.get(name='Store 2'))
    
    def test_user_sees_own_products(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_superuser_sees_all_products(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)