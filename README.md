# BizBridge

**An Entrepreneurship Support and Connection Platform**

BizBridge is a web platform designed to help entrepreneurs discover mentors, investors, partners and relevant business opportunities. The current prototype includes role-aware accounts, self-service profiles, a searchable opportunity directory, and entrepreneur-to-mentor and entrepreneur-to-investor request workflows.

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
- Profile editing for first name, last name, email, organisation, location and bio.
- Profile editing does not allow users to change their account role.
- Opportunity directory available to signed-in users.
- Search opportunities by title, provider, description, sector or location.
- Filter opportunities by funding, training, competition, mentorship, partnership or other category.
- Inactive opportunities are hidden from the directory.
- Administrators can add, update, activate and deactivate opportunities through Django admin.
- Entrepreneurs can browse mentor profiles and send a mentorship request with an introductory message.
- Entrepreneurs can track pending, accepted and declined mentorship requests.
- Mentors can review incoming requests and accept or reject them.
- A declined mentorship request can be resubmitted; duplicate pending or accepted requests are prevented.
- Entrepreneurs can browse and search investor profiles by name, organisation, location or investment focus.
- Entrepreneurs can introduce their businesses to investors through a connection request.
- Investors can review incoming entrepreneur introductions and accept or decline them.
- Entrepreneurs can track pending, accepted and declined investor connection requests; declined requests can be resubmitted.
- Role-based access checks prevent mentors from initiating investor requests and prevent users from responding to requests addressed to someone else.
- Automated tests cover account access, profile editing, opportunity discovery, mentorship requests and investor connection permissions/status changes.

## Setup and run locally

### 1. Install Python

Python 3.12 is recommended to match the automated checks and deployment environment. Confirm it is available:

```bash
python3 --version
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
.venv\\Scripts\\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment variables (optional for local use)

Copy `.env.example` to a new file named `.env`. The default settings use SQLite, so no database server is required to run the prototype.

Keep `.env` private. Do not commit real secret keys or database passwords.

### 6. Create database tables

```bash
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
- Edit profile (requires login): `/accounts/profile/`
- Discover opportunities (requires login): `/opportunities/`
- Find mentors (entrepreneur accounts): `/mentorship/mentors/`
- Send a mentorship request: `/mentorship/mentors/<mentor_id>/request/`
- View sent or received mentorship requests: `/mentorship/requests/`
- Find and search investors (entrepreneur accounts): `/connections/investors/`
- Send an investor connection request: `/connections/investors/<investor_id>/request/`
- View sent or received investor requests: `/connections/requests/`
- Admin: `/admin/`

### 9. Run the tests

```bash
python manage.py test
```

## Managing opportunities

Create a staff or superuser account and sign in at `/admin/`. Use the Opportunities section to add a title, provider, description, category, sector, location, optional deadline and application link. Keep an opportunity active while applications are open; deactivate it when it is no longer available.

## Deploy a public demo on Render

The repository includes a Render Blueprint in `render.yaml`. It defines a Python web service and a PostgreSQL database in the Frankfurt region.

1. Push or merge the deployment configuration to the `main` branch.
2. Sign in to [Render](https://render.com/) and connect the GitHub account that can access this repository.
3. In the Render Dashboard, choose **New + → Blueprint**.
4. Select `duwase7/bizbridge` and the `main` branch.
5. Review the web service and PostgreSQL resources, then apply the Blueprint.
6. Wait for the first build and deploy to complete. Render will install dependencies, verify that model changes are represented by committed migrations, collect static files, apply the versioned migrations and start Django with Gunicorn.
7. Copy the public `.onrender.com` URL shown on the web service page and test registration, login, profile editing, opportunity discovery, mentorship requests and investor connection requests.

The Blueprint uses Render's Free plans for a course prototype. Important limitations: a free web service spins down after 15 minutes without traffic and may take about a minute to wake up. A free Render PostgreSQL database expires 30 days after it is created. Do not use this setup for permanent production data; export or migrate the database before it expires, or upgrade it if the data must be retained.

Each Django app now has a committed initial migration, so local setup and deployment use the same versioned database schema. Before adding or changing models, run `python manage.py makemigrations`, review the generated migration files, and commit them with the model changes. CI and the Render build run `python manage.py makemigrations --check --dry-run` to catch model changes that have not been captured in migrations, then apply the committed migrations with `python manage.py migrate`. The free web-service plan does not provide dashboard Shell access. To create a hosted admin account without Shell access, add `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD` as private environment variables in the Render service settings, then trigger a deploy. The build script runs an idempotent bootstrap command after migrations: it creates the account only if that username does not already exist, and never changes an existing account or password. Remove the password environment variable after the first successful bootstrap. Never commit administrator credentials to this repository.

## Database configuration

By default, BizBridge uses SQLite for local development. For a hosted PostgreSQL database, set `DATABASE_URL` to its connection string. The app parses this variable automatically.

For local PostgreSQL installations that do not use `DATABASE_URL`, set:

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST` (defaults to `localhost`)
- `DB_PORT` (defaults to `5432`)

The PostgreSQL driver is included in `requirements.txt`.

## Initial user roles

- **Entrepreneur** — creates a profile, discovers support and opportunities, and initiates connections.
- **Mentor** — joins to share experience and guide entrepreneurs.
- **Investor** — creates an organisation profile and reviews introductions from entrepreneurs.
- **Administrator** — manages accounts, opportunity listings and connection requests through Django admin.

## Current scope and next steps

This is an early prototype, not the complete SRS implementation. Direct messaging, notifications, partner discovery and formal verification workflows remain future development milestones.

## Repository

https://github.com/duwase7/bizbridge
