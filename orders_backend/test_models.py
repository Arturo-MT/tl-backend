from django.test import TestCase
from .models import User, Store, Product, Order, OrderItem, Payment
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            phone_number='1234567890',
            password='testpassword'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.name, 'Test User')
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
                name='Another User',
                password='testpassword'
            )

class StoreModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', address='123 Main St', phone_number='1234567890', email='test@store.com')
        
    def test_store_name(self):
        expected_name = 'Test Store'
        self.assertEqual(self.store.name, expected_name)

    def test_product_name(self):
        product = Product.objects.create(name='Test Product', price=10.0, store=self.store)
        expected_name = 'Test Product'
        self.assertEqual(product.name, expected_name)

    def test_product_price(self):
        product = Product.objects.create(name='Test Product', price=10.0, store=self.store)
        expected_price = 10.0
        self.assertEqual(product.price, expected_price)

    def test_product_store(self):
        product = Product.objects.create(name='Test Product', price=10.0, store=self.store)
        self.assertEqual(product.store, self.store)
    
    def test_store_address(self):
        address = '123 Main St'
        self.assertEqual(self.store.address, address)
    
    def test_store_phone_number(self):
        phone_number = '1234567890'
        self.assertEqual(self.store.phone_number, phone_number)
    
    def test_store_email(self):
        email = 'test@store.com'
        self.assertEqual(self.store.email, email)
    
    def test_store_products(self):
        product = Product.objects.create(name='Test Product', price=10.0, store=self.store)
        self.assertEqual(self.store.products.count(), 1)
        self.assertEqual(self.store.products.first(), product)

    def test_product_relation(self):
        product = Product.objects.create(name='Test Product', price=10.0, store=self.store)
        self.assertTrue(product in self.store.products.all())

class ProductModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', address='Test Address', phone_number='1234567890', email='test@store.com')
        self.product = Product.objects.create(name='Test Product', description='Test Description', price=10.0, available=True, store=self.store)

    def test_name_label(self):
        field_label = self.product._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_description_label(self):
        field_label = self.product._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')

    def test_price_label(self):
        field_label = self.product._meta.get_field('price').verbose_name
        self.assertEqual(field_label, 'price')

    def test_available_label(self):
        field_label = self.product._meta.get_field('available').verbose_name
        self.assertEqual(field_label, 'available')

    def test_store_relation(self):
        self.assertEqual(self.product.store, self.store)

    def test_negative_price(self):
        with self.assertRaises(ValidationError):
            product = Product(
                name='Invalid Product',
                price=-10.0,
                store=self.store
            )
            product.full_clean()

class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', name='testuser', password='12345')
        self.store = Store.objects.create(name='Test Store', address='Test Address', phone_number='1234567890', email='test@store.com')
        self.order = Order.objects.create(customer=self.user, status='R', store=self.store)

    def test_customer_relation(self):
        self.assertEqual(self.order.customer.name, 'testuser')

    def test_status_label(self):
        field_label = self.order._meta.get_field('status').verbose_name
        self.assertEqual(field_label, 'status')

    def test_store_relation(self):
        self.assertEqual(self.order.store, self.store)

class OrderItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', name='testuser', password='testpassword')
        self.store = Store.objects.create(name='Test Store', address='123 Main St', phone_number='1234567890', email='test@store.com')
        self.product = Product.objects.create(name='Test Product', description='Test Description', price=10.0, available=True, store=self.store)
        self.order = Order.objects.create(customer=self.user, status='R', store=self.store)
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2, description='Test Description')

    def test_quantity(self):
        order_item = self.order_item
        self.assertEqual(order_item.quantity, 2)

    def test_description(self):
        order_item = self.order_item
        self.assertEqual(order_item.description, 'Test Description')

    def test_order_relation(self):
        order_item = self.order_item
        self.assertEqual(order_item.order, self.order)

    def test_product_relation(self):
        order_item = self.order_item
        self.assertEqual(order_item.product, self.product)

""" class PaymentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Store.objects.create(name='Test Store', address='Test Address', phone_number='1234567890', email='test@store.com')
        Order.objects.create(customer_id=1, status='R')
        Payment.objects.create(order_id=1, amount=100.0, store_id=1)

    def test_order_relation(self):
        payment = Payment.objects.get(id=1)
        self.assertEquals(payment.order.id, 1)

    def test_amount(self):
        payment = Payment.objects.get(id=1)
        self.assertEquals(payment.amount, 100.0)

    def test_store_relation(self):
        payment = Payment.objects.get(id=1)
        self.assertEquals(payment.store.id, 1) """