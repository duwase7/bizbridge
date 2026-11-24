# BizBridge

BizBridge is a website that helps entrepreneurs in Rwanda find mentors, investors, business partners and opportunities (funding, training, competitions and incubators) in one place.

- **Live website:** https://bizbridge-coz9.onrender.com
- **SRS and system design:** _add your SRS link here_
- **GitHub repository:** https://github.com/duwase7/bizbridge

## The problem

In Rwanda, help for small businesses is spread across many websites, social media pages and WhatsApp groups. An entrepreneur has to search in many places to find a mentor, an investor or a funding opportunity. Research by UNDP (AGUKA), Access to Finance Rwanda and NISR shows that mentorship, networks and access to finance are what entrepreneurs need most. Many entrepreneurs, especially those without a strong network, never find the right support.

## The solution

BizBridge brings everything into one website. Users create a profile, and BizBridge suggests people and opportunities that match their **sector, business stage and location**. Users can send requests, get accepted and message each other. An administrator checks profiles and keeps the opportunities up to date.

## Who uses BizBridge

| User | What they can do |
|---|---|
| Visitor | See the home page and help page, sign up, log in, reset a forgotten password |
| Entrepreneur | Add business details, search for mentors, investors, partners and opportunities, see recommendations, send requests, send messages |
| Mentor | Add expertise and availability, accept or reject mentorship requests, send messages |
| Investor | Add organisation details, search for businesses, accept or decline requests, send messages |
| Administrator | Verify mentors and investors, suspend or delete accounts, add and edit opportunities, view reports |

## Main features

- **Accounts:** sign up with a role, log in with email or username, log out, reset a password by email, delete your own account.
- **Profiles:** each role fills in different details (business, expertise or investment information).
- **Search:** find people and opportunities by keyword, sector, location, stage and type.
- **Recommendations:** the dashboard shows the best matches for you.
- **Opportunities:** each opportunity has a details page. Opportunities that have passed their deadline are hidden automatically.
- **Requests:** connection requests, mentorship requests and investor introductions, with a status of pending, accepted or declined.
- **Messages:** you can message someone only after they accept your request.
- **Notifications:** you are told about new requests, answers, messages and profile verification.
- **Admin console:** verify profiles, suspend or reactivate accounts, manage opportunities, and see activity reports (with CSV download).
- **Safety:** a warning that BizBridge never asks for payments, a session timeout after 30 minutes, and passwords stored securely.

## How the features match the SRS

| SRS requirement | Feature |
|---|---|
| FR-01 to FR-05 | Sign up, check details, log in and out, role-based access, password reset |
| FR-06 to FR-09 | Profiles for entrepreneurs, mentors and investors |
| FR-10 to FR-13 | Search, filters, recommendations, details pages |
| FR-14, FR-15 | Admin manages opportunities; expired ones are hidden |
| FR-16 to FR-19 | Connection and mentorship requests |
| FR-20 to FR-23 | Messages and notifications |
| FR-24 to FR-26 | Admin manages accounts, verifies profiles, views reports |

Not included in version 1 (as planned in the SRS): payments, video calls, a mobile app and AI matching.

## Tools used

- Python 3.12 and Django 5
- HTML and CSS, plus a little JavaScript for animations
- SQLite on my computer, PostgreSQL on the live website
- Render for hosting

## How to run it on your computer

Follow these steps one by one.

**1. Install Python 3.12 or newer** from https://www.python.org/downloads/. Check it works:

```bash
python3 --version
```

**2. Download the project:**

```bash
git clone https://github.com/duwase7/bizbridge.git
cd bizbridge
```

**3. Create and turn on a virtual environment.**

On Mac or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

**4. Install the required packages:**

```bash
pip install -r requirements.txt
```

**5. Create the database:**

```bash
python manage.py migrate
```

**6. Add the demo accounts and sample data:**

```bash
python manage.py seed_demo_data --password 'DemoAccess!2026'
```

**7. Start the website:**

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

**8. (Optional) Run the tests:**

```bash
python manage.py test
```

## Demo accounts

These accounts work on the live website and on your computer after step 6.
The password for all of them is **DemoAccess!2026**.

| Username | Role |
|---|---|
| demo_founder | Entrepreneur |
| demo_partner | Entrepreneur |
| demo_mentor | Mentor (verified) |
| demo_investor | Investor (verified) |
| demo_admin | Administrator |

You can also create your own account on the sign-up page.

## How to deploy on Render

1. Go to https://dashboard.render.com and sign in with GitHub.
2. Click **New → Blueprint** and choose this repository.
3. When asked for `DEMO_PASSWORD`, type `DemoAccess!2026` (this creates the demo accounts).
4. Click **Apply** and wait until the service says **Live**.
5. Open the website link shown on the service page.

Notes about the free plan:
- The website sleeps after 15 minutes with no visitors. The first visit after that takes about one minute to load.
- The free database is deleted 30 days after it is created.

## Password reset emails

If no email settings are added, the reset email is printed in the server log instead of being sent. To send real emails, add `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` and `DEFAULT_FROM_EMAIL` (see `.env.example`).

## Known limitations

- Notifications are shown inside the website. Email is only used for password reset.
- Matching uses simple rules (sector, stage and location), not AI.
- The free hosting plan has no automatic database backups.

## Use of AI

I designed BizBridge, wrote the SRS and system design, decided on the features, directed the development, and tested and deployed the website. I used Claude, an AI coding assistant, to help write and implement parts of the code.
