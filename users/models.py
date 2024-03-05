from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('El Email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)

# The User class is a model that extends the AbstractUser class and adds additional fields and
# relationships for user authentication and store ownership.
class User(AbstractUser):
    # Otros campos de usuario
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_users'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_users_permissions'
    )

    username = models.CharField(max_length=50, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    password = models.CharField(max_length=128, blank=False)

    is_superuser = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    owned_stores = models.ManyToManyField('orders.Store', related_name='owners', blank=True)

    objects = UserManager()

    def __str__(self):
        return self.username or ''
