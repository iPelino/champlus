# ChamPlus Backend

Multi-tenant Django REST API for group financial management.

## Architecture

### Multi-Tenancy

The application uses a **subdomain-based multi-tenancy** architecture:

- Each organization/group has a unique subdomain (e.g., `acme.champlus.com`)
- The `TenantMiddleware` identifies the tenant from the subdomain
- All data is automatically scoped to the current tenant
- Complete data isolation between tenants

### Database Schema

The database consists of 4 main apps:

#### 1. Tenants App
- **Tenant**: Organization/group entity with subscription management

#### 2. Groups App
- **Group**: Financial group (chama) within a tenant
- Manages contribution settings, frequency, and rules

#### 3. Members App
- **UserProfile**: Extended user information
- **GroupMembership**: User's membership in groups with roles (admin/treasurer/member)
- **GroupInvitation**: Email-based invitation system

#### 4. Financials App
- **Contribution**: Member contributions to the group
- **Expense**: Group expenses and withdrawals
- **Transaction**: Unified ledger for all financial activities

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 14+

### Installation

1. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export DB_NAME=champlus_db
export DB_USER=postgres
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

## Development

### Creating a Tenant

```python
from tenants.models import Tenant
from datetime import datetime, timedelta

tenant = Tenant.objects.create(
    name="Acme Corp",
    slug="acme-corp",
    subdomain="acme",
    subscription_status="trial",
    trial_ends_at=datetime.now() + timedelta(days=14)
)
```

### Accessing with Subdomain

For local development, add to `/etc/hosts`:
```
127.0.0.1 acme.localhost
```

Then access: `http://acme.localhost:8000`

### Tenant-Aware Models

Models that need tenant isolation should use `TenantManager`:

```python
from tenants.managers import TenantManager

class MyModel(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    objects = TenantManager()  # Automatic tenant filtering
```

## API Structure

The API follows RESTful conventions:

- `/api/groups/` - Group management
- `/api/members/` - Member management
- `/api/contributions/` - Contribution tracking
- `/api/expenses/` - Expense management
- `/api/transactions/` - Transaction ledger

## Security

- All queries are automatically scoped to the current tenant
- Subdomain validation prevents cross-tenant data access
- Subscription status is checked on every request
- Role-based permissions (admin, treasurer, member)

## Testing

Run tests:
```bash
python manage.py test
```

## Database Migrations

Create migrations after model changes:
```bash
python manage.py makemigrations
```

Apply migrations:
```bash
python manage.py migrate
```
