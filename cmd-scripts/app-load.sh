#!/bin/bash

if [[ $1 == "migrate" ]]; then
   echo "Running django migrations"
   docker-compose --project-name registration-backend-prod -f docker-compose-prod.yml exec web python manage.py migrate --noinput

fi

if [[ $1 == "static" ]]; then
   echo "Running collectstatic"
   docker-compose --project-name registration-backend-prod -f docker-compose-prod.yml exec web python manage.py collectstatic --noinput

fi