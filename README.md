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
- In-app notifications when mentorship or investor requests are received or accepted/declined, with unread counts and read controls.
- Optional, explicit demo-data command creates sample role-based accounts, opportunities, requests and notifications; it never runs automatically.
- Automated tests cover account access, profile editing, opportunity discovery, mentorship requests, investor connection permissions/status changes and demo-data seeding.

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
- Notifications: `/notifications/`
- Admin: `/admin/`

## Managing opportunities

Create a staff or superuser account and sign in at `/admin/`. Use the Opportunities section to add or update opportunity information, including its category, sector, location, deadline and application link.

## Preparing demonstration data

For a walkthrough, you can create three sample accounts (entrepreneur, mentor and investor), three clearly labelled sample opportunities, one pending mentorship request, one pending investor connection request and their notifications:

```bash
python manage.py seed_demo_data --password "Choose-A-Strong-Demo-Password"
```

The password must meet the project's Django password validators. The command prints the three usernames but does not print the password. The default usernames are `demo_founder`, `demo_mentor` and `demo_investor`. All sample opportunities are labelled `[DEMO]` and are not real funding or application calls.

Useful options:

- `--prefix mydemo` uses `mydemo_founder`, `mydemo_mentor` and `mydemo_investor` instead of the default usernames.
- `--reset-passwords` explicitly resets passwords for existing matching demo accounts. Without this option, rerunning the command preserves existing passwords and profile edits.

On the first run, both requests are pending and the mentor and investor receive unread notifications. Rerunning the command reuses existing records and preserves any request decisions or notification read states. It does not delete data, create an administrator or run during deployment. It refuses to repurpose an existing username with a different role or an administrative account. Run it only when you intentionally want sample records in the database used for your demonstration, and do not reuse a personal or production password.

## Deployment

The repository includes a Render Blueprint in `render.yaml` for a Python web service and PostgreSQL database.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/duwase7/bizbridge)

To deploy the current `main` branch:

1. Merge the features you want included in the demo before deploying. The button deploys the repository's default branch.
2. Click **Deploy to Render** and sign in to Render. Connect GitHub if Render asks for permission.
3. Review the Blueprint. It should create a `bizbridge` web service and a `bizbridge-db` PostgreSQL database in Frankfurt, both on the Free plan.
4. Click **Apply** or **Deploy Blueprint** to provision the resources.
5. Wait for the web service's deploy status to show **Live**, then open its generated `.onrender.com` URL and test registration, login, dashboards and the main workflows.

The Blueprint generates the `SECRET_KEY` and connects the web service to PostgreSQL. Do not add secrets or database passwords to GitHub.

**Free-plan limitations:** Render free web services spin down after 15 minutes without traffic and can take about a minute to wake on the next request. Free Render PostgreSQL databases expire 30 days after creation; export any demo data you need before the database expires. These limits are suitable for a short prototype demonstration, not long-term production data storage. See [Render's free-instance limits](https://render.com/docs/free) and [Blueprint setup guide](https://render.com/docs/infrastructure-as-code).

A public deployment URL is not claimed until the Render service has deployed successfully and the live site has been opened and checked.

## Current scope

The prototype implements account registration and access, role-specific profile editing, opportunity discovery, mentorship requests, investor connection requests and in-app notifications. The SRS also specifies direct messaging, administrator verification, account suspension and activity reports. These remain outstanding implementation work and should not be described as completed until implemented and tested.

## Repository

https://github.com/duwase7/bizbridge
