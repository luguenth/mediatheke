#!/bin/bash
# Running both uvicorn and celery worker
#pipenv run celery -A app.celery worker -l error -c 1 -Q default > ./celery.log 2>&1 &
pipenv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --root-path /api
