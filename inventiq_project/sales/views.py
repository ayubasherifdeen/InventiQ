from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction
from accounts.models import ActivityLog
from inventory.models import Product
from .models import Sale, SaleItem
import json


@login_required
def pos_view(request):
    products = Product.objects.filter(is_active=True, stock_quantity__gt=0).select_related('category').order_by('name')
    categories = list(products.values_list('category__name', flat=True).distinct())
    return render(request, 'sales/pos.html', {'products': products, 'categories': categories})


@login_required
def process_sale(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        discount = float(data.get('discount', 0))
        notes = data.get('notes', '')
        if not items:
            return JsonResponse({'error': 'No items in cart'}, status=400)
        with transaction.atomic():
            sale = Sale.objects.create(salesperson=request.user, discount_amount=discount, notes=notes)
            total = 0
            for item_data in items:
                product = Product.objects.select_for_update().get(pk=item_data['product_id'])
                qty = int(item_data['quantity'])
                if product.stock_quantity < qty:
                    raise ValueError(f"Insufficient stock for {product.name}. Available: {product.stock_quantity}")
                SaleItem.objects.create(
                    sale=sale, product=product, quantity=qty,
                    unit_price=product.selling_price, cost_price=product.cost_price,
                )
                product.stock_quantity -= qty
                product.save()
                total += float(product.selling_price) * qty
            sale.total_amount = total - discount
            sale.save()
            ActivityLog.objects.create(
                user=request.user, action='sale_created',
                description=f"Sale #{sale.pk}: ${sale.total_amount:.2f} ({len(items)} items)",
            )
        return JsonResponse({'success': True, 'sale_id': sale.pk, 'total': float(sale.total_amount)})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def sale_list(request):
    sales = Sale.objects.select_related('salesperson').prefetch_related('items__product')
    if not request.user.is_manager:
        sales = sales.filter(salesperson=request.user)
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        sales = sales.filter(created_at__date__gte=date_from)
    if date_to:
        sales = sales.filter(created_at__date__lte=date_to)
    page = Paginator(sales, 15).get_page(request.GET.get('page'))
    return render(request, 'sales/sale_list.html', {'sales': page, 'date_from': date_from, 'date_to': date_to})


@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if not request.user.is_manager and sale.salesperson != request.user:
        messages.error(request, 'Access denied.')
        return redirect('sales:sale_list')
    return render(request, 'sales/sale_detail.html', {'sale': sale})


@login_required
def sale_receipt(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if not request.user.is_manager and sale.salesperson != request.user:
        messages.error(request, 'Access denied.')
        return redirect('sales:sale_list')
    return render(request, 'sales/sale_receipt.html', {'sale': sale})
