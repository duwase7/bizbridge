# BizBridge

**An Entrepreneurship Support and Connection Platform**

BizBridge is a web platform designed to help entrepreneurs discover mentors, investors, partners, and relevant business opportunities.

## Initial implementation

The project is being developed with:
- Python and Django
- HTML, CSS, and JavaScript
- PostgreSQL for the planned production database (SQLite is used by default for a quick local setup)

The first development milestone establishes the Django project, role-aware user accounts, authentication, and the initial landing page.

## Local setup

1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create an administrator: `python manage.py createsuperuser`
5. Start the development server: `python manage.py runserver`

Open http://127.0.0.1:8000/.

## Database configuration

By default, BizBridge uses SQLite for local development. To use PostgreSQL, set these environment variables before starting Django:

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST` (defaults to `localhost`)
- `DB_PORT` (defaults to `5432`)

Never commit database credentials or secret keys.

## Initial user roles

- Entrepreneur
- Mentor
- Investor
- Administrator (Django staff/superuser account)

Role-based permissions and dedicated dashboards will be expanded as the relevant SRS features are implemented.
