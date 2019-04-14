# Žinau, ką renku platform

[![Build Status](https://travis-ci.org/zinaukarenku/zkr-platform.svg?branch=master)](https://travis-ci.org/zinaukarenku/zkr-platform)

This repository contains all Žinau, ką renku platform code. 

Local development
------------

It's a standart Django based project. After cloning project:
1. Create [Python virtual environment](https://docs.python.org/3/tutorial/venv.html)
```
python -m venv virtual-env
```
Windows:
```
virtual-env\Scripts\activate.bat
```
Unix/MacOS:
```
source virtual-env/bin/activate
```
2. Install project requirements using pip e.g `pip install -r requirements.txt`
3. Set environment variable `DEV=1`
4. Create Sqlite database file `db.sqlite3` or Postgres database and apply migrations using `python manage.py migrate`
5. Fetch some data by running `python manage.py fetch_seimas_data`. You can see all possible Celery tasks in `zkr/settings.py` near `CELERY_BEAT_SCHEDULE`
6. Start project using `python manage.py runserver`

Deployment
------------
Once code is pushed to Master branch Travis should automatically deploy changes to the server.  
Server environment is completely dockerized: `Docker` and `Docker-Compose` are used.  
In very rare cases you may need to edit Docker environment file `.env` in which all secrets are kept.  
The structure of `.env` file:  
```
SECRET_KEY=[SECRET_KEY]
POSTGRES_USER=[POSTGRES_USER]
POSTGRES_PASSWORD=[POSTGRES_PASSWORD]
POSTGRES_HOST=[POSTGRES_HOST]
POSTGRES_DB=[POSTGRES_DB]
REDIS_PORT_6379_TCP_ADDR=[REDIS_PORT_6379_TCP_ADDR]
SENTRY_KEY=[SENTRY_KEY]
SENTRY_SECRET=[SENTRY_SECRET]
SENTRY_PROJECT_ID=[SENTRY_PROJECT_ID]
RECAPTCHA_PUBLIC_KEY=[RECAPTCHA_PUBLIC_KEY]
RECAPTCHA_PRIVATE_KEY=[RECAPTCHA_PRIVATE_KEY]
ALLOWED_HOSTS=[ALLOWED_HOSTS]
SENDGRID_API_KEY=[SENDGRID_API_KEY]
```

This file should be edited on the server. 
