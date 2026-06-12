from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField(blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_threshold = models.PositiveIntegerField(default=10)
    ai_reorder_threshold = models.PositiveIntegerField(default=10)
    use_ai_threshold = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def effective_threshold(self):
        return self.ai_reorder_threshold if self.use_ai_threshold else self.reorder_threshold

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.effective_threshold

    @property
    def is_out_of_stock(self):
        return self.stock_quantity == 0

    @property
    def profit_margin(self):
        if self.selling_price > 0:
            return round(((self.selling_price - self.cost_price) / self.selling_price) * 100, 1)
        return 0

    @property
    def stock_status(self):
        if self.is_out_of_stock:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        return 'in_stock'

    @property
    def stock_value(self):
        return self.cost_price * self.stock_quantity


class StockAdjustment(models.Model):
    REASON_CHOICES = [
        ('restock', 'Restock'), ('damaged', 'Damaged/Removed'),
        ('correction', 'Inventory Correction'), ('returned', 'Customer Return'), ('other', 'Other'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='adjustments')
    quantity_change = models.IntegerField()
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    notes = models.TextField(blank=True)
    adjusted_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.product.name}: {'+' if self.quantity_change > 0 else ''}{self.quantity_change}"
