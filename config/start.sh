#!/bin/bash
set -e

echo "==> Django setup, executing: collectstatic"
python manage.py collectstatic --noinput

echo "==> Django setup, executing: migrate"
python manage.py migrate

echo "==> Starting uWSGI ..."
gunicorn zkr.wsgi --bind 0.0.0.0:8080 --enable-threads --workers 5