from django.db import models
from django.conf import settings
from decimal import Decimal


class Sale(models.Model):
    STATUS_CHOICES = [('completed', 'Completed'),
                      ('voided', 'Voided'),
    ]
    salesperson = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sales')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Sale #{self.pk} — ${self.total_amount}"

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('inventory.Product', on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['sale', 'product']

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    @property
    def profit(self):
        return (self.unit_price - self.cost_price) * self.quantity
