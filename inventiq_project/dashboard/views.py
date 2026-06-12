from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from datetime import timedelta
from accounts.decorators import manager_required
from inventory.models import Product
from sales.models import Sale, SaleItem
from ai_engine.services import get_sales_over_time, get_top_products, run_full_ai_analysis
import json, csv


@login_required
def index(request):
    return manager_dashboard(request) if request.user.is_manager else salesperson_dashboard(request)


@login_required
def salesperson_dashboard(request):
    today = timezone.now().date()
    my_today = Sale.objects.filter(salesperson=request.user, created_at__date=today, status='completed')
    my_week = Sale.objects.filter(salesperson=request.user, created_at__date__gte=today - timedelta(days=7), status='completed')
    recent = Sale.objects.filter(salesperson=request.user, status='completed').prefetch_related('items__product')[:5]
    return render(request, 'dashboard/salesperson.html', {
        'today_revenue': my_today.aggregate(t=Sum('total_amount'))['t'] or 0,
        'today_count': my_today.count(),
        'week_revenue': my_week.aggregate(t=Sum('total_amount'))['t'] or 0,
        'week_count': my_week.count(),
        'recent_sales': recent,
        'products_available': Product.objects.filter(is_active=True, stock_quantity__gt=0).count(),
    })


@login_required
@manager_required
def manager_dashboard(request):
    period = request.GET.get('period', '30')
    try:
        days = int(period)
    except ValueError:
        days = 30

    start = timezone.now() - timedelta(days=days)
    sales_qs = Sale.objects.filter(created_at__gte=start, status='completed')
    total_revenue = sales_qs.aggregate(t=Sum('total_amount'))['t'] or 0
    total_sales = sales_qs.count()
    avg_sale = sales_qs.aggregate(a=Avg('total_amount'))['a'] or 0

    products = list(Product.objects.filter(is_active=True))
    low_stock = [p for p in products if p.is_low_stock]

    chart_data = get_sales_over_time(days)
    top_products = get_top_products(limit=8, days=days)
    recent_sales = Sale.objects.select_related('salesperson').prefetch_related('items')[:8]
    _, alerts = run_full_ai_analysis()

    top_salespeople = Sale.objects.filter(created_at__gte=start, status='completed').values(
        'salesperson__id', 'salesperson__first_name', 'salesperson__last_name', 'salesperson__username',
    ).annotate(total=Sum('total_amount'), count=Count('id')).order_by('-total')[:5]

    return render(request, 'dashboard/manager.html', {
        'period': period, 'days': days,
        'total_revenue': total_revenue, 'total_sales': total_sales, 'avg_sale': avg_sale,
        'total_products': len(products), 'low_stock_count': len(low_stock),
        'low_stock_products': low_stock[:5],
        'chart_labels': json.dumps(chart_data['labels']),
        'chart_revenue': json.dumps(chart_data['revenue']),
        'chart_counts': json.dumps(chart_data['counts']),
        'top_products': top_products,
        'recent_sales': recent_sales,
        'alerts': alerts[:5],
        'top_salespeople': top_salespeople,
    })


@login_required
@manager_required
def export_csv(request):
    period = request.GET.get('period', '30')
    try:
        days = int(period)
    except ValueError:
        days = 30
    start = timezone.now() - timedelta(days=days)
    sales = Sale.objects.filter(created_at__gte=start, status='completed').select_related('salesperson').prefetch_related('items__product')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_{days}days.csv"'
    writer = csv.writer(response)
    writer.writerow(['Sale ID', 'Date', 'Salesperson', 'Items', 'Total', 'Status'])
    for sale in sales:
        writer.writerow([sale.pk, sale.created_at.strftime('%Y-%m-%d %H:%M'), sale.salesperson.full_name if sale.salesperson else 'N/A', sale.item_count, sale.total_amount, sale.status])
    return response


@login_required
@manager_required
def export_inventory_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory.csv"'
    writer = csv.writer(response)
    writer.writerow(['SKU', 'Name', 'Category', 'Cost Price', 'Selling Price', 'Stock', 'Threshold', 'Status'])
    for p in Product.objects.filter(is_active=True).select_related('category'):
        writer.writerow([p.sku, p.name, p.category.name if p.category else 'N/A', p.cost_price, p.selling_price, p.stock_quantity, p.effective_threshold, p.stock_status])
    return response
