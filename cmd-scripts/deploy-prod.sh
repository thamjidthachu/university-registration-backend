#!/bin/bash

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/reg-backend

PROJECT_PATH='/opt/projects/registration'
PROJECT_DIR='backend-production'
PROJECT_DIR_PATH=${PROJECT_PATH}/${PROJECT_DIR}

cd ${PROJECT_DIR_PATH}
git checkout master
git pull origin master

${PROJECT_DIR_PATH}/cmd-scripts/app-run.sh up-d
ssh-agent -k

