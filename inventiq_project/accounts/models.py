from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [('manager', 'Manager'), ('salesperson', 'Salesperson')]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='salesperson')
    phone = models.CharField(max_length=20, blank=True)
    avatar_initials = models.CharField(max_length=3, blank=True)

    def save(self, *args, **kwargs):
        if not self.avatar_initials:
            parts = [self.first_name[:1], self.last_name[:1]]
            self.avatar_initials = ''.join(p for p in parts if p) or self.username[:2].upper()
        super().save(*args, **kwargs)

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_salesperson(self):
        return self.role == 'salesperson'

    @property
    def full_name(self):
        return self.get_full_name() or self.username

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'), ('logout', 'Logout'),
        ('sale_created', 'Sale Created'), ('product_added', 'Product Added'),
        ('product_updated', 'Product Updated'), ('product_deleted', 'Product Deleted'),
        ('stock_updated', 'Stock Updated'), ('user_created', 'User Created'),
        ('user_updated', 'User Updated'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} — {self.action}"
