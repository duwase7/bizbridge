# BizBridge

**An Entrepreneurship Support and Connection Platform**

BizBridge is a web platform designed to help entrepreneurs discover mentors, investors, partners and relevant business opportunities. The current prototype includes role-aware accounts, role-specific profiles, a searchable opportunity directory, and entrepreneur-to-mentor and entrepreneur-to-investor request workflows.

## Technology

- Python 3.12
- Django 5.1+
- HTML and CSS
- SQLite for local development
- PostgreSQL for hosted deployment
- Gunicorn and WhiteNoise for production serving

## Features in this milestone

- Public landing page introducing BizBridge and its user groups.
- Account registration for Entrepreneurs, Mentors and Investors.
- Login and logout using Django authentication.
- Protected dashboard showing the signed-in user's role and profile details.
- Shared profile fields: name, email, organisation, location and biography.
- Entrepreneur-specific profile fields: business name, sector, stage and description.
- Mentor-specific profile fields: areas of expertise and availability.
- Investor-specific profile fields: investor type and website.
- Profile forms display only the fields relevant to the signed-in user's role; users cannot change their assigned role.
- Opportunity directory, keyword search and category filters; inactive opportunities are hidden.
- Administrators can add, update, activate and deactivate opportunities through Django admin.
- Entrepreneurs can browse mentor profiles and send mentorship requests; mentors can accept or reject requests.
- Entrepreneurs can browse and search investor profiles and send introductions; investors can accept or decline requests.
- Request status tracking, role-based permissions and duplicate-request protection.
- Automated tests cover account access, profile editing, opportunity discovery, mentorship requests and investor connection permissions/status changes.

## Setup and run locally

### 1. Install Python

Python 3.12 is recommended. Confirm it is available:

```bash
python3 --version
```

### 2. Clone the repository

```bash
git clone https://github.com/duwase7/bizbridge.git
cd bizbridge
```

### 3. Create and activate a virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
```

### 4. Install dependencies and migrate the database

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
```

The default local database is SQLite; a separate database server is not required.

### 5. Create an administrator (optional) and run the application

```bash
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/.

### 6. Run automated tests

```bash
python manage.py test
python manage.py makemigrations --check --dry-run
```

## Main pages

- Landing page: `/`
- Sign up: `/accounts/signup/`
- Log in: `/accounts/login/`
- Dashboard: `/accounts/dashboard/`
- Edit role-specific profile: `/accounts/profile/`
- Discover opportunities: `/opportunities/`
- Find mentors: `/mentorship/mentors/`
- Mentorship requests: `/mentorship/requests/`
- Find investors: `/connections/investors/`
- Investor connection requests: `/connections/requests/`
- Admin: `/admin/`

## Managing opportunities

Create a staff or superuser account and sign in at `/admin/`. Use the Opportunities section to add or update opportunity information, including its category, sector, location, deadline and application link.

## Deployment

The repository currently includes a Render Blueprint in `render.yaml` for a Python web service and PostgreSQL database. Deployment is a separate milestone; no public deployment URL is claimed in this repository update.

The free Render web service can spin down after inactivity, and the free PostgreSQL database has a limited lifetime. Review the provider's current plan terms before deploying. Keep secret keys and database credentials in private environment variables; never commit them to Git.

## Current scope

The prototype implements account registration and access, role-specific profile editing, opportunity discovery, mentorship requests and investor connection requests. The SRS also specifies direct messaging, notifications, administrator verification, account suspension and activity reports. These remain outstanding implementation work and should not be described as completed until implemented and tested.

## Repository

https://github.com/duwase7/bizbridge
