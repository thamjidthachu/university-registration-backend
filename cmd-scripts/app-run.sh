#!/bin/bash

if [[ $1 == "up" ]]; then
   echo "Building and Running registration-backend-prod App"
   docker-compose --project-name registration-backend-prod -f docker-compose-prod.yml up --build

fi

if [[ $1 == "up-d" ]]; then
   echo "Building and Running registration-backend-prod App in background"
   docker-compose --project-name registration-backend-prod -f docker-compose-prod.yml up --build -d
   docker-compose --project-name registration-backend-prod -f docker-compose-prod.yml restart web
   docker-compose --project-name registration-backend-prod -f docker-compose-prod.yml restart celery

fi

if [[ $1 == "down" ]]; then
   echo "Stopping registration-backend-prod App"
   docker-compose --project-name registration-backend-prod -f docker-compose-prod.yml down

fi