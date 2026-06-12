from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.decorators import manager_required
from inventory.models import Product
from .services import run_full_ai_analysis, run_ai_analysis, get_daily_sales_data


@login_required
@manager_required
def ai_dashboard(request):
    results, alerts = run_full_ai_analysis()
    return render(request, 'ai_engine/dashboard.html', {
        'results': results, 'alerts': alerts,
        'low_stock': [r for r in results if r['is_low_stock']],
        'spike_products': [r for r in results if r['demand_spike']],
    })


@login_required
@manager_required
def refresh_analysis(request):
    if request.method == 'POST':
        results, alerts = run_full_ai_analysis()
        return JsonResponse({'success': True, 'alerts_count': len(alerts)})
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
@manager_required
def product_analysis(request, pk):
    product = get_object_or_404(Product, pk=pk)
    analysis = run_ai_analysis(product)
    sales_data = get_daily_sales_data(product, 30)
    return render(request, 'ai_engine/product_analysis.html', {
        'product': product, 'analysis': analysis, 'sales_data': sales_data,
    })
