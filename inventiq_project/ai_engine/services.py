from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta


def get_daily_sales_data(product, days=30):
    from sales.models import SaleItem
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    items = SaleItem.objects.filter(
        product=product, sale__created_at__date__gte=start_date,
        sale__created_at__date__lte=end_date, sale__status='completed',
    ).values('sale__created_at__date').annotate(total_qty=Sum('quantity'))
    daily = {str(i['sale__created_at__date']): i['total_qty'] for i in items}
    return [daily.get(str(start_date + timedelta(days=i)), 0) for i in range(days)]


def moving_average(data, window=7):
    if not data:
        return 0
    window = min(window, len(data))
    return sum(data[-window:]) / window


def calculate_sales_velocity(product, days=30):
    data = get_daily_sales_data(product, days)
    active_days = sum(1 for d in data if d > 0)
    return sum(data) / max(active_days, 1) if active_days else 0


def detect_demand_spike(product, window=7, multiplier=2.0):
    recent = get_daily_sales_data(product, window)
    historical = get_daily_sales_data(product, 30)
    recent_avg = moving_average(recent, window)
    historical_avg = moving_average(historical, 30)
    if historical_avg == 0:
        return False, 0
    ratio = recent_avg / historical_avg
    return ratio >= multiplier, round(ratio, 2)


def calculate_dynamic_threshold(product, lead_time=7, safety=1.5):
    velocity = calculate_sales_velocity(product, 30)
    if velocity == 0:
        return max(product.reorder_threshold, 5)
    recent_ma = moving_average(get_daily_sales_data(product, 7), 7)
    hist_ma = moving_average(get_daily_sales_data(product, 30), 30)
    trend = min(max(recent_ma / hist_ma, 0.8), 1.5) if hist_ma > 0 else 1.0
    return max(int(velocity * lead_time * safety * trend), 5)


def calculate_restock_suggestion(product, lead_time=7, safety=1.5, cycle_days=30):
    velocity = calculate_sales_velocity(product, 30)
    if velocity == 0:
        return 0
    return max(int(velocity * lead_time * safety + velocity * cycle_days), 1)


def run_ai_analysis(product):
    velocity = calculate_sales_velocity(product, 30)
    threshold = calculate_dynamic_threshold(product)
    restock = calculate_restock_suggestion(product)
    spike, spike_ratio = detect_demand_spike(product)
    product.ai_reorder_threshold = threshold
    product.save(update_fields=['ai_reorder_threshold'])
    return {
        'product': product,
        'daily_velocity': round(velocity, 2),
        'ai_threshold': threshold,
        'restock_suggestion': restock,
        'demand_spike': spike,
        'spike_ratio': spike_ratio,
        'is_low_stock': product.is_low_stock,
        'current_stock': product.stock_quantity,
    }


def run_full_ai_analysis():
    from inventory.models import Product
    results, alerts = [], []
    for product in Product.objects.filter(is_active=True):
        r = run_ai_analysis(product)
        results.append(r)
        if r['is_low_stock']:
            alerts.append({
                'type': 'low_stock',
                'severity': 'critical' if product.is_out_of_stock else 'warning',
                'product': product,
                'message': f"{'Out of stock' if product.is_out_of_stock else 'Low stock'}: {product.name} ({product.stock_quantity} remaining, threshold: {r['ai_threshold']})",
                'restock_suggestion': r['restock_suggestion'],
            })
        if r['demand_spike']:
            alerts.append({
                'type': 'demand_spike',
                'severity': 'info',
                'product': product,
                'message': f"Demand spike: {product.name} at ×{r['spike_ratio']} normal rate",
                'restock_suggestion': r['restock_suggestion'],
            })
    return results, alerts


def get_top_products(limit=5, days=30):
    from sales.models import SaleItem
    from django.db.models import F
    start = timezone.now() - timedelta(days=days)
    return list(SaleItem.objects.filter(
        sale__created_at__gte=start, sale__status='completed',
    ).values('product__id', 'product__name', 'product__sku').annotate(
        total_qty=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('unit_price')),
    ).order_by('-total_revenue')[:limit])


def get_sales_over_time(days=30):
    from sales.models import Sale
    end = timezone.now().date()
    start = end - timedelta(days=days - 1)
    sales = Sale.objects.filter(created_at__date__gte=start, status='completed').values(
        'created_at__date').annotate(daily_total=Sum('total_amount'), count=Count('id')).order_by('created_at__date')
    dm = {str(s['created_at__date']): {'total': float(s['daily_total']), 'count': s['count']} for s in sales}
    labels, revenue, counts = [], [], []
    for i in range(days):
        d = start + timedelta(days=i)
        labels.append(d.strftime('%b %d'))
        revenue.append(dm.get(str(d), {}).get('total', 0))
        counts.append(dm.get(str(d), {}).get('count', 0))
    return {'labels': labels, 'revenue': revenue, 'counts': counts}


def get_category_performance(days=30):
    from sales.models import SaleItem
    from django.db.models import F
    start = timezone.now() - timedelta(days=days)
    return list(SaleItem.objects.filter(
        sale__created_at__gte=start, sale__status='completed', product__category__isnull=False,
    ).values('product__category__name').annotate(
        total_revenue=Sum(F('quantity') * F('unit_price')), total_qty=Sum('quantity'),
    ).order_by('-total_revenue'))
