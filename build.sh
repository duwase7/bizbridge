#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --no-input
python manage.py migrate --noinput
python manage.py bootstrap_admin

# Optional: load the demo accounts and sample data when DEMO_PASSWORD is set.
# The command is idempotent, so redeploys do not duplicate data or reset passwords.
if [ -n "${DEMO_PASSWORD:-}" ]; then
  python manage.py seed_demo_data --password "$DEMO_PASSWORD"
fi
