from django.test import TestCase
from users.models import User
from django.db.utils import IntegrityError

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='Test User',
            phone_number='1234567890',
            password='testpassword'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'Test User')
        self.assertEqual(self.user.phone_number, '1234567890')
        self.assertTrue(self.user.check_password('testpassword'))
        self.assertFalse(self.user.is_superuser)
        self.assertFalse(self.user.is_seller)
        self.assertFalse(self.user.is_staff)
        self.assertEqual(self.user.owned_stores.count(), 0)

    def test_unique_email(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='test@example.com',
                username='Another User',
                password='testpassword'
            )