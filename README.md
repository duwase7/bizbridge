# BizBridge

**An Entrepreneurship Support and Connection Platform**

BizBridge is a web platform that helps entrepreneurs in Rwanda find mentors, investors, business partners and opportunities (funding, training, competitions, incubators and partnerships) in one place. Entrepreneurs no longer need to search across many websites, social media pages and WhatsApp groups.

- **Live demo:** _add your Render URL here after deploying, e.g. `https://bizbridge.onrender.com`_
- **SRS / system design:** _add the link to your SRS document here_
- **Repository:** https://github.com/duwase7/bizbridge

## Problem and solution

Business support in Rwanda is spread across many organisations and platforms, so it is hard for entrepreneurs to find the right mentor, investor or opportunity. Research (UNDP AGUKA tracer study, Access to Finance Rwanda FinMap 2024, NISR IBES) shows that mentorship, networks and access to finance are what entrepreneurs need most. BizBridge brings these people and opportunities together and matches them by **sector, stage and location**.

## Users (actors)

| Actor | What they can do |
|---|---|
| Visitor | View the home and help pages, register, log in, reset a password |
| Entrepreneur | Build a business profile, search mentors, investors, partners and opportunities, see recommendations, send connection, mentorship and investor requests, message connections, receive notifications |
| Mentor | Build an expertise profile, search businesses, accept or reject mentorship and connection requests, message connections |
| Investor | Build an organisation profile, search businesses by sector, location and stage, send and accept requests, message connections |
| Administrator | Manage accounts (suspend, reactivate, delete), verify mentor and investor profiles, manage opportunities, view activity reports and export them as CSV |

## Features mapped to the SRS

| SRS | Feature | Where |
|---|---|---|
| FR-01, FR-02 | Register with name, email, password and role. Duplicate emails and passwords shorter than 8 characters are rejected | `/accounts/signup/` |
| FR-03 | Log in with **email or username**, and log out | `/accounts/login/` |
| FR-04, NFR-07 | Role-based menus and permissions (each role sees only its own features) | all pages |
| FR-05 | Reset a forgotten password by email link | `/accounts/password-reset/` |
| FR-06 to FR-09 | Role-specific profiles: business details, mentor expertise and availability, investor type and website, sectors of interest | `/accounts/profile/` |
| FR-10, FR-11 | Search people with filters for keyword, type, sector, location and stage. Search opportunities with filters for keyword, category, sector and location | `/people/`, `/opportunities/` |
| FR-12 | Ranked rule-based recommendations of people and opportunities on the dashboard | `/accounts/dashboard/` |
| FR-13 | Full profile and opportunity detail pages | `/people/<id>/`, `/opportunities/<id>/` |
| FR-14, BR-04 | Administrator creates, edits and removes opportunities | `/manage/opportunities/` |
| FR-15, BR-07 | Opportunities past their deadline are hidden automatically | |
| FR-16, FR-17, BR-03 | Send and answer connection requests (pending, accepted, declined). Self-requests and duplicate requests are blocked | `/network/` |
| FR-18, FR-19, BR-05 | Request mentorship on a topic. The mentor accepts or rejects it | `/mentorship/` |
| FR-20, FR-21, BR-02 | Messaging only between accepted connections, with history shown newest first | `/messages/` |
| FR-22, FR-23 | Notifications for requests, responses, messages and verification. Mark one or all as read | `/notifications/` |
| FR-24, BR-06 | Administrator views, suspends, reactivates and deletes accounts. Suspended users cannot log in | `/manage/users/` |
| FR-25, NFR-04 | Administrator verifies mentor and investor profiles, which then show a **✔ Verified** badge | `/manage/users/` |
| FR-26 | Activity report: registrations, requests, acceptance rate, messages, opportunity views and pilot targets. CSV export | `/manage/` |
| NFR-05 | Warning that BizBridge never takes payments (footer, messages, help) | |
| NFR-06 | Hashed passwords. Sessions expire after 30 minutes of inactivity | |
| NFR-08 | Django form validation, ORM queries (protect against SQL injection), auto-escaped templates (protect against XSS) and CSRF protection | |
| NFR-09 | Members can delete their own account and data | Edit profile → Delete my account |
| NFR-14 | Modular apps, Git history and 89 automated tests run in GitHub Actions | |
| 2.6 User documentation | In-app help page and FAQ | `/help/` |

**Out of scope for version 1.0 (as stated in the SRS):** payments, video calls, native mobile apps and AI matching.

## Technology

- Python 3.12 and Django 5
- HTML and CSS (responsive, no JavaScript framework)
- SQLite for local development and PostgreSQL in production
- Gunicorn and WhiteNoise, deployed on Render

## Project structure

```
accounts/              users, profiles, search, matching/recommendations, password reset, demo data command
opportunities/         opportunity model, search and detail pages
mentorships/           entrepreneur → mentor requests
investor_connections/  entrepreneur → investor introductions
networking/            general connection requests and messaging
notifications/         in-app notifications
adminpanel/            administrator console: accounts, verification, opportunities, reports
templates/, static/    HTML templates and CSS
```

## Run it locally (step by step)

1. **Install Python 3.12+** from https://www.python.org/downloads/ and check it is installed:
   ```bash
   python3 --version
   ```
2. **Install Git** from https://git-scm.com/downloads, then clone the project:
   ```bash
   git clone https://github.com/duwase7/bizbridge.git
   cd bizbridge
   ```
3. **Create and activate a virtual environment.**
   macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   Windows (PowerShell):
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
4. **Install the dependencies:**
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. **(Optional) Create a `.env` file.** No `.env` is needed locally because the defaults use SQLite and debug mode. To customise settings:
   ```bash
   cp .env.example .env
   ```
6. **Create the database tables:**
   ```bash
   python manage.py migrate
   ```
7. **Load the demo data.** This creates five accounts, sample opportunities, requests and messages:
   ```bash
   python manage.py seed_demo_data --password "DemoAccess!2026"
   ```
8. **(Optional) Create your own superuser** for the Django admin at `/admin/`:
   ```bash
   python manage.py createsuperuser
   ```
9. **Start the server:**
   ```bash
   python manage.py runserver
   ```
   Open http://127.0.0.1:8000/ in your browser.
10. **Run the tests:**
    ```bash
    python manage.py test
    ```

### Demo accounts

After step 7, every account uses the password you passed with `--password`. You can log in with either the username or the email.

| Username | Role | What to try |
|---|---|---|
| `demo_founder` | Entrepreneur (agritech, Kigali) | Dashboard recommendations, search, mentorship and investor requests, messages |
| `demo_partner` | Entrepreneur (logistics) | Already connected to the founder, with existing messages |
| `demo_mentor` | Mentor (verified) | Accept or reject the pending mentorship request |
| `demo_investor` | Investor (verified) | Search businesses, answer the pending introduction |
| `demo_admin` | Administrator | `/manage/`: reports, verify, suspend, opportunities |

All demo opportunities are labelled `[DEMO]`. One of them has already expired, to show that expired opportunities are hidden.

### Password reset emails

Without SMTP settings, the reset email (and its link) is printed in the terminal or server log. To send real emails, set `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` and `DEFAULT_FROM_EMAIL` (see `.env.example`). For example, you can use a Gmail app password.

## Deploy on Render (free)

The repository includes a Render Blueprint (`render.yaml`). It creates a Python web service and a PostgreSQL database.

1. Make sure everything is merged into `main` on GitHub.
2. Go to https://dashboard.render.com, sign in with GitHub, and click **New → Blueprint**.
3. Select the `duwase7/bizbridge` repository and click **Connect**.
4. Render asks for **`DEMO_PASSWORD`**. Enter a strong password (for example `DemoAccess!2026`) to create the demo accounts automatically, or leave it empty to skip them.
5. Click **Apply**. Wait 3–5 minutes until the `bizbridge` service shows **Live**.
6. Open the `https://bizbridge-xxxx.onrender.com` URL shown on the service page and log in with a demo account.
7. (Optional) To create a real superuser, add `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD` under **Environment**, then redeploy.

**Free-plan notes:** the service sleeps after 15 minutes without traffic, so the first visit can take about a minute to load. Free Render PostgreSQL databases expire after 30 days. For a longer-lived database, create a free Supabase project and set the web service's `DATABASE_URL` to Supabase's **Session pooler** connection string.

## Known limitations

- Email notifications are in-app. Email is used only for password reset.
- Matching is rule-based (sector, stage, location). AI matching is planned for a later version.
- Database backups (NFR-13) depend on the hosting plan. The free tier has no automatic backups.
