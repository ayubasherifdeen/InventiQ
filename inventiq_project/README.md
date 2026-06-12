# InventiQ — Inventory & Sales Management

Full-stack Django application with multi-role auth, POS, AI-powered inventory intelligence, and analytics.

## Stack
- **Backend**: Django 4.2, Python 3.10+
- **Frontend**: Django Templates + Tailwind CSS (CDN)
- **Fonts**: Plus Jakarta Sans (headings/numbers) + Inter (body) via Google Fonts
- **Charts**: Chart.js (CDN)
- **Database**: SQLite (default) — PostgreSQL ready

## Quick start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python manage.py makemigrations accounts inventory sales dashboard ai_engine
python manage.py migrate
python manage.py seed_data

python manage.py runserver
```

Visit **http://localhost:8000**

## Credentials

| Role        | Username     | Password   |
|-------------|--------------|------------|
| Manager     | `admin`      | `admin123` |
| Salesperson | `sarah_chen` | `sales123` |
| Salesperson | `marcus_j`   | `sales123` |

Django admin available at `/django-admin/` (log in as `admin`).

## Features

**Manager**
- Dashboard: KPI cards, revenue chart, top products, AI alerts, recent transactions
- Full inventory CRUD — products, categories, stock adjustments
- User management (create, edit, activate/deactivate)
- AI Insights: demand spike detection, dynamic reorder thresholds, restock suggestions
- Activity log (full audit trail)
- CSV export (sales + inventory)

**Salesperson**
- Personal dashboard with daily/weekly stats
- Point of Sale — cart-based, live stock validation, discount support
- Sales history with date filters
- Printable receipts

## AI Engine
Lightweight, rule-based — no external ML libraries:
- **Velocity**: avg units/active day (30-day window)
- **Dynamic threshold**: `velocity × lead_time(7d) × safety(1.5) × trend_factor`
- **Restock suggestion**: `safety_stock + 30-day cycle_stock`
- **Spike detection**: 7-day MA ≥ 2× 30-day MA

## PostgreSQL (optional)
Replace `DATABASES` in `inventiq_project/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventiq', 'USER': 'your_user',
        'PASSWORD': 'your_pass', 'HOST': 'localhost', 'PORT': '5432',
    }
}
```
Then: `pip install psycopg2-binary`
