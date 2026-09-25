# Restaurant Portal — Backend API

A production-ready Django REST API for a multi-tenant restaurant platform supporting customers, restaurant admins, kitchen staff, delivery drivers, and a super-admin.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 4.2 + Django REST Framework |
| Database | PostgreSQL 15 |
| Auth | JWT (simplejwt) + Djoser |
| Cache / Broker | Redis 7 |
| Async Tasks | Celery |
| WebSocket | Django Channels + Redis |
| Tests | pytest-django + factory-boy |

## Project Structure

```
restaurant_portal/
├── apps/                   # Domain apps
│   ├── common/             # Shared models, serializers, utilities
│   ├── users/              # Custom user model & authentication
│   ├── restaurants/        # Restaurant management
│   ├── menu/               # Menu & item management
│   ├── orders/             # Order lifecycle
│   ├── payments/           # Payment processing (Stripe)
│   ├── kitchen/            # Kitchen Display System + WebSocket
│   ├── delivery/           # Delivery tracking
│   ├── support/            # Customer support tickets
│   └── analytics/          # Reports & analytics
├── restaurant_portal/      # Django project config
│   ├── settings/           # Environment-specific settings
│   ├── urls.py
│   ├── asgi.py             # WebSocket entrypoint
│   └── wsgi.py
├── docker/                 # Docker + Compose files
├── tests/                  # Shared test config & fixtures
├── static/
├── media/
└── logs/
```

## Quick Start

### 1. Clone & create virtual environment

```bash
git clone <repo-url>
cd restaurant_portal
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your database, Redis, and email credentials
```

### 3. Start services (Docker)

```bash
docker compose -f docker/docker-compose.yml up -d db redis
```

### 4. Run migrations & create superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Start the development server

```bash
python manage.py runserver
```

### 6. (Optional) Start Celery worker

```bash
celery -A restaurant_portal worker --loglevel=info
```

## Running Tests

```bash
pytest
pytest --cov=apps --cov-report=html  # with coverage
```

## API Base URL

```
http://localhost:8000/api/v1/
```

## Key Endpoints (v1)

| App | Base path |
|---|---|
| Auth | `/api/v1/auth/` |
| Restaurants | `/api/v1/restaurants/` |
| Menu | `/api/v1/menu/` |
| Orders | `/api/v1/orders/` |
| Payments | `/api/v1/payments/` |
| Kitchen | `/api/v1/kitchen/` |
| Delivery | `/api/v1/delivery/` |
| Support | `/api/v1/support/` |
| Analytics | `/api/v1/analytics/` |

WebSocket: `ws://localhost:8000/ws/kitchen/orders/`

## Environment Variables

See `.env.example` for the full list with descriptions.

## Contributing

1. Create a feature branch off `main`.
2. Write tests for new functionality.
3. Run `pytest` and ensure all tests pass.
4. Open a pull request.

## License

MIT
