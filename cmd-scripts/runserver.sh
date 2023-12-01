#!/usr/bin/env sh

gunicorn --workers $(( 2 * `cat /proc/cpuinfo | grep 'core id' | wc -l` + 1 )) --bind 0.0.0.0:8000 --timeout 500 --error-logfile ./logs/gunicorn-app-error.log university.wsgi:application

#gunicorn --workers 2 --bind 0.0.0.0:8000 --timeout 500 --error-logfile ./logs/gunicorn-app-error.log university.wsgi:application