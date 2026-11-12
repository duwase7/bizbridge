# BizBridge

**An Entrepreneurship Support and Connection Platform**

BizBridge is a web platform designed to help entrepreneurs discover mentors, investors, partners and relevant business opportunities. This first prototype milestone establishes the application foundation, public landing page, role-aware registration, login/logout and a protected user dashboard.

## Technology

- Python 3.10+
- Django 5.1+
- HTML and CSS
- SQLite for local development
- PostgreSQL support through environment variables

## Features in this milestone

- Public landing page introducing BizBridge and its user groups.
- Account registration for Entrepreneurs, Mentors and Investors.
- Login and logout using Django authentication.
- Protected dashboard showing the signed-in user's role and profile details.
- Django admin for managing user accounts.
- Automated tests for the landing page, registration and dashboard access.

## Setup and run locally

### 1. Install Python

Install Python 3.10 or newer. Confirm it is available:

```bash
python --version
```

### 2. Clone the repository

```bash
git clone https://github.com/duwase7/bizbridge.git
cd bizbridge
```

### 3. Create a virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment variables (optional for local use)

Copy `.env.example` to a new file named `.env`. The default settings use SQLite, so no database server is required to run the initial prototype.

Keep `.env` private. Do not commit real secret keys or database passwords.

### 6. Create database tables

```bash
python manage.py makemigrations accounts
python manage.py migrate
```

### 7. Create an administrator account (optional)

```bash
python manage.py createsuperuser
```

### 8. Run the development server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

- Landing page: `/`
- Sign up: `/accounts/signup/`
- Log in: `/accounts/login/`
- Dashboard (requires login): `/accounts/dashboard/`
- Admin: `/admin/`

### 9. Run the tests

In a separate terminal with the virtual environment activated:

```bash
python manage.py test
```

## Database configuration

By default, BizBridge uses SQLite for local development. To use PostgreSQL, create a PostgreSQL database and set the following variables in your private `.env` file:

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST` (defaults to `localhost`)
- `DB_PORT` (defaults to `5432`)

When `DB_NAME` is set, Django uses PostgreSQL. The PostgreSQL driver is included in `requirements.txt`.

## Initial user roles

- **Entrepreneur** — creates a profile and will be able to discover support and opportunities.
- **Mentor** — joins to share experience and guide entrepreneurs.
- **Investor** — joins to discover ventures and potential investment connections.
- **Administrator** — managed through Django's built-in staff and superuser permissions.

## Current scope and next steps

This is an early working foundation, not the complete SRS implementation. Profile editing, opportunity discovery, search and filtering, connection/mentorship requests, messaging, notifications and verification workflows remain future development milestones.

## Repository

https://github.com/duwase7/bizbridge
