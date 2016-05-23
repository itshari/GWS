#!/bin/bash

nohup celery -A gws.celery worker --loglevel=info > ./celery.out &
nohup python gws.py > ./uwsgi.out &
