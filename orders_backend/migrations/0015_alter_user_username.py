# Generated by Django 3.2.23 on 2024-02-13 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders_backend', '0014_alter_order_paid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]