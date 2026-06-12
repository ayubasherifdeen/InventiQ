import random
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seeds the database with demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding InventiQ...\n')

        from accounts.models import User
        from inventory.models import Category, Product
        from sales.models import Sale, SaleItem

        manager, _ = User.objects.get_or_create(username='admin', defaults=dict(
            email='admin@inventiq.com', role='manager',
            first_name='Alex', last_name='Morgan', is_staff=True,
        ))
        manager.set_password('admin123')
        manager.save()
        self.stdout.write('  ✅ admin / admin123 (Manager)')

        salespeople = []
        for uname, first, last in [('sarah_chen','Sarah','Chen'),('marcus_j','Marcus','Johnson'),('priya_k','Priya','Kumar')]:
            sp, _ = User.objects.get_or_create(username=uname, defaults=dict(
                email=f'{uname}@inventiq.com', role='salesperson', first_name=first, last_name=last))
            sp.set_password('sales123')
            sp.save()
            salespeople.append(sp)
        self.stdout.write('  ✅ sarah_chen, marcus_j, priya_k / sales123')

        cats = {}
        for name in ['Electronics', 'Accessories', 'Office Supplies', 'Audio', 'Networking']:
            cat, _ = Category.objects.get_or_create(name=name)
            cats[name] = cat

        product_data = [
            ('MacBook Pro 14"',        'ELEC-001', 'Electronics',     1200, 1599, 25, 5),
            ('iPhone 15 Pro',           'ELEC-002', 'Electronics',      800, 1099, 40, 8),
            ('iPad Air',                'ELEC-003', 'Electronics',      550,  749, 30, 6),
            ('AirPods Pro',             'AUDIO-001', 'Audio',           180,  249, 60, 15),
            ('Sony WH-1000XM5',         'AUDIO-002', 'Audio',           250,  349, 45, 10),
            ('USB-C Hub 7-in-1',        'ACC-001',  'Accessories',       25,   49, 80, 20),
            ('MagSafe Charger',         'ACC-002',  'Accessories',       15,   39, 90, 25),
            ('Laptop Stand',            'ACC-003',  'Accessories',       30,   59, 55, 12),
            ('Mechanical Keyboard',     'ELEC-004', 'Electronics',       70,  129, 35, 8),
            ('Wireless Mouse',          'ELEC-005', 'Electronics',       20,   45, 70, 18),
            ('Monitor 27" 4K',          'ELEC-006', 'Electronics',      300,  449, 20, 4),
            ('Ethernet Switch 8-Port',  'NET-001',  'Networking',        40,   79, 30, 8),
            ('WiFi 6 Router',           'NET-002',  'Networking',        90,  149, 25, 6),
            ('Desk Organizer',          'OFF-001',  'Office Supplies',   12,   24, 100, 20),
            ('Whiteboard Markers (pk)', 'OFF-002',  'Office Supplies',    3,    8,  4, 30),
            ('Webcam 4K',               'ELEC-007', 'Electronics',       60,   99,  0, 10),
            ('Portable SSD 1TB',        'ELEC-008', 'Electronics',       70,  119, 50, 12),
            ('Screen Cleaner Kit',      'ACC-004',  'Accessories',        5,   14, 150, 30),
        ]

        products = []
        for name, sku, cat_name, cost, price, stock, threshold in product_data:
            p, _ = Product.objects.get_or_create(sku=sku, defaults=dict(
                name=name, category=cats[cat_name],
                cost_price=Decimal(str(cost)), selling_price=Decimal(str(price)),
                stock_quantity=stock, reorder_threshold=threshold, ai_reorder_threshold=threshold,
            ))
            products.append(p)
        self.stdout.write(f'  ✅ {len(products)} products created')

        in_stock = [p for p in products if p.stock_quantity > 0]

        if Sale.objects.count() < 10:
            count = 0
            for days_ago in range(60, 0, -1):
                sale_date = timezone.now() - timedelta(days=days_ago)
                for _ in range(random.randint(1, 4)):
                    sp = random.choice(salespeople)
                    cart = random.sample(in_stock, k=random.randint(1, 3))
                    sale = Sale.objects.create(salesperson=sp, status='completed')
                    total = Decimal('0')
                    for product in cart:
                        qty = random.randint(1, 3)
                        SaleItem.objects.create(
                            sale=sale, product=product, quantity=qty,
                            unit_price=product.selling_price, cost_price=product.cost_price,
                        )
                        total += product.selling_price * qty
                    Sale.objects.filter(pk=sale.pk).update(total_amount=total, created_at=sale_date)
                    count += 1
            self.stdout.write(f'  ✅ {count} historical sales created')

        from ai_engine.services import run_full_ai_analysis
        _, alerts = run_full_ai_analysis()
        self.stdout.write(f'  ✅ AI analysis complete — {len(alerts)} alerts\n')
        self.stdout.write(self.style.SUCCESS('🎉 Done! Visit http://localhost:8000'))
        self.stdout.write('  admin / admin123  |  sarah_chen / sales123\n')
