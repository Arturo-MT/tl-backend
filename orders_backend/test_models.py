from django.test import TestCase
from .models import User, Store, Product, Order, OrderItem, Payment

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

class StoreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Product.objects.create(name='Test Product', price=10.0)
        Store.objects.create(name='Test Store', address='Test Address', phone_number='1234567890', email='test@store.com')

    def test_name_label(self):
        store = Store.objects.get(id=1)
        field_label = store._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_address_label(self):
        store = Store.objects.get(id=1)
        field_label = store._meta.get_field('address').verbose_name
        self.assertEquals(field_label, 'address')

    def test_phone_number_label(self):
        store = Store.objects.get(id=1)
        field_label = store._meta.get_field('phone_number').verbose_name
        self.assertEquals(field_label, 'phone number')

    def test_email_label(self):
        store = Store.objects.get(id=1)
        field_label = store._meta.get_field('email').verbose_name
        self.assertEquals(field_label, 'email')

    def test_name_max_length(self):
        store = Store.objects.get(id=1)
        max_length = store._meta.get_field('name').max_length
        self.assertEquals(max_length, 50)

    def test_str_method(self):
        store = Store.objects.get(id=1)
        expected_object_name = f'{store.name}'
        self.assertEquals(expected_object_name, str(store))

    def test_product_relation(self):
        store = Store.objects.get(id=1)
        product = Product.objects.get(id=1)
        store.products.add(product)
        self.assertTrue(product in store.products.all())

class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Store.objects.create(name='Test Store', address='Test Address', phone_number='1234567890', email='test@store.com')
        Product.objects.create(name='Test Product', description='Test Description', price=10.0, available=True, store_id=1)

    def test_name_label(self):
        product = Product.objects.get(id=1)
        field_label = product._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_description_label(self):
        product = Product.objects.get(id=1)
        field_label = product._meta.get_field('description').verbose_name
        self.assertEquals(field_label, 'description')

    def test_price_label(self):
        product = Product.objects.get(id=1)
        field_label = product._meta.get_field('price').verbose_name
        self.assertEquals(field_label, 'price')

    def test_available_label(self):
        product = Product.objects.get(id=1)
        field_label = product._meta.get_field('available').verbose_name
        self.assertEquals(field_label, 'available')

    def test_store_relation(self):
        product = Product.objects.get(id=1)
        self.assertEquals(product.store.id, 1)

class OrderModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        User.objects.create_user(name='testuser', password='12345')
        Store.objects.create(name='Test Store', address='Test Address', phone_number='1234567890', email='test@store.com')
        Order.objects.create(customer_id=1, status='R', store_id=1)

    def test_customer_relation(self):
        order = Order.objects.get(id=1)
        self.assertEquals(order.customer.name, 'testuser')

    def test_status_label(self):
        order = Order.objects.get(id=1)
        field_label = order._meta.get_field('status').verbose_name
        self.assertEquals(field_label, 'status')

    def test_store_relation(self):
        order = Order.objects.get(id=1)
        self.assertEquals(order.store.id, 1)

class OrderItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Product.objects.create(name='Test Product', price=10.0)
        Store.objects.create(name='Test Store', address='Test Address', phone_number='1234567890', email='test@store.com')
        Order.objects.create(customer_id=1, status='R')
        OrderItem.objects.create(order_id=1, product_id=1, quantity=2, store_id=1, description='Test Description')

    def test_order_relation(self):
        order_item = OrderItem.objects.get(id=1)
        self.assertEquals(order_item.order.id, 1)

    def test_product_relation(self):
        order_item = OrderItem.objects.get(id=1)
        self.assertEquals(order_item.product.id, 1)

    def test_store_relation(self):
        order_item = OrderItem.objects.get(id=1)
        self.assertEquals(order_item.store.id, 1)

    def test_quantity(self):
        order_item = OrderItem.objects.get(id=1)
        self.assertEquals(order_item.quantity, 2)

    def test_description(self):
        order_item = OrderItem.objects.get(id=1)
        self.assertEquals(order_item.description, 'Test Description')

class PaymentModelTest(TestCase):
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
        self.assertEquals(payment.store.id, 1)