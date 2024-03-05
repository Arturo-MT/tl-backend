from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User

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