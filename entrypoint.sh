#!/bin/bash

# Prepare log files and start outputting logs to stdout
mkdir ./logs
touch ./logs/gunicorn.log
touch ./logs/gunicorn-access.log
tail -f ./logs/gunicorn*.log &

exec gunicorn server:app \
  --name bless_server \
  --bind 0.0.0.0:8000 \
  --workers 5 \
  --log-level=info \
  --log-file=./logs/gunicorn.log \
  --access-logfile=./logs/gunicorn-access.log \
  "$@"
