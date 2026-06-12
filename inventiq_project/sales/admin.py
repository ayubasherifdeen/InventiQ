from django.contrib import admin
from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ('get_subtotal', 'get_profit')
    fields = ('product', 'quantity', 'unit_price', 'cost_price', 'get_subtotal', 'get_profit')

    @admin.display(description='Subtotal')
    def get_subtotal(self, obj):
        return f"${obj.subtotal:.2f}"

    @admin.display(description='Profit')
    def get_profit(self, obj):
        return f"${obj.profit:.2f}"


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'salesperson', 'total_amount', 'get_item_count', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'salesperson')
    search_fields = ('salesperson__username', 'salesperson__first_name', 'notes')
    readonly_fields = ('created_at', 'get_item_count')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    inlines = [SaleItemInline]

    @admin.display(description='Items')
    def get_item_count(self, obj):
        return obj.item_count


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'unit_price', 'get_subtotal')
    search_fields = ('product__name', 'product__sku')
    readonly_fields = ('sale',)

    @admin.display(description='Subtotal')
    def get_subtotal(self, obj):
        return f"${obj.subtotal:.2f}"
