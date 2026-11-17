#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations --noinput
python manage.py collectstatic --no-input
python manage.py migrate --run-syncdb --noinput
python manage.py bootstrap_admin
