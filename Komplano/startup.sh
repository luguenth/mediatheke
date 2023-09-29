#!/bin/bash
# Running both uvicorn and celery worker
pipenv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --root-path /api &
pipenv run celery -A app.celery worker -l error -c 1 -Q default
