from django.db import models

class Payment(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stripe_payment_id = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default='pending')
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    def __str__(self):
        return str(self.id)

class Suscription(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'suscriptions'
        verbose_name = 'Suscription'
        verbose_name_plural = 'Suscriptions'
    def __str__(self):
        return str(self.id)
