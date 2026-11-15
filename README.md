# BizBridge

**An Entrepreneurship Support and Connection Platform**

BizBridge is a web platform designed to help entrepreneurs discover mentors, investors, partners and relevant business opportunities. The current prototype includes role-aware accounts, self-service profiles, a searchable opportunity directory and an initial entrepreneur-to-mentor request workflow.

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
- A declined request can be resubmitted; duplicate pending or accepted requests are prevented.
- Automated tests for account access, profile editing, opportunity discovery and mentorship request permissions/status changes.

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

Copy `.env.example` to a new file named `.env`. The default settings use SQLite, so no database server is required to run the prototype.

Keep `.env` private. Do not commit real secret keys or database passwords.

### 6. Create database tables

```bash
python manage.py makemigrations
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
- Admin: `/admin/`

### 9. Run the tests

In a separate terminal with the virtual environment activated:

```bash
python manage.py test
```

## Managing opportunities

Create a staff or superuser account and sign in at `/admin/`. Use the Opportunities section to add a title, provider, description, category, sector, location, optional deadline and application link. Keep an opportunity active while applications are open; deactivate it when it is no longer available.

## Database configuration

By default, BizBridge uses SQLite for local development. To use PostgreSQL, create a PostgreSQL database and set the following variables in your private `.env` file:

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST` (defaults to `localhost`)
- `DB_PORT` (defaults to `5432`)

When `DB_NAME` is set, Django uses PostgreSQL. The PostgreSQL driver is included in `requirements.txt`.

## Initial user roles

- **Entrepreneur** — creates a profile and discovers support and opportunities.
- **Mentor** — joins to share experience and guide entrepreneurs.
- **Investor** — joins to discover ventures and potential investment connections.
- **Administrator** — manages accounts and opportunity listings through Django admin.

## Current scope and next steps

This is an early prototype, not the complete SRS implementation. Investor connections, messaging, notifications, verification workflows and deployment remain future development milestones.

## Repository

https://github.com/duwase7/bizbridge
