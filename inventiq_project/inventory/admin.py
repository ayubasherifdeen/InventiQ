from django.contrib import admin
from .models import Category, Product, StockAdjustment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'sku', 'category', 'selling_price',
        'stock_quantity', 'get_threshold', 'stock_status', 'is_active',
    )
    list_filter = ('category', 'is_active', 'use_ai_threshold')
    search_fields = ('name', 'sku', 'description')
    readonly_fields = ('created_at', 'updated_at', 'ai_reorder_threshold', 'profit_margin', 'stock_value')
    ordering = ('name',)
    list_editable = ('is_active',)
    fieldsets = (
        ('Product info', {
            'fields': ('name', 'sku', 'category', 'description', 'is_active')
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price', 'profit_margin')
        }),
        ('Stock', {
            'fields': ('stock_quantity', 'stock_value', 'reorder_threshold', 'ai_reorder_threshold', 'use_ai_threshold')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Threshold')
    def get_threshold(self, obj):
        suffix = ' (AI)' if obj.use_ai_threshold else ''
        return f"{obj.effective_threshold}{suffix}"

    @admin.display(description='Status')
    def stock_status(self, obj):
        return obj.stock_status


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_change', 'reason', 'adjusted_by', 'timestamp')
    list_filter = ('reason', 'timestamp')
    search_fields = ('product__name', 'product__sku', 'notes')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
