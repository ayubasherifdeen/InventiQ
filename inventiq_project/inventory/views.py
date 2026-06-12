from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import manager_required
from accounts.models import ActivityLog
from .models import Product, Category, StockAdjustment
from .forms import ProductForm, CategoryForm, StockAdjustmentForm


@login_required
def product_list(request):
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    status = request.GET.get('status', '')
    products = Product.objects.select_related('category').filter(is_active=True)
    if search:
        products = products.filter(Q(name__icontains=search) | Q(sku__icontains=search))
    if category_id:
        products = products.filter(category_id=category_id)
    products = list(products)
    if status == 'low':
        products = [p for p in products if p.is_low_stock]
    elif status == 'out':
        products = [p for p in products if p.is_out_of_stock]
    categories = Category.objects.all()
    page = Paginator(products, 15).get_page(request.GET.get('page'))
    return render(request, 'inventory/product_list.html', {'products': page, 'categories': categories, 'search': search, 'category_id': category_id, 'status': status})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    adjustments = product.adjustments.select_related('adjusted_by').all()[:10]
    return render(request, 'inventory/product_detail.html', {'product': product, 'adjustments': adjustments})


@login_required
@manager_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        product = form.save()
        ActivityLog.objects.create(user=request.user, action='product_added', description=f"Added: {product.name} ({product.sku})")
        messages.success(request, f'Product "{product.name}" created.')
        return redirect('inventory:product_list')
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Add Product', 'action': 'Create'})


@login_required
@manager_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        ActivityLog.objects.create(user=request.user, action='product_updated', description=f"Updated: {product.name}")
        messages.success(request, f'Product "{product.name}" updated.')
        return redirect('inventory:product_list')
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Edit Product', 'action': 'Update', 'product': product})


@login_required
@manager_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.is_active = False
        product.save()
        ActivityLog.objects.create(user=request.user, action='product_deleted', description=f"Deleted: {product.name}")
        messages.success(request, f'Product "{product.name}" removed.')
        return redirect('inventory:product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})


@login_required
@manager_required
def stock_adjust(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = StockAdjustmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        adj = form.save(commit=False)
        adj.product = product
        adj.adjusted_by = request.user
        new_qty = product.stock_quantity + adj.quantity_change
        if new_qty < 0:
            messages.error(request, 'Cannot reduce stock below zero.')
            return render(request, 'inventory/stock_adjust.html', {'form': form, 'product': product})
        product.stock_quantity = new_qty
        product.save()
        adj.save()
        ActivityLog.objects.create(user=request.user, action='stock_updated', description=f"Stock adjusted for {product.name}: {'+' if adj.quantity_change > 0 else ''}{adj.quantity_change}")
        messages.success(request, f'Stock updated. New quantity: {product.stock_quantity}')
        return redirect('inventory:product_list')
    return render(request, 'inventory/stock_adjust.html', {'form': form, 'product': product})


@login_required
@manager_required
def category_list(request):
    categories = Category.objects.all()
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category created.')
        return redirect('inventory:category_list')
    return render(request, 'inventory/category_list.html', {'categories': categories, 'form': form})
