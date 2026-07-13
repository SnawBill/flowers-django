#!/bin/sh
set -e

.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput
exec .venv/bin/gunicorn flowers_django.wsgi:application --bind 0.0.0.0:8000 --workers "${GUNICORN_WORKERS:-3}" --timeout "${GUNICORN_TIMEOUT:-60}" --access-logfile - --error-logfile -
